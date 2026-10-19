# data/ — corpus file map

The YouTube-derived files are released **stand-off**: they carry the YouTube comment id, the token count, a SHA-1 of the space-joined tokens, and the entity spans, but never the comment text. Run `pipeline/rehydrate_youtube.py` with your own YouTube Data API v3 key to rebuild the token-level files locally (see the root README). The DODa-derived test files carry their text, which DODa's MIT licence allows.

| file | role | sentences | content |
|---|---|---|---|
| `arabizi_native_full.standoff.jsonl` | **canonical TRAIN** | 1,531 | stand-off: `{"comment_id", "n_tokens", "text_sha1", "spans"}` |
| `arabizi_train_native.standoff.jsonl` | frozen ablation pool | 1,400 | stand-off; the subset used by the paper's native-vs-transliteration scaling ablation |
| `morisco_iaa200_adjudicated.standoff.jsonl` | adjudicated IAA subset | 200 | stand-off, plus the subset's own `id`; the doubly annotated sentences after adjudication |
| `arabizi_gold.jsonl` | **frozen TEST** | 400 | `{"tokens", "spans"}`; DODa Latin sentences, teacher-drafted then native-corrected |
| `arabizi_gold_ar.jsonl` | Arabic-script test variant | 400 | Arabic-script rendering of the test set, used for the transliteration reference arm |

Spans are `[start, end, TYPE]` token indices, inclusive, over the whitespace tokens of the comment text after the collection pipeline's normalisation (whitespace collapsed, URLs removed). `rehydrate_youtube.py` writes the token-level files under their original names (`arabizi_native_full.jsonl` and so on), which `.gitignore` keeps out of the repository.

## Invariants (verify before any release)
- **Test is frozen** (`arabizi_gold.jsonl`, 400 sentences): new sentences go to train only.
- **Zero train/test sentence overlap**: re-check after every batch fold-in.
- Per-type counts (train span records): PER 845 · LOC 809 · MISC 616 · ORG 373.
