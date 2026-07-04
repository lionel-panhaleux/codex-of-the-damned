# TODO

Findings from the 2026-07-04 full-site review, ordered by priority.
Every P0 item was verified by actually rendering the pages / reading the code.

## P0 — Broken for readers right now

- [ ] **Fix ~45 `{% trans %}` blocks referencing undeclared variables** — Jinja renders
  undefined variables as empty strings, so card names silently vanish from the prose
  (e.g. Malkarishat renders *"together with the infamour ."*). Known sites:
  - `archetypes/new-kids/malkarishat.html:14` — trans header declares nothing, all 16
    card refs empty (arishat, ashur_tablets, condemnation_mute, deflection,
    elder_impersonation, forgotten_labyrinth, govern_the_unaligned, juliet_parr,
    kine_resources_contested, lost_in_crowds, my_kin_against_the_world, obedience,
    parity_shift, stealth, the_sargon_fragment, unleash_hell_s_fury)
  - `archetypes/new-kids/piper-war-ghoul-24.html:14` — deep_ecology, one_with_the_land
  - `archetypes/top-tier/`: gangrel-thing.html:14 (club_illusion, villein),
    illegal-brawl.html:14 (chimerstry), lutz-politics.html:14 (ancient_influence,
    force_of_personality, information_highway, perfect_paragon, ubende),
    mistress.html:14 (rutors_hand), platinum-revelation.html:14 (minion_tap),
    princess-toolbox.html:14 (anonymous_freight, bonding, nra_pac, rego_motum,
    smiling_jack_the_anarch), stanislava.html:14 (enkil_cog, freak_drive),
    the-unnamed.html:14 (vessel), tupdogs.html:14 (target_vitals)
  - `archetypes/runner-ups/`: dementation-bleed, forced-ball, infernal-barons,
    lasombra-nocturn, protean-barons (all :14)
  - `archetypes/archive/`: anson-guns, chameleon, emerald-legion, khazars-diary,
    nananimalism, tzimisce-toolbox, war-ghouls, weenie-aus (all :14)
  - `best-cards/clans/`: harbingers-of-skulls.html:43 (`ventre_antitribu` typo →
    ventrue_antitribu), :57/:64 (emerald_legion), malkavian.html:99, ministry.html:154,
    nosferatu.html:30/:101, salubri.html:94, salubri-antitribu.html:56/:63,
    toreador.html:89, tremere.html:7 (`aud` typo → `aus`), :48, :68,
    tremere-antitribu.html:48
  - `best-cards/generic/`: blood-sorcery.html:67 (flash), master-cards.html:27 (villein)
  - `strategy/`: archetype-categories.html:101 (malk_22, malk_94 — probably meant
    `link()` calls), combat.html:234 (assault_rifle), fundamentals.html:302
    (atonement, cats_guidance, guardian_vigil)
- [ ] **Add a lint test that catches the above class of bug forever**: extract
  `{% trans %}` block bodies, diff the `{{ var }}` names against declared kwargs +
  `BASE_CONTEXT` keys. Pure-offline, fast, belongs in the regular pytest run.
  Consider also making `link()` raise (or warn under TESTING) on unknown paths
  instead of returning `""`.
- [ ] **Best Cards index: two clan pages unreachable** — `best-cards/index.html:76,84`
  have `" warn"` inside the link *path* instead of `_class`
  (`link("/best-cards/clans/daughters-of-cacophony warn", ...)`), and `link()`
  silently returns `""`. Daughters of Cacophony and Ishtarri are orphaned.
- [ ] **Reflected XSS in both search pages** — raw `?card=` / `?id=` URL params flow
  into `Error(...)` messages rendered via `innerHTML`:
  `static/js/card-search.js:76` + `:264`, `static/js/deck-search.js:162` + `:203`.
  Fix: use `textContent` for these two message assignments.
- [ ] **Make `make test` green again**:
  - [ ] `black` fails on `codex_of_the_damned/navigation.py` — run `black` on it.
  - [ ] 3 tests fail on DriveThruRPG/DriveThruCards links (their anti-bot layer 403s
    any non-browser client, even with a browser User-Agent). Add both domains to the
    skip-list in `tests/test_pages.py:32-38` next to eBay/Reddit/Kickstarter; verify
    the links once manually in a real browser.

## P1 — Cheap, high-value fixes

### SEO / metadata
- [ ] `<title>` is hardcoded to "Codex of the Damned" on all pages
  (`templates/layout.html:39`) while the per-page `title()` helper already exists and
  feeds `og:title`. Change to `<title>{{ title() }}</title>`. Biggest SEO win available.
- [ ] Remove (or migrate to GA4) the dead Universal Analytics tag `UA-157267369-1`
  (`layout.html:28-35`) — collecting nothing since mid-2023, still loaded on every page.
  KISS-est option: delete it.
- [ ] Add `<link rel="alternate" hreflang="en|fr|x-default">` + `rel="canonical"` for
  the parallel `/en/`–`/fr/` URL scheme. Currently absent site-wide.
- [ ] Same hardcoded `<meta name="description">` on every page (`layout.html:21`) —
  allow per-page override (the existing `{% block meta %}` is only used for decklists).

### Markup bugs
- [ ] 8× `target=" _blank"` (leading space) in `templates/index.html`
  (lines 131, 223, 230, 237, 244, 251, 258, 265).
- [ ] 12 anchors with a stray comma between attributes (`<a href="…" , target="_blank">`)
  in `strategy/articles/basic/what-should-i-buy.html`
  (lines 1571, 1578-1580, 1586, 1602, 1608-1609, 1614-1617, 1622).
- [ ] Add `rel="noopener"` centrally: in the `external()` helper
  (`codex_of_the_damned/__init__.py:358`) + the raw `target="_blank"` anchors in
  templates. Site-wide there are currently zero occurrences of noopener.
- [ ] Invalid ARIA role `role="translation"` (`layout.html:81`) — use
  `<nav aria-label="Language">` or similar.
- [ ] Double `<h1>` on every page: site logo h1 (`layout.html:47`) + content h1.
  Demote the logo heading (or make it h1 only on the homepage).
- [ ] Missing `alt` attributes: `index.html:44` (Discord widget), `index.html:351`
  (dark-pack.png), `deck-search.html:41` + `archetypes/_layout.html:12` (VDB favicon),
  `online-play/lackeyccg.html:95`, `strategy/table-talk.html:266`.
- [ ] `fundamentals.html:295` has invalid `</ li>`.

### Dead code / stale scaffolding
- [ ] Delete `templates/_layout_promo.html` + its import (`layout.html:1`) — imported
  but never rendered, contains a stale "April 20th, 2024 Grand Prix in Paris" ad.
- [ ] Delete (or write) `strategy/articles/advanced/guide-for-competitive-play.html` —
  0-byte orphan since 2024-07, not referenced in `navigation.py`.
- [ ] Deduplicate the card-image slug logic: `__init__.py:267-271` (og_image block)
  re-implements `file_name()` (`__init__.py:381-386`) with a weaker regex. Use
  `file_name()` and drop the plain-`http://` og:image at `:272` (keep https only).
- [ ] Upgrade plain `http://` hrefs where HTTPS exists: vekn.fr/vekn.net links
  (`deck-search.html:15`, `card-search.html:14`, `archetypes/index.html:13,189`,
  `best-cards/index.html:7`, `index.html:47,50`, 2 advanced articles), plus
  `index.html:85,288`, `strategy/deck-building.html:38,48`.
- [ ] `strategy/deck-guides/_layout.html:21` ships a literal `href="http://example.com"`
  placeholder — confirm every child guide overrides it.

## P2 — Content refresh (feeds the planned TWDA-agent work)

- [ ] Archetypes: newest example decklist is 2025-03-10; "New Kids" newest is
  Piper War Ghoul **'24**. Tier assignments need fresh TWDA stats for the 2026 meta.
  Index criteria ("proven twice in the last 3 years", ⭐ = 50%+ more wins) are
  date-window claims that drift — recompute.
- [ ] Best Cards: "900+ decks from 2020 onward" (`best-cards/index.html:12`) computed
  ~2025-03 — same refresh.
- [ ] What Should I Buy: the "upcoming V5 format" insert
  (`what-should-i-buy.html:260-289`) says "announced, no precise list yet" — almost
  certainly superseded; verify on vekn.net and rewrite. Product list stops at
  30th Anniversary (2024) — check 2025-26 Black Chantry releases.
- [ ] Online Play: re-verify the two LackeyCCG Discord invites (`discord.gg/fJjac75`,
  `discord.gg/QJtDzp5`) and the "foremost platform, up-to-date cardwise" claim.
- [ ] Anthelios ban year stated as 2016 in `archetypes/_layout-erratum.html:95` +
  `archive/dmitris-big-band.html:61` but 2017 in `what-should-i-buy.html:1222`
  (announced vs effective, probably) — pick one.
- [ ] Typo sweep: "Methusalah" (16×, correct "Methuselah" only 10×), particularily,
  loosing, successfuly, independant(ly), recommanded, unneccessary, "infamour",
  "Maris streck" (piper-war-ghoul-24).
- [ ] Garbled prose: `fundamentals.html:32-33` (mangled sentence about non-limited
  bleed modifiers — the rule itself is stated correctly elsewhere),
  `piper-war-ghoul-24.html:76-77` ends mid-thought ("there is no need to fret").
- [ ] i18n chrome gaps (content pages are fine): `index.html:82-89` ("Deck builder:",
  "Cards finder:", "Telegram Bot:", "Forum VEKN France" unwrapped),
  `deck-search.html:23,29` + `card-search.html:22` (placeholder/value attributes).

## P3 — Performance (KISS-compatible)

- [ ] Font `src` ordering: browsers pick the first supported format, which is
  `truetype` — the woff2 files are never used (`static/css/base.css:32-34,40-42`).
  Put `woff2` first (~halves font bytes: fa-solid TTF is 192 KB vs 76 KB woff2);
  drop the dead `.eot`/`.svg` entries.
- [ ] Compress the big PNG/JPG screenshots to WebP (rest of the site already is):
  `lackeyccg-interface.png` 2.0 MB, `tts-rotation.jpg` + `tts-table.jpg` 1.7 MB each,
  `lackeyccg-deck-browse.png` 1.4 MB, `tommi_hakomaa.png` 1.0 MB, more in `static/img/`.
- [ ] No `<img>` on the site carries `width`/`height` — add them (at least on the
  large screenshots) to avoid layout shift.
- [ ] `base.css:944` `.autocomplete-items { overflow: scroll }` → `auto` (cosmetic).

## P4 — Small JS bugs

- [ ] `static/js/complete.js:22-24` — catch block uses `this.message` but the field is
  `this.message_output`; autocomplete fetch failures are silently swallowed.
- [ ] `static/js/statistics.js:20-27` — `howManyNeeded` returns `undefined` when no
  copy count reaches the target probability; deck-building calculator prints
  "undefined copies". Return the stack size (or a message) as a floor.
- [ ] `static/js/card-search.js:213` — leftover `console.log(ruling_text)`.
- [ ] `static/js/complete.js:77-80` — `Completion.reset()` is dead and would throw
  (`div.reset()` doesn't exist); delete.
- [ ] `static/js/complete.js:115` — `encodeUrlParam` only replaces the first `/`
  (string arg to `replace`); use a global regex.
- [ ] `display.js:26` has an `es` branch that is unreachable while `config.py:8` only
  lists en/fr — keep in mind for the ES translation work (don't delete).

## Backlog — to discuss before acting

1. **Framework**: entire backend is ~750 lines of Python; Babel i18n and the
   `navigation.py` tree are the only real coupling. A pure jinja-to-static build
   looks very tractable. Decide: Flask stays / FastAPI / static build chain.
2. **Remove deck search**: only `deck-search.html` + `deck-search.js` are exclusive.
   `complete.js` and `decklist.js` are shared with card-search and archetype pages —
   they stay. Also remove the Nav entry, nav header link, and FR translations.
3. **Agents/skills for slow-moving content**: TWDA-based top-tier + best-cards stats,
   "What Should I Buy" product list. (See P2 for the current staleness baseline.)
4. **ES / PT translations**: git tag `i18n-es` (2020) holds a full 9,719-line ES base
   catalog to seed from; `display.js` already has an `es` branch; FR is at 96%
   (86/2149 untranslated, 0 fuzzy). Land the P0 trans-lint test first.
5. **Navigation / page-tree rework** for discoverability.

## Verified fine — no action

- Rules accuracy spot-checks all passed (political-action stealth/undirected,
  referendum term timing, "limited" bleed-modifier exceptions, Archon Investigation
  at 4+, bounce timing).
- Banned/errata'd cards are properly contextualized (erratum macros, Pentex 2020
  errata note).
- Every archetype page (including all 67 archive pages) has a matching decklist
  `.json` with date/event/player metadata.
- All 7 JS files and the single CSS file are referenced — no orphaned assets.
- i18n wrapping of article/strategy/best-cards/archetype prose is consistently good.
