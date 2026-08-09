# Handoff: Sthree Boutique — Mobile Storefront App

## Overview
A mobile-first storefront for **Sthree Boutique** (Instagram @sthreeboutique2026), a boutique selling
western wear, ethnic wear, anti-tarnish jewellery, press-on nails, and (soon) bags. The app is a
browse-and-enquire catalogue: customers browse by category, open a product sheet, add pieces to a bag,
and complete the order over WhatsApp or a phone call to **+91 90360 87427**. There is no payment
integration — checkout hands off to WhatsApp with a prefilled order message.

## About the Design Files
The files in this bundle are **design references created in HTML** — a working prototype showing the
intended look and behaviour, **not production code to copy directly**. The task is to **recreate these
designs in the target codebase's environment** (React Native, Next.js, Vue, SwiftUI, Shopify theme,
etc.) using that codebase's established patterns, component library, and data layer. If no codebase
exists yet, pick the framework that best fits the goal (a React/Next.js PWA is a good default for a
boutique catalogue) and implement the designs there.

Files:
- `Sthree Boutique App.dc.html` — the authored source (template + logic; product data lives at the top of the script block).
- `standalone-preview.html` — self-contained build; open in any browser to click through the real thing.
- `image-slot.js` — the drag-and-drop image placeholder component used for every product photo. **Not for production** — replace each `<image-slot>` with a real `<img>`/CDN image.
- `sthree-logo.jpg` — the brand logo (also used as favicon and og:image).

## Fidelity
**High-fidelity.** Colors, typography, spacing, motion, and interactions are final and should be
recreated closely. The only deliberate placeholders are: product **photography** (image slots) and the
**product catalogue data** (10 demo products with demo prices) — both to be replaced with the client's
real assets and inventory.

## Screens / Views

The whole app renders inside a centered shell: `width:100%; max-width:460px; min-height:100vh;
background:#faf6ef; overflow:hidden`, on a `#e8e4de` page backdrop with `box-shadow:0 0 60px rgba(0,0,0,.12)`.
On phones it is full-bleed; on desktop it reads as a phone-width column. Content area has
`padding-bottom:104px` to clear the fixed tab bar.

### Global — App bar (sticky)
- `position:sticky; top:0; z-index:40`, `background:rgba(250,246,239,.92)`, `backdrop-filter:blur(12px)`,
  `border-bottom:1px solid rgba(21,19,15,.07)`, `padding:14px 20px 12px`, flex, space-between.
- **Wordmark** (left): "Sthree" — Pinyon Script 30px, `#a8842c`, `line-height:.9`; under it "BOUTIQUE" —
  Jost 8.5px, `letter-spacing:.42em`, `#15130f`, `margin-top:3px`.
- **CALL pill**: `height:38px; padding:0 14px; border:1px solid rgba(168,132,44,.45); border-radius:999px;`
  font 11px / `letter-spacing:.14em`, color `#a8842c`. Href `tel:+919036087427`.
  Hover: background `#a8842c`, text `#faf6ef`.
- **BAG button**: 38×38 circle, `border:1px solid rgba(21,19,15,.15)`, label "BAG" 10px. Badge appears
  only when count > 0: absolute `top:-5px; right:-5px`, min-width 17px, height 17px, radius 999px,
  background `#a8842c`, text `#faf6ef` 9px.

### Global — Bottom tab bar (fixed)
- `position:fixed; bottom:0; width:100%; max-width:460px; z-index:50`, `background:rgba(250,246,239,.94)`,
  `backdrop-filter:blur(14px)`, `border-top:1px solid rgba(21,19,15,.08)`, `display:grid;
  grid-template-columns:repeat(4,1fr); padding:12px 8px 16px`.
- Items: **HOME · SHOP · BAG · CONTACT**. Jost 9.5px, `letter-spacing:.2em`.
  Active `#15130f`; inactive `rgba(21,19,15,.35)`. Active item shows a 14×1px `#a8842c` underline dot,
  absolutely positioned `bottom:2px; left:50%; translateX(-50%)`.

### 1. Home
- **Hero**: 430px tall image area (`linear-gradient(160deg,#f2ebdd,#e6dac6)` behind the photo), photo
  `object-fit:cover`, full-bleed.
- **Hero overlay**: absolutely positioned at the bottom, `padding:26px 22px 24px`,
  `background:linear-gradient(to top,rgba(250,246,239,.97) 45%,rgba(250,246,239,0))`.
  - Eyebrow "AUTUMN EDIT · 2026" — 9.5px, `letter-spacing:.34em`, `#a8842c`, margin-bottom 8px.
  - Headline "Dressed for / *every* occasion" — Cormorant Garamond 38px weight 300, `line-height:1.05`,
    `letter-spacing:-.01em`; the word "every" is Pinyon Script 46px in `#a8842c` (not italic).
  - Buttons row, `gap:10px`, height 46px, radius 2px:
    **SHOP THE EDIT** (flex:1, bg `#15130f`, text `#faf6ef`, 11px / `.2em`; hover bg `#a8842c`) → Shop screen;
    **ENQUIRE** (outline `1px solid rgba(21,19,15,.2)`, 11px / `.16em`) → `https://wa.me/919036087427`.
- **Shop by category**: section title Cormorant Garamond 22px; right-side "ALL" text button 10px /
  `.18em` in `#a8842c` → Shop screen. Horizontal scroller, `gap:14px`, `padding:18px 20px 6px`.
  Each tile: 104×132 photo card + label (Jost 9.5px / `.16em`) + count line (JetBrains Mono 8.5px,
  `rgba(21,19,15,.4)`) reading "N pieces" — or "coming soon" for BAGS.
  Categories: WESTERN, ETHNIC, JEWELLERY, PRESS-ON NAILS, BAGS. Tapping filters the Shop screen.
- **Promise card**: `margin:22px 20px; padding:20px; border:1px solid rgba(168,132,44,.3);
  background:linear-gradient(135deg,#f4ecdc,#faf6ef)`. Eyebrow "THE STHREE PROMISE" 9px / `.3em` `#a8842c`;
  body Cormorant Garamond 19px: "Anti-tarnish jewellery, hand-checked before it reaches you — with a
  one-year shine guarantee."
- **Just in**: title Cormorant Garamond 22px + right-side count in JetBrains Mono 9px. Grid
  `repeat(2,minmax(0,1fr))`, `gap:14px`, `padding:16px 20px 0`; first 4 products; card image 200px tall.
- **Card anatomy**: image pane; title Cormorant Garamond 15px `margin-top:9px`; price row
  (₹ price 11px `#a8842c`) + category label 9px `rgba(21,19,15,.35)`. Whole card opens the product sheet.
- **Dark CTA block**: `margin:34px 20px 0; padding:24px 20px; background:#15130f; color:#faf6ef`.
  Eyebrow "VISIT / ORDER" 9px / `.3em` `#c9a75a`; headline Cormorant Garamond 26px weight 300
  "Styling help on call, / every day 10am–8pm"; buttons height 44px — **90360 87427** (bg `#c9a75a`,
  text `#15130f`, `tel:`) and **INSTAGRAM** (outline `rgba(250,246,239,.3)`).

### 2. Shop
- Title "The Collection" — Cormorant Garamond 30px weight 300, `padding:22px 20px 0`.
- **Filter chips**, sticky at `top:65px`, `background:rgba(250,246,239,.95)`, blur(8px), `z-index:20`,
  horizontal scroll, `gap:8px`, `padding:16px 20px 14px`. Chip: height 34px, `padding:0 16px`,
  radius 999px, Jost 9.5px / `.16em`. Selected: bg `#15130f`, text `#faf6ef`, border `#15130f`.
  Unselected: transparent, text `#15130f`, border `rgba(21,19,15,.15)`. Order: ALL, WESTERN, ETHNIC,
  JEWELLERY, PRESS-ON NAILS, BAGS.
- **Grid**: `repeat(2,minmax(0,1fr))`, `gap:16px`, image 210px tall. Same card anatomy as Home (no
  category label under price).
- **Empty state** (BAGS): centered, `padding:60px 30px`, Cormorant Garamond 20px, `rgba(21,19,15,.5)`:
  "Bags are landing soon — call to pre-book."

### 3. Product sheet (modal, over any screen)
- Backdrop `rgba(21,19,15,.45)`, fades in 250ms; tap to dismiss.
- Panel: bottom-anchored, `max-width:460px`, `max-height:88vh`, scrollable, bg `#faf6ef`,
  slides up 320ms `cubic-bezier(.22,1,.36,1)`.
- Image 330px tall, full-bleed. Close button top-right: 34×34 circle, `rgba(250,246,239,.9)`, "×".
- Body `padding:22px 22px 26px`: category eyebrow 9px / `.3em` `#a8842c`; name Cormorant Garamond 28px
  weight 300; price 14px `#a8842c`; description Cormorant Garamond 16px weight 300 `rgba(21,19,15,.6)`,
  `line-height:1.55`.
- **Size row**: buttons height 36px, `padding:0 14px`, Jost 10px / `.14em`. Selected: bg `#15130f`,
  text `#faf6ef`. Unselected: transparent, border `rgba(21,19,15,.18)`. First size preselected.
- **Actions**: **ADD TO BAG** (flex:1, height 50px, bg `#15130f`, 11px / `.2em`; label switches to
  "ADDED TO BAG ✓" after tapping; hover `#a8842c`) and **ASK** (outline, height 50px) → WhatsApp with
  prefilled text `Hi! Is "<name>" (₹<price>) available?`.

### 4. Bag
- Title "Your Bag" Cormorant Garamond 30px weight 300.
- **Empty state**: `padding:70px 10px`, centered — "Nothing picked yet." Cormorant Garamond 20px
  `rgba(21,19,15,.5)`; **BROWSE PIECES** outline button height 44px, `padding:0 26px`, 11px / `.18em`
  (hover: bg `#15130f`, text `#faf6ef`).
- **Line item**: flex row, `gap:14px`, 62×76 thumbnail; name Cormorant Garamond 16px; meta line 10px /
  `.12em` `rgba(21,19,15,.4)` = "<CATEGORY> · QTY n"; right column shows ₹line-total 12px `#a8842c` and a
  **REMOVE** text button 9px / `.14em` `rgba(21,19,15,.35)`.
- **Summary**: top border `rgba(21,19,15,.1)`, `padding-top:16px`. Row "SUBTOTAL" / ₹total (12px /
  `.1em`; total in `#a8842c`). Note in JetBrains Mono 9px: "Order is confirmed over WhatsApp — payment
  link follows." CTA **SEND ORDER ON WHATSAPP** height 50px, bg `#15130f`, 11px / `.2em`.

### 5. Contact
- Title "Say hello" 30px; intro Cormorant Garamond 17px weight 300 `rgba(21,19,15,.6)`: "Share your
  size, occasion or a screenshot — we curate a set for you within the hour."
- Three tap rows (`padding:20px; border:1px solid rgba(21,19,15,.12); background:#fff`; hover border
  `#a8842c`), each: eyebrow 9px / `.3em` `#a8842c` + value Cormorant Garamond 24px, and a right-hand
  "TAP" label 11px / `.14em`:
  1. CALL — "90360 87427" → `tel:+919036087427`
  2. WHATSAPP — "Chat with us" → `https://wa.me/919036087427?text=Hi%20Sthree%20Boutique!`
  3. INSTAGRAM — "@sthreeboutique2026" → `https://instagram.com/sthreeboutique2026`
- **Delivery block**: bg `#15130f`, `padding:22px`; eyebrow "DELIVERY" `#c9a75a`; body Cormorant
  Garamond 20px weight 300: "Same-day within the city. / All-India shipping in 3–5 days."
- Footer: "Sthree" Pinyon Script 26px `#a8842c` + "BOUTIQUE · EST 2026" 8px / `.4em`.

## Interactions & Behavior
- **Navigation**: tab bar switches screens and resets scroll to top; category tile and "ALL"/"SHOP THE
  EDIT" buttons jump to Shop (tile also applies its filter). Screens are client-side only — consider
  real routes (`/`, `/shop`, `/bag`, `/contact`, `/product/:id`) in production.
- **Product sheet**: opening sets the selected product, preselects its first size, resets the
  "added" flag. Closes on backdrop tap or ×.
- **Add to bag**: increments qty if the product is already in the bag, else appends with qty 1; button
  label flips to "ADDED TO BAG ✓" (persists until the sheet is reopened).
- **WhatsApp checkout**: builds `https://wa.me/919036087427?text=<encoded>` with
  `Hi Sthree Boutique! I'd like to order: 2× Ivory satin slip dress, 1× Pearl drop earrings. Total ₹5,790.`
- **Animations**: `fadeIn` 300–350ms on screen change; `riseIn` (14px up + fade) 350–400ms on cards;
  `sheetUp` 320ms `cubic-bezier(.22,1,.36,1)` on the modal.
- **3D card tilt**: wrapper `perspective:1000px`; inner pane resting state
  `transform:rotateY(-9deg) rotateX(5deg)` with `box-shadow:14px 18px 34px -18px rgba(21,19,15,.45),
  0 2px 6px rgba(21,19,15,.08)`; on hover `rotateY(0) rotateX(0) scale(1.03)` with
  `box-shadow:6px 26px 46px -20px rgba(21,19,15,.5)`; transition 550ms `cubic-bezier(.22,1,.36,1)`.
  A non-interactive gloss layer sits on top:
  `linear-gradient(115deg,rgba(255,255,255,.42) 0%,rgba(255,255,255,0) 34%,rgba(255,255,255,0) 68%,rgba(168,132,44,.16) 100%)`,
  fading to `opacity:.35` on hover. On touch devices consider triggering the tilt on scroll-into-view
  instead of hover, and respect `prefers-reduced-motion`.
- **Responsive**: single fluid column capped at 460px; everything else scales. Grids use
  `minmax(0,1fr)` (required — `1fr` alone lets image min-content width overflow the shell).
- **Not built (add in production)**: search, wishlist, quantity stepper in the bag, size guide,
  real product detail routes, stock state, analytics, order persistence.

## State Management
Single component state:
- `screen`: `'home' | 'shop' | 'cart' | 'contact'` (default `'home'`)
- `cat`: `'all' | 'western' | 'ethnic' | 'jewellery' | 'nails' | 'bags'` (default `'all'`)
- `sel`: selected product object or `null` (drives the modal)
- `size`: selected size string
- `cart`: array of `{...product, qty}`
- `added`: boolean, "ADDED TO BAG ✓" feedback flag

Derived: `cartCount` (sum of qty), `total` (qty × numeric price, formatted `en-IN`), filtered product
list, WhatsApp URLs. In production the catalogue should come from an API/CMS and the cart should
persist (localStorage or account).

## Design Tokens
**Colors**
| Token | Value | Use |
|---|---|---|
| Ink | `#15130f` | Text, primary buttons, dark blocks |
| Cream | `#faf6ef` | App background, text on dark |
| Page backdrop | `#e8e4de` | Area outside the phone column |
| Gold | `#a8842c` | Wordmark, prices, eyebrows, links, hover |
| Gold light | `#c9a75a` | Accents on dark blocks |
| Border | `rgba(21,19,15,.12)` / `.15` / `.18` | Outlines, dividers |
| Muted text | `rgba(21,19,15,.35–.6)` | Meta, captions, body |
| Gold border | `rgba(168,132,44,.3–.45)` | Promise card, call pill |
| Card gradients | western `#ece6dc→#e2d8c8`, ethnic `#f0e3d6→#e6d2bd`, jewellery `#f3ead3→#e8d9b0`, nails `#f1e4e4→#e6d2d2`, bags `#e9e6e0→#dcd7ce` | Image fallback per category (`linear-gradient(150deg,…)`) |

**Typography** — Cormorant Garamond (300/400) for headings and product names; Jost (300/400/500) for UI
labels and buttons; Pinyon Script for the wordmark and the accent word "every"; JetBrains Mono (300/400)
for micro-captions.
Scale: 38 / 30 / 28 / 26 / 24 / 22 / 20 / 19 / 17 / 16 / 15 / 14 / 12 / 11 / 10 / 9.5 / 9 / 8.5 / 8 px.
Letter-spacing: `.42em` (BOUTIQUE), `.3–.34em` (eyebrows), `.2em` (buttons/tabs), `.14–.18em` (small
labels), `.06em` (prices), `-.01em` (display headline).

**Spacing** — 3, 4, 6, 8, 9, 10, 12, 14, 16, 18, 20, 22, 24, 26, 30, 34 px. Screen gutter: 20px.
**Radius** — 0 (blocks/cards), 2px (buttons/tiles), 999px (pills, badge).
**Heights** — hero 430; sheet image 330; shop card image 210; home card image 200; category tile 104×132;
bag thumb 62×76; primary CTA 50; secondary 44/46; chip 34; header pill/bag 38.
**Shadows** — shell `0 0 60px rgba(0,0,0,.12)`; card rest/hover as listed under 3D card tilt.

## Assets
- `sthree-logo.jpg` — client-supplied logo (black gown illustration, gold script "Sthree", "BOUTIQUE").
  Used as favicon and og:image; the header currently renders the wordmark as live text in Pinyon Script
  so it stays crisp — keep that, or swap in an SVG version of the logo if the client can supply one.
- **Product photography: not supplied.** Every product image is an `<image-slot>` placeholder. Replace
  with real photos at 4:5 (cards) and roughly 4:3 (sheet hero), served from a CDN with `srcset`.
- Icons: none — the design is deliberately text-label-only. Keep it that way if possible.
- Fonts: Google Fonts — Cormorant Garamond, Jost, Pinyon Script, JetBrains Mono.

## Content notes
Product names, descriptions, prices and the "AUTUMN EDIT · 2026" hero copy are **demo content** written
for the prototype. Replace with the client's real inventory before launch. Contact details are real:
phone **+91 90360 87427**, Instagram **@sthreeboutique2026**. Copy is British English
("jewellery", "anti-tarnish", "co-ord").

## Files
- `Sthree Boutique App.dc.html` — source of truth for markup, styles, and logic.
- `standalone-preview.html` — click-through build (open directly in a browser).
- `image-slot.js` — prototype-only image placeholder component.
- `sthree-logo.jpg` — brand logo.
