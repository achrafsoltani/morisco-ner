# pipeline/ — shared build stages

Source-agnostic stages applied to any `sources/<src>/raw/*.jsonl` to turn raw candidates into the released corpus.
Scripts were copied from the Aljamiado paper repo (original names preserved); run them from the repo root so relative
`data/` paths resolve.

## Stage order
| # | Stage | Script(s) | In → Out |
|---|---|---|---|
| 1 | Filter | `filter.py` *(new)* | raw source JSONL → Latin-script + entity-likely candidates |
| 2 | Teacher draft | `teacher_ner.py`, `arabizi_label.py` | candidates → draft labelling (LLM teacher) |
| 3 | Native annotate | *(manual; → `annotation/batch_*.csv`)* | draft → human review-and-correct, in batches |
| 4 | To-JSONL + QC | `batch_to_jsonl.py` → `qc_annotations.py` | batches → `data/*.jsonl` (offset-grounding + comma-split fix) |
| 5 | Build gold/test | `build_arabizi_gold.py`, `arabizi_gold.py` | draft → frozen 400-sentence test (DODa) |
| 6 | IAA | `make_iaa_pack.py` → `iaa_score.py` | blank A/B packs → Cohen's κ + per-type F1 → adjudicate |
| 7 | Audits | `audit_groundedness.py`, `audit_offensive.py` | corpus → groundedness + offensive-content review |
| 8 | Release | `release_standoff.py` *(new)* | `data/*.jsonl` → CC-BY-NC stand-off HF dataset (on acceptance) |
| — | Utility | `transliterate.py`, `make_review_worksheets.py` | Arabizi↔Arabic transliteration; reviewer worksheets |

## Conventions
- Record format: `{"tokens": [...], "spans": [[start, end, TYPE], ...]}` (inclusive indices; stand-off).
- Tagset CoNLL-4 (PER/LOC/ORG/MISC); **binding MISC rule** in `../ANNOTATION-GUIDELINES.md` (cultural/ethnic/religious → MISC).
- **Test stays frozen**; new sentences are train-only; re-verify zero train/test overlap after each fold-in (`qc_annotations.py`).
- Credentials (YouTube API key, Anthropic key for the teacher) live in a gitignored `.env` — never hard-coded.
