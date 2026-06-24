#!/usr/bin/env python3
"""Convert annotated batch CSV(s) -> {tokens, spans, comment_id} jsonl (the Arabizi NER training format).
Final entities per row = column CORRECTION (C3) if non-empty, else predicted_entities (C2). 'NONE' -> no entities.
Map each entity verbatim to a token span. Usage: batch_to_jsonl.py batch_01.csv [batch_02.csv ...] --out train.jsonl"""
import argparse
import csv
import json
import re
from collections import Counter


def parse_ents(cell):
    cell = (cell or "").strip()
    if not cell or cell.upper() == "NONE":
        return []
    out = []
    # split on ';' OR a ',' that directly follows a ']' (annotators sometimes comma-separate
    # tagged entities, e.g. "WAC[ORG], bidawa[MISC]" -> two entities, not one mangled span).
    for item in re.split(r"\s*;\s*|(?<=\])\s*,\s*", cell):
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
    ap = argparse.ArgumentParser()
    ap.add_argument("csvs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--source", choices=["correction", "predicted"], default="correction",
                    help="'correction' = C3 else C2 (annotated); 'predicted' = C2 only (teacher draft, for dry-run)")
    a = ap.parse_args()
    rows_out, types, nent, unmatched = [], Counter(), 0, 0
    for path in a.csvs:
        rd = list(csv.reader(open(path, encoding="utf-8")))[1:]
        for r in rd:
            ar = r[0]
            c2 = r[1] if len(r) > 1 else ""
            c3 = r[2] if len(r) > 2 else ""
            cid = r[3] if len(r) > 3 else ""
            if a.source == "predicted":
                ents = parse_ents(c2)
            else:
                ents = parse_ents(c3) if (c3 or "").strip() else parse_ents(c2)
            toks, offs = tok_offsets(ar)
            spans = []
            for txt, typ in ents:
                sp = to_span(ar, offs, txt)
                if sp:
                    spans.append(sp + [typ]); types[typ] += 1; nent += 1
                else:
                    unmatched += 1
            rows_out.append({"tokens": toks, "spans": spans, "comment_id": cid})
    with open(a.out, "w", encoding="utf-8") as f:
        for r in rows_out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    we = sum(1 for r in rows_out if r["spans"])
    print(f"{len(rows_out)} sentences | {we} with entities | {nent} entities {dict(types)} | {unmatched} unmatched -> {a.out}")


if __name__ == "__main__":
    main()
