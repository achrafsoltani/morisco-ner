#!/usr/bin/env python3
"""Token-aligned transliteration via Claude (Bedrock). Input jsonl {tokens, spans}; transliterate each token to the
target script KEEPING the token count (so entity spans transfer 1:1). Misaligned sentences are dropped (span safety).
--dir ar2arabizi | arabizi2ar. Threaded. Usage: transliterate.py --input X.jsonl --out Y.jsonl --dir ar2arabizi"""
import argparse
import json
import re
import threading
from concurrent.futures import ThreadPoolExecutor

from anthropic import AnthropicBedrock

MODEL = "eu.anthropic.claude-sonnet-4-6"
REGION = "eu-west-1"
PROMPTS = {
    "ar2arabizi": ("Transliterate each Moroccan Darija token from ARABIC SCRIPT to ARABIZI (Latin script, using the usual "
                   "digits 3=ع 7=ح 9=ق 2=glottal where natural). Keep the SAME number of tokens, same order, one output per "
                   "input token. Return ONLY a JSON array of strings.\nTokens: %s\nJSON:"),
    "arabizi2ar": ("Transliterate each Moroccan Darija token from ARABIZI (Latin script) to ARABIC SCRIPT. Keep the SAME "
                   "number of tokens, same order, one output per input token. Return ONLY a JSON array of strings.\n"
                   "Tokens: %s\nJSON:"),
}
_cost = {"in": 0, "out": 0}
_lock = threading.Lock()


def translit(client, tokens, direction):
    msg = client.messages.create(model=MODEL, max_tokens=2048, temperature=0,
                                 messages=[{"role": "user", "content": PROMPTS[direction] % json.dumps(tokens, ensure_ascii=False)}])
    with _lock:
        _cost["in"] += msg.usage.input_tokens; _cost["out"] += msg.usage.output_tokens
    m = re.search(r"\[.*\]", msg.content[0].text, re.S)
    try:
        out = json.loads(m.group(0)) if m else None
    except Exception:
        out = None
    if isinstance(out, list) and len(out) == len(tokens) and all(str(x).strip() for x in out):
        return [str(x) for x in out]
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--dir", required=True, choices=list(PROMPTS)); ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    client = AnthropicBedrock(aws_region=REGION)
    rows = [json.loads(l) for l in open(a.input, encoding="utf-8")]
    out = [None] * len(rows); done = [0]

    def work(i):
        try:
            t = translit(client, rows[i]["tokens"], a.dir)
        except Exception:
            t = None
        out[i] = {"tokens": t, "spans": rows[i]["spans"]} if t else None
        with _lock:
            done[0] += 1
            if done[0] % 200 == 0:
                print(f"  {done[0]}/{len(rows)}", flush=True)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        list(ex.map(work, range(len(rows))))
    kept = [r for r in out if r]
    with open(a.out, "w", encoding="utf-8") as f:
        for r in kept:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{a.input} -> {a.out}: {len(kept)}/{len(rows)} kept ({len(rows)-len(kept)} token-misaligned dropped) "
          f"| ~${_cost['in']/1e6*3 + _cost['out']/1e6*15:.2f}")


if __name__ == "__main__":
    main()
