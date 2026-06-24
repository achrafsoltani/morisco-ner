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
*Arabizi* — with chat-digits `3`/`7`/`9`). To our knowledge, the first NER **training** corpus for Moroccan Darija in Latin
script (native NER corpora already exist for Algerian — NArabizi, NERDz).

*Part of the **Aljamiado** project (Moroccan Latin-script NLP); paired encoder: **MoRoBERTa**. The names evoke the Andalusi
Moriscos who resettled in Morocco and their Aljamiado cross-script writing tradition — the historical parallel to writing
Darija in Latin script. Released under `AchrafSoltani/` (HF id `morisco-ner`), grouped in the "Aljamiado" collection.*

## Dataset structure

| split | sentences | entities | source |
|---|---|---|---|
| train | 1,531 | 2,643 | entity-likely Moroccan YouTube Arabizi comments, natively annotated |
| test  | 400   | 252   | DODa Latin sentences, teacher-drafted then native-corrected |

Per-type (train): PER 845 · LOC 809 · MISC 616 · ORG 373 (1.73 entities/sentence). **No sentence overlap** between train and test.
The native-vs-translit ablation in the paper uses subsets up to 1,400 of this corpus (the extra 131 were annotated afterwards).

Each record: `{"tokens": [...], "spans": [[start, end, TYPE], ...]}` (token indices inclusive; stand-off).

## Tagset (CoNLL-4, after DarNERcorp)

- **PER** person names · **LOC** cities/countries/places · **ORG** organisations/institutions/companies/teams ·
  **MISC** nationalities/demonyms, languages, ethnic/religious/cultural groups & named cultural genres.
- **Binding native rule:** anything **cultural / ethnic / religious → MISC**, including religious figures
  (*Allah* / *Lah* → MISC, **not** PER, **not** O). This deliberately broadens DarNERcorp's nationality/language-centric MISC.

## Annotation

Two **native Moroccan-Darija co-annotators** — **Achraf Soltani** and **Soukaina Allali** — labelled disjoint portions
(700 and 831 sentences), in a review-and-correct workflow over a teacher draft. Inter-annotator agreement on a
doubly-annotated 200-sentence subset (independent, from scratch): **Cohen's κ = 0.873** (token; observed agreement 0.968),
entity-level F1 = **0.859 / 0.863** (exact/relaxed); per-type exact F1 PER 0.92 / LOC 0.95 / MISC 0.89 / ORG 0.75
(see `iaa/`). Disagreements (60/200) adjudicated.

### Moroccan-specific phenomena (analysis)
French code-switching (81 entities), Moroccan honorifics with a learnable boundary asymmetry (Moulay/Lalla kept in-span,
vocative *Si* stripped), Amazigh-origin entities (*agadir*, *Azrou*, *Tafraout*, *Imazighen*), and heavy romanization
variation (207 spelling clusters, ~58% of mentions). See `results/MOROCCAN-PHENOMENA.md`.

## Licensing & ethics

- **Licence:** CC BY-NC-4.0. Built from public YouTube comments and DODa (MIT); no private data.
- **Annotator credit:** the two native co-annotators — Achraf Soltani and Soukaina Allali — are credited here and
  acknowledged in the paper, **with their consent** (consent obtained 2026-06-13).

## Citation
```
[BibTeX — to be added on release; see paper/references.bib]
```
Base scheme: DarNERcorp (Moussa & Mourhir, 2023). Related: NArabizi (Riabi et al., 2023), NERDz (Touileb, 2022).
