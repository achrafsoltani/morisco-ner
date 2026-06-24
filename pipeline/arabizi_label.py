#!/usr/bin/env python3
"""Teacher pre-annotation of Arabizi Darija sentences for NER (PER/LOC/ORG/MISC), producing a DRAFT for the
native author to validate. Spans are returned verbatim and offset-grounded (found in the text). Sonnet via Bedrock.
Output: arabizi_draft.json (machine) + arabizi_draft_review.csv (human review). Usage: arabizi_label.py [--limit N]"""
import argparse
import csv
import json
import re
from pathlib import Path

from anthropic import AnthropicBedrock

HERE = Path(__file__).parent
MODEL = "eu.anthropic.claude-sonnet-4-6"
REGION = "eu-west-1"

PROMPT = """You annotate Moroccan Darija written in Arabizi (Latin script; numerals 3=ع 7=ح 9=ق 2=ء/glottal).
Extract named entities of EXACTLY these 4 types:
- PER: person names
- LOC: locations (cities, countries, neighbourhoods, places)
- ORG: organisations, companies, brands, institutions, teams
- MISC: other proper-noun entities (events, nationalities, languages, products, works)
Tag ONLY clear PROPER-NOUN named entities. Do NOT tag common nouns, days of the week (sebt, tlat, lhad...),
generic time words (yawmia, l3otla...), pronouns, or plain adjectives.
Return ONLY a JSON array of {"text": <substring copied VERBATIM from the sentence>, "type": <PER|LOC|ORG|MISC>}.
Do not translate or re-spell; copy exactly. If there are no named entities, return [].
Sentence: «%s»
JSON:"""


def label(client, s):
    msg = client.messages.create(model=MODEL, max_tokens=1024, temperature=0,
                                 messages=[{"role": "user", "content": PROMPT % s}])
    txt = msg.content[0].text.strip()
    m = re.search(r"\[.*\]", txt, re.S)
    ents = json.loads(m.group(0)) if m else []
    out = []
    for e in ents:
        t = str(e.get("text", "")); typ = str(e.get("type", ""))
        idx = s.find(t)
        out.append({"text": t, "type": typ, "start": idx, "end": idx + len(t) - 1 if idx >= 0 else -1,
                    "grounded": idx >= 0})
    return out, msg.usage


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--limit", type=int, default=400); a = ap.parse_args()
    client = AnthropicBedrock(aws_region=REGION)
    rows = [json.loads(l) for l in open(HERE / "arabizi_candidates.jsonl", encoding="utf-8")][:a.limit]
    out, nent, ti, to = [], 0, 0, 0
    for i, r in enumerate(rows):
        try:
            ents, u = label(client, r["arabizi"])
            nent += len(ents); ti += u.input_tokens; to += u.output_tokens
            out.append({**r, "entities": ents})
        except Exception as e:
            out.append({**r, "entities": [], "err": str(e)[:140]})
        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{len(rows)} | {nent} ents", flush=True)
    json.dump(out, open(HERE / "arabizi_draft.json", "w"), ensure_ascii=False, indent=1)
    cost = ti / 1e6 * 3 + to / 1e6 * 15
    print(f"\nlabelled {len(out)} | {nent} entities | ~${cost:.2f} (in {ti} out {to})")
    with open(HERE / "arabizi_draft_review.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f); w.writerow(["arabizi", "english", "predicted_entities", "CORRECTION (edit here)"])
        for r in out:
            es = "; ".join(f"{e['text']}[{e['type']}]" + ("" if e["grounded"] else "(?)") for e in r["entities"])
            w.writerow([r["arabizi"], r["eng"], es, ""])
    print("wrote arabizi_draft.json + arabizi_draft_review.csv")


if __name__ == "__main__":
    main()
