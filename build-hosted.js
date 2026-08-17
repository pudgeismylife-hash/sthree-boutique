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

  const seq = {}, CAT = {ethnic:"ETH", western:"WES", coord:"COR", jewellery:"JWL"};
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
        offers: {
          // availability is deliberately omitted: the boutique has not
          // supplied stock status, and asserting InStock could be wrong.
          "@type": "Offer", price: String(p.price), priceCurrency: "INR",
          url: base + "/?p=" + key,
          seller: {"@type": "Organization", name: "Sthree Boutique"}
        }
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
  const CAT = {ethnic:"ETH", western:"WES", coord:"COR", jewellery:"JWL"};
  const LABEL = {ethnic:"Ethnic wear", western:"Western wear", coord:"Co-ord sets", jewellery:"Jewellery"};
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
         + `<td class="code">Rs ${r.price.toLocaleString("en-IN")}</td><td class="box">☐ ☐ ☐</td></tr>`;
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
  const rupee = n => "Rs " + Number(n).toLocaleString("en-IN");
  const thumbOf = p => {
    const t = DIR + p.images[0].replace("assets/products/", "assets/products/thumb/");
    return fs.existsSync(t) ? `<img src="data:image/jpeg;base64,${fs.readFileSync(t).toString("base64")}" alt="">` : "";
  };
  /* Codes are derived the same way as the schema and the shot list, from
     category order, so all three name a piece identically. */
  const CAT = {ethnic:"ETH", western:"WES", coord:"COR", jewellery:"JWL"};
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

  const clothing = items.filter(p => p.cat !== "jewellery");
  const jewellery = items.filter(p => p.cat === "jewellery");
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

<h2>1 &nbsp;Your second WhatsApp number</h2>
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
console.log("logo   " + logoName + " (" + kb(logoBytes.length) + ")");
console.log("index.html                    " + kb(pages.length) + "   links " + logoName);
console.log("sthree-boutique-hosted.html   " + kb(artifact.length) + "   logo inlined");
console.log("sthree-boutique-share.html    " + kb(share.length) + "   logo inlined");
if (!SITE_URL) {
  console.log("");
  console.log("NOTE  SITE_URL is empty, so link previews will not work yet.");
  console.log("      Set it at the top of this file to the live address, then rerun.");
}
