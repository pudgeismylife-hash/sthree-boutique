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

Every photo slot is a labelled placeholder — hero at 1080x1350, category tiles 3:4,
product cards 4:5 — awaiting the client's photography. Prices in `arrivals` are the
handoff's demo figures and need confirming against real stock.
