"""Curated Moroccan YouTube channels for Darija comment collection.

Web-grounded 2026-06-14 (handles/IDs verified against live channels / vidIQ / SocialBlade / Wikipedia — see notes).
The scraper prefers `channel_id` (UC..., most stable) and falls back to resolving `@handle` via the API. Entries with
neither are in UNVERIFIED (disabled) for manual completion.

Curation policy (per Achraf): prioritise ENTITY-DIVERSE, conversational Darija with quality comments.
  • DROP music/rap (lyric-dump comments) and football-dominated channels (repetitive player names).
  • DROP sensationalist tabloid/buzz (e.g. ChoufTV) — low-signal comments.
  • Latin-script (Arabizi) skews to YOUNGER audiences → talk/career/tech/vlog podcasts give the best Arabizi yield.
  • Politics/intellectual channels are entity-rich but comments skew ARABIC-SCRIPT → fewer Arabizi lines (still useful).

Recommended set for the Latin corpus: `--channel-set quality` (talk + society + politics, deduped).
"""

# --- Talk / podcasts / interviews / vlog (entity-diverse, latin-heavy → best Arabizi yield) ---
TALK = [
    {"name": "Masar wa Afkar", "channel_id": "UCw31cMEpWZ66LwrIlrY3P0Q", "handle": "@masarwaafkar",
     "note": "latin-heavy; career-journey interviews (varied fields → companies/schools/tools/cities)"},
    {"name": "GeeksBlaBla", "channel_id": "UCW2WV7NKU0WPyuv4YoNSqBA", "handle": "",
     "note": "latin-heavy; Moroccan tech community (devs/founders/companies/universities)"},
    {"name": "Radio Maarif", "channel_id": "UCmCV8H59mZSjtTh0rM9Pp9Q", "handle": "@radiomaarif",
     "note": "mixed; history/culture/icons podcast (Reda Allali) — varied figures/cities/tribes"},
    {"name": "MARYA & AMINE", "channel_id": "UCH1FOPC7QAueP2zd_D3cgIQ", "handle": "@MARYA_AMINE",
     "note": "latin-heavy; travel/vlog couple (LOC/ORG/PER-rich)"},
    {"name": "Laadiyoun", "channel_id": "UCh8qdCxA7FtP1nAwLKyL3Lw", "handle": "@laadiyoune",
     "note": "mixed; everyday-people/society travel"},
    {"name": "Tajriba", "channel_id": "UCVlqGg1WZjfwz5JPJ5cPF9g", "handle": "",
     "note": "latin-heavy; long-form 'game changers' interviews (Youssef El Allali) — recovered id"},
    {"name": "Arkadas vlog", "channel_id": "", "handle": "@arkadasvlog",
     "note": "latin-heavy; travel vlog (resolve by handle)"},
    {"name": "The Moroccan Podcast (ilal Internet Stories)", "channel_id": "UCJFH9V20yL9ceTWbHiwzV8Q", "handle": "@ilalinternetstories",
     "note": "latin-heavy; long-form Darija interviews"},
    {"name": "Data Maroc", "channel_id": "UC0eQAfZTFIvWZ9dZ45RIGEw", "handle": "@thedatamaroc",
     "note": "latin-heavy; data/society podcast"},
    {"name": "SOULIMA (Youssef Ksiyer)", "channel_id": "", "handle": "@youssefksiyer",
     "note": "latin-heavy; film/TV analysis in Darija (films/directors/actors/countries)"},
    {"name": "Podcast Maroc", "channel_id": "UC_RUhyZSiij0iO36Z_CzAeQ", "handle": "@Podcastmaroc",
     "note": "mixed; large general Moroccan interview podcast"},
    {"name": "Tomorocco Podcast", "channel_id": "", "handle": "@TomoroccoPodcast",
     "note": "mixed; Moroccan podcast (resolve by handle)"},
]

# --- Society / education / history (entity-rich, mixed script) ---
SOCIETY = [
    {"name": "Aji Tfham", "channel_id": "UC9JyBC7MshDg1uTyhm3UX3g", "handle": "@ajitfham",
     "note": "mixed; public-affairs explainers (elections/policy/economy/world events) — very entity-rich"},
    {"name": "Mustapha Swinga", "channel_id": "UCMPBiSwYY4fS1LYw4KkDZuw", "handle": "@mustaphaswingaofficiel",
     "note": "mixed; history/society explainers (people/dynasties/cities/institutions)"},
    {"name": "Najib El Mokhtari", "channel_id": "UCzNcnIeuGLXR4uAsJ6cP3kw", "handle": "@NajibElMokhtari",
     "note": "mixed; education/knowledge content"},
    {"name": "Misaha", "channel_id": "UCAHfrKOebWz6_23eKKm9vqw", "handle": "@misaha",
     "note": "mixed; society/ideas (Youssef Aabou)"},
    {"name": "Nationale Bedarija", "channel_id": "UCVDExRloqHhhgcBH88dU_Vw", "handle": "@nationalebedarija",
     "note": "latin-heavy; society/explainer in Darija"},
    {"name": "MAJAL", "channel_id": "UCVpPeRXp-9qwdOHYZgQIdIA", "handle": "@majal1",
     "note": "mixed; history/heritage (people/places/events)"},
    {"name": "L'Histoire Bdarija", "channel_id": "UC-eJa9uC_EBb1mK8TAjXPXg", "handle": "",
     "note": "mixed; Moroccan/world history in Darija (entity-dense)"},
    {"name": "Ayah Choukri — History of Morocco", "channel_id": "UCVVdzPAG4KENF9WlOHle-bQ", "handle": "",
     "note": "latin-heavy; Moroccan history storytelling (dynasties/sultans/cities; Morisco-relevant) — very entity-rich"},
    {"name": "Marocopedia", "channel_id": "", "handle": "@Marocopedia",
     "note": "mixed; Darija heritage mini-docs (villages/regions/crafts) — entity-dense"},
    {"name": "HistoireduMaroc", "channel_id": "", "handle": "@HistoireduMaroc",
     "note": "mixed; Moroccan history (entity-dense; some Arabic-script comments)"},
]

# --- Politics / intellectual (entity-rich, but comments skew ARABIC-script → fewer Arabizi) ---
POLITICS = [
    {"name": "Achachi Podcast (Rachid Achachi)", "channel_id": "", "handle": "@AchachiPodcast",
     "note": "arabic-heavy; economist/geopolitics analysis (politicians/parties/states/institutions). resolve by handle"},
    {"name": "Taoufik Bouachrine — Kalam fi al-Siyasa", "channel_id": "UCWI8rzerkLk1IABUnoenzfg", "handle": "@Taoufik_bouachrine",
     "note": "arabic-heavy; veteran journalist political-economy commentary (handle↔id not 100% disambiguated)"},
    {"name": "Maroc Hebdo — L'Info en Face", "channel_id": "UCi_psaiM_aWJnmJ43UXqoCQ", "handle": "",
     "note": "latin-heavy; FR/Darija elite political-affairs debate (good Latin yield for politics)"},
]

# --- News outlets (mostly ARABIC-script comments; ChoufTV dropped per curation policy) ---
NEWS = [
    {"name": "Hespress (Arabic)", "channel_id": "UCvyivffb2WwNKonKiLwVAEQ", "handle": "@hespress",
     "note": "flagship news; comments overwhelmingly Arabic-script (MLM/Arabic pile, not Arabizi)"},
    {"name": "Goud TV", "channel_id": "UC5KA6-w3CREqiDWW6Yq-z2w", "handle": "@goudtv7811",
     "note": "Darija-leaning; more Latin than other news"},
    {"name": "Le360 (Arabic)", "channel_id": "UCGYE6-D0--78oXa4wDiOk6g", "handle": "",
     "note": "major outlet; Arabic-script-heavy comments"},
    {"name": "Barlamane.com", "channel_id": "UCRZf0mP_Y__iN6Wc8445Y6w", "handle": "@Barlamanecomofficiel",
     "note": "Rabat news/politics; arabic-heavy"},
    {"name": "Médias24", "channel_id": "UC3D3-UgKi5DQVb4-nB9SBKw", "handle": "",
     "note": "economic news; bilingual FR/Darija"},
    # DROPPED (sensationalist/tabloid per policy): Chouf TV. Akhbarona/Rue20/LeSiteInfo also tabloid-ish — omit from quality.
]

# --- Broadcast TV (arabic-heavy comments) ---
MEDIA_TV = [
    {"name": "2M TV", "channel_id": "UClozwh5URilIQpDFeXch8qw", "handle": "@2mtv", "note": "~10M subs; arabic-heavy"},
    {"name": "Al Aoula (SNRT)", "channel_id": "UCuSyI3P8JZOD1nPa_pqjutg", "handle": "@AlAoulaTV", "note": "~3.2M subs; arabic-heavy"},
]

# --- Entertainment creators (vlog/comedy/gaming) — kept for volume; comedy/gaming are entity-SPARSE ---
CREATORS = [
    {"name": "Oussama BL", "channel_id": "UClSh66QSQuUw8oYGV9TMrCg", "handle": "@OussamaBL1", "note": "travel/food vlogs (LOC-rich)"},
    {"name": "Bilal Mouhouch (BIMO)", "channel_id": "UCH0cJKPdmB0XaTlF6iFC2mQ", "handle": "@bilalmouhouch", "note": "storytelling/cultural commentary"},
    {"name": "Amine Nkaity", "channel_id": "UC31a-0Ek3RpT-uM3wpIzrZQ", "handle": "@aminenkaity", "note": "storytelling/folklore (place names)"},
    {"name": "Youssef Zenzouni", "channel_id": "UCutpM3arN1QWHQdcfvj1_VA", "handle": "@youssefzenzouni", "note": "film recaps (foreign PER)"},
    {"name": "Simo Sedraty", "channel_id": "UCWkmLEuhRrDGPzRFvEBC7dw", "handle": "@SimoSedraty", "note": "comedy (entity-sparse)"},
    {"name": "Reda El Wahabi", "channel_id": "", "handle": "@redaelwahabi", "note": "challenges/vlogs"},
    {"name": "Kawtar Bamo", "channel_id": "", "handle": "@kawtarbamo", "note": "lifestyle/beauty vlogs"},
]

# --- Street-interview / vox-pop + young vlog (entity-rich, latin-heavy young audience) ---
STREET = [
    {"name": "Micro Ghassan", "channel_id": "UCZro4XZlPNYw1Dm7UWyefIg", "handle": "@ghassanofficiel",
     "note": "micro-trottoir; society/money/identity street Qs (names people/cities/figures) — strong entity yield"},
    {"name": "Alwankoum", "channel_id": "UCyaDuI8K0Ln2vqgFHAovCDw", "handle": "@alwankoum",
     "note": "~950K; daily street vox-pop (cities/neighbourhoods/current events)"},
    {"name": "Souhail Echaddini", "channel_id": "UCUB3GW9rS6DlRP9WWPuyYfg", "handle": "",
     "note": "~535K; society / social-experiment Q&A in Darija"},
    {"name": "TopTivi", "channel_id": "UC9AKSfOsVCJcHXDUrIlJSmw", "handle": "",
     "note": "Casablanca youth web-TV; street-interview segments (caution: some music/cinema segments)"},
    {"name": "Fayssal Vlog", "channel_id": "UCH_XMDSC8K696kE6I0x5D8Q", "handle": "@FayssalVlog",
     "note": "~3M; latin-heavy travel vlog (cities/countries/hotels/brands) — best vlog fit"},
    {"name": "Zineb Koutten", "channel_id": "UCwq3sgFAlir4jXSfpF2uDrg", "handle": "@zineb_koutten_",
     "note": "~250K; daily-life/storytime vlogs + brand collabs (places/brands)"},
    {"name": "Haytam Alaoui", "channel_id": "UCr4sM0TisClsOgAk3uIaCGw", "handle": "@Haytam.alaoui",
     "note": "latin-heavy; vlog"},
    {"name": "Adil Vlog", "channel_id": "UCiQB8MDYHAdE2pAuVt86t9A", "handle": "@AdilVlog1",
     "note": "vlog (daily life/travel)"},
    {"name": "jamil EL (Marrakchi)", "channel_id": "UCWzX7Zlgb8ax1-t-Qm3-LTQ", "handle": "",
     "note": "Marrakech vlog (mixed/arabic-leaning)"},
    {"name": "AYub Traveler", "channel_id": "UC_sZrfZHA2148MnD0NRztmg", "handle": "",
     "note": "travel vlog (LOC-rich)"},
]

# --- EXCLUDED per Achraf (kept for reference; NOT in any set) — lyric-dump / repetitive comments ---
MUSIC = [
    {"name": "7-TOUN", "channel_id": "UC2PRVeYNiJZ4LXLjRjufYig", "handle": "", "note": "rap — lyric-dump comments (excluded)"},
    {"name": "ElGrandeToto", "channel_id": "UCVG705xosVltZb52R0hHr_g", "handle": "", "note": "rap (excluded)"},
]

# --- Could NOT confirm id OR handle — verify before use (DISABLED) ---
UNVERIFIED = [
    {"name": "9addat", "channel_id": "", "handle": "", "note": "women role-model interviews; YT presence unverified"},
    {"name": "Hamid El Mahdaoui (Badil.info)", "channel_id": "", "handle": "", "note": "populist news/politics; arabic-heavy; id/handle unconfirmed"},
    {"name": "Maghareb (Errammach)", "channel_id": "", "handle": "", "note": "pan-Maghreb history, MSA-leaning; not Moroccan-Darija-specific"},
    {"name": "Fi Rass Derbe", "channel_id": "", "handle": "", "note": "audio-only (Spotify/iHeart) — no discoverable YouTube channel"},
    {"name": "+212 / Machi Rojola / The Moroccan Dudes / Les Bonnes Ondes", "channel_id": "", "handle": "", "note": "FRENCH/English-dominant — excluded (want Darija-Arabizi)"},
]

SETS: dict[str, list[dict]] = {
    "talk": TALK,
    "society": SOCIETY,
    "politics": POLITICS,
    "street": STREET,
    "news": NEWS,
    "media": NEWS + MEDIA_TV,
    "creators": CREATORS,
    "quality": TALK + SOCIETY + POLITICS + STREET,   # recommended: entity-diverse, no music/football/tabloid
    "all": TALK + SOCIETY + POLITICS + STREET + CREATORS + NEWS + MEDIA_TV,  # music excluded by policy
}


def get_set(name: str) -> list[dict]:
    if name not in SETS:
        raise KeyError(f"unknown channel set '{name}'; choose from {sorted(SETS)}")
    return SETS[name]


def identifiers(entries: list[dict]) -> list[str]:
    """One identifier per entry: channel_id if present else @handle; dedup; skip entries with neither."""
    seen, out = set(), []
    for e in entries:
        ident = e.get("channel_id") or e.get("handle")
        if ident and ident not in seen:
            seen.add(ident)
            out.append(ident)
    return out
