"""Rebuild the "Shop by category" tiles from chosen product photographs.

    python3 build-tiles.py            report only, writes nothing
    python3 build-tiles.py --apply    rebuild the tiles listed below

The five tiles on the front page are composites, not product images, so an
import never refreshes them: replacing a product photograph leaves its category
tile still showing the old picture. That has caught this project out before, so
the choice of photograph per tile is written down here and can be rerun.

Every tile is framed by the same rule the product cards use: the piece trimmed
out of its own padding and then fitted whole, as large as the tile will take it,
centred on cream. Nothing of a cut-out is ever cropped -- a cut-out is 2:3 and
the tile is 3:4, so it carries a hand's width of cream down either side, and
filling instead would take a tenth of the height off, which on a full-length
figure is her head and the hem.

Only the tiles named in TILES are touched. A tile left out keeps whatever it
already has.
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageChops
from scipy import ndimage

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
        os.path.join(OUT, "armcuff_1-a1.jpg"),
        "the butterfly armcuff, chosen by the owner for this tile. Its review "
        "is settled -- SB-JWL-03 was matched against her own photograph in "
        "armcuff.pdf and cleared -- so unlike the bracelet that briefly sat "
        "here, this one needs no exception",
    ),
    "cat-nails": (
        os.path.join(OUT, "pink-heart-3d-press-on-nails-a1.jpg"),
        "the pink heart set, from the renamed batch -- the newest stock, and "
        "the clearest at tile size. Filled rather than fitted: it is a grid of "
        "nails, so a crop at the sides loses nothing",
        False, True,
    ),
    "cat-bags": (
        os.path.join(OUT, "mk-signature-satchel-brown-a1.jpg"),
        "the Michael Kors signature satchel in brown monogram with gold charm",
        True, False,
    ),
}


def refuses_render(path):
    """A tile may not show a picture flagged as not being her stock."""
    if not os.path.exists(LOCK):
        return None
    lock = json.load(open(LOCK, encoding="utf-8")).get("products", {})
    name = os.path.basename(path)
    for code, v in lock.items():
        if name not in (v.get("images") or []):
            continue
        sr = v.get("sourceReview")
        # A review that has been answered is not a standing objection. Testing
        # for the record rather than its state is what silently broke this build
        # all morning: the armcuff was settled and the tile still refused it, so
        # no tile was written and the front page kept yesterday's picture.
        if sr and sr.get("state") == "REVIEW_REQUIRED":
            return code
    return None


def not_transparent(path):
    """A tile may only be built from a piece that has a real cut-out.

    Every tile source names a .jpg, because that is what the build reads, but
    each of those is the flattened copy of a transparent original. If the .webp
    beside it is missing the source is a flat photograph, and a flat photograph
    put on a tile is a rectangle of somebody's backdrop sitting on cream."""
    return not os.path.exists(path[:-4] + ".webp")


def trim_box(im, tol=12):
    """The picture inside its flat border, whatever colour that border is.

    Image.getbbox is no use: it trims black, and these margins are cream or the
    white of her catalogue pages."""
    bg = Image.new("RGB", im.size, im.getpixel((1, 1)))
    mask = ImageChops.difference(im, bg).convert("L").point(lambda p: 255 if p > tol else 0)
    return mask.getbbox() or (0, 0, im.width, im.height)


# The framing below is the same rule the product cards use, and the reasoning
# for it is written out once, in build-og-images.py. It is repeated here rather
# than imported because this file's name has a hyphen in it.
FAINT = 4        # alpha below this is invisible haze, not the piece
SPECK = 0.005    # a part holding less of the picture than this is not the piece
KEEP = 0.98      # ... and the trim is refused outright if it would cost this much
SOLID = 0.85     # opaque this far out to its own edges and it is a photograph
INSET = 8        # the one margin, in pixels of the 720x960 tile


def alpha_box(im):
    """The piece inside its own file, past the haze and the stray hairlines that
    background removal leaves out at the edges."""
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
    """A whole photograph, as against a piece cut out of one."""
    h = im.getchannel("A").histogram()
    return sum(h[250:]) / max(1, sum(h)) >= SOLID


def build(src, fill=False):
    """The piece as large as the tile will take it, centred on cream.

    Read from the cut-out beside the named .jpg, not the .jpg itself: the flat
    copy is letterboxed, and its border is not always the same cream, so a tile
    built from it arrives with the piece small inside its own margin.

    A cut-out is fitted whole and never cropped -- a bracelet with a sixth off
    each side is a fragment of a clasp with no way to tell what it was. A whole
    photograph, and anything set to fill here, covers the tile instead, because
    what the crop takes off those is backdrop or more of the same pattern."""
    im = Image.open(src[:-4] + ".webp")
    im.load()
    im = im.convert("RGBA")
    im = im.crop(alpha_box(im))
    tw, th = SIZE
    canvas = Image.new("RGB", SIZE, CREAM)
    if fill or is_photograph(im):
        s = max(tw / im.width, th / im.height)
        r = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
        canvas.paste(r, (-(r.width - tw) // 2, -(r.height - th) // 2), r)
        return canvas
    s = min((tw - INSET * 2) / im.width, (th - INSET * 2) / im.height)
    r = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    canvas.paste(r, ((tw - r.width) // 2, (th - r.height) // 2), r)
    return canvas


def main():
    bad = 0
    for name, entry in TILES.items():
        src, why = entry[0], entry[1]
        allow_flagged = len(entry) > 2 and entry[2]
        fill = len(entry) > 3 and entry[3]
        if not os.path.exists(src):
            print("  MISS %-14s source not found: %s" % (name, src))
            bad += 1
            continue
        if not_transparent(src):
            print("  FAIL %-14s %s has no transparent original" % (
                name, os.path.basename(src)))
            bad += 1
            continue
        flagged = refuses_render(src)
        if flagged and not allow_flagged:
            print("  FAIL %-14s %s is flagged %s -- not her stock" % (
                name, os.path.basename(src), flagged))
            bad += 1
            continue
        if flagged:
            print("  NOTE %-14s %s is still flagged %s; allowed by instruction" % (
                name, os.path.basename(src), flagged))
        tile = build(src, fill)
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
