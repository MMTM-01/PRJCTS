#!/usr/bin/env python3
"""
Technical SEO crawler for https://themomentumfitness.com
(Momentum Proactive Health & Fitness — Pantego, TX)

What it does, in order:
  Step 1: Reads robots.txt + the XML sitemap (following sitemap-index children)
          to build the list of indexable pages. Prints the page count.
  Step 2: Crawls every page politely (1 request/second, browser user-agent,
          respects robots.txt) and extracts all technical SEO fields.
  Step 3: Runs sitewide analysis (duplicates, unoptimized titles, schema
          summary, heavy media, broken links, redirect chains, orphan pages).
  Step 4: Writes reports/audit-data.csv and reports/audit-raw.json
          (override the destination with --out-dir).

Usage:
  .venv/bin/python seo_audit.py            # full audit
  .venv/bin/python seo_audit.py --max-pages 5   # quick smoke test
"""

import argparse
import csv
import io
import json
import os
import re
import sys
import time
import urllib.robotparser
from collections import Counter, defaultdict
from urllib.parse import urljoin, urlparse, urldefrag
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup

BASE = "https://themomentumfitness.com"
HOST = urlparse(BASE).netloc.lower()
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
CRAWL_DELAY = 1.0          # seconds between requests (polite crawling)
HEAVY_IMAGE_BYTES = 300 * 1024
THIN_CONTENT_WORDS = 300
TITLE_MAX = 60
DESC_MAX = 160
DEFAULT_TITLE_SUFFIX = re.compile(r"[-–—]\s*Momentum Fitness\s*$", re.I)
JUNK_FILENAME = re.compile(
    r"(?i)(^|[/_-])(img[_-]?\d+|dsc[_-]?\d+|screen[\s_-]?shot|unnamed|untitled"
    r"|image\s?\(?\d*\)?|photo[_-]?\d+|whatsapp[\s_-]?image|received[_-]?\d+"
    r"|fb[_-]?img[_-]?\d+|\d{6,})"
)

_last_request_time = [0.0]


def polite_wait():
    elapsed = time.monotonic() - _last_request_time[0]
    if elapsed < CRAWL_DELAY:
        time.sleep(CRAWL_DELAY - elapsed)
    _last_request_time[0] = time.monotonic()


def fetch(session, url, method="GET", **kw):
    polite_wait()
    kw.setdefault("timeout", 30)
    kw.setdefault("allow_redirects", True)
    return session.request(method, url, **kw)


def norm_url(url):
    """Normalize for comparisons: drop fragment, lowercase host, keep trailing slash as-is."""
    url, _ = urldefrag(url)
    p = urlparse(url)
    return p._replace(netloc=p.netloc.lower(), query=p.query).geturl()


def is_internal(url):
    host = urlparse(url).netloc.lower()
    return host in (HOST, HOST.replace("www.", ""), "www." + HOST)


# ---------------------------------------------------------------- Step 1

def load_robots(session):
    url = BASE + "/robots.txt"
    rp = urllib.robotparser.RobotFileParser()
    sitemaps = []
    try:
        r = fetch(session, url)
        if r.status_code == 200:
            lines = r.text.splitlines()
            rp.parse(lines)
            sitemaps = [l.split(":", 1)[1].strip()
                        for l in lines if l.lower().startswith("sitemap:")]
            print(f"robots.txt fetched ({len(lines)} lines, "
                  f"{len(sitemaps)} sitemap declarations)")
        else:
            print(f"robots.txt returned HTTP {r.status_code}; assuming allow-all")
            rp.parse([])
    except requests.RequestException as e:
        print(f"robots.txt fetch failed ({e}); assuming allow-all")
        rp.parse([])
    return rp, sitemaps


def _localname(tag):
    return tag.rsplit("}", 1)[-1].lower() if isinstance(tag, str) else ""


def parse_sitemap_xml(content):
    """Return (child_sitemap_urls, page_urls) from one sitemap document."""
    children, pages = [], []
    try:
        root = ElementTree.fromstring(content)
    except ElementTree.ParseError:
        return children, pages
    is_index = "sitemapindex" in _localname(root.tag)
    # Only take <loc> that is a direct child of <url>/<sitemap>, so that
    # image:loc / video:loc extensions are not mistaken for page URLs.
    for entry in root:
        if _localname(entry.tag) not in ("url", "sitemap"):
            continue
        for child in entry:
            if _localname(child.tag) != "loc":
                continue
            u = (child.text or "").strip()
            if u:
                (children if is_index else pages).append(u)
    return children, pages


def discover_pages(session, robots_sitemaps):
    candidates = list(robots_sitemaps) or [
        BASE + "/sitemap.xml",
        BASE + "/sitemap_index.xml",
        BASE + "/wp-sitemap.xml",
    ]
    seen_sitemaps, pages = set(), []
    queue = list(candidates)
    while queue:
        sm = queue.pop(0)
        if sm in seen_sitemaps:
            continue
        seen_sitemaps.add(sm)
        try:
            r = fetch(session, sm)
        except requests.RequestException as e:
            print(f"  sitemap {sm}: fetch failed ({e})")
            continue
        if r.status_code != 200:
            print(f"  sitemap {sm}: HTTP {r.status_code}")
            continue
        children, page_urls = parse_sitemap_xml(r.text)
        print(f"  sitemap {sm}: {len(children)} child sitemaps, {len(page_urls)} URLs")
        queue.extend(children)
        pages.extend(page_urls)
        if page_urls and not robots_sitemaps:
            # We found a working default-location sitemap; stop probing others.
            robots_sitemaps = [sm]
    # Keep same-host page URLs only, dedupe, stable order.
    out, seen = [], set()
    for u in pages:
        n = norm_url(u)
        if is_internal(n) and n not in seen:
            seen.add(n)
            out.append(n)
    return out


# ---------------------------------------------------------------- Step 2

def extract_schema_types(node, found):
    if isinstance(node, dict):
        t = node.get("@type")
        if isinstance(t, str):
            found.append(t)
        elif isinstance(t, list):
            found.extend(x for x in t if isinstance(x, str))
        for v in node.values():
            extract_schema_types(v, found)
    elif isinstance(node, list):
        for v in node:
            extract_schema_types(v, found)


def word_count_main(soup):
    body = soup.find("body")
    if not body:
        return 0
    clone = BeautifulSoup(str(body), "html.parser")
    for sel in ("script", "style", "noscript", "header", "footer", "nav", "form"):
        for el in clone.find_all(sel):
            el.decompose()
    # Elementor header/footer templates live in divs with these markers.
    for el in clone.find_all(attrs={"data-elementor-type": re.compile(r"header|footer", re.I)}):
        el.decompose()
    text = clone.get_text(" ", strip=True)
    return len(text.split())


def analyze_page(url, resp, soup):
    d = {"url": url, "status": resp.status_code, "final_url": norm_url(resp.url)}
    d["redirect_chain"] = " -> ".join(
        [f"{h.status_code}:{h.url}" for h in resp.history] + [str(resp.status_code) + ":" + resp.url]
    ) if resp.history else ""

    title_el = soup.find("title")
    d["title"] = title_el.get_text(strip=True) if title_el else ""
    d["title_length"] = len(d["title"])

    desc_el = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    d["meta_description"] = (desc_el.get("content") or "").strip() if desc_el else ""
    d["meta_desc_length"] = len(d["meta_description"])

    robots_el = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.I)})
    d["meta_robots"] = (robots_el.get("content") or "").strip() if robots_el else ""
    d["noindex"] = "noindex" in d["meta_robots"].lower()

    canon_el = soup.find("link", attrs={"rel": lambda v: v and "canonical" in v})
    d["canonical"] = norm_url(urljoin(url, canon_el["href"])) if canon_el and canon_el.get("href") else ""
    d["canonical_mismatch"] = bool(d["canonical"]) and d["canonical"].rstrip("/") != d["final_url"].rstrip("/")

    h1s = soup.find_all("h1")
    d["h1_count"] = len(h1s)
    d["h1_text"] = " || ".join(h.get_text(" ", strip=True) for h in h1s)

    outline = []
    for h in soup.find_all(["h1", "h2", "h3"]):
        level = int(h.name[1])
        txt = h.get_text(" ", strip=True)[:90]
        outline.append(("  " * (level - 1)) + f"H{level}: {txt}")
    d["heading_outline"] = "\n".join(outline)

    images = []
    for img in soup.find_all("img"):
        src = img.get("src") or img.get("data-src") or img.get("data-lazy-src") or ""
        if not src or src.startswith("data:"):
            continue
        src = urljoin(url, src)
        alt = (img.get("alt") or "").strip()
        fname = urlparse(src).path.rsplit("/", 1)[-1]
        images.append({
            "src": src,
            "alt": alt,
            "missing_alt": not alt,
            "junk_filename": bool(JUNK_FILENAME.search(fname)),
        })
    d["images"] = images
    d["images_total"] = len(images)
    d["images_missing_alt"] = sum(1 for i in images if i["missing_alt"])
    d["images_junk_filename"] = sum(1 for i in images if i["junk_filename"])

    types = []
    d["schema_raw"] = []
    for s in soup.find_all("script", attrs={"type": re.compile(r"ld\+json", re.I)}):
        raw = s.string or s.get_text() or ""
        try:
            data = json.loads(raw.strip())
        except (json.JSONDecodeError, AttributeError):
            try:
                data = json.loads(re.sub(r"[\x00-\x1f]", " ", raw))
            except Exception:
                continue
        d["schema_raw"].append(data)
        extract_schema_types(data, types)
    d["schema_types"] = sorted(set(types))

    links = set()
    for a in soup.find_all("a", href=True):
        href = urljoin(url, a["href"])
        href, _ = urldefrag(href)
        if href.startswith(("mailto:", "tel:", "javascript:")):
            continue
        if is_internal(href):
            links.add(norm_url(href))
    d["internal_links"] = sorted(links)

    d["word_count"] = word_count_main(soup)
    d["thin_content"] = d["word_count"] < THIN_CONTENT_WORDS

    videos = soup.find_all("video")
    d["video_count"] = len(videos)
    d["autoplay_video_count"] = sum(1 for v in videos if v.has_attr("autoplay"))
    d["embed_count"] = len(soup.find_all(
        "iframe", src=re.compile(r"youtube|youtu\.be|vimeo|wistia", re.I)))
    d["media_srcs"] = sorted(
        {i["src"] for i in images}
        | {urljoin(url, v.get("src") or (v.find("source") or {}).get("src", ""))
           for v in videos if v.get("src") or v.find("source")}
    )
    return d


def head_size(session, url, cache):
    if url in cache:
        return cache[url]
    size = None
    try:
        r = fetch(session, url, method="HEAD")
        cl = r.headers.get("content-length")
        if r.status_code == 405 or cl is None:
            r = fetch(session, url, method="GET", stream=True)
            cl = r.headers.get("content-length")
            r.close()
        size = int(cl) if cl else None
    except (requests.RequestException, ValueError):
        pass
    cache[url] = size
    return size


def check_link(session, url, cache):
    if url in cache:
        return cache[url]
    status = None
    try:
        r = fetch(session, url, method="HEAD")
        if r.status_code in (405, 403):
            r = fetch(session, url, method="GET", stream=True)
            r.close()
        status = r.status_code
    except requests.RequestException:
        status = 0  # connection failure
    cache[url] = status
    return status


# ---------------------------------------------------------------- Step 3 + 4

def sitewide_analysis(pages, link_status, media_sizes):
    a = {}
    ok_pages = [p for p in pages if p["status"] == 200]

    a["default_suffix_titles"] = [
        {"url": p["url"], "title": p["title"]}
        for p in ok_pages if DEFAULT_TITLE_SUFFIX.search(p["title"] or "")
    ]
    a["missing_titles"] = [p["url"] for p in ok_pages if not p["title"]]
    a["long_titles"] = [{"url": p["url"], "title": p["title"], "length": p["title_length"]}
                        for p in ok_pages if p["title_length"] > TITLE_MAX]
    a["missing_descriptions"] = [p["url"] for p in ok_pages if not p["meta_description"]]
    a["long_descriptions"] = [{"url": p["url"], "length": p["meta_desc_length"]}
                              for p in ok_pages if p["meta_desc_length"] > DESC_MAX]

    def dupes(field):
        groups = defaultdict(list)
        for p in ok_pages:
            v = p[field].strip()
            if v:
                groups[v].append(p["url"])
        return {k: v for k, v in groups.items() if len(v) > 1}

    a["duplicate_titles"] = dupes("title")
    a["duplicate_descriptions"] = dupes("meta_description")

    schema_counter = Counter()
    schema_by_page = {}
    for p in ok_pages:
        schema_by_page[p["url"]] = p["schema_types"]
        schema_counter.update(p["schema_types"])
    a["schema_type_counts"] = dict(schema_counter)
    a["schema_by_page"] = schema_by_page
    a["schema_missing_for_local_business"] = [
        t for t in ("LocalBusiness", "HealthClub", "Service", "FAQPage", "Review",
                    "AggregateRating")
        if t not in schema_counter
    ]

    sized = [(u, s) for u, s in media_sizes.items() if s]
    sized.sort(key=lambda x: -x[1])
    a["heaviest_media"] = [{"url": u, "kb": round(s / 1024)} for u, s in sized[:20]]
    a["media_over_300kb"] = [{"url": u, "kb": round(s / 1024)}
                             for u, s in sized if s > HEAVY_IMAGE_BYTES]

    a["broken_internal_links"] = []
    for p in pages:
        for l in p.get("internal_links", []):
            if link_status.get(l) in (404, 410):
                a["broken_internal_links"].append({"on_page": p["url"], "link": l,
                                                   "status": link_status[l]})
    a["redirect_chains"] = [{"url": p["url"], "chain": p["redirect_chain"]}
                            for p in pages if p["redirect_chain"]]
    a["error_pages"] = [{"url": p["url"], "status": p["status"]}
                        for p in pages if p["status"] >= 400]
    a["noindex_pages"] = [p["url"] for p in ok_pages if p["noindex"]]
    a["canonical_mismatches"] = [{"url": p["url"], "canonical": p["canonical"]}
                                 for p in ok_pages if p["canonical_mismatch"]]
    a["missing_canonical"] = [p["url"] for p in ok_pages if not p["canonical"]]
    a["multi_or_no_h1"] = [{"url": p["url"], "h1_count": p["h1_count"], "h1": p["h1_text"]}
                           for p in ok_pages if p["h1_count"] != 1]
    a["thin_pages"] = [{"url": p["url"], "words": p["word_count"]}
                       for p in ok_pages if p["thin_content"]]

    linked_to = set()
    for p in pages:
        for l in p.get("internal_links", []):
            if l.rstrip("/") != p["url"].rstrip("/"):
                linked_to.add(l.rstrip("/"))
    a["orphan_pages"] = [p["url"] for p in pages
                         if p["url"].rstrip("/") not in linked_to]
    return a


CSV_COLUMNS = [
    "url", "status", "redirect_chain", "noindex", "meta_robots",
    "title", "title_length", "meta_description", "meta_desc_length",
    "h1_count", "h1_text", "canonical", "canonical_mismatch",
    "images_total", "images_missing_alt", "images_junk_filename",
    "schema_types", "internal_links_count", "broken_links_on_page",
    "word_count", "thin_content", "video_count", "autoplay_video_count",
    "embed_count", "heavy_media_on_page", "heading_outline",
]


def write_csv(pages, link_status, media_sizes, path):
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        w.writeheader()
        for p in pages:
            broken = [l for l in p.get("internal_links", [])
                      if link_status.get(l) in (404, 410)]
            heavy = [u for u in p.get("media_srcs", [])
                     if (media_sizes.get(u) or 0) > HEAVY_IMAGE_BYTES]
            w.writerow({
                "url": p["url"], "status": p["status"],
                "redirect_chain": p.get("redirect_chain", ""),
                "noindex": p.get("noindex", ""), "meta_robots": p.get("meta_robots", ""),
                "title": p.get("title", ""), "title_length": p.get("title_length", ""),
                "meta_description": p.get("meta_description", ""),
                "meta_desc_length": p.get("meta_desc_length", ""),
                "h1_count": p.get("h1_count", ""), "h1_text": p.get("h1_text", ""),
                "canonical": p.get("canonical", ""),
                "canonical_mismatch": p.get("canonical_mismatch", ""),
                "images_total": p.get("images_total", ""),
                "images_missing_alt": p.get("images_missing_alt", ""),
                "images_junk_filename": p.get("images_junk_filename", ""),
                "schema_types": ", ".join(p.get("schema_types", [])),
                "internal_links_count": len(p.get("internal_links", [])),
                "broken_links_on_page": " | ".join(broken),
                "word_count": p.get("word_count", ""),
                "thin_content": p.get("thin_content", ""),
                "video_count": p.get("video_count", ""),
                "autoplay_video_count": p.get("autoplay_video_count", ""),
                "embed_count": p.get("embed_count", ""),
                "heavy_media_on_page": " | ".join(heavy),
                "heading_outline": p.get("heading_outline", ""),
            })


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pages", type=int, default=None,
                    help="limit crawl size (smoke testing)")
    ap.add_argument("--out-dir", default="reports",
                    help="where to write audit-data.csv / audit-raw.json")
    args = ap.parse_args()

    session = requests.Session()
    session.headers.update(HEADERS)

    print("== Step 1: discovery ==")
    rp, robots_sitemaps = load_robots(session)
    urls = discover_pages(session, robots_sitemaps)
    if not urls:
        print("No sitemap found — falling back to crawling from the homepage.")
        urls = [BASE + "/"]
    sitemap_urls = set(urls)
    print(f"\nTOTAL PAGES DISCOVERED: {len(urls)}\n")

    if args.max_pages:
        urls = urls[: args.max_pages]

    print("== Step 2: crawling ==")
    pages, queue, seen = [], list(urls), set(urls)
    while queue:
        url = queue.pop(0)
        if not rp.can_fetch(USER_AGENT, url):
            print(f"  SKIP (robots.txt disallow): {url}")
            continue
        try:
            r = fetch(session, url)
        except requests.RequestException as e:
            print(f"  ERROR {url}: {e}")
            pages.append({"url": url, "status": 0, "redirect_chain": "",
                          "error": str(e), "internal_links": [], "media_srcs": []})
            continue
        ct = r.headers.get("content-type", "")
        if r.status_code == 200 and "html" in ct:
            soup = BeautifulSoup(r.text, "html.parser")
            pages.append(analyze_page(url, r, soup))
        else:
            pages.append({"url": url, "status": r.status_code,
                          "redirect_chain": " -> ".join(
                              f"{h.status_code}:{h.url}" for h in r.history),
                          "internal_links": [], "media_srcs": []})
        print(f"  [{len(pages)}/{len(seen)}] {r.status_code} {url}")

    print("\n== Step 2b: media sizes + internal link checks ==")
    media_sizes, link_status = {}, {}
    all_media = sorted({m for p in pages for m in p.get("media_srcs", [])})
    print(f"  checking {len(all_media)} media files (HEAD, content-length)...")
    for m in all_media:
        head_size(session, m, media_sizes)
    crawled = {p["url"].rstrip("/") for p in pages}
    to_check = sorted({l for p in pages for l in p.get("internal_links", [])
                       if l.rstrip("/") not in crawled})
    for p in pages:
        link_status[p["url"]] = p["status"]
        link_status.setdefault(p["url"].rstrip("/"), p["status"])
    print(f"  checking {len(to_check)} internal links not in the page set...")
    for l in to_check:
        check_link(session, l, link_status)

    print("\n== Step 3: sitewide analysis ==")
    analysis = sitewide_analysis(pages, link_status, media_sizes)
    analysis["sitemap_page_count"] = len(sitemap_urls)
    analysis["crawled_page_count"] = len(pages)

    print("== Step 4: writing deliverables ==")
    out = args.out_dir.rstrip("/")
    os.makedirs(out, exist_ok=True)
    write_csv(pages, link_status, media_sizes, f"{out}/audit-data.csv")
    with open(f"{out}/audit-raw.json", "w", encoding="utf-8") as f:
        json.dump({"pages": pages, "analysis": analysis,
                   "link_status": link_status, "media_sizes": media_sizes},
                  f, indent=1, default=str)
    print(f"Wrote {out}/audit-data.csv and {out}/audit-raw.json")
    print("\nSummary:")
    for k in ("error_pages", "redirect_chains", "multi_or_no_h1", "thin_pages",
              "missing_descriptions", "duplicate_titles", "broken_internal_links",
              "orphan_pages", "noindex_pages", "media_over_300kb"):
        v = analysis[k]
        print(f"  {k}: {len(v)}")
    print(f"  schema types found: {analysis['schema_type_counts'] or 'NONE'}")


if __name__ == "__main__":
    sys.exit(main())
