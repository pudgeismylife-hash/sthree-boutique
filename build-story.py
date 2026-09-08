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
LOGO_LIGHT = os.path.join(HERE, "assets", "logo-web.png")  # ink, for cream grounds

# The cream cards stand a figure on the ground rather than bleeding it off the
# bottom, so the cut-out has to be one that reaches the feet. Two of the sarees
# stop at the shin because the photograph did.
STANDING = "gowns_1-a1"
TILES = ["cat-western", "cat-ethnic", "cat-coord",
         "cat-jewellery", "cat-nails", "cat-bags"]


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


def shadow(canvas, cx, base, width):
    """The soft contact shadow the product cards use. Without it a cut-out on
    cream is a sticker; with it the piece is standing on something."""
    w = int(width)
    h = max(8, int(width * 0.13))
    pad = h * 2
    lay = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(lay).ellipse([pad, pad, pad + w, pad + h], fill=(20, 17, 15, 62))
    lay = lay.filter(ImageFilter.GaussianBlur(h * 0.55))
    canvas.alpha_composite(lay, (int(cx - w / 2 - pad), int(base - h / 2 - pad)))


def rule(d, y, half=60, colour=None):
    d.line([(SIZE[0] / 2 - half, y), (SIZE[0] / 2 + half, y)],
           fill=colour or GOLD, width=2)


def build_cream():
    """The light card: the shop's other face. Everything the site does on a
    product card -- a piece cut out, stood on cream, with a soft shadow under
    it -- at story size. Reads completely differently from the dark one, which
    is the point of having both."""
    marks = []
    canvas = Image.new("RGBA", SIZE, CREAM + (255,))
    d = ImageDraw.Draw(canvas)

    logo = Image.open(LOGO_LIGHT).convert("RGBA")
    lw = 300
    logo = logo.resize((lw, int(round(logo.height * lw / logo.width))), Image.LANCZOS)
    canvas.alpha_composite(logo, ((SIZE[0] - lw) // 2, SAFE[0]))
    marks.append(("logo", SAFE[0], SAFE[0] + logo.height))

    centred(d, 590, "NOW ONLINE", font(UI_MED, 28), GOLD, track=11)
    marks.append(("eyebrow", 590, 618))

    f = font(DISPLAY, 82)
    for i, line in enumerate(["The boutique where", "fashion meets personality."]):
        centred(d, 650 + i * 88, line, f, INK)
    marks.append(("headline", 650, 650 + 88 + 82))

    fig = cutout(STANDING)
    th = 620
    tw = int(round(fig.width * th / fig.height))
    fig = fig.resize((tw, th), Image.LANCZOS)
    base = 1490
    shadow(canvas, SIZE[0] / 2, base, tw * 0.78)
    canvas.alpha_composite(fig, (int(SIZE[0] / 2 - tw / 2), base - th))
    marks.append(("figure", base - th, base))

    rule(d, 1520)
    centred(d, 1548, "sthreeboutique.com", font(DISPLAY_R, 66), GOLD)
    marks.append(("address", 1548, 1614))
    centred(d, 1642, "WESTERN  ·  ETHNIC  ·  JEWELLERY  ·  BAGS",
            font(UI, 22), (138, 129, 119), track=5)
    marks.append(("categories", 1642, 1664))
    return canvas.convert("RGB"), marks


def build_grid():
    """The card that shows the range rather than one piece. The six squares are
    the site's own category tiles, already framed to one rule by build-tiles.py,
    so this stays in step with the front page for free."""
    marks = []
    canvas = Image.new("RGBA", SIZE, CREAM + (255,))
    d = ImageDraw.Draw(canvas)

    logo = Image.open(LOGO_LIGHT).convert("RGBA")
    lw = 320
    logo = logo.resize((lw, int(round(logo.height * lw / logo.width))), Image.LANCZOS)
    canvas.alpha_composite(logo, ((SIZE[0] - lw) // 2, SAFE[0]))
    marks.append(("logo", SAFE[0], SAFE[0] + logo.height))

    # Three across, two down. Six squares stacked two-across ran 1343px tall and
    # pushed the address out under Instagram's reply box -- the safe-area check
    # caught it. Three across is also simply the better shape for an upright frame.
    centred(d, 610, "NOW ONLINE", font(UI_MED, 28), GOLD, track=11)
    marks.append(("eyebrow", 610, 638))

    cols, gap, margin, label = 3, 16, 60, 38
    cell = (SIZE[0] - margin * 2 - gap * (cols - 1)) // cols
    gy = 700
    lf = font(UI, 21)
    for i, name in enumerate(TILES):
        p = os.path.join(HERE, "assets", "products", name + ".jpg")
        if not os.path.exists(p):
            raise SystemExit("missing tile %s -- run build-tiles.py --apply" % name)
        t = Image.open(p).convert("RGB").resize((cell, cell), Image.LANCZOS)
        x = margin + (i % cols) * (cell + gap)
        y = gy + (i // cols) * (cell + gap + label)
        canvas.paste(t, (x, y))
        d.rectangle([x, y, x + cell - 1, y + cell - 1], outline=(226, 217, 205), width=1)
        # A picture of a bangle does not say "anti-tarnish jewellery"; the tile
        # needs its name the same way the front page gives it one.
        cap = name.replace("cat-", "").upper()
        tw = d.textlength(cap, font=lf) + 3 * (len(cap) - 1)
        cx = x + (cell - tw) / 2
        for ch in cap:
            d.text((cx, y + cell + 11), ch, font=lf, fill=(138, 129, 119))
            cx += d.textlength(ch, font=lf) + 3
    rows = (len(TILES) + cols - 1) // cols
    grid_h = rows * (cell + label) + (rows - 1) * gap
    marks.append(("tiles", gy, gy + grid_h))

    ty = gy + grid_h + 46
    rule(d, ty)
    centred(d, ty + 28, "sthreeboutique.com", font(DISPLAY_R, 64), GOLD)
    marks.append(("address", ty + 28, ty + 92))
    return canvas.convert("RGB"), marks


def build(sticker=False):
    """Returns (image, marks): every drawn element as (name, top, bottom), so
    the safe area is checked rather than eyeballed.

    sticker=True leaves the foot of the safe area empty and prints no address.
    A picture cannot be tapped -- Instagram's own link sticker carries the link
    and has to be laid on top in the app -- so that version reserves a clean
    band for it and says "tap the link below" instead of naming the address,
    which the sticker will show anyway. The other version prints the address,
    because a WhatsApp status and a printed card have nothing to tap.
    """
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
        (0.50, 0.00), (0.555, 0.70), (0.63, 0.92), (0.78, 0.95), (1.00, 0.97)]
        if sticker else [
        (0.00, 0.80), (0.16, 0.30), (0.34, 0.00),
        (0.50, 0.00), (0.58, 0.62), (0.66, 0.90), (0.80, 0.95), (1.00, 0.97)]))

    d = ImageDraw.Draw(canvas)

    logo = Image.open(LOGO).convert("RGBA")
    lw = 380
    logo = logo.resize((lw, int(round(logo.height * lw / logo.width))), Image.LANCZOS)
    ly = SAFE[0] + 10
    canvas.alpha_composite(logo, ((SIZE[0] - lw) // 2, ly))
    marks.append(("logo", ly, ly + logo.height))

    top = 1120 if sticker else 1215
    centred(d, top, "NOW ONLINE", font(UI_MED, 30), GOLD_HI, track=11)
    marks.append(("eyebrow", top, top + 30))

    hy = top + 70
    f = font(DISPLAY, 86)
    for i, line in enumerate(["The boutique where", "fashion meets personality."]):
        centred(d, hy + i * 90, line, f, CREAM)
    marks.append(("headline", hy, hy + 90 + 86))

    ry = hy + 205
    d.line([(SIZE[0] / 2 - 60, ry), (SIZE[0] / 2 + 60, ry)], fill=GOLD, width=2)

    cats = "WESTERN  ·  ETHNIC  ·  JEWELLERY  ·  BAGS"
    if sticker:
        centred(d, ry + 30, cats, font(UI, 25), (196, 186, 175), track=5)
        marks.append(("categories", ry + 30, ry + 55))
        centred(d, ry + 105, "TAP THE LINK BELOW", font(UI_MED, 26), GOLD, track=9)
        marks.append(("cue", ry + 105, ry + 131))
        # Left deliberately clear: this is where the link sticker is laid in
        # the app. Reported as an element so the safe-area check covers it too.
        marks.append(("sticker space", ry + 175, SAFE[1]))
    else:
        centred(d, ry + 35, "sthreeboutique.com", font(DISPLAY_R, 72), GOLD_HI)
        marks.append(("address", ry + 35, ry + 107))
        centred(d, ry + 142, cats, font(UI, 25), (196, 186, 175), track=5)
        marks.append(("categories", ry + 142, ry + 167))

    return canvas.convert("RGB").filter(ImageFilter.GaussianBlur(0.3)), marks


CARDS = [
    ("story-website.jpg", lambda: build(False),
     "dark, address printed -- WhatsApp status, print, anywhere untappable"),
    ("story-website-link.jpg", lambda: build(True),
     "dark, room left for Instagram's link sticker"),
    ("story-cream.jpg", build_cream,
     "light editorial -- a piece stood on cream, the site's card language"),
    ("story-grid.jpg", build_grid,
     "the six categories -- shows the range rather than one piece"),
]


def main():
    rc = 0
    for name, make, why in CARDS:
        im, marks = make()
        print("%s  %dx%d  -- %s" % (name, im.width, im.height, why))
        bad = []
        for label, top, bot in marks:
            room = "ok"
            if top < SAFE[0] or bot > SAFE[1]:
                room = "OUTSIDE the safe area -- Instagram will cover it"
                bad.append(label)
            print("    %-14s %4d - %4d   %s" % (label, top, bot, room))
        if bad:
            print("    not written -- %s would be hidden\n" % ", ".join(bad))
            rc = 1
            continue
        if not APPLY:
            print("    report only; rerun with --apply\n")
            continue
        os.makedirs(OUT, exist_ok=True)
        p = os.path.join(OUT, name)
        im.save(p, quality=92, optimize=True, progressive=True)
        print("    wrote assets/social/%s  %d KB\n" % (name, os.path.getsize(p) // 1024))
    return rc


if __name__ == "__main__":
    sys.exit(main())
