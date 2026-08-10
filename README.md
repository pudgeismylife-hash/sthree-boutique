# Sthree Boutique

Website for **Sthree Boutique** — ethnic wear, western wear, anti-tarnish jewellery and
press-on nails. Instagram [@sthreeboutique2026](https://instagram.com/sthreeboutique2026),
orders over WhatsApp.

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
  whatsapp : "917625077531",             // primary, per the branding handoff
  whatsappAlt: "919036087420",           // secondary line
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

Every photo slot is a labelled placeholder — hero at 1080x1350, category tiles 3:4,
product cards 4:5 — awaiting the client's photography. Prices in `arrivals` are the
handoff's demo figures and need confirming against real stock.

## Open items

| Item | Detail |
|---|---|
| **Phone numbers** | The branding handoff uses **76250 77531** throughout and the site treats it as primary. The two handoffs disagree on the second line — the app handoff says **90360 87427**, the branding handoff says **90360 87420**. One is a typo. The site currently shows 87420. Confirm before any print or ad spend. |
| **Photography** | Not supplied. Needed: hero 1080×1350 portrait, 5 category tiles at 3:4, 6 product shots at 4:5. Serve WebP at 1×/2×. |
| **Mobile nav overlay** | Shipped as a cream full-screen overlay with the five nav links and the WhatsApp CTA. The handoff lists this as needing design sign-off. |
| **Map** | Links out to a Google Maps search so nothing needs an API key. Swap for an embed once the place ID exists. |
| **Fonts** | Loaded from Google Fonts. The handoff asks for self-hosting in production; the private preview copy cannot load them and falls back to system faces. |

## History

The site was first built to a written brief before the branding handoff existed,
in a different visual direction with a wishlist, quick view, growth roadmap and
FAQ. That version is intact at commit `9588494` if any of it is wanted back.
