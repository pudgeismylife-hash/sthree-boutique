/* Builds the Artifact-hosted copy from the standalone file.
   The host wraps content in its own <!doctype>/<head>/<body>, so the
   document wrapper tags are stripped. Everything else is untouched, so
   sthree-boutique.html stays the single source of truth. */
const fs = require("fs");

const DIR = "C:/Maya test/";
const SRC = DIR + "sthree-boutique.html";
const OUT = DIR + "sthree-boutique-hosted.html";
const SHARE = DIR + "sthree-boutique-share.html";

let s = fs.readFileSync(SRC, "utf8");
const before = s.length;

/* The published page must be self-contained — it cannot fetch logo.png
   from anywhere. So the artwork is inlined as a data URI. Drop any of
   these filenames next to this script and it is picked up automatically. */
const MIME = { ".png":"image/png", ".jpg":"image/jpeg", ".jpeg":"image/jpeg", ".webp":"image/webp", ".svg":"image/svg+xml" };
const found = ["logo.png","logo.jpg","logo.jpeg","logo.webp","logo.svg"]
  .map(f => DIR + f).find(p => fs.existsSync(p));

let logoNote = "no logo file found — using the drawn mark";
if (found) {
  const ext = found.slice(found.lastIndexOf("."));
  const bytes = fs.readFileSync(found);
  const uri = "data:" + MIME[ext] + ";base64," + bytes.toString("base64");
  const patched = s.replace(/logo     : ""/, 'logo     : "' + uri + '"');
  if (patched === s) { console.error("FAIL could not find the logo setting to patch"); process.exit(1); }
  s = patched;
  logoNote = found.split("/").pop() + " embedded (" + Math.round(bytes.length / 1024) + " KB)";
  // A standalone copy carrying the logo, for sending as a file.
  fs.writeFileSync(SHARE, s, "utf8");
}
s = s
  .replace(/<!doctype html>\s*/i, "")
  .replace(/<html[^>]*>\s*/i, "")
  .replace(/<\/html>\s*/i, "")
  .replace(/<head>\s*/i, "")
  .replace(/<\/head>\s*/i, "")
  .replace(/<body>\s*/i, "")
  .replace(/<\/body>\s*/i, "")
  .trim();

// Guard: no wrapper tag may survive. Matched as whole tags so that
// <header>/</header> are not mistaken for <head>/</head>.
const leftovers = [
  [/<!doctype/i, "<!doctype"],
  [/<html[\s>]/i, "<html>"], [/<\/html\s*>/i, "</html>"],
  [/<head[\s>]/i, "<head>"], [/<\/head\s*>/i, "</head>"],
  [/<body[\s>]/i, "<body>"], [/<\/body\s*>/i, "</body>"]
].filter(([re]) => re.test(s)).map(([, name]) => name);
if (leftovers.length) {
  console.error("FAIL leftover wrapper tags:", leftovers.join(" "));
  process.exit(1);
}

// Guard: the parts that matter must still be present.
const required = ["<title>", "<style>", "<script>", "id=\"prodGrid\"", "917625077531", "demo-strip"];
const missing = required.filter(t => !s.includes(t));
if (missing.length) {
  console.error("FAIL missing content:", missing.join(" "));
  process.exit(1);
}

fs.writeFileSync(OUT, s, "utf8");
console.log("ok   " + logoNote);
console.log("     " + before + "b -> " + s.length + "b");
console.log("     " + OUT);
if (found) console.log("     " + SHARE + "  (standalone, logo included)");
