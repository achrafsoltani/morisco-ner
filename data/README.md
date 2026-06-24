# data/ — canonical corpus file map

Original filenames are preserved (copied from the Aljamiado paper repo, 2026-06-14) so the pipeline scripts keep working.
Record format: one JSON object per line — `{"tokens": [...], "spans": [[start, end, TYPE], ...]}` (token indices inclusive; stand-off).

| file | role | sentences | notes |
|---|---|---|---|
| `arabizi_native_full.jsonl` | **canonical TRAIN** | 1,531 | full native-annotated training corpus (the headline release set) |
| `arabizi_train_native.jsonl` | frozen ablation pool | 1,400 | the subset used by the paper's native-vs-translit scaling ablation; **do not change** |
| `arabizi_gold.jsonl` | **frozen TEST** | 400 | DODa Latin, teacher-drafted then native-corrected; no overlap with train; **frozen** |
| `arabizi_gold_ar.jsonl` | Arabic-script test variant | 400 | Arabic-script rendering of the gold, used for the transliteration reference arm |
| `morisco_iaa200_adjudicated.jsonl` | adjudicated IAA subset | 200 | the doubly-annotated batch_02 sentences after adjudication (κ pass); fold-in candidate |
| `raw/arabizi_draft.json` | teacher draft | — | pre-annotation teacher labelling (input to native review) |
| `raw/arabizi_draft_review.csv` | review worksheet | — | the worksheet the draft was reviewed against |

## Invariants (verify before any release)
- **Test is frozen** (`arabizi_gold.jsonl`, 400) — never add to it; new sentences go to train only.
- **Zero train/test sentence overlap** — re-check after every batch fold-in.
- Per-type (train): PER 845 · LOC 809 · MISC 616 · ORG 373 (1.73 entities/sentence).

## Canonical names (applied at release time)
On HF, the release uses MoriscoNER branding: `train` ← `arabizi_native_full.jsonl`, `test` ← `arabizi_gold.jsonl`.
`pipeline/release_standoff.py` performs the rename + stand-off emit; the working files keep the `arabizi_*` names here.
