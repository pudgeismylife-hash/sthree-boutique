"""Build the Instagram story card announcing the website.

    python3 build-story.py            report only, writes nothing
    python3 build-story.py --apply    write assets/social/

The shop announced the site with a stock gradient and the address typed on it,
which is what the tools hand you and looks like nobody's shop. This makes the
same announcement out of the site's own parts: its dark warm ground, its
logo, its typeface, its colours and one of its own photographs. Somebody who
sees the story and then opens the link should recognise the second from the
first.

Sized 1080x1920 for a story. Instagram lays its own furniture over the top and
bottom of that frame -- the account name and the reply box -- so nothing that
has to be read sits outside SAFE.
"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "social")
FONTS = os.path.join(HERE, "assets", "fonts")
APPLY = "--apply" in sys.argv

SIZE = (1080, 1920)
SAFE = (250, 1670)          # Instagram covers above and below this
INK = (20, 17, 15)          # --ink
CREAM = (250, 246, 240)     # --cream
GOLD = (169, 128, 55)       # --gold
GOLD_HI = (201, 162, 39)    # --gold-bright
GLOW = (74, 52, 33)         # the hero's warm stage light

# The site's own faces, vendored so this renders the same on any machine.
DISPLAY = os.path.join(FONTS, "cormorant-300.ttf")   # --display, headlines
DISPLAY_R = os.path.join(FONTS, "cormorant-400.ttf")
UI = os.path.join(FONTS, "jost-400.ttf")             # --ui, body
UI_MED = os.path.join(FONTS, "jost-500.ttf")

FIGURE = "sarees_1-a1"      # the pink zari saree: the strongest colour she has
LOGO = os.path.join(HERE, "assets", "logo-web-dark.png")   # gold, for dark grounds


def font(path, size):
    return ImageFont.truetype(path, size)


def ground(size):
    """The hero's ground, in portrait: warm and lifted where the figure stands,
    falling to near-black at the edges so the type at top and foot has quiet."""
    w, h = size
    y, x = np.mgrid[0:h, 0:w]
    fx, fy = x / w, y / h
    d = ((fx - 0.52) / 0.78) ** 2 + ((fy - 0.42) / 0.52) ** 2
    g = np.clip(1.0 - d, 0, 1) ** 1.8
    base = np.array(INK, float)[None, None, :]
    lift = (np.array(GLOW, float) - np.array(INK, float))[None, None, :]
    return Image.fromarray(
        np.clip(base + g[:, :, None] * lift, 0, 255).astype("uint8"), "RGB")


def cutout(key):
    p = os.path.join(HERE, "assets", "products", key + ".webp")
    if not os.path.exists(p):
        raise SystemExit("no cut-out for %s" % key)
    im = Image.open(p).convert("RGBA")
    a = np.array(im)[:, :, 3]
    ys, xs = np.where(a > 8)
    return im.crop((int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1))


def scrim(size, stops):
    """A vertical gradient of the page's own dark, as its own layer.

    stops is [(y as a share of height, alpha 0-1), ...] in order. The site
    darkens its hero the same way and for the same reason: a photograph cannot
    be relied on to be dark where the words fall, so the words bring their own.
    """
    w, h = size
    ys = np.linspace(0, 1, h)
    a = np.interp(ys, [s[0] for s in stops], [s[1] for s in stops])
    layer = np.zeros((h, w, 4), "uint8")
    layer[:, :, :3] = np.array(INK, "uint8")
    layer[:, :, 3] = (a * 255).astype("uint8")[:, None]
    return Image.fromarray(layer, "RGBA")


def centred(d, y, text, ft, fill, track=0):
    """Draw one line centred, with optional letter-spacing.

    PIL has no tracking, so spaced text is drawn a glyph at a time. The site
    letterspaces every small-caps line it has; without it the type reads as a
    different brand.
    """
    w = SIZE[0]
    if not track:
        tw = d.textlength(text, font=ft)
        d.text(((w - tw) / 2, y), text, font=ft, fill=fill)
        return
    widths = [d.textlength(c, font=ft) + track for c in text]
    x = (w - (sum(widths) - track)) / 2
    for c, cw in zip(text, widths):
        d.text((x, y), c, font=ft, fill=fill)
        x += cw


def build():
    """Returns (image, marks) where marks is every drawn element as
    (name, top, bottom) so the safe area can be checked rather than eyeballed."""
    marks = []
    canvas = ground(SIZE).convert("RGBA")

    # The figure, hung from the head and run off the bottom edge -- the cut-out
    # stops at her shin because the photograph did, and a figure that ends
    # inside the frame reads as a paper doll.
    fig = cutout(FIGURE)
    th = int(SIZE[1] * 0.76)
    tw = int(round(fig.width * th / fig.height))
    fig = fig.resize((tw, th), Image.LANCZOS)
    # Hung low enough that her head clears the logo. The logo has a drawn woman
    # in it, so any overlap reads as two figures fighting rather than a mark
    # over a photograph -- the first version put the mark across her face.
    canvas.alpha_composite(fig, (int(SIZE[0] * 0.52 - tw / 2), int(SIZE[1] * 0.355)))

    # Dark at both ends, clear through the middle where she is.
    canvas.alpha_composite(scrim(SIZE, [
        (0.00, 0.80), (0.16, 0.30), (0.34, 0.00),
        (0.50, 0.00), (0.58, 0.62), (0.66, 0.90), (0.80, 0.95), (1.00, 0.97)]))

    d = ImageDraw.Draw(canvas)

    logo = Image.open(LOGO).convert("RGBA")
    lw = 380
    logo = logo.resize((lw, int(round(logo.height * lw / logo.width))), Image.LANCZOS)
    ly = SAFE[0] + 10
    canvas.alpha_composite(logo, ((SIZE[0] - lw) // 2, ly))
    marks.append(("logo", ly, ly + logo.height))

    f = font(UI_MED, 30)
    centred(d, 1215, "NOW ONLINE", f, GOLD_HI, track=11)
    marks.append(("eyebrow", 1215, 1215 + 30))

    f = font(DISPLAY, 86)
    for i, line in enumerate(["The boutique where", "fashion meets personality."]):
        centred(d, 1285 + i * 90, line, f, CREAM)
    marks.append(("headline", 1285, 1285 + 90 + 86))

    d.line([(SIZE[0] / 2 - 60, 1490), (SIZE[0] / 2 + 60, 1490)], fill=GOLD, width=2)

    centred(d, 1525, "sthreeboutique.com", font(DISPLAY_R, 72), GOLD_HI)
    marks.append(("address", 1525, 1525 + 72))
    centred(d, 1632, "WESTERN  ·  ETHNIC  ·  JEWELLERY  ·  BAGS",
            font(UI, 25), (196, 186, 175), track=5)
    marks.append(("categories", 1632, 1632 + 25))

    return canvas.convert("RGB").filter(ImageFilter.GaussianBlur(0.3)), marks


def main():
    im, marks = build()
    print("story  %dx%d  figure %s" % (im.width, im.height, FIGURE))
    bad = []
    for name, top, bot in marks:
        room = "ok"
        if top < SAFE[0] or bot > SAFE[1]:
            room = "OUTSIDE the safe area -- Instagram will cover it"
            bad.append(name)
        print("  %-11s %4d - %4d   %s" % (name, top, bot, room))
    if bad:
        print("\nnot written -- %s would be hidden" % ", ".join(bad))
        return 1
    if not APPLY:
        print("report only; rerun with --apply to write assets/social/")
        return 0
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, "story-website.jpg")
    im.save(p, quality=92, optimize=True, progressive=True)
    print("wrote assets/social/story-website.jpg  %d KB" % (os.path.getsize(p) // 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
