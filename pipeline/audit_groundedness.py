#!/usr/bin/env python3
"""Offset-groundedness audit (the keynote tie): what fraction of the teacher's predicted entity strings are VERBATIM
present in the source sentence — Arabic-script (MArSum news) vs Arabizi (DODa). Records grounded AND ungrounded
(unlike the silver pipeline, which drops ungrounded). Sonnet via Bedrock, threaded."""
import csv
import json
import random
import re
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from anthropic import AnthropicBedrock

HERE = Path(__file__).parent
MODEL = "eu.anthropic.claude-sonnet-4-6"
REGION = "eu-west-1"
random.seed(5)
N = 500
PROMPT = """You annotate Moroccan Darija named entities (4 types: PER, LOC, ORG, MISC).
Tag ONLY clear proper-noun named entities; not common nouns, days, generic words, pronouns, adjectives.
Return ONLY a JSON array of {"text": <substring copied VERBATIM from the sentence>, "type": <PER|LOC|ORG|MISC>}. If none, [].
Sentence: «%s»
JSON:"""

_lock = threading.Lock()
_cost = {"in": 0, "out": 0}


def sample_marsum(n):
    sents = []
    for r in csv.reader(open(HERE / "MArSum/MArSum1_train.txt"), delimiter="\t"):
        if not r or not r[0].strip() or r[0].strip() == "text summary":
            continue
        for s in re.split(r"[.!؟\n]+", r[0]):
            s = s.strip()
            if 20 <= len(s) <= 180:
                sents.append(s)
    random.shuffle(sents)
    return sents[:n]


def sample_arabizi(n):
    sents = []
    for r in csv.DictReader(open(HERE / "DODa/sentences/sentences.csv")):
        s = (r.get("darija") or "").strip()
        if 20 <= len(s) <= 160:
            sents.append(s)
    random.shuffle(sents)
    return sents[:n]


def label(client, s):
    msg = client.messages.create(model=MODEL, max_tokens=1024, temperature=0,
                                 messages=[{"role": "user", "content": PROMPT % s}])
    with _lock:
        _cost["in"] += msg.usage.input_tokens; _cost["out"] += msg.usage.output_tokens
    m = re.search(r"\[.*\]", msg.content[0].text, re.S)
    ents = json.loads(m.group(0)) if m else []
    g = t = 0
    for e in ents:
        txt = str(e.get("text", ""))
        if not txt:
            continue
        t += 1; g += 1 if s.find(txt) >= 0 else 0
    return g, t


def audit(name, sents):
    client = AnthropicBedrock(aws_region=REGION)
    res = [0, 0]

    def work(s):
        try:
            gg, tt = label(client, s)
        except Exception:
            gg, tt = 0, 0
        with _lock:
            res[0] += gg; res[1] += tt

    with ThreadPoolExecutor(max_workers=6) as ex:
        list(ex.map(work, sents))
    g, t = res
    print(f"  {name}: {t} entities | {g} grounded (verbatim) = {100*g/max(1,t):.1f}%", flush=True)


def main():
    print("=== offset-groundedness audit (teacher = Sonnet) ===")
    audit("Arabic-script (MArSum news)", sample_marsum(N))
    audit("Arabizi (DODa)", sample_arabizi(N))
    print(f"~${_cost['in']/1e6*3 + _cost['out']/1e6*15:.2f}")


if __name__ == "__main__":
    main()
