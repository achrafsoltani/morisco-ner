# Source: Facebook (Moroccan Darija Arabizi comments)

**Status:** stub.

## Rationale
Large Moroccan-Darija comment volume; entity-dense (public-figure pages, news outlets, sport clubs).

## Provenance / licence (risks, not certainties)
- Facebook ToS prohibits automated collection; Graph API access to public-page comments is restricted/reviewed.
- Comments = personal data (GDPR) → pseudonymise; release stand-off + IDs only, never bulk text.
- Highest access friction of the social sources — treat as lower priority than YouTube/news unless a clean route exists.

## TODO
- `collect.py`: scope a compliant route (Graph API for owned/public pages, or a licensed dataset) before any scraping.
