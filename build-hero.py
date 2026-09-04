"""Compose the front-page hero picture from the boutique's own photographs.

    python3 build-hero.py            report only, writes nothing
    python3 build-hero.py --apply    write assets/hero/hero-still.jpg

The hero wants a wide picture with faces high in it, a quiet lower left for the
words and no pale margin at any edge.  Nothing the boutique has sent is that
shape: every photograph is a tall studio shot of one figure, letterboxed on
cream so the product cards all match.  Cropping one to a wide band either takes
the head off or shows the cream down both sides.

So the band is built rather than cropped.  The figures used here are the
cut-outs already in assets/products -- the same photographs the catalogue
shows, with their backgrounds removed -- stood on a dark ground at different
sizes and brightnesses so the eye reads depth.  Nothing about a garment is
altered: no colour, no shape, no invention.  This is an arrangement of her
photographs, not a picture of clothes that do not exist.

Three constraints come from the page itself, not from taste, and moving a
figure means checking them again:

  the mobile window   The hero covers its box from 50%% across, so a phone sees
                      only the middle third or so of this file.  MOBILE_BAND
                      below is that window; the front figure has to sit inside
                      it or the phone gets an empty ground.

  the top             Covering a wide short viewport crops top and bottom, held
                      at 22%% from the top.  Heads below HEAD_FLOOR survive that
                      crop; heads above it get shaved on wide screens.

  the lower left      The headline, the lede and the button sit there over a
                      scrim.  Everything left of QUIET_LEFT is kept as bare
                      ground so the words have air on a wide screen.

Run build-og-images.py afterwards only if a product changed; this script writes
one file and touches nothing else.
"""
import os, sys
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "assets", "products")
OUT = os.path.join(HERE, "assets", "hero", "hero-still.jpg")
APPLY = "--apply" in sys.argv

SIZE = (2400, 1100)          # 2.18:1 -- close to the hero's own box on a laptop,
                             # so a desktop crops almost nothing away
INK = (14, 11, 9)            # --ink, the page's own dark
GLOW = (74, 52, 33)          # warm stage light behind the front figure
QUIET_LEFT = 0.26            # left of this stays bare ground, for the words
HEAD_FLOOR = 0.09            # no head above this, or a wide screen shaves it
MOBILE_BAND = (0.35, 0.65)   # what a phone actually sees of this file

# cx  centre of the figure across the frame, 0 left edge to 1 right
# h   the figure's height as a share of the canvas
# top where the top of the figure sits, as a share of the canvas
# a   opacity, and with it the sense of distance
#
# top + h is over 1 for every figure on purpose. Two of these cut-outs stop at
# the shin because the photograph did, and a figure that ends inside the frame
# reads as a paper doll floating in the dark whether it was cut short or not.
# Running the hem off the bottom edge hides the join and puts the whole frame
# to work.
FIGURES = [
    dict(key="gowns_1-a1",  cx=0.315, h=0.92, top=0.16, a=0.50, dim=0.55),
    dict(key="sarees_1-a1", cx=0.525, h=1.00, top=0.10, a=1.00, dim=1.00),
    dict(key="sarees_3-a1", cx=0.765, h=0.92, top=0.12, a=0.92, dim=0.84),
    dict(key="sarees_2-a1", cx=0.950, h=0.90, top=0.17, a=0.45, dim=0.55),
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


def ground(size):
    """The dark the figures stand on: warmer and lighter toward the middle
    right, where they are, falling away to near-black at the edges and along
    the bottom so the words at the foot have something quiet to sit on."""
    w, h = size
    y, x = np.mgrid[0:h, 0:w]
    fx, fy = x / w, y / h
    # one soft ellipse of warm light, centred behind the front figure
    d = ((fx - 0.55) / 0.62) ** 2 + ((fy - 0.34) / 0.70) ** 2
    glow = np.clip(1.0 - d, 0, 1) ** 1.9
    # and the floor of the frame darkened, under where the copy falls
    glow *= np.clip(1.25 - fy * 1.05, 0, 1)
    base = np.array(INK, float)[None, None, :]
    lift = (np.array(GLOW, float) - base)[0, 0][None, None, :]
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


def check(spans):
    """The three page constraints, stated as failures rather than trusted."""
    bad = []
    for spec, (l, rgt) in zip(FIGURES, spans):
        if spec["top"] < HEAD_FLOOR:
            bad.append("%s starts at %.2f, above the %.2f head floor -- a wide "
                       "screen will shave it" % (spec["key"], spec["top"], HEAD_FLOOR))
        if spec["a"] > 0.7 and l < QUIET_LEFT:
            bad.append("%s reaches %.2f, into the %.2f left kept for the words"
                       % (spec["key"], l, QUIET_LEFT))
    front = max(range(len(FIGURES)), key=lambda i: FIGURES[i]["a"])
    fl, fr = spans[front]
    if not (fl < MOBILE_BAND[1] and fr > MOBILE_BAND[0]):
        bad.append("the front figure (%s, %.2f-%.2f) misses the phone's window "
                   "%.2f-%.2f -- a phone would see bare ground"
                   % (FIGURES[front]["key"], fl, fr, *MOBILE_BAND))
    for i in range(len(spans) - 1):
        if spans[i][1] > spans[i + 1][0] + 0.005:
            bad.append("%s and %s overlap" % (FIGURES[i]["key"], FIGURES[i + 1]["key"]))
    return bad


def main():
    canvas = ground(SIZE).convert("RGBA")
    spans = [place(canvas, cutout(s["key"]), s) for s in FIGURES]
    for s, (l, r) in zip(FIGURES, spans):
        print("  %-16s %.2f - %.2f  head %.2f  opacity %.2f"
              % (s["key"], l, r, s["top"], s["a"]))
    bad = check(spans)
    for b in bad:
        print("  FAIL " + b)

    out = canvas.convert("RGB").filter(ImageFilter.GaussianBlur(0.3))
    if bad:
        print("\nnot written -- fix the above first")
        return 1
    if not APPLY:
        print("\nreport only; rerun with --apply to write %s"
              % os.path.relpath(OUT, HERE))
        return 0
    out.save(OUT, quality=86, optimize=True, progressive=True)
    print("\nwrote %s  %dx%d  %d KB"
          % (os.path.relpath(OUT, HERE), out.width, out.height,
             os.path.getsize(OUT) // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
