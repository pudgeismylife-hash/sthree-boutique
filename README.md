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
| `sthree-boutique.html` | **The source.** Edit this one. |
| `build-hosted.js` | Produces every distributable copy from the source. |
| `index.html` | Built — the public site (GitHub Pages serves this). |
| `sthree-boutique-share.html` | Built — standalone copy to send as a file on WhatsApp. |
| `sthree-boutique-hosted.html` | Built — copy for the private Claude preview link. |
| `assets/` | Logo artwork. `logo-web.png` is used on the site; the full-size and dark variants are kept alongside it. |
| `og-image.jpg` | 1200×630 link-preview thumbnail (WhatsApp, Instagram, Facebook). |
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

## Link previews

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
Drive product sheets. Category tiles filter the grid. Jewellery is 17 of the 25.
The hero image is still a placeholder.

## What we still need from Priyanka

**Blocking a proper launch**

| Item | Why it matters |
|---|---|
| **Hero photo, 1080×1350 portrait** | The top of the page is still a grey placeholder. Her existing photos are 716×716 and cannot fill it. Biggest single visual gap. |
| **Sizes** | Her product sheets have none. Clothing is hard to sell without it, even over WhatsApp. |
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

Press-on nails and bags are listed as categories with no photos and no products. Both show as "Coming soon".

| **Fabric, fit, wash care** | Per piece. The product view has rows for these and shows them only when supplied; right now every one is empty. |
| **More photos** | One per piece today. Two or three angles each would make the zoom worth having. |

**Smaller**

Google Maps place ID for the Visit embed · sign-off on the mobile menu overlay · higher-resolution photo originals.

**Needs a decision, not data**

No analytics yet, so nobody can tell whether the site produces enquiries. Adding it needs an account (Google Analytics, or a lighter privacy-friendly service) and its ID — a one-line change once chosen.

## History

The site was first built to a written brief before the branding handoff existed,
in a different visual direction with a wishlist, quick view, growth roadmap and
FAQ. That version is intact at commit `9588494` if any of it is wanted back.
