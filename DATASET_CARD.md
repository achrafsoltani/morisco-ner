---
language:
  - ary
license: cc-by-nc-4.0
task_categories:
  - token-classification
task_ids:
  - named-entity-recognition
pretty_name: MoriscoNER
size_categories:
  - 1K<n<10K
annotations_creators:
  - expert-generated
language_creators:
  - found
multilinguality:
  - monolingual
tags:
  - moroccan-darija
  - arabizi
  - latin-script
  - named-entity-recognition
  - low-resource
  - code-switching
---

# MoriscoNER — Native Moroccan-Darija Latin-script NER

A native-annotated named-entity recognition dataset for **Moroccan Darija written in Latin script** (romanised, a.k.a.
*Arabizi* — with chat-digits `3`/`7`/`9`). To our knowledge, the first NER **training** corpus annotated natively in Latin-script Moroccan Darija. Native Latin-script NER corpora already exist for Algerian (NArabizi, NERDz), and the multi-dialect Maghrebi benchmark of Mahdhaoui et al. (ICAART 2026) covers Moroccan Darija mostly in Arabic script and transliterates the Arabizi entities it contains.

*Part of the **Aljamiado** project (Moroccan Latin-script NLP); paired encoder: **MoRoBERTa** (`AchrafSoltani/MoRoBERTa`). The names evoke the Andalusi Moriscos who resettled in Morocco and their Aljamiado cross-script writing tradition — the historical parallel to writing Darija in Latin script.*

## Dataset structure

| split | sentences | entities | source |
|---|---|---|---|
| train | 1,531 | 2,643 | entity-likely Moroccan YouTube Arabizi comments, natively annotated |
| test  | 400   | 252   | DODa Latin sentences, teacher-drafted then native-corrected |

Per-type (train): PER 845 · LOC 809 · MISC 616 · ORG 373 (1.73 entities/sentence). **No sentence overlap** between train and test.
The native-vs-translit ablation in the paper uses subsets up to 1,400 of this corpus (the extra 131 were annotated afterwards).

The training split is released **stand-off**, because the text of YouTube comments may not be redistributed: each record is `{"comment_id", "n_tokens", "text_sha1", "spans": [[start, end, TYPE], ...]}` (token indices inclusive). `rehydrate_youtube.py` rebuilds `{"tokens", "spans"}` records with your own YouTube Data API key and checks each one against its count and hash; comments deleted or edited since collection cannot be recovered (2 of 50 in a spot check on 2026-10-19). The test split carries its text: `{"tokens": [...], "spans": [...]}`, from DODa (MIT).

## Tagset (CoNLL-4, after DarNERcorp)

- **PER** person names · **LOC** cities/countries/places · **ORG** organisations/institutions/companies/teams ·
  **MISC** nationalities/demonyms, languages, ethnic/religious/cultural groups & named cultural genres.
- **Binding native rule:** anything **cultural / ethnic / religious → MISC**, including religious figures
  (*Allah* / *Lah* → MISC, **not** PER, **not** O). This deliberately broadens DarNERcorp's nationality/language-centric MISC.

## Annotation

Two **native Moroccan-Darija co-annotators** — **Achraf Soltani** and **Soukaina Allali** — labelled disjoint portions
(700 and 831 sentences), in a review-and-correct workflow over a teacher draft. Inter-annotator agreement on a
doubly-annotated 200-sentence subset (independent, from scratch): **Cohen's κ = 0.873** (token; observed agreement 0.968),
entity-level F1 = **0.859 / 0.863** (exact/relaxed); per-type exact F1 PER 0.92 / LOC 0.95 / MISC 0.89 / ORG 0.75.
Disagreements (60/200) adjudicated.

### Moroccan-specific phenomena (analysis)
French code-switching (81 entities), Moroccan honorifics with a learnable boundary asymmetry (Moulay/Lalla kept in-span,
vocative *Si* stripped), Amazigh-origin entities (*agadir*, *Azrou*, *Tafraout*, *Imazighen*), and heavy romanization
variation (207 spelling clusters, ~58% of mentions). See `docs/MOROCCAN-PHENOMENA.md`.

## Licensing & ethics

- **Licence:** CC BY-NC-4.0. Built from public YouTube comments (released stand-off; the comment text is not redistributed) and DODa (MIT); no private data.
- **Annotator credit:** the two native co-annotators — Achraf Soltani and Soukaina Allali — are credited here and
  acknowledged in the paper, **with their consent** (consent obtained 2026-06-13).

## Citation
```bibtex
@inproceedings{soltani2026morisconer,
  title     = {{MoriscoNER}: A Native {Moroccan-Darija} Latin-Script {NER} Corpus and an Encoder-Conditional Native-vs-Transliteration Study},
  author    = {Soltani, Achraf},
  booktitle = {Proceedings of IANLP 2026},
  series    = {Advances in Computer Science Applications and Research},
  publisher = {Springer},
  year      = {2026},
  note      = {in press}
}
```
Base scheme: DarNERcorp (Moussa & Mourhir, 2023). Related: NArabizi (Riabi et al., 2023), NERDz (Touileb, 2022).
