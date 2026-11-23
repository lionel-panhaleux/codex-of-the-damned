# /// script
# requires-python = ">=3.11"
# dependencies = ["krcg", "numpy>=1.26", "scipy>=1.11"]
# ///
"""Compute Codex of the Damned archetype tiers from Primogen's classification + live TWDA.

Reads Primogen's upstream `knowledge/classification.json` (sibling `../primogen`
checkout when present, else GitHub raw URL daily-cached), places post-pass TWDA
decks using Primogen's exact cosine TF-IDF similarity (crypt/library weighted
0.5 each, vampire groups merged, no SVD, calibrated LOO 5th-percentile threshold),
and computes Codex's rolling 3-year / 20+ players halving-ladder tier table
diffed against `codex_of_the_damned/navigation.py`.

    uv run archetype_tiers.py --refresh
    uv run archetype_tiers.py --as-of 2026-11-23 --json /tmp/tiers.json
"""

from __future__ import annotations

import argparse
import collections
import datetime
import json
import math
import pathlib
import re
import time
import urllib.request

import numpy as np
import scipy.sparse as sp

import twda

PRIMOGEN_LOCAL = twda.REPO.parent / "primogen" / "knowledge" / "classification.json"
PRIMOGEN_URL = (
    "https://raw.githubusercontent.com/lionel-panhaleux/primogen/"
    "main/knowledge/classification.json"
)
PRIMOGEN_CACHE = twda.CACHE / "primogen-classification.json"

CRITERIA_PLAYERS = 20
CRITERIA_YEARS = 3
LIVE_SECTIONS = ("top-tier", "runner-ups", "new-kids", "old-guard")


def subtract_years(iso_date: str, years: int) -> str:
    d = datetime.date.fromisoformat(iso_date)
    try:
        return d.replace(year=d.year - years).isoformat()
    except ValueError:
        # Feb 29 -> Feb 28
        return d.replace(year=d.year - years, day=28).isoformat()


def load_classification(
    path: pathlib.Path | None = None, refresh: bool = False
) -> tuple[dict, str]:
    """Load Primogen's classification.json and return (data, source_description)."""
    if path:
        return json.loads(path.read_text()), str(path)
    if PRIMOGEN_LOCAL.exists():
        return json.loads(PRIMOGEN_LOCAL.read_text()), str(PRIMOGEN_LOCAL)
    twda.CACHE.mkdir(parents=True, exist_ok=True)
    stale = (
        not PRIMOGEN_CACHE.exists()
        or time.time() - PRIMOGEN_CACHE.stat().st_mtime > twda.CACHE_TTL
    )
    if refresh or stale:
        urllib.request.urlretrieve(PRIMOGEN_URL, PRIMOGEN_CACHE)
    return json.loads(PRIMOGEN_CACHE.read_text()), PRIMOGEN_URL


def l2_normalize_csr(mat: sp.csr_matrix) -> sp.csr_matrix:
    norms = np.sqrt(np.asarray(mat.multiply(mat).sum(axis=1)).ravel())
    inv = np.divide(1.0, norms, out=np.zeros_like(norms), where=norms > 0)
    return sp.diags(inv) @ mat


def build_tfidf(
    decks: list, crypt_weight: float, min_df: int
) -> sp.csr_matrix:
    """Primogen/Codex TF-IDF vectors (no SVD, L2-normalized rows)."""
    features = []
    for deck in decks:
        feats = {
            "c:" + k: v for k, v in twda.crypt_features(deck, merge_groups=True).items()
        }
        feats.update(("l:" + k, v) for k, v in twda.library_features(deck).items())
        features.append(feats)

    df = collections.Counter(key for feats in features for key in feats)
    vocab = sorted(key for key, count in df.items() if count >= min_df)
    index = {key: i for i, key in enumerate(vocab)}

    rows, cols, vals = [], [], []
    for row, feats in enumerate(features):
        for key, count in feats.items():
            col = index.get(key)
            if col is not None:
                rows.append(row)
                cols.append(col)
                vals.append(1.0 + math.log(count))
    mat = sp.csr_matrix((vals, (rows, cols)), shape=(len(decks), len(vocab)))

    n = len(decks)
    idf = np.array([math.log((1.0 + n) / (1.0 + df[key])) + 1.0 for key in vocab])
    mat = mat.multiply(idf).tocsr()

    crypt_cols = np.array([key.startswith("c:") for key in vocab])
    crypt = l2_normalize_csr(mat[:, crypt_cols]) * crypt_weight
    library = l2_normalize_csr(mat[:, ~crypt_cols]) * (1.0 - crypt_weight)
    return l2_normalize_csr(sp.hstack([crypt, library]).tocsr())


def load_site_archetypes() -> dict[str, str]:
    """Return {slug: section} for all archetype pages currently on disk."""
    out: dict[str, str] = {}
    for path in sorted(twda.ARCHETYPES.glob("*/*.html")):
        if path.name.startswith("_") or path.name == "index.html":
            continue
        out[path.stem] = path.parent.name
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--classification", type=pathlib.Path, default=None)
    parser.add_argument(
        "--as-of",
        default="",
        help="Reference ISO date for the 3-year cutoff (default: newest TWDA deck)",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Override similarity bar for placing unlabeled decks (default: calibrated LOO p5)",
    )
    parser.add_argument("--refresh", action="store_true", help="Refresh cached TWDA")
    parser.add_argument("--json", type=pathlib.Path, default=None, help="Write JSON output")
    args = parser.parse_args()

    truth, source = load_classification(args.classification, args.refresh)
    params = truth["params"]
    since = params["since"]
    crypt_weight = float(params.get("crypt_weight", 0.5))
    min_df = int(params.get("min_df", 2))

    group_of = {d["id"]: g["ref"] for g in truth["groups"] for d in g["decks"]}
    names = {g["ref"]: g["name"] for g in truth["groups"]}
    parents = {g["ref"]: g["variant_of"] for g in truth["groups"]}
    reps_of = {
        g["ref"]: [d["id"] for d in g["decks"] if d.get("representative")]
        for g in truth["groups"]
    }
    noise_ids = {d["id"] for d in truth["noise"]}

    def root_of(ref: str) -> str:
        seen = set()
        while parents.get(ref) and ref not in seen:
            seen.add(ref)
            ref = parents[ref]
        return ref

    archive = twda.load_archive(args.refresh)
    all_dates = [twda.deck_date(d) for d in archive.values() if twda.deck_date(d)]
    as_of = args.as_of or max(all_dates)
    cutoff = subtract_years(as_of, CRITERIA_YEARS)

    window_decks = [
        d for d in archive.values() if since <= twda.deck_date(d) <= as_of
    ]
    row_of = {d.id: i for i, d in enumerate(window_decks)}
    mat = build_tfidf(window_decks, crypt_weight, min_df)

    # Group centroids over labeled decks present in window
    rows_by_ref: dict[str, list[int]] = collections.defaultdict(list)
    for deck_id, ref in group_of.items():
        if deck_id in row_of:
            rows_by_ref[ref].append(row_of[deck_id])
    refs = sorted(rows_by_ref)
    ref_idx = {r: i for i, r in enumerate(refs)}

    sums = np.vstack(
        [np.asarray(mat[rows_by_ref[r]].sum(axis=0)).ravel() for r in refs]
    )
    counts = np.array([len(rows_by_ref[r]) for r in refs])
    centroid_norms = np.linalg.norm(sums, axis=1, keepdims=True)
    centroids = np.where(centroid_norms > 0, sums / np.maximum(centroid_norms, 1e-12), 0.0)

    # LOO self-validation + calibrated 5th-percentile threshold (Primogen's bar)
    own_sims, ok_group, ok_root, loo_total = [], 0, 0, 0
    for ref in refs:
        idx = ref_idx[ref]
        if counts[idx] < 2:
            continue
        for r in rows_by_ref[ref]:
            vec = np.asarray(mat[r].toarray()).ravel()
            loo_sum = sums[idx] - vec
            loo_norm = np.linalg.norm(loo_sum)
            own = float(vec @ (loo_sum / loo_norm)) if loo_norm > 0 else 0.0
            sims = centroids @ vec
            sims[idx] = own
            best = refs[int(np.argmax(sims))]
            loo_total += 1
            own_sims.append(own)
            if best == ref:
                ok_group += 1
            if root_of(best) == root_of(ref):
                ok_root += 1

    calibrated = float(np.percentile(own_sims, 5)) if own_sims else 0.49
    threshold = args.threshold if args.threshold is not None else calibrated

    # Place unlabeled decks in the window
    placed_group: dict[str, tuple[str, float]] = {}
    unassigned_qualifying = []
    for i, deck in enumerate(window_decks):
        if deck.id in group_of or deck.id in noise_ids:
            continue
        vec = np.asarray(mat[i].toarray()).ravel()
        sims = centroids @ vec
        best_i = int(np.argmax(sims))
        best_sim = float(sims[best_i])
        best_ref = refs[best_i]
        if best_sim >= threshold:
            placed_group[deck.id] = (best_ref, best_sim)
        else:
            players = deck.event.players_count if deck.event else 0
            date = twda.deck_date(deck)
            if date >= cutoff and players >= CRITERIA_PLAYERS:
                unassigned_qualifying.append(
                    {
                        "id": deck.id,
                        "date": date,
                        "players": players,
                        "name": deck.name or "(unnamed)",
                        "event": deck.event.name if deck.event else "",
                        "nearest": names[root_of(best_ref)],
                        "nearest_ref": root_of(best_ref),
                        "similarity": round(best_sim, 3),
                        "kind": "unlabeled",
                    }
                )

    # Also track noise decks that qualified in the 3-year window
    for deck_id in noise_ids:
        deck = archive.get(deck_id)
        if not deck:
            continue
        date = twda.deck_date(deck)
        players = deck.event.players_count if deck.event else 0
        if cutoff <= date <= as_of and players >= CRITERIA_PLAYERS:
            unassigned_qualifying.append(
                {
                    "id": deck.id,
                    "date": date,
                    "players": players,
                    "name": deck.name or "(unnamed)",
                    "event": deck.event.name if deck.event else "",
                    "nearest": "",
                    "nearest_ref": "",
                    "similarity": None,
                    "kind": "noise",
                }
            )
    unassigned_qualifying.sort(key=lambda x: (-x["players"], x["date"]), reverse=False)
    unassigned_qualifying.sort(key=lambda x: x["date"], reverse=True)

    # Aggregate stats per root archetype
    anchors = twda.load_anchors()
    site_pages = load_site_archetypes()
    root_stats: dict[str, dict] = {}
    for g in truth["groups"]:
        r = root_of(g["ref"])
        entry = root_stats.setdefault(
            r,
            {
                "ref": r,
                "name": names[r],
                "variants": [],
                "q": 0,
                "q_placed": 0,
                "total_3y": 0,
                "total_5y": 0,
                "first_date": "9999-99-99",
                "newest_date": "",
                "pages": set(),
                "reps": [],
                "q_decks": [],
            },
        )
        if g["ref"] != r:
            entry["variants"].append(g["name"])
        entry["reps"].extend(reps_of.get(g["ref"], []))

    def record_deck(deck, ref: str, placed: bool) -> None:
        r = root_of(ref)
        entry = root_stats[r]
        date = twda.deck_date(deck)
        players = deck.event.players_count if deck.event else 0
        entry["total_5y"] += 1
        if date and date < entry["first_date"]:
            entry["first_date"] = date
        if date and date > entry["newest_date"]:
            entry["newest_date"] = date
        if deck.id in anchors:
            slug = anchors[deck.id]["archetype"]
            if slug in site_pages:
                entry["pages"].add((slug, site_pages[slug]))
        if cutoff <= date <= as_of:
            entry["total_3y"] += 1
            if players >= CRITERIA_PLAYERS:
                entry["q"] += 1
                if placed:
                    entry["q_placed"] += 1
                entry["q_decks"].append(
                    {
                        "id": deck.id,
                        "date": date,
                        "players": players,
                        "name": deck.name or "(unnamed)",
                        "event": deck.event.name if deck.event else "",
                        "placed": placed,
                    }
                )

    for deck in window_decks:
        if deck.id in group_of:
            record_deck(deck, group_of[deck.id], placed=False)
        elif deck.id in placed_group:
            record_deck(deck, placed_group[deck.id][0], placed=True)

    # Also attach site pages whose anchor deck predates the 5y window (e.g. old-guard/archive),
    # or whose slug matches the root archetype's slugified name
    for deck_id, info in anchors.items():
        if deck_id in group_of:
            r = root_of(group_of[deck_id])
            slug = info["archetype"]
            if slug in site_pages:
                root_stats[r]["pages"].add((slug, site_pages[slug]))
    for entry in root_stats.values():
        if not entry["pages"]:
            slug = re.sub(r"[^\sa-zA-Z0-9]", "", entry["name"]).lower().strip()
            slug = re.sub(r"\s+", "-", slug)
            if slug in site_pages:
                entry["pages"].add((slug, site_pages[slug]))

    # Halving ladder
    ranked = sorted(
        (e for e in root_stats.values() if e["q"] >= 2),
        key=lambda e: (-e["q"], -e["total_3y"], e["name"]),
    )
    anomaly = None
    if len(ranked) >= 2 and ranked[0]["q"] > 2 * ranked[1]["q"]:
        anomaly = ranked[0]
        leader_q = ranked[1]["q"]
    elif ranked:
        leader_q = ranked[0]["q"]
    else:
        leader_q = 0

    top_floor = math.ceil(leader_q / 2) if leader_q else 0
    runner_floor = max(4, top_floor // 2) if top_floor else 4

    tiers: dict[str, list[dict]] = {
        "anomaly": [],
        "top-tier": [],
        "runner-ups": [],
        "new-kids-or-old-guard": [],
    }
    for e in ranked:
        e["q_decks"].sort(key=lambda d: (d["date"], d["players"]), reverse=True)
        e["pages_sorted"] = sorted(e["pages"])
        if anomaly is e:
            e["computed_tier"] = "top-tier"
            e["anomaly"] = True
            tiers["anomaly"].append(e)
        elif e["q"] >= top_floor:
            e["computed_tier"] = "top-tier"
            e["anomaly"] = False
            tiers["top-tier"].append(e)
        elif e["q"] >= runner_floor:
            e["computed_tier"] = "runner-ups"
            e["anomaly"] = False
            tiers["runner-ups"].append(e)
        else:
            # 2..3q (or up to runner_floor-1): distinguish new vs established
            sections = {sec for _, sec in e["pages_sorted"]}
            is_old = (
                e["first_date"] < cutoff
                or "old-guard" in sections
                or "archive" in sections
                or "top-tier" in sections
                or "runner-ups" in sections
            )
            if is_old and e["q"] >= 3:
                e["computed_tier"] = "old-guard"
            elif not is_old and e["q"] >= 2:
                e["computed_tier"] = "new-kids"
            else:
                e["computed_tier"] = "out"
            e["anomaly"] = False
            tiers["new-kids-or-old-guard"].append(e)

    # Report
    revised = truth.get("revised") or truth.get("generated")
    print(f"Classification: {source} (generated {truth.get('generated')}, revised {revised})")
    print(
        f"TWDA window: {since} .. {as_of} ({len(window_decks)} decks; "
        f"{len(group_of)} labeled, {len(placed_group)} placed by similarity >= {threshold:.3f})"
    )
    print(
        f"LOO self-validation ({loo_total} decks): "
        f"{ok_group / loo_total:.1%} group, {ok_root / loo_total:.1%} root archetype"
    )
    print(
        f"Qualifying criteria: {CRITERIA_PLAYERS}+ players since {cutoff} "
        f"(rolling {CRITERIA_YEARS} years to {as_of})"
    )
    print(
        f"Halving ladder: L={leader_q}"
        + (f" (anomaly {anomaly['name']} at {anomaly['q']}q)" if anomaly else "")
        + f" -> top-tier >= {top_floor}q, runner-ups {runner_floor}..{top_floor - 1}q, "
        f"old-guard 3q (old), new-kids 2..{runner_floor - 1}q (new)\n"
    )

    seen_live_slugs: set[str] = set()

    def fmt_site_action(entry: dict) -> str:
        target = entry["computed_tier"]
        pages = entry["pages_sorted"]
        for slug, sec in pages:
            if sec in LIVE_SECTIONS:
                seen_live_slugs.add(slug)
        if not pages:
            return "NEW PAGE" if target != "out" else "no page"
        live = [(s, sec) for s, sec in pages if sec in LIVE_SECTIONS]
        if live:
            slug, sec = live[0]
            if target == "out":
                return f"ARCHIVE ({slug}: {sec} -> archive)"
            if sec == target:
                return f"stays ({slug})"
            return f"MOVE {slug}: {sec} -> {target}"
        slug, sec = pages[0]
        if target == "out":
            return f"stays archive ({slug})"
        return f"REVIVE {slug}: archive -> {target}"

    def print_section(title: str, entries: list[dict]) -> None:
        print(f"=== {title} ({len(entries)}) ===")
        for e in entries:
            placed_note = f"+{e['q_placed']}sim" if e["q_placed"] else "0sim"
            flag = " [ANOMALY]" if e.get("anomaly") else ""
            action = fmt_site_action(e)
            print(
                f"  {e['q']:2d}q ({placed_note:>5})  {e['total_3y']:3d}d/3y  "
                f"first:{e['first_date']}  {e['ref']:<4} {e['name']:<26}  "
                f"[{e['computed_tier']}]  {action}{flag}"
            )
        print()

    if tiers["anomaly"]:
        print_section("Anomaly", tiers["anomaly"])
    print_section("Top Tier", tiers["top-tier"])
    print_section("Runner-ups", tiers["runner-ups"])
    new_kids = [e for e in tiers["new-kids-or-old-guard"] if e["computed_tier"] == "new-kids"]
    old_guard = [e for e in tiers["new-kids-or-old-guard"] if e["computed_tier"] == "old-guard"]
    falling_2q = [e for e in tiers["new-kids-or-old-guard"] if e["computed_tier"] == "out"]
    print_section("New Kids", new_kids)
    print_section("Old Guard", old_guard)
    if falling_2q:
        print_section("2q Established (Out)", falling_2q)

    # Check live site pages that dropped below 2q (or have no anchor in any qualifying group)
    dropped_live = []
    for slug, sec in sorted(site_pages.items()):
        if sec in LIVE_SECTIONS and slug not in seen_live_slugs:
            # Find if any root archetype holds this slug
            matched = [
                (e["ref"], e["name"], e["q"], e["total_3y"])
                for e in root_stats.values()
                if any(s == slug for s, _ in e["pages"])
            ]
            dropped_live.append((slug, sec, matched))
    if dropped_live:
        print(f"=== Live pages below 2q -> ARCHIVE ({len(dropped_live)}) ===")
        for slug, sec, matched in dropped_live:
            if matched:
                ref, name, q, t3 = matched[0]
                print(f"  {slug} ({sec}) -> {q}q, {t3}d/3y ({ref} {name})")
            else:
                print(f"  {slug} ({sec}) -> 0q / no anchor in classification")
        print()

    unlabeled_q = [u for u in unassigned_qualifying if u["kind"] == "unlabeled"]
    noise_q = [u for u in unassigned_qualifying if u["kind"] == "noise"]
    print(
        f"=== Unassigned qualifying decks ({len(unlabeled_q)} unlabeled below "
        f"{threshold:.3f}, {len(noise_q)} noise) ==="
    )
    for u in unlabeled_q[:25]:
        print(
            f"  {u['date']}  {u['players']:3d}p  {u['id']:<8}  "
            f"{u['name'][:34]:<34}  nearest: {u['nearest']} ({u['similarity']:.3f})"
        )
    if len(unlabeled_q) > 25:
        print(f"  ... and {len(unlabeled_q) - 25} more unlabeled qualifying decks")

    if args.json:
        payload = {
            "source": source,
            "generated": truth.get("generated"),
            "revised": revised,
            "as_of": as_of,
            "cutoff": cutoff,
            "threshold": round(threshold, 4),
            "ladder": {
                "leader_q": leader_q,
                "anomaly": anomaly["ref"] if anomaly else None,
                "top_floor": top_floor,
                "runner_floor": runner_floor,
            },
            "archetypes": [
                {
                    k: (list(v) if isinstance(v, set) else v)
                    for k, v in e.items()
                    if k != "pages"
                }
                for e in ranked
            ],
            "dropped_live": [
                {"slug": s, "section": sec, "matched": m}
                for s, sec, m in dropped_live
            ],
            "unassigned_qualifying": unassigned_qualifying,
        }
        args.json.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
        print(f"\nWrote {args.json}")


if __name__ == "__main__":
    main()
