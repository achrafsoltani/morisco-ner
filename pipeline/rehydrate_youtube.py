#!/usr/bin/env python3
"""Re-hydrate the stand-off MoriscoNER files into token-level JSONL.

The corpus is released stand-off: each record carries the YouTube comment id, the number of tokens, a SHA-1
of the space-joined tokens, and the entity spans (token indices, inclusive) -- never the comment text, which
YouTube's terms and the GDPR do not allow us to redistribute. This script fetches each comment's text with
your own YouTube Data API v3 key, rebuilds the tokens exactly as the collection pipeline did (plain-text
textDisplay, whitespace collapsed, URLs removed, split on whitespace), checks them against the stored count
and hash, and writes {"tokens", "spans", "comment_id"} records.

Comments deleted or edited since collection cannot be recovered; they are reported and skipped.
Quota: one comments.list call (1 unit) per 50 comments, about 63 units for the whole corpus.

Usage:
  YT_API_KEY=... python pipeline/rehydrate_youtube.py data/arabizi_native_full.standoff.jsonl \
      data/arabizi_native_full.jsonl
  python pipeline/rehydrate_youtube.py IN OUT --raw my_comments.jsonl   # offline: {"comment_id", "text"} lines
"""
import argparse
import hashlib
import json
import os
import re
import sys
import urllib.parse
import urllib.request

API = "https://www.googleapis.com/youtube/v3/comments"


def to_tokens(text_display):
    t = re.sub(r"\s+", " ", text_display).strip()
    t = re.sub(r"http\S+", " ", t)
    return re.sub(r"\s+", " ", t).strip().split()


def sha1(tokens):
    return hashlib.sha1(" ".join(tokens).encode("utf-8")).hexdigest()


def fetch(ids, key):
    texts = {}
    for i in range(0, len(ids), 50):
        q = urllib.parse.urlencode({"part": "snippet", "id": ",".join(ids[i:i + 50]),   # no maxResults with id
                                    "textFormat": "plainText", "key": key})
        with urllib.request.urlopen(f"{API}?{q}", timeout=30) as r:
            for it in json.load(r).get("items", []):
                texts[it["id"]] = it["snippet"].get("textDisplay", "")
    return texts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("standoff")
    ap.add_argument("out")
    ap.add_argument("--raw", help="offline source: JSONL with comment_id and text (plain-text textDisplay)")
    a = ap.parse_args()
    recs = [json.loads(l) for l in open(a.standoff, encoding="utf-8")]
    ids = sorted({r["comment_id"] for r in recs})
    if a.raw:
        texts = {}
        for line in open(a.raw, encoding="utf-8"):
            d = json.loads(line)
            texts.setdefault(d["comment_id"], d["text"])
    else:
        key = os.environ.get("YT_API_KEY")
        if not key:
            sys.exit("set YT_API_KEY to a YouTube Data API v3 key, or pass --raw")
        texts = fetch(ids, key)
    ok = missing = changed = 0
    with open(a.out, "w", encoding="utf-8") as f:
        for r in recs:
            if r["comment_id"] not in texts:
                missing += 1
                continue
            toks = to_tokens(texts[r["comment_id"]])
            if len(toks) != r["n_tokens"] or sha1(toks) != r["text_sha1"]:
                changed += 1
                continue
            out = {"tokens": toks, "spans": r["spans"], "comment_id": r["comment_id"]}
            if "id" in r:
                out["id"] = r["id"]
            f.write(json.dumps(out, ensure_ascii=False) + "\n")
            ok += 1
    print(f"{a.standoff}: {ok} re-hydrated, {missing} unavailable (deleted or private), "
          f"{changed} changed since collection (skipped)")


if __name__ == "__main__":
    main()
