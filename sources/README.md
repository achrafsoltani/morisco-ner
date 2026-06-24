# sources/ — data-source registry

Each source is a self-contained adapter folder that produces **raw candidate sentences** for the shared `pipeline/`.
A source folder contains: a collector script, a `source.md` provenance note, and a (gitignored) `raw/` output dir.
The point of the split: MoriscoNER must **not** depend on a single platform. Named entities (people, places, teams,
brands) are sparse in translation corpora and dense in social/news text — so we diversify deliberately.

## Registry

| Source | Script form | Licence / redistribution | Entity density | Volume potential | Status |
|---|---|---|---|---|---|
| **youtube** | Latin Arabizi | YouTube ToS — text **not** redistributable (release model + IDs/stand-off only) | high | very high (~1M comments/day API ceiling) | **populated** — v1 train (1,531) came from here |
| **doda** | Latin (DODa native) | **CC BY-NC 4.0**, downloadable | low (translation pairs) | ~45K sentences (entity-likely ≈ exhausted, ~194 left) | test source; little new entity yield |
| **twitter** | Latin Arabizi | X dev terms — IDs-only rehydration; text not redistributable | high | medium–high | stub |
| **facebook** | Latin Arabizi | ToS-constrained; access-limited | high | medium | stub |
| **news** | Latin Arabizi (comments) | site ToS; comments = personal data (GDPR) | high (politics/sport/entertainment) | medium | stub (e.g. Hespress comment sections) |

## Why each role differs
- **youtube / twitter / facebook / news** → the *entity-dense* well. These feed both MoriscoNER (the entity-likely slice,
  then annotated) **and** the MoRoBERTa-large unlabelled MLM corpus (the bulk, un-annotated). Raw text stays internal.
- **doda** → already-licensed, downloadable, but entity-sparse and nearly exhausted for entity-likely sentences; best for
  the frozen test set and as clean MLM filler, not for growing the labelled train set.

## Redistribution rule (binding)
Scraped raw text is **never** committed to the public release or a public repo. We release: (1) the small transformed
**stand-off** corpus (CC BY-NC), (2) optionally **comment IDs / offsets** for re-hydration, (3) a documented sample,
(4) trained **models**. This is the same pattern DarijaBERT / atlasia / MorRoBERTa used (models, not corpora). Private
backup of raw batches in this repo is fine; public bulk-text release is not.

## Adding a source
Copy `_adapter_template.py` into a new `sources/<name>/`, implement `collect()` to emit JSONL of
`{"text": ..., "source": "<name>", "source_id": ...}` into `sources/<name>/raw/`, write `source.md`, then run the
shared `pipeline/` stages. Register it in the table above.
