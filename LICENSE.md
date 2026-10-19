# Licensing

This repository is **dual-licensed**, separating code from data (the same split used across the Aljamiado project).

## Code — Apache License 2.0
All pipeline, source and utility scripts (`pipeline/`, `sources/`, `*.py`) are licensed under Apache-2.0. Full text: [`LICENSE-CODE`](LICENSE-CODE).

## Data — Creative Commons Attribution-NonCommercial 4.0 (CC BY-NC 4.0)
The MoriscoNER annotations (`data/`, including the stand-off files and the annotation artefacts) are licensed **CC BY-NC 4.0**. Full text: [`LICENSE-DATA`](LICENSE-DATA), also at https://creativecommons.org/licenses/by-nc/4.0/legalcode.

- Attribution: MoriscoNER (Soltani, A.), part of the Aljamiado project. Annotators: Achraf Soltani, Soukaina Allali.
- NonCommercial: commercial use must be negotiated separately.
- Sources: public YouTube comments (released stand-off, see below) and the Darija Open Dataset (DODa, MIT); no private data.

## Redistribution boundary (binding)
We release the small transformed **stand-off** corpus (comment ids, token counts, text hashes and entity spans), a re-hydration script, the DODa-derived test set, and trained **models**. We do **not** redistribute the text of YouTube comments: the YouTube API terms forbid redistribution and cap storage, and comments are personal data under the GDPR. Users re-hydrate the text with their own API key; the raw collection is retained privately for research only. The repository history was rewritten on 2026-10-19 to remove files that had carried comment text since the first release.
