# Brief: finish moving Sthree Boutique to sthreeboutique.com

Paste this whole file into a fresh agent session as the opening message.
It is written to stand alone — it assumes no memory of earlier work.

---

## The project

A boutique catalogue site for Sthree Boutique, Bikarnakatte, Mangalore.

- **Repository:** `pudgeismylife-hash/sthree-boutique`, branch `main`
- **Hosting:** GitHub Pages, branch deploy from `main`. **Pushing to `main` is deploying.**
- **Currently live at:** `https://pudgeismylife-hash.github.io/sthree-boutique/`
- **Moving to:** `https://sthreeboutique.com` (already bought, at GoDaddy)
- 58 products live. Static site, no backend, no database.

### How it is built

`sthree-boutique.html` is the **only** file edited by hand. The products are a
JavaScript array literal (`const arrivals = [...]`) inside it. Everything else
is generated:

```sh
node build-hosted.js        # -> index.html, collection.html,
                            #    sthree-boutique-hosted.html, -share.html,
                            #    c/*.html (6 category stubs),
                            #    p/*.html (58 product stubs), sw.js,
                            #    photo-shot-list.html, owner-questions.html
python3 build-og-images.py --apply   # link-preview images + card thumbnails
python3 build-tiles.py --apply       # the "Shop by category" tiles
python3 build-hero.py --apply        # the two front-page hero pictures
```

Only `build-hosted.js` is needed for this task. Do not run the others; they
rewrite images and are unrelated.

---

## Where things stand right now

| Step | Who | Status |
|---|---|---|
| 1. Buy `sthreeboutique.com` | owner | ✅ done, at GoDaddy |
| 2. Point GoDaddy DNS at GitHub | owner, by hand | ⏳ in progress |
| 3. Set the custom domain in GitHub Settings → Pages | owner, by hand | ⬜ not started |
| 4. Tick "Enforce HTTPS" | owner, by hand | ⬜ not started |
| 5. **Change the site's own address** | **you, the agent** | ⬜ **this is your job** |
| 6. Verify | you + owner | ⬜ |

Steps 2–4 are clicks in GoDaddy and GitHub's web UI. You cannot do them and
should not try. Ask the owner to confirm each is done.

---

## Step 5 — your actual task

Every absolute URL the site emits — the canonical tag, `og:url`, the link
preview for all 58 product share stubs and 6 category stubs, and the link at
the foot of every WhatsApp order message — comes from **one constant**:

**`build-hosted.js`, line 26:**

```js
const SITE_URL = "https://pudgeismylife-hash.github.io/sthree-boutique";
```

Change it to:

```js
const SITE_URL = "https://sthreeboutique.com";
```

Then:

```sh
node build-hosted.js

# must print nothing at all:
grep -rl "github\.io" index.html collection.html sthree-boutique-hosted.html \
        sthree-boutique-share.html p/ c/

git add -A
git commit -m "Move the site to sthreeboutique.com"
git push origin main
```

That one line rewrites all 68 built files. This was tested on 5 September 2026
by making the change, rebuilding, confirming no trace of the old address
survived anywhere, and reverting. **Nothing else in the code needs touching** —
every asset path, the manifest `scope` and `start_url`, and the service worker
shell are all already relative, so moving from a repository subpath to a domain
root breaks nothing.

### Do not run Step 5 early

Run it **only after** the owner confirms `sthreeboutique.com` actually
resolves and loads. Doing it first leaves 58 share previews pointing at an
address that does not answer yet.

---

## Rules that are not negotiable

1. **Never set the custom domain in GitHub before DNS resolves.** The moment a
   custom domain is set, GitHub stops serving the github.io address and
   redirects it to the new one. If the new one is not answering, the shop is
   offline. Confirm DNS first.
2. **Never delete the `CNAME` file.** Once the owner saves the domain in
   Settings → Pages, GitHub commits a file called `CNAME` to `main` containing
   `sthreeboutique.com`. Pull it before your next push
   (`git fetch origin main && git merge --ff-only origin/main`). If it is ever
   removed from `main`, the custom domain switches off.
3. **Never invent product data.** Prices, names, sizes and materials come from
   the owner only. Nine pieces currently read "Price on WhatsApp" — that is
   correct and deliberate, not a bug to fill in.
4. **Never replace a real photograph with a generated image.** Every picture on
   the site is the boutique's own. Keep it that way.
5. **Verify on the built output, not the source.** `sthree-boutique.html` is
   the input; what ships is `index.html` and the rest. Check those.

---

## The DNS records, for reference

If the owner asks what to enter at GoDaddy (Domain → DNS → DNS Records):

| Type | Name | Value | TTL |
|---|---|---|---|
| A | `@` | `185.199.108.153` | 600 |
| A | `@` | `185.199.109.153` | 600 |
| A | `@` | `185.199.110.153` | 600 |
| A | `@` | `185.199.111.153` | 600 |
| CNAME | `www` | `pudgeismylife-hash.github.io` | 1 hour |

- Four A records deliberately share the name `@`. That is not a duplicate.
- The CNAME value ends at `.github.io` — **no path after it.** A path in a
  CNAME is invalid and is the most common failure here.
- GoDaddy ships the zone parked. The existing `A @ WebsiteBuilder Site` record
  should be **edited** (GoDaddy may refuse to delete it), and the pre-filled
  `CNAME www → @` must be changed.
- Check the **Forwarding** tab and remove anything there — forwarding silently
  overrides every record above it.
- Leave `NS`, `SOA` and `_domainconnect` alone.
- Verify at <https://www.whatsmydns.net> — look up `sthreeboutique.com`, type
  **A**, and wait for the `185.199.*` addresses to appear worldwide.

---

## How to check it worked

After Step 5 is pushed and the GitHub Pages deploy is green:

- `https://sthreeboutique.com` loads, with a padlock
- `https://www.sthreeboutique.com` loads
- `https://pudgeismylife-hash.github.io/sthree-boutique/` **redirects** to the
  new address — GitHub does this automatically, so links already sent keep
  working
- Open a piece → **Add to bag** → **WhatsApp order**. The link at the bottom of
  the message now reads `sthreeboutique.com`
- Paste `https://sthreeboutique.com` into a WhatsApp chat — the preview shows
  the logo and description

---

## Not in scope, but you will see them

- **Nine pieces show "Price on WhatsApp"** — four ruched gowns, the indigo
  tunic set, four nail sets. Waiting on the owner. Do not guess prices.
- **Three "Michael Kors" satchels at ₹3,500** carry a brand name with no
  provenance. The owner authorised publishing them and the risk is documented
  in `HANDOVER.md`. Do not silently change or remove them.
- **The hero pictures are composites** built by `build-hero.py` from the shop's
  own cut-out photographs, standing in until a real photograph is shot.
  `assets/hero/README.txt` explains how to replace them.

Read `GOING-LIVE.md` for the full runbook and `HANDOVER.md` for project history.
