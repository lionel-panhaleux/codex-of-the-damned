---
name: twda
description: Analyze the TWDA (Tournament Winning Deck Archive) to refresh the site's slow-moving content — best-cards stats and top-archetype identification via deck clustering. Use when recomputing best cards, tier assignments, meta statistics, or classifying TWD decks into archetypes.
---

# TWDA analysis

Turns the TWDA into the numbers the site's content needs (see TODO.md P2).

## Data

- The TWDA (~4,500 decks since 1994), via the **krcg library** models:
  `https://static.krcg.org/data/v5/twda.json` decoded into `krcg.models.Deck`
  (daily-cached in `~/.cache/codex-twda/`, krcg's bundled snapshot as offline
  fallback). Deck entries (`CardInDeck`) carry kind, types and disambiguated
  names — `unique_name` keeps group variants distinct, `twda.merge_key()`
  collapses them (re-grouped star vampires define the same archetype).
- **Anchors**: `templates/archetypes/*/*.json` each carry the TWDA `id` of the
  page's example deck — free ground-truth labels (~90, of which ~27 live, i.e.
  non-archive). `twda.load_anchors()` maps TWDA id → archetype slug + section.

`scripts/twda.py` is the shared data layer. The krcg library (same author as
this site) is the intended toolkit for TWDA work — prefer extending on top of
it; `krcg.analyzer` also offers set-overlap primitives (played/affinity/
build_deck) useful for deck-building suggestions.

## Scripts

All in `scripts/`, self-contained (PEP 723, `uv run`) — the site gains no
dependency.

```bash
uv run scripts/best_cards.py --since 2020-01-01 --top 20   # play stats by card type
uv run scripts/cluster.py --since 2021-07-01 --out c.json  # archetype clustering
uv run scripts/cluster.py --anchors-nn                     # vector-space sanity check
uv run scripts/review_page.py c.json -o review.html        # owner review/editor page
```

`review_page.py` renders the owner's review & classification editor (publish as
an artifact): group naming, bulk deck moves, group create/delete, variant-of
links (a variant group nests under its main, TOC reordered, qualifying counts
combined on the main), representative stars, criteria greying (archetypes index
rule: 20+ players twice in the last 3 years — proven groups show their count in
the TOC), NC/CC badges on qualifying national/continental championship wins
(regex on event names; qualifiers/side events excluded), proposed variant
splits, and an Export button whose JSON is the input for archetype-page
generation. Edits persist in localStorage — regenerating the page with
identical clustering (same data + params ⇒ identical C-refs; verify when in
doubt) keeps them valid.

## TWDA refresh workflow (the working tool)

1. `uv run scripts/cluster.py --since <5 years back> --out data/clusters.json`
2. `uv run scripts/review_page.py data/clusters.json -o review.html`, publish
   as an artifact (keep the same file path to keep the URL). The page embeds
   all decklists (hover) with live rare-card / odd-count / missing-staple
   signals against the deck's current group.
3. The owner reviews and refines in the page (names, moves, splits, variants,
   representatives), then **Export**. Save the export's `editor_state` as
   `data/review-<date>.editor-state.json` and rebuild the canonical file:
   `uv run scripts/apply_review.py data/clusters.json <state> --generated
   <date> -o data/classification.json`. Commit both. classification.json is
   the ground truth: the owner's labels are the most valuable asset this
   skill produces (first pass 2026-07-05: 89 archetypes + 30 variants, 1,083
   decks, 51 proven). The `editor_state` can also be re-imported into a page
   generated from the SAME clustering run (refs must match).
   `scripts/benchmark.py` scores any run against the labels (baseline: ARI
   0.861 groups / 0.687 variant-merged) and prints the tier table (--tiers).
4. Next refresh (planned `classify.py`): don't re-cluster from scratch —
   nearest-centroid–assign new TWD decks to the labeled archetypes, run
   HDBSCAN only on unassigned decks to propose novel archetypes, and generate
   a review page of deltas (auto-assignments + novelties) pre-seeded with the
   stored names/variants. Each confirmed export grows the labels.
5. Any pipeline tuning must be scored against `data/classification.json`
   (ARI / anchor checks) before being adopted — the labels are the benchmark,
   never a thing to silently overwrite.

## Clustering pipeline (the hard part — still experimental)

Card-count vectors → sublinear TF + IDF (mutes staples like Villein/Deflection) →
crypt and library blocks L2-normalized separately then weighted (`--crypt-weight`,
default 0.5 — crypt defines archetypes, don't let the 80-card library drown it) →
TruncatedSVD (`--components`) → HDBSCAN (default) or agglomerative/cosine
(`--method agglo --threshold`). Vampire group variants are merged by default
(`--keep-groups` to disable).

Evaluation, printed by every run: cluster count and noise share, anchors landing
in noise, and — the key failure signal — clusters merging several *live* anchors
(distinct archetypes should not share a cluster). `--out file.json` dumps
assignments for downstream use.

If auto-clustering stalls, fall back to human-in-the-middle: propose nearest
anchors + characteristic cards per new deck, let the owner confirm (see TODO.md).

**Status 2026-07-05**: the defaults are the winning config of the first sweep —
HDBSCAN(min_cluster_size=5, min_samples=2) on 2020+ (1,430 decks) gives 107
clusters, 17% noise, 41/44 anchors clustered, zero live-anchor merges, and
coherent archetypes down to size-5 clusters. Agglomerative assigns everything
but merges close archetypes — candidate for attaching noise decks later, not
the primary method. Owner review of the 5-year run confirmed quality overall.

Within-cluster variants (e.g. an ally-rush module inside the Lasombra Oblivion
bleed cluster) are NOT separable by global re-weighting — a card-type-totals
block (`--type-features`) changed nothing at 0.1 and only added noise at 0.15.
What works is local sub-clustering (`--subcluster`, default 0.8): rebuild the
matrix over one cluster's decks so the IDF is local, staples flatten, and the
variant modules emerge — it reproduced the owner's manual split of C5 exactly
and correctly left cohesive clusters alone. Details and next steps in TODO.md P2.
