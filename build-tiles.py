"""Rebuild the "Shop by category" tiles from chosen product photographs.

    python3 build-tiles.py            report only, writes nothing
    python3 build-tiles.py --apply    rebuild the tiles listed below

The five tiles on the front page are composites, not product images, so an
import never refreshes them: replacing a product photograph leaves its category
tile still showing the old picture. That has caught this project out before, so
the choice of photograph per tile is written down here and can be rerun.

Every tile is built the same way -- the piece scaled to the full height of the
tile and centred on cream. A cut-out is 2:3 and the tile is 3:4, so that leaves
a hand's width of cream down either side and crops nothing. Filling instead
would take a tenth of the height off, which on a full-length figure is her head
and the hem.

Only the tiles named in TILES are touched. A tile left out keeps whatever it
already has.
"""
import json, os, sys
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "products")
THUMB = os.path.join(OUT, "thumb")
LOCK = os.path.join(HERE, "product-image-lock.json")
APPLY = "--apply" in sys.argv

SIZE = (720, 960)
CREAM = (250, 246, 240)
THUMB_SIZE = (360, 480)

# category -> the photograph its tile is built from, and why that one.
TILES = {
    "cat-western": (
        os.path.join(OUT, "gowns_1-a1.jpg"),
        "the black linen dress, her own photograph, as a cut-out -- the tile "
        "was a room-set shot of the same dress, which was the only lifestyle "
        "picture among five tiles and read as a different shop",
    ),
    "cat-ethnic": (
        os.path.join(OUT, "sarees_3-a1.jpg"),
        "the black sequin saree with the copper pallu, from the renamed batch "
        "-- the strongest of the five sarees at tile size, being high contrast "
        "rather than fine print that turns to mush when small",
    ),
    "cat-coord": (
        os.path.join(OUT, "cloth_section_western_wear_2-a1.jpg"),
        "the brown cutwork cordset, from the renamed batch. Same piece the tile "
        "already showed, but the old one was inset inside its own cream margin "
        "and sat small in the middle of the tile",
    ),
    "cat-jewellery": (
        os.path.join(OUT, "earring_3.jpg"),
        "the petal drop earrings, straight from her own catalogue -- gold on "
        "cream silk, which is the only jewellery picture that still reads at "
        "tile size and the only one whose colour belongs beside the clothes. "
        "The tile was the butterfly armcuff, one of the six jewellery pictures "
        "flagged REVIEW_REQUIRED -- a render, not a photograph of her stock, so "
        "it had no business being the face of the category",
    ),
    "cat-nails": (
        os.path.join(OUT, "pink-heart-3d-press-on-nails-a1.jpg"),
        "the pink heart set, from the renamed batch -- the newest stock, and "
        "the clearest at tile size",
    ),
}


def refuses_render(path):
    """A tile may not show a picture flagged as not being her stock."""
    if not os.path.exists(LOCK):
        return None
    lock = json.load(open(LOCK, encoding="utf-8")).get("products", {})
    name = os.path.basename(path)
    for code, v in lock.items():
        if name in (v.get("images") or []) and v.get("sourceReview"):
            return code
    return None


def trim_box(im, tol=12):
    """The picture inside its flat border, whatever colour that border is.

    Image.getbbox is no use: it trims black, and these margins are cream or the
    white of her catalogue pages."""
    bg = Image.new("RGB", im.size, im.getpixel((1, 1)))
    mask = ImageChops.difference(im, bg).convert("L").point(lambda p: 255 if p > tol else 0)
    return mask.getbbox() or (0, 0, im.width, im.height)


def build(src):
    """The piece at full tile height, centred on cream.

    Trimmed to the piece first. A necklace photographed small in the middle of
    its own white page would otherwise arrive at the tile still small, and the
    tile would be mostly cream."""
    im = Image.open(src).convert("RGB")
    im = im.crop(trim_box(im))
    tw, th = SIZE
    s = th / im.height
    w = max(1, round(im.width * s))
    canvas = Image.new("RGB", SIZE, CREAM)
    if w <= tw:
        canvas.paste(im.resize((w, th), Image.LANCZOS), ((tw - w) // 2, 0))
        return canvas
    # Wider than the tile once it is that tall -- a pair of earrings, a set of
    # nails. Letterboxing those leaves them floating in a short band while the
    # clothing tiles beside them run full height, and the row reads broken. Fill
    # instead and take the crop off the sides: a tile is a way in to the
    # category, not the picture of the piece, which is on the product itself.
    r = im.resize((w, th), Image.LANCZOS)
    canvas.paste(r, (-(w - tw) // 2, 0))
    return canvas


def main():
    bad = 0
    for name, (src, why) in TILES.items():
        if not os.path.exists(src):
            print("  MISS %-14s source not found: %s" % (name, src))
            bad += 1
            continue
        flagged = refuses_render(src)
        if flagged:
            print("  FAIL %-14s %s is flagged %s -- not her stock" % (
                name, os.path.basename(src), flagged))
            bad += 1
            continue
        tile = build(src)
        print("%-14s <- %s" % (name, os.path.relpath(src, HERE)))
        print("               %s" % why)
        if APPLY:
            tile.save(os.path.join(OUT, name + ".jpg"),
                      quality=86, optimize=True, progressive=True)
            tile.resize(THUMB_SIZE, Image.LANCZOS).save(
                os.path.join(THUMB, name + ".jpg"),
                quality=82, optimize=True, progressive=True)
            print("               written, full and thumb")
    if bad:
        sys.exit("\n%d tile(s) could not be built" % bad)
    if not APPLY:
        print("\ndry run -- nothing written. add --apply.")


if __name__ == "__main__":
    main()
