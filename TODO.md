# TODO

Findings from the 2026-07-04 full-site review, ordered by priority.
Every P0 item was verified by actually rendering the pages / reading the code.

## P0 — Broken for readers right now

*All P0 items done (2026-07-04). The new lint (`tests/test_templates.py`) found ~100
undeclared-variable sites across 38 templates — the list below plus extras (khazars-diary,
dementation-bleed, lasombra-nocturn, tremere.html:50/:69, …). All fixed via trans-header
declarations so existing FR msgids/translations are preserved; the four in-body typo fixes
(`revolutionnary_council`, `ventre_antitribu`, `aud`→`aus`, `chimerstry`→`chi`) were
mirrored into the FR catalog. `link()` now raises under TESTING, which surfaced 8 more
broken links (ravnos-break→ravnos-bonds, gangrel-barons→gangrel-thing, palla-grande
missing slash, assamite-legacy.html suffix, the_unnamed underscore, archetypes- typo,
runner-ups/shambling-hordes, dead aaa declaration) — all fixed. Also fixed in passing:
`card("rolling_with_the_punches")` rendering its variable name (emerald-legion) and
`card("Maris streck")` casing (war-ghouls, piper-war-ghoul-24).*

- [x] **Fix ~45 `{% trans %}` blocks referencing undeclared variables** — Jinja renders
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
- [x] **Add a lint test that catches the above class of bug forever**: extract
  `{% trans %}` block bodies, diff the `{{ var }}` names against declared kwargs +
  `BASE_CONTEXT` keys. Pure-offline, fast, belongs in the regular pytest run.
  Consider also making `link()` raise (or warn under TESTING) on unknown paths
  instead of returning `""`.
- [x] **Best Cards index: two clan pages unreachable** — `best-cards/index.html:76,84`
  have `" warn"` inside the link *path* instead of `_class`
  (`link("/best-cards/clans/daughters-of-cacophony warn", ...)`), and `link()`
  silently returns `""`. Daughters of Cacophony and Ishtarri are orphaned.
- [x] **Reflected XSS in both search pages** — raw `?card=` / `?id=` URL params flow
  into `Error(...)` messages rendered via `innerHTML`:
  `static/js/card-search.js:76` + `:264`, `static/js/deck-search.js:162` + `:203`.
  Fix: use `textContent` for these two message assignments.
- [x] **Make `make test` green again**:
  - [x] `black` fails on `codex_of_the_damned/navigation.py` — run `black` on it.
  - [x] 3 tests fail on DriveThruRPG/DriveThruCards links (their anti-bot layer 403s
    any non-browser client, even with a browser User-Agent). Add both domains to the
    skip-list in `tests/test_pages.py:32-38` next to eBay/Reddit/Kickstarter; verify
    the links once manually in a real browser. *(Both verified live in Chrome 2026-07-04:
    the Player's Guide product page and the 1060-title Legacy Card Singles category.
    shop.cardgamegeek.com turned out to be the same anti-bot class — 500 to any
    non-browser client, loads fine in Chrome — so it is skipped too.)*

## P1 — Cheap, high-value fixes

*All P1 items done (2026-07-05). Notes: no raw `target="_blank"` anchor sits inside a
`{% trans %}` body, so the whole sweep was msgid-safe — verified by diffing `pybabel
extract` before/after (only the 2 msgids of the deleted `_layout_promo.html` dropped).
ghost.mnsi.net (deck-building.html) serves no HTTPS — left http. The lackeyccg/table-talk
"missing alt" line refs were stale (alts already present); an exhaustive img sweep found
the real list instead: Discord widget + dark-pack.png (index), VDB favicons and
JS-populated card images (`alt=""`, decorative/redundant), 20 pool.svg icons in the
Montano article (`alt="pool"`). The deck-guides `example.com` placeholder was a hidden
JS-populated decklist stub — dropped the href to match `archetypes/_layout.html`,
`decklist.js` sets it. Logo h1 is now a `.site-title` span except on the homepage (which
has no content h1). canonical/hreflang loop over `config['SUPPORTED_LANGUAGES']` and
build from `request.host_url` like the sitemap does.*

### SEO / metadata
- [x] `<title>` is hardcoded to "Codex of the Damned" on all pages
  (`templates/layout.html:39`) while the per-page `title()` helper already exists and
  feeds `og:title`. Change to `<title>{{ title() }}</title>`. Biggest SEO win available.
- [x] Remove (or migrate to GA4) the dead Universal Analytics tag `UA-157267369-1`
  (`layout.html:28-35`) — collecting nothing since mid-2023, still loaded on every page.
  KISS-est option: delete it. *(Deleted.)*
- [x] Add `<link rel="alternate" hreflang="en|fr|x-default">` + `rel="canonical"` for
  the parallel `/en/`–`/fr/` URL scheme. Currently absent site-wide.
  *(New `canonical_url()` context processor.)*
- [x] Same hardcoded `<meta name="description">` on every page (`layout.html:21`) —
  allow per-page override. *(Wrapped in a `{% block description %}`; no page overrides
  it yet.)*

### Markup bugs
- [x] 8× `target=" _blank"` (leading space) in `templates/index.html`.
- [x] 12 anchors with a stray comma between attributes (`<a href="…" , target="_blank">`)
  in `strategy/articles/basic/what-should-i-buy.html` *(13 with the multi-line
  Australia one, plus a stray `</a>` and a doubled `</li>` in the same section)*.
- [x] Add `rel="noopener"` centrally: in the `external()` helper + the 89 raw
  `target="_blank"` anchors in templates (the two `rel="external"` VDB buttons became
  `rel="external noopener"`).
- [x] Invalid ARIA role `role="translation"` (`layout.html:81`) — now
  `<nav aria-label="Language">`; CLAUDE.md reference updated.
- [x] Double `<h1>` on every page: logo heading demoted to `.site-title` span,
  h1 kept on the homepage only.
- [x] Missing `alt` attributes (see sweep notes above).
- [x] `fundamentals.html:295` has invalid `</ li>`.

### Dead code / stale scaffolding
- [x] ~~Delete~~ `templates/_layout_promo.html`: kept on request (used sparingly for
  event promos) — now a commented `{% include %}` banner slot in `layout.html` instead
  of the old always-on import; its anchor got the noopener fix too.
- [x] Delete `strategy/articles/advanced/guide-for-competitive-play.html` (0-byte orphan).
- [x] Deduplicate the card-image slug logic: og_image block now uses `file_name()`,
  https-only (dropped `og_image_secure` from the route and layout).
- [x] Upgrade plain `http://` hrefs where HTTPS exists — all done except
  `ghost.mnsi.net` (no HTTPS); every target curl-verified 200 over https first.
- [x] `strategy/deck-guides/_layout.html:21` `href="http://example.com"` placeholder
  removed (JS-populated stub, see notes).

## P2 — Content refresh (feeds the planned TWDA-agent work)

### The TWDA-analysis skill (in progress 2026-07-05)

A project skill (`.claude/skills/twda/`) that turns the TWDA into the numbers the
content items below need. Source: `static.krcg.org/data/twda.json` (rebuilt daily,
~4,540 decks, 4-digit years back to 1994) + `vtes.json` for card metadata. Scripts are
self-contained `uv run` scripts (PEP 723 inline deps) — the site itself gains no
dependency.

- [x] **Best cards** (easy): per-card play counts / deck shares over a date window,
  by card type — direct refresh input for `best-cards/`. *(Script landed 2026-07-05:
  `uv run scripts/best_cards.py --since 2020-01-01`. The window is now 1,430 decks —
  the index's "900+" has drifted. By-clan breakdowns still TODO.)*
- [ ] **Top archetypes** (hard): cluster TWD decklists to find what the meta actually
  plays. The journey:
  1. Vectorize decklists (card-count vectors; crypt weighted — it defines archetypes),
     IDF-weight to mute staples, reduce dimensions (SVD or similar) so clustering has
     a chance.
  2. Auto-clusterization first (HDBSCAN / agglomerative / kNN-graph community
     detection — compare). Evaluate against a free ground truth: the 90 archetype-page
     decklist JSONs carry TWDA ids — anchors should land in coherent, distinct
     clusters that pull in their known kin.
  3. If auto-clustering doesn't converge, fall back to a human-in-the-middle loop:
     the model proposes a classification for each new TWD deck (nearest anchors +
     top characteristic cards), Lionel confirms/corrects. Time-consuming — last resort.

  *First results (2026-07-05) — auto-clustering looks viable.* `scripts/cluster.py`:
  sublinear TF + IDF, crypt/library blocks L2-normalized then weighted 50/50, SVD-128,
  HDBSCAN(min_cluster_size=5, min_samples=2) over 1,430 decks (2020+) → **107
  clusters, 17% noise, 41/44 anchors clustered, zero clusters merging distinct live
  anchors** (the parameter sweep is in the script's defaults; agglomerative assigns
  everything but merges close archetypes — dementation-bleed+thucimia,
  haqim-royalty+kalinda). Even size-5 clusters are coherent named archetypes (Anson
  Guns, Montano Baltimore, Legacy of Pander…). The 3 noise anchors (malk-94,
  shadow-court-satyrs, thucimia) are genuinely sparse post-2020 — correct behavior.
  Notable: several 15+ deck clusters have no site page (Lasombra Progeny ~22 decks
  2024-12+, Hecata Swarm ~18 decks 2025+, Gangrel Renegade-Garou wall ~18) — New
  Kids candidates. Next: name clusters (top cards + common deck names), recompute
  tier criteria from cluster sizes/dates, decide noise handling (nearest-cluster
  attachment vs leave out).
- [ ] Once stable, wire the outputs into the refresh items below (tier assignments,
  "proven twice in 3 years" / ⭐ recomputation, best-cards deck counts).

  *Update 2026-07-05, owner review in progress.* The review/editor page
  (`scripts/review_page.py`, published as an artifact) is the working tool: vdb
  links, decklist hover with rare-card/odd-count/missing-staple signals, criteria
  greying + NC/CC championship flags, group editing (names, moves, splits,
  variant-of with TOC regrouping), Export. The exported JSON gets committed as
  `.claude/skills/twda/data/classification.json` — the owner's labels. Next steps:
  *Labels landed 2026-07-05*: the owner completed the full review pass —
  `data/classification.json` (rebuilt deterministically from the editor state by
  `scripts/apply_review.py`): 89 archetypes + 30 variants, 1,083 decks classified,
  242 noise, 51 proven archetypes. Baseline (`scripts/benchmark.py`): raw
  clustering scores ARI 0.861 vs groups, 0.687 vs variant-merged archetypes
  (lower by design — HDBSCAN over-segments, the owner merges via variant-of).
  Tier data is live: `uv run scripts/benchmark.py … --tiers` (Gangrel Renegades
  44 qualifying — ⭐ by the 50% rule; next Illegal Brawl 18).
  - [x] `classify.py`: refresh loop without re-clustering — nearest-centroid
    assignment of new TWD decks to labeled archetypes (calibrated threshold →
    else "novel" pile clustered by HDBSCAN). Leave-one-out self-validation:
    94.3% exact group, 98.6% archetype-level on the 1,082 validatable labeled
    decks. Still open: pre-seeded delta review page once a refresh actually
    brings new decks.
  - [x] Benchmark mode: `scripts/benchmark.py` scores any clustering run against
    the curated labels (ARI at both granularities + noise agreement) and prints
    the archetype tier table. Use before adopting any pipeline change.
  - [ ] Per-archetype discriminative cards (supervised scores, e.g. one-vs-rest
    chi²) — for page prose and assignment explanations, not for training (yet).

### Staleness found in the 2026-07-04 review

*Content-refresh pass done 2026-07-13. The archetype tier pages, Best Cards deck counts,
and the What Should I Buy V5 coverage were refreshed in the earlier "Cover the V5
releases" work; the remaining items below were closed in this pass. The automated tier
recompute (⭐/"proven twice") still feeds from the TWDA-analysis clustering item above.
All body-text edits were mirrored into the fr/es/pt catalogs (0 fuzzy after
reconciliation).*

- [x] Archetypes: tier pages refreshed for the 2026 meta (New Kids etc.). Ongoing
  ⭐/"proven twice" automation is tracked under the TWDA-analysis item above.
- [x] Best Cards: `best-cards/index.html:12` now reads "1,300+ decks from the last five
  years" (was "900+").
- [x] What Should I Buy: V5 releases covered; the stale "announced, no precise list yet"
  insert is gone and the product list runs through the 2025-26 releases.
- [x] Online Play: Discord invites `discord.gg/fJjac75` and `discord.gg/QJtDzp5`
  re-verified live (2026-07-13, both return valid invites). The "foremost platform"
  LackeyCCG claim is left as an editorial call for the owner (Succubus Club now exists
  as a modern alternative).
- [x] Anthelios ban year standardized to **2016** (KRCG/VEKN B&R list, 2016-02-16):
  fixed the outlier "2017" in `what-should-i-buy.html`. Also corrected Lilith's Blessing
  to **2013** in the erratum macro (it wrongly said 2016; the year was already right in
  what-should-i-buy).
- [x] Typo sweep: residual EN typos fixed (recommanded, plateform, unneccessary,
  independantly, 2× loosing, "provided"→"provide"); the Methusalah/particularily/etc.
  set was already cleared in the "Fix more English source typos" commit. Fixes mirrored
  into all three catalogs.
- [x] Garbled prose: `fundamentals.html` non-limited-modifier sentence fixed in the V5
  pass; `piper-war-ghoul-24.html` mid-thought sentence completed ("…no need to fret over
  converting them first, so Piper is online from the opening turn") + "arguable"→"arguably".
- [x] Copy-pasted captions: already resolved in the Best Cards refresh —
  `harbingers-of-skulls.html` "Acheron Vortex" & "Vengeful Spirit" now have distinct
  captions, and `salubri-antitribu.html` was reworked (no shared-caption pair remains).
- [x] i18n chrome gaps: wrapped "Deck builder", "Cards finder", "Telegram Bot"
  (`index.html`) and the search `Card Name` placeholder + `Clear` button value
  (`card-search.html`, `deck-search.html`), all translated in fr/es/pt. ("Forum VEKN
  France" is inside a `{% if lang == "fr" %}` block, so correctly not translated.)
- [ ] **Untranslated backlog from the V5/Best-Cards content refresh** (found 2026-07-13):
  the big "Cover the V5 releases" content pass added many strings that ship untranslated
  (empty `msgstr`, so they fall back to English) — ~76 in fr, ~75 in es, ~110 in pt.
  Mostly clan names, "V5: …" set names, card names, and new archetype names. Not a
  regression (tests pass; English fallback renders), but a translation debt to clear.

## P3 — Performance (KISS-compatible)

*All P3 items done 2026-07-13.*

- [x] Font `src` ordering: `woff2` now first, then `woff`/`truetype`; dropped the dead
  `.eot`/`.svg` entries (`base.css`).
- [x] Compress the big PNG/JPG screenshots to WebP: converted 18 images (all LackeyCCG /
  TTS / JOL screenshots, the 5 player portraits, and `background.jpg`), downscaled to
  max 1600px wide where larger. **15.9 MB → 2.66 MB (−13.2 MB).** Originals removed.
- [x] Added `width`/`height` to every converted screenshot/portrait `<img>` to avoid
  layout shift.
- [x] `base.css` `.autocomplete-items { overflow: scroll }` → `auto`.

## P4 — Small JS bugs

*All P4 items done 2026-07-13.*

- [x] `static/js/complete.js` — catch block now uses `this.message_output` (was
  `this.message`); autocomplete fetch failures surface again.
- [x] `static/js/statistics.js` — `howManyNeeded` now returns the stack size as a floor
  instead of `undefined` when no copy count reaches the target probability.
- [x] `static/js/card-search.js` — removed leftover `console.log(ruling_text)`.
- [x] `static/js/complete.js` — deleted the dead `Completion.reset()` (would have thrown).
- [x] `static/js/complete.js` — `encodeUrlParam` now uses global regexes, replacing all
  `/` and `\` (was only the first occurrence).
- [x] `display.js` `es` branch: resolved by the ES/PT landing — `getLangText()` now has
  `fr`/`es`/`pt` branches and all three are live in `config.py`.

## Backlog — to discuss before acting

1. **Framework**: entire backend is ~750 lines of Python; Babel i18n and the
   `navigation.py` tree are the only real coupling. A pure jinja-to-static build
   looks very tractable. Decide: Flask stays / FastAPI / static build chain.
2. **Remove deck search**: only `deck-search.html` + `deck-search.js` are exclusive.
   `complete.js` and `decklist.js` are shared with card-search and archetype pages —
   they stay. Also remove the Nav entry, nav header link, and FR translations.
3. **Agents/skills for slow-moving content**: promoted to P2 — see "The TWDA-analysis
   skill" above. Remaining discussion: "What Should I Buy" product list automation.
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
