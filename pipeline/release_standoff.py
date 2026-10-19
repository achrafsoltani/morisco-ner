"""Stage 8 — build the CC-BY-NC release of MoriscoNER for the Hugging Face Hub.

Produces a release/ folder with:
  - train.standoff.jsonl : the YouTube-derived training split, stand-off
                           {"id", "comment_id", "n_tokens", "text_sha1", "spans": [[s,e,TYPE]]}
  - test.jsonl           : the DODa-derived test split with its text {"id", "tokens", "spans", "source"}
  - sample.jsonl         : a small human-readable sample, taken from the test split
  - rehydrate_youtube.py : rebuilds the training tokens from the comment ids (own YouTube API key)
  - DATASET_CARD.md      : copied from the repo root (the HF card)

Binding: we release the stand-off corpus, the comment ids, the DODa test set and a sample (models elsewhere).
We do NOT release the text of YouTube comments (YouTube API terms / GDPR).
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
TRAIN = REPO / "data" / "arabizi_native_full.standoff.jsonl"
TEST = REPO / "data" / "arabizi_gold.jsonl"


def emit(src: Path, dst: Path, split: str, standoff: bool) -> int:
    n = 0
    dst.parent.mkdir(parents=True, exist_ok=True)
    with src.open(encoding="utf-8") as fin, dst.open("w", encoding="utf-8") as fout:
        for i, line in enumerate(fin):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if standoff:
                if "tokens" in rec:
                    raise SystemExit(f"{src}: a stand-off split must not carry text")
                out = {"id": f"morisco-{split}-{i:05d}", **rec}
            else:
                out = {"id": f"morisco-{split}-{i:05d}", "tokens": rec["tokens"],
                       "spans": rec.get("spans", []), "source": "doda"}
            fout.write(json.dumps(out, ensure_ascii=False) + "\n")
            n += 1
    return n


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the MoriscoNER Hugging Face release")
    ap.add_argument("--out", type=Path, default=REPO / "release", help="release output dir")
    ap.add_argument("--sample", type=int, default=25, help="size of the documented sample")
    args = ap.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    counts = {"train": emit(TRAIN, args.out / "train.standoff.jsonl", "train", standoff=True),
              "test": emit(TEST, args.out / "test.jsonl", "test", standoff=False)}

    with (args.out / "test.jsonl").open(encoding="utf-8") as fin, \
            (args.out / "sample.jsonl").open("w", encoding="utf-8") as fout:
        for i, line in enumerate(fin):
            if i >= args.sample:
                break
            fout.write(line)

    shutil.copy(REPO / "pipeline" / "rehydrate_youtube.py", args.out / "rehydrate_youtube.py")
    card = REPO / "DATASET_CARD.md"
    if card.exists():
        shutil.copy(card, args.out / "DATASET_CARD.md")
    print("Release built:", {**counts, "sample": args.sample}, "->", args.out)


if __name__ == "__main__":
    main()
