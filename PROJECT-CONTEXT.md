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
the Product structured data, `photo-shot-list.html`, and `owner-questions.html`.
Nothing can drift.

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

**Derived images are not covered by the importer.** The hero band and the category
tiles are separate composites built from product photos. Replacing a product photo
does not update them. `build-tiles.py` now rebuilds a category tile from a named
photograph, so at least that choice is written down and repeatable; the hero band is
still by hand.

**From a catalogue PDF:** `extract-source.py --apply` unpacks the photographs,
`prep-source-views.py --apply` cuts off the caption printed into each picture and
splits composites, then the normal importer takes `source/staged`. The PDFs have no
text layer — names and prices are drawn into the images — so they are transcribed by
hand in `source/customer-source.json`, sha1-tied to the picture they were read from.

## State as of 17 Aug 2026

- 25 products, real names and prices, 6 categories with filtering plus search.
- Zoomable product view: pinch, wheel, double-tap, drag-to-pan, thumbnail strip.
- Enquiries carry product, price, code and a link back to the piece.
- 9 products carry 3 Antigravity images each and are **LOCKED**. The other 16 keep
  the boutique's own photograph.
- `SB-JWL-10` is deliberately **SKIPPED** — no matching product, no confirmed price.
- Hero built from four photographs; logo, favicon and link thumbnail all real.
- 47 images referenced, 47 on disk, no orphans, no superseded photo displayed.

## Still needed from Priyanka

All of it is on one page for her in `owner-questions.html`, generated by the build with
a blank against every question. Send that instead of retyping this list.

**Blocking:** sizes · stock status · fabric, fit and wash care per piece · more photos
(one angle each today) · one genuine customer review.

**To confirm:** her second WhatsApp line (she wrote `903608742`, nine digits; the two
handoffs say `9036087427` and `9036087420`) · the six earring names, which are mine
since her sheet called all six "Antitarnish earring" · spelling corrections
(Lilen→Linen, kafthan→kaftan, Plazo→Palazzo, sequence→sequin) · whether the black and
orange linen dresses are one product or two · imported vs Indian per item · delivery
cost and timeline.

**Missing stock:** press-on nails and bags show "Coming soon".

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
