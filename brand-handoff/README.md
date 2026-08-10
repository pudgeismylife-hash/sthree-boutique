# Handoff: Sthree Boutique — Editorial direction (3a)

## Overview
Mobile-first marketing/storefront site for **Sthree Boutique**, a womenswear boutique in Bikarnakatte, Mangalore (Karnataka, India). Owner: Priyanka. Orders happen over **WhatsApp**, not a cart — every product action is an enquiry deep-link. The chosen direction is **3a "Editorial"**: cream ground, generous whitespace, serif display type, product photography carrying the page.

## About the design files
`index.html` and the files under `reference/` are **design references created in HTML** — prototypes of the intended look and behaviour, not production code to ship. Recreate them in the target codebase's environment (Next.js/React, Astro, WordPress, etc.) using its established patterns. If no codebase exists yet, pick a framework suited to a small content-driven site (Astro or Next.js static export is a good fit) and implement from this README.

- `index.html` — standalone, responsive implementation of direction 3a. Open it directly in a browser. Content is rendered from three plain JS arrays at the bottom of the file (`categories`, `arrivals`, `storeInfo`) — these are the content model.
- `reference/Sthree Boutique (all directions).dc.html` — the full design exploration (3a/3b/3c mobile, tablet, desktop and earlier turns). Reference only; needs `reference/support.js` beside it to render.
- `assets/` — logo assets.

## Fidelity
**High fidelity.** Colours, type sizes, spacing, and copy below are final and should be matched. Product photography is **not** final — every diagonal-hatch block is an image placeholder awaiting real photos from the client.

## Screens / views
One page, four responsive layouts. Single content column on phones; a 1280px max-width centred column from 900px up.

### Header
- Announcement strip: full-bleed, `#14110F` background, `#EFE7D9` text, 7px padding, 10px / .14em uppercase Jost. Copy: "Imported & Indian · Mangalore".
- Header row: cream `#FAF6F0`, 10px 18px padding (14px 32px ≥900px), 1px bottom border `rgba(20,17,15,.09)`.
- Logo: `assets/sthree-logo-full.png`, **84px tall**, width auto, centred on mobile / left on desktop. Do not shrink below 84px — the script wordmark stops being legible. Do not re-add a separate "STHREE / BOUTIQUE" text lock-up next to it; the logo already contains the name.
- Hamburger (☰) and search (⌕) glyphs in 44×44px hit targets. From 900px the hamburger is replaced by an inline nav: Western, Ethnic, Co-ord sets, Jewellery, Visit — 12px, .18em tracking, uppercase.

### Hero
Full-bleed image, 300px tall on mobile, 520px from 900px. Portrait source asset (1080 × 1350). No overlaid text — the headline sits below it.

### Intro block
- Eyebrow: "Quality. Style. Personality." — JetBrains Mono 10px, .2em, uppercase, `#A98037`.
- H1: "The boutique where fashion meets personality." — Cormorant Garamond 300, 34px / 1.1 mobile, 44px at 600px, 52px at 900px, `text-wrap: balance`.
- Body: "Western and ethnic wear, co-ord sets, anti-tarnish jewellery and bags." — 14px / 1.7, `#57514A`.
- Primary CTA: "Shop on WhatsApp" — 16px padding, `#14110F` fill, `#FAF6F0` text, 11px / .18em uppercase, square corners. Hover: fill `#A98037`.

### Shop by category
H2 26px (34px ≥900px). Grid: 2 columns mobile → 3 at 600px → 5 at 900px, 12/16/20px gaps. Each cell: 3:4 image placeholder + Cormorant 17px name. Items: Western wear, Ethnic wear, Co-ord sets, Jewellery, Bags.

### New arrivals
Section background `#F3EDE4`. Grid 2 → 3 → 4 columns. Card: `#FAF6F0`, 9px padding, 8px gap — 4:5 image, name 13px / 1.35, price Cormorant 17px, "Enquire" button (12px padding, 1px border `rgba(20,17,15,.2)`, 10px / .14em uppercase; hover inverts to `#14110F` / cream). Enquire opens WhatsApp with a prefilled message naming the product.

### Visit the boutique
Two-up from 900px (details left, map right); stacked on mobile with a 150px map block. Detail rows: label in Mono 9px / .14em uppercase `#8A8177`, value 14px / 1.5, 11px vertical padding, 1px bottom rules.

### Review band
`#14110F` background, `#EFE7D9`. Quote in Cormorant italic 300, 19px / 1.5 mobile, 26px centred ≥900px. Attribution 10px / .16em uppercase `#C9A227`.

### Sticky WhatsApp bar (mobile only, <900px)
Fixed to the bottom: `rgba(250,246,240,.96)` + blur, 1px top border. Primary "WhatsApp order" fills the row (`#A98037` on cream text, 15px padding, 48px+ tall); a 52×48px outlined call button (☏ → `tel:+917625077531`) sits beside it. Body has 76px bottom padding to clear it. Hidden from 900px, where the header CTA takes over.

## Interactions & behaviour
- Every CTA is a link: `https://wa.me/917625077531` (add `?text=` prefilled enquiry on product cards), `tel:+917625077531`, `mailto:priyankamonteiro@gmail.com`.
- Hover states: CTA fill → `#A98037`; Enquire → inverted; nav links → `#14110F`.
- Hamburger has no panel yet — a full-screen cream overlay with the five nav items and the WhatsApp CTA is the intended behaviour; needs design sign-off before build.
- No animation beyond default link/hover colour transitions (~150ms ease).
- Images should be lazy-loaded below the hero; hero preloaded.

## State management
Static content site — no client state beyond the mobile nav open/closed boolean. Content (categories, arrivals, store info, reviews) should come from a CMS or a JSON/markdown file the owner can edit; "New arrivals" is expected to be updated weekly (Fridays).

## Design tokens
Colours: ink `#14110F` · ink soft `#57514A` · grey `#8A8177` · cream `#FAF6F0` · cream alt `#F3EDE4` · warm light `#EFE7D9` · gold `#A98037` · gold bright `#C9A227` · hairline `rgba(20,17,15,.09)`.
Type: display **Cormorant Garamond** 300 (H1 34/44/52, H2 26/34, prices 17, quote 19/26); UI **Jost** 300/400 (body 13–15, buttons 10–11 uppercase .14–.18em); labels **JetBrains Mono** 9–11 uppercase .14–.2em.
Spacing: 4 · 8 · 9 · 12 · 14 · 16 · 22 · 30 · 32 · 64px. Radius: 0 everywhere (except pill chips in direction 3b, 999px). Shadows: none — separation is by hairline rules and background tone. Hit targets ≥44px.
Breakpoints: <600 single/2-col · 600–899 3-col · ≥900 desktop, 4–5-col, 1280px max content width.

## Assets
- `assets/sthree-logo-full.png` — client logo, background keyed to transparent, for cream/light surfaces. **Use this everywhere on light backgrounds.**
- `assets/sthree-logo-full-dark.png` — same mark recoloured cream + gold for dark surfaces (`#12100E`).
- `assets/sthree-logo-original.jpg` — the client's original file (cream card on grey), kept for provenance only; do not use in the build.
- Product/hero photography: **not supplied.** Needed from the client — hero 1080×1350 portrait, category tiles 3:4, product cards 4:5. Serve WebP at 1×/2×.
- Fonts loaded from Google Fonts; self-host for production.

## Files
- `index.html` — the implementable reference for this direction.
- `reference/Sthree Boutique (all directions).dc.html` + `reference/support.js` — full exploration, all breakpoints and the two alternate directions (3b Catalogue, 3c Dark luxe).

## Open items for the client / next steps
1. Real photography for hero, 5 category tiles, 6 products.
2. Mobile nav overlay design.
3. Google Maps embed key/place ID for the Visit section.
4. Confirm which WhatsApp number is primary (76250 77531 is used throughout).
