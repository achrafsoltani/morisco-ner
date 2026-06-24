#!/usr/bin/env python3
"""Rough offensive-content + privacy audit of the MoriscoNER CSVs (scoping, NOT a validated toxicity classifier).
Flags reviewed rows containing common Moroccan-Darija/Arabizi + FR + EN insult/slur markers, reports prevalence, and
extracts PER entities that occur in offensive rows (the privacy-sensitive cases: named individuals in insulting contexts).
Output: results/offensive_audit.json. Usage: audit_offensive.py annotation/batch_01.csv:700 annotation/batch_03.csv:831"""
import argparse, csv, json, re
from collections import Counter

# rough markers (romanised Darija/Arabizi insults + FR + EN). Heuristic only; for scoping the ethics statement.
MARKERS = [
    r"\bn[i1]k\b", r"nik", r"9a7ba", r"qa7ba", r"qahba", r"7ayawan", r"tboun", r"taboun", r"zaml", r"zamel",
    r"qlawi", r"9lawi", r"\bzb\b", r"\bzeb\b", r"khra", r"5ra", r"3aher", r"bhim", r"bhima", r"\b7mar\b", r"hmar",
    r"\bklb\b", r"\bkleb\b", r"kelb", r"mok\b", r"mmk", r"l3ar", r"mzabl", r"mkawd", r"9wad", r"qwad", r"sat",
    r"\bzbi\b", r"3affen", r"wld l9a7ba", r"wld lqahba", r"hmar", r"bagra",
    # French
    r"\bpute\b", r"\bmerde\b", r"connard", r"salope", r"encul", r"\bpd\b",
    # English
    r"\bfuck", r"\bshit\b", r"\bbitch\b", r"\basshole\b", r"\bcunt\b",
]
RX = re.compile("|".join(MARKERS), re.I)
ITEM = re.compile(r"^(.*)\[(PER|LOC|ORG|MISC)\]\s*$")

def per_ents(c2, c4):
    cell = c4.strip() if (c4 or "").strip() else (c2 or "")
    if not cell or cell.strip().upper() == "NONE":
        return []
    out = []
    for raw in re.split(r"\s*;\s*|(?<=\])\s*,\s*", cell):
        m = ITEM.match(raw.strip().replace("(?)", "").strip())
        if m and m.group(2) == "PER":
            out.append(m.group(1).strip())
    return out

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("batches", nargs="+"); ap.add_argument("--out", default="results/offensive_audit.json")
    a = ap.parse_args()
    total = off = 0
    per_in_off = Counter(); off_examples = []
    for spec in a.batches:
        path, _, rc = spec.partition(":"); rev = int(rc) if rc else None
        rows = list(csv.reader(open(path, encoding="utf-8")))[1:]
        if rev: rows = rows[:rev]
        for r in rows:
            total += 1
            ar = r[0] if r else ""
            if RX.search(ar):
                off += 1
                for p in per_ents(r[1] if len(r) > 1 else "", r[2] if len(r) > 2 else ""):
                    per_in_off[p.lower()] += 1
                if len(off_examples) < 25:
                    off_examples.append({"text": ar[:120], "PER": per_ents(r[1] if len(r) > 1 else "", r[2] if len(r) > 2 else "")})
    res = {"reviewed_rows": total, "offensive_rows": off, "offensive_pct": round(100 * off / total, 1) if total else 0,
           "PER_in_offensive_rows": {"unique": len(per_in_off), "by_surface": per_in_off.most_common(40)},
           "examples_redacted_preview": off_examples}
    json.dump(res, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"reviewed {total} | offensive(rough) {off} ({res['offensive_pct']}%) | PER-in-offensive: {len(per_in_off)} unique")
    print("top PER appearing in offensive rows (these need public-figure vs private check):")
    for s, c in per_in_off.most_common(25):
        print(f"  {c:3}x {s}")
    print(f"-> {a.out}")

if __name__ == "__main__":
    main()
