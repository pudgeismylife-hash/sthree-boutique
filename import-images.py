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


def skin_mask(rgb):
    """Skin, and specifically not gold.

    Both are warm - red above green above blue - so the usual skin rule calls
    a gold bangle a wrist.  What separates them is how far blue falls away:
    skin keeps blue close to green, gold drops it hard.  Anything with that
    yellow gap is metal, and metal is the product, not the model.
    """
    a = rgb.astype(np.int16)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    mx, mn = a.max(axis=2), a.min(axis=2)
    warm = ((r > 95) & (g > 40) & (b > 20) &
            ((mx - mn) > 15) & (abs(r - g) > 15) & (r > g) & (r > b))
    metal = (g - b) > 45
    return warm & ~metal


def skin_inside(rgb, alpha):
    """Share of the *kept* product that looks like skin.

    Measuring skin across the whole frame is useless here: half these pieces
    are shot on a warm beige surface that reads as skin, and a cream ground
    is not a wrist.  What matters is whether the thing that survived the cut
    is skin - a hand still wearing the ring, a wrist still wearing the bangle.
    That product cannot be published: the part hidden behind the hand is not
    in the file, and drawing it back would invent product.
    """
    keep = alpha >= SOLID
    if keep.sum() < 100:
        return 0.0
    return float(skin_mask(rgb)[keep].mean())


def looks_like_packaging(rgb, alpha, box):
    """A retail display card kept instead of the jewellery on it.

    The card is a pale rectangle that fills its own bounding box; the piece
    of jewellery pinned to it is a few percent of the area.  Cutting that out
    gives a photograph of packaging, not of a product.
    """
    if box is None:
        return False
    x0, y0, x1, y1 = box
    a = alpha[y0:y1, x0:x1]
    fill = float((a > FAINT).mean())
    if fill < 0.80:
        return False
    patch = rgb[y0:y1, x0:x1].astype(np.int16)
    inside = a >= SOLID
    if inside.sum() < 100:
        return False
    px = patch[inside]
    bright = float(px.mean())
    sat = float((px.max(axis=1) - px.min(axis=1)).mean())
    return bright > 180 and sat < 40


def largest_part_share(alpha):
    """How much of the cut-out sits in one connected piece.

    A chain that survived intact is one shape, or a shape and its pendant.
    A chain the model tore up is a scatter of unrelated fragments, and no
    single one of them holds much of what is left.  Counting solid pixels
    cannot tell these apart - a thin chain is legitimately nearly all rim -
    but the shape of what survived can.
    """
    ink = alpha > FAINT
    if not ink.any():
        return 0.0
    lab, n = ndimage.label(ink)
    if n == 0:
        return 0.0
    sizes = ndimage.sum(ink, lab, range(1, n + 1))
    return round(float(sizes.max() / sizes.sum()), 4)


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
        "skinInProduct": round(skin_inside(source_rgb, a), 4),
        "productWidth":  (box[2] - box[0]) if box else 0,
        "productHeight": (box[3] - box[1]) if box else 0,
    }
    m["packaging"] = looks_like_packaging(source_rgb, a, box)
    if box:
        crop = a[box[1]:box[3], box[0]:box[2]]
        m["bboxFill"] = round(float((crop > FAINT).mean()), 4)
        m["opaquePixels"] = int((crop >= SOLID).sum())
    else:
        m["bboxFill"], m["opaquePixels"] = 0.0, 0
    m["largestPart"] = largest_part_share(a)
    return m, box


# -------------------------------------------------------------------- gate

def judge(m):
    """Return (verdict, reasons).  'review' is the best a machine can give.

    Only checks that hold up on this shop's actual stock live here.  Two that
    did not, and why they were taken out rather than tuned:

      skin colour  - meant to catch a bangle still on a wrist.  Pale gold has
                     the same warm signature as skin, so it condemned the
                     butterfly armcuff and the ginkgo earrings.  Tightening it
                     to spare the gold let a real worn shot back through.

      fragment count - meant to catch a chain the model tore up.  A pair of
                     earrings is two pieces for the same honest reason, and
                     nothing in the numbers separates the pair from the wreck.

    Both asked the machine to answer "is this a photograph of the product",
    which is the judgement this pipeline deliberately leaves to a person.
    What stays below is only what can be measured and proved.
    """
    bad = []
    if m["alphaMin"] == m["alphaMax"]:
        bad.append("no real alpha channel - nothing was cut away")
    if m["clearShare"] < 0.05:
        bad.append("almost nothing was removed - the background is still there")
    if max(m["productWidth"], m["productHeight"]) < MIN_PX:
        bad.append("product is %dx%d px, below the %d px floor"
                   % (m["productWidth"], m["productHeight"], MIN_PX))
    if m["packaging"]:
        bad.append("the cut kept the display card, not the jewellery pinned to it")
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
