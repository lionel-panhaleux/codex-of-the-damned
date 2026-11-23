# AGENTS.md

This file provides guidance to coding agents (Antigravity and Claude Code) working in this repository. `CLAUDE.md` is a symlink to this file.

## Project

Flask website compiling Vampire: The Eternal Struggle (VTES) strategy resources, served at codex-of-the-damned.org. Content lives in Jinja templates — there is no database or backend logic beyond routing and i18n.

## Principles

- **Keep it KISS**: vanilla JS, handcrafted CSS, Jinja-templated HTML. A single framework, and as dead-simple a build as possible. Do not introduce build tooling, JS frameworks, CSS preprocessors, or new dependencies without an explicit request.
- **This is a static website**: no dynamic features — no comments, no stars/ratings, no online editing, no user accounts. Interactivity is limited to client-side JS consuming the external KRCG API.
- **Fix every failure, not just yours**: when lint or tests fail, fix them even if the failure predates the current change — proving it isn't yours is not a stopping point. A dead external link gets a working URL (and any stale text around it fixed, catalogs included); a site that blocks bots on every user agent goes in the `tests/test_pages.py` skip list.

## VTES Grounding — Primogen MCP

All VTES game knowledge comes from the **Primogen MCP** (`https://mcp.krcg.org/mcp`), never from memory and never by ad-hoc `curl` calls to `api.krcg.org` or static local rules copies:

- **Cards, errata & rulings**: `vtes_cards` (official text, requirements, legality, rulings, card-changes history).
- **Rules & rulings archive**: `vtes_rules_case`, `vtes_rules_search`, `vtes_rules_read`, `vtes_rulings_archive`.
- **Decks & strategy**: `vtes_deck` (full dossier: crypt, requirements, modules, combat posture, economy, track record, nearest archetypes/decks).
- **Card play rates & competitors**: `vtes_card_stats` (single-card TWDA frequency, archetypes, co-played cards, slot competitors).
- **Meta & events**: `vtes_meta` (player-weighted TWDA win share + Archon full-field play share/conversion, archetype cores, representative/newest decks) and `vtes_events`.

Archetype labels (`classification.json`) are owned upstream in `lionel-panhaleux/primogen` (`knowledge/classification.json`). Codex consumes them read-only rather than maintaining a local fork; if new archetypes need naming or grouping, update them in `primogen` first.

## Commands

`mise tasks` lists every task (`mise.toml` pins Python and `uv`):

```bash
mise run update             # sync/upgrade dev dependencies (uv)
mise run test               # full check: black --check, ruff check, pytest (matches CI)
mise run lint               # black --check + ruff check
mise run fmt                # black + ruff check --fix
mise run serve              # run dev server (DEBUG=1 mise run serve for debug mode)
mise run po                 # extract + update fr/es/pt + compile translations
mise run po-compile         # compile .po -> .mo only
mise run release            # tag + PyPI upload (clean tree required)
uv run --extra dev pytest "tests/test_pages.py::test[/strategy/combat.html]"  # single page test
```

**Releasing and deploying**: `mise run release` (tag + PyPI upload), then run the `Deploy` GitHub workflow (`gh workflow run deploy.yml -f environment=...`) — **always `beta` first, then `prod`**, every time, so beta stays aligned with prod.

Tests require an internet connection and `api.krcg.org` to be up: they crawl every page in the navigation tree and issue real HTTP requests to validate every external link. Code style is `black`; versioning is `setuptools-scm` from git tags.

## Agents & Skills

- **`strategist`** (`.claude/agents/strategist.md` / `.agents/agents/strategist.md`): read-only VTES strategist and Codex content reviewer, grounded in Primogen MCP and `.claude/skills/twda/references/archetype-page-style.md`.
- **`translator`** (`.claude/agents/translator.md` / `.agents/agents/translator.md`): EN/FR/ES/PT-BR gettext translation specialist with official BCP vocabulary and settled community jargon tables.
- **`twda` skill** (`.claude/skills/twda/SKILL.md`, symlinked at `.agents/skills`): bulk TWDA aggregation workflows (Archetype 18-month / 20+ players tiering and Best Cards 5-year / all-time stats) paired with Primogen MCP for prose and review.

## Architecture

The whole site hangs off two files:

- `codex_of_the_damned/__init__.py` — the Flask app. A single catch-all route (`/<lang_code>/<path:page>`) renders the Jinja template whose path matches the URL, redirecting to add a language prefix (`/en/`, `/fr/`) when missing. It also defines `BASE_CONTEXT`, which injects VTES discipline/clan icon markup into every template (e.g. `{{ cel }}`/`{{ CEL }}` for inferior/superior Celerity, `{{ brujah }}` for the clan icon), and context processors providing `link()`, `i18n_url()`, `translation()`, `top()`/`prev()`/`next()`, `external()`, `card()` and `card_image()`.

- `codex_of_the_damned/navigation.py` — the source of truth for site structure. `STRUCTURE` is a tree of `Nav` nodes; walking it builds `HELPER`, a dict mapping URL paths to pages with their top/prev/next links. The sitemap, the nav menus, and the test parametrization are all derived from `HELPER`.

**Adding a page requires both**: a `Nav` entry in `navigation.py` and a template at the matching path under `templates/`. The template path is the slugified Nav name (unidecode, strip punctuation, lowercase, spaces → hyphens): `Nav("Malk' 22")` under Archetypes/Top Tier → `templates/archetypes/top-tier/malk-22.html`. Tests will fail if either side is missing.

**Linking to archetype pages**: always link the root path — `link("/archetypes/malk-22")`, never the subsection path (`/archetypes/top-tier/malk-22`). Archetypes move between subsections over time (Top Tier ↔ Runner Ups ↔ New Kids ↔ Old Guard ↔ Archive), and `HELPER` registers a subsection-less shortcut for every deep leaf, so root-path links survive those moves. Corollary (deliberate): no two archetypes may share a name, whatever their subsections — `tests/test_navigation.py` enforces this uniqueness.

### Templates

- All pages extend `templates/layout.html`. Archetype pages extend `templates/archetypes/_layout.html` and import a co-located `.json` decklist file.
- Card names are rendered with `card("Card Name")`, which emits a `krcg-card` span; hover previews and card data come from the external KRCG services (`static.krcg.org` for images/CSS/JS, `api.krcg.org` for the card/deck search pages, which are pure JS frontends in `static/js/`).
- **Voice — never address the reader.** Body prose stays generic and impersonal: no "you"/"your". Use "one" ("one can", "one's prey"), the impersonal deck/player ("the deck", "the player"), the passive, or a bare imperative instead. This is a firm, site-wide rule for all user-facing content.

### i18n

Flask-Babel with URL-prefixed locales (`en`, `fr`, `es`, `pt` — declared in `config.py` `SUPPORTED_LANGUAGES`). All user-facing template text must be wrapped in `{% trans trimmed %}` blocks (or `_()`), with anything dynamic — card names, discipline icons, links — passed as parameters (e.g. `{% trans trimmed govern=card("Govern the Unaligned") %}`). Translators must keep HTML tags and `%(param)s` placeholders intact. Catalogs live in `codex_of_the_damned/translations/<lang>/LC_MESSAGES/`; a new language also needs a `translation()` line in the `nav[aria-label="Language"]` block of `layout.html`.

**Proper nouns that read identically in every language are not wrapped for translation at all** — card names (rendered via `card()`), proper-noun clans (`Nav("Tzimisce")`, not `lazy_gettext`), player/product names, and English jargon are left as plain text so they never enter the catalog. Only terms with a genuine local form (disciplines like Célérité, translatable clans like Sacerdoce/Malkavien, sects, section labels) stay wrapped and get every `msgstr` filled. A blank `msgstr` therefore means genuinely-untranslated, not deliberate. See `.claude/agents/translator.md` for the full policy.
