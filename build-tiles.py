"""Rebuild the category tiles from chosen product photographs.

    python3 build-tiles.py            report only, writes nothing
    python3 build-tiles.py --apply    rebuild the tiles listed below

The four tiles on the front page are composites, not product images, so an
import never refreshes them: replacing a product photograph leaves its category
tile still showing the old picture. That has caught this project out before, so
the choice of photograph per tile is written down here and can be rerun.

Only the tiles named in TILES are touched. A tile left out keeps whatever it
already has.
"""
import os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "assets", "products")
THUMB = os.path.join(OUT, "thumb")
APPLY = "--apply" in sys.argv

SIZE = (720, 960)
INSET = 64                      # cream margin, matching the product frames
CREAM = (250, 246, 240)
THUMB_SIZE = (360, 480)

# category -> the photograph its tile is built from, and why that one.
TILES = {
    "cat-coord": (
        os.path.join(HERE, "source", "staged", "SB-JWL-08-2.jpg"),
        "the cotton embroidery cordset worn, from the boutique's own catalogue "
        "photograph -- the tile was a flat render because both co-ord products "
        "had only renders until now",
    ),
}


def build(src):
    im = Image.open(src).convert("RGB")
    im.thumbnail((SIZE[0] - INSET, SIZE[1] - INSET), Image.LANCZOS)
    canvas = Image.new("RGB", SIZE, CREAM)
    canvas.paste(im, ((SIZE[0] - im.width) // 2, (SIZE[1] - im.height) // 2))
    return canvas


def main():
    for name, (src, why) in TILES.items():
        if not os.path.exists(src):
            print("  MISS %-14s source not found: %s" % (name, src))
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
    if not APPLY:
        print("\ndry run -- nothing written. add --apply.")


if __name__ == "__main__":
    main()
