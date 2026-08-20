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
import numpy as np
from PIL import Image, ImageChops
from scipy import ndimage

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
        if "hold:true" in row:
            continue          # not on the site, so it needs no card and no crop
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


THUMB = os.path.join(HERE, "assets", "products", "thumb")
THUMB_SIZE = (360, 450)
FULL = os.path.join(HERE, "assets", "products")


FAINT = 4        # alpha below this is invisible haze, not the piece
SPECK = 0.005    # a part holding less of the picture than this is not the piece
KEEP = 0.98      # ... and the trim is refused outright if it would cost this much
SOLID = 0.85     # opaque this far out to its own edges and it is a photograph
INSET = 4        # the one margin, in pixels of the 360x450 card


def alpha_box(im):
    """The piece inside its own file.

    Two things stop Image.getbbox() from finding it. Background removal leaves a
    haze of alpha 1 to 3 out to the file edges, and getbbox() counts any pixel
    above zero, so its box is the whole file and the trim does nothing -- which
    is why the vanilla satchel, 667px wide inside a 1024px file, was being
    framed as though it were 1024. And several cut-outs carry a stray hairline
    pinned against one edge, a column a pixel or two wide that the removal left
    behind; that held the box open just as effectively, and on the petal drop
    earrings it showed on the card as a scratch down the right-hand side.

    So the piece is measured by its parts rather than by its extremes. Anything
    holding less than half a percent of the picture is not the piece: across
    this catalogue the largest stray holds 0.15% and the smallest real part --
    one earring of a pair -- holds 45%, so nothing sits near the line. Should
    that stop being true and the small parts add up to real cloth, the trim is
    refused and the whole file is used instead."""
    a = im.getchannel("A")
    whole = a.getbbox() or (0, 0, im.width, im.height)
    arr = np.asarray(a, dtype=np.int64)
    mask = arr >= FAINT
    if not mask.any():
        return whole
    lab, n = ndimage.label(mask)
    ink = ndimage.sum(arr, lab, range(1, n + 1))
    total = ink.sum()
    if not total:
        return whole
    keep = [i + 1 for i, v in enumerate(ink) if v / total >= SPECK]
    if keep and sum(ink[i - 1] for i in keep) / total >= KEEP:
        mask = np.isin(lab, keep)
    ys, xs = np.where(mask)
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def is_photograph(im):
    """A whole photograph, as against a piece cut out of one.

    A cut-out is the piece and nothing else, so cropping it cuts the piece --
    the bow anklet lost the chain off both ends that way. A photograph, worn on
    the arm or shot close on fabric, is backdrop at its edges and a crop into
    that costs nothing. The picture says which it is without being told: a
    cut-out is full of holes, a photograph is opaque out to its own corners."""
    if im.mode != "RGBA":
        return True
    h = im.getchannel("A").histogram()
    return sum(h[250:]) / max(1, sum(h)) >= SOLID


def make_thumb(path, transparent=False):
    """The piece as large as the card will take it without ever cutting into it.

    The full-size files are letterboxed so the zoom viewer always gets the same
    canvas, and a card that showed that padding too had the piece floating in
    the middle of it. Trim to the piece first, then one rule, with the picture
    deciding which half of it applies:

    a cut-out is fitted whole inside the card, undistorted, with one consistent
    margin -- nothing of the piece is ever cropped;

    a photograph fills the card, centred, because what the crop takes off it is
    somebody's backdrop.

    The flat .jpg copies keep the older shape-based treatment: they have no
    alpha to read, so a composite of several views has to be recognised by being
    wide, and a full-length figure by being tall -- filling that one costs a
    sixth of its height, which is her head and the hem."""
    tw, th = THUMB_SIZE
    if transparent:
        # Cut from the RGBA original so the thumbnail keeps its alpha. The card
        # and the gallery strip sit on cream-alt, and a thumbnail flattened onto
        # cream shows a visible seam against it.
        im = Image.open(path)
        im.load()
        im = im.convert("RGBA")
        im = im.crop(alpha_box(im))
        canvas = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
        if is_photograph(im):
            s = max(tw / im.width, th / im.height)
            r = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
            canvas.paste(r, (-(r.width - tw) // 2, -(r.height - th) // 2))
        else:
            s = min((tw - INSET * 2) / im.width, (th - INSET * 2) / im.height)
            r = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
            canvas.paste(r, ((tw - r.width) // 2, (th - r.height) // 2))
        return canvas

    im = Image.open(path).convert("RGB")
    im = im.crop(trim_box(im))
    canvas = Image.new("RGB", (tw, th), CREAM)
    ar, frame = im.width / im.height, tw / th
    if ar > 1.30:
        s = min((tw - INSET * 2) / im.width, (th - INSET * 2) / im.height)
        r = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
        canvas.paste(r, ((tw - r.width) // 2, (th - r.height) // 2))
    elif ar < frame * 0.88:
        r = im.resize((max(1, round(im.width * th / im.height)), th), Image.LANCZOS)
        canvas.paste(r, ((tw - r.width) // 2, 0))
    else:
        s = max(tw / im.width, th / im.height)
        r = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
        canvas.paste(r, (-(r.width - tw) // 2, -(r.height - th) // 2))
    return canvas


def rebuild_thumbs():
    """Every thumbnail, not just the ones a card happens to show: the category
    tiles and the viewer's gallery strip read from here too.

    A product marked alpha:true is served its .webp, and the page rewrites the
    thumbnail path the same way -- so wherever a full-size .webp exists, its
    thumbnail must exist as .webp as well or the card asks for a file that was
    never written and shows nothing."""
    n = m = 0
    for f in sorted(os.listdir(FULL)):
        if not f.lower().endswith(".jpg"):
            continue
        alpha = os.path.join(FULL, f[:-4] + ".webp")
        cut = make_thumb(alpha, transparent=True) if os.path.exists(alpha) else None
        if APPLY:
            if cut is None:
                make_thumb(os.path.join(FULL, f)).save(
                    os.path.join(THUMB, f), quality=82, optimize=True, progressive=True)
            else:
                # Flatten the cut-out rather than reframing the flat copy, so the
                # two thumbnails of one piece cannot end up framed differently.
                flat = Image.new("RGB", THUMB_SIZE, CREAM)
                flat.paste(cut, (0, 0), cut)
                flat.save(os.path.join(THUMB, f),
                          quality=82, optimize=True, progressive=True)
                cut.save(os.path.join(THUMB, f[:-4] + ".webp"), "WEBP",
                         quality=86, method=6)
        n += 1
        if cut is not None:
            m += 1
    return n, m


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
    thumbs, alphas = rebuild_thumbs()
    print("%d product card(s)%s" % (made, "" if APPLY else " would be built"))
    print("%d thumbnail(s)%s, trimmed to fill the card" % (thumbs, "" if APPLY else " would be rebuilt"))
    print("%d of them also%s as transparent webp" % (alphas, "" if APPLY else " would be"))
    if missing:
        print("%d product(s) had no photograph and were skipped" % missing)
    if APPLY:
        total = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
        print("assets/og/  %.0f KB total, %.0f KB average" % (total / 1024, total / 1024 / max(made, 1)))
    else:
        print("dry run -- nothing written. add --apply.")


if __name__ == "__main__":
    main()
