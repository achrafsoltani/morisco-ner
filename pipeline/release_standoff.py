"""Stage 8 — build the CC-BY-NC stand-off release of MoriscoNER for the Hugging Face Hub.

Run ONLY on paper acceptance (public release breaks double-blind before then). Produces a release/ folder with:
  - train.jsonl / test.jsonl  : stand-off records {"id", "tokens", "spans": [[s,e,TYPE]], "source"}
  - sample.jsonl              : a small human-readable documented sample
  - DATASET_CARD.md           : copied from repo root (the HF card)
  - (optional) source_ids.csv : platform IDs for re-hydration, where text cannot be redistributed

Binding: we release the transformed stand-off corpus + IDs + sample (+ models elsewhere). We do NOT release bulk raw
scraped text (YouTube ToS / GDPR). Usernames/handles/channel-ids must already be stripped upstream.
"""
from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SPLITS = {
    "train": REPO / "data" / "arabizi_native_full.jsonl",
    "test": REPO / "data" / "arabizi_gold.jsonl",
}


def emit_split(src: Path, dst: Path, split: str) -> int:
    n = 0
    dst.parent.mkdir(parents=True, exist_ok=True)
    with src.open(encoding="utf-8") as fin, dst.open("w", encoding="utf-8") as fout:
        for i, line in enumerate(fin):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            out = {
                "id": f"morisco-{split}-{i:05d}",
                "tokens": rec["tokens"],
                "spans": rec.get("spans", []),
                "source": rec.get("source", "unknown"),
            }
            fout.write(json.dumps(out, ensure_ascii=False) + "\n")
            n += 1
    return n


def main() -> None:
    ap = argparse.ArgumentParser(description="Build the MoriscoNER stand-off HF release (on acceptance only)")
    ap.add_argument("--out", type=Path, default=REPO / "release", help="release output dir")
    ap.add_argument("--sample", type=int, default=25, help="size of the documented sample")
    ap.add_argument("--i-confirm-acceptance", action="store_true",
                    help="required guard: public release breaks double-blind before acceptance")
    args = ap.parse_args()

    if not args.i_confirm_acceptance:
        raise SystemExit("Refusing: pass --i-confirm-acceptance (release is public; only after paper acceptance).")

    args.out.mkdir(parents=True, exist_ok=True)
    counts = {split: emit_split(src, args.out / f"{split}.jsonl", split) for split, src in DEFAULT_SPLITS.items()}

    # documented sample from train
    sample_src = args.out / "train.jsonl"
    with sample_src.open(encoding="utf-8") as fin, (args.out / "sample.jsonl").open("w", encoding="utf-8") as fout:
        for i, line in enumerate(fin):
            if i >= args.sample:
                break
            fout.write(line)

    card = REPO / "DATASET_CARD.md"
    if card.exists():
        shutil.copy(card, args.out / "DATASET_CARD.md")

    print("Stand-off release built:", {**counts, "sample": args.sample}, "->", args.out)
    print("TODO before push: strip any residual identifiers; add BibTeX; `huggingface-cli upload AchrafSoltani/morisco-ner`.")


if __name__ == "__main__":
    main()
