"""Template for a MoriscoNER data-source adapter.

Copy this file into sources/<name>/collect.py and implement collect().
Each adapter is responsible ONLY for pulling raw candidate text for one platform/source
and writing it as JSONL. All downstream cleaning/labelling/QC is shared in ../../pipeline/.

Output contract — one JSON object per line into sources/<name>/raw/<name>.jsonl:
    {"text": "<raw sentence/comment>", "source": "<name>", "source_id": "<platform id>", "meta": {...}}

Binding rule: raw/ is gitignored and its bulk text is never redistributed (ToS / GDPR).
Only the downstream stand-off corpus, IDs, a documented sample, and models are released.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

SOURCE_NAME = "TEMPLATE"  # <-- set to the folder name, e.g. "twitter"


def collect(limit: int | None = None) -> list[dict]:
    """Pull raw candidate records for this source.

    TODO: implement. Return a list of dicts matching the output contract above.
    Keep platform credentials in a gitignored .env (never hard-code tokens).
    """
    raise NotImplementedError(f"implement collect() for source '{SOURCE_NAME}'")


def main() -> None:
    ap = argparse.ArgumentParser(description=f"Collect raw candidates for source '{SOURCE_NAME}'")
    ap.add_argument("--limit", type=int, default=None, help="cap number of records (debug)")
    ap.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).parent / "raw" / f"{SOURCE_NAME}.jsonl",
        help="output JSONL path (under raw/, gitignored)",
    )
    args = ap.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    records = collect(limit=args.limit)
    with args.out.open("w", encoding="utf-8") as fh:
        for r in records:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"[{SOURCE_NAME}] wrote {len(records)} records -> {args.out}")


if __name__ == "__main__":
    main()
