#!/usr/bin/env python3
"""Scrape a public Telegram channel via its t.me/s/ web preview.

No API key or account needed. Emits JSON with posts plus a precomputed stats
block so the caller doesn't have to recompute the obvious aggregates.
"""
import argparse, html, json, re, sys, time, urllib.request, urllib.error
from collections import Counter

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"


def fetch(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(2 * (i + 1))


def strip_tags(s):
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"</p>", "\n", s)
    return html.unescape(re.sub(r"<[^>]+>", "", s)).strip()


def to_int(s):
    """'1.59K' -> 1590. Telegram abbreviates view counts."""
    if not s:
        return None
    s = s.strip().replace(",", "")
    try:
        if s.endswith("K"):
            return int(float(s[:-1]) * 1_000)
        if s.endswith("M"):
            return int(float(s[:-1]) * 1_000_000)
        return int(s)
    except ValueError:
        return None


def parse_channel_meta(page):
    def grab(pat):
        m = re.search(pat, page, re.S)
        return strip_tags(m.group(1)) if m else None

    meta = {
        "title": grab(r'tgme_header_title"[^>]*>(.*?)</div>')
        or grab(r'tgme_channel_info_header_title"[^>]*>(.*?)</div>'),
        "username": grab(r'tgme_channel_info_header_username"[^>]*>(.*?)</div>'),
        "description": grab(r'tgme_channel_info_description"[^>]*>(.*?)</div>'),
    }
    for val, typ in re.findall(r'counter_value">([^<]*)</span>\s*<span class="counter_type">([^<]*)', page):
        meta[typ.strip()] = val.strip()
    return meta


def parse_posts(page):
    posts = []
    for b in re.split(r'(?=<div class="tgme_widget_message[ "])', page):
        m = re.search(r'data-post="([^"/]+)/(\d+)"', b)
        if not m:
            continue
        # The text div closes at the FIRST </div> — the reaction bar and the
        # "Please open Telegram to view this post" interstitial are siblings that
        # follow it, so a greedy match would pull them into the body and corrupt
        # the char and emoji counts.
        body = re.search(r'js-message_text"[^>]*>(.*?)</div>', b, re.S)
        text = strip_tags(body.group(1)) if body else ""
        dt = re.search(r'datetime="([^"]+)"', b)
        views = re.search(r'message_views">([^<]*)', b)

        reactions = {}
        for emo, cnt in re.findall(r'tgme_reaction"[^>]*>.*?<b>([^<]*)</b></i>\s*([\d.KM]+)', b, re.S):
            reactions[emo] = to_int(cnt) or 0

        links = [l for l in re.findall(r'href="(https?://[^"]+)"', b)
                 if "telegram.org" not in l and f"/{m.group(1)}" not in l]

        posts.append({
            "id": int(m.group(2)),
            "url": f"https://t.me/{m.group(1)}/{m.group(2)}",
            "date": dt.group(1) if dt else None,
            "views": to_int(views.group(1)) if views else None,
            "views_raw": views.group(1).strip() if views else None,
            "text": text,
            "chars": len(text),
            "has_photo": "tgme_widget_message_photo_wrap" in b,
            "has_video": "tgme_widget_message_video" in b,
            "is_forwarded": "message_forwarded_from" in b,
            "reactions": reactions,
            "reactions_total": sum(reactions.values()),
            "external_links": sorted(set(links)),
            "emojis": re.findall(r"[\U0001F300-\U0001FAFF☀-➿]", text),
        })
    return posts


def compute_stats(posts):
    if not posts:
        return {}
    dated = [p for p in posts if p["date"]]
    days = 0
    if len(dated) > 1:
        from datetime import datetime
        fmt = lambda s: datetime.fromisoformat(s.replace("Z", "+00:00"))
        days = max((fmt(dated[-1]["date"]) - fmt(dated[0]["date"])).total_seconds() / 86400, 0.01)

    views = sorted(p["views"] for p in posts if p["views"])
    chars = sorted(p["chars"] for p in posts if p["chars"])
    med = lambda a: a[len(a) // 2] if a else None

    domains = Counter()
    for p in posts:
        for l in p["external_links"]:
            domains[re.sub(r"https?://(www\.)?([^/]+).*", r"\2", l)] += 1

    return {
        "post_count": len(posts),
        "date_from": dated[0]["date"] if dated else None,
        "date_to": dated[-1]["date"] if dated else None,
        "span_days": round(days, 2),
        "posts_per_day": round(len(posts) / days, 2) if days else None,
        "median_views": med(views),
        "min_views": views[0] if views else None,
        "max_views": views[-1] if views else None,
        "median_chars": med(chars),
        "max_chars": chars[-1] if chars else None,
        "pct_with_photo": round(100 * sum(p["has_photo"] for p in posts) / len(posts), 1),
        "pct_with_video": round(100 * sum(p["has_video"] for p in posts) / len(posts), 1),
        "pct_text_only": round(100 * sum(not (p["has_photo"] or p["has_video"]) for p in posts) / len(posts), 1),
        "pct_forwarded": round(100 * sum(p["is_forwarded"] for p in posts) / len(posts), 1),
        "posts_with_external_links": sum(1 for p in posts if p["external_links"]),
        "top_link_domains": domains.most_common(20),
        "hour_histogram_utc": sorted(Counter(int(p["date"][11:13]) for p in dated).items()),
        "top_emojis": Counter(e for p in posts for e in p["emojis"]).most_common(25),
        "median_emojis_per_post": med(sorted(len(p["emojis"]) for p in posts)),
        "top_reactions": Counter({k: v for p in posts for k, v in p["reactions"].items()}).most_common(15),
        "median_reactions": med(sorted(p["reactions_total"] for p in posts)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("channel", help="t.me link or bare @username")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--out", default="telegram_data.json")
    a = ap.parse_args()

    name = re.sub(r"^@", "", re.sub(r"https?://t\.me/(s/)?", "", a.channel.strip()).split("/")[0])

    first = fetch(f"https://t.me/s/{name}")
    meta = parse_channel_meta(first)
    if not meta.get("title"):
        sys.exit(f"ERROR: could not read channel '{name}'. It may be private, nonexistent, or have no public preview.")

    seen, cursor = {}, None
    while len(seen) < a.limit:
        page = first if cursor is None else fetch(f"https://t.me/s/{name}?before={cursor}")
        batch = parse_posts(page)
        if not batch:
            break
        new = [p for p in batch if p["id"] not in seen]
        for p in batch:
            seen[p["id"]] = p
        print(f"  fetched {len(batch)}, total {len(seen)}", file=sys.stderr)
        if not new:
            break
        cursor = min(p["id"] for p in batch)
        time.sleep(1)

    posts = sorted(seen.values(), key=lambda p: p["id"])[-a.limit:]
    out = {"channel": meta, "stats": compute_stats(posts), "posts": posts}
    json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(json.dumps({"channel": meta, "stats": out["stats"]}, ensure_ascii=False, indent=1))
    print(f"\nSaved {len(posts)} posts -> {a.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
