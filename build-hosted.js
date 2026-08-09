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
const logoFile = ["logo.jpg","logo.jpeg","logo.png","logo.webp","logo.svg"]
  .map(f => DIR + f).find(p => fs.existsSync(p));

if (!logoFile) { console.error("FAIL no logo file (expected logo.jpg or logo.png in " + DIR + ")"); process.exit(1); }

const logoName = logoFile.slice(logoFile.lastIndexOf("/") + 1);
const logoBytes = fs.readFileSync(logoFile);
const logoDataUri = "data:" + MIME[logoFile.slice(logoFile.lastIndexOf("."))] + ";base64," + logoBytes.toString("base64");

function setLogo(s, value) {
  const out = s.replace(/logo     : ""/, 'logo     : "' + value + '"');
  if (out === s) { console.error("FAIL could not patch the logo setting"); process.exit(1); }
  return out;
}
const setSiteUrl = (s, url) => s.split("__SITE_URL__").join(url);

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
check(pages, "index.html", ["<!doctype html>", 'id="prodGrid"', "919036087427", "og:image"]);
fs.writeFileSync(DIR + "index.html", pages, "utf8");

/* ── 2. Claude artifact ─────────────────────────────────────────── */
let artifact = unwrap(setSiteUrl(setLogo(src, logoDataUri), SITE_URL));
check(artifact, "hosted", ["<title>", "<style>", 'id="prodGrid"', "919036087427", "demo-strip"]);
fs.writeFileSync(DIR + "sthree-boutique-hosted.html", artifact, "utf8");

/* ── 3. Standalone to send as a file ────────────────────────────── */
const share = setSiteUrl(setLogo(src, logoDataUri), SITE_URL);
fs.writeFileSync(DIR + "sthree-boutique-share.html", share, "utf8");

const kb = n => Math.round(n / 1024) + " KB";
console.log("logo   " + logoName + " (" + kb(logoBytes.length) + ")");
console.log("index.html                    " + kb(pages.length) + "   links " + logoName);
console.log("sthree-boutique-hosted.html   " + kb(artifact.length) + "   logo inlined");
console.log("sthree-boutique-share.html    " + kb(share.length) + "   logo inlined");
if (!SITE_URL) {
  console.log("");
  console.log("NOTE  SITE_URL is empty, so link previews will not work yet.");
  console.log("      Set it at the top of this file to the live address, then rerun.");
}
