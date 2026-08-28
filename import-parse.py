"""Turn the client's product message into records the importer can use.

    python3 import-parse.py --from=message.txt
    python3 import-parse.py --from=message.txt --write     write parsed-products.json
    cat message.txt | python3 import-parse.py

What arrives looks like this, and this is the whole of it:

    Bodycon stretchable fit gown L to XL
    Price-2180/-

    Twisted heart chain
    Price-200/-

There is no structure to rely on. The name is a line; the price is the next
line, or the same line, or two lines down; the size may be inside the name or
absent; nothing says what category anything is. The one thing that is reliable
is that a blank line usually ends a product -- and even that fails when the
client sends five products with no gaps at all, so a price line also ends one.

WHAT THIS WILL NOT DO

It will not invent. A product with no price gets no price -- not zero, not a
guess from a similar item -- and is marked for review. A size that was never
written stays empty. A category that no keyword matches stays empty rather than
becoming the most likely one. Every guess it does make is recorded with what it
was guessed from, so the review page can show its working and a person can
disagree with it.

That rule is not fussiness. This shop has been caught by invented data before,
and a wrong price on a public page is a promise the boutique has to keep.
"""
import json
import os
import re
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "import-config.json")
OUT = os.path.join(HERE, "parsed-products.json")

# Every way the client has written a price, and the ways she has not yet but
# will. The number is what matters; the decoration around it is noise.
PRICE = re.compile(r"""
    (?:price\s*[-:–]?\s*)?      # optional "Price", "Price-", "Price :"
    (?:₹|rs\.?\s*|inr\s*)?      # optional currency mark
    (\d[\d,]*)                       # the number itself
    (?:\s*/\s*-|\s*/-|\s*only)?      # optional trailing /- or "only"
""", re.I | re.X)
HAS_PRICE_WORD = re.compile(r"\bprice\b|₹|\brs\.?\b|\binr\b", re.I)

# Sizes as they are actually written on a WhatsApp line.
SIZE_PATTERNS = [
    (re.compile(r"\b(free\s*size|freesize|one\s*size)\b", re.I), lambda m: "Free size"),
    (re.compile(r"\b([SMLX]{1,4}L?)\s*(?:to|-|–)\s*([SMLX]{1,4}L?)\b"),
     lambda m: "%s to %s" % (m.group(1).upper(), m.group(2).upper())),
    (re.compile(r"\b(regular|standard|one|plus|small|medium|large)\s*size\b", re.I),
     lambda m: m.group(1).capitalize() + " size"),
    (re.compile(r"\bsize\s*[-:]?\s*([\w\s,/]+)", re.I), lambda m: m.group(1).strip(" .,-")),
    (re.compile(r"\b(\d{2})\s*(?:to|-|–)\s*(\d{2})\b"),
     lambda m: "%s to %s" % (m.group(1), m.group(2))),
]

NOISE = re.compile(r"^\s*(?:\d{1,2}[:.]\d{2}\s*(?:am|pm)?|[-–—*•]+|\W)\s*$", re.I)

# The client's own messages name the file above the product. That line is the
# single most valuable thing in the whole message: it says which photograph
# belongs to which product, which is otherwise the hardest part of the import
# and the one most likely to be got wrong. Read as a name it would produce
# "IMG_7979.PNG Multi colour heart hanging chain"; read for what it is, it
# removes the guesswork entirely.
FILENAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 _.\-]*\.(png|jpe?g|webp|heic|heif)$", re.I)


def load_config():
    with open(CONFIG, encoding="utf-8") as f:
        return json.load(f)


def slug(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return re.sub(r"-{2,}", "-", text)


def read_price(line):
    """The number, or None. Never a default.

    A line is only read as a price when it says so -- with the word, a currency
    mark, or a trailing /-. Otherwise "Bodycon gown 2 piece" would price a gown
    at two rupees."""
    if not HAS_PRICE_WORD.search(line) and not re.search(r"\d\s*/\s*-", line):
        return None
    m = PRICE.search(line)
    if not m:
        return None
    try:
        value = int(m.group(1).replace(",", ""))
    except ValueError:
        return None
    return value if value > 0 else None


def read_size(text):
    for pattern, render in SIZE_PATTERNS:
        m = pattern.search(text)
        if m:
            return render(m), m.group(0)
    return None, None


def read_category(name, rules):
    """A suggestion, with the word it came from, or nothing.

    Longest keyword first, so "press on nails" beats "on" and "cord set" is not
    mistaken for something else."""
    # She writes "armcuff" and "arm cuff", "press on" and "press-on". Match
    # against both the words as written and the same with spaces closed up.
    low = " " + name.lower() + " "
    tight = " " + re.sub(r"[\s\-]+", "", name.lower()) + " "
    best = None
    for key, words in rules.items():
        if key.startswith("_"):
            continue
        for w in words:
            # Plurals: she writes "earrings", "nails", "sarees". Matching the
            # singular only meant "Pearl drop earrings" found no category at all
            # and went to review for nothing.
            pat = r"\b" + re.escape(w) + r"(?:e?s)?\b"
            hit = re.search(pat, low) is not None
            if not hit:
                # Spaces closed up on both sides, so "arm cuff" finds "armcuff".
                # No word boundary is possible once the spaces are gone, so this
                # is a plain substring test -- kept to keywords of five letters
                # or more, because "ring" inside a longer word would be luck
                # rather than a match.
                wt = re.sub(r"[\s\-]+", "", w)
                hit = len(wt) >= 5 and wt in tight
            if hit:
                if best is None or len(w) > len(best[1]):
                    best = (key, w)
    return best or (None, None)


def blocks(text):
    """Split the message into one chunk per product.

    A blank line ends a product. So does a price line, because the client often
    sends five products with no gaps at all -- name, price, name, price -- and
    a blank-line-only rule would read that as one product with five names."""
    out, cur, priced = [], [], False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or NOISE.match(line):
            if cur:
                out.append(cur); cur, priced = [], False
            continue
        if priced:
            out.append(cur); cur, priced = [], False
        cur.append(line)
        if read_price(line) is not None:
            priced = True
    if cur:
        out.append(cur)
    return out


def parse(text, cfg):
    products = []
    for chunk in blocks(text):
        price, price_line, source_file = None, None, None
        name_lines = []
        for line in chunk:
            if FILENAME.match(line):
                # First one wins: the client sometimes repeats the last file
                # at the foot of a screenshot.
                if source_file is None:
                    source_file = line
                continue
            p = read_price(line)
            if p is not None and price is None:
                price, price_line = p, line
                # "Twisted heart chain Price-200/-" -- the name is on the same
                # line, so keep whatever sits before the price.
                before = line[:PRICE.search(line).start()].strip(" .,-–:")
                before = re.sub(r"\bprice\b\s*$", "", before, flags=re.I).strip(" .,-–:")
                if before:
                    name_lines.append(before)
            else:
                name_lines.append(line)

        # A line that is only a size is an attribute, not part of the name --
        # "Floral thin gold bracelet / Regular size" is one product with a size,
        # not a product called "Floral thin gold bracelet Regular size".
        size, size_text = None, None
        kept = []
        for line in name_lines:
            s_val, s_txt = read_size(line)
            if s_val and s_txt and s_txt.strip().lower() == line.strip().lower():
                if size is None:
                    size, size_text = s_val, s_txt
                continue
            kept.append(line)
        name_lines = kept

        name = " ".join(name_lines).strip(" .,-–:")
        if not name and price is None:
            continue

        if size is None:
            size, size_text = read_size(name)
        # The size is part of how she writes the name, so it stays in the name
        # as well; the field is for filtering, not for rewriting her words.
        cat, cat_word = read_category(name, cfg["categories"])

        review = []
        if not name:
            review.append("no product name")
        if price is None:
            review.append("no price")
        if cat is None:
            review.append("no category matched")

        products.append({
            "name": name or None,
            "slug": slug(name) if name else None,
            "price": price,
            "size": size,
            "category": cat,
            "categoryFrom": cat_word,
            "variant": None,
            "colour": None,
            "description": None,
            "sku": None,
            "sourceFile": source_file,
            "source": {"lines": chunk, "priceLine": price_line, "sizeText": size_text},
            "needsReview": review,
        })

    # Two products with the same name in one message. Sometimes the client has
    # sent the same piece twice; sometimes they are genuinely different and only
    # a photograph will say which. Either way it is not something to resolve by
    # guessing, so both are flagged and both keep their record.
    #
    # Making the filenames unique is deliberately not done here: the name has to
    # be unique against the whole catalogue, not just against this message, and
    # this step cannot see the catalogue.
    seen = {}
    for p in products:
        if p["slug"]:
            seen.setdefault(p["slug"], []).append(p)
    for slug_key, group in seen.items():
        if len(group) > 1:
            for p in group:
                p["needsReview"].append("same name as %d other product(s) in this message"
                                        % (len(group) - 1))
    return products


def main():
    write = "--write" in sys.argv
    src = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--from=")), None)
    try:
        if src:
            with open(src, encoding="utf-8") as f:
                text = f.read()
        elif not sys.stdin.isatty():
            text = sys.stdin.read()
        else:
            sys.exit("No message given.  Pass --from=<file.txt>, or pipe it in on stdin.")
    except FileNotFoundError:
        sys.exit("No such file: %s" % src)
    if not text.strip():
        sys.exit("That message is empty.")

    cfg = load_config()
    products = parse(text, cfg)
    if not products:
        sys.exit("Nothing in that message read as a product.")

    wide = max([len(p["name"] or "(no name)") for p in products] + [7])
    fwide = max([len(p["sourceFile"] or "-") for p in products] + [5])
    print("%-*s  %-*s  %9s  %-11s  %-10s  %s" % (
        fwide, "IMAGE", wide, "PRODUCT", "PRICE", "SIZE", "CATEGORY", "REVIEW"))
    for p in products:
        print("%-*s  %-*s  %9s  %-11s  %-10s  %s" % (
            fwide, p["sourceFile"] or "-",
            wide, p["name"] or "(no name)",
            ("₹" + format(p["price"], ",")) if p["price"] is not None else "—",
            p["size"] or "—",
            p["category"] or "—",
            ", ".join(p["needsReview"]) or "ready"))

    ready = [p for p in products if not p["needsReview"]]
    print("\n%d product(s) read: %d ready, %d need review"
          % (len(products), len(ready), len(products) - len(ready)))

    if not write:
        print("\nreport only -- parsed-products.json not written. add --write.")
        return
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"products": products}, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("\nparsed-products.json written.")


if __name__ == "__main__":
    main()
