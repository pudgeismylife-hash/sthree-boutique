"""Read the client's Drive folder and keep a record of what has been seen.

    python3 import-manifest.py                 report what is in INPUT
    python3 import-manifest.py --write         write/refresh import-manifest.json
    python3 import-manifest.py --reprocess=ID  mark one file to be done again

This is step one of the catalogue importer, and it deliberately does nothing but
look. No image is opened, nothing is moved, nothing in Drive is written. The
client's originals are the one thing this pipeline must not lose, so the only
verb it knows for INPUT is "read".

WHY A MANIFEST

The same folder gets read many times -- once to see what arrived, again after a
photograph is replaced, again next month. Without a record, every run would
reprocess everything, which wastes work and, worse, would quietly overwrite a
cut-out that had already been corrected by hand.

So each file is recorded by its Drive id, which is stable across renames, along
with its size and modified time. A file whose id is already recorded and whose
size and time are unchanged is `seen`; the pipeline skips it unless it is asked
not to. A file whose id is known but whose size or time has moved is `changed`
-- the client sent a new version -- and that one is processed again.

The manifest is committed. It is the difference between "this photograph has
never been dealt with" and "this photograph was dealt with and somebody has
since replaced it", and neither Drive nor the filesystem records that for us.

WHAT IT CANNOT DO YET

Reading the file list needs the Drive tools, which are not available to a bare
python process. This script therefore takes the listing as JSON on stdin or in
--from=<file>, and the session that has Drive access supplies it. That keeps the
credential where it belongs -- outside this repository -- and keeps this script
testable without a network.
"""
import hashlib
import json
import os
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "import-config.json")
MANIFEST = os.path.join(HERE, "import-manifest.json")

# What the pipeline can actually open. A client sends what a phone produces.
IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp", "image/heic", "image/heif"}
# Product information may arrive as a file rather than a pasted message.
TEXT_TYPES = {
    "text/plain", "text/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/vnd.google-apps.document",
    "application/vnd.google-apps.spreadsheet",
}


def load(path, default):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def fingerprint(entry):
    """What "the same file, unchanged" means.

    Drive gives no checksum for every type, and the id survives a rename, so
    the id says which file this is and the size and modified time say whether
    it is still the file we looked at."""
    raw = "%s|%s|%s" % (entry.get("id", ""), entry.get("fileSize", ""),
                        entry.get("modifiedTime", ""))
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]


def classify(entry):
    mime = (entry.get("mimeType") or "").lower()
    if mime in IMAGE_TYPES or mime.startswith("image/"):
        return "image"
    if mime in TEXT_TYPES:
        return "text"
    if mime == "application/vnd.google-apps.folder":
        return "folder"
    return "other"


def read_listing():
    """The Drive listing, as JSON, from --from=<file> or stdin.

    Accepts either the raw tool response ({"files": [...]}) or a bare list, so
    whatever the session pastes in works without reshaping it by hand."""
    src = None
    for a in sys.argv[1:]:
        if a.startswith("--from="):
            src = a.split("=", 1)[1]
    hint = ("Pass --from=<file.json>, or pipe the Drive listing in on stdin:\n"
            "    python3 import-manifest.py --from=listing.json --write")
    try:
        if src:
            with open(src, encoding="utf-8") as f:
                data = json.load(f)
        elif not sys.stdin.isatty():
            text = sys.stdin.read().strip()
            if not text:
                sys.exit("No listing given -- stdin was empty.\n" + hint)
            data = json.loads(text)
        else:
            sys.exit("No listing given.\n" + hint)
    except FileNotFoundError:
        sys.exit("No such file: %s\n%s" % (src, hint))
    except json.JSONDecodeError as e:
        sys.exit("That listing is not valid JSON (%s).\n%s" % (e.msg, hint))
    if isinstance(data, dict):
        data = data.get("files", [])
    if not isinstance(data, list):
        sys.exit("The listing should be a list of files, or {\"files\": [...]}.")
    return data


def main():
    write = "--write" in sys.argv
    reprocess = {a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--reprocess=")}

    cfg = load(CONFIG, None)
    if not cfg:
        sys.exit("FAIL  import-config.json is missing.")
    manifest = load(MANIFEST, {"files": {}, "runs": []})
    known = manifest.get("files", {})

    listing = read_listing()
    rows, counts = [], {"new": 0, "changed": 0, "seen": 0, "skipped": 0}

    for entry in listing:
        kind = classify(entry)
        fid = entry.get("id")
        title = entry.get("title") or entry.get("name") or "(untitled)"
        if kind in ("folder", "other"):
            counts["skipped"] += 1
            rows.append((title, kind, "skipped", "not an image or a product list"))
            continue

        fp = fingerprint(entry)
        prev = known.get(fid)
        if fid in reprocess:
            state, why = "changed", "asked for again"
        elif prev is None:
            state, why = "new", "not seen before"
        elif prev.get("fingerprint") != fp:
            state, why = "changed", "replaced since it was last read"
        else:
            state, why = "seen", "already dealt with"
        counts[state] += 1
        rows.append((title, kind, state, why))

        known[fid] = {
            "title": title,
            "kind": kind,
            "mimeType": entry.get("mimeType"),
            "fileSize": entry.get("fileSize"),
            "modifiedTime": entry.get("modifiedTime"),
            "fingerprint": fp,
            "state": state,
            "firstSeen": (prev or {}).get("firstSeen") or
                         datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }

    width = max([len(r[0]) for r in rows] + [12])
    print("%-*s  %-6s  %-8s  %s" % (width, "FILE", "KIND", "STATE", "WHY"))
    for title, kind, state, why in sorted(rows, key=lambda r: (r[2] != "new", r[0])):
        print("%-*s  %-6s  %-8s  %s" % (width, title, kind, state, why))

    todo = counts["new"] + counts["changed"]
    print("\n%d file(s) in INPUT: %d new, %d changed, %d already dealt with, %d not usable"
          % (len(listing), counts["new"], counts["changed"], counts["seen"], counts["skipped"]))
    print("%d to process." % todo if todo else "Nothing to process.")

    if not write:
        print("\nreport only -- import-manifest.json not written. add --write.")
        return

    manifest["files"] = known
    manifest.setdefault("runs", []).append({
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "listed": len(listing),
        **counts,
    })
    manifest["runs"] = manifest["runs"][-20:]          # a short history, not a log file
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("\nimport-manifest.json written: %d file(s) recorded." % len(known))


if __name__ == "__main__":
    main()
