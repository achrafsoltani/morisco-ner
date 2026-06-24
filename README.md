# MoriscoNER

Native named-entity recognition corpus for **Moroccan Darija written in Latin script** (romanised / *Arabizi*,
with chat-digits `3`/`7`/`9`). CoNLL-4 tagset (PER / LOC / ORG / MISC). Released stand-off under **CC BY-NC 4.0**.

Part of the **Aljamiado** project (Moroccan Latin-script NLP). Paired encoder: **MoRoBERTa** (`huggingface.co/AchrafSoltani/MoRoBERTa`).
GitHub: `achrafsoltani/morisco-ner` · HF dataset: `AchrafSoltani/morisco-ner` · HF encoder: `AchrafSoltani/MoRoBERTa` — all openly released.

## Why this is its own repo
MoriscoNER is a shared, separately-released resource consumed by **two** papers — the submitted Aljamiado NER paper
(`../ianlp2026-moroccan-aljamiado-ner/`) and **MoRoBERTa-large** (`../moroberta-encoder/`, eval bed). It was extracted
non-destructively from the submitted paper repo on 2026-06-14; that repo keeps its own frozen snapshot for reproducibility.
This repo is now the **canonical** home for the corpus and its build pipelines. Encoder training, scaling experiments and
distillation scripts stay in the consuming repos — they are **not** here.

## Current corpus (v1, from the Aljamiado paper)
| split | sentences | entities | source |
|---|---|---|---|
| train | 1,531 | 2,643 | entity-likely Moroccan YouTube Arabizi comments, natively annotated |
| test  | 400   | 252   | DODa Latin sentences, teacher-drafted then native-corrected (**frozen**) |

Two native co-annotators (Achraf Soltani, Soukaina Allali). IAA on a blind 200-sentence subset: **Cohen's κ = 0.873**.
See `DATASET_CARD.md`, `ANNOTATION-GUIDELINES.md`, `docs/MOROCCAN-PHENOMENA.md`, `iaa/`.

## Layout
```
data/        canonical corpus (JSONL: {"tokens":[...], "spans":[[s,e,TYPE],...]}) + data/README.md (file map)
annotation/  raw native-annotation batches (CSV) + labelled master
iaa/         inter-annotator-agreement packs, scorer output, adjudication, offensive-content review
sources/     one folder per data source (collector + provenance note) → see sources/README.md
pipeline/    shared build stages applied to any source: filter → teacher-draft → to-jsonl → QC → IAA → release
docs/        corpus analyses (Moroccan phenomena, etc.)
```

## Build pipeline (per source → corpus)
1. **collect** — `sources/<src>/` adapter pulls raw text for that source.
2. **filter** — `pipeline/filter.py` keeps Latin-script + entity-likely sentences.
3. **teacher-draft** — `pipeline/teacher_ner.py` / `arabizi_label.py` produce a draft labelling.
4. **annotate** — native review-and-correct, in batches (`annotation/`).
5. **to-jsonl + QC** — `pipeline/batch_to_jsonl.py` → `pipeline/qc_annotations.py` (offset-grounding + comma-split fix).
6. **IAA** — `pipeline/make_iaa_pack.py` → `pipeline/iaa_score.py` (Cohen's κ) → adjudicate.
7. **release** — `pipeline/release_standoff.py` emits the CC-BY-NC stand-off HF dataset (on acceptance).

See `pipeline/README.md` for the stage contract and `sources/README.md` for the source registry.

## Setup
```bash
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
```

## Binding annotation rule (carry-over, do not change)
Anything **cultural / ethnic / religious → MISC**, including religious figures (*Allah* / *Lah* → MISC, not PER, not O).
This deliberately broadens DarNERcorp's nationality/language-centric MISC. See `ANNOTATION-GUIDELINES.md`.

## Licensing
Code (pipelines): **Apache-2.0**. Data: **CC BY-NC 4.0**, stand-off. Built from public YouTube comments + DODa; no private
data. Raw bulk-scraped text is **never** redistributed (YouTube ToS / GDPR) — only the small transformed stand-off corpus,
the documented sample, and trained models are released. See `LICENSE.md`.
