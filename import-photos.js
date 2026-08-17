/* Import product photographs, safely and incrementally.
 *
 *   node import-photos.js <folder>                 validate and report only
 *   node import-photos.js <folder> --apply         import what passes
 *   node import-photos.js <folder> --apply --unlock SB-JWL-03[,SB-JWL-05]
 *
 * Rules, in order of authority:
 *
 *   PRODUCT CODE = PERMANENT IMAGE IDENTITY
 *     SB-JWL-01 owns SB-JWL-01-1/2/3.jpg and nothing else. Assignment is
 *     never inferred from array position, product number, filename order,
 *     alphabetical order or catalogue order.
 *
 *   LOCKED = DO NOT CHANGE
 *     product-image-lock.json is the source of truth. A locked entry is not
 *     remapped, reordered or overwritten unless named in --unlock.
 *
 *   CONFLICT = STOP THAT PRODUCT, DO NOT GUESS
 *     A single product failing validation is skipped and reported; the rest
 *     of the batch continues.
 *
 * photo-map.json translates an outside batch's codes onto catalogue product
 * keys, for batches that number things their own way.
 */
const fs = require("fs");
const path = require("path");
const { execFileSync } = require("child_process");

/* The project folder is wherever this script lives — see build-hosted.js. */
const DIR        = __dirname.replace(/\\/g, "/").replace(/\/?$/, "/");
const SRC_HTML   = DIR + "sthree-boutique.html";
const LOCK_FILE  = DIR + "product-image-lock.json";
const MAP_FILE   = DIR + "photo-map.json";
const OUT_FULL   = DIR + "assets/products/";
const OUT_THUMB  = DIR + "assets/products/thumb/";
const P          = "assets/products/";

const folder = process.argv[2];
const apply  = process.argv.includes("--apply");
const unlockArg = (process.argv[process.argv.indexOf("--unlock") + 1] || "");
const UNLOCK = process.argv.includes("--unlock")
  ? new Set(unlockArg.split(",").map(s => s.trim().toUpperCase()).filter(Boolean))
  : new Set();

if (!folder) {
  console.error("usage: node import-photos.js <folder> [--apply] [--unlock CODE[,CODE]]");
  process.exit(1);
}
if (!fs.existsSync(folder)) { console.error("FAIL folder not found: " + folder); process.exit(1); }

/* ── catalogue ─────────────────────────────────────────────────────────── */
const html = fs.readFileSync(SRC_HTML, "utf8");
const m = html.match(/const arrivals = \[([\s\S]*?)\n\];/);
if (!m) { console.error("FAIL could not read the catalogue"); process.exit(1); }
const items = eval("[" + m[1] + "]");
const CAT = { ethnic:"ETH", western:"WES", coord:"COR", jewellery:"JWL", nails:"NLS", bags:"BAG" };
const seq = {}, byKey = new Map();
for (const p of items) {
  seq[p.cat] = (seq[p.cat] || 0) + 1;
  p.siteCode = "SB-" + (CAT[p.cat] || "GEN") + "-" + String(seq[p.cat]).padStart(2, "0");
  byKey.set(p.key, p);
}

const lock = fs.existsSync(LOCK_FILE)
  ? JSON.parse(fs.readFileSync(LOCK_FILE, "utf8"))
  : { _comment: "product image lock", products: {} };
const MAP = fs.existsSync(MAP_FILE) ? JSON.parse(fs.readFileSync(MAP_FILE, "utf8")) : null;

/* ── group incoming files by their product code ────────────────────────── */
const files = fs.readdirSync(folder).filter(f => /\.(jpe?g|png|webp)$/i.test(f));
const batch = new Map(), rejected = [];
for (const f of files) {
  const hit = f.match(/^(SB-[A-Z]{3}-\d{2})-([123])\.(jpe?g|png|webp)$/i);
  if (!hit) { rejected.push([f, "filename is not <CODE>-<1|2|3>.jpg"]); continue; }
  const code = hit[1].toUpperCase();
  if (!batch.has(code)) batch.set(code, {});
  batch.get(code)[+hit[2]] = f;
}

/* ── validate every product independently ──────────────────────────────── */
const PASS = [], SKIP = [];
const claimed = new Map();   // productKey -> code, to catch two codes on one product

for (const [code, shots] of [...batch].sort()) {
  const fail = r => SKIP.push({ code, why: r });

  const entry = lock.products[code];

  // 2. already locked?
  if (entry && entry.status === "LOCKED" && !UNLOCK.has(code)) {
    SKIP.push({ code, why: "LOCKED — unchanged (use --unlock " + code + " to replace)", locked: true });
    continue;
  }
  if (entry && entry.status === "SKIPPED") { fail("marked SKIPPED in the lock: " + (entry.reason || "review required")); continue; }

  /* 3 & 4. the views present must be named for this code and run 1,2,3 with no
     gap. One or two is allowed: a photograph sometimes holds only one honest
     view of a piece, and padding it out with an invented angle or a crop
     enlarged past legibility would be worse than showing fewer. */
  const have = [1,2,3].filter(n => shots[n]);
  if (!have.length)                      { fail("no image 1 for this code"); continue; }
  if (have[have.length-1] !== have.length) { fail("views must be numbered 1" +
    (have.length>1 ? "-"+have.length : "") + " with no gap; got " + have.join(",")); continue; }

  // 1. does the code resolve to a catalogue product?
  let key = null, via = "code";
  if (MAP && MAP[code]) {
    if (!MAP[code].key) { fail("photo-map says: " + (MAP[code].note || "no product")); continue; }
    key = MAP[code].key; via = "photo-map.json";
  } else {
    const direct = items.find(p => p.siteCode === code);
    if (direct) key = direct.key;
  }
  if (!key)            { fail("no catalogue product for " + code + " and no entry in photo-map.json"); continue; }
  const product = byKey.get(key);
  if (!product)        { fail("mapping points at unknown product key '" + key + "'"); continue; }

  // 5. does an existing unlocked entry disagree about the product?
  if (entry && entry.productKey && entry.productKey !== key) {
    console.log("\nIMAGE MAPPING CONFLICT\n\nProduct:\n  " + code +
      "\n\nExisting locked mapping:\n  " + entry.productKey + " (" + entry.siteCode + ")" +
      "\n\nIncoming mapping:\n  " + key + " (" + product.siteCode + ")" +
      "\n\nAction:\n  SKIPPED — MANUAL REVIEW REQUIRED\n");
    fail("mapping conflict with the lock file"); continue;
  }

  // 6 & 7. is this product already claimed, by the lock or by this batch?
  const otherInBatch = claimed.get(key);
  if (otherInBatch)    { fail("product " + key + " is already taken by " + otherInBatch + " in this batch"); continue; }
  const otherLocked = Object.entries(lock.products)
    .find(([c, v]) => c !== code && v.status === "LOCKED" && v.productKey === key);
  if (otherLocked)     { fail("product " + key + " is already LOCKED to " + otherLocked[0]); continue; }

  claimed.set(key, code);
  PASS.push({ code, key, product, shots, via, views: have, replacing: UNLOCK.has(code) });
}

/* ── report ────────────────────────────────────────────────────────────── */
const locked = Object.values(lock.products).filter(v => v.status === "LOCKED").length;
console.log("catalogue   : " + items.length + " products");
console.log("lock file   : " + locked + " LOCKED, " +
  Object.values(lock.products).filter(v => v.status === "SKIPPED").length + " SKIPPED");
console.log("batch       : " + files.length + " files, " + batch.size + " product codes");
if (UNLOCK.size) console.log("unlocking   : " + [...UNLOCK].join(", "));

if (PASS.length) {
  console.log("\nWILL IMPORT (" + PASS.length + ")");
  for (const r of PASS) console.log("  " + r.code + " -> " + r.product.siteCode.padEnd(11) +
    (r.replacing ? "REPLACE  " : "new      ") + r.product.name);
}
if (SKIP.length) {
  console.log("\nSKIPPED (" + SKIP.length + ")");
  for (const r of SKIP) console.log("  " + r.code + "  " + r.why);
}
if (rejected.length) {
  console.log("\nREJECTED FILENAMES (" + rejected.length + ")");
  for (const [f, why] of rejected.slice(0, 15)) console.log("  " + f.padEnd(26) + why);
}

if (!apply) { console.log("\nvalidation only — nothing written. add --apply to import."); process.exit(0); }
if (!PASS.length) { console.log("\nnothing to import."); process.exit(0); }

/* ── install ───────────────────────────────────────────────────────────── */
fs.mkdirSync(OUT_FULL, { recursive: true });
fs.mkdirSync(OUT_THUMB, { recursive: true });
/* The full-size file keeps its cream margin, so the zoom viewer always gets the
   same canvas. The thumbnail must not: a card showing that margin puts the
   piece in the middle of a mostly empty frame, which is how the grid ended up
   with the photograph filling under half of it. So the thumbnail is cut from
   the picture itself and fills the card — cropped when it is a single subject,
   scaled to the width when it is a wide composite, because cropping one of
   those to a portrait frame cuts straight through the middle of it. */
const py = [
  "from PIL import Image", "import sys",
  "src, full, thumb = sys.argv[1], sys.argv[2], sys.argv[3]",
  "CREAM=(250,246,240)",
  "im = Image.open(src).convert('RGB')",
  "im.thumbnail((720, 900), Image.LANCZOS)",
  /* The full-size file is the photograph, not the photograph on a cream mat.
     It used to be letterboxed onto 720x900, which meant the zoom viewer fitted
     a mostly-empty canvas into the stage and showed the piece small in the
     middle of it — the photograph was only 48% of its own file. */
  "im.save(full, quality=88, optimize=True, progressive=True)",
  "tw, th = 360, 450",
  "t = Image.new('RGB',(tw,th),CREAM)",
  "if im.width/im.height <= 1.30:",
  "    s = max(tw/im.width, th/im.height)",
  "    r = im.resize((max(1,round(im.width*s)), max(1,round(im.height*s))), Image.LANCZOS)",
  "    t.paste(r, (-(r.width-tw)//2, -(r.height-th)//2))",
  "else:",
  "    r = im.resize((tw, max(1,round(im.height*tw/im.width))), Image.LANCZOS)",
  "    t.paste(r, (0, (th-r.height)//2))",
  "t.save(thumb, quality=82, optimize=True, progressive=True)"
].join("\n");
const script = path.join(require("os").tmpdir(), "sthree-resize.py");
fs.writeFileSync(script, py, "utf8");

/* "python" on Windows, "python3" almost everywhere else. Pick whichever is
   actually there and can load Pillow, rather than failing halfway through a
   batch with a bare ENOENT. */
const PYTHON = ["python3", "python"].find(bin => {
  try { execFileSync(bin, ["-c", "import PIL"], { stdio: "pipe" }); return true; }
  catch (_) { return false; }
});
if (!PYTHON) {
  console.error("FAIL  need python with Pillow installed  (pip install pillow)");
  process.exit(1);
}

let out = html, written = 0;
for (const r of PASS) {
  const list = [];
  for (const n of r.views) {
    const name = r.key + "-a" + n + ".jpg";
    execFileSync(PYTHON, [script, path.join(folder, r.shots[n]), OUT_FULL + name, OUT_THUMB + name], { stdio: "pipe" });
    list.push(name); written++;
  }
  const arr = "images:[" + list.map(s => 'P+"' + s + '"').join(",") + "]";
  const re = new RegExp('(key:"' + r.key.replace(/[-_]/g, "[-_]") + '",\\s*)images:\\[[^\\]]*\\]');
  if (!re.test(out)) { console.log("  WARN could not wire " + r.code); continue; }
  out = out.replace(re, "$1" + arr);

  lock.products[r.code] = {
    productKey: r.key, siteCode: r.product.siteCode, productName: r.product.name,
    status: "LOCKED", lockedOn: new Date().toISOString().slice(0, 10),
    source: folder, sourceFiles: r.views.map(n => r.shots[n]), images: list
  };
}
fs.writeFileSync(SRC_HTML, out, "utf8");
lock.products = Object.fromEntries(Object.entries(lock.products).sort());
fs.writeFileSync(LOCK_FILE, JSON.stringify(lock, null, 2) + "\n", "utf8");

console.log("\nwrote " + written + " images, locked " + PASS.length + " products");
console.log("now run:  node build-hosted.js");
