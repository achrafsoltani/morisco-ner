# Source: YouTube (Moroccan Darija Arabizi comments)

**Status:** populated — the v1 MoriscoNER train set (1,531 sentences) was collected and annotated from here.

## Collectors
- `yt_collect.py`, `yt_collect2.py` — pull comment threads from Moroccan channels (YouTube Data API v3).
- `yt_label_split.py` — split collected comments into the entity-likely annotation stream vs the bulk MLM stream.

## Provenance / licence
- Script form: Latin / Arabizi (chat-digits 3/7/9/2).
- **YouTube API ToS:** comment text must not be redistributed; API data not stored > 30 days. → release **stand-off corpus
  + comment IDs + a documented sample + models**, never bulk raw text. Private backup in this repo only.
- Comments are **personal data** (GDPR) — strip/avoid usernames and channel IDs in any release; pseudonymise.

## Quota note (grounded)
YouTube Data API v3: 10,000 units/day default; `commentThreads.list` = 1 unit / up to 100 comments
→ ~1M comments/day theoretical ceiling per project (before Arabizi filtering + dedup, which cut this sharply).

## Next
- Re-run with a broader, documented channel list across domains (news, sport, entertainment, vlogs) to diversify entities.
- Keep the entity-likely slice for annotation; route the rest to the MoRoBERTa-large MLM corpus (`../../../moroberta-encoder/`).
