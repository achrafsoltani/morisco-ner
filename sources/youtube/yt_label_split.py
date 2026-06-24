#!/usr/bin/env python3
"""INCREMENTAL teacher-filter + split. Sonnet NER on collected YouTube Arabizi comments; KEEP only entity-bearing.
Skips comment_ids already labelled (labelled_ids.txt + yt_labeled.jsonl) so re-runs only label NEW comments.
Appends entity-bearing to yt_labeled.jsonl; regenerates ALL batch CSVs (1000 each) from the full set."""
import csv
import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from anthropic import AnthropicBedrock

HERE = Path("/home/achraf/Documents/Lab/darija-llm-ner-gonogo")
MODEL = "eu.anthropic.claude-sonnet-4-6"
REGION = "eu-west-1"
TYPES = {"PER", "LOC", "ORG", "MISC"}
PROMPT = ("You do Moroccan Darija (Arabizi, Latin script) named-entity recognition. 4 types: PER person, LOC location, "
          "ORG organisation, MISC (nationalities, languages, ethnic/religious groups, named cultural genres). Tag ONLY clear "
          "proper-noun named entities; common nouns / pronouns / dates / numbers are O. Return ONLY a JSON array of "
          '{"text": <substring copied verbatim>, "type": <PER|LOC|ORG|MISC>}. If none, [].\nSentence: «%s»\nJSON:')
_lock = threading.Lock()
_cost = {"in": 0, "out": 0}
_done = [0]


def clean(t):
    t = re.sub(r"http\S+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def offsets(toks):
    text, offs = "", []
    for i, t in enumerate(toks):
        if i:
            text += " "
        s = len(text); text += t; offs.append((s, len(text)))
    return text, offs


def to_span(offs, cs, ce):
    idx = [i for i, (s, e) in enumerate(offs) if s < ce and cs < e]
    return [idx[0], idx[-1]] if idx else None


def label(client, tokens):
    text = " ".join(tokens)
    msg = client.messages.create(model=MODEL, max_tokens=512, temperature=0,
                                 messages=[{"role": "user", "content": PROMPT % text}])
    with _lock:
        _cost["in"] += msg.usage.input_tokens; _cost["out"] += msg.usage.output_tokens
        _done[0] += 1
        if _done[0] % 300 == 0:
            print(f"  labelled {_done[0]}", flush=True)
    m = re.search(r"\[.*\]", msg.content[0].text, re.S)
    try:
        ents = json.loads(m.group(0)) if m else []
    except Exception:
        ents = []
    _, offs = offsets(tokens); spans = []
    for e in ents if isinstance(ents, list) else []:
        if not isinstance(e, dict):
            continue
        t, typ = str(e.get("text", "")), str(e.get("type", ""))
        if typ not in TYPES or not t:
            continue
        idx = text.find(t)
        if idx < 0:
            continue
        sp = to_span(offs, idx, idx + len(t))
        if sp:
            spans.append(sp + [typ])
    return spans


def write_batches():
    allk = [json.loads(l) for l in open(HERE / "yt_labeled.jsonl", encoding="utf-8")] if (HERE / "yt_labeled.jsonl").exists() else []
    BD = HERE / "annotation_batches"; BD.mkdir(exist_ok=True)
    nb = (len(allk) + 999) // 1000
    for b in range(nb):
        chunk = allk[b * 1000:(b + 1) * 1000]
        with open(BD / f"batch_{b+1:02d}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["arabizi", "predicted_entities", "CORRECTION", "comment_id"])
            for k in chunk:
                ents = "; ".join(f"{' '.join(k['tokens'][s:e+1])}[{t}]" for s, e, t in k["pred"])
                w.writerow([" ".join(k["tokens"]), ents, "", k["comment_id"]])
    return len(allk), nb


def main():
    rows = [json.loads(l) for l in open(HERE / "yt_comments.jsonl", encoding="utf-8")]
    gold = set(" ".join(json.loads(l)["tokens"]).lower() for l in open(HERE / "data/arabizi_gold.jsonl", encoding="utf-8"))
    labelled = set()
    if (HERE / "labelled_ids.txt").exists():
        labelled |= set(open(HERE / "labelled_ids.txt", encoding="utf-8").read().split())
    if (HERE / "yt_labeled.jsonl").exists():
        labelled |= set(json.loads(l)["comment_id"] for l in open(HERE / "yt_labeled.jsonl", encoding="utf-8"))
    items, seen = [], set()
    for r in rows:
        txt = clean(r["text"]); toks = txt.split()
        if not (3 <= len(toks) <= 40):
            continue
        key = txt.lower()
        if key in gold or key in seen or r["comment_id"] in labelled:
            continue
        seen.add(key); items.append({"tokens": toks, "comment_id": r["comment_id"], "video_id": r["video_id"]})
    print(f"pool {len(rows)} | already labelled {len(labelled)} | NEW to label {len(items)}")
    if items:
        client = AnthropicBedrock(aws_region=REGION)
        out = [None] * len(items)

        def work(i):
            try:
                out[i] = label(client, items[i]["tokens"])
            except Exception:
                out[i] = []

        with ThreadPoolExecutor(max_workers=6) as ex:
            list(ex.map(work, range(len(items))))
        bearing = [{**items[i], "pred": out[i]} for i in range(len(items)) if out[i]]
        with open(HERE / "yt_labeled.jsonl", "a", encoding="utf-8") as f:
            for k in bearing:
                f.write(json.dumps(k, ensure_ascii=False) + "\n")
        with open(HERE / "labelled_ids.txt", "a", encoding="utf-8") as f:
            for it in items:
                f.write(it["comment_id"] + "\n")
        print(f"  +{len(bearing)} new entity-bearing ({sum(len(k['pred']) for k in bearing)} entities) | cost ~${_cost['in']/1e6*3 + _cost['out']/1e6*15:.2f}")
    total, nb = write_batches()
    print(f"=> TOTAL entity-bearing: {total} | {nb} batch CSV(s) of 1000")


if __name__ == "__main__":
    main()
