# Licensing

This repository is **dual-licensed**, separating code from data (the same split used across the Aljamiado project).

## Code — Apache License 2.0
All pipeline/source/utility scripts (`pipeline/`, `sources/`, `*.py`) are licensed under Apache-2.0.
Drop the full `LICENSE-CODE` (Apache-2.0 text) here before public release.

## Data — Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0)
The MoriscoNER corpus (`data/`, the released stand-off splits, annotation artefacts) is licensed **CC BY-NC 4.0**.
Full text: https://creativecommons.org/licenses/by-nc/4.0/legalcode . Drop `LICENSE-DATA` here before public release.

- Attribution: MoriscoNER (Soltani, A.), part of the Aljamiado project. Annotators: Achraf Soltani, Soukaina Allali.
- NonCommercial: commercial use must be negotiated separately.
- Built from public YouTube comments + DODa (CC BY-NC 4.0); no private data.

## Redistribution boundary (binding)
We release the small **transformed stand-off corpus**, optional **source IDs** for re-hydration, a documented **sample**,
and trained **models**. We do **not** redistribute bulk raw scraped text (YouTube API ToS forbids redistribution and caps
storage at 30 days; comments are personal data under GDPR). Raw collection is retained privately for research only.

## Release timing
Public release (GitHub public + HF `AchrafSoltani/morisco-ner`) happens **on paper acceptance only** — earlier public
release would break the double-blind review of the consuming papers.
