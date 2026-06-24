"""Stage 1 — filter raw source candidates to ARABIZI (Latin-script Moroccan Darija) + entity-likely sentences.

Source-agnostic: reads any sources/<src>/raw/*.jsonl (records with a "text" field) and keeps a comment only if it is
  (1) predominantly Latin-script,
  (2) actually Moroccan Darija in Latin script (ARABIZI) — NOT pure French / English / Spanish, and
  (3) entity-likely (worth annotating) — unless --keep-all-darija is given (then (3) is skipped, for the MLM pool).

Code-switched Darija (Darija + some French/English) is KEPT — that is a wanted MoriscoNER phenomenon. Only comments
with NO Darija signal at all (pure FR/EN/ES) are dropped.

Arabizi signal = a chat-digit fused into a word (3la, 7it, 9al, n9adro, ch7al) OR a distinctive Darija marker word
(wach, kayn, dyal, bzaf, khoya, daba, nchallah, …). Pure French/English/Spanish lack both.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Script / structure
_ARABIC = re.compile(r"[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿]")
_LATIN = re.compile(r"[A-Za-z]")
_INTERIOR_CAP = re.compile(r"(?<=\s)[A-Z][a-z]+")

# Arabizi chat-digit: a digit 2-9 FOLLOWED by a letter (3la, 7it, 9al, ch7al, n9adro).
# Requiring a letter *after* the digit avoids trailing-digit noise like "PS5", "web3", "mp3", "GTA6".
_ARABIZI_DIGIT = re.compile(r"[2-9][a-zA-Z]")

# Distinctive Moroccan-Darija marker words (Latin). Chosen to be rare in FR/EN/ES to keep precision high.
_DARIJA_MARKERS = {
    # interrogatives / relatives / demonstratives
    "wach", "wash", "achno", "chno", "chnou", "chnoo", "kifach", "kifash", "3lach", "3lash", "fin", "mnin", "fch",
    "li", "lli", "hadi", "hada", "had", "hadik", "hadak", "dakchi", "hadchi", "dak", "dik",
    # existence / negation / very-common particles
    "kayn", "kayna", "kaynin", "makayn", "makaynch", "makanch", "makansh", "ma3reftch", "machi", "mashi",
    "dyal", "dial", "ntaya", "ntiya", "nta", "nti", "ntoma", "huwa", "hiya", "hna", "7na",
    # quantity / degree / time
    "bzaf", "bezzaf", "chwiya", "shwiya", "ch7al", "ch7al", "chhal", "koulchi", "kolchi", "ga3", "ga3ma",
    "daba", "gha", "ghir", "walo", "walou", "deba", "lyoum", "lbar7", "ghda",
    # adjectives / reactions
    "zwin", "zwina", "mzyan", "mzyana", "mezyan", "wakha", "safi", "bslama", "yallah", "yalah", "zayed",
    # people / address
    "khoya", "khouya", "khoya", "sahbi", "s7abi", "drari", "wlad", "weldi", "bnt", "lalla", "sidi", "a3yan",
    # verbs / wishes
    "bghit", "bgha", "baghi", "kanbghi", "ghadi", "gadi", "3afak", "3afakoum", "smiti", "n9adro", "kayn",
    "nchallah", "inchallah", "nchalah", "hamdullah", "lhamdullah", "tbarklah", "tbareklah", "tbarkallah",
    # prepositions / connectors distinctive to Darija romanization
    "3la", "3and", "3end", "m3a", "m3ak", "men", "mn", "f9", "fou9", "ta7t", "blasti", "blati",
}

# Entity-likely cues (proper-noun-ish): interior capitalised token OR a known Moroccan entity trigger.
_TRIGGERS = (
    "si ", "sidi", "lalla", "moulay", "club", "wydad", "raja", "maroc", "casa", "rabat", "fes", "agadir",
    "tanja", "marrakech", "oujda", "nador", "dyal ",
)

# Cosmetic cleaning applied to kept text: strip URLs, @mentions, video timestamps, emojis/pictographs.
_URL = re.compile(r"https?://\S+|www\.\S+")
_MENTION = re.compile(r"@\w+")
_TIMESTAMP = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")
_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF"
    "←-⇿⌀-⏿⬀-⯿️‍⃣]"
)


def clean(text: str) -> str:
    text = _URL.sub(" ", text)
    text = _MENTION.sub(" ", text)
    text = _TIMESTAMP.sub(" ", text)
    text = _EMOJI.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def latin_ratio(text: str) -> float:
    lat = len(_LATIN.findall(text))
    ar = len(_ARABIC.findall(text))
    tot = lat + ar
    return lat / tot if tot else 0.0


def is_darija_arabizi(text: str) -> bool:
    """True if the (Latin) text shows a positive Darija signal — fused chat-digit or a Darija marker word."""
    if _ARABIZI_DIGIT.search(text):
        return True
    toks = set(re.findall(r"[a-z0-9]+", text.lower()))
    return bool(toks & _DARIJA_MARKERS)


def is_entity_likely(text: str) -> bool:
    if _INTERIOR_CAP.search(text):
        return True
    low = " " + text.lower() + " "
    return any(t in low for t in _TRIGGERS)


def classify(text: str, min_latin: float, min_tokens: int, max_tokens: int, need_entity: bool) -> str:
    """Return 'keep' or the drop reason."""
    n = len(text.split())
    if n < min_tokens:
        return "too_short"
    if n > max_tokens:
        return "too_long"
    if latin_ratio(text) < min_latin:
        return "not_latin"          # Arabic-script-heavy
    if not is_darija_arabizi(text):
        return "not_darija"         # pure French / English / Spanish etc.
    if need_entity and not is_entity_likely(text):
        return "not_entity_likely"
    return "keep"


def main() -> None:
    ap = argparse.ArgumentParser(description="Filter raw comments -> Arabizi (Darija-Latin) + entity-likely candidates")
    ap.add_argument("inputs", type=Path, nargs="+", help="input JSONL file(s) with a 'text' field")
    ap.add_argument("--out", type=Path, required=True, help="output JSONL of kept candidates")
    ap.add_argument("--rejected", type=Path, default=None, help="optional JSONL of dropped records (with _reason)")
    ap.add_argument("--min-latin", type=float, default=0.5, help="min Latin-script ratio (default 0.5)")
    ap.add_argument("--min-tokens", type=int, default=4)
    ap.add_argument("--max-tokens", type=int, default=60)
    ap.add_argument("--keep-all-darija", action="store_true",
                    help="skip the entity-likely requirement (broad Darija pool for MLM, not just annotation candidates)")
    args = ap.parse_args()

    need_entity = not args.keep_all_darija
    counts: dict[str, int] = {}
    seen: set[str] = set()
    kept = total = 0
    args.out.parent.mkdir(parents=True, exist_ok=True)
    rej_fh = args.rejected.open("w", encoding="utf-8") if args.rejected else None
    with args.out.open("w", encoding="utf-8") as fout:
        for inp in args.inputs:
            with inp.open(encoding="utf-8") as fin:
                for line in fin:
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    text = clean(rec.get("text") or "")
                    if not text:
                        continue
                    rec["text"] = text
                    total += 1
                    h = hash(text.lower())
                    if h in seen:
                        counts["dup"] = counts.get("dup", 0) + 1
                        continue
                    seen.add(h)
                    reason = classify(text, args.min_latin, args.min_tokens, args.max_tokens, need_entity)
                    counts[reason] = counts.get(reason, 0) + 1
                    if reason == "keep":
                        fout.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        kept += 1
                    elif rej_fh:
                        rec["_reason"] = reason
                        rej_fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    if rej_fh:
        rej_fh.close()
    print(f"in={total}  kept={kept} ({100*kept/max(total,1):.0f}%)  -> {args.out}", file=sys.stderr)
    print("breakdown: " + "  ".join(f"{k}={v}" for k, v in sorted(counts.items(), key=lambda x: -x[1])), file=sys.stderr)


if __name__ == "__main__":
    main()
