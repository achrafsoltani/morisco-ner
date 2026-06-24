I have all the data I need in the provided JSON. Let me write the concise markdown report directly.

# The "100% Moroccan" Novelty Layer

DarNERcorp's native Moroccan-Darija Arabizi gold set: **1,448 unique (surface, type) entities**, **2,420 total mentions**. Four phenomena ground the "100% Moroccan" novelty claim, followed by a native-review checklist of confirmed annotation issues.

---

## 1. French Code-Switching

**81 French / French-influenced entities, 216 mentions** (89 rows; 2 surfaces — *gilets jaunes*, *coupe du monde* — appear under two types). Breakdown: **LOC = 35, MISC = 27, ORG = 11, PER = 8**.

The signal is French orthography (accents é/è/ë/ô, cedilla ç), French articles/elision (la/le/l'/d'), and French-language acronyms used *in place of* English ones.

- **Accented country names (LOC):** *Algérie* (17), *Espagne* (6), *Afrique* (6), *Sénégal* (4); plus uniquely French geopolitical terms *Cisjordanie* (West Bank) and *région parisienne*.
- **French demonyms → MISC:** *algériens* (10), *algérien* (8), *français/française* (4 each), *sénégalais/sénégalaise* (3 each); cultural terms *gilets jaunes*, *Marche verte*, *franc cfa*, *téranga*.
- **French acronyms not English (ORG):** *FMI* (not IMF), *ONU* (not UN), *CEDEAO* (not ECOWAS); plus *Conseil de Sécurité*, *Fédération marocaine*, media brands *France24 / Franceinfo / TV5 / W9*.
- **French public/colonial figures (PER):** *Squeezie* (6), *Sarkozy*, *rachida dati*, *Jack Lang*, *Maréchal Lyautey / Hubert Lyautey* (Protectorate Resident-General), *Hervé Renard*.
- **Morocco-specific colonial toponymy & brands:** *Souss / Sous Massa Dar3a* (French administrative spelling), *French Protectorate*, French-spelled Moroccan brands *Afriquia*, *Marjane*, *Renault*; French competition names *Coupe du Trône*, *première ligue*.

---

## 2. Moroccan Honorifics & Span-Boundary Challenges

**16 entities, 26 mentions** carrying honorifics — and the gold reveals a **systematic, learnable asymmetry**.

- **INCLUDED in the span (name-bearing royal/aristocratic titles):** *mouly lhasan* (Moulay El Hassan, PER), *lala nezha* (Princess Lalla Nezha, PER).
- **Honorific-as-head (the bare title *is* the span):** *haj* (the coach referred to by title alone, PER), *ljlala* ("His Majesty / l-Jlala" → the King, PER).
- **EXCLUDED — the "Si" pattern (11 PER entities, 21 occurrences):** the polite/vocative particle *Si / A si* is consistently stripped, span starts at the name — *Yassine* (6), *boubker* (4), *benkirane* (2), *Reda* (2), plus *Abd El Krim*, *bou3arouf*, *baderdine*, *noureedin*.
- **Cultural-lineage edge case → MISC:** *Chrife* (Sharifian/Chorfa lineage) is kept in-span but tagged **MISC**, not PER, per the binding native rule (religious/ethnic descriptor).

**Boundary takeaway:** lexicalised name-bearing honorifics (Moulay, Lalla) stay inside the span; the vocative particle *Si* is always dropped — an asymmetry a model must learn explicitly.

---

## 3. Amazigh-Origin Entities

**20 entities, 52 mentions**, uniquely Moroccan, in three groups:

- **Amazigh-etymology toponyms (LOC):** *agadir* (= fortified granary, 23 — the single most frequent Amazigh entity), *AZROU* (= rock), *inezgane*, *tafrawt* (Tafraout), *Agadir Oufella* (upper kasbah), *Souss*, *narif* (the Rif via its Tarifit name).
- **Ethnic / identity / language terms → MISC** (binding native rule): *Imazighen* (5), *amazigh* (3), *tamazight* (2, the language), *swasa* (Souss people), *soussia*, *agadiri*.
- **ORG:** *Ultras imazighen* (HUSA Agadir Amazigh supporters' group).

Conservatively excluded to keep the count defensible: Arabic-etymology cities in Amazigh regions (Oujda, Nador, Berkane) and Arabic-origin surnames in Amazigh contexts.

---

## 4. Romanization Variation

The headline robustness signal: **207 clusters** (each ≥2 distinct spellings), covering **657 surface forms** and **1,394 mentions (~58% of all 2,420 mentions)** — every cluster groups *the same real-world entity* written many ways.

- **maroc — 12 spellings, freq 112:** maroc / Morocco / morroco / Marocco / maroco / Morrocco / lmaroco💞🤍😻.
- **maghrib — 20 spellings, freq 57:** maghrib / lmaghrib / mghrib / Maghreb / al maghrib / Maghriiiib / Mgherib.
- **Lmgharba (demonym) — 22 spellings, freq 53:** Lmgharba / MAGHRIBI / mgharba / mghribi / Moghrabi / magharyba.
- **wydad — 9 spellings, freq 63:** wydad / widad / lwidad / lwydad / WIYDAD / widaddi.
- **regragui — 7 spellings:** regragui / regragi / RAGRAGUI / Rgragi / Ragiragi / raguragui.

**Dominant variation axes (clusters touched):** vowel-drop 163, doubling/elongation 74, y/i 40, article-l (l-/al-/el-) 37, chat-digits (3/7/9…) 34, ou/u 14, k/q/c 11, g/j 5, ch/sh 4.

---

## 5. Native-Review Checklist (Confirmed Issues Only)

All 8 flagged issues were verified against the corpus and guidelines (`real_issue: true`, confidence high). Grouped by severity.

### High severity — demonym/cultural-noun mistagged as LOC (3)
- [ ] **`Marocaine` (LOC, freq 2)** — demonym tagged LOC; *"Marocaine francaise"* is a nationality, not a place. **Fix:** remove the spurious LOC span (token already correctly MISC); also repair collapsed `[0,0]` indices. Majority is MISC (10 vs LOC 3).
- [ ] **`marocains` (LOC, freq 1)** — plural demonym; *"militaires et policiers marocains"*. **Fix:** drop the duplicate LOC span layered on an already-correct MISC token. Majority MISC 13 vs LOC 2.
- [ ] **`cuisine Marocaine` (LOC, freq 1)** — cultural genre ("Moroccan cuisine"), not a place; cf. *rap marocain* correctly MISC. **Fix:** retag MISC (or O for the common-noun head); review span boundary.

### Medium severity — same-surface ORG/MISC conflict on a single referent (3)
- [ ] **`CAN` (freq 4 MISC vs 10 ORG)** — Africa Cup of Nations, one referent; lowercase *can* is an orthographic variant only. **Fix:** harmonise to ORG.
- [ ] **`CAF` (freq 1 MISC vs ~5–6 ORG)** — Confederation of African Football. **Fix:** harmonise to ORG.
- [ ] **`derby` (MISC, freq 2)** — common-noun sporting event; 6 other occurrences correctly left O; guidelines say events → O when in doubt. **Fix:** retag both to O (confirm not a named event).

### Low severity — tournament-name type inconsistency (1)
- [ ] **`coupe du monde` (freq ORG 2–3 vs MISC 1–5)** — World Cup, identical sense across taggings. **Fix:** normalise; note the report's prescribed ORG target is *not* scheme-grounded — guidelines treat recurring events as **O** (or arguably MISC), since the CAN sibling is itself split and offers no settled ORG convention.

---

## Distinctiveness vs Algerian NArabizi / NERDz

These four layers make DarNERcorp Morocco-specific rather than a generic Maghrebi Arabizi set: it carries French *colonial* toponymy and figures absent from Algerian corpora (Souss-Massa-Drâa, the French Protectorate, Maréchal Lyautey), French-spelled Moroccan brands (Afriquia, Marjane) and competitions (Coupe du Trône), plus a documented Amazigh-toponym layer (agadir ×23, Azrou, Tafraout) and a learnable honorific asymmetry (Moulay/Lalla kept in-span vs the always-stripped *Si* particle). Crucially, the binding native typing rule routes all nationalities, demonyms, cultural genres, and religious tokens (incl. *Allah/Lah*) to MISC — a consistent scheme decision that, with the 207-cluster (~58% of mentions) romanization-robustness challenge, differentiates the gold from NArabizi/NERDz at both the annotation-scheme and surface-variation levels.
