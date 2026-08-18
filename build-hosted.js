/* Builds every distributable copy from sthree-boutique.html, which stays
   the single source of truth. Run:  node build-hosted.js

   Outputs
     index.html                     GitHub Pages site. Links logo.jpg and
                                    og-image.jpg normally, so WhatsApp and
                                    other crawlers can fetch the thumbnail.
     sthree-boutique-hosted.html    Claude artifact copy. Document wrapper
                                    stripped (the host supplies its own) and
                                    the logo inlined, because a published
                                    artifact cannot fetch external files.
     sthree-boutique-share.html     Standalone file to send on WhatsApp.
                                    Logo inlined so it travels with the file.
*/
const fs = require("fs");

/* The project folder is wherever this script lives, so the build runs from any
   checkout on any machine rather than one hardcoded path. Kept with a trailing
   slash and forward slashes, as every path below is built by concatenation. */
const DIR = __dirname.replace(/\\/g, "/").replace(/\/?$/, "/");
const SRC = DIR + "sthree-boutique.html";

/* Public base URL of the live site, no trailing slash. Until this is set,
   link previews cannot work — crawlers need an absolute address.
   For GitHub Pages it is:  https://<user>.github.io/<repo>          */
const SITE_URL = "https://pudgeismylife-hash.github.io/sthree-boutique";

const src = fs.readFileSync(SRC, "utf8");

/* ── the logo ───────────────────────────────────────────────────── */
const MIME = { ".png":"image/png", ".jpg":"image/jpeg", ".jpeg":"image/jpeg", ".webp":"image/webp", ".svg":"image/svg+xml" };
const logoFile = ["assets/logo-web.png","logo.jpg","logo.png"]
  .map(f => DIR + f).find(p => fs.existsSync(p));

if (!logoFile) { console.error("FAIL no logo file (expected logo.jpg or logo.png in " + DIR + ")"); process.exit(1); }

// Path relative to the site root, so index.html can link it directly.
const logoName = logoFile.slice(DIR.length);
const logoBytes = fs.readFileSync(logoFile);
const logoDataUri = "data:" + MIME[logoFile.slice(logoFile.lastIndexOf("."))] + ";base64," + logoBytes.toString("base64");

function setLogo(s, value) {
  const out = s.replace(/logo     : ""/, 'logo     : "' + value + '"');
  if (out === s) { console.error("FAIL could not patch the logo setting"); process.exit(1); }
  return out;
}
const setSiteUrl = (s, url) => s.split("__SITE_URL__").join(url);

/* Product and hero photos are linked relatively, which is right for the hosted site
   but broken for the artifact (cannot fetch external files) and for the
   standalone copy (travels on its own). Inline them for those two. */
function inlineProducts(s) {
  const cache = new Map();
  return s.replace(/assets\/(?:products\/|hero-)[A-Za-z0-9._-]+\.jpg/g, ref => {
    if (!cache.has(ref)) {
      const p = DIR + ref;
      if (!fs.existsSync(p)) { console.error("FAIL missing product image: " + ref); process.exit(1); }
      cache.set(ref, "data:image/jpeg;base64," + fs.readFileSync(p).toString("base64"));
    }
    return cache.get(ref);
  });
}

/* Emit Product structured data at build time, so search engines see the
   catalogue without having to run the page's JavaScript. Read from the same
   arrivals list the page renders, so the two cannot drift. */
function productSchema(s, base) {
  const m = s.match(/const arrivals = \[([\s\S]*?)\n\];/);
  if (!m) { console.error("FAIL could not find the arrivals list for schema"); process.exit(1); }
  const P = "assets/products/";
  let items;
  try { items = eval("[" + m[1] + "]"); }
  catch (e) { console.error("FAIL could not parse arrivals:", e.message); process.exit(1); }

  const seq = {}, CAT = {ethnic:"ETH", western:"WES", coord:"COR", jewellery:"JWL", nails:"NLS", bags:"BAG"};
  const list = items.map((p, n) => {
    seq[p.cat] = (seq[p.cat] || 0) + 1;
    const key = p.key;
    const code = "SB-" + (CAT[p.cat] || "GEN") + "-" + String(seq[p.cat]).padStart(2, "0");
    return {
      "@type": "ListItem", position: n + 1,
      item: {
        "@type": "Product", name: p.name, sku: code,
        image: base + "/" + p.images[0], url: base + "/?p=" + key,
        brand: {"@type": "Brand", name: "Sthree Boutique"},
        category: p.label,
        // The offer is omitted entirely for a piece the boutique has not
        // priced. A Product without an Offer is valid; an Offer without a
        // price is not, and inventing one to satisfy a validator would put a
        // figure she never gave in front of a search engine.
        ...(p.price == null ? {} : { offers: {
          // availability is deliberately omitted: the boutique has not
          // supplied stock status, and asserting InStock could be wrong.
          "@type": "Offer", price: String(p.price), priceCurrency: "INR",
          url: base + "/?p=" + key,
          seller: {"@type": "Organization", name: "Sthree Boutique"}
        }})
      }
    };
  });
  const json = JSON.stringify({"@context":"https://schema.org","@type":"ItemList",
    name:"Sthree Boutique collection", numberOfItems:list.length, itemListElement:list});
  return { html: s.replace("<!-- __PRODUCT_SCHEMA__ -->",
    '<script type="application/ld+json">' + json + '<\/script>'), count: list.length, items };
}

/* A printable list for the boutique: every piece with its thumbnail, code and
   three checkboxes, so photos come back named and matchable. Built from the
   same catalogue, so it cannot fall out of step with the site. */
function shotList(items) {
  const CAT = {ethnic:"ETH", western:"WES", coord:"COR", jewellery:"JWL", nails:"NLS", bags:"BAG"};
  const LABEL = {ethnic:"Ethnic wear", western:"Western wear", coord:"Co-ord sets", jewellery:"Jewellery", nails:"Press-on nails", bags:"Bags"};
  const seq = {};
  const rows = items.map(p => {
    seq[p.cat] = (seq[p.cat] || 0) + 1;
    const thumb = DIR + p.images[0].replace("assets/products/", "assets/products/thumb/");
    return {
      cat: p.cat, name: p.name, price: p.price,
      code: "SB-" + (CAT[p.cat] || "GEN") + "-" + String(seq[p.cat]).padStart(2, "0"),
      b64: fs.existsSync(thumb) ? fs.readFileSync(thumb).toString("base64") : ""
    };
  });
  const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  let h = `<meta charset="utf-8"><title>Sthree Boutique — photo shot list</title>
<style>
body{font-family:system-ui,"Segoe UI",sans-serif;background:#FAF6F0;color:#14110F;margin:0;padding:24px}
h1{font-family:Georgia,serif;font-weight:400;font-size:26px;margin:0 0 4px}
p.sub{margin:0 0 18px;color:#57514A;font-size:13px;max-width:70ch;line-height:1.6}
.rules{background:#fff;border:1px solid rgba(20,17,15,.12);padding:14px 18px;margin-bottom:22px;font-size:13px;line-height:1.7;max-width:80ch}
.rules b{color:#A98037}
h2{font-family:Georgia,serif;font-weight:400;font-size:17px;margin:22px 0 8px;border-bottom:1px solid rgba(20,17,15,.12);padding-bottom:5px}
table{border-collapse:collapse;width:100%;max-width:900px}
td{border-bottom:1px solid rgba(20,17,15,.09);padding:7px 8px;vertical-align:middle;font-size:13px}
td.img{width:56px}img{width:48px;height:60px;object-fit:cover;display:block}
td.code{font-family:ui-monospace,Consolas,monospace;font-size:11px;color:#A98037;white-space:nowrap}
td.box{white-space:nowrap;font-size:16px;letter-spacing:5px;color:#8A8177}
@media print{body{background:#fff}.rules{break-inside:avoid}}
</style>
<h1>Photo shot list — Sthree Boutique</h1>
<p class="sub">One row per piece. Take <b>3 photos of each</b> and name the files with the code shown.</p>
<div class="rules">
<b>Do not send photos on WhatsApp as pictures</b> — WhatsApp shrinks them and the quality is lost for good.
Upload to Google Drive instead, or on WhatsApp use <b>Document</b> (paperclip &rarr; Document) so they arrive full size.<br>
<b>Name each file with the code:</b> SB-JWL-01-1.jpg, SB-JWL-01-2.jpg, SB-JWL-01-3.jpg<br>
<b>The 3 shots:</b> 1 = the whole piece, front. 2 = worn, or draped. 3 = close up of the fabric, work or clasp.<br>
<b>Light:</b> stand near a window in daytime. No flash. Same spot and same background every time.
</div>`;
  for (const cat of ["ethnic", "western", "coord", "jewellery"]) {
    const grp = rows.filter(r => r.cat === cat);
    if (!grp.length) continue;
    h += `<h2>${LABEL[cat]} — ${grp.length} pieces</h2><table>`;
    for (const r of grp) {
      const img = r.b64 ? `<img src="data:image/jpeg;base64,${r.b64}" alt="">` : "";
      h += `<tr><td class="img">${img}</td><td class="code">${r.code}</td><td>${esc(r.name)}</td>`
         + `<td class="code">${r.price == null ? "price?" : "Rs " + r.price.toLocaleString("en-IN")}</td>`
         + `<td class="box">☐ ☐ ☐</td></tr>`;
    }
    h += `</table>`;
  }
  fs.writeFileSync(DIR + "photo-shot-list.html", h, "utf8");
  return rows.length;
}

/* Everything still outstanding from the boutique, on one page she can answer in
   a single pass. Built from the same catalogue as the site, so the piece list
   and the prices quoted back to her cannot drift. Nothing here asserts a fact
   about a product; every row is a question or a statement of what the site
   shows today. */
function ownerQuestions(items) {
  const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const rupee = n => n == null ? "not priced yet" : "Rs " + Number(n).toLocaleString("en-IN");
  const thumbOf = p => {
    const t = DIR + p.images[0].replace("assets/products/", "assets/products/thumb/");
    return fs.existsSync(t) ? `<img src="data:image/jpeg;base64,${fs.readFileSync(t).toString("base64")}" alt="">` : "";
  };
  /* Codes are derived the same way as the schema and the shot list, from
     category order, so all three name a piece identically. */
  const CAT = {ethnic:"ETH", western:"WES", coord:"COR", jewellery:"JWL", nails:"NLS", bags:"BAG"};
  const seq = {}, code = new Map();
  for (const p of items) {
    seq[p.cat] = (seq[p.cat] || 0) + 1;
    code.set(p.key, "SB-" + (CAT[p.cat] || "GEN") + "-" + String(seq[p.cat]).padStart(2, "0"));
  }
  const codeOf = p => code.get(p.key);
  const byKey = k => items.find(p => p.key === k);
  /* Quoted back to her from the catalogue rather than typed in here, so the
     questionnaire cannot end up citing a price the site no longer shows. */
  const priceOf = k => { const p = byKey(k); return p ? rupee(p.price) : ""; };
  const codeKey = k => { const p = byKey(k); return p ? codeOf(p) : ""; };

  const GARMENT = ["ethnic", "western", "coord"];
  const clothing = items.filter(p => GARMENT.includes(p.cat));
  const jewellery = items.filter(p => p.cat === "jewellery");
  const unpriced = items.filter(p => p.price == null);
  const earrings = jewellery.filter(p => /^earring_/.test(p.key));

  let h = `<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sthree Boutique — what we still need from you</title>
<style>
body{font-family:system-ui,"Segoe UI",sans-serif;background:#FAF6F0;color:#14110F;margin:0;padding:24px;line-height:1.6}
.wrap{max-width:860px;margin:0 auto}
h1{font-family:Georgia,serif;font-weight:400;font-size:27px;margin:0 0 6px}
p.sub{margin:0 0 20px;color:#57514A;font-size:14px}
h2{font-family:Georgia,serif;font-weight:400;font-size:19px;margin:30px 0 4px;padding-bottom:5px;border-bottom:1px solid rgba(20,17,15,.12)}
p.why{margin:0 0 12px;color:#57514A;font-size:13px}
/* The clothing table is eight columns wide, which overflows a phone. Let each
   table scroll inside its own box so the page itself never does; printing is
   unaffected because the wrapper has no width of its own. */
.tw{overflow-x:auto;margin-top:6px}
table{border-collapse:collapse;width:100%;min-width:520px}
th{font-size:10px;letter-spacing:.09em;text-transform:uppercase;color:#8A8177;text-align:left;padding:0 8px 6px;font-weight:500}
td{border-bottom:1px solid rgba(20,17,15,.09);padding:7px 8px;vertical-align:middle;font-size:13px}
/* contain, not cover: she has to recognise which piece each row is, and a
   cropped jewellery shot can come out an unreadable dark corner. */
td.img{width:66px}img{width:58px;height:72px;object-fit:contain;background:#fff;display:block}
td.code{font-family:ui-monospace,Consolas,monospace;font-size:11px;color:#A98037;white-space:nowrap}
td.fill{background:#fff;border-bottom:1px solid rgba(20,17,15,.18);min-width:78px}
ol{padding-left:20px;margin:8px 0}
li{margin-bottom:14px}
.ask{font-weight:500}
.note{color:#57514A;font-size:13px}
.box{background:#fff;border:1px solid rgba(20,17,15,.12);padding:14px 18px;font-size:13px;margin:14px 0}
.box b{color:#A98037}
.ans{display:block;background:#fff;border:1px solid rgba(20,17,15,.18);height:30px;margin-top:6px}
@media print{body{background:#fff;padding:0}.box,li,table{break-inside:avoid}}
</style>
<div class="wrap">
<h1>What we still need from you</h1>
<p class="sub">Sthree Boutique &middot; for Priyanka. Answer what you can &mdash; anything left blank
simply stays off the site rather than being guessed at.</p>

<div class="box">
<b>Why this matters:</b> the site never shows information we have not been given. Every
blank below is a row that is hidden from customers today. Filling one in makes it appear.
</div>

${unpriced.length ? `<h2>1 &nbsp;What do these cost?</h2>
<p class="why">${unpriced.length} piece${unpriced.length === 1 ? "" : "s"} on the site ${unpriced.length === 1 ? "has" : "have"} no price,
so ${unpriced.length === 1 ? "it shows" : "they show"} <b>&ldquo;Price on WhatsApp&rdquo;</b> instead of a number. The photographs you sent
carry no price, and the &#8377;999 printed on the maker's instruction card is <b>their</b> MRP,
not yours &mdash; we will not put that on your site as your price. Write what you sell each for
and the number appears.</p>
<div class="tw"><table><tr><th></th><th>Code</th><th>Piece</th><th>Your price</th></tr>
${unpriced.map(p => `<tr><td class="img">${thumbOf(p)}</td><td class="code">${codeOf(p)}</td>`
  + `<td>${esc(p.name)}</td><td class="fill"></td></tr>`).join("")}
</table></div>

<h2>2 &nbsp;Your second WhatsApp number</h2>` : `<h2>1 &nbsp;Your second WhatsApp number</h2>`}
<p class="why">You wrote <b>903608742</b> &mdash; that is nine digits and a mobile number needs ten,
so we have left it off the site rather than publish a number that might not reach you. One
handoff note says 9036087427 and another says 9036087420. Please write it out in full.</p>
<span class="ans"></span>

<h2>2 &nbsp;The ${earrings.length} earring names</h2>
<p class="why">Your sheet called all ${earrings.length} of these &ldquo;Antitarnish earring&rdquo;, which would have
made them impossible to tell apart on the site, so we named each one after what it looks
like. <b>These names are ours, not yours.</b> Change any you do not like.</p>
<div class="tw"><table><tr><th></th><th>Code</th><th>Name we used</th><th>Price</th><th>Your name for it</th></tr>`;
  for (const p of earrings) {
    h += `<tr><td class="img">${thumbOf(p)}</td><td class="code">${codeOf(p)}</td>`
       + `<td>${esc(p.name)}</td><td class="code">${rupee(p.price)}</td><td class="fill"></td></tr>`;
  }
  h += `</table></div>

<h2>3 &nbsp;Clothing &mdash; sizes, fabric and care</h2>
<p class="why">The site shows <b>no size at all</b> on clothing, because guessing a size list causes
wrong orders. Fabric, fit and care have a place on every product page and are empty on all
${items.length} pieces. Sizes can be a list (S, M, L) or free size.</p>
<div class="tw"><table><tr><th></th><th>Code</th><th>Piece</th><th>Price</th><th>Sizes</th><th>Fabric</th><th>Wash care</th><th>In stock?</th></tr>`;
  for (const p of clothing) {
    h += `<tr><td class="img">${thumbOf(p)}</td><td class="code">${codeOf(p)}</td>`
       + `<td>${esc(p.name)}</td><td class="code">${rupee(p.price)}</td>`
       + `<td class="fill"></td><td class="fill"></td><td class="fill"></td><td class="fill"></td></tr>`;
  }
  h += `</table></div>

<h2>4 &nbsp;Jewellery &mdash; what is in stock</h2>
<p class="why">All ${jewellery.length} show as free size, which we understand is right. The one thing missing
is whether each is available &mdash; you already mark &ldquo;Sold&rdquo; on Instagram. Until we have this the
site says nothing about availability either way. Tick, cross, or write the material if it
should be shown.</p>
<div class="tw"><table><tr><th></th><th>Code</th><th>Piece</th><th>Price</th><th>In stock?</th><th>Material, if you want it shown</th></tr>`;
  for (const p of jewellery) {
    h += `<tr><td class="img">${thumbOf(p)}</td><td class="code">${codeOf(p)}</td>`
       + `<td>${esc(p.name)}</td><td class="code">${rupee(p.price)}</td>`
       + `<td class="fill"></td><td class="fill"></td></tr>`;
  }
  h += `</table></div>

<h2>5 &nbsp;Quick questions</h2>
<ol>`;

  /* These two ask about particular pieces, so they are emitted only while those
     pieces are still in the catalogue, and quote their live code and price. */
  const pair = (a, b) => byKey(a) && byKey(b);
  if (pair("gowns_1", "gowns_2")) {
    h += `<li><span class="ask">Are the two linen dresses one product or two?</span><br>
<span class="note">${codeKey("gowns_1")} (black) at ${priceOf("gowns_1")} and ${codeKey("gowns_2")} (orange) at
${priceOf("gowns_2")}. Right now they are two separate products. If it is one dress in two colours,
say so and we will merge them into one with a colour choice.</span><span class="ans"></span></li>
`;
  }
  if (pair("necklace_2", "necklace_3")) {
    h += `<li><span class="ask">Are these two necklaces different?</span><br>
<span class="note">${codeKey("necklace_2")} &ldquo;${esc(byKey("necklace_2").name)}&rdquo; at ${priceOf("necklace_2")} and
${codeKey("necklace_3")} &ldquo;${esc(byKey("necklace_3").name)}&rdquo; at ${priceOf("necklace_3")} read almost the same.
If they differ, what should each be called?</span><span class="ans"></span></li>
`;
  }

  h += `<li><span class="ask">What does delivery cost, and how long does it take?</span><br>
<span class="note">The site says &ldquo;all over India and worldwide&rdquo; with no charge and no timeline,
because none was given. Even &ldquo;3&ndash;5 days within Karnataka&rdquo; helps a customer decide.</span><span class="ans"></span></li>

<li><span class="ask">Which pieces are imported and which are Indian?</span><br>
<span class="note">Your brand line is &ldquo;Imported &amp; Indian&rdquo; but no piece says which, so the cards show
the category instead. If it is easier, just tell us which <em>categories</em> are imported.</span><span class="ans"></span></li>

<li><span class="ask">One real customer review.</span><br>
<span class="note">One honest line from a happy customer, with her first name and town. There is a
place for it on the site that stays hidden until you give us a real one &mdash; we will not write it
for you.</span><span class="ans"></span></li>

<li><span class="ask">Press-on nails and bags.</span><br>
<span class="note">Both are listed as categories but have no products, so they show &ldquo;Coming soon&rdquo;.
Send photos and prices and they go live; tell us to drop them and they come off.</span><span class="ans"></span></li>

<li><span class="ask">One photograph of a co-ord set being worn.</span><br>
<span class="note">The co-ord tile is the weakest picture on the site &mdash; it is a flat product render
while every other category shows a real photograph. One good photo of
${codeKey("cloth_section_western_wear_2")} or ${codeKey("cloth_section_western_wear_3")} fixes it.</span><span class="ans"></span></li>
</ol>

<h2>6 &nbsp;Spellings we corrected</h2>
<p class="why">We fixed these from your sheet. Tell us if any is actually right as you wrote it.</p>
<div class="box">
Lilen &rarr; <b>Linen</b> &nbsp;&middot;&nbsp; desiner &rarr; <b>designer</b> &nbsp;&middot;&nbsp;
polyster &rarr; <b>polyester</b> &nbsp;&middot;&nbsp; kafthan &rarr; <b>kaftan</b> &nbsp;&middot;&nbsp;
Plazo &rarr; <b>Palazzo</b> &nbsp;&middot;&nbsp; Studed &rarr; <b>Studded</b> &nbsp;&middot;&nbsp;
sequence &rarr; <b>sequin</b>
</div>

<h2>7 &nbsp;More photographs</h2>
<p class="why">${items.filter(p => (p.images||[]).length > 1).length} of the ${items.length} pieces have three photographs and look far better for it;
the other ${items.filter(p => (p.images||[]).length === 1).length} have one. The separate <b>photo shot list</b> has every code with tick boxes.</p>
<div class="box">
<b>Please do not send photos as WhatsApp pictures</b> &mdash; WhatsApp shrinks them and the quality is
lost for good. Use Google Drive, or on WhatsApp attach them with <b>Document</b> (paperclip
&rarr; Document).<br>
<b>Name each file with its code:</b> SB-JWL-01-1.jpg, SB-JWL-01-2.jpg, SB-JWL-01-3.jpg
</div>
</div>`;
  fs.writeFileSync(DIR + "owner-questions.html", h, "utf8");
  return { clothing: clothing.length, jewellery: jewellery.length };
}

/* The service worker, so the site can be installed to a phone's home screen.
   Chrome will not offer "Install" without one.

   Deliberately network-first for pages. A cache-first worker on a shop is how
   an owner updates a price and keeps being told the old one is still showing;
   the cache here is a fallback for a bad connection, not the source of truth.
   Photographs are cache-first because their names change when they change.

   The cache name carries a hash of the built page, so every deploy retires the
   previous cache instead of layering on top of it. */
function serviceWorker(builtHtml) {
  const ver = require("crypto").createHash("sha1").update(builtHtml).digest("hex").slice(0, 10);
  fs.writeFileSync(DIR + "sw.js",
`/* Generated by build-hosted.js — do not edit. Rebuilt on every deploy. */
const VERSION = "sthree-${ver}";
const SHELL = ["./", "./index.html", "./manifest.webmanifest",
  "./assets/icons/icon-192.png", "./assets/icons/icon-512.png"];

self.addEventListener("install", e => {
  self.skipWaiting();
  e.waitUntil(caches.open(VERSION).then(c => c.addAll(SHELL)).catch(() => {}));
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    for (const k of await caches.keys()) if (k !== VERSION) await caches.delete(k);
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET" || new URL(req.url).origin !== location.origin) return;

  // Pages: always try the network, so a change to a price or a photograph is
  // seen immediately. The cache only answers when the network cannot.
  if (req.mode === "navigate") {
    e.respondWith((async () => {
      try {
        const net = await fetch(req);
        const c = await caches.open(VERSION); c.put(req, net.clone());
        return net;
      } catch (_) {
        return (await caches.match(req)) || (await caches.match("./index.html")) ||
               new Response("Offline", { status: 503, headers: { "Content-Type": "text/plain" } });
      }
    })());
    return;
  }

  // Photographs and icons: served from the cache, refreshed behind the scenes.
  // A changed picture arrives under a changed name, so this cannot go stale.
  if (/\\.(?:jpg|jpeg|png|webp|ico|webmanifest)$/i.test(new URL(req.url).pathname)) {
    e.respondWith((async () => {
      const hit = await caches.match(req);
      const net = fetch(req).then(r => {
        if (r && r.ok) caches.open(VERSION).then(c => c.put(req, r.clone()));
        return r;
      }).catch(() => null);
      return hit || (await net) || new Response("", { status: 504 });
    })());
  }
});
`, "utf8");
  return ver;
}

/* The hero band shows the collection itself, so it can put a photograph in the
   most prominent place on the site. Two ways that could go wrong, both refused
   here rather than noticed later: naming a piece that is not in the catalogue,
   and naming one whose picture is a generated render rather than the boutique's
   own photograph. The old baked hero carried a render for weeks precisely
   because nothing checked. */
function checkHeroField(s, items) {
  let made = [];
  const m = s.match(/heroField:\s*\[([\s\S]*?)\]/);
  if (!m) { console.error("FAIL could not find CONFIG.heroField"); process.exit(1); }
  const keys = [...m[1].matchAll(/"([^"]+)"/g)].map(x => x[1]);
  if (!keys.length) { console.error("FAIL CONFIG.heroField is empty"); process.exit(1); }

  const known = new Map(items.map(p => [p.key, p]));
  const unknown = keys.filter(k => !known.has(k));
  if (unknown.length) {
    console.error("FAIL heroField names piece(s) not in the catalogue: " + unknown.join(", "));
    process.exit(1);
  }

  const lockPath = DIR + "product-image-lock.json";
  if (fs.existsSync(lockPath)) {
    const lock = JSON.parse(fs.readFileSync(lockPath, "utf8")).products || {};
    const rendered = new Map();
    const recreated = new Map();
    for (const [code, v] of Object.entries(lock)) {
      if (!v.productKey) continue;
      if (v.sourceReview) rendered.set(v.productKey, code);
      else if (v.recreated) recreated.set(v.productKey, code);
    }
    const bad = keys.filter(k => rendered.has(k));
    if (bad.length) {
      console.error("FAIL the hero may only show the boutique's own photographs.");
      for (const k of bad) console.error("     " + k + " (" + rendered.get(k) + ") is a generated render");
      process.exit(1);
    }
    /* A recreation is a different thing from a render of the wrong item, and is
       not fatal: these were checked against her own photograph of the same piece
       and match it. But the hero is the one place that trades on being the real
       shop, so it says so out loud every build rather than going quiet. */
    made = keys.filter(k => recreated.has(k));
    if (made.length) {
      console.log("NOTE " + made.length + " of " + keys.length +
                  " hero pieces show an AI recreation, not her photograph:");
      for (const k of made) console.log("     " + k + " (" + recreated.get(k) + ")");
    }
  }
  /* every hero photograph must actually have a cut crop on disk */
  const noCrop = keys.filter(k => !fs.existsSync(DIR + "assets/hero/" + k + ".jpg"));
  if (noCrop.length) {
    console.error("FAIL no hero crop for: " + noCrop.join(", "));
    console.error("     run:  python3 build-og-images.py --apply");
    process.exit(1);
  }
  return { n: keys.length, recreated: made.length };
}

/* One small page per product, carrying that product's own link preview.
   WhatsApp, Instagram and Facebook read the preview out of the HTML they are
   given and never run its JavaScript, so a single page that switches products
   client-side can only ever offer one preview for all 25. These give each piece
   its own, then send a real visitor on to the piece itself.

   ?p=<key> keeps working exactly as before; this is an extra address, not a
   replacement, so every link already shared stays valid. */
function productPages(items, base) {
  const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
  const dir = DIR + "p/";
  fs.mkdirSync(dir, { recursive: true });

  const LABEL = {ethnic:"Ethnic wear", western:"Western wear", coord:"Co-ord set", jewellery:"Jewellery", nails:"Press-on nails", bags:"Bags"};
  const seq = {}, CAT = {ethnic:"ETH", western:"WES", coord:"COR", jewellery:"JWL", nails:"NLS", bags:"BAG"};
  let written = 0, noCard = [];

  for (const p of items) {
    seq[p.cat] = (seq[p.cat] || 0) + 1;
    const code = "SB-" + (CAT[p.cat] || "GEN") + "-" + String(seq[p.cat]).padStart(2, "0");
    const card = "assets/og/" + p.key + ".jpg";
    if (!fs.existsSync(DIR + card)) noCard.push(p.key);

    const priced = p.price != null;
    const price = priced ? "₹" + Number(p.price).toLocaleString("en-IN") : "Price on WhatsApp";
    const title = priced ? p.name + " — " + price : p.name;
    const desc  = price + " · " + (LABEL[p.cat] || p.label) + " · " + code +
                  " · Sthree Boutique, Bikarnakatte, Mangalore. Order on WhatsApp.";
    const here  = base + "/p/" + p.key + ".html";
    const real  = base + "/?p=" + encodeURIComponent(p.key);
    /* Crawlers are given absolute addresses, which they require, but the
       redirect and the visible link are relative so the page also works opened
       from disk, from a preview host, or from anywhere the site is copied to
       rather than jumping to the live domain. */
    const rel   = "../?p=" + encodeURIComponent(p.key);

    fs.writeFileSync(dir + p.key + ".html",
`<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>${esc(title)} — Sthree Boutique</title>
<meta name="description" content="${esc(desc)}">
<link rel="canonical" href="${esc(real)}">
<meta property="og:type" content="product">
<meta property="og:site_name" content="Sthree Boutique">
<meta property="og:locale" content="en_IN">
<meta property="og:title" content="${esc(title)}">
<meta property="og:description" content="${esc(desc)}">
<meta property="og:url" content="${esc(here)}">
<meta property="og:image" content="${esc(base + "/" + card)}">
<meta property="og:image:secure_url" content="${esc(base + "/" + card)}">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="${esc(p.name)}">
${priced ? `<meta property="product:price:amount" content="${esc(String(p.price))}">
<meta property="product:price:currency" content="INR">` : ""}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="${esc(title)}">
<meta name="twitter:description" content="${esc(desc)}">
<meta name="twitter:image" content="${esc(base + "/" + card)}">
<style>
body{margin:0;background:#FAF6F0;color:#14110F;font-family:system-ui,"Segoe UI",sans-serif;
  display:grid;place-items:center;min-height:100vh;padding:24px;line-height:1.6}
.c{max-width:420px;text-align:center}
img{max-width:100%;height:auto;display:block;margin:0 auto 18px;border:1px solid rgba(20,17,15,.12)}
h1{font-family:Georgia,serif;font-weight:400;font-size:23px;margin:0 0 4px}
p{margin:0 0 18px;color:#57514A;font-size:14px}
.pr{color:#A98037;font-family:ui-monospace,Consolas,monospace}
a.b{display:inline-block;background:#14110F;color:#FAF6F0;text-decoration:none;
  padding:12px 22px;font-size:13px;letter-spacing:.1em;text-transform:uppercase}
a.b:focus-visible{outline:2px solid #A98037;outline-offset:3px}
</style>
</head>
<body>
<div class="c">
<img src="../${esc(card)}" alt="${esc(p.name)}" width="1200" height="630">
<h1>${esc(p.name)}</h1>
<p><span class="pr">${esc(price)}</span> · ${esc(LABEL[p.cat] || p.label)} · ${esc(code)}</p>
<p><a class="b" href="${esc(rel)}">View this piece</a></p>
</div>
<script>
/* Send a real visitor to the piece itself. replace(), not assign(), so Back
   returns to wherever they came from instead of bouncing them here again. */
location.replace(${JSON.stringify(rel)});
<\/script>
</body>
</html>
`, "utf8");
    written++;
  }
  return { written, noCard };
}

/* ── strip the document wrapper for the artifact host ───────────── */
function unwrap(s) {
  const out = s
    .replace(/<!doctype html>\s*/i, "")
    .replace(/<html[^>]*>\s*/i, "")
    .replace(/<\/html>\s*/i, "")
    .replace(/<head>\s*/i, "")
    .replace(/<\/head>\s*/i, "")
    .replace(/<body>\s*/i, "")
    .replace(/<\/body>\s*/i, "")
    .trim();
  // Whole-tag matches, so <header>/</header> are not mistaken for the wrapper.
  const left = [
    [/<!doctype/i, "<!doctype"],
    [/<html[\s>]/i, "<html>"], [/<\/html\s*>/i, "</html>"],
    [/<head[\s>]/i, "<head>"], [/<\/head\s*>/i, "</head>"],
    [/<body[\s>]/i, "<body>"], [/<\/body\s*>/i, "</body>"]
  ].filter(([re]) => re.test(out)).map(([, n]) => n);
  if (left.length) { console.error("FAIL leftover wrapper tags:", left.join(" ")); process.exit(1); }
  return out;
}

function check(s, label, needles) {
  const missing = needles.filter(n => !s.includes(n));
  if (missing.length) { console.error("FAIL " + label + " missing:", missing.join(" ")); process.exit(1); }
}

/* ── 1. GitHub Pages ────────────────────────────────────────────── */
let pages = setLogo(src, logoName);
pages = setSiteUrl(pages, SITE_URL || "__SITE_URL__");
const schema = productSchema(pages, SITE_URL || "");
pages = schema.html;
const shots = shotList(schema.items);
const asks = ownerQuestions(schema.items);
const stubs = productPages(schema.items, SITE_URL || "");
const heroN = checkHeroField(src, schema.items);
const swVer = serviceWorker(pages);
check(pages, "index.html", ["<!doctype html>", 'id="items"', "917625077531", "og:image", "assets/products/"]);
fs.writeFileSync(DIR + "index.html", pages, "utf8");

/* ── 2. Claude artifact ─────────────────────────────────────────── */
let artifact = unwrap(inlineProducts(setSiteUrl(setLogo(src, logoDataUri), SITE_URL)).replace("<!-- __PRODUCT_SCHEMA__ -->", ""));
check(artifact, "hosted", ["<title>", "<style>", 'id="items"', "917625077531", "Shop on WhatsApp"]);
fs.writeFileSync(DIR + "sthree-boutique-hosted.html", artifact, "utf8");

/* ── 3. Standalone to send as a file ────────────────────────────── */
const share = inlineProducts(setSiteUrl(setLogo(src, logoDataUri), SITE_URL)).replace("<!-- __PRODUCT_SCHEMA__ -->", "");
fs.writeFileSync(DIR + "sthree-boutique-share.html", share, "utf8");

const kb = n => Math.round(n / 1024) + " KB";
console.log("schema " + schema.count + " products");
console.log("shots  photo-shot-list.html (" + shots + " pieces)");
console.log("asks   owner-questions.html (" + asks.clothing + " clothing, " + asks.jewellery + " jewellery)");
console.log("share  p/*.html (" + stubs.written + " product link previews)");
console.log("hero   " + heroN.n + " pieces, " + (heroN.n - heroN.recreated) +
            " her own photograph" + (heroN.recreated ? ", " + heroN.recreated + " recreated" : ""));
console.log("app    sw.js + manifest, installable (cache sthree-" + swVer + ")");
if (stubs.noCard.length) {
  console.log("       WARN no preview card for: " + stubs.noCard.join(", "));
  console.log("       run:  python3 build-og-images.py --apply");
}
console.log("logo   " + logoName + " (" + kb(logoBytes.length) + ")");
console.log("index.html                    " + kb(pages.length) + "   links " + logoName);
console.log("sthree-boutique-hosted.html   " + kb(artifact.length) + "   logo inlined");
console.log("sthree-boutique-share.html    " + kb(share.length) + "   logo inlined");
if (!SITE_URL) {
  console.log("");
  console.log("NOTE  SITE_URL is empty, so link previews will not work yet.");
  console.log("      Set it at the top of this file to the live address, then rerun.");
}
