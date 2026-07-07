# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Flask website compiling Vampire: The Eternal Struggle (VTES) strategy resources, served at codex-of-the-damned.org. Content lives in Jinja templates — there is no database or backend logic beyond routing and i18n.

## Principles

- **Keep it KISS**: vanilla JS, handcrafted CSS, Jinja-templated HTML. A single framework, and as dead-simple a build as possible. Do not introduce build tooling, JS frameworks, CSS preprocessors, or new dependencies without an explicit request.
- **This is a static website**: no dynamic features — no comments, no stars/ratings, no online editing, no user accounts. Interactivity is limited to client-side JS consuming the external KRCG API.

## Commands

```bash
pip install -e ".[dev]"     # setup (Python >= 3.11)
make test                   # full check: black --check, ruff check, pytest (this is what CI runs)
pytest                      # tests only
pytest "tests/test_pages.py::test[/strategy/combat.html]"   # single page test (parametrized by URL)
codex                       # run dev server (DEBUG=1 codex for debug mode)
make po                     # extract + compile translations (BABEL_LANG=es make po-update for a new language)
```

Tests require an internet connection and api.krcg.org to be up: they crawl every page in the navigation tree and issue real HTTP requests to validate every external link. Code style is black; versioning is setuptools-scm from git tags (`make release`).

## Architecture

The whole site hangs off two files:

- `codex_of_the_damned/__init__.py` — the Flask app. A single catch-all route (`/<lang_code>/<path:page>`) renders the Jinja template whose path matches the URL, redirecting to add a language prefix (`/en/`, `/fr/`) when missing. It also defines `BASE_CONTEXT`, which injects VTES discipline/clan icon markup into every template (e.g. `{{ cel }}`/`{{ CEL }}` for inferior/superior Celerity, `{{ brujah }}` for the clan icon), and context processors providing `link()`, `i18n_url()`, `translation()`, `top()`/`prev()`/`next()`, `external()`, `card()` and `card_image()`.

- `codex_of_the_damned/navigation.py` — the source of truth for site structure. `STRUCTURE` is a tree of `Nav` nodes; walking it builds `HELPER`, a dict mapping URL paths to pages with their top/prev/next links. The sitemap, the nav menus, and the test parametrization are all derived from `HELPER`.

**Adding a page requires both**: a `Nav` entry in `navigation.py` and a template at the matching path under `templates/`. The template path is the slugified Nav name (unidecode, strip punctuation, lowercase, spaces → hyphens): `Nav("Malk' 22")` under Archetypes/Top Tier → `templates/archetypes/top-tier/malk-22.html`. Tests will fail if either side is missing.

**Linking to archetype pages**: always link the root path — `link("/archetypes/malk-22")`, never the subsection path (`/archetypes/top-tier/malk-22`). Archetypes move between subsections over time (Top Tier ↔ Runner Ups ↔ New Kids ↔ Archive), and `HELPER` registers a subsection-less shortcut for every deep leaf, so root-path links survive those moves. Corollary (deliberate): no two archetypes may share a name, whatever their subsections — `tests/test_navigation.py` enforces this uniqueness.

### Templates

- All pages extend `templates/layout.html`. Archetype pages extend `templates/archetypes/_layout.html` and import a co-located `.json` decklist file.
- Card names are rendered with `card("Card Name")`, which emits a `krcg-card` span; hover previews and card data come from the external KRCG services (static.krcg.org for images/CSS/JS, api.krcg.org for the card/deck search pages, which are pure JS frontends in `static/js/`).
- **Voice — never address the reader.** Body prose stays generic and impersonal: no "you"/"your". Use "one" ("one can", "one's prey"), the impersonal deck/player ("the deck", "the player"), the passive, or a bare imperative instead. This is a firm, site-wide rule for all user-facing content.

### i18n

Flask-Babel with URL-prefixed locales (`en`, `fr` — declared in `config.py` `SUPPORTED_LANGUAGES`). All user-facing template text must be wrapped in `{% trans trimmed %}` blocks (or `_()`), with anything dynamic — card names, discipline icons, links — passed as parameters (e.g. `{% trans trimmed govern=card("Govern the Unaligned") %}`). Translators must keep HTML tags and `%(param)s` placeholders intact. Catalogs live in `codex_of_the_damned/translations/<lang>/LC_MESSAGES/`; a new language also needs a `translation()` line in the `nav[aria-label="Language"]` block of `layout.html`.
