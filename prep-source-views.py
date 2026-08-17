"""Turn the boutique's catalogue photographs into views the importer can take.

    python3 prep-source-views.py              report only, writes nothing
    python3 prep-source-views.py --apply      write source/staged/

Each catalogue page is one photograph sitting on a white sheet with the product
name and price printed underneath. The printed caption cannot go on the website
-- it would put "Price - 950/-" inside the product picture -- so it is found and
cut away here, along with the white sheet around it.

Several pages hold more than one genuine view of the same garment: the kaftan
page shows the kaftan and its inner side by side, the cordset page shows it worn
and on hangers. Those halves are cut apart into separate views. Every view is a
crop of the customer's own photograph. Nothing is generated, extended or
repainted, so a view can only ever show what the camera actually saw.

Output is named the way import-photos.js expects, <CODE>-1/-2/-3.jpg, so the
existing importer does the mapping, locking and wiring.
"""
import json, os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source", "extracted")
OUT = os.path.join(HERE, "source", "staged")
APPLY = "--apply" in sys.argv

WHITE = 238          # a pixel this bright in all channels counts as the sheet
INK = 0.012          # fraction of a row that must be ink for it to be content


def content_rows(im):
    """Row ranges that hold something other than the white sheet."""
    g = im.convert("L")
    w, h = g.size
    px = g.load()
    runs, start = [], None
    for y in range(h):
        ink = sum(1 for x in range(0, w, 3) if px[x, y] < WHITE)
        solid = ink > (w / 3) * INK
        if solid and start is None:
            start = y
        elif not solid and start is not None:
            runs.append((start, y))
            start = None
    if start is not None:
        runs.append((start, h))
    return runs


def content_cols(im, top, bot):
    g = im.convert("L")
    w, _ = g.size
    px = g.load()
    xs = [x for x in range(w)
          if sum(1 for y in range(top, bot, 3) if px[x, y] < WHITE) > ((bot - top) / 3) * INK]
    return (min(xs), max(xs) + 1) if xs else (0, w)


def photo_box(path):
    """The photograph itself, with the printed caption and sheet removed.

    The caption is a short band of text under a tall band of picture, so the
    tallest run of content rows is the photograph and anything below it is
    wording that must not reach the website."""
    im = Image.open(path).convert("RGB")
    runs = content_rows(im)
    if not runs:
        return im, None
    top, bot = max(runs, key=lambda r: r[1] - r[0])
    left, right = content_cols(im, top, bot)
    dropped = [r for r in runs if r[0] >= bot]
    return im.crop((left, top, right, bot)), dropped


def split_h(img, at=0.5, gap=0.012):
    """Cut a side-by-side composite into its left and right halves."""
    w, h = img.size
    g = int(w * gap)
    return img.crop((0, 0, int(w * at) - g, h)), img.crop((int(w * at) + g, 0, w, h))


def crop_frac(img, l, t, r, b):
    w, h = img.size
    return img.crop((int(w * l), int(h * t), int(w * r), int(h * b)))


# The frame the website fits a product photograph into. Views are enlarged to
# fill it here rather than left small: the importer only ever shrinks, so a
# narrow crop would otherwise sit as a stamp in the middle of a cream page.
FRAME = (720 - 64, 900 - 64)


def to_frame(img):
    s = min(FRAME[0] / img.width, FRAME[1] / img.height)
    if s <= 1:
        return img, 1.0
    return img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS), s


# Which views come out of which page. Every entry is a crop of the same
# photograph, so all views are necessarily the same physical garment.
#
# There is no invented macro shot here. A close crop of a 400px photograph is
# only about 120px across, which enlarges to mush, so a piece gets the views its
# photograph genuinely holds and no filler.
def views_kaftan(p):
    left, right = split_h(p)
    # The product is "kaftan with inner", so the hero shows both pieces.
    return [("both pieces as supplied", p),
            ("the kaftan", right),
            ("the inner", left)]


def views_cordset(p):
    worn, hung = split_h(p)
    return [("both views as supplied", p),
            ("worn", worn),
            ("top and trousers on hangers", hung)]


def views_palazzo(p):
    # One photograph only, so two honest views: the whole thing, and a closer
    # look at the garment away from the street behind it.
    return [("worn, full length", p),
            ("closer on the top and its zari work", crop_frac(p, .12, .10, .98, .72))]


PLAN = {
    "Cloth_section_western_wear_p1": ("SB-JWL-07", views_kaftan),
    "Cloth_section_western_wear_p2": ("SB-JWL-08", views_cordset),
    "Cloth_section_western_wear_p3": ("SB-JWL-09", views_palazzo),
}


def main():
    meta = json.load(open(os.path.join(HERE, "source", "customer-source.json"),
                          encoding="utf-8"))["sources"]
    if APPLY:
        os.makedirs(OUT, exist_ok=True)
    made = 0
    for sid, (code, fn) in PLAN.items():
        path = os.path.join(SRC, sid + ".jpeg")
        if not os.path.exists(path):
            print("  MISS %s -- run extract-source.py --apply first" % sid)
            continue
        photo, dropped = photo_box(path)
        cap = meta.get(sid, {}).get("caption", "?")
        print("%s  <- %s" % (code, sid))
        print("     caption cut away : %s (%d band(s) below the picture)"
              % (cap, len(dropped or [])))
        print("     photograph       : %dx%d" % photo.size)
        for n, (what, img) in enumerate(fn(photo), 1):
            name = "%s-%d.jpg" % (code, n)
            sized, scale = to_frame(img)
            print("     %-2s %-36s %4dx%-4d -> %4dx%-4d  %s"
                  % (n, what, img.width, img.height, sized.width, sized.height,
                     ("enlarged x%.2f" % scale) if scale > 1 else "as shot"))
            if APPLY:
                sized.save(os.path.join(OUT, name), quality=95, subsampling=0)
                made += 1
    if APPLY:
        print("\nwrote %d view(s) to source/staged/" % made)
        print("next:  node import-photos.js source/staged")
    else:
        print("\ndry run -- nothing written. add --apply.")


if __name__ == "__main__":
    main()
