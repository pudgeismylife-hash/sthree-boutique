#!/usr/bin/env python3
"""Turn a client photograph into a website-ready product picture.

Two things have to be true before a picture is allowed near the website,
and this script only ever decides one of them:

  transparent  - the cut-out really has an alpha channel, the product is
                 opaque inside it, and the surround is clear.  Measured,
                 not assumed, and read back off the saved file.

  dimensional  - the picture still reads as a photograph of an object.
                 The machine can only reject the obvious failures here.
                 Whether the result actually looks premium is a judgement
                 a person makes, so anything that survives is offered for
                 review, never published on the strength of these numbers.

Nothing is deleted and nothing is written back to Drive.  A photograph the
gate turns down keeps its original file and gets a reason.
"""

import argparse, json, os, sys

from PIL import Image, ImageFilter
import numpy as np
from scipy import ndimage

FAINT   = 4      # alpha at or below this is "not really there"
SOLID   = 250    # alpha at or above this is "fully opaque"
SPECK   = 0.005  # a blob holding less than this share of the ink is a hairline
CANVAS  = 1200   # finished square
MARGIN  = 0.08   # share of the canvas left clear around the product
MIN_PX  = 400    # a product smaller than this on its long edge is too small


# ---------------------------------------------------------------- measuring

def alpha_box(alpha):
    """Bounding box of the real product, ignoring stray hairlines.

    Image.getbbox() is no use here: background removal leaves alpha 1-3
    scattered to the file edges, so getbbox() returns the whole frame.
    Threshold first, then keep only blobs that hold a real share of the ink.
    """
    ink = alpha > FAINT
    if not ink.any():
        return None
    lab, n = ndimage.label(ink)
    if n == 0:
        return None
    sizes = ndimage.sum(ink, lab, range(1, n + 1))
    keep = [i + 1 for i, s in enumerate(sizes) if s >= sizes.sum() * SPECK]
    if not keep:
        return None
    mask = np.isin(lab, keep)
    ys, xs = np.where(mask)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def skin_share(rgb):
    """Rough share of the frame that looks like skin.

    A worn photograph cannot be cut out into a product picture: the half of
    the bangle behind the wrist is not in the file, and inventing it would
    change the product.  Detecting skin is how such a photograph is caught.
    """
    a = rgb.astype(np.int16)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    mx, mn = a.max(axis=2), a.min(axis=2)
    return float((
        (r > 95) & (g > 40) & (b > 20) &
        ((mx - mn) > 15) & (abs(r - g) > 15) & (r > g) & (r > b)
    ).mean())


def measure(cut, source_rgb):
    a = np.array(cut)[:, :, 3]
    box = alpha_box(a)
    ink = a > FAINT
    m = {
        "alphaMin":     int(a.min()),
        "alphaMax":     int(a.max()),
        "opaqueShare":  round(float((a >= SOLID).mean()), 4),
        "clearShare":   round(float((a <= FAINT).mean()), 4),
        "inkShare":     round(float(ink.mean()), 4),
        "skinShare":    round(skin_share(source_rgb), 4),
        "productWidth":  (box[2] - box[0]) if box else 0,
        "productHeight": (box[3] - box[1]) if box else 0,
    }
    # how solid the product is inside its own outline
    if box and ink.any():
        inside = a[box[1]:box[3], box[0]:box[2]]
        m["solidInside"] = round(float((inside >= SOLID).sum() / max(1, (inside > FAINT).sum())), 4)
    else:
        m["solidInside"] = 0.0
    return m, box


# -------------------------------------------------------------------- gate

def judge(m):
    """Return (verdict, reasons).  'review' is the best a machine can give."""
    bad = []
    if m["alphaMin"] == m["alphaMax"]:
        bad.append("no real alpha channel - nothing was cut away")
    if m["clearShare"] < 0.05:
        bad.append("almost nothing was removed - the background is still there")
    if m["inkShare"] < 0.02:
        bad.append("only %.1f%% of the frame survived the cut - too little left to be the product"
                   % (m["inkShare"] * 100))
    if max(m["productWidth"], m["productHeight"]) < MIN_PX:
        bad.append("product is %dx%d px, below the %d px floor"
                   % (m["productWidth"], m["productHeight"], MIN_PX))
    if m["solidInside"] < 0.55:
        bad.append("the cut-out is more haze than product (%.0f%% solid inside its outline)"
                   % (m["solidInside"] * 100))
    if m["skinShare"] > 0.15:
        bad.append("worn on a model (%.0f%% of the photograph is skin) - the hidden part of the "
                   "product is not in the file and must not be invented" % (m["skinShare"] * 100))
    return ("hold" if bad else "review"), bad


# ------------------------------------------------------------- presentation

def present(cut, box, canvas=CANVAS, margin=MARGIN, shadow=True):
    """Place the cut-out on a square transparent canvas.

    Presentation only.  The product is not recoloured, reshaped, relit or
    redrawn - it is trimmed to its own outline, scaled once, and centred.
    """
    piece = cut.crop(box)
    room = int(canvas * (1 - 2 * margin))
    scale = min(room / piece.width, room / piece.height)
    piece = piece.resize((max(1, round(piece.width * scale)),
                          max(1, round(piece.height * scale))), Image.LANCZOS)

    out = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    x = (canvas - piece.width) // 2
    y = (canvas - piece.height) // 2

    if shadow:
        # a soft contact shadow under the piece: the only thing added, and it
        # sits beneath the product rather than altering it
        sh = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
        sil = Image.new("RGBA", piece.size, (60, 52, 46, 90))
        sil.putalpha(Image.fromarray(
            (np.array(piece)[:, :, 3] * 0.35).astype(np.uint8)))
        sh.paste(sil, (x, y + int(piece.height * 0.045)), sil)
        sh = sh.filter(ImageFilter.GaussianBlur(canvas * 0.018))
        out = Image.alpha_composite(out, sh)

    out.paste(piece, (x, y), piece)
    return out


def verify_saved(path):
    """Read the file back off disk - the gate is checked on what was saved."""
    im = Image.open(path)
    if im.mode != "RGBA":
        return False, "saved file has no alpha channel"
    a = np.array(im)[:, :, 3]
    if a.min() == a.max():
        return False, "saved file's alpha is flat"
    if (a <= FAINT).mean() < 0.05:
        return False, "saved file has no clear surround"
    return True, "transparent"


# -------------------------------------------------------------------- main

def process(src_path, out_dir, name, session):
    from rembg import remove
    src = Image.open(src_path).convert("RGB")
    cut = remove(src, session=session)
    m, box = measure(cut, np.array(src))
    verdict, reasons = judge(m)

    rec = {"source": os.path.basename(src_path), "name": name,
           "measured": m, "verdict": verdict, "reasons": reasons, "output": None}

    if verdict == "hold" or box is None:
        return rec

    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name + ".png")
    present(cut, box).save(path)

    ok, why = verify_saved(path)
    if not ok:
        os.remove(path)
        rec["verdict"], rec["reasons"] = "hold", [why]
        return rec

    rec["output"] = path
    rec["reasons"] = ["transparency confirmed on the saved file",
                      "a person still has to confirm it looks premium"]
    return rec


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--in", dest="indir", required=True, help="folder of source photographs")
    p.add_argument("--out", dest="outdir", required=True, help="where cut-outs are written")
    p.add_argument("--report", help="write the run's findings here as JSON")
    a = p.parse_args()

    from rembg import new_session
    session = new_session("u2net")

    files = sorted(f for f in os.listdir(a.indir)
                   if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp")))
    if not files:
        print("no photographs in %s" % a.indir, file=sys.stderr)
        return 1

    out = []
    for f in files:
        name = os.path.splitext(f)[0]
        rec = process(os.path.join(a.indir, f), a.outdir, name, session)
        out.append(rec)
        mark = "ready for review" if rec["verdict"] == "review" else "HELD"
        print("%-22s %-16s %s" % (f, mark, rec["reasons"][0] if rec["reasons"] else ""))

    if a.report:
        json.dump({"processed": out}, open(a.report, "w"), indent=2)
        print("\nreport written to %s" % a.report)

    held = sum(1 for r in out if r["verdict"] == "hold")
    print("\n%d photograph(s), %d cut out, %d held" % (len(out), len(out) - held, held))
    return 0


if __name__ == "__main__":
    sys.exit(main())
