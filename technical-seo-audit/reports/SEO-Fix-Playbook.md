# Momentum Fitness — SEO Fix Playbook

**Companion to:** `audit-report.md` (the audit) · **Site:** https://themomentumfitness.com
**How to use this:** Every fix below gives you the **exact text to paste** and **where to click** in WordPress. Work top-down — they're ordered by impact. Anything only you know is marked **`FILL-IN`**.

> **Two things before you start**
> 1. **Back up first.** Your host (GoDaddy) or a plugin like *UpdraftPlus* can take a one-click backup. Do it before touching schema or bulk media.
> 2. **Where changes happen:** *wp-admin* = your WordPress dashboard (`themomentumfitness.com/wp-admin`). *Elementor* = the visual page editor (click **Edit with Elementor** on a page). *Rank Math* = your SEO plugin, both in the left sidebar and in a box below each page's editor.

---

## 1. Homepage 27 MB autoplay video  `[HIGH]`

The homepage autoplays a **27 MB** video (`file.mp4`) plus a 1 MB loop. This is the single biggest speed problem. Two ways to fix — do **A** (fastest) or **B** (best).

**Option A — stop it autoplaying (5 min, no new files):**
1. Homepage → **Edit with Elementor**.
2. Click the hero video widget → left panel **Content** tab.
3. Set **Autoplay: No**, and set a **Poster** image (a nice still frame). Leave **Lazy Load: Yes** if shown.
4. Update. Now the big file only downloads if a visitor clicks play.

**Option B — replace it with a small file (best result):**
1. Compress the video first. Free tool **HandBrake** (handbrake.fr) → open `file.mp4` → use these exact settings:
   - Preset: **Web → Gmail Medium 5 Minutes 480p30**, then bump **Resolution Limit to 1280×720**.
   - **Audio tab:** remove the audio track (a background hero doesn't need it).
   - Format **MP4**, Video codec **H.264**. Target output **under 4 MB**.
2. In wp-admin → **Media → Add New** → upload the new file.
3. Homepage → Edit with Elementor → hero widget → swap the video URL to the new upload → Update.

Repeat for the other autoplay offenders: `members-1.mp4` (~6.7 MB) and the Instagram rip `Snapinst.app_video_…mp4` (~11 MB) on Pricing, Who We Are, Careers, and Gallery. The `Snapinst` file especially should be re-exported or dropped.

> The testimonial videos elsewhere on your site are already done right (poster image + click-to-play). You're just bringing the hero up to the same standard.

---

## 2. Page titles — paste-ready rewrites  `[HIGH]`

**Where to set each one:** open the page → scroll to the **Rank Math** box below the editor → click **Edit Snippet** → paste into the **Title** field → Update. (Do *not* retype the page's H1 — this is only the browser-tab / Google-results title.)

These are all **≤60 characters** with the service + city first and the brand last. Skip any page you're going to noindex in §3–§4 (trainer, category, author, thank-you pages) — those don't need titles.

### Core / money pages
| Page | Paste this title |
|---|---|
| Homepage `/` | `More Than a Gym: PT + Training \| Arlington TX` |
| `/pricing/` | `Personal Training & PT Pricing \| Arlington TX` |
| `/what-we-do/` | `Our Services: Training & PT \| Arlington TX` |
| `/who-we-are/` | `Meet the Team: DPTs & Trainers \| Arlington TX` |
| `/results/` | `Client Transformations: Pain to Performance \| TX` |
| `/gallery/` | `Photo Gallery \| Momentum Fitness Gym, Pantego TX` |
| `/blog/` | `Training & Recovery Tips \| Momentum Fitness Blog` |
| `/careers/` | `Careers at Momentum Fitness \| Arlington TX` |
| `/vip-membership/` | `VIP Gym Membership \| Momentum Fitness, Pantego TX` |
| `/hsa-fsa/` | `Use Your HSA/FSA for Training & PT \| Momentum TX` |
| `/information-for-physicians/` | `Information for Physicians \| Momentum Fitness TX` |
| `/physician-referrals-…/` | `Physician Referrals for PT \| Arlington TX` |

### "What We Do" service pages
| Page | Paste this title |
|---|---|
| `/what-we-do/1-on-1-personal-training/` | `1-on-1 Personal Training \| Arlington & Mansfield TX` |
| `/what-we-do/semi-private-personal-training-in-arlington/` | `Partner & Couples Training \| Arlington TX` |
| `/what-we-do/nutritional-guidance/` | `Nutrition Coaching \| Arlington & Mansfield TX` |
| `/what-we-do/executive-membership/` | `Executive Gym Membership \| Arlington TX` |
| `/what-we-do/physics-101/` | `Physics 101 Training Method \| Momentum Fitness TX` |
| `/adult-fitness-in-arlington-and-mansfield/` | `Adult Fitness Training \| Arlington & Mansfield TX` |

### Athlete performance pages
| Page | Paste this title |
|---|---|
| `/athlete-performance-training-…/` (parent) | `Athlete Performance Training \| Arlington TX` |
| `…/sports-performance-training-…/` | `Sports Performance Training \| Arlington TX` |
| `…/sports-specific-1-on-1-athlete-training-…/` | `1-on-1 Sports-Specific Training \| Arlington TX` |
| `…/off-season-athletic-training-…/` | `Off-Season Athletic Training \| Arlington TX` |
| `…/in-season-athletic-training-…/` | `In-Season Athletic Training \| Arlington TX` |

### Recovery & movement therapy pages
| Page | Paste this title |
|---|---|
| `/recovery-and-movement-therapy-…/` (parent) | `Recovery & Movement Therapy \| Arlington TX` |
| `…/physical-therapy-…/` | `Physical Therapy \| Arlington & Mansfield TX` |
| `…/manual-therapy/` | `Manual Therapy: Fascial Distortion Model \| TX` |
| `…/myofascial-release-…/` | `Myofascial Release Therapy \| Arlington TX` |
| `…/dry-needling-…/` | `Dry Needling \| Arlington & Mansfield TX` |
| `…/cupping-therapy-…/` | `Cupping Therapy for Recovery \| Arlington TX` |
| `…/mobility-training-…/` | `Mobility Training \| Arlington & Mansfield TX` |
| `…/strength-based-rehab-…/` | `Strength-Based Rehab \| Arlington & Mansfield TX` |
| `…/rehab-to-performance-…/` | `Rehab to Performance \| Arlington & Mansfield TX` |

### "Conditions We Treat" pages
| Page | Paste this title |
|---|---|
| `/conditions-we-help-treat/` (parent) | `Conditions We Treat \| Physical Therapy Arlington TX` |
| `…/chronic-pain-musculoskeletal-conditions/` | `Chronic Pain & Musculoskeletal Care \| Arlington TX` |
| `…/metabolic-conditions/` | `Metabolic & Diabetes Care \| Arlington TX` |
| `…/degenerative-aging-conditions/` | `Degenerative & Aging Condition Care \| Arlington TX` |
| `…/cardiovascular-fatigue-conditions/` | `Cardiovascular & Fatigue Care \| Arlington TX` |
| `…/womens-health-hormonal-conditions/` | `Women's Health & Hormonal Care \| Arlington TX` |
| `…/behavioral-lifestyle-patterns/` | `Behavioral & Lifestyle Support \| Arlington TX` |
| `…/post-rehab-performance-gap-…/` | `Post-Rehab & Performance Gap \| Arlington TX` |
| `…/neurological-conditions-care/` | `Neurological Condition Care \| Arlington TX` |

### Low-priority (optional)
`/privacy-policy/` and `/terms-and-conditions/` can keep their default titles — they don't rank and it doesn't matter.

---

## 3. Trainer pages — thin & orphaned  `[MED-HIGH]`

Your 12 `/team-member/…` pages have ~15 words each, no meta description, and nothing links to them. Two options — **I recommend the quick noindex path** unless you're ready to write real bios.

**Path A — Quick (recommended, ~15 min):** hide them from Google.
1. For each trainer page: open it → **Rank Math** box → **Advanced** tab → set **Robots Meta** to **No Index**. Update.
2. Rank Math → **Titles & Meta → check for a "Team Member" / CPT section** and set its sitemap to **off** (removes `team-member-sitemap.xml`).

**Path B — Better (if you want them to rank):** give each a real profile.
- Use this template per trainer (replace **`FILL-IN`**):
  > **`FILL-IN Name`** is a **`FILL-IN role/credential, e.g. Doctor of Physical Therapy / NASM-CPT`** at Momentum Fitness in Pantego, serving Arlington and Mansfield. They specialize in **`FILL-IN 2–3 specialties`** and work with clients who **`FILL-IN who they help`**. **`FILL-IN one sentence of personality or a client win.`** *(Aim for 150–300 words.)*
- Meta description template: `Meet FILL-IN Name, FILL-IN role at Momentum Fitness in Arlington & Mansfield TX. Specializes in FILL-IN.` (~150 chars)
- **Make the team grid link to them:** Who We Are → Edit with Elementor → each team card's image/name should be a **Link** to that trainer's URL (currently they aren't crawlable links).

---

## 4. Junk pages in your sitemap  `[MED-HIGH]`

These should never appear in Google. All fixes are in **Rank Math → Titles & Meta**.

1. **Categories:** open the **Categories** tab → set **Robots Meta → No Index**. (Drops `/category/uncategorized/` and its sitemap.)
2. **Authors:** open the **Authors** tab → toggle **Author Archives → Off** entirely (you have two near-empty author pages, one leaking your agency's email in the URL).
3. **Thank-you page:** open `/thank-you/` → Rank Math box → **Advanced → Robots Meta → No Index**. (Stops it showing in search and firing false conversions.)
4. **Rename "Uncategorized":** wp-admin → **Posts → Categories** → hover *Uncategorized* → **Edit** → rename to **`Training Tips`** (slug `training-tips`) → assign both existing blog posts to it.

---

## 5. Pages missing an H1  `[MED-HIGH]`

Every page should have **exactly one H1**. These currently have zero (or the homepage has three). In **Elementor**, click the main headline → left panel → **Advanced → (or the heading widget's) HTML Tag** dropdown → set to **H1**.

| Page | What to do |
|---|---|
| Homepage `/` | Keep **"Personal and Physical Training To Feel Your Best"** as the only H1; change *"Specialized Training and Physical Therapy in Arlington"* and *"Services We Offer"* to **H2**. |
| `/pricing/` | Set the top headline (near *"The Cost of Action…"*) to **H1** — or add one: `Personal Training & Physical Therapy Pricing`. |
| `/contact/` | Set **"CONTACT US!"** to **H1**. |
| `/who-we-are/` | Set **"WHO WE ARE"** to **H1**. |
| `/gallery/` | Set **"View Our Gym"** to **H1**. |
| `/careers/` | Set **"Build a Career, Not Just a Job"** to **H1**. |
| `/vip-membership/` | Set **"VIP MEMBERSHIP"** to **H1**. |
| `/what-we-do/executive-membership/` | Set **"Executive Membership"** to **H1**. |
| `/what-we-do/nutritional-guidance/` | Set **"Nutrition Coaching in Arlington & Mansfield, TX"** to **H1**. |
| `/blog/` | Set **"OUR BLOG"** to **H1**. |
| `/terms-and-conditions/` | Delete the duplicate — it has **two** identical "Terms and Conditions" H1s; keep one. |
| `/thank-you/` | No action needed (you're noindexing it in §4). |

---

## 6. Missing / duplicate meta descriptions  `[MEDIUM]`

Once §3 and §4 are done, only these three need attention. **Rank Math** box → **Edit Snippet → Description**:

| Page | Paste this description |
|---|---|
| `/pricing/` | `See transparent pricing for personal training and physical therapy at Momentum Fitness in Pantego, serving Arlington & Mansfield. Book a free discovery visit.` |
| `/gallery/` | `Take a look inside Momentum Fitness — our private training facility and recovery space in Pantego, TX, serving Arlington and Mansfield.` |
| `/blog/` | `Training, recovery, and physical-therapy tips from the coaches and DPTs at Momentum Fitness in Arlington & Mansfield, TX.` |

---

## 7. Oversized images  `[MEDIUM]`

26 files are over 300 KB, including six ~1 MB **PNG** squares and ~1 MB trainer portraits. Fix in bulk:

1. wp-admin → **Plugins → Add New** → search **ShortPixel** (or **Imagify**) → install & activate → grab the free API key it prompts for.
2. In its settings: enable **WebP/AVIF conversion**, set **Resize large images to max 1024px wide**, quality **Glossy/80**.
3. Run **Bulk Optimize** on the whole Media Library. Typically cuts those 1 MB files to 60–150 KB with no visible change.
4. **Going forward:** save photos as **JPG or WebP**, never PNG. PNG is only for logos/flat-color graphics.

---

## 8. Missing image alt text  `[MEDIUM]`

502 of 658 image slots have no alt text. The fast win: **8 template images repeat on every page** — fixing them once clears the count across all 62 pages. In **Media → Library**, click each file and fill the **Alt Text** field:

| File | Paste this alt text |
|---|---|
| `53DB4F05-…C9281.webp` (your logo) | `Momentum Fitness logo` |
| `Email-Logo.png` | *(leave blank — decorative)* |
| `cassie.jpg` | `FILL-IN Cassie's role, e.g. Cassie, personal trainer at Momentum Fitness` |
| `Jade.jpg` | `FILL-IN Jade's role at Momentum Fitness` |
| `DREW.jpg` | `FILL-IN Drew's role at Momentum Fitness` |
| `mona.jpg` | `FILL-IN Mona's role at Momentum Fitness` |
| `Dina.jpg` | `FILL-IN Dina's role at Momentum Fitness` |

**For every other image, use this formula:** *what's happening + where.* Examples:
- A training photo → `Coach guiding a client through a barbell squat at Momentum Fitness in Pantego, TX`
- A gym interior → `Private training floor at Momentum Fitness, Arlington & Mansfield TX`
- The 64 junk-named files (`IMG_4769`, `Screenshot-…`, `Snapinst.app_…`) — add alt text now; when you replace them, rename to something like `personal-training-arlington-tx.webp` before uploading.

---

## 9. Structured data (schema)  `[MEDIUM]`

Good news: your site already outputs proper local-business schema. Two fixes:

**A) Fix the opening hours (all 50 pages at once).** Your schema currently claims you're open **9 AM–5 PM, 7 days a week** — almost certainly a default. Rank Math → **Titles & Meta → Local SEO** (or **Rank Math → Local SEO**) → set your **real** hours:
> **`FILL-IN` your actual hours**, e.g. Mon–Fri 05:00–20:00, Sat 07:00–12:00, Sun closed.

Make sure they match your Google Business Profile exactly.

**B) Add FAQ schema to key pages.** Edit Pricing and each condition page in the block editor → add a **Rank Math → FAQ block** → use drafts like these (edit the answers to be true):
- **Q:** `How much does personal training cost at Momentum Fitness?`
  **A:** `FILL-IN — e.g. Our programs start at $X/session; book a free discovery visit for a custom plan.`
- **Q:** `Do you take insurance or HSA/FSA?`
  **A:** `FILL-IN — e.g. We're self-pay but provide superbills and accept HSA/FSA with a Letter of Medical Necessity.`
- **Q:** `Where are you located?`
  **A:** `We're at 2401 W Pioneer Pkwy #103, Pantego, TX 76013 — serving Arlington and Mansfield.`

**C) Review markup (optional).** On the Results page, mark up a few real client reviews with Rank Math's review schema so your Best-Gym-2024/2025 recognition can show as stars.

Validate everything at **https://search.google.com/test/rich-results** — paste the homepage URL; it should show "Local business" with no errors.

---

## 10. Internal-link gaps  `[LOW]`

- **VIP Membership is orphaned** (a sales page nothing links to). Add it to your main menu: wp-admin → **Appearance → Menus** → add the *VIP Membership* page → Save. Also link to it from the Pricing page body.
- **Privacy / Terms** footer links aren't rendering as real links — check the footer template in Elementor and make sure they're proper **Link** elements, not plain text.
- **Email-protection links:** the Cloudflare `/cdn-cgi/l/email-protection` link shows on all 62 pages. Harmless, but if you'd rather, display your email as plain text or an image and turn off Cloudflare's email obfuscation.

---

## How to check your work

After you've made changes, you can **re-run the same audit** that produced this list to see the numbers drop:

```bash
cd technical-seo-audit
.venv/bin/python seo_audit.py
```

Watch these counts in the summary fall toward zero:
- `default_suffix_titles` (§2) · `multi_or_no_h1` (§5) · `missing_descriptions` (§6)
- `noindex_pages` should *rise* to ~15 as you noindex the junk/trainer pages (§3–§4) — that's correct.

Then:
- **Schema:** https://search.google.com/test/rich-results
- **Speed (after the video fix):** https://pagespeed.web.dev — test the homepage, watch **Largest Contentful Paint** improve.

---

### Realistic time budget
| Session | Do | ~Time |
|---|---|---|
| 1 | §1 video + §4 junk pages + §9A hours | ~1.5 hr |
| 2 | §2 titles (paste from the tables) | ~2 hr |
| 3 | §5 H1s + §3 trainer pages | ~2 hr |
| 4 | §7 image plugin + §8 alt text + §6 descriptions + §10 links | ~2 hr |
