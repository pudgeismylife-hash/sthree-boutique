"""Rebuild the hero band from the boutique's own photographs.

    python3 build-hero.py            report only, writes nothing
    python3 build-hero.py --apply    write assets/hero-wide.jpg and hero-narrow.jpg

The hero is a composite, not a product image, so no import ever refreshes it: a
photograph can be replaced everywhere else on the site and the hero will keep
showing the old one. Writing the panel choices down here makes that repeatable
instead of remembered.

Only the boutique's own photographs may appear. Every generated render is
refused by name below rather than by good intentions -- the band showed a
generated butterfly armcuff on both desktop and mobile, which is exactly the
substitution the fidelity rule exists to prevent.

The layout is unchanged: four panels wide, two narrow, hairline cream gaps.
This rebuilds the band, it does not redesign it.
"""
import json, os, sys
from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, "assets", "products")
OUT = os.path.join(HERE, "assets")
LOCK = os.path.join(HERE, "product-image-lock.json")
APPLY = "--apply" in sys.argv

CREAM = (250, 246, 240)
GAP = 6

# Each panel names the photograph it uses, where to anchor the crop, and why
# that piece. "top" keeps heads and necklines in frame on a full-length figure;
# "mid" centres a close-up.
WIDE = (1600, 580, [
    ("sarees_2.jpg",                        "top", "Ethnic — silk designer mirror handwork saree"),
    ("gowns_1.jpg",                         "top", "Western — linen cotton dress with belt"),
    ("cloth_section_western_wear_2-a2.jpg", "top", "Co-ord — cotton embroidery cordset, her own photograph, "
                                                  "replacing the generated armcuff render"),
    ("earring_1.jpg",                       "mid", "Jewellery — Starfish studs, worn. Chosen over the leaf\n                                                   studs because a close-up of a pair laid flat loses both\n                                                   edges to a tall panel, and worn matches the other three"),
])
NARROW = (880, 620, [
    ("sarees_2.jpg",  "top", "Ethnic — the same saree that opens the wide band"),
    ("earring_1.jpg", "mid", "Jewellery — keeps a piece of jewellery on the phone, where the "
                             "generated armcuff used to sit; jewellery is 17 of the 25 products"),
])


def customer_only(files):
    """Refuse any photograph the lock marks as a generated render."""
    lock = json.load(open(LOCK, encoding="utf-8"))["products"]
    banned = {}
    for code, v in lock.items():
        if v.get("productKey") and v.get("sourceReview"):
            for img in v.get("images", []):
                banned[img] = (code, v["productKey"])
    bad = [(f, banned[f]) for f in files if f in banned]
    if bad:
        for f, (code, key) in bad:
            print("  REFUSED %s — %s (%s) is a generated render, not her photograph" % (f, code, key))
        sys.exit("FAIL  the hero may only use the boutique's own photographs")


def trim_box(im, tol=12):
    """The picture inside its flat cream border. Image.getbbox is no use here:
    it trims black, and every stored product photograph is letterboxed on cream.
    Skipping this leaves the piece floating small in the middle of the panel."""
    bg = Image.new("RGB", im.size, im.getpixel((1, 1)))
    mask = ImageChops.difference(im, bg).convert("L").point(lambda p: 255 if p > tol else 0)
    return mask.getbbox() or (0, 0, im.width, im.height)


def panel(path, w, h, anchor):
    """Fill the panel with the photograph, cropping rather than distorting."""
    im = Image.open(path).convert("RGB")
    im = im.crop(trim_box(im))
    s = max(w / im.width, h / im.height)
    im = im.resize((max(1, round(im.width * s)), max(1, round(im.height * s))), Image.LANCZOS)
    x = (im.width - w) // 2
    y = 0 if anchor == "top" else (im.height - h) // 2
    return im.crop((x, y, x + w, y + h))


def band(spec):
    w, h, panels = spec
    canvas = Image.new("RGB", (w, h), CREAM)
    n = len(panels)
    pw = (w - GAP * (n - 1)) // n
    x = 0
    for i, (f, anchor, _why) in enumerate(panels):
        width = pw if i < n - 1 else w - x
        canvas.paste(panel(os.path.join(P, f), width, h, anchor), (x, 0))
        x += width + GAP
    return canvas


def main():
    used = [f for spec in (WIDE, NARROW) for f, _, _ in spec[2]]
    missing = [f for f in used if not os.path.exists(os.path.join(P, f))]
    if missing:
        sys.exit("FAIL  missing photograph(s): " + ", ".join(missing))
    customer_only(used)

    for name, spec in (("hero-wide", WIDE), ("hero-narrow", NARROW)):
        w, h, panels = spec
        print("%s  %dx%d, %d panels" % (name, w, h, len(panels)))
        for f, anchor, why in panels:
            print("    %-38s %-4s %s" % (f, anchor, why))
        if APPLY:
            band(spec).save(os.path.join(OUT, name + ".jpg"),
                            quality=86, optimize=True, progressive=True)
            print("    written")
    if not APPLY:
        print("\ndry run -- nothing written. add --apply.")


if __name__ == "__main__":
    main()
