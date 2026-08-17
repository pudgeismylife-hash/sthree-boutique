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

const DIR = "C:/Maya test/";
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
console.log("logo   " + logoName + " (" + kb(logoBytes.length) + ")");
console.log("index.html                    " + kb(pages.length) + "   links " + logoName);
console.log("sthree-boutique-hosted.html   " + kb(artifact.length) + "   logo inlined");
console.log("sthree-boutique-share.html    " + kb(share.length) + "   logo inlined");
if (!SITE_URL) {
  console.log("");
  console.log("NOTE  SITE_URL is empty, so link previews will not work yet.");
  console.log("      Set it at the top of this file to the live address, then rerun.");
}
