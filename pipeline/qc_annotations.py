#!/usr/bin/env python3
"""Quality-control the native Arabizi NER annotations BEFORE they reach the gold.

Mirrors batch_to_jsonl.py's exact parsing so it reports precisely what the converter
would silently drop/lose. Operates on the *reviewed region* of each batch (the first
--reviewed rows that the native annotator has actually gone through).

Checks (deterministic, no guessing):
  1. MALFORMED C4   - non-empty, not NONE, but a ';'-item fails the text[TYPE] regex
                      -> in batch_to_jsonl this can zero-out the whole row (no fallback to C3).
  2. UNGROUNDED     - a parsed entity's text is not a verbatim substring of C1
                      -> silently dropped by the converter's to_span().
  3. NEAR-MISS TYPE - bracketed tag that is not exactly PER/LOC/ORG/MISC (e.g. [Per],[GPE]).
  4. TYPE CLASH     - same surface form annotated with >1 type across rows.
  5. LIKELY-MISSED  - capitalised proper-noun-shaped token left outside every entity (native review only).
  6. STATS          - per-type counts, density, progress vs the ~1500-entity target.

Usage: qc_annotations.py --batches annotation/batch_01.csv:700 annotation/batch_03.csv:700 \
                         --out results/annotation_qc.json [--jsonl data/arabizi_train_native.jsonl]
"""
import argparse
import csv
import json
import re
from collections import Counter, defaultdict

VALID = {"PER", "LOC", "ORG", "MISC"}
ITEM_RE = re.compile(r"^(.*)\[(PER|LOC|ORG|MISC)\]\s*$")
ANYTAG_RE = re.compile(r"^(.*)\[([^\]]+)\]\s*$")  # any bracketed tag, to catch near-misses
# tokens that look like proper nouns in Arabizi (Capitalised, alpha-ish, len>=3)
CAP_RE = re.compile(r"^[A-Z][a-zA-Z']{2,}$")
# common Arabizi lowercase function words / non-entities that sometimes appear capitalised at sentence start
STOP = {"Ana", "Nta", "Nti", "Howa", "Hiya", "Hna", "Ntoma", "Homa", "Wach", "Wash",
        "Chno", "Chnou", "Kifash", "Kifach", "Fin", "Imta", "3lash", "Allah", "Llah",
        "Inshallah", "Inchallah", "Hamdoullah", "Hamdulillah", "Bismillah", "Salam",
        "Mashallah", "Machallah", "Wallah", "Safi", "Yallah", "Yak", "Hadi", "Hada",
        "Hadik", "Hadak", "The", "And", "But", "For", "Mais", "Les", "Des", "Une"}


def parse_items(cell):
    """Return (good, bad) lists. good=[(text,type)], bad=[(raw_item, reason, tagfound)]."""
    cell = (cell or "").strip()
    if not cell or cell.upper() == "NONE":
        return [], []
    good, bad = [], []
    # split on ';' OR a ',' that directly follows a ']' (recover comma-separated tagged entities).
    for raw in re.split(r"\s*;\s*|(?<=\])\s*,\s*", cell):
        item = raw.strip().replace("(?)", "").strip()
        if not item:
            continue
        m = ITEM_RE.match(item)
        if m:
            good.append((m.group(1).strip(), m.group(2)))
            continue
        am = ANYTAG_RE.match(item)
        if am:
            bad.append((item, "near-miss-type", am.group(2).strip()))
        else:
            bad.append((item, "no-bracket-tag", None))
    return good, bad


def grounded(text, ent):
    return text.lower().find(ent.lower()) >= 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--batches", nargs="+", required=True, help="path:reviewed_row_count")
    ap.add_argument("--out", required=True)
    ap.add_argument("--jsonl", help="also write the gold-ready training JSONL of the reviewed region")
    ap.add_argument("--target", type=int, default=1500)
    a = ap.parse_args()

    report = {"batches": [], "issues": {"malformed": [], "ungrounded": [], "near_miss_type": [],
                                        "type_clash": [], "likely_missed": []},
              "stats": {}}
    types = Counter()
    surface_types = defaultdict(set)   # normalized surface -> {types}
    surface_rows = defaultdict(list)
    jsonl_rows = []
    n_sent = n_with = n_ent = n_reviewed = 0
    cap_candidates = []

    for spec in a.batches:
        path, _, rc = spec.partition(":")
        reviewed = int(rc) if rc else None
        rows = list(csv.reader(open(path, encoding="utf-8")))[1:]
        if reviewed is not None:
            rows = rows[:reviewed]
        b_sent = b_ent = b_with = b_corr = b_none = 0
        for ridx, r in enumerate(rows):
            n_reviewed += 1
            ar = r[0] if len(r) > 0 else ""
            c3 = r[1] if len(r) > 1 else ""   # predicted (teacher)
            c4 = r[2] if len(r) > 2 else ""   # CORRECTION (native)
            cid = r[3] if len(r) > 3 else ""
            c4s = (c4 or "").strip()
            if c4s:
                b_corr += 1
                if c4s.upper() == "NONE":
                    b_none += 1
            # final source = C4 if non-empty else C3 (exactly batch_to_jsonl logic)
            src_cell = c4 if c4s else c3
            good, bad = parse_items(src_cell)

            # malformed: a non-empty, non-NONE C4 with a failed item -> potential silent loss
            for raw, reason, tag in bad:
                rec = {"batch": path, "row": ridx, "comment_id": cid, "item": raw,
                       "from": "C4" if c4s else "C3", "reason": reason, "tag": tag,
                       "cell": src_cell, "arabizi": ar}
                if reason == "near-miss-type":
                    report["issues"]["near_miss_type"].append(rec)
                report["issues"]["malformed"].append(rec)
            # if C4 was filled but yields ZERO good entities and isn't NONE -> whole row lost
            if c4s and c4s.upper() != "NONE" and not good:
                report["issues"]["malformed"].append(
                    {"batch": path, "row": ridx, "comment_id": cid, "item": c4s,
                     "from": "C4", "reason": "row-zeroed-no-fallback", "tag": None,
                     "cell": c4s, "arabizi": ar})

            # build spans & grounding check
            toks = ar.split()
            covered = set()
            spans = []
            for txt, typ in good:
                if not grounded(ar, txt):
                    report["issues"]["ungrounded"].append(
                        {"batch": path, "row": ridx, "comment_id": cid, "entity": txt,
                         "type": typ, "arabizi": ar})
                    continue
                # span mapping (same as converter)
                idx = ar.lower().find(txt.lower())
                s, e = idx, idx + len(txt)
                # token coverage
                pos = 0
                offs = []
                for t in toks:
                    i = ar.find(t, pos)
                    offs.append((i, i + len(t)))
                    pos = i + len(t)
                cov = [i for i, (x, y) in enumerate(offs) if x < e and s < y]
                if cov:
                    spans.append([cov[0], cov[-1], typ])
                    for ci in range(cov[0], cov[-1] + 1):
                        covered.add(ci)
                    types[typ] += 1
                    b_ent += 1
                    nrm = re.sub(r"\W+", "", txt.lower())
                    surface_types[nrm].add(typ)
                    surface_rows[nrm].append((path, ridx))
            jsonl_rows.append({"tokens": toks, "spans": [s[:2] + [s[2]] for s in spans],
                               "comment_id": cid})
            b_sent += 1
            if spans:
                b_with += 1
            # likely-missed: capitalised proper-noun-shaped token not covered, not a stopword
            for ti, t in enumerate(toks):
                if ti in covered:
                    continue
                if CAP_RE.match(t) and t not in STOP:
                    cap_candidates.append({"batch": path, "row": ridx, "comment_id": cid,
                                           "token": t, "arabizi": ar})
        report["batches"].append({"path": path, "reviewed_rows": len(rows),
                                  "entities": b_ent, "sent_with_entities": b_with,
                                  "rows_with_C4": b_corr, "none_rows": b_none})
        n_sent += b_sent
        n_with += b_with
        n_ent += b_ent

    # type clashes
    for nrm, tset in surface_types.items():
        if len(tset) > 1:
            report["issues"]["type_clash"].append(
                {"surface": nrm, "types": sorted(tset),
                 "occurrences": len(surface_rows[nrm])})

    report["issues"]["likely_missed"] = cap_candidates
    report["stats"] = {
        "reviewed_rows": n_reviewed,
        "sentences": n_sent,
        "sentences_with_entities": n_with,
        "total_entities": n_ent,
        "entities_per_sentence": round(n_ent / n_sent, 3) if n_sent else 0,
        "by_type": dict(types),
        "target_entities": a.target,
        "progress_pct": round(100 * n_ent / a.target, 1),
        "counts": {k: len(v) for k, v in report["issues"].items()},
    }
    json.dump(report, open(a.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

    if a.jsonl:
        with open(a.jsonl, "w", encoding="utf-8") as f:
            for row in jsonl_rows:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

    s = report["stats"]
    print("=" * 64)
    print(f"REVIEWED {s['reviewed_rows']} rows | {s['sentences']} sentences | "
          f"{s['sentences_with_entities']} with entities")
    print(f"ENTITIES {s['total_entities']} ({s['entities_per_sentence']}/sent) "
          f"by type {s['by_type']}")
    print(f"PROGRESS toward ~{a.target} entities: {s['progress_pct']}%")
    print("-" * 64)
    print("ISSUES (counts):")
    for k, v in s["counts"].items():
        print(f"  {k:16} {v}")
    if a.jsonl:
        print(f"\nwrote gold-ready -> {a.jsonl}  ({len(jsonl_rows)} sentences)")
    print(f"full report -> {a.out}")


if __name__ == "__main__":
    main()
