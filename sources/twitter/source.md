# Source: Twitter / X (Moroccan Darija Arabizi)

**Status:** stub.

## Rationale
High named-entity density (politics, sport, celebrities, brands) — strong complement to YouTube for entity coverage.

## Provenance / licence (risks, not certainties)
- X developer agreement bars redistributing tweet **text**; standard practice = release **tweet IDs** for re-hydration.
- Tweets are personal data (GDPR) → pseudonymise; never release handles.
- Access: X API is paid/limited as of 2026 — confirm current tier/quota before committing effort.

## TODO
- `collect.py`: keyword/geo-seeded pull of Moroccan-Darija romanised tweets; emit `{text, source:"twitter", source_id}`.
- Decide collection route (API tier vs alternative) given cost.
