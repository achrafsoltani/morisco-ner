# Arabizi NER annotation guidelines (Darija)

Scope: **4 entity types only**, matching DarNERcorp (so the test set is consistent with the training gold):
**PER, LOC, ORG, MISC.** Everything else is **O** (not tagged).

## What each type covers (grounded in DarNERcorp's own gold)
- **PER** — person names (real, historical, fictional): محمد, أرسطو (Aristotle), Latifa Bouhsini, Roger Blench, Mona, Sartre.
- **LOC** — cities, countries, places: مراكش, فرانسا, ألمانيا, طنجة, الدار البيضاء, مصر, Argentina, Koutoubia, El Jadida.
- **ORG** — organisations, institutions, companies, brands, teams, empires: الأمم المتحدة, اليونسكو, OPEC,
  كوكا كولا (Coca-Cola), الإمبراطورية الرومانية, **Inwi** (telecom).
- **MISC** — the catch-all, but in DarNERcorp it means specifically: **nationalities/demonyms** (المغربي = Moroccan,
  almany = German, indonisi = Indonesian), **languages** (العربية, الدارجة, anglais = English), **ethnic/religious/cultural
  groups** (اليهود = Jews, المسيحية = Christianity, الأمازيغية = Amazigh, العيطة = Aita genre).
  - **Native broadening (binding, 2026-06-13): anything CULTURAL or ETHNIC → MISC.** This includes **religious figures**:
    **Allah / Lah / Lah ir7am → MISC** (a religious figure is **not** a PER, and is **not** left O). When a token is cultural,
    ethnic, or religious in nature, prefer MISC over O.

## NOT tagged (O)
Dates, days of the week, times, numbers/quantities/percentages, common nouns, pronouns, ordinary adjectives.
**Events** (e.g. WWII), products, and works are *not* clearly MISC in DarNERcorp (its MISC is nationality/language-centric)
→ when in doubt, leave **O** for consistency.

## Disambiguation rules (binding, 2026-06-13 — settled during IAA adjudication)
- **Competitions / leagues / tournaments → ORG** (apply uniformly): AFCON / CAN, World Cup / coupe du monde, Coupe du Trône,
  Botola, première ligue. (We tag the named competition as ORG since the 4-type scheme has no EVENT type.)
- **Governing bodies / federations / confederations → ORG**: CAF, FRMF, FIFA. (Distinct from the competition, but both ORG.)
- **Clubs / teams → ORG**: Wydad/WAC, Raja (Raja is the club, NOT a LOC). Tag **PER** only if "Widad"/"Raja" is a *person's* name in context.
- **Companies / brands → ORG** (Inwi, Coca-Cola, Yamaha); **specific products / models → O** (TMAX, iPhone, a car model).
- **Non-competition cultural events** (moussem/festival, religious occasions) → **MISC** (per the cultural→MISC rule), else O.

## The CSV workflow (`data/arabizi_draft_review.csv`)
- Edit **only column C4 (`CORRECTION`)**, and only where C3 (`predicted_entities`) is wrong or incomplete.
- C3 correct → **leave C4 empty** (C3 is accepted).
- C3 wrong/incomplete → write the **full corrected list** in C4, same format as C3: `text[TYPE]; text[TYPE]`
  (copy C3 then adjust). C4 **replaces** C3.
- No entities (and C3 wrongly has some) → write **`NONE`** in C4.
- Entity text must be **copied verbatim from C1 (the arabizi)**.
- Row 1 is the header — do not edit. C2 (english, from DODa) is a reading aid only — ignore its translation errors;
  annotate from C1 (arabizi) using native understanding.

## Final gold = C4 if non-empty, else C3.
