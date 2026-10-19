# Changelog — MoriscoNER

## v1.0.1 — stand-off re-release (2026-10-19)
- The three YouTube-derived files now carry only the comment id, the token count, a SHA-1 of the tokens and the entity spans (`data/*.standoff.jsonl`). The files that had carried the comment text since v1.0 were removed from the repository and from its whole history.
- New `pipeline/rehydrate_youtube.py` rebuilds the token-level files with the user's own YouTube Data API key and verifies every record against its stored count and hash. Comments deleted or edited since collection cannot be recovered; in a spot check on 2026-10-19, 2 of 50 were no longer available.
- Annotations are unchanged: re-hydration reproduces the v1.0 token-level records exactly.
- Full licence texts added (`LICENSE-CODE`, `LICENSE-DATA`); the documentation now describes the stand-off format.

## v1.0 — patch (2026-07-04)
- Removed an erroneous `PER` label on a mislabelled token in the native files (a single-label correction; does not affect the paper's reported results).

## v1.0 — initial release (2026-06-24)
- 1,531 train / 400 test sentences, Cohen's κ = 0.873, CC BY-NC 4.0.
