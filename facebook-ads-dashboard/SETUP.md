# One-time Meta API setup

Goal: two values.

1. **`META_ACCESS_TOKEN`** — a long-lived token the fetcher uses to read ad
   data (goes into the Claude Code environment settings, never into a file).
2. **Ad account id** — looks like `act_1202…` (goes into `config.json`).

Everything happens at **business.facebook.com** (Business Settings) and
**developers.facebook.com**. You need to be an admin of the Momentum
Fitness Business portfolio. Budget ~30 minutes the first time.

---

## Step 0 — Find out what you already have

You mentioned you're not sure whether any of this already exists. Check in
this order; stop at the first thing you find:

1. Go to **business.facebook.com** → gear icon (**Settings**) →
   **Users → System users**.
   - *A system user is listed?* You may already be most of the way there —
     click it, check that the **Momentum ad account** is listed under its
     assets, and use **Generate token** (Step 3) instead of starting over.
   - *The menu doesn't show "System users"?* You may be on a personal ad
     account without a Business portfolio — Step 1 covers creating one.
2. Go to **developers.facebook.com/apps** while logged in with the same
   Facebook login.
   - *An app is listed?* (GoHighLevel's own connection will NOT appear here
     — integrations you authorized live under Business Settings →
     Integrations → Connected apps and can't be reused for this.) If you or
     an agency created an app before, you can reuse it: open it and jump to
     Step 2.
   - *Nothing listed?* That's the normal case — continue to Step 1.

> Tip: if an old agency set up your ads, the ad account may live in *their*
> Business portfolio. In Business Settings → **Accounts → Ad accounts**,
> confirm the Momentum account is owned by (or shared with) your portfolio.

## Step 1 — Create the app (skip if Step 0 found one)

1. **developers.facebook.com** → **My Apps → Create app**.
2. Type: **Business**. Name it something like `Momentum Ads Dashboard`.
   Connect it to the Momentum Business portfolio when asked.
3. No products need to be added — the Marketing API works from any Business
   app. Leave the app in **Development mode** (fine for reading your own
   account's data).

## Step 2 — Create a system user and give it the ad account

1. **business.facebook.com** → Settings → **Users → System users** →
   **Add**. Name: `ads-dashboard`. Role: **Employee** (Admin not needed).
2. With the system user selected → **Add assets**:
   - **Apps** → your app from Step 1 → toggle **Develop app**.
   - **Ad accounts** → the Momentum ad account → toggle **View performance**
     (read-only is all the dashboard needs).

## Step 3 — Generate the token

1. Still on the system user → **Generate new token**.
2. Pick the app from Step 1.
3. Token expiration: **Never** (system-user tokens support this; it's what
   makes the daily auto-refresh hands-off).
4. Permissions: check **`ads_read`** and **`read_insights`**. Nothing else.
5. Copy the token now — Meta shows it once.

## Step 4 — Find the ad account id

Business Settings → **Accounts → Ad accounts** → the id is shown under the
account name (a long number). In Ads Manager it's also the `act=` number in
the page URL. Put it in `config.json`:

```json
"ad_account_id": "act_XXXXXXXXXXXXXXX"
```

(committing this id is fine — it's not a secret, just an address).

## Step 5 — Store the token for Claude sessions

In **claude.ai/code** open this repository's **environment settings** and
add an environment variable:

- Name: `META_ACCESS_TOKEN`
- Value: the token from Step 3

That keeps it out of the repo while every session (including the scheduled
daily refresh) can read it.

## Step 6 — Smoke test

In a Claude session (or any terminal with the env var set):

```bash
cd facebook-ads-dashboard
pip install -r requirements.txt
python3 fetch_ads.py --fetch-only
```

Success looks like `Fetching ads for act_… / N ads`. The two common errors
are self-explanatory: an expired/invalid token (regenerate, Step 3) or a
missing-permission error (recheck Step 2's ad-account toggle and Step 3's
`ads_read`).

---

## GoHighLevel link (optional, 1 minute)

Open GoHighLevel in the browser, navigate to wherever you review new leads
(Contacts, or an Opportunities pipeline), copy the URL, and paste it into
`config.json` → `"gohighlevel_url"`. Website-lead ads will then show a
**Leads · GHL** button. Leave it `""` to hide those buttons.
