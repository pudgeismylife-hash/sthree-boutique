"""Extract the customer's product photographs out of the catalogue PDFs.

    python3 extract-source.py                 report only, writes nothing
    python3 extract-source.py --apply         write source/extracted/

The PDFs the boutique sends carry one photograph per page with the product name
and price drawn into the picture itself -- there is no text layer, so nothing
here can read a name or a price automatically. Those live in
source/customer-source.json, transcribed by eye and checkable against the
extracted image sitting next to them.

This step only unpacks and records. It never touches the website; that is
catalogue-import.js, which refuses to overwrite a LOCKED product.
"""
import json, os, sys, hashlib

HERE = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(HERE, "source", "customer-pdf")
OUT_DIR = os.path.join(HERE, "source", "extracted")
MANIFEST = os.path.join(HERE, "source", "customer-source.json")
APPLY = "--apply" in sys.argv

try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf
    except ImportError:
        sys.exit("FAIL  pymupdf is not installed.  pip install pymupdf")


def slug(name):
    """Stable id for a source image: the PDF's name plus its page."""
    return os.path.splitext(os.path.basename(name))[0]


def extract():
    if not os.path.isdir(PDF_DIR):
        sys.exit("FAIL  no such folder: " + PDF_DIR)
    found = []
    for pdf in sorted(os.listdir(PDF_DIR)):
        if not pdf.lower().endswith(".pdf"):
            continue
        doc = pymupdf.open(os.path.join(PDF_DIR, pdf))
        for pno in range(doc.page_count):
            images = doc[pno].get_images(full=True)
            if not images:
                print("  WARN %s page %d has no image, skipped" % (pdf, pno + 1))
                continue
            if len(images) > 1:
                # Never guess which of several pictures is the product.
                print("  WARN %s page %d has %d images, needs a human, skipped"
                      % (pdf, pno + 1, len(images)))
                continue
            info = doc.extract_image(images[0][0])
            found.append({
                "id": "%s_p%d" % (slug(pdf), pno + 1),
                "pdf": pdf, "page": pno + 1,
                "file": "%s_p%d.%s" % (slug(pdf), pno + 1, info["ext"]),
                "width": info["width"], "height": info["height"],
                "sha1": hashlib.sha1(info["image"]).hexdigest(),
                "bytes": info["image"],
            })
        doc.close()
    return found


def main():
    found = extract()
    manifest = {}
    if os.path.exists(MANIFEST):
        manifest = json.load(open(MANIFEST, encoding="utf-8")).get("sources", {})

    print("%-34s %-11s %-9s %s" % ("SOURCE IMAGE", "SIZE", "STATE", "TRANSCRIBED AS"))
    print("-" * 92)
    unknown = 0
    for f in found:
        rec = manifest.get(f["id"])
        if rec is None:
            state, note = "NEW", "-- not yet transcribed, add it to customer-source.json"
            unknown += 1
        elif rec.get("sha1") and rec["sha1"] != f["sha1"]:
            # The picture behind a transcription changed: the words on file may
            # now describe a different photograph, so stop rather than trust it.
            state, note = "CHANGED", "!! image differs from the one transcribed"
            unknown += 1
        else:
            price = rec.get("price")
            state = "known"
            note = "%s  %s" % (rec.get("caption", "?"),
                               ("Rs " + str(price)) if price else "(no price printed)")
        print("%-34s %-11s %-9s %s" % (f["file"], "%dx%d" % (f["width"], f["height"]), state, note))

    if APPLY:
        os.makedirs(OUT_DIR, exist_ok=True)
        for f in found:
            open(os.path.join(OUT_DIR, f["file"]), "wb").write(f["bytes"])
        print("\nwrote %d image(s) to source/extracted/" % len(found))
    else:
        print("\n%d image(s) found. Dry run -- nothing written. Use --apply." % len(found))
    if unknown:
        print("%d image(s) need a transcription in source/customer-source.json "
              "before they can be imported." % unknown)


if __name__ == "__main__":
    main()
