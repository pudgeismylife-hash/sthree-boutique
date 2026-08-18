"""Bring the boutique's renamed photo set into assets/products/.

    python3 import-updated-photos.py            report only, writes nothing
    python3 import-updated-photos.py --apply    write the product files

The source is source/updated-photos/, whose filenames are the mapping:

    <product>-front.png  <product>-3quarter.png  <product>-back.png   clothing
    <product>.png                                                     nails

Every file is a 1024x1536 (nails 1536x1024) cut-out with a transparent
background. Nothing here resizes them: the site's zoom viewer is the reason the
full pixels are kept, and the earlier catalogue's 900px files are the ones that
look soft next to these, not the other way round. Each view is written twice,
following the convention the rest of assets/products/ already uses:

    <key>-a1.webp   transparent, what a modern browser is served
    <key>-a1.jpg    flattened on cream, the fallback

MAP is written out by hand rather than derived, because four of these files
replace photographs of pieces already in the catalogue and five do not, and that
is not something a filename can tell you. Each line records which and why. A
product whose images come from here is marked recreated:true in the lock file --
these are AI recreations of the boutique's own catalogue photographs, not
photographs of the stock, and the lock is where that has to stay visible.
"""
import json, os, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source", "updated-photos")
OUT = os.path.join(HERE, "assets", "products")
LOCK = os.path.join(HERE, "product-image-lock.json")
APPLY = "--apply" in sys.argv

CREAM = (250, 246, 240)
VIEWS = ["front", "3quarter", "back"]

# slug -> (catalogue key, what this is)
#
# REPLACES: the piece is already in the catalogue under that key, and these
# three views replace its single photograph. Verified by eye against the stored
# photograph, one pair at a time -- colour, motif, neckline, border and hem all
# match. Her name and price stay; only the pictures change.
#
# NEW: nothing in the catalogue matches, so the slug becomes the key. No price
# is invented for these; they go up as "Price on WhatsApp" until she gives one.
MAP = {
    "pink-striped-saree": (
        "sarees_1", "REPLACES",
        "magenta saree, navy and gold striped pallu -- her Poly cotton zari "
        "weaving saree, previously one photograph against a yellow wall"),
    "black-brown-border-saree": (
        "sarees_3", "REPLACES",
        "black sequin saree with a copper pallu and scalloped border -- her "
        "Georgette sequin embroidery saree, previously one photograph on a "
        "hanger against an orange wall"),
    "brown-floral-salwar-suit": (
        "cloth_section_western_wear_2", "REPLACES",
        "brown cutwork set, scalloped floral hem on both top and palazzo -- her "
        "Cotton embroidery elastic-hand cordset"),
    "black-gold-embroidered-kurta-set": (
        "cloth_section_western_wear_3", "REPLACES",
        "charcoal kurta, gold outline florals down the front, matching palazzo "
        "-- her Palazzo cordset with inner lining"),
    "navy-blue-red-printed-kurta-set": (
        "navy-blue-red-printed-kurta-set", "NEW",
        "navy kurta with a red and white printed panel and tassels; no piece in "
        "the catalogue looks like it"),
    "pink-printed-salwar-suit": (
        "pink-printed-salwar-suit", "NEW",
        "pink kurta and palazzo with a printed dupatta. Close to her Round-neck "
        "polyester kaftan with inner in colour and print, but not the same "
        "garment -- the kaftan's wing sleeves and gold embroidered neckline are "
        "not here, the print is a narrow dupatta instead. Kept separate rather "
        "than replacing the kaftan's photographs, which would show a customer "
        "something she does not sell"),
    "pink-heart-3d-press-on-nails": (
        "pink-heart-3d-press-on-nails", "NEW",
        "pink hearts and pearls on a square nail; none of her five sets match"),
    "nude-gold-marble-press-on-nails": (
        "nude-gold-marble-press-on-nails", "NEW",
        "nude with gold marbling. Resembles her Champagne glitter set, but not "
        "closely enough to overwrite it on a guess -- flagged for her to say"),
    "nude-gold-floral-press-on-nails": (
        "nude-gold-floral-press-on-nails", "NEW",
        "nude with a raised flower, gold vines and pearls. Sits between her "
        "Blush floral and Silver filigree sets -- flagged for her to say"),
}


def load(slug, view=None):
    name = "%s-%s.png" % (slug, view) if view else "%s.png" % slug
    p = os.path.join(SRC, name)
    return p if os.path.exists(p) else None


def write_pair(src, stem):
    """One view, as transparent WebP and as a cream-flattened JPEG."""
    im = Image.open(src)
    im.load()
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    webp = os.path.join(OUT, stem + ".webp")
    jpg = os.path.join(OUT, stem + ".jpg")
    flat = Image.new("RGB", im.size, CREAM)
    flat.paste(im, mask=im.getchannel("A"))
    if APPLY:
        im.save(webp, "WEBP", quality=90, method=6)
        flat.save(jpg, quality=88, optimize=True, progressive=True)
    return im.size, (os.path.getsize(webp) if APPLY else 0), (os.path.getsize(jpg) if APPLY else 0)


def main():
    if not os.path.isdir(SRC):
        sys.exit("FAIL  no source folder at %s" % os.path.relpath(SRC, HERE))
    lock = json.load(open(LOCK, encoding="utf-8"))
    seen, written, wb, jb = set(), 0, 0, 0

    for slug in sorted(MAP):
        key, kind, why = MAP[slug]
        nail = "press-on-nails" in slug
        srcs = [load(slug)] if nail else [load(slug, v) for v in VIEWS]
        if any(s is None for s in srcs):
            print("  MISS %-34s missing view(s) in source/updated-photos" % slug)
            continue
        print("%-34s %-9s -> %s" % (slug, kind, key))
        print("      %s" % why)
        for n, s in enumerate(srcs, 1):
            stem = "%s-a%d" % (key, n)
            size, a, b = write_pair(s, stem)
            wb += a
            jb += b
            written += 1
            print("      a%d  %dx%d  %-46s %s" % (
                n, size[0], size[1], os.path.basename(s),
                ("%.0f KB webp / %.0f KB jpg" % (a / 1024, b / 1024)) if APPLY else ""))
            seen.add(os.path.basename(s))

        lock.setdefault("products", {})["SB-UP-" + key] = {
            "productKey": key,
            "productName": slug,
            "status": "LOCKED" if APPLY else "PENDING",
            "lockedOn": "2026-08-18",
            "source": "source/updated-photos (Google Drive, 'Updated photos')",
            "sourceFiles": [os.path.basename(s) for s in srcs],
            "images": ["%s-a%d.jpg" % (key, n) for n in range(1, len(srcs) + 1)],
            "recreated": True,
            "recreatedNote": (
                "AI-generated product image supplied by the shop, not a photograph "
                "of the stock. " + why),
        }

    stray = sorted(set(os.listdir(SRC)) - seen)
    if stray:
        print("\n%d source file(s) not referenced by MAP:" % len(stray))
        for s in stray:
            print("  " + s)

    print("\n%d view(s)%s" % (written, "" if APPLY else " would be written"))
    if APPLY:
        print("%.0f KB webp, %.0f KB jpg" % (wb / 1024, jb / 1024))
        json.dump(lock, open(LOCK, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        open(LOCK, "a", encoding="utf-8").write("\n")
        print("product-image-lock.json updated")
    else:
        print("dry run -- nothing written. add --apply.")


if __name__ == "__main__":
    main()
