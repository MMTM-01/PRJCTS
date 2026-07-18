# Momentum Fitness — Technical SEO Audit Report

**Site:** https://themomentumfitness.com (Momentum Proactive Health & Fitness, Pantego TX)
**Crawl date:** July 18, 2026 · **Pages crawled:** 62 (every URL in the sitemap) · all returned HTTP 200

## The good news first

The foundation is solid, and several things many local sites get wrong are already right:

- **Every page loads correctly** — no 404s, no server errors, no redirect chains.
- **Canonical tags are clean** on all 62 pages (no mismatches, none missing).
- **The sitemap and robots.txt work** and are properly linked.
- **Local business schema is already live on ~50 pages** — `ExerciseGym` + `Organization` with the correct street address, geo-coordinates, phone number, logo, and social profiles. (This means the `schema-localbusiness.json` file in this folder is now a nice-to-have, not a must-do — see item 9 for the two things the existing schema still gets wrong.)
- **Nothing is accidentally noindexed.**

Below are the top 10 problems, ranked by how much fixing each one is likely to move the needle.

---

## 1. The homepage autoplays a 27 MB video 🔴

**What we found:** The homepage hero autoplays `wp-content/uploads/2025/01/file.mp4` — **27.2 MB** — plus a second 1 MB autoplay loop. Because they autoplay, browsers download them immediately. A visitor on a phone is pulling down roughly 30 MB before the page settles; on average mobile data that's 15–30 seconds of loading and a real chunk of someone's data plan. Google's page-experience signals (Core Web Vitals) will grade this harshly, and slow heroes measurably increase bounce rate on exactly the page most ad clicks and Google Business Profile clicks land on. Pricing, Who We Are, Careers, and Gallery also autoplay 6–11 MB videos (`members-1.mp4`, the `Snapinst.app_…` Instagram rip).

**The fix (biggest single win on this list):**
- Re-export the hero video web-optimized: 720p, no audio track, H.264/H.265, target **2–4 MB** for a short loop. HandBrake (free) or any editor can do this; upload the new file and swap it in Elementor.
- Or replace autoplay with a poster image + click-to-play (the testimonial videos elsewhere on the site already do this correctly with `preload="metadata"` and poster frames — copy that pattern).
- For any video over ~10 MB you want to keep, host it on YouTube/Vimeo and embed it instead of serving it from your own WordPress uploads.

## 2. 38 of 62 page titles are unoptimized defaults 🔴

**What we found:** 38 pages still have the auto-generated "`Page Name - Momentum Fitness`" title, and 23 titles are longer than 60 characters (Google cuts them off). The title tag is the strongest on-page ranking signal you directly control, and these are on money pages: **Pricing**, **Conditions We Help Treat**, the sports-performance pages, and both blog posts. Meanwhile the pages that *were* hand-written ("More Than a Gym: Physical Therapy + Training | Momentum Fitness, TX") show the team already knows the format — it just hasn't been applied everywhere.

**The fix:** In Rank Math's snippet editor on each page, write a ~50–60-character title with the service + city first, brand last. Examples:
- Pricing → `Personal Training Pricing | Arlington & Mansfield TX`
- Conditions We Help Treat → `Conditions We Treat | Physical Therapy Arlington TX`
- Blog post → `Momentum Fitness vs. Big-Box Gyms in Arlington TX`

Start with Pricing, the six "what we do" pages, and the condition pages — those are the searches with buying intent.

## 3. All 12 trainer pages are nearly empty and invisible 🟠

**What we found:** Every `/team-member/…` page contains about **15 words** of real content, has **no meta description**, and — critically — **no other page links to any of them** (the Who We Are team grid isn't producing crawlable links). Twelve orphaned, near-blank indexable pages is exactly the "thin content" pattern Google's helpful-content systems demote sites for, and it wastes the chance to rank for "personal trainer Arlington" / trainer-name searches.

**The fix (pick one, don't leave as-is):**
- **Better:** Give each trainer a 150–300 word bio (certifications, specialties, who they help, a client quote) and make the Who We Are grid link to the profiles with real links.
- **Faster:** If you don't want trainer pages ranking, set them to noindex in Rank Math and remove `team-member-sitemap.xml` from the sitemap.

## 4. Junk pages are in your sitemap and index 🟠

**What we found:** The sitemap invites Google to index pages that should never rank:
- `/category/uncategorized/` — the default WordPress category, with 90 words of duplicate blog-roll content.
- `/author/themomentumfitness/` and `/author/hellolevitatedigitalmedia-com/` — near-empty author archives; the second one also exposes your web agency's email-derived username in a public URL.
- `/thank-you/` — the post-contact confirmation page (32 words). If this ranks or gets clicked from search, your conversion tracking fires without a real lead.

**The fix:** In Rank Math → Titles & Meta, set **Categories** and **Authors** to noindex (this also drops them from the sitemap automatically). Set `/thank-you/` to noindex in its page-level Rank Math settings. Rename the "Uncategorized" category to something real (e.g. "Training Tips") and assign both posts to it.

## 5. 12 pages have no H1 heading — including Pricing and Contact 🟠

**What we found:** Pricing, Contact, Who We Are, Careers, Gallery, VIP Membership, Executive Membership, Nutritional Guidance, Blog, Thank You, and the archive pages have **zero H1 tags**; the homepage has **three** and Terms has two. The H1 tells Google (and screen readers) what the page is about — a Pricing page with no H1 is leaving an easy signal on the table.

**The fix:** In Elementor, each page's main headline widget should be set to tag **H1** (Style/HTML-tag dropdown) — exactly one per page. On the homepage, keep "Personal and Physical Training To Feel Your Best" as the H1 and demote the other two to H2.

## 6. 16 pages missing meta descriptions, 2 sharing one 🟡

**What we found:** 16 pages have no meta description (the 12 trainer pages, Blog, and the archives — mostly resolved by items 3 and 4), and Pricing and Gallery share the same copy-pasted description. Descriptions don't directly affect rankings but they are your ad copy in the search results.

**The fix:** After doing items 3–4, only Blog, Pricing, and Gallery need attention: write a unique ~150-character description for each in Rank Math (Pricing's should mention transparent pricing, Arlington/Mansfield, and a reason to click).

## 7. 26 media files are oversized — 1 MB+ PNG portraits 🟡

**What we found:** Beyond the videos in item 1, 26 images/videos exceed 300 KB. The worst offenders are six ~1 MB **PNG** square graphics (`/2025/09/…-1024x1024.png`) and ~1 MB trainer portraits (`PT-David-Bri-2-.png`, 849 KB `PT-Hasbi-Darla-1-.png`) — photos saved as PNG, which is the wrong format and 5–10× larger than needed.

**The fix:** Install a compression plugin (ShortPixel, Imagify, or Smush) and bulk-convert the media library to WebP with max width 1024px. That alone typically cuts these to 60–150 KB each with no visible difference. Going forward, upload photos as JPG/WebP, never PNG (PNG is only for logos/graphics with flat colors).

## 8. Three-quarters of image tags have no alt text 🟡

**What we found:** 502 of 658 image instances have empty alt attributes — including the same ~8 template images (footer/testimonial section) repeated on every page — and 64 images have junk filenames like `Screenshot-2024-11-01-154605_edited.avif`, `IMG_4769`, and `Snapinst.app_468398002_…`. Alt text is how Google understands images, it's an accessibility requirement, and image search is a real discovery channel for gyms ("gym in pantego tx" image results).

**The fix:** In Media Library, add alt text describing the photo naturally ("Trainer coaching a client through a barbell squat at Momentum Fitness in Pantego TX"). Fix the ~8 sitewide template images first — that clears the count on all 62 pages at once. Rename files before uploading in the future (`personal-training-arlington-tx.webp`, not `IMG_4769.webp`).

## 9. The schema says you're open 9–5 every day 🟡

**What we found:** The good news is the site already outputs proper `ExerciseGym` local-business schema (see top of report). Two problems in it:
1. `openingHours` is **"Monday–Sunday 09:00–17:00"** — almost certainly the plugin's default, not your real hours. Wrong structured hours can surface directly in search results and contradict your Google Business Profile, which erodes Google's trust in both.
2. No `Review`/`AggregateRating`, `Service`, or `FAQPage` schema anywhere — the site brags about being Living Magazine's Best Gym 2024 & 2025 but gives Google nothing machine-readable about ratings or services.

**The fix:** In Rank Math → Local SEO, set your real opening hours (this fixes all 50 pages at once). Then add FAQ blocks (with Rank Math's FAQ schema) to the Pricing and condition pages, and mark up genuine client reviews on the Results page. Verify at https://search.google.com/test/rich-results.

## 10. Internal-link gaps: your VIP sales page is orphaned 🟢

**What we found:** Besides the trainer pages (item 3), **`/vip-membership/`** — a sales page — has no internal links pointing to it at all; nothing on the site tells visitors or Google it exists. `/privacy-policy/` and `/terms-and-conditions/` are also orphaned (footer links to them aren't rendering as crawlable links). Minor: the Cloudflare email-protection link (`/cdn-cgi/l/email-protection`) shows up as a broken-looking link on all 62 pages — harmless for users, but noise for crawlers; consider displaying the email as plain text or an image instead of relying on Cloudflare's obfuscation.

**The fix:** Add VIP Membership to the main nav or the What We Do page and mention it from Pricing. Check the footer widget so Privacy/Terms render as normal `<a>` links.

---

## Suggested order of attack

| Week | Do | Effort | Impact |
|---|---|---|---|
| 1 | Compress/replace the homepage hero video (item 1) | ~1 hr | 🔴 High |
| 1 | Noindex archives + thank-you, rename Uncategorized (item 4) | ~30 min | 🟠 Med-high |
| 1 | Fix opening hours in Rank Math Local SEO (item 9) | ~10 min | 🟡 Medium |
| 2 | Rewrite titles on the ~15 money pages (item 2) | ~3 hrs | 🔴 High |
| 2 | Set one H1 on every page (item 5) | ~2 hrs | 🟠 Medium |
| 3 | Trainer bios + team-grid links, or noindex (item 3) | ~4 hrs | 🟠 Med-high |
| 3 | Bulk image compression plugin + WebP (item 7) | ~1 hr | 🟡 Medium |
| 4 | Alt text on template images, then per-page (item 8) | ongoing | 🟡 Medium |
| 4 | Meta descriptions, VIP links, FAQ schema (items 6, 9, 10) | ~2 hrs | 🟡 Medium |

## Data files

- **`audit-data.csv`** — one row per page with every field checked (opens in Excel/Google Sheets).
- **`audit-raw.json`** — full raw crawl data: heading outlines, per-image detail, schema blocks, media sizes, link statuses.
