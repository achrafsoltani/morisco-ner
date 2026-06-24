#!/usr/bin/env python3
"""Teacher pre-annotation (DRAFT) of Arabizi candidates for NER -> annotation worksheet CSV.

Reads a candidates JSONL (records with "text" + "source_id"), labels each via Claude on Bedrock, and writes a batch
CSV in the established annotation format:  arabizi,predicted_entities,CORRECTION,comment_id
(CORRECTION left blank for the native annotator to fill — the review-and-correct workflow). `batch_to_jsonl.py` then
converts the filled batch to the {tokens,spans} training format.

  python pipeline/teacher_draft.py --in candidates/deduped.jsonl --out annotation/batch_06.csv --limit 700 [--offset 0] [--haiku]

Cost (approx): Sonnet $3/$15 per M tok (~$1 / 700 short comments); Haiku $1/$5 (~$0.35 / 700). Bedrock, eu-west-1.
"""
import argparse
import csv
import json
import re
import sys
from pathlib import Path

from anthropic import AnthropicBedrock

REGION = "eu-west-1"
SONNET = "eu.anthropic.claude-sonnet-4-6"
HAIKU = "eu.anthropic.claude-haiku-4-5"

PROMPT = """You annotate Moroccan Darija written in Arabizi (Latin script; numerals 3=ع 7=ح 9=ق 2=ء/glottal).
Extract named entities of EXACTLY these 4 types:
- PER: person names
- LOC: locations (cities, countries, neighbourhoods, places)
- ORG: organisations, companies, brands, institutions, teams
- MISC: other proper-noun entities (events, nationalities, languages, products, works)
Tag ONLY clear PROPER-NOUN named entities. Do NOT tag common nouns, days of the week (sebt, tlat, lhad...),
generic time words, pronouns, or plain adjectives. Binding rule: anything cultural/ethnic/religious -> MISC,
including religious figures (Allah / Lah -> MISC, NOT PER, NOT O).
Return ONLY a JSON array of {"text": <substring copied VERBATIM from the sentence>, "type": <PER|LOC|ORG|MISC>}.
Copy exactly; do not translate or re-spell. If there are no named entities, return [].
Sentence: «%s»
JSON:"""


def label(client, model, s):
    msg = client.messages.create(model=model, max_tokens=512, temperature=0,
                                 messages=[{"role": "user", "content": PROMPT % s}])
    txt = msg.content[0].text.strip()
    m = re.search(r"\[.*\]", txt, re.S)
    ents = json.loads(m.group(0)) if m else []
    out = []
    for e in ents:
        t = str(e.get("text", "")).strip()
        typ = str(e.get("type", "")).strip()
        if t and typ in ("PER", "LOC", "ORG", "MISC"):
            out.append((t, typ, s.lower().find(t.lower()) >= 0))
    return out, msg.usage


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=700)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--haiku", action="store_true", help="use Haiku (cheaper) instead of Sonnet")
    a = ap.parse_args()
    model = HAIKU if a.haiku else SONNET
    client = AnthropicBedrock(aws_region=REGION)
    rows = [json.loads(l) for l in open(a.inp, encoding="utf-8")][a.offset:a.offset + a.limit]
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    ti = to = nent = errs = 0
    with open(a.out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["arabizi", "predicted_entities", "CORRECTION", "comment_id"])
        for i, r in enumerate(rows):
            s = r["text"]
            try:
                ents, u = label(client, model, s)
                ti += u.input_tokens; to += u.output_tokens; nent += len(ents)
                pe = "; ".join(f"{t}[{ty}]" + ("" if g else "(?)") for t, ty, g in ents) or "NONE"
            except Exception as e:  # noqa: BLE001
                pe = ""; errs += 1
                print(f"  err {i}: {str(e)[:120]}", file=sys.stderr)
            w.writerow([s, pe, "", r.get("source_id", "")])
            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{len(rows)} | {nent} ents | {errs} errs", flush=True)
    r0, r1 = (1, 5) if a.haiku else (3, 15)
    cost = ti / 1e6 * r0 + to / 1e6 * r1
    print(f"drafted {len(rows)} -> {a.out} | {nent} entities | {errs} errors | "
          f"~${cost:.2f} ({'Haiku' if a.haiku else 'Sonnet'}; in {ti} out {to})")


if __name__ == "__main__":
    main()
