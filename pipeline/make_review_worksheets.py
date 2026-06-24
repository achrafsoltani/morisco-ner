#!/usr/bin/env python3
"""Lay the ground for the two native-judgment tasks:
 (1) iaa/iaa_adjudication.csv      -- the 60 IAA disagreements, A vs B, with a blank `adjudicated` column.
 (2) iaa/per_offensive_review.csv  -- PER entities appearing in offensive rows, with one example context, a heuristic
     `suggested` label (public-figure / fictional / ??), and a blank `verdict` column.
Run: make_review_worksheets.py"""
import csv, json, re
from collections import OrderedDict

# ---- (1) IAA adjudication worksheet ----
res = json.load(open("iaa/iaa_results.json", encoding="utf-8"))
dis = res.get("disagreements", [])
with open("iaa/iaa_adjudication.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["id", "arabizi", "annotator_A", "annotator_B", "adjudicated", "note"])
    for d in dis:
        w.writerow([d["id"], d["arabizi"], "; ".join(d.get("A", [])), "; ".join(d.get("B", [])), "", ""])
print(f"wrote iaa/iaa_adjudication.csv ({len(dis)} disagreements) -- fill `adjudicated` with the correct entity list (or NONE)")

# ---- (2) PER-in-offensive review worksheet ----
KNOWN_PUBLIC = {"regragui", "regragi", "ragragui", "ziyach", "ziyech", "hakimi", "bono", "bounou", "wahbi",
                "hasan 2", "hassan 2", "cheb khaled", "bou3achrine", "bouachrine", "changriha", "benkirane",
                "ronaldo", "messi", "amrabat", "boufal", "en nesyri", "regragua"}
FICTIONAL = {"tolkien", "elizabeth bennet", "rony", "toto"}  # toto/rony likely nicknames/fictional -> confirm
ITEM = re.compile(r"^(.*)\[(PER|LOC|ORG|MISC)\]\s*$")
MARK = json.load(open("results/offensive_audit.json", encoding="utf-8"))
per_freq = dict(MARK["PER_in_offensive_rows"]["by_surface"])
# re-scan for one example context per PER-in-offensive
from importlib import import_module
import importlib.util, sys
spec = importlib.util.spec_from_file_location("ao", "scripts/audit_offensive.py")
ao = importlib.util.module_from_spec(spec); spec.loader.exec_module(ao)
context = {}
for path, rev in [("annotation/batch_01.csv", 700), ("annotation/batch_03.csv", 831)]:
    for r in list(csv.reader(open(path, encoding="utf-8")))[1:][:rev]:
        ar = r[0] if r else ""
        if ao.RX.search(ar):
            for p in ao.per_ents(r[1] if len(r) > 1 else "", r[2] if len(r) > 2 else ""):
                context.setdefault(p.lower(), ar[:140])
with open("iaa/per_offensive_review.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["per_surface", "freq", "suggested", "verdict", "example_context"])
    for surf, fr in sorted(per_freq.items(), key=lambda x: -x[1]):
        sug = "public-figure" if surf in KNOWN_PUBLIC else ("fictional?" if surf in FICTIONAL else "??")
        w.writerow([surf, fr, sug, "", context.get(surf, "")])
print(f"wrote iaa/per_offensive_review.csv ({len(per_freq)} PER) -- fill `verdict`: public-figure / private / not-an-entity")
