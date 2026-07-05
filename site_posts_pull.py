#!/usr/bin/env python3
"""site_posts_pull.py - pull latest essays from The Data Muse (Substack RSS) into
posts.json, so the website's Writing section markets the newest posts automatically.

Deterministic: reads the real RSS feed; writes only what the feed contains (no
invented titles). Safe to run on a schedule. After running, call build_site.py.

Usage: python3 site_posts_pull.py [--limit N]
"""
import datetime
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
POSTS = os.path.join(HERE, "posts.json")


def _feed_url():
    try:
        c = json.load(open(os.path.join(HERE, "content.json"), encoding="utf-8"))
        base = c["brand"]["substack"].rstrip("/")
    except Exception:
        base = "https://thedatamuse.substack.com"
    return base + "/feed"


def _clean(txt, n=180):
    txt = re.sub(r"<[^>]+>", "", txt or "")
    txt = re.sub(r"\s+", " ", txt).strip()
    return (txt[: n - 1] + "\u2026") if len(txt) > n else txt


def _fmt_date(s):
    for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z"):
        try:
            return datetime.datetime.strptime(s, fmt).strftime("%d %b %Y")
        except Exception:
            continue
    return ""


def pull(limit=6):
    url = _feed_url()
    req = urllib.request.Request(url, headers={"User-Agent": "openclaw-site/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        xml = r.read()
    root = ET.fromstring(xml)
    posts = []
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = item.findtext("description") or ""
        pub = item.findtext("pubDate") or ""
        if title and link:
            posts.append({"title": title, "url": link,
                          "blurb": _clean(desc), "date": _fmt_date(pub)})
        if len(posts) >= limit:
            break
    data = {"updated": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "posts": posts}
    tmp = POSTS + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp, POSTS)
    print(f"pulled {len(posts)} post(s) from {url}")


def main():
    limit = 6
    a = sys.argv[1:]
    if "--limit" in a:
        try:
            limit = int(a[a.index("--limit") + 1])
        except Exception:
            pass
    try:
        pull(limit)
    except Exception as e:  # noqa: BLE001
        print(f"posts pull failed (leaving posts.json unchanged): {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
