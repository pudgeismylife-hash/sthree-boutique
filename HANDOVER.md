# Sthree Boutique — handover

Paste this whole file into a new chat to pick the project up.

---

## The shop

Sthree Boutique, Bikarnakatte, Mangalore. Owner **Priyanka Monteiro**.
A single static page. Orders happen on **WhatsApp only** — no cart, no checkout,
no payments, no stock system.

**Live:** https://pudgeismylife-hash.github.io/sthree-boutique/
**Repo:** `pudgeismylife-hash/sthree-boutique`
**Branch:** `claude/sthree-boutique-work-wqme9s`, pushed to `main`
**At handover:** commit `afff1f9`, deployed and green, tree clean

---

## First command, every session

```bash
./check-sync.sh
```

This container has come back at an older commit **three times**. A stale tree
does not look stale — it looks like a broken project: folders missing, products
never committed, counts wrong. A diagnosis went out on 19 Aug saying the
customer's photographs had been lost. They had not; the tree was a day behind.

Run it before any diagnosis, file check, catalogue count, image check, build
check or deployment check. Quote the hash it prints in anything you report.
`./check-sync.sh --sync` fast-forwards first. If it refuses, an untracked folder
is usually in the way — move it aside, rerun, move it back.

---

## How it builds

`sthree-boutique.html` is the **only** file edited by hand. Everything else is
generated:

```bash
node build-hosted.js                  # index.html, p/*.html, sw.js, share + hosted copies
python3 build-og-images.py --apply    # link-preview cards, hero crops, thumbnails
python3 build-tiles.py --apply        # the five category tiles
python3 import-updated-photos.py --apply   # bring in a photo batch
python3 clean-backgrounds.py --apply       # cut a flat white field off a picture
```

Images arrive via **Google Drive** — folder "Updated photos". Chat images cannot
be saved to disk, so anything pasted into the conversation is unusable as a file.

---

## Current catalogue

**22 on sale · 15 held · 37 total**

| Category | On sale |
|---|---|
| Ethnic | 4 |
| Western | 1 |
| Co-ord sets | 3 |
| Jewellery | 9 |
| Press-on nails | 5 |
| Bags | 0 |

Every live product uses a **transparent cut-out**. That was deliberate: the shop
had been a mix of cut-outs and photographs on silk, grey card and room sets, and
read as two different shops.

**Held** = still in the file with name, price, code and URL, invisible on the
site. Delete `hold:true` from its line and it returns. Fourteen are held only
because they have no cut-out yet.

---

## Standing rules — these came from the owner and hold

1. Her product is the source of truth. Never invent a different-looking product.
2. Never guess a mapping between an image and a product.
3. **Never invent a price.** Unpriced pieces show "Price on WhatsApp".
4. Never invent sizes, stock, fabric or wash care.
5. AI recreations are marked `recreated: true` in the lock and never passed off
   as her photographs.
6. Verify on the built site before calling anything done.

---

## Bags, and the Michael Kors bag

Bags is a **live, clickable category showing 0**. It is not "coming soon" — that
was removed deliberately; an empty shelf and an unopened shop are different
things. Selecting it shows "No bags available yet."

One bag record exists: **`SB-BAG-01`, Michael Kors signature satchel, ₹3,500**,
`PENDING_VERIFICATION` / `NOT_VERIFIED` / `HELD`, `images: []`.

**It is not published, and this was argued at length. Do not quietly reverse it,
and do not re-open it unless the owner brings new provenance.**

What was established:

- The owner **explicitly authorised** publishing it. The hold is not theirs.
- The owner then confirmed, honestly, that there is **no invoice, no supplier
  document, no retailer receipt, nothing**.
- Research showed the bags match **genuine MK design families** (the vanilla one
  closely matches the Charlotte Signature Logo Tote, style 35F3GCFT9T). Design
  match is what a good replica has, so it does not establish authenticity.
- Against it: ₹3,500 versus ~₹25–30k retail; "12@ High End Quality", a replica
  grade; a pitch built on included branded box, dust cover, tags and charm; and
  a hangtag in the photograph reading **MICHAEL / MIOAHI / KORR**.
- De-branding the images was considered and **rejected** — the monogram is the
  printed surface of the bag, so editing it out fabricates a different product
  and misleads the buyer, while the goods still bear the mark.

**What would change it:** genuine provenance — supplier, wholesaler, invoice,
importer. With that, publish in full, brand and logo intact, three colourways.
Nothing else does.

Selling it in the shop or over WhatsApp was never in question. The constraint is
only the public indexed listing.

---

## Waiting on Priyanka

1. **Two-heart drop earring** — file already in `source/updated-earrings/e1.png`.
   Not her Heart studs (hers is a single heart, no drop). Needs a name and price.
2. **Monstera leaf studs** — five files came for six earrings; this one had none.
3. **Prices** for seven live pieces showing "Price on WhatsApp".
4. **Nail duplicates** — are nude gold marble and nude gold floral the same stock
   as her Champagne glitter and Blush floral?
5. **Cut-outs for her own photographs** — biggest single win. Six earrings and
   three necklaces are twelve of seventeen jewellery pieces.
6. **Bags** — anything own-label; the category is wired and empty.

---

## Four still flagged REVIEW_REQUIRED

The picture may not be the item: `SB-JWL-02` anti-tarnish anklet, `SB-JWL-04`
sculpted floral armcuff, `SB-JWL-05` evil eye bracelet, `SB-JWL-06` black clover
set. Two were cleared on 18 Aug by matching new images to her own PDF photos.

---

## Traps, all hit at least once

- **A review record is not a review state.** Two builds tested for the presence
  of `sourceReview` rather than `state === "REVIEW_REQUIRED"` and silently
  refused settled pieces. The tile build failed for hours and looked like a cache
  problem.
- **Tiles never refresh themselves.** Replacing a product photo leaves its
  category tile on the old picture. Rerun `build-tiles.py`.
- **Cream is not one colour.** Images flattened on `#FAF6F0` sit on a `#F3EDE4`
  stage and show a seam — hence transparent WebP beside every JPEG.
- **`alpha:true` demands a `.webp` for every view**, not just the first.
- **`Image.getbbox()` trims black, not cream.** Use the difference-mask `trim_box`.
- **github.io is unreachable from the container.** Confirm deploys from the
  Actions run and by rendering the built file. Cache complaints need `?v=N`.
- **Stale checkout.** See the top of this file.
