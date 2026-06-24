#!/usr/bin/env python3
"""Build a CROSS-annotation IAA pack from an EXISTING annotated batch (no new data, validates the real gold).
Take ~200 sentences from a batch already annotated by one person; the OTHER person re-labels them, and we score
against the existing labels. Only one extra 200-row pass is needed.

Default: source = batch_03 (assistant-annotated) -> Achraf re-labels -> compare to the assistant's existing labels.
Achraf works in the SAME review-the-draft workflow the gold was made with (edit `correction`; blank = accept C3).
"""
import argparse
import csv
import random
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="annotation/batch_03.csv", help="batch already annotated by annotator B")
    ap.add_argument("--reviewed", type=int, default=700, help="how many leading rows of --src are annotated")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--seed", type=int, default=13)
    ap.add_argument("--out", default="iaa")
    ap.add_argument("--reannotator", default="achraf")   # the person who re-labels (annotator A)
    ap.add_argument("--existing", default="assistant")   # who made --src (annotator B)
    a = ap.parse_args()

    rows = list(csv.reader(open(a.src, encoding="utf-8")))[1:][:a.reviewed]
    idx = list(range(len(rows)))
    random.Random(a.seed).shuffle(idx)
    pick = [(i, rows[i]) for i in idx][:a.n]
    out = Path(a.out); out.mkdir(exist_ok=True)

    # sheet for the RE-ANNOTATOR: same review-the-draft workflow (sees C3 predicted, edits `correction`; blank=accept)
    with open(out / f"iaa_cross_{a.reannotator}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["id", "arabizi", "predicted_entities", "correction", "comment_id"])
        for i, r in pick:
            w.writerow([i, r[0], r[1] if len(r) > 1 else "", "", r[3] if len(r) > 3 else ""])
    # reference = the EXISTING annotator's final labels (correction C4 else predicted C3)
    with open(out / "iaa_ref.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["id", "arabizi", "final_entities", "comment_id"])
        for i, r in pick:
            c4 = (r[2] if len(r) > 2 else "").strip()
            final = c4 if c4 else (r[1] if len(r) > 1 else "")
            w.writerow([i, r[0], final, r[3] if len(r) > 3 else ""])
    print(f"wrote {a.out}/iaa_cross_{a.reannotator}.csv ({len(pick)} rows, '{a.reannotator}' edits `correction`)")
    print(f"wrote {a.out}/iaa_ref.csv ('{a.existing}' existing labels)")
    print(f"score: python scripts/iaa_score.py --a {a.out}/iaa_cross_{a.reannotator}.csv --b {a.out}/iaa_ref.csv")


if __name__ == "__main__":
    main()
