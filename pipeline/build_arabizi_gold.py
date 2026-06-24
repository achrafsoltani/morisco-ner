#!/usr/bin/env python3
"""Build the Arabizi NER gold test set from the native-validated review CSV.
Final entities per row = column C4 (CORRECTION) if non-empty, else C3 (predicted). 'NONE' -> no entities.
Map each entity string to a verbatim token span in C1 (arabizi); case-insensitive fallback. Run from the repo root.
Usage: python scripts/build_arabizi_gold.py  ->  data/arabizi_gold.jsonl"""
import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "arabizi_draft_review.csv"
OUT = ROOT / "data" / "arabizi_gold.jsonl"
# 2 native-typed romanisation typos -> verbatim form present in the sentence (intent unambiguous).
FIX = {"talyania": "talyaniya", "nasi7ia": "masi7ia"}


def parse_ents(cell):
    cell = (cell or "").strip()
    if not cell or cell.upper() == "NONE":
        return []
    out = []
    for item in cell.split(";"):
        item = item.strip().replace("(?)", "")
        m = re.match(r"^(.*)\[(PER|LOC|ORG|MISC)\]\s*$", item)
        if m:
            out.append((m.group(1).strip(), m.group(2)))
    return out


def tok_offsets(text):
    toks, offs, pos = text.split(), [], 0
    for t in toks:
        i = text.find(t, pos); offs.append((i, i + len(t))); pos = i + len(t)
    return toks, offs


def to_span(text, offs, ent):
    idx = text.lower().find(ent.lower())
    if idx < 0:
        return None
    s, e = idx, idx + len(ent)
    cov = [i for i, (a, b) in enumerate(offs) if a < e and s < b]
    return [cov[0], cov[-1]] if cov else None


def main():
    rows = list(csv.reader(open(CSV, encoding="utf-8")))[1:]
    gold, nent, types = [], 0, Counter()
    for r in rows:
        ar = r[0]
        c3 = r[2] if len(r) > 2 else ""
        c4 = r[3] if len(r) > 3 else ""
        ents = parse_ents(c4) if (c4 or "").strip() else parse_ents(c3)
        toks, offs = tok_offsets(ar)
        spans = []
        for txt, typ in ents:
            sp = to_span(ar, offs, FIX.get(txt, txt))
            if sp:
                spans.append(sp + [typ]); types[typ] += 1; nent += 1
        gold.append({"tokens": toks, "spans": spans})
    with open(OUT, "w", encoding="utf-8") as f:
        for g in gold:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")
    print(f"{len(gold)} sentences | {sum(1 for g in gold if g['spans'])} with entities | {nent} entities | {dict(types)}")


if __name__ == "__main__":
    main()
