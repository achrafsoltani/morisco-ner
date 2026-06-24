# Source: DODa (Darija Open Dataset)

**Status:** stub (used for the frozen test set; low new-entity yield).

## What it is
DODa v2 — ~45,378 Latin-script Moroccan-Darija sentences (Latin is DODa's primary/original script), translation pairs
with English/French. The single largest **downloadable, licence-clean** Latin Moroccan sentence resource.

## Provenance / licence (grounded)
- **CC BY-NC 4.0** (non-commercial; commercial use negotiated separately) — arXiv:2405.13016 §3.3.
- Downloadable: https://github.com/darija-open-dataset/dataset , https://darija-open-dataset.github.io/

## Role here
- Provided the **400-sentence frozen test** (teacher-drafted, native-corrected).
- Translation pairs are **entity-sparse**; entity-likely sentences are **nearly exhausted** (~194 left) → little value for
  growing the labelled train set. Best used as clean filler for the MoRoBERTa-large MLM corpus (CC BY-NC permits research use).

## TODO
- `collect.py`: load DODa v2 sentences.csv, isolate the Latin-script column, dedup vs existing corpus.
