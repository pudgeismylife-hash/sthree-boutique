/* Import product photographs into the catalogue.
 *
 *   node import-photos.js <folder>            report what is there
 *   node import-photos.js <folder> --apply    resize, install, and wire up
 *
 * Expects files named  <CODE>-<n>.jpg  e.g.  SB-JWL-01-1.jpg
 *   -1  full view      shown on the card and as the opening photo
 *   -2  worn / draped
 *   -3  detail
 *
 * Codes are matched against the codes the site already assigns
 * (SB-ETH-01, SB-WES-01, SB-COR-01, SB-JWL-01 …), so a photo can only ever
 * land on the piece whose code it carries. Nothing is guessed.
 *
 * Photos are written at two sizes, matching the rest of the catalogue:
 *   assets/products/<key>-<n>.jpg        720x900, used by the zoomable viewer
 *   assets/products/thumb/<key>-<n>.jpg  360 wide, used by cards and the strip
 */
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

const DIR = "C:/Maya test/";
const SRC_HTML = DIR + "sthree-boutique.html";
const OUT_FULL = DIR + "assets/products/";
const OUT_THUMB = DIR + "assets/products/thumb/";

const folder = process.argv[2];
const apply = process.argv.includes("--apply");

if (!folder) {
  console.error("usage: node import-photos.js <folder> [--apply]");
  process.exit(1);
}
if (!fs.existsSync(folder)) {
  console.error("FAIL folder not found: " + folder);
  process.exit(1);
}

/* ── the catalogue's own codes, derived the same way the page derives them ── */
const html = fs.readFileSync(SRC_HTML, "utf8");
const m = html.match(/const arrivals = \[([\s\S]*?)\n\];/);
if (!m) { console.error("FAIL could not read the catalogue"); process.exit(1); }
const P = "assets/products/";
const items = eval("[" + m[1] + "]");
const CAT = { ethnic:"ETH", western:"WES", coord:"COR", jewellery:"JWL" };
const seq = {};
const byCode = new Map();
for (const p of items) {
  seq[p.cat] = (seq[p.cat] || 0) + 1;
  const code = "SB-" + (CAT[p.cat] || "GEN") + "-" + String(seq[p.cat]).padStart(2, "0");
  p.code = code;
  p.key = p.img.replace(/^.*\//, "").replace(/\.jpg$/, "");
  byCode.set(code, p);
}

/* ── what is in the folder ────────────────────────────────────────────── */
const files = fs.readdirSync(folder).filter(f => /\.(jpe?g|png|webp)$/i.test(f));
/* An outside batch may number things its own way. photo-map.json translates
   its codes onto catalogue products, matched on product name. Without a map,
   codes are taken to mean the catalogue's own codes. */
let MAP = null;
const mapPath = DIR + "photo-map.json";
if (fs.existsSync(mapPath)) {
  MAP = JSON.parse(fs.readFileSync(mapPath, "utf8"));
  console.log("using photo-map.json to translate incoming codes\n");
}
const byKey = new Map([...byCode.values()].map(p => [p.key, p]));

const parsed = [], skipped = [];
for (const f of files) {
  const hit = f.match(/^(SB-[A-Z]{3}-\d{2})-([123])\.(jpe?g|png|webp)$/i);
  if (!hit) { skipped.push([f, "name does not match <CODE>-<1|2|3>.jpg"]); continue; }
  const code = hit[1].toUpperCase(), n = +hit[2];

  let product = null;
  if (MAP && MAP[code]) {
    if (!MAP[code].key) { skipped.push([f, "mapped to nothing: " + (MAP[code].note || "no product")]); continue; }
    product = byKey.get(MAP[code].key);
    if (!product) { skipped.push([f, "map points at unknown key " + MAP[code].key]); continue; }
  } else {
    product = byCode.get(code);
    if (!product) { skipped.push([f, "no product with code " + code]); continue; }
  }
  parsed.push({ file: f, code, n, product });
}

const groups = new Map();          // keyed by the catalogue product, not the incoming code
for (const r of parsed) {
  const k = r.product.key;
  if (!groups.has(k)) groups.set(k, []);
  groups.get(k).push(r);
}

console.log("catalogue codes : " + byCode.size);
console.log("image files     : " + files.length);
console.log("usable          : " + parsed.length + " across " + groups.size + " products");
if (skipped.length) {
  console.log("\nnot imported:");
  for (const [f, why] of skipped.slice(0, 20)) console.log("  " + f.padEnd(22) + why);
  if (skipped.length > 20) console.log("  … and " + (skipped.length - 20) + " more");
}
console.log("\nper product:");
for (const [, rows] of [...groups].sort()) {
  const have = rows.map(r => r.n).sort().join(",");
  const p = rows[0].product;
  console.log("  " + rows[0].code + " -> " + p.code.padEnd(11)
    + (have === "1,2,3" ? "1,2,3" : have + " (partial)").padEnd(13) + p.name);
}
const missing = [...byCode.values()].filter(p => !groups.has(p.key)).map(p => p.code);
if (missing.length) console.log("\nno photos yet   : " + missing.length + " products (" + missing.slice(0,6).join(", ") + (missing.length>6?" …":"") + ")");

if (!apply) {
  console.log("\nnothing written. re-run with --apply to install these.");
  process.exit(0);
}

/* ── install ──────────────────────────────────────────────────────────── */
fs.mkdirSync(OUT_FULL, { recursive: true });
fs.mkdirSync(OUT_THUMB, { recursive: true });

const py = [
  "from PIL import Image",
  "import sys",
  "src, full, thumb = sys.argv[1], sys.argv[2], sys.argv[3]",
  "CREAM=(250,246,240)",
  "im = Image.open(src).convert('RGB')",
  "im.thumbnail((720-64, 900-64), Image.LANCZOS)",
  "c = Image.new('RGB',(720,900),CREAM)",
  "c.paste(im, ((720-im.width)//2, (900-im.height)//2))",
  "c.save(full, quality=86, optimize=True, progressive=True)",
  "t = c.resize((360,450), Image.LANCZOS)",
  "t.save(thumb, quality=82, optimize=True, progressive=True)"
].join("\n");
const script = path.join(require("os").tmpdir(), "sthree-resize.py");
fs.writeFileSync(script, py, "utf8");

let written = 0;
const wired = new Map();
for (const [key, rows] of groups) {
  const p = rows[0].product;
  const list = [p.img];                       // her own photograph stays first
  for (const r of rows.sort((a, b) => a.n - b.n)) {
    const outName = p.key + "-a" + r.n + ".jpg";
    execFileSync("python", [script, path.join(folder, r.file), OUT_FULL + outName, OUT_THUMB + outName], { stdio: "pipe" });
    list.push(P + outName);
    written++;
  }
  wired.set(key, list);
}
console.log("\nwrote " + written + " photos at two sizes each");

/* ── wire the image lists into the catalogue ──────────────────────────── */
let out = html, patched = 0;
for (const [key, list] of wired) {
  const p = byKey.get(key);
  const needle = new RegExp('(\\{ cat:"' + p.cat + '"[^\\n]*?img:P\\+"' + p.key.replace(/[-_]/g, "[-_]") + '\\.jpg")');
  if (!needle.test(out)) { console.log("  WARN could not wire " + p.code); continue; }
  const arr = ", images:[" + list.map(s => 'P+"' + s.replace(P, "") + '"').join(",") + "]";
  out = out.replace(needle, "$1" + arr);
  patched++;
}
if (patched) {
  fs.writeFileSync(SRC_HTML, out, "utf8");
  console.log("wired " + patched + " products with an images list");
  console.log("\nnow run:  node build-hosted.js");
}
