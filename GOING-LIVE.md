# Putting the site on its own domain

The site is **already live** at
`https://pudgeismylife-hash.github.io/sthree-boutique/`. Nothing here makes it
work — it works now. This is about giving it an address that looks like a shop
instead of a code repository.

Total time: about **40 minutes of actual work**, spread over **1–2 days**
because DNS takes hours to spread around the world. Cost: roughly
**₹900–1,500 a year**.

Do the steps in this order. The domain must work *before* the site is told to
call itself by that name, or link previews point at an address that does not
answer yet.

---

## Step 1 — Buy the domain (15 minutes)

**Pick the name first.** Check availability at the registrar; I could not check
it from here.

| Option | Notes |
|---|---|
| `sthreeboutique.com` | The one to want. Recognised everywhere. |
| `sthreeboutique.in` | Cheaper, and reads as an Indian business. Good second choice. |
| `sthreeboutique.shop` / `.store` | Available when `.com` is not, but renews dearer than it sells. |

Avoid hyphens and numbers — `sthree-boutique-2026.com` is hard to say over the
phone, and the phone is how this shop sells.

**Where to buy.** Any registrar works; the difference is honesty about renewal
price.

- **Cloudflare Registrar** — sells at cost, no first-year trick, renews at the
  same price. You must use Cloudflare's DNS, which is Step 2 either way.
  Cheapest over five years.
- **Namecheap** — straightforward, fair renewals, simple DNS screen.
- **GoDaddy / BigRock** — heavily advertised. Watch the renewal price: the
  ₹199 first year often becomes ₹1,800. Also decline every add-on they offer.

**Buy only the domain.** Not hosting, not "website builder", not SSL, not
"professional email" yet. GitHub gives us hosting and the certificate free.
The only add-on worth having is **WHOIS privacy**, and most registrars now
include it free — it keeps Priyanka's name, address and phone out of a public
database.

Buy at least **2 years** if the price is the same per year. It is one less
thing to forget.

---

## Step 2 — Point the domain at GitHub (10 minutes)

In the registrar's **DNS** screen, add these records. Delete any existing
`A`, `AAAA` or `CNAME` on `@` or `www` first — a leftover parking record will
fight these.

**For the bare domain** (`sthreeboutique.com`) — four A records, all with host
`@`:

```
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

Optionally the same four times over for IPv6, as AAAA records on `@`:

```
2606:50c0:8000::153
2606:50c0:8001::153
2606:50c0:8002::153
2606:50c0:8003::153
```

**For `www`** — one CNAME record:

```
Type: CNAME    Host: www    Value: pudgeismylife-hash.github.io
```

Note the CNAME value is **just the github.io host, with no `/sthree-boutique`
after it.** A path in a CNAME is invalid and is the single most common mistake
here.

> ⚠️ I could not reach GitHub's docs from this machine to re-verify those IP
> addresses. They have been unchanged for years, but confirm them against
> <https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site>
> before typing them in. GitHub's own settings page (Step 3) will also tell you
> if they are wrong.

**Then wait.** DNS spreads in anything from 10 minutes to 24 hours. Check with:

```sh
dig +short sthreeboutique.com
dig +short www.sthreeboutique.com
```

When the four `185.199.*` addresses come back, move on. Until then everything
below will just report errors, so there is no point rushing it.

---

## Step 3 — Tell GitHub the domain (2 minutes)

1. Go to the repository → **Settings** → **Pages**.
2. Under **Custom domain**, type `sthreeboutique.com` and press **Save**.
3. GitHub runs a DNS check and shows a green tick, or tells you exactly what is
   wrong. If it complains, the DNS from Step 2 has not spread yet — wait and
   press Save again.

Saving this makes GitHub **commit a file called `CNAME` to the `main` branch**.
That file is what tells the server which domain to answer to.

**Pull it down before doing any more work**, or your next push will be built on
a branch that is one commit behind:

```sh
git fetch origin main
git merge --ff-only origin/main
cat CNAME          # should print: sthreeboutique.com
```

> **Never delete `CNAME`.** If it disappears from `main`, the custom domain
> switches off and the site drops back to the github.io address.

---

## Step 4 — Turn on HTTPS (1 minute, plus waiting)

Still in **Settings → Pages**, tick **Enforce HTTPS**.

The tick box is greyed out at first: GitHub has to get a certificate for the
domain from Let's Encrypt, which takes anywhere from a few minutes to about an
hour. Come back later and tick it.

Do not skip this. Without it browsers show "Not secure" next to the shop's
name, which costs more trust than the domain buys.

---

## Step 5 — Change the site's own address (5 minutes)

Everything above changes where the site *lives*. This changes what the site
*says about itself* — the canonical URL, the WhatsApp share previews for all 58
pieces, and the link at the bottom of every order message.

It is **one line**. In `build-hosted.js`, line 26:

```js
const SITE_URL = "https://pudgeismylife-hash.github.io/sthree-boutique";
```

becomes

```js
const SITE_URL = "https://sthreeboutique.com";
```

Then rebuild and push:

```sh
node build-hosted.js
grep -rl "github\.io" index.html collection.html p/ c/    # should print nothing
git add -A
git commit -m "Move the site to sthreeboutique.com"
git push origin main
```

I tested exactly this change on 5 September: that one line rewrites all 68
built files — `index.html`, `collection.html`, both standalone copies, 58
product share stubs and 6 category stubs — leaving no trace of the old address.
Nothing else in the code needs touching, because every image, stylesheet and
link in the site is already written as a relative path.

---

## Step 6 — Check it (5 minutes)

On a phone, not just a laptop:

- `https://sthreeboutique.com` loads and shows a padlock
- `https://www.sthreeboutique.com` loads too
- `https://pudgeismylife-hash.github.io/sthree-boutique/` **redirects** to the
  new address — GitHub does this automatically, so old links Priyanka has
  already sent keep working
- Open a piece → **Add to bag** → **WhatsApp order**. The message at the
  bottom should now carry `sthreeboutique.com`, not `github.io`
- Paste `https://sthreeboutique.com` into a WhatsApp chat to yourself. The link
  preview should show the logo and the shop's description

Then update the address in the places outside the site: **Instagram bio**,
Google Business Profile, WhatsApp Business profile, and Priyanka's status.

---

## What does *not* change

- **Hosting stays free.** GitHub Pages costs nothing and the certificate is
  free. The domain is the only bill.
- **Nothing about how the site is edited.** Same repository, same
  `node build-hosted.js`, same push-to-deploy.
- **No downtime.** The old address redirects the moment the new one works.
- **Emails.** `priyankamonteiro@gmail.com` keeps working exactly as now. See
  below if you want to change that.

---

## Costs, honestly

| Item | Per year |
|---|---|
| Domain `.com` | ₹900–1,500 (check the **renewal** price, not the first-year offer) |
| Domain `.in` | ₹500–900 |
| Hosting (GitHub Pages) | ₹0 |
| HTTPS certificate | ₹0 |
| **Total** | **₹500–1,500 a year** |

Set a calendar reminder for the renewal, or turn on auto-renew. A boutique
whose domain lapses loses the address to a squatter and does not get it back.

---

## Optional — email on the domain

Once the domain exists, `priyanka@sthreeboutique.com` is possible. It is a
separate job and it is not required for the website.

- **Zoho Mail** — free for one domain and a handful of users. The realistic
  choice for a shop this size.
- **Google Workspace** — around ₹150–250 per user per month. Familiar Gmail
  interface, but a real monthly bill.

If you do this, add the MX records the provider gives you **alongside** the A
records from Step 2 — they do not conflict, and email and website are separate
services on the same name. Then update `CONFIG.email` in
`sthree-boutique.html` and rebuild.

---

## If something goes wrong

| Symptom | Cause |
|---|---|
| GitHub says "Domain does not resolve" | DNS from Step 2 has not spread. Wait, retry Save. |
| Site loads but no padlock | Certificate not issued yet. Wait, then tick Enforce HTTPS. |
| `www` works, bare domain does not | The four A records on `@` are missing or wrong. |
| Bare domain works, `www` does not | The CNAME record is missing, or has a path after `.github.io`. |
| Site reverts to the github.io address | The `CNAME` file was deleted from `main`. Restore it. |
| Old WhatsApp links show the old preview | WhatsApp caches previews for days. It corrects itself. |
