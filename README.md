# MoriscoNER

Native named-entity recognition corpus for **Moroccan Darija written in Latin script** (romanised / *Arabizi*,
with chat-digits `3`/`7`/`9`). CoNLL-4 tagset (PER / LOC / ORG / MISC). Released stand-off under **CC BY-NC 4.0**.

Part of the **Aljamiado** project (Moroccan Latin-script NLP). Paired encoder: **MoRoBERTa** (`huggingface.co/AchrafSoltani/MoRoBERTa`).
GitHub: `achrafsoltani/morisco-ner` · HF dataset: `AchrafSoltani/morisco-ner` · HF encoder: `AchrafSoltani/MoRoBERTa` — all openly released.

## Current corpus (v1)
| split | sentences | entities | source |
|---|---|---|---|
| train | 1,531 | 2,643 | entity-likely Moroccan YouTube Arabizi comments, natively annotated |
| test  | 400   | 252   | DODa Latin sentences, teacher-drafted then native-corrected (**frozen**) |

Two native co-annotators (Achraf Soltani, Soukaina Allali). IAA on a blind 200-sentence subset: **Cohen's κ = 0.873**.
See `DATASET_CARD.md`, `ANNOTATION-GUIDELINES.md`, and `docs/MOROCCAN-PHENOMENA.md`.

## Getting the training text (re-hydration)
The training split comes from public YouTube comments, whose text we may not redistribute. `data/*.standoff.jsonl` therefore carries, for each comment, its id, its token count, a SHA-1 of its tokens and the entity spans. Rebuild the token-level files with your own [YouTube Data API v3](https://developers.google.com/youtube/v3) key (about 63 quota units for the whole corpus):

```bash
export YT_API_KEY=...   # your own key
for f in arabizi_native_full arabizi_train_native morisco_iaa200_adjudicated; do
  python pipeline/rehydrate_youtube.py data/$f.standoff.jsonl data/$f.jsonl
done
```

Every rebuilt record is checked against its stored count and hash. Comments deleted or edited since collection cannot be recovered and are reported; in a spot check on 2026-10-19, 2 of 50 were no longer available.

## Layout
```
data/        stand-off training files, the DODa test set, and data/README.md (file map)
sources/     one folder per data source (collector + provenance note) → see sources/README.md
pipeline/    build stages: filter → teacher-draft → to-jsonl → QC → IAA → release
docs/        corpus analyses (Moroccan phenomena, etc.)
```

## Build pipeline (per source → corpus)
1. **collect** — `sources/<src>/` adapter pulls raw text for that source.
2. **filter** — `pipeline/filter.py` keeps Latin-script + entity-likely sentences.
3. **teacher-draft** — `pipeline/teacher_ner.py` / `arabizi_label.py` produce a draft labelling.
4. **annotate** — native review-and-correct, in batches.
5. **to-jsonl + QC** — `pipeline/batch_to_jsonl.py` → `pipeline/qc_annotations.py` (offset-grounding + comma-split fix).
6. **IAA** — `pipeline/make_iaa_pack.py` → `pipeline/iaa_score.py` (Cohen's κ) → adjudicate.
7. **release** — `pipeline/release_standoff.py` builds the Hugging Face release (stand-off training split, DODa test set, re-hydration script).

See `pipeline/README.md` for the stage contract and `sources/README.md` for the source registry.

## Setup
```bash
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
```

## Binding annotation rule
Anything **cultural / ethnic / religious → MISC**, including religious figures (*Allah* / *Lah* → MISC, not PER, not O).
This deliberately broadens DarNERcorp's nationality/language-centric MISC. See `ANNOTATION-GUIDELINES.md`.

## Licensing
Code (pipelines): **Apache-2.0** (`LICENSE-CODE`). Data: **CC BY-NC 4.0** (`LICENSE-DATA`), stand-off for the YouTube-derived split. Built from public YouTube comments and DODa (MIT); no private data. The text of YouTube comments is never redistributed (YouTube API terms / GDPR): only the stand-off corpus, the DODa test set, and trained models are released. See `LICENSE.md`.

## Citation
Soltani, A. MoriscoNER: A Native Moroccan-Darija Latin-Script NER Corpus and an Encoder-Conditional Native-vs-Transliteration Study. In: Proceedings of IANLP 2026, Advances in Computer Science Applications and Research. Springer (in press).

## Versions
See `CHANGELOG.md` for release history and corrections.
