# Source: News-site comments (e.g. Hespress)

**Status:** stub.

## Rationale
Moroccan news comment sections (Hespress and similar) are a rich, openly-readable well of Latin-script Darija with **high
entity density** (politicians, places, institutions, events) — and a different register from YouTube/social chatter, which
improves domain coverage of the corpus.

## Provenance / licence (risks, not certainties)
- Site terms of service govern scraping; comments are user personal data (GDPR) → pseudonymise, no usernames in release.
- Release stand-off + offsets + sample, not bulk text. Confirm each site's robots.txt / ToS before collecting.

## TODO
- `collect.py`: paginate article comment sections; emit `{text, source:"news", source_id:<article+comment id>}`.
- Add a section/topic spread (politics, economy, sport, society) for entity-type balance.
