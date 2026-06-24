#!/usr/bin/env python3
"""Score inter-annotator agreement from two filled IAA sheets (iaa_blank_A.csv, iaa_blank_B.csv).
Reports: token-level Cohen's kappa (le kappa de Cohen), entity-level pairwise F1 (exact + relaxed IoU>=0.5),
per-type breakdown, and a per-sentence disagreement report for adjudication. No external deps."""
import argparse
import csv
import json
import re
from collections import Counter

TYPES = ["PER", "LOC", "ORG", "MISC"]
ITEM = re.compile(r"^(.*)\[(PER|LOC|ORG|MISC)\]\s*$")


def final_label(row):
    """Resolve the final entity string from any sheet format: explicit final/entities,
    or the review workflow (correction C4 else predicted C3)."""
    if "final_entities" in row:
        return row["final_entities"]
    corr = (row.get("correction") or row.get("CORRECTION") or "").strip()
    if "predicted_entities" in row:
        return corr if corr else (row.get("predicted_entities") or "")
    return row.get("entities") or corr or ""


def parse_ents(cell):
    cell = (cell or "").strip()
    if not cell or cell.upper() == "NONE":
        return []
    out = []
    for raw in re.split(r"\s*;\s*|(?<=\])\s*,\s*", cell):
        m = ITEM.match(raw.strip().replace("(?)", "").strip())
        if m:
            out.append((m.group(1).strip(), m.group(2)))
    return out


def spans(text, ents):
    toks, offs, pos = text.split(), [], 0
    for t in toks:
        i = text.find(t, pos); offs.append((i, i + len(t))); pos = i + len(t)
    sp = []
    for txt, typ in ents:
        idx = text.lower().find(txt.lower())
        if idx < 0:
            continue
        s, e = idx, idx + len(txt)
        cov = [i for i, (x, y) in enumerate(offs) if x < e and s < y]
        if cov:
            sp.append((cov[0], cov[-1], typ))
    return toks, sp


def bio(n, sp):
    tags = ["O"] * n
    for a, b, t in sp:
        if a < n:
            tags[a] = "B-" + t
        for k in range(a + 1, min(b + 1, n)):
            tags[k] = "I-" + t
    return tags


def kappa(la, lb):
    n = len(la)
    po = sum(1 for x, y in zip(la, lb) if x == y) / n
    ca, cb = Counter(la), Counter(lb)
    pe = sum((ca[l] / n) * (cb[l] / n) for l in set(la) | set(lb))
    return (po - pe) / (1 - pe) if pe < 1 else 1.0, po


def iou(a, b):
    s, e = max(a[0], b[0]), min(a[1], b[1]); inter = max(0, e - s + 1)
    return inter / ((a[1] - a[0] + 1) + (b[1] - b[0] + 1) - inter) if inter else 0.0


def ent_f1(A, B, thr, typ=None):
    fa = [s for s in A if typ is None or s[2] == typ]
    fb = [s for s in B if typ is None or s[2] == typ]
    used, tp = set(), 0
    for g in fa:
        for j, p in enumerate(fb):
            if j in used or g[2] != p[2]:
                continue
            if (thr >= 1 and g[:2] == p[:2]) or (thr < 1 and iou(g, p) >= thr):
                used.add(j); tp += 1; break
    denom = len(fa) + len(fb)
    return (2 * tp / denom) if denom else 1.0, len(fa), len(fb)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", default="iaa/iaa_blank_A.csv")
    ap.add_argument("--b", default="iaa/iaa_blank_B.csv")
    ap.add_argument("--out", default="iaa/iaa_results.json")
    args = ap.parse_args()
    A = {r["id"]: r for r in csv.DictReader(open(args.a, encoding="utf-8"))}
    B = {r["id"]: r for r in csv.DictReader(open(args.b, encoding="utf-8"))}
    ids = [i for i in A if i in B]
    tagsA, tagsB, spA, spB, disagree = [], [], [], [], []
    for i in ids:
        text = A[i]["arabizi"]
        ta, sa = spans(text, parse_ents(final_label(A[i])))
        tb, sb = spans(text, parse_ents(final_label(B[i])))
        n = len(ta)
        tagsA += bio(n, sa); tagsB += bio(n, sb)
        spA.append(sa); spB.append(sb)
        if set(sa) != set(sb):
            disagree.append({"id": i, "arabizi": text,
                             "A": [f"{' '.join(ta[s:e+1])}[{t}]" for s, e, t in sa],
                             "B": [f"{' '.join(ta[s:e+1])}[{t}]" for s, e, t in sb]})
    k, po = kappa(tagsA, tagsB)
    res = {"sentences": len(ids), "tokens": len(tagsA),
           "token_cohen_kappa": round(k, 4), "token_observed_agreement": round(po, 4),
           "entity_f1_exact": round(sum(ent_f1(spA[j], spB[j], 1.0)[0] for j in range(len(ids))) / len(ids), 4),
           "entity_f1_relaxed": round(sum(ent_f1(spA[j], spB[j], 0.5)[0] for j in range(len(ids))) / len(ids), 4),
           "by_type_exact_f1": {}, "n_disagreement_sentences": len(disagree)}
    allA = [s for sl in spA for s in sl]; allB = [s for sl in spB for s in sl]
    for t in TYPES:
        f, na, nb = ent_f1(allA, allB, 1.0, t)
        res["by_type_exact_f1"][t] = {"f1": round(f, 4), "A_count": na, "B_count": nb}
    res["entity_count"] = {"A": len(allA), "B": len(allB)}
    json.dump({"summary": res, "disagreements": disagree}, open(args.out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"sentences={res['sentences']} tokens={res['tokens']}")
    print(f"Cohen's kappa (token)   = {res['token_cohen_kappa']}  (obs.agreement {res['token_observed_agreement']})")
    print(f"Entity F1 exact/relaxed = {res['entity_f1_exact']} / {res['entity_f1_relaxed']}")
    print(f"per-type exact F1       = " + ", ".join(f"{t} {res['by_type_exact_f1'][t]['f1']}" for t in TYPES))
    print(f"disagreement sentences  = {res['n_disagreement_sentences']}  -> {args.out}")


if __name__ == "__main__":
    main()
