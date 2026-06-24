#!/usr/bin/env python3
"""Collect organic Moroccan Darija ARABIZI (Latin-script) comments via the YouTube Data API v3.
Stand-off friendly: stores {text, comment_id, video_id} only (NO author identities). Filters to Latin-Darija.
Key: read from env YOUTUBE_API_KEY or from ./.yt_key (one line). Output yt_comments.jsonl.
Quota note: search.list=100 units, commentThreads.list=1 unit; free quota 10,000/day → plenty for ~15K comments."""
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
API = "https://www.googleapis.com/youtube/v3"
OUT = HERE / "yt_comments.jsonl"
TARGET = 15000

KEY = os.environ.get("YOUTUBE_API_KEY") or (HERE / ".yt_key").read_text().strip() if (HERE / ".yt_key").exists() else os.environ.get("YOUTUBE_API_KEY")

# Entity-rich Moroccan topics (Arabic/French queries find the videos; comments are where the Arabizi lives).
SEARCH_QUERIES = [
    "اخبار المغرب", "actualité maroc", "الرجاء البيضاوي", "الوداد الرياضي", "المنتخب المغربي اليوم",
    "سياسة المغرب", "برلمان المغرب", "حوار مع", "مقابلة المغرب", "ماتش المنتخب المغربي",
    "اخنوش", "حكومة المغرب", "مهرجان موازين", "كأس افريقيا المغرب", "خبر عاجل المغرب",
]
DARIJA_WORDS = {"wach", "dyal", "bzaf", "bzzaf", "kayn", "ghadi", "ghadya", "hna", "walakin", "dial", "kima",
                "khoya", "wlah", "nta", "nti", "7na", "3lach", "fin", "kifach", "b7al", "daba", "ghir",
                "mzyan", "makayn", "chwiya", "rah", "lik", "lia", "3ndi", "3ndo", "had", "dak", "hadchi"}


def get(endpoint, **params):
    params["key"] = KEY
    url = f"{API}/{endpoint}?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def latin_darija(t):
    toks = t.split()
    if not (4 <= len(toks) <= 40):
        return False
    letters = re.sub(r"[^A-Za-z؀-ۿ]", "", t)
    if len(letters) < 6:
        return False
    latin = sum(1 for c in letters if c.isascii() and c.isalpha())
    if latin / len(letters) < 0.85:        # mostly Latin script
        return False
    words = set(t.lower().split())
    return bool(re.search(r"[379]", t)) or bool(words & DARIJA_WORDS)   # Arabizi digit or a Darija word


def main():
    assert KEY, "No API key — set YOUTUBE_API_KEY or create ./.yt_key"
    vids = []
    for q in SEARCH_QUERIES:
        try:
            r = get("search", q=q, part="id", type="video", regionCode="MA", maxResults=50, order="relevance")
            vids += [it["id"]["videoId"] for it in r.get("items", []) if it["id"].get("videoId")]
        except Exception as e:
            print("search err", q, str(e)[:90])
    vids = list(dict.fromkeys(vids))
    print(f"{len(vids)} videos found")
    seen, out = set(), []
    for vid in vids:
        if len(out) >= TARGET:
            break
        page = None
        for _ in range(8):
            try:
                kw = {"pageToken": page} if page else {}
                r = get("commentThreads", part="snippet", videoId=vid, maxResults=100, textFormat="plainText", **kw)
            except Exception:
                break
            for it in r.get("items", []):
                sn = it["snippet"]["topLevelComment"]["snippet"]
                txt = re.sub(r"\s+", " ", sn.get("textDisplay", "")).strip()
                cid = it["snippet"]["topLevelComment"]["id"]
                if cid not in seen and latin_darija(txt):
                    seen.add(cid)
                    out.append({"text": txt, "comment_id": cid, "video_id": vid})
            page = r.get("nextPageToken")
            if not page or len(out) >= TARGET:
                break
        print(f"  {len(out)} Latin-Darija comments so far", flush=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"=> {len(out)} comments -> {OUT}")


if __name__ == "__main__":
    main()
