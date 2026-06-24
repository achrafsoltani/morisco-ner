#!/usr/bin/env python3
"""Teacher NER (Sonnet/Bedrock) on token-lists (Moroccan Darija, Arabic script OR Arabizi). Maps verbatim entity
strings to TOKEN spans. Threaded. Input jsonl: {tokens:[...], spans?:[[s,e,t]]}. Output jsonl: same + "pred":[[s,e,t]].
Usage: teacher_ner.py --input X.jsonl --out Y.jsonl [--limit N --workers 6]"""
import argparse
import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from anthropic import AnthropicBedrock

MODEL = "eu.anthropic.claude-sonnet-4-6"
REGION = "eu-west-1"
TYPES = {"LOC", "MISC", "ORG", "PER"}
PROMPT = """You annotate Moroccan Darija named entities (4 types). PER: persons. LOC: locations (cities, countries, places).
ORG: organisations, companies, brands, teams, institutions. MISC: other proper nouns (events, nationalities, languages, products, works).
Tag ONLY clear PROPER-NOUN named entities; NOT common nouns, days of the week, generic time words, pronouns, or plain adjectives.
Return ONLY a JSON array of {"text": <substring copied VERBATIM from the sentence>, "type": <PER|LOC|ORG|MISC>}. If none, [].
Sentence: «%s»
JSON:"""

_cost = {"in": 0, "out": 0}
_lock = threading.Lock()


def offsets(tokens):
    text, offs = "", []
    for i, t in enumerate(tokens):
        if i:
            text += " "
        s = len(text); text += t; offs.append((s, len(text)))
    return text, offs


def to_span(offs, cs, ce):
    idx = [i for i, (s, e) in enumerate(offs) if s < ce and cs < e]
    return [idx[0], idx[-1]] if idx else None


def label(client, tokens):
    text, offs = offsets(tokens)
    msg = client.messages.create(model=MODEL, max_tokens=1024, temperature=0,
                                 messages=[{"role": "user", "content": PROMPT % text}])
    with _lock:
        _cost["in"] += msg.usage.input_tokens; _cost["out"] += msg.usage.output_tokens
    m = re.search(r"\[.*\]", msg.content[0].text, re.S)
    ents = json.loads(m.group(0)) if m else []
    spans = []
    for e in ents:
        t, typ = str(e.get("text", "")), str(e.get("type", ""))
        if typ not in TYPES or not t:
            continue
        idx = text.find(t)
        if idx < 0:
            continue
        ts = to_span(offs, idx, idx + len(t))
        if ts:
            spans.append(ts + [typ])
    return spans


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0); ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    client = AnthropicBedrock(aws_region=REGION)
    rows = [json.loads(l) for l in open(a.input, encoding="utf-8")]
    if a.limit:
        rows = rows[:a.limit]
    out = [None] * len(rows); done = [0]

    def work(i):
        try:
            pred = label(client, rows[i]["tokens"])
        except Exception:
            pred = []
        r = dict(rows[i]); r["pred"] = pred; out[i] = r
        with _lock:
            done[0] += 1
            if done[0] % 100 == 0:
                print(f"  {done[0]}/{len(rows)}", flush=True)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        list(ex.map(work, range(len(rows))))
    with open(a.out, "w", encoding="utf-8") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"labelled {len(out)} → {a.out} | ~${_cost['in']/1e6*3 + _cost['out']/1e6*15:.2f}")


if __name__ == "__main__":
    main()
