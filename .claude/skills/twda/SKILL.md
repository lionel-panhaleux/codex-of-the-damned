---
name: twda
description: >-
  Refresh the Codex of the Damned's TWDA-backed sections — Archetypes (18-month /
  20+ player tiering against Primogen's archetype labels) and Best Cards
  (5-year and all-time play statistics). Use when recomputing archetype tiers,
  updating best-cards counts/rankings, drafting or reviewing archetype pages,
  or checking what moved in the tournament meta.
---

# TWDA refresh workflows

Combines the **Primogen MCP** (`https://mcp.krcg.org/mcp`) for VTES knowledge,
deck analysis, card stats, and meta reading with lean local bulk-aggregation
scripts under `scripts/` (PEP 723, `uv run` — no dependency added to the site).

## Division of responsibilities

- **Primogen MCP** owns all VTES facts and archetype labels:
  - `vtes_meta`: live player-weighted TWDA win share, Archon full-field play
    share/conversion, rising/falling archetypes, archetype cores, and
    representative/newest decks.
  - `vtes_deck`: full deck dossier (crypt, requirements, modules, combat
    posture, economy, track record, nearest archetypes/decks).
  - `vtes_cards` & `vtes_card_stats`: exact card text, requirements, rulings,
    errata history, and single-card play rates/competitors.
  - `vtes_rules_case` / `vtes_rulings_archive`: rules verification.
  - Upstream `classification.json` lives in `lionel-panhaleux/primogen`
    (`knowledge/classification.json`). Codex never forks or edits it locally.
- **Local `scripts/`** handle only bulk TWDA aggregation that MCP does not
  return in one shot:
  - `archetype_tiers.py`: Codex's 18-month / 20+ players halving-ladder tier
    table, reading Primogen's `classification.json` + live TWDA similarity
    placement, diffed against `navigation.py`.
  - `best_cards_report.py`, `best_cards_pages.py`, `best_cards_update.py`,
    `assemble_best_cards.py`, `disambiguate_crypt.py`: bulk 5-year and
    all-time rankings across all ~60 Best Cards pages.
  - `page_json.py <twda_id>`: emit a co-located archetype decklist `.json`.
  - `twda.py`: shared daily-cached KRCG v5 TWDA loader + site anchor map.

## Workflow 1: Archetypes refresh

1. **Read the live meta with Primogen MCP**: call `vtes_meta(detail=True)` to
   see rising/falling archetypes, full-field Archon context, and the share in
   no archetype.
2. **Compute the Codex tier table**:
   ```bash
   uv run .claude/skills/twda/scripts/archetype_tiers.py --refresh
   ```
   This applies Codex's tier rule (rolling **18 months**, events with **20+ players**):
   - **Anomaly (`💀`)**: leader > `2 × L` (where `L` is the runner-up leader).
   - **Top Tier**: `⌈L/2⌉ .. L` qualifying wins.
   - **Runner-ups**: next halving (`⌈top_floor/2⌉ .. top_floor - 1`).
   - **New Kids**: genuinely new archetype with `2+` tournament wins (any event size) in the window.
   - **Old Guard**: `2` qualifying wins (or `runner_floor - 1`) AND established archetype.
   - **Out → Archive**: everything else.
3. **Check unassigned qualifying decks**: if a cluster of unassigned 20+ player
   winners represents a real emerging archetype, update `classification.json`
   upstream in `primogen` first (and re-run step 2) rather than inventing
   local labels here.
4. **Confirm moves, new pages, and representatives with the owner**: call
   `vtes_meta(archetype="<name>", detail=True)` to inspect recent qualifying
   wins (prefer NC/CC wins when available) and confirm tier moves / new pages.
5. **Write or refresh archetype pages**:
   - Read [references/archetype-page-style.md](references/archetype-page-style.md)
     before writing or editing any archetype page.
   - Generate co-located decklists with
     `uv run .claude/skills/twda/scripts/page_json.py <twda_id> -o <path>.json`.
   - Call `vtes_deck` on the example deck and any linked variant decks; call
     `vtes_cards` on any other card mentioned.
   - Update `codex_of_the_damned/navigation.py` and
     `codex_of_the_damned/templates/archetypes/index.html` (remember: always
     link archetypes via root path `/archetypes/<slug>`).
6. **Review & translate**:
   - Have the `strategist` subagent review every new/edited archetype page.
   - Have the `translator` subagent update `fr`, `es`, `pt` catalogs and run
     `mise run po`.
   - Validate with `uv run --extra dev pytest tests/test_navigation.py tests/test_templates.py`
     and targeted `tests/test_pages.py` (or full `mise run test`).

## Workflow 2: Best Cards refresh

1. **Generate 5-year and all-time reports** (rolling 5-year window and 2-year
   `NEW` cutoff by default; override with `--since` / `--recent-since`):
   ```bash
   uv run .claude/skills/twda/scripts/best_cards_report.py --refresh -o /tmp/best-5y.json
   uv run .claude/skills/twda/scripts/best_cards_report.py --since 1994-01-01 -o /tmp/best-all.json
   ```
2. **Inspect proposed page lists and stat diffs**:
   ```bash
   uv run .claude/skills/twda/scripts/best_cards_pages.py --report /tmp/best-5y.json --alltime /tmp/best-all.json -o /tmp/best-proposed.md
   uv run .claude/skills/twda/scripts/best_cards_update.py /tmp/best-5y.json --alltime /tmp/best-all.json
   ```
   - For a **numbers-only refresh** (keeping current cards, updating `decks=`
     and `copies=`): run `best_cards_update.py ... --apply` followed by
     `uv run .claude/skills/twda/scripts/disambiguate_crypt.py --apply`.
   - For a **full curation refresh** (adding/dropping/reordering cards): get
     owner sign-off on `/tmp/best-proposed.md`, run
     `uv run .claude/skills/twda/scripts/assemble_best_cards.py /tmp/best-proposed.md /tmp/best-5y.json /tmp/best-all.json /tmp/best-todo.json`,
     then `disambiguate_crypt.py --apply`.
3. **Write prose for newly added cards**:
   - For every card in `todo.json`, call `vtes_cards` and `vtes_card_stats` via
     Primogen MCP so descriptions are grounded in exact card text, current
     archetypes, and competitors — following Codex voice (impersonal, no
     "you"/"your", concise strategic role rather than card-text recital,
     discipline/clan icons on every mention).
   - Check `codex_of_the_damned/templates/best-cards/index.html` for the deck
     count mention (e.g. `1,300+ decks from the last five years`) and any clan
     red-flag (`warn` class) transitions.
4. **Review, translate, and validate**:
   - Have `strategist` review new prose, `translator` update `fr`/`es`/`pt`
     (mirroring any EN edits to existing msgids before `mise run po`), and run
     `mise run test`.
