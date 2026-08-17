"""Build the link-preview card for every product.

    python3 build-og-images.py            report only, writes nothing
    python3 build-og-images.py --apply    write assets/og/

When a product link is pasted into WhatsApp, the preview comes from the card
named in that page's og:image. WhatsApp gives a landscape image the wide
treatment and a portrait one a small square thumbnail, so these are built at
1200x630 -- the 1.91:1 shape it expects -- even though every product photograph
is portrait.

No text is drawn into the card. WhatsApp already prints the name and price
beside the picture from og:title and og:description, so painting them in as
well would duplicate them, and it would tie the build to a font that is not on
every machine. The card is the boutique's mark and the piece, nothing else.

Output is committed, so `node build-hosted.js` stays free of any dependency.
Rerun this only when a product photograph changes.
"""
import os, re, sys
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "sthree-boutique.html")
OUT = os.path.join(HERE, "assets", "og")
LOGO = os.path.join(HERE, "assets", "logo-web.png")
APPLY = "--apply" in sys.argv

W, H = 1200, 630
CREAM = (250, 246, 240)
PAD = 34                 # breathing room top and bottom
GAP = 56                 # between the mark and the piece


def catalogue():
    """Read the arrivals list without running the page's JavaScript."""
    html = open(SRC, encoding="utf-8").read()
    block = re.search(r"const arrivals = \[([\s\S]*?)\n\];", html)
    if not block:
        sys.exit("FAIL  could not find the arrivals list")
    # Photographs are written as P+"name.jpg", so the prefix has to come from
    # the page rather than being assumed here.
    pref = re.search(r'const P = "([^"]+)"', html)
    if not pref:
        sys.exit("FAIL  could not find the product image prefix")
    prefix = pref.group(1)
    items = []
    for m in re.finditer(r"\{[^{}]*\}", block.group(1)):
        row = m.group(0)
        key = re.search(r'key:"([^"]+)"', row)
        cat = re.search(r'cat:"([^"]+)"', row)
        imgs = re.search(r"images:\[([^\]]*)\]", row)
        if not key or not imgs:
            continue
        first = re.search(r'P\+"([^"]+)"', imgs.group(1))
        if not first:
            continue
        items.append((key.group(1), prefix + first.group(1), cat.group(1) if cat else ""))
    return items


def trim_box(im, tol=12):
    """The picture inside its flat border, whatever colour that border is."""
    bg = Image.new("RGB", im.size, im.getpixel((1, 1)))
    mask = ImageChops.difference(im, bg).convert("L").point(lambda p: 255 if p > tol else 0)
    return mask.getbbox() or (0, 0, im.width, im.height)


def card(photo_path, logo):
    canvas = Image.new("RGB", (W, H), CREAM)
    photo = Image.open(photo_path).convert("RGB")
    # The stored photograph is already letterboxed on cream, so trim it back to
    # the picture before laying it out, or the card inherits a second margin and
    # the piece ends up small in the middle of it. Image.getbbox is no use here:
    # it trims black, and this margin is cream.
    photo = photo.crop(trim_box(photo))

    mark = logo.copy()
    mw = 300
    mark = mark.resize((mw, max(1, round(mark.height * mw / mark.width))), Image.LANCZOS)

    # Fit the piece to the space actually left beside the mark, in both
    # directions. Height alone is not enough: a wide photograph such as a
    # bracelet laid flat then runs past the edge and pushes the mark off the card.
    box_w = W - PAD * 2 - mark.width - GAP
    box_h = H - PAD * 2
    scale = min(box_w / photo.width, box_h / photo.height)
    photo = photo.resize((max(1, round(photo.width * scale)),
                          max(1, round(photo.height * scale))), Image.LANCZOS)

    total = mark.width + GAP + photo.width
    x = (W - total) // 2
    canvas.paste(mark, (x, (H - mark.height) // 2), mark if mark.mode == "RGBA" else None)
    canvas.paste(photo, (x + mark.width + GAP, (H - photo.height) // 2))
    return canvas


HERO = os.path.join(HERE, "assets", "hero")
HERO_SIZE = (440, 550)          # 4:5, covers the hero cell at either breakpoint


def hero_crop(photo_path, cat=""):
    """A tight portrait crop for the hero band.

    The stored photographs are letterboxed on cream, and the margin differs for
    every one, so the band cannot just cover-crop them: the piece ends up small
    inside its own border, and that cream going translucent over the dark ground
    turns the whole band grey. Trim to the picture first, then fill."""
    im = Image.open(photo_path).convert("RGB")
    im = im.crop(trim_box(im))
    tw, th = HERO_SIZE
    s = max(tw / im.width, th / im.height)
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    x = (im.width - tw) // 2
    # A full-length figure is cropped near the top so the face stays in; a
    # jewellery close-up is centred, because anchoring it high lands on hair and
    # ear and loses the piece entirely.
    y = (im.height - th) // 2 if cat == "jewellery" else round(im.height * 0.06)
    y = min(max(0, y), max(0, im.height - th))
    return im.crop((x, y, x + tw, y + th))


def main():
    items = catalogue()
    logo = Image.open(LOGO).convert("RGBA")
    if APPLY:
        os.makedirs(OUT, exist_ok=True)
        os.makedirs(HERO, exist_ok=True)
    made = missing = 0
    for key, rel, cat in items:
        src = os.path.join(HERE, rel)
        if not os.path.exists(src):
            print("  MISS %-32s no photograph at %s" % (key, rel))
            missing += 1
            continue
        if APPLY:
            card(src, logo).save(os.path.join(OUT, key + ".jpg"),
                                 quality=84, optimize=True, progressive=True)
            hero_crop(src, cat).save(os.path.join(HERO, key + ".jpg"),
                                quality=80, optimize=True, progressive=True)
        made += 1
    print("%d product card(s)%s" % (made, "" if APPLY else " would be built"))
    if missing:
        print("%d product(s) had no photograph and were skipped" % missing)
    if APPLY:
        total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
        print("assets/og/  %.0f KB total, %.0f KB average" % (total / 1024, total / 1024 / max(made, 1)))
    else:
        print("dry run -- nothing written. add --apply.")


if __name__ == "__main__":
    main()
