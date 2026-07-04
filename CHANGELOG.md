# Changelog — MoriscoNER

## v1.0 — patch (2026-07-04)
- **Annotation correction:** removed an erroneous `PER` span on the vulgar token *taboune* (comment `Ugz0Xp…`) in the native files — a slur that had been mistagged as a person. This is the only change from the initial v1.0 (one label of 2,643; no reported result is affected). The `MISC` label on the same row is correct (religious/ethnic → MISC rule).
- Reviewed named entities that appear in offensive comments: **no private individuals** — all are public figures or fictional characters. Offensive content is **retained** as authentic social-media usage, covered by the documented content warning.

## v1.0 — initial release (2026-06-24)
- 1,531 train / 400 test sentences, Cohen's κ = 0.873, stand-off, CC BY-NC-4.0.

_A broader annotation-quality review is ongoing; further corrections will ship in a future v1.1._
