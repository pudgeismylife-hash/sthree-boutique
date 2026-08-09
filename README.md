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
| `logo.jpg` | Brand logo, web size. Used in the header, footer and tab icon. |
| `logo-full.png` | Brand logo, full resolution. |
| `og-image.jpg` | 1200×630 link-preview thumbnail (WhatsApp, Instagram, Facebook). |
| `app-handoff/` | Separate design bundle for the mobile storefront app. |

## Editing

Everything an owner normally needs to change lives in one block at the top of the
script in `sthree-boutique.html`:

```js
const CONFIG = {
  whatsapp : "917625077531",   // country code + number, no + or spaces
  instagram: "sthreeboutique2026",
  email    : "hello@sthreeboutique.in",
  currency : "₹",
  logo     : ""                // filled in by the build
};
```

Change the number there and every WhatsApp button on the site follows.

Products, collections, reviews, the roadmap and the FAQ are plain lists just below
that block — add or edit entries and the page updates itself.

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

## Status

Design preview. Product photography, prices, stock and customer reviews are
placeholders pending the client's real content — the page carries a banner saying so.
