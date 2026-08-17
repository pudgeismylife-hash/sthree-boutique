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
const parsed = [], skipped = [];
for (const f of files) {
  const hit = f.match(/^(SB-[A-Z]{3}-\d{2})-([123])\.(jpe?g|png|webp)$/i);
  if (!hit) { skipped.push([f, "name does not match <CODE>-<1|2|3>.jpg"]); continue; }
  const code = hit[1].toUpperCase(), n = +hit[2];
  if (!byCode.has(code)) { skipped.push([f, "no product with code " + code]); continue; }
  parsed.push({ file: f, code, n });
}

const groups = new Map();
for (const r of parsed) {
  if (!groups.has(r.code)) groups.set(r.code, []);
  groups.get(r.code).push(r);
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
for (const [code, rows] of [...groups].sort()) {
  const have = rows.map(r => r.n).sort().join(",");
  const p = byCode.get(code);
  console.log("  " + code + "  " + (have === "1,2,3" ? "1,2,3 complete" : have + " incomplete").padEnd(18) + p.name);
}
const missing = [...byCode.keys()].filter(c => !groups.has(c));
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
for (const [code, rows] of groups) {
  const p = byCode.get(code);
  const list = [];
  for (const r of rows.sort((a, b) => a.n - b.n)) {
    const outName = p.key + "-" + r.n + ".jpg";
    execFileSync("python", [script, path.join(folder, r.file), OUT_FULL + outName, OUT_THUMB + outName], { stdio: "pipe" });
    list.push(P + outName);
    written++;
  }
  wired.set(code, list);
}
console.log("\nwrote " + written + " photos at two sizes each");

/* ── wire the image lists into the catalogue ──────────────────────────── */
let out = html, patched = 0;
for (const [code, list] of wired) {
  const p = byCode.get(code);
  const needle = new RegExp('(\\{ cat:"' + p.cat + '"[^\\n]*?img:P\\+"' + p.key.replace(/[-_]/g, "[-_]") + '\\.jpg")');
  if (!needle.test(out)) { console.log("  WARN could not wire " + code); continue; }
  const arr = ", images:[" + list.map(s => 'P+"' + s.replace(P, "") + '"').join(",") + "]";
  out = out.replace(needle, "$1" + arr);
  patched++;
}
if (patched) {
  fs.writeFileSync(SRC_HTML, out, "utf8");
  console.log("wired " + patched + " products with an images list");
  console.log("\nnow run:  node build-hosted.js");
}
