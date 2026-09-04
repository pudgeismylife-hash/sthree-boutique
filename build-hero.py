"""Compose the front-page hero pictures from the boutique's own photographs.

    python3 build-hero.py            report only, writes nothing
    python3 build-hero.py --apply    write both files under assets/hero

The hero wants a picture with faces high in it, a quiet lower half for the
words and no pale margin at any edge.  Nothing the boutique has sent is that
shape: every photograph is a tall studio shot of one figure, letterboxed on
cream so the product cards all match.  Cropping one to a hero band either takes
the head off or shows the cream down both sides.

So the picture is built rather than cropped.  The figures used here are the
cut-outs already in assets/products -- the same photographs the catalogue
shows, with their backgrounds removed -- stood on a dark ground at different
sizes and brightnesses so the eye reads depth.  Nothing about a garment is
altered: no colour, no shape, no invention.  This is an arrangement of her
photographs, not a picture of clothes that do not exist.

TWO PICTURES, NOT ONE SCALED
----------------------------
A phone's hero box is taller than it is wide; a laptop's is more than twice as
wide as it is tall.  One file cannot serve both.  The wide file on a phone gets
covered from the middle out, so the phone saw about a third of it -- one figure,
and two and a half others paid for in bandwidth and never seen.  The tall file
is composed for that shape instead: the same front figure, the others brought
in close behind her where a narrow frame can hold them.

  hero-still.jpg        2400x1100   laptops and tablets
  hero-still-tall.jpg   1000x1400   phones, via a <source media> in the page

Each layout carries its own checks, because the constraints differ.  Both are
stated as failures the script refuses to write past rather than as intentions:

  the top          Covering crops top and bottom, held at 22%% from the top.
                   Heads below head_floor survive that; heads above get shaved.

  the words        On a laptop the copy sits lower left over a scrim, so the
                   wide layout keeps quiet_left as bare ground.  On a phone the
                   copy runs the full width, so what matters instead is that
                   the front figure's face clears copy_top.

  the crop         The wide file is only partly visible on a phone, so its
                   front figure has to sit inside seen_band or the phone gets
                   an empty ground.  The tall file is seen whole, and its
                   figures are allowed to overlap on purpose.

This script writes those two files and touches nothing else.
"""
import os, sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets", "products")
HERO = os.path.join(HERE, "assets", "hero")
APPLY = "--apply" in sys.argv

INK = (14, 11, 9)            # --ink, the page's own dark
GLOW = (74, 52, 33)          # warm stage light behind the front figure

# Each figure:
#   cx   centre across the frame, 0 left edge to 1 right
#   h    height as a share of the canvas
#   top  where the top of the figure sits, as a share of the canvas
#   a    opacity, and with it the sense of distance
#   dim  brightness, likewise
# Painted in order, so a figure later in the list stands in front of an earlier
# one.
#
# top + h is over 1 for every figure on purpose.  Two of these cut-outs stop at
# the shin because the photograph did, and a figure that ends inside the frame
# reads as a paper doll floating in the dark whether it was cut short or not.
# Running the hem off the bottom edge hides the join and puts the whole frame
# to work.
LAYOUTS = [
    dict(
        name="wide", out="hero-still.jpg",
        size=(2400, 1100),       # 2.18:1, close to the hero's box on a laptop,
                                 # so a desktop crops almost nothing away
        glow=(0.55, 0.34, 0.62, 0.70),
        head_floor=0.09, quiet_left=0.26, seen_band=(0.35, 0.65),
        copy_top=None, may_overlap=False,
        figures=[
            dict(key="gowns_1-a1",  cx=0.315, h=0.92, top=0.16, a=0.50, dim=0.55),
            dict(key="sarees_1-a1", cx=0.525, h=1.00, top=0.10, a=1.00, dim=1.00),
            dict(key="sarees_3-a1", cx=0.765, h=0.92, top=0.12, a=0.92, dim=0.84),
            dict(key="sarees_2-a1", cx=0.950, h=0.90, top=0.17, a=0.45, dim=0.55),
        ],
    ),
    dict(
        name="tall", out="hero-still-tall.jpg",
        size=(1000, 1400),       # 0.71:1, the middle of what phones ask for --
                                 # a hero box runs about 0.6 to 0.85 wide-to-tall
        glow=(0.48, 0.26, 0.78, 0.66),
        head_floor=0.05, quiet_left=None, seen_band=None,
        copy_top=0.42, may_overlap=True,
        figures=[
            # The two behind stand close in and half hidden, which a narrow
            # frame can hold and a wide one cannot -- side by side at this width
            # they would each be a sliver.
            dict(key="gowns_1-a1",  cx=0.110, h=0.82, top=0.22, a=0.40, dim=0.48),
            dict(key="sarees_3-a1", cx=0.950, h=0.86, top=0.18, a=0.55, dim=0.60),
            dict(key="sarees_1-a1", cx=0.460, h=0.98, top=0.06, a=1.00, dim=1.00),
        ],
    ),
]


def cutout(key):
    """The transparent copy, trimmed to the figure itself.

    The .webp is the cut-out; the .jpg beside it is the same photograph still on
    its cream. Only the cut-out is any use here -- a hero of pasted rectangles
    is not a hero -- so a missing .webp is a hard stop rather than a fallback.
    """
    p = os.path.join(SRC, key + ".webp")
    if not os.path.exists(p):
        raise SystemExit("no cut-out for %s -- run the import for it first" % key)
    im = Image.open(p).convert("RGBA")
    a = np.array(im)[:, :, 3]
    ys, xs = np.where(a > 8)
    if not len(xs):
        raise SystemExit("%s has no visible pixels" % key)
    return im.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))


def ground(size, glow_spec):
    """The dark the figures stand on: warmer and lighter where they are, falling
    away to near-black at the edges and along the bottom so the words at the
    foot have something quiet to sit on."""
    w, h = size
    gx, gy, rx, ry = glow_spec
    y, x = np.mgrid[0:h, 0:w]
    fx, fy = x / w, y / h
    # one soft ellipse of warm light, centred behind the front figure
    d = ((fx - gx) / rx) ** 2 + ((fy - gy) / ry) ** 2
    glow = np.clip(1.0 - d, 0, 1) ** 1.9
    # and the floor of the frame darkened, under where the copy falls
    glow *= np.clip(1.25 - fy * 1.05, 0, 1)
    base = np.array(INK, float)[None, None, :]
    lift = (np.array(GLOW, float) - np.array(INK, float))[None, None, :]
    arr = base + glow[:, :, None] * lift
    return Image.fromarray(np.clip(arr, 0, 255).astype("uint8"), "RGB")


def place(canvas, fig, spec):
    """Scale by height and hang from the top, not the bottom.

    Two of these cut-outs stop at the shin because the photograph did; anchoring
    them by their feet would float them. Anchoring by the head puts every face
    where the page needs it and lets the hems fall off the bottom edge, which
    costs nothing.
    """
    w, h = canvas.size
    th = int(round(spec["h"] * h))
    tw = max(1, int(round(fig.width * th / fig.height)))
    r = fig.resize((tw, th), Image.LANCZOS)
    if spec["dim"] < 1:
        rgb, alpha = r.convert("RGB"), r.getchannel("A")
        rgb = ImageEnhance.Brightness(rgb).enhance(spec["dim"])
        r = Image.merge("RGBA", (*rgb.split(), alpha))
    if spec["a"] < 1:
        alpha = r.getchannel("A").point(lambda v: int(v * spec["a"]))
        r.putalpha(alpha)
    x = int(round(spec["cx"] * w - tw / 2))
    y = int(round(spec["top"] * h))
    canvas.alpha_composite(r, (x, y))
    return (x / w, (x + tw) / w)


def check(lay, spans):
    """The page's constraints for this layout, stated as failures."""
    figs = lay["figures"]
    bad = []
    for spec, (l, _r) in zip(figs, spans):
        if spec["top"] < lay["head_floor"]:
            bad.append("%s starts at %.2f, above the %.2f head floor -- covering "
                       "will shave it" % (spec["key"], spec["top"], lay["head_floor"]))
        if spec["top"] + spec["h"] <= 1.0:
            bad.append("%s ends at %.2f, inside the frame -- a figure that stops "
                       "short of the bottom edge floats"
                       % (spec["key"], spec["top"] + spec["h"]))
        if lay["quiet_left"] and spec["a"] > 0.7 and l < lay["quiet_left"]:
            bad.append("%s reaches %.2f, into the %.2f left kept for the words"
                       % (spec["key"], l, lay["quiet_left"]))

    front = max(range(len(figs)), key=lambda i: figs[i]["a"])
    fl, fr = spans[front]
    if lay["seen_band"]:
        lo, hi = lay["seen_band"]
        if not (fl < hi and fr > lo):
            bad.append("the front figure (%s, %.2f-%.2f) misses the window a phone "
                       "sees of this file, %.2f-%.2f -- a phone would get bare "
                       "ground" % (figs[front]["key"], fl, fr, lo, hi))
    if lay["copy_top"]:
        # A face sits roughly a fifth of the way down a standing figure.
        face = figs[front]["top"] + 0.20 * figs[front]["h"]
        if face > lay["copy_top"]:
            bad.append("the front figure's face lands at %.2f, below the %.2f the "
                       "copy starts at -- the words would cross it"
                       % (face, lay["copy_top"]))
    if not lay["may_overlap"]:
        for i in range(len(spans) - 1):
            if spans[i][1] > spans[i + 1][0] + 0.005:
                bad.append("%s and %s overlap" % (figs[i]["key"], figs[i + 1]["key"]))
    return bad


def build(lay):
    canvas = ground(lay["size"], lay["glow"]).convert("RGBA")
    spans = [place(canvas, cutout(s["key"]), s) for s in lay["figures"]]
    print("%s  %dx%d" % (lay["name"], *lay["size"]))
    for s, (l, r) in zip(lay["figures"], spans):
        print("  %-16s %6.2f -%6.2f  head %.2f  opacity %.2f"
              % (s["key"], l, r, s["top"], s["a"]))
    bad = check(lay, spans)
    for b in bad:
        print("  FAIL " + b)
    if bad:
        return 1
    if not APPLY:
        print("  ok -- rerun with --apply to write assets/hero/%s" % lay["out"])
        return 0
    out = canvas.convert("RGB").filter(ImageFilter.GaussianBlur(0.3))
    path = os.path.join(HERO, lay["out"])
    out.save(path, quality=86, optimize=True, progressive=True)
    print("  wrote assets/hero/%s  %d KB" % (lay["out"], os.path.getsize(path) // 1024))
    return 0


def main():
    return max(build(lay) for lay in LAYOUTS)


if __name__ == "__main__":
    sys.exit(main())
