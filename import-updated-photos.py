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
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "source", "updated-photos")
OUT = os.path.join(HERE, "assets", "products")
LOCK = os.path.join(HERE, "product-image-lock.json")
APPLY = "--apply" in sys.argv
ONLY = ([a.split("=", 1)[1] for a in sys.argv if a.startswith("--only=")] or [None])[0]

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


# The jewellery batch arrived as composites: the piece cut out on the left, and
# two photographs stacked down the right -- worn, and a close-up. One file per
# product rather than one per view, so the panels are cut here. Boxes were
# measured off the alpha channel, not guessed: the panel block is the run of
# fully opaque columns, and the seam between the two panels is the strongest
# horizontal edge inside it.
#
# slug -> (key, main box, top panel, bottom panel, view names, what and why)
SRC_JWL = os.path.join(HERE, "source", "updated-jewellery")
COMPOSITES = {
    "j1": (
        "armcuff_1", (0, 0, 916, 1024), (919, 0, 1536, 575), (919, 575, 1536, 1024),
        ["Front", "Worn", "Detail"],
        "the butterfly armcuff. Matches her own photograph in armcuff.pdf -- "
        "coiled band, two filigree butterflies, and the worn view mirrors hers. "
        "Replaces a render flagged REVIEW_REQUIRED that showed a heavier cuff "
        "with a wider band and stones",
    ),
    "j2": (
        "anklets_1", (0, 0, 927, 1024), (930, 15, 1522, 558), (930, 575, 1522, 994),
        ["Front", "Worn", "Detail"],
        "the bow anklet. Matches her own photograph in Anklets.pdf -- half pave "
        "chain, half rolo, gold bow, worn on the ankle. Replaces a render "
        "flagged REVIEW_REQUIRED that laid it flat and read as a bracelet",
    ),
}

# Single-image files in the same folder.
SINGLES = {
    "j3": ("nails_4", "wine chrome almond nails -- her Wine gloss press-on set, "
                      "previously the catalogue card photograph"),
    "j4": ("nude-leopard-press-on-nails", "nude leopard print with silver; none "
                                          "of her sets match, so it goes up new"),
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


def write_piece(im, stem):
    """One already-cut view, as transparent WebP and cream-flattened JPEG."""
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    flat = Image.new("RGB", im.size, CREAM)
    flat.paste(im, mask=im.getchannel("A"))
    if APPLY:
        im.save(os.path.join(OUT, stem + ".webp"), "WEBP", quality=90, method=6)
        flat.save(os.path.join(OUT, stem + ".jpg"), quality=88, optimize=True, progressive=True)
    return im.size


def jewellery(lock):
    """The composites and singles in source/updated-jewellery."""
    if not os.path.isdir(SRC_JWL):
        return 0
    n = 0
    for slug in sorted(list(COMPOSITES) + list(SINGLES)):
        if ONLY and ONLY not in slug:
            continue
        p = os.path.join(SRC_JWL, slug + ".png")
        if not os.path.exists(p):
            print("  MISS %-34s not in source/updated-jewellery" % slug)
            continue
        im = Image.open(p)
        im.load()
        im = im.convert("RGBA")

        if slug in COMPOSITES:
            key, main, top, bot, names, why = COMPOSITES[slug]
            cut = im.crop(main)
            # trim the cut-out back to the piece; the panels are photographs and
            # are left exactly as cut
            bb = cut.getchannel("A").getbbox()
            parts = [cut.crop(bb) if bb else cut, im.crop(top), im.crop(bot)]
        else:
            key, why = SINGLES[slug]
            names = None
            bb = im.getchannel("A").getbbox()
            parts = [im.crop(bb) if bb else im]

        print("%-6s -> %-32s %s" % (slug, key, "3 views" if len(parts) > 1 else "1 image"))
        print("      %s" % why)
        for i, part in enumerate(parts, 1):
            size = write_piece(part, "%s-a%d" % (key, i))
            print("      a%d  %dx%d%s" % (i, size[0], size[1],
                                          "  " + names[i - 1] if names else ""))
            n += 1

        lock.setdefault("products", {})["SB-UP-" + key] = {
            "productKey": key,
            "productName": slug,
            "status": "LOCKED" if APPLY else "PENDING",
            "lockedOn": "2026-08-18",
            "source": "source/updated-jewellery (Google Drive, 'Updated photos/jewellary')",
            "sourceFiles": [slug + ".png"],
            "images": ["%s-a%d.jpg" % (key, i) for i in range(1, len(parts) + 1)],
            "recreated": True,
            "recreatedNote": ("AI-generated product image supplied by the shop, not a "
                              "photograph of the stock. " + why),
        }
        # whatever these replace, they are no longer the wrong piece
        for code, v in lock.get("products", {}).items():
            if v.get("productKey") == key and v.get("sourceReview"):
                v["sourceReview"]["state"] = "RESOLVED"
                v["sourceReview"]["resolvedOn"] = "2026-08-18"
                v["sourceReview"]["resolution"] = (
                    "replaced on 18 Aug 2026 by SB-UP-%s, which matches her own "
                    "photograph of this piece. Still a recreation, not a "
                    "photograph of the stock." % key)
                print("      cleared the REVIEW_REQUIRED flag on %s" % code)
    return n


# The earring batch, from Google Drive "Updated photos/earing". Every file here
# was checked for real alpha before anything was written: not "white background"
# but pixels that are actually clear, 43% to 80% of each frame.
#
# Three of them are composites again -- the piece cut out on the left, photographs
# stacked down the right -- and only the cut-out is taken. The photographs are
# shot on white, and a white panel on a cream stage is the exact thing that had
# to be scrubbed off the armcuff; there is no reason to add more of them.
#
# Prices and names are not invented here. earring.pdf carries both, and they
# match what the catalogue already had, so nothing about either changes.
#
# slug -> (key, left edge of the panel block or None for a full-frame cut-out, why)
SRC_EAR = os.path.join(HERE, "source", "updated-earrings")
EARRINGS = {
    "e2": ("earring_5", None,
           "octopus studs, matching her Octopus studs at Rs 120"),
    "e3": ("earring_3", 932,
           "leaf and petal drops, matching her Petal drop earrings at Rs 120"),
    "e4": ("earring_2", 921,
           "daisy studs, matching her Chrysanthemum studs at Rs 110"),
    "e5": ("earring_1", 928,
           "starfish studs, matching her Starfish studs at Rs 120"),
}

# e1 is a two-heart drop: a stud heart with a larger heart hanging beneath it.
# Her Heart studs, in the catalogue and on page 6 of earring.pdf, are a single
# puffy heart with no drop. Not the same earring, so it is not applied to that
# product and no new product is invented for it either -- she has not said what
# it is or what it costs.
UNMATCHED = {
    "e1": "two-heart drop earring; her Heart studs are a single heart, no drop",
}


def earrings(lock):
    """One transparent image per earring, cut-out only."""
    if not os.path.isdir(SRC_EAR):
        return 0
    n = 0
    for slug in sorted(EARRINGS):
        key, panel_x, why = EARRINGS[slug]
        f = os.path.join(SRC_EAR, slug + ".png")
        if not os.path.exists(f):
            print("  MISS %-6s not in source/updated-earrings" % slug)
            continue
        im = Image.open(f)
        im.load()
        im = im.convert("RGBA")
        if panel_x:
            im = im.crop((0, 0, panel_x, im.height))
        bb = im.getchannel("A").getbbox()
        if bb:
            im = im.crop(bb)
        clear = 100.0 * (np.asarray(im.getchannel("A")) < 16).mean()
        size = write_piece(im, key + "-a1")
        print("%-4s -> %-12s %dx%d  %.0f%% clear" % (slug, key, size[0], size[1], clear))
        print("      %s" % why)
        n += 1

        lock.setdefault("products", {})["SB-UP-" + key] = {
            "productKey": key,
            "productName": slug,
            "status": "LOCKED" if APPLY else "PENDING",
            "lockedOn": "2026-08-18",
            "source": "source/updated-earrings (Google Drive, 'Updated photos/earing')",
            "sourceFiles": [slug + ".png"],
            "images": [key + "-a1.jpg"],
            "recreated": True,
            "recreatedNote": ("AI-generated product image supplied by the shop, not a "
                              "photograph of the stock. " + why + ". Name and price "
                              "unchanged, both confirmed against earring.pdf."),
        }
    for slug, why in UNMATCHED.items():
        print("  HELD %-4s %s" % (slug, why))
    return n


def main():
    if not os.path.isdir(SRC):
        sys.exit("FAIL  no source folder at %s" % os.path.relpath(SRC, HERE))
    lock = json.load(open(LOCK, encoding="utf-8"))
    seen, written, wb, jb = set(), 0, 0, 0

    for slug in sorted(MAP):
        if ONLY:
            break
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

    written += jewellery(lock)
    written += earrings(lock)

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
