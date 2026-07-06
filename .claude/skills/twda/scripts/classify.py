# /// script
# requires-python = ">=3.11"
# dependencies = ["krcg", "numpy>=1.26", "scipy>=1.11", "scikit-learn>=1.4"]
# ///
"""Classify new TWD decks against the owner's labeled archetypes.

The refresh loop: instead of re-clustering, embed labeled + new decks in the
shared vector space (same pipeline and params as the labels' clustering run),
compute a centroid per labeled group, and assign each new deck to its nearest
centroid when the similarity clears the threshold; the rest go to a novel
pile clustered by HDBSCAN. Leave-one-out self-validation on the labeled decks
measures accuracy and calibrates the default threshold.

    uv run classify.py                          # validate + classify new decks
    uv run classify.py --refresh --out new.json # pull latest TWDA first
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib

import numpy as np
from sklearn.cluster import HDBSCAN
from sklearn.preprocessing import normalize

import cluster as clu
import twda

DATA = pathlib.Path(__file__).resolve().parent.parent / "data"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--classification", type=pathlib.Path,
                        default=DATA / "classification.json")
    parser.add_argument("--threshold", type=float, default=None,
                        help="min similarity to assign (default: calibrated "
                             "5th percentile of own-group similarity)")
    parser.add_argument("--top", type=int, default=3,
                        help="candidate archetypes to report per deck")
    parser.add_argument("--out", type=pathlib.Path, default=None)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    truth = json.loads(args.classification.read_text())
    params = truth["params"]
    group_of = {d["id"]: g["ref"] for g in truth["groups"] for d in g["decks"]}
    names = {g["ref"]: g["name"] for g in truth["groups"]}
    parents = {g["ref"]: g["variant_of"] for g in truth["groups"]}
    noise_ids = {d["id"] for d in truth["noise"]}

    def root_of(ref: str) -> str:
        seen = set()
        while parents.get(ref) and ref not in seen:
            seen.add(ref)
            ref = parents[ref]
        return ref

    archive = twda.load_archive(args.refresh)
    labeled = [archive[i] for i in group_of if i in archive]
    candidates = [
        deck for deck in archive.values()
        if twda.deck_date(deck) >= params["since"]
        and deck.id not in group_of and deck.id not in noise_ids
    ]
    print(f"{len(labeled)} labeled decks, {len(candidates)} new candidates "
          f"(window {params['since']}+, labels {truth['generated']})")

    decks = labeled + candidates
    matrix, vocab = clu.build_matrix(
        decks, params["crypt_weight"], params["min_df"], True)
    reduced = clu.reduce(matrix, params["components"])

    # centroids per group; per-group sums enable leave-one-out validation
    rows_of = collections.defaultdict(list)
    for row, deck in enumerate(labeled):
        rows_of[group_of[deck.id]].append(row)
    refs = sorted(rows_of)
    sums = np.stack([reduced[rows_of[r]].sum(axis=0) for r in refs])
    counts = np.array([len(rows_of[r]) for r in refs])
    centroids = normalize(sums / counts[:, None])
    index = {r: i for i, r in enumerate(refs)}

    # leave-one-out self-validation on groups with 2+ decks
    own_sims, correct_group, correct_root, total = [], 0, 0, 0
    for ref in refs:
        if counts[index[ref]] < 2:
            continue
        for row in rows_of[ref]:
            loo = normalize(
                (sums[index[ref]] - reduced[row])[None, :])[0]
            own = float(reduced[row] @ loo)
            sims = centroids @ reduced[row]
            sims[index[ref]] = own
            best = refs[int(np.argmax(sims))]
            total += 1
            own_sims.append(own)
            if best == ref:
                correct_group += 1
            if root_of(best) == root_of(ref):
                correct_root += 1
    suggested = float(np.percentile(own_sims, 5))
    print(f"self-validation (leave-one-out, {total} decks): "
          f"{correct_group / total:.1%} exact group, "
          f"{correct_root / total:.1%} archetype (variants merged)")
    threshold = args.threshold if args.threshold is not None else suggested
    print(f"threshold: {threshold:.3f} "
          f"({'given' if args.threshold is not None else 'calibrated'})\n")

    assigned, novel = [], []
    for offset, deck in enumerate(candidates):
        row = reduced[len(labeled) + offset]
        sims = centroids @ row
        order = np.argsort(sims)[::-1][: args.top]
        best = [
            {"group": refs[i], "root": root_of(refs[i]),
             "name": names[refs[i]], "similarity": round(float(sims[i]), 3)}
            for i in order
        ]
        entry = {
            "id": deck.id, "date": twda.deck_date(deck), "name": deck.name,
            "player": deck.player,
            "players": deck.event.players_count if deck.event else 0,
            "candidates": best,
        }
        if best[0]["similarity"] >= threshold:
            assigned.append(entry)
        else:
            novel.append(entry)

    for entry in sorted(assigned, key=lambda e: -e["candidates"][0]["similarity"]):
        top = entry["candidates"][0]
        print(f"  {top['similarity']:.3f} -> {top['group']} {top['name']:<24}"
              f" {entry['date']} {entry['name'] or '(unnamed)'}")
    print(f"\n{len(assigned)} assigned, {len(novel)} below threshold")

    novel_clusters = []
    if len(novel) >= 5:
        rows = [len(labeled) + candidates.index(
            next(d for d in candidates if d.id == e["id"])) for e in novel]
        labels = HDBSCAN(min_cluster_size=3, min_samples=2).fit_predict(
            reduced[rows])
        by_label = collections.defaultdict(list)
        for entry, label in zip(novel, labels):
            by_label[int(label)].append(entry)
        for label, entries in sorted(by_label.items()):
            if label == -1:
                continue
            ids = [e["id"] for e in entries]
            member_rows = [rows[novel.index(e)] for e in entries]
            cards = clu.top_cards(matrix, vocab, member_rows, 8)
            novel_clusters.append({"decks": ids, "cards": cards})
            print(f"novel cluster: {len(entries)} decks — {', '.join(cards)}")
            for e in entries:
                print(f"    {e['date']} {e['name'] or '(unnamed)'}")
    elif novel:
        print("novel pile too small to cluster:")
        for e in novel:
            top = e["candidates"][0]
            print(f"    {e['date']} {e['name'] or '(unnamed)'} "
                  f"(closest: {top['name']} {top['similarity']:.3f})")

    if args.out:
        args.out.write_text(json.dumps({
            "generated_against": truth["generated"],
            "threshold": threshold,
            "validation": {
                "decks": total,
                "group_accuracy": round(correct_group / total, 4),
                "root_accuracy": round(correct_root / total, 4),
            },
            "assigned": assigned,
            "novel": novel,
            "novel_clusters": novel_clusters,
        }, indent=1))
        print(f"\nwritten to {args.out}")


if __name__ == "__main__":
    main()
