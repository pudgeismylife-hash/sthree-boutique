# Sthree Boutique — project context

Everything needed to pick this work up cold. Written 17 Aug 2026.

## The business

**Sthree Boutique**, Bikarnakatte, Mangalore, Karnataka. Owner **Priyanka Monteiro**
(priyankamonteiro@gmail.com). Founded 14 June 2026. Hours 9am–8pm daily. Ships across
India and worldwide. Instagram [@sthreeboutique2026](https://instagram.com/sthreeboutique2026).

**Orders happen on WhatsApp only** — no cart, no checkout, no payment integration.
Every product action is a WhatsApp deep link. Primary number **+91 76250 77531**.

Her pricing is **affordable, not luxury**: jewellery ₹110–499, sarees ₹1,180–1,820,
western ₹950–2,093. Jewellery is 17 of the 25 products.

## Where things are

| What | Where |
|---|---|
| Live site | https://pudgeismylife-hash.github.io/sthree-boutique/ |
| Repo | https://github.com/pudgeismylife-hash/sthree-boutique |
| Private preview | https://claude.ai/code/artifact/fc3f30f9-4eb0-4aad-8bf4-dec21a2b8b91 |
| Working copy | `C:\Maya test` |
| Antigravity images | `C:\Property\SB-JWL-Products` |
| Rollback point | `git reset --hard pre-image-lock` |

## How it is built

One self-contained HTML page. No framework, no dependencies, no server.
`sthree-boutique.html` is the **only** file to edit. Then:

```bash
node build-hosted.js
```

That produces `index.html` (the public site), `sthree-boutique-share.html` (standalone
copy to send as a file), `sthree-boutique-hosted.html` (the preview copy),
the Product structured data, `photo-shot-list.html`, `owner-questions.html`, and `p/` —
one small page per product carrying its own WhatsApp link preview. Nothing can drift.

The preview **cards** in `assets/og/` are built separately by
`python3 build-og-images.py --apply`, only when a product photo changes, so the main
build needs no Python. The build warns if a product has no card.

The build runs from wherever the repo sits — the scripts take their folder from their
own location, so `C:\Maya test` is no longer required.

Design follows **direction 3a "Editorial"** in `brand-handoff/` — cream `#FAF6F0`,
ink `#14110F`, gold `#A98037`, Cormorant Garamond / Jost / JetBrains Mono, square
corners, no shadows, hairline rules. Do not redesign it.

## Rules that must not be broken

1. **Nothing on the page may be invented.** No prices, no fabric specs, no delivery
   times, no returns policy, no reviews. Rows appear only when the data exists. A
   fabricated testimonial once sat live for days; the review band now renders only
   from a `reviews` list that starts empty.
2. **Product code = permanent image identity.** `SB-JWL-01` owns `SB-JWL-01-1/2/3.jpg`
   and nothing else. Never infer assignment from position, number or filename order.
3. **LOCKED = do not change.** `product-image-lock.json` is the source of truth.
   Locked products are untouched by imports unless named in `--unlock`.
4. **Conflict = stop that product, do not guess.** Report and skip; carry on with the rest.
5. **Product identity is `key`, not a filename.** Deep links (`?p=<key>`) must keep working
   when photographs change.
6. **Verify in a browser before pushing.** A valid built file is not a working page.

## Photos

```bash
node import-photos.js "path/to/folder"          # validate only, writes nothing
node import-photos.js "path/to/folder" --apply  # import what passes
node build-hosted.js
```

Files must be named `<CODE>-1.jpg` / `-2` / `-3` — full view, worn, detail.
`photo-map.json` translates an outside batch's codes onto catalogue keys where the
two number differently. **Always read the dry run.** A batch supplied on 17 Aug used
`SB-JWL-01`–`10` for anklets and kaftans while those same codes here are earrings and
necklaces; importing blind would have put a kaftan photo on a necklace.

**Collecting photos from the boutique:** WhatsApp recompresses pictures to ~800px and
discards the original, so they arrive unusable. Ask via Google Drive, or WhatsApp
**Document** mode. Send her `photo-shot-list.html` — it carries every code with a
thumbnail and three checkboxes.

**The hero is no longer a composite.** It is built in the page from the pieces named in
`CONFIG.heroField`, over crops cut by `build-og-images.py` into `assets/hero/`. The build
refuses to run if that list names a piece missing from the catalogue, a piece whose
picture is a generated render, or one with no crop on disk. The **category tiles** are
still composites — `build-tiles.py` rebuilds one from a named photograph.

**From a catalogue PDF:** `extract-source.py --apply` unpacks the photographs,
`prep-source-views.py --apply` cuts off the caption printed into each picture and
splits composites, then the normal importer takes `source/staged`. The PDFs have no
text layer — names and prices are drawn into the images — so they are transcribed by
hand in `source/customer-source.json`, sha1-tied to the picture they were read from.

## State as of 17 Aug 2026

- **30 products**, 6 categories, filtering plus search. 25 priced; the 5 press-on nail
  designs carry `price:null` and show "Price on WhatsApp" — a product may omit its price
  and nothing (page, enquiry, link preview, structured data) will invent one.
- Zoomable product view: pinch, wheel, double-tap, drag-to-pan, thumbnail strip.
- **One action per product.** "Order on WhatsApp", or "Ask the price on WhatsApp" when
  unpriced. It was two near-identical buttons; the second sent a weaker message.
- **The hero is built in the page**, not baked — the collection behind one cream band,
  12 photographs wide / 6 on a phone, from `CONFIG.heroField`. The build **exits 1** if
  that list names a missing piece, a generated render, or one with no crop.
- **Every product link previews as itself** on WhatsApp. `p/<key>.html` per product with
  its own tags; `assets/og/<key>.jpg` is the 1200×630 card. `?p=<key>` still works.
- Thumbnails are cut to fill their card (fill went 45% → 92%). All of `assets/products/`,
  `/thumb`, `/og`, `/hero` derive from the same photographs.
- **7 products show a Fabric row**, quoted from the boutique's own product names, plus
  general care for that material — labelled as general, never as her instruction.
- Photographs on disk: 52 full + 52 thumb + 30 preview cards + 30 hero crops, 30 stubs.
- Lock: **14 LOCKED**, 1 SKIPPED (`SB-JWL-10`, no price), **6 flagged
  `sourceReview: REVIEW_REQUIRED`** — status left LOCKED on purpose so no import can
  take them silently.

## The rule added this session

**Customer Image Fidelity.** Her originals are the source of truth. Assess before
touching: use as-is when good, enhance when recoverable, and *stop and report* when too
degraded — never substitute a generated lookalike. Measured: every photograph she has
supplied needs only 1.2–1.5× enlargement, so the "recreate" band never triggers here.
Full workflow and thresholds: https://claude.ai/code/artifact/dced4510-4875-4aa6-87c6-bdac498bcf38

**No image generation is available in this environment**, and model-weight hosts
(huggingface.co, download.pytorch.org) are blocked. Enhancement is Pillow arithmetic on
her pixels; recreation cannot be done at all.

## Still needed from Priyanka

All of it is on one page for her in `owner-questions.html`, generated by the build with
a blank against every question. Send that instead of retyping this list.

**Blocking, in the order they cost her money:**
1. **The five press-on nail prices.** Five numbers. They currently read "Price on
   WhatsApp". `owner-questions.html` opens with a table for them.
2. **Sizes** per garment, and **which of the 30 are in stock.** Neither is derivable from
   a photograph — a wrong size list makes wrong orders on a shop with no returns policy.
3. One genuine customer review. The band renders only from a real one.

Fabric is **no longer blocking on 7 products** — it was already in her own product names
and is now shown. Only the palazzo cordset names no material.

**To confirm:** her second WhatsApp line (she wrote `903608742`, nine digits; the two
handoffs say `9036087427` and `9036087420`) · the six earring names **and the five press-on nail names**, all of which are
ours — her sheet called all six earrings "Antitarnish earring", and the nail PDF named
nothing · spelling corrections
(Lilen→Linen, kafthan→kaftan, Plazo→Palazzo, sequence→sequin) · whether the black and
orange linen dresses are one product or two · imported vs Indian per item · delivery
cost and timeline.

**Missing stock:** bags still show "Coming soon". Press-on nails are live — five designs
from her catalogue PDF — but **unpriced**: they carry `price:null` and the card reads
"Price on WhatsApp". The ₹999 on the maker's instruction card is that maker's MRP, not
hers, so it is not used. `owner-questions.html` now opens by asking for the five prices.

**Needs a decision:** no analytics, so nobody can tell whether the site produces
enquiries. Requires an account and an ID.

**Fixed 17 Aug 2026:** the Co-ord sets tile now uses the boutique's own photograph of
the cotton embroidery cordset, rebuilt by `build-tiles.py`.

**Open conflict:** six jewellery products (SB-JWL-01 to 06) still show generated
renders while the boutique's own photograph of each sits in `source/customer-pdf/`.
Two of them, the anklets, are drawn as flat-lay bracelets with a clasp rather than as
anklets. They are flagged `sourceReview: REVIEW_REQUIRED` in the lock, with status
deliberately left `LOCKED` so no import can take them silently. Replacing one is
`node import-photos.js <folder> --apply --unlock SB-JWL-0<n>`.

## What changed on 17 Aug 2026, and why

Read this before assuming anything above is old news.

| Change | Why it was done |
|---|---|
| Build runs from its own folder | Both scripts were pinned to `C:\Maya test` and ran nowhere else. |
| Keyboard traps closed | The closed mobile menu held 7 tab stops; the open viewer leaked 20 into the page behind it. |
| `owner-questions.html` | The open questions were written for a developer, not for Priyanka. |
| Catalogue PDFs vendored to `source/` | They existed only in an upload folder that dies with the session. |
| 3 clothing photos replaced | They were flat vector renders, not photographs of her garments. |
| Per-product link previews | Every shared product previewed as the same logo. Orders arrive by shared link. |
| Hero rebuilt in the page | The baked band carried a generated render for weeks because nothing checked. |
| Thumbnails re-cut | Photographs filled 45% of their own file; the rest was baked cream. |
| Press-on nails added | Category had said "Coming soon" since launch. No prices exist, hence `price:null`. |
| One WhatsApp action | Two buttons, same number, and the second sent the weaker message. |
| Fabric + general care | Fabric was already in her wording; care is standard for that material, labelled as such. |

**Still true and still wrong:** six jewellery products show generated renders while her own
photographs sit in `source/customer-pdf/`. Both anklets are drawn as flat-lay bracelets
with a clasp, and the Jewellery category tile is the rendered armcuff. Needs nothing from
her — `node import-photos.js <folder> --apply --unlock SB-JWL-0<n>`, then
`python3 build-og-images.py --apply` and `python3 build-tiles.py --apply`.

**Environment note:** `github.io` is unreachable from the build container, so the live
page can be verified on GitHub and locally over HTTP but never rendered here. Test over
`http://` — `?p=` resolves to a directory on `file://` and will look broken.
