# Sthree Boutique

Website for **Sthree Boutique**, Bikarnakatte, Mangalore — western wear, ethnic wear,
co-ord sets, anti-tarnish jewellery, press-on nails and bags. Imported and Indian,
delivered across India and worldwide. Owner: Priyanka Monteiro. Established June 2026.
Instagram [@sthreeboutique2026](https://instagram.com/sthreeboutique2026),
orders over WhatsApp — no cart, no payment integration.

The site is one self-contained HTML page: no build tools, no dependencies, no server.
It opens straight from a file or from any static host.

## Files

| File | What it is |
|---|---|
| `PROJECT-CONTEXT.md` | **Start here.** Everything needed to pick this work up cold. |
| `sthree-boutique.html` | **The source.** Edit this one. |
| `build-hosted.js` | Produces every distributable copy from the source. |
| `import-photos.js` | Installs product photographs, validating against the lock before writing. |
| `extract-source.py` | Unpacks the photographs out of the boutique's catalogue PDFs. |
| `prep-source-views.py` | Cuts the printed caption off each photograph and splits composites into separate views, ready for the importer. |
| `build-tiles.py` | Rebuilds a category tile from a chosen product photograph. Tiles are composites, so an import never refreshes them. |
| `build-og-images.py` | Builds `assets/og/<key>.jpg`, the 1200×630 card each product link previews with, and `assets/hero/<key>.jpg`, the crops behind the hero band. |
| `assets/hero/` | Built — per-product crops used by the hero band. |
| `p/` | Built — one small page per product carrying its own link preview, forwarding to the piece. |
| `assets/og/` | Built — the per-product preview cards. |
| `source/customer-pdf/` | The boutique's catalogue PDFs — the source of truth for what each product actually looks like. |
| `source/customer-source.json` | Every product name and price as printed in those PDFs, transcribed by hand because the PDFs have no text layer. |
| `product-image-lock.json` | Source of truth for product-image mapping. LOCKED entries are never changed by an import. |
| `photo-map.json` | Translates an outside batch's codes onto catalogue product keys. |
| `index.html` | Built — the public site (GitHub Pages serves this). |
| `sthree-boutique-share.html` | Built — standalone copy to send as a file on WhatsApp. |
| `sthree-boutique-hosted.html` | Built — copy for the private Claude preview link. |
| `assets/` | Logo artwork. `logo-web.png` is used on the site; the full-size and dark variants are kept alongside it. |
| `og-image.jpg` | 1200×630 link-preview thumbnail (WhatsApp, Instagram, Facebook). |
| `photo-shot-list.html` | Built — printable list of every piece with its code and three checkboxes, to send to the boutique when collecting photos. |
| `owner-questions.html` | Built — every outstanding question on one page (sizes, stock, fabric, the second number, the earring names, delivery), with a blank against each. Send it to Priyanka. |
| `app-handoff/` | Separate design bundle for the mobile storefront app. |
| `brand-handoff/` | Branding handoff for direction 3a, which this site implements. |

## Editing

Everything an owner normally needs to change lives in one block at the top of the
script in `sthree-boutique.html`:

```js
const CONFIG = {
  whatsapp : "917625077531",             // primary
  whatsappAlt: "",                       // second line — see open items below
  tel      : "+917625077531",
  email    : "priyankamonteiro@gmail.com",
  address  : "Bikarnakatte, Mangalore, Karnataka",
  hours    : "9:00 am – 8:00 pm, all days",
  logo     : ""                          // filled in by the build
};
```

Change the number there and every WhatsApp button on the site follows.

The `categories` and `arrivals` lists sit just below that block. New arrivals are
expected to change weekly — edit that list, rebuild, and push.

After any edit:

```bash
node build-hosted.js
```

That one command rebuilds the three site copies, regenerates the Product
structured data, and refreshes the photo shot list — so none of them can drift
away from the catalogue.

## Collecting photos

WhatsApp re-compresses pictures to about 800px and discards the original, so
photos sent that way arrive unusable. Ask for them through **Google Drive**, or
on WhatsApp via **Document** (paperclip → Document).

Name files by product code — `SB-JWL-01-1.jpg`, `-2`, `-3` — so 25 pieces ×
3 angles can be matched automatically instead of by eye. `photo-shot-list.html`
carries the codes with thumbnails; send it to the boutique.

Images live at these sizes: `assets/products/` (720×900, used by the zoomable
viewer), `assets/products/thumb/` (360px, used by cards and tiles), `assets/hero/`
(440×550 crops behind the hero band) and `assets/og/` (1200×630 link-preview cards).
The last two are cut by `build-og-images.py`.

### From a catalogue PDF

When the boutique sends a catalogue PDF rather than named files:

```bash
python3 extract-source.py --apply       # unpack the photographs from source/customer-pdf/
python3 prep-source-views.py --apply    # cut off the printed caption, split composites
node import-photos.js source/staged     # dry run — read it
node import-photos.js source/staged --apply --unlock <CODE>
python3 build-tiles.py --apply          # only if a category tile should change
node build-hosted.js
```

The PDFs carry **no text layer** — the product name and price are drawn into the
photograph itself, so nothing can read them automatically. They are transcribed by
hand into `source/customer-source.json`, each tied by sha1 to the image it was read
from so a changed picture is caught rather than silently keeping the old wording.

`prep-source-views.py` removes the printed caption before anything reaches the site,
and splits a page that holds two genuine views (worn / on hangers) into separate
images. Every view is a crop of the boutique's own photograph — nothing is generated.
A piece gets only the views its photograph really contains; the importer accepts one,
two or three rather than padding a set out with an invented angle.

### The product gallery

A product's `images` array is the gallery — one photograph, two, three or more,
with no change to any component. The strip appears only when there is more than one.

```js
{ ..., views:["Front","Side","Back"], alpha:true,
  images:[P+"gowns_1-a1.jpg", P+"gowns_1-a2.jpg", P+"gowns_1-a3.jpg"] }
```

`views` names the angles. It is optional: a product that does not say what its
angles are gets "Photo 1, 2, 3" rather than a guess. Names are never inferred from
position — they used to be, and a dress's back view was announced as "Detail".

`alpha:true` is set by the importer when the batch was cut out. Transparent WebP
copies are written beside the JPEGs, the page asks for them where the browser can
read them, and falls back to the JPEG where it cannot. Transparency matters here:
the stage is cream-alt and a flattened photograph is cream, which left a visible
rectangle around every piece.

A customer can change angle by tapping a thumbnail, swiping the photograph
sideways on a phone, or pressing the left and right arrow keys. Swiping is ignored
while zoomed in, where a horizontal drag is panning.

### Installing photos

Name files `<CODE>-1.jpg`, `-2`, `-3` — full view, worn, detail — then:

```bash
node import-photos.js "path/to/folder"          # report only, writes nothing
node import-photos.js "path/to/folder" --apply  # resize, install, wire up
node build-hosted.js
```

It resizes to both sizes, adds an `images` list to each product, and the viewer
grows a thumbnail strip automatically. Products with one photo are unaffected.

**Always read the dry run first.** Codes are the only thing tying a photo to a
product, and a folder prepared elsewhere may number things differently. A batch
supplied in Aug 2026 used `SB-JWL-01`–`10` for anklets, arm cuffs and kaftans,
while those same codes on this site are earrings and necklaces — applying it
blind would have put a kaftan photo on a necklace. The dry run exists to catch
exactly that.

## Link previews

Every product has its own preview. Paste a product link into WhatsApp and it shows
that piece, its name and its price, instead of the boutique logo — which matters when
orders arrive by shared link.

WhatsApp, Instagram and Facebook read the preview out of the HTML they are handed and
never run its JavaScript, so a single page that switches products client-side can only
ever offer one preview for all 25. The build therefore writes one small page per
product in `p/`, each carrying its own tags and forwarding a real visitor to the piece.
The Share button and every WhatsApp enquiry now send that address.

`?p=<key>` is unchanged and still opens a piece directly, so links shared before this
keep working.

The preview cards themselves are built separately, because they need Pillow and
`node build-hosted.js` must stay dependency-free:

```bash
python3 build-og-images.py --apply    # only when a product photo changes
node build-hosted.js
```

The build warns if a product has no card. No text is drawn into a card: WhatsApp
already prints the name and price beside it, and burning words into an image ties the
build to a font that is not on every machine.

## Site-wide link preview

For the logo to appear as the thumbnail when the link is shared on WhatsApp, the site
must be publicly reachable and `SITE_URL` at the top of `build-hosted.js` must be set to
its address, for example `https://<user>.github.io/<repo>`. Crawlers need an absolute
URL — a relative path or an embedded image will not produce a preview.

Set it, rerun the build, commit, and re-share the link.

## Design

Implements **direction 3a "Editorial"** from `brand-handoff/`: cream ground,
Cormorant Garamond display type, Jost UI, JetBrains Mono labels, square corners,
no shadows, separation by hairline rules. Colours, type sizes and copy follow the
handoff tokens.

## Status

Live at **https://pudgeismylife-hash.github.io/sthree-boutique/**

Her real catalogue is live: **25 products** at her own prices, loaded from the
Drive product sheets. Category tiles filter the grid and there is a search;
tapping any photo opens a zoomable product view whose enquiry carries the piece,
its code and a link back to it. Jewellery is 17 of the 25. The hero is built
from four of her own photographs.

## What we still need from Priyanka

`owner-questions.html` is this section as one page she can answer in a single pass —
built from the catalogue, so the pieces and prices it quotes back to her cannot drift.
Send that rather than retyping the list.

**Blocking a proper launch**

| Item | Why it matters |
|---|---|
| **Sizes** | Her product sheets have none. Clothing is hard to sell without it, even over WhatsApp. Jewellery shows "Free size"; clothing shows no selector at all. |
| **Fabric, fit, wash care** | Per piece. The product view has rows for these and shows them only when supplied — right now every one is empty. |
| **More photos** | One per piece today. Two or three angles each would make the zoom worth having. |
| **Stock status** | No indication which of the 25 pieces are available. She already marks "Sold — stock ll be back soon" on Instagram. Product structured data omits availability until this exists. |
| **A real customer review** | The invented testimonial has been removed and the band is hidden. It reappears the moment a genuine review is added to the `reviews` list. Ask a happy customer for one line. |

**Data to confirm**

| Item | Detail |
|---|---|
| **Second WhatsApp line** | She wrote `903608742` — nine digits. The app handoff says `9036087427`, the branding handoff `9036087420`. Left off the site until confirmed. |
| **Earring names** | Her sheet called all six "Antitarnish earring". Named by motif — Starfish, Chrysanthemum, Petal drop, Monstera leaf, Octopus, Heart. Needs her approval. |
| **Spelling corrections** | Lilen→Linen, desiner→designer, polyster→polyester, kafthan→kaftan, Plazo→Palazzo, Studed→Studded, sequence→sequin. |
| **The two linen dresses** | Black and orange, both ₹2,093 — one product in two colours, or two products? |
| **Imported or Indian** | The brand line is "Imported & Indian" but no per-item origin was supplied, so cards show the category instead. |
| **Delivery cost and time** | "Worldwide" is stated with no charges or timelines. |

**Missing stock**

Bags are listed as a category with no photos and no products, and show as "Coming soon".
Press-on nails are live with five designs, but none of them has a price: they carry
`price:null`, the card reads "Price on WhatsApp", and the enquiry goes out without a
figure. A product may always omit its price — nothing on the page, in the structured
data or in a link preview will invent one.

**Smaller**

Google Maps place ID for the Visit embed · sign-off on the mobile menu overlay · higher-resolution photo originals.

**Needs a decision, not data**

No analytics yet, so nobody can tell whether the site produces enquiries. Adding it needs an account (Google Analytics, or a lighter privacy-friendly service) and its ID — a one-line change once chosen.

## History

The site was first built to a written brief before the branding handoff existed,
in a different visual direction with a wishlist, quick view, growth roadmap and
FAQ. That version is intact at commit `9588494` if any of it is wanted back.
