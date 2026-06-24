#!/usr/bin/env python3
"""Expanded APPEND collection pass. Many more Moroccan entity-rich queries + more comment pages/video.
Appends NEW Latin-Darija comments to yt_comments.jsonl (dedup by comment_id vs existing). Reads key from ./.yt_key."""
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path("/home/achraf/Documents/Lab/darija-llm-ner-gonogo")
API = "https://www.googleapis.com/youtube/v3"
OUT = HERE / "yt_comments.jsonl"
KEY = (HERE / ".yt_key").read_text().strip()
MAX_PAGES = 12

QUERIES = [
    "le360 المغرب", "هسبريس اخبار", "ميديا24", "chouf tv maroc", "febrayer tv", "الأولى المغرب نشرة",
    "medi1 tv المغرب", "goud المغرب", "البطولة الاحترافية المغربية", "ديربي الرجاء الوداد",
    "حسنية اكادير", "الفتح الرباطي", "أسود الأطلس مباراة", "وليد الركراكي", "حكيم زياش", "أشرف حكيمي",
    "سفيان بوفال", "اخنوش الحكومة", "مجلس النواب المغرب", "وزير الداخلية المغرب", "الدار البيضاء",
    "مراكش", "فاس المدينة", "طنجة", "اكادير", "وجدة", "مهرجان موازين", "مهرجان تيميتار", "كأس العرش",
    "كان 2025 المغرب", "حوار مع فنان مغربي", "برنامج مغربي", "بودكاست مغربي",
]
DARIJA_WORDS = {"wach", "dyal", "bzaf", "bzzaf", "kayn", "ghadi", "ghadya", "hna", "walakin", "dial", "kima",
                "khoya", "wlah", "nta", "nti", "7na", "3lach", "fin", "kifach", "b7al", "daba", "ghir",
                "mzyan", "makayn", "chwiya", "rah", "lik", "lia", "3ndi", "3ndo", "had", "dak", "hadchi"}


def get(endpoint, **params):
    params["key"] = KEY
    with urllib.request.urlopen(f"{API}/{endpoint}?" + urllib.parse.urlencode(params), timeout=30) as r:
        return json.load(r)


def latin_darija(t):
    toks = t.split()
    if not (4 <= len(toks) <= 40):
        return False
    letters = re.sub(r"[^A-Za-z؀-ۿ]", "", t)
    if len(letters) < 6:
        return False
    latin = sum(1 for c in letters if c.isascii() and c.isalpha())
    if latin / len(letters) < 0.85:
        return False
    words = set(t.lower().split())
    return bool(re.search(r"[379]", t)) or bool(words & DARIJA_WORDS)


def main():
    seen = set()
    if OUT.exists():
        for l in open(OUT, encoding="utf-8"):
            seen.add(json.loads(l)["comment_id"])
    print(f"existing pool: {len(seen)} comments")
    vids = []
    for q in QUERIES:
        try:
            r = get("search", q=q, part="id", type="video", regionCode="MA", maxResults=50, order="relevance")
            vids += [it["id"]["videoId"] for it in r.get("items", []) if it["id"].get("videoId")]
        except Exception as e:
            print("search err", q, str(e)[:80])
    vids = list(dict.fromkeys(vids))
    print(f"{len(vids)} videos")
    added = 0
    f = open(OUT, "a", encoding="utf-8")
    for vid in vids:
        page = None
        for _ in range(MAX_PAGES):
            try:
                kw = {"pageToken": page} if page else {}
                r = get("commentThreads", part="snippet", videoId=vid, maxResults=100, textFormat="plainText", **kw)
            except Exception:
                break
            for it in r.get("items", []):
                sn = it["snippet"]["topLevelComment"]["snippet"]
                cid = it["snippet"]["topLevelComment"]["id"]
                txt = re.sub(r"\s+", " ", sn.get("textDisplay", "")).strip()
                if cid not in seen and latin_darija(txt):
                    seen.add(cid); added += 1
                    f.write(json.dumps({"text": txt, "comment_id": cid, "video_id": vid}, ensure_ascii=False) + "\n")
            page = r.get("nextPageToken")
            if not page:
                break
        f.flush()
        print(f"  +{added} new (pool {len(seen)})", flush=True)
    f.close()
    print(f"=> added {added} new Latin-Darija comments; pool now {len(seen)}")


if __name__ == "__main__":
    main()
