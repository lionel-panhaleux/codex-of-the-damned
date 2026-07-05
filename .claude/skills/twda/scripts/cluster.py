# /// script
# requires-python = ">=3.11"
# dependencies = ["krcg", "numpy>=1.26", "scipy>=1.11", "scikit-learn>=1.4"]
# ///
"""Cluster TWD decklists into archetypes.

Pipeline: card-count vectors (sublinear TF, IDF to mute staples), crypt and
library L2-normalized separately then weighted (crypt defines archetypes),
TruncatedSVD, then a clustering algorithm. Evaluated against the repo's
archetype-page decklists ("anchors" — known TWDA ids with archetype labels).

    uv run cluster.py --since 2020-01-01                  # HDBSCAN (default)
    uv run cluster.py --method agglo --threshold 0.7      # agglomerative/cosine
    uv run cluster.py --anchors-nn                        # vector-space sanity check
"""

from __future__ import annotations

import argparse
import collections
import json
import pathlib

import numpy as np
import scipy.sparse as sp
from sklearn.cluster import HDBSCAN, AgglomerativeClustering
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

import twda


def build_matrix(decks, crypt_weight, min_df, merge_groups, type_weight=0.0):
    """TF-IDF matrix with separately normalized crypt/library blocks.

    Returns (X, vocab) — vocab entries are "c:Name" / "l:Name". With
    type_weight > 0, a third block of library card-type totals ("t:Ally", …)
    is appended, and the two card blocks shrink to (1 - type_weight).
    """
    features = []
    for deck in decks:
        feats = {
            "c:" + k: v
            for k, v in twda.crypt_features(deck, merge_groups).items()
        }
        feats.update(
            ("l:" + k, v) for k, v in twda.library_features(deck).items()
        )
        features.append(feats)

    df = collections.Counter(key for feats in features for key in feats)
    vocab = sorted(key for key, count in df.items() if count >= min_df)
    index = {key: i for i, key in enumerate(vocab)}

    matrix = sp.lil_matrix((len(decks), len(vocab)))
    for row, feats in enumerate(features):
        for key, count in feats.items():
            if key in index:
                matrix[row, index[key]] = 1 + np.log(count)
    matrix = matrix.tocsr()

    n = len(decks)
    idf = np.array([np.log((1 + n) / (1 + df[key])) + 1 for key in vocab])
    matrix = matrix.multiply(idf).tocsr()

    # normalize each block to a fixed share of the row norm, so the ~80-card
    # library does not drown the 12-card crypt
    crypt_cols = np.array([key.startswith("c:") for key in vocab])
    crypt = normalize(matrix[:, crypt_cols]) * crypt_weight
    library = normalize(matrix[:, ~crypt_cols]) * (1 - crypt_weight)
    blocks = [crypt * (1 - type_weight), library * (1 - type_weight)]
    vocab = [k for k, c in zip(vocab, crypt_cols) if c] + [
        k for k, c in zip(vocab, crypt_cols) if not c
    ]
    if type_weight:
        type_feats = [twda.type_features(deck) for deck in decks]
        type_names = sorted({t for feats in type_feats for t in feats})
        totals = np.zeros((len(decks), len(type_names)))
        for row, feats in enumerate(type_feats):
            for name, count in feats.items():
                totals[row, type_names.index(name)] = 1 + np.log(count)
        blocks.append(normalize(totals) * type_weight)
        vocab += ["t:" + name for name in type_names]
    return sp.hstack(blocks).tocsr(), vocab


def subclusters(decks, rows, crypt_weight, threshold):
    """Variant split within one cluster, or None if it is cohesive.

    The matrix is rebuilt over the cluster's decks only, so the IDF is local:
    cluster-wide staples flatten out and variant modules (e.g. an ally-rush
    package inside a bleed archetype) become the signal."""
    subset = [decks[r] for r in rows]
    matrix, vocab = build_matrix(subset, crypt_weight, 2, True)
    labels = AgglomerativeClustering(
        n_clusters=None,
        metric="cosine",
        linkage="average",
        distance_threshold=threshold,
    ).fit_predict(normalize(matrix.toarray()))
    groups = collections.defaultdict(list)
    for i, label in enumerate(labels):
        groups[label].append(i)
    if sum(1 for g in groups.values() if len(g) >= 2) < 2:
        return None
    return [
        {
            "ids": [subset[i].id for i in idx],
            "cards": top_cards(matrix, vocab, idx, 6) if len(idx) > 1 else [],
        }
        for _, idx in sorted(groups.items(), key=lambda kv: -len(kv[1]))
    ]


def reduce(matrix, components):
    """LSA: TruncatedSVD then re-normalize rows so euclidean ~ cosine."""
    components = min(components, min(matrix.shape) - 1)
    reduced = TruncatedSVD(components, random_state=42).fit_transform(matrix)
    return normalize(reduced)


def top_cards(matrix, vocab, rows, count=8):
    """Most characteristic cards of a cluster: mean weight above corpus mean."""
    cluster_mean = np.asarray(matrix[rows].mean(axis=0)).ravel()
    corpus_mean = np.asarray(matrix.mean(axis=0)).ravel()
    order = np.argsort(cluster_mean - corpus_mean)[::-1]
    tags = {"c": " [crypt]", "l": "", "t": " [type total]"}
    return [vocab[i][2:] + tags[vocab[i][0]] for i in order[:count]]


def report(decks, labels, matrix, vocab, anchors, show_max):
    clusters = collections.defaultdict(list)
    for row, label in enumerate(labels):
        clusters[label].append(row)
    noise = clusters.pop(-1, [])

    anchor_rows = {}  # row -> anchor info
    for row, deck in enumerate(decks):
        if deck.id in anchors:
            anchor_rows[row] = anchors[deck.id]

    print(f"{len(clusters)} clusters, {len(noise)} noise decks "
          f"({len(noise) / len(decks):.0%}) out of {len(decks)}")
    in_noise = [a["archetype"] for r, a in anchor_rows.items() if labels[r] == -1]
    clustered = len(anchor_rows) - len(in_noise)
    print(f"anchors in window: {len(anchor_rows)}, clustered: {clustered}, "
          f"in noise: {sorted(in_noise)}")

    merged = []
    for label, rows in clusters.items():
        live = {anchor_rows[r]["archetype"] for r in rows
                if r in anchor_rows and anchor_rows[r]["section"] != "archive"}
        if len(live) > 1:
            merged.append(sorted(live))
    print(f"clusters merging several live anchors: {merged or 'none'}\n")

    by_size = sorted(clusters.items(), key=lambda kv: -len(kv[1]))
    for label, rows in by_size[:show_max]:
        tags = sorted(
            f"{anchor_rows[r]['archetype']} ({anchor_rows[r]['section']})"
            for r in rows if r in anchor_rows
        )
        dates = sorted(twda.deck_date(decks[r]) for r in rows)
        print(f"-- cluster {label}: {len(rows)} decks "
              f"({dates[0]} .. {dates[-1]})"
              + (f"  ANCHORS: {', '.join(tags)}" if tags else ""))
        print("   cards: " + ", ".join(top_cards(matrix, vocab, rows)))
        names = collections.Counter(
            decks[r].name for r in rows if decks[r].name)
        if names:
            print("   names: " + ", ".join(
                f"{name} x{c}" if c > 1 else name
                for name, c in names.most_common(4)))
    if len(by_size) > show_max:
        print(f"... and {len(by_size) - show_max} more clusters")
    return clusters, noise, anchor_rows


def anchors_nn(decks, reduced, anchors, neighbors=6):
    """Vector-space sanity check: nearest decks to each live anchor."""
    for row, deck in enumerate(decks):
        info = anchors.get(deck.id)
        if not info or info["section"] == "archive":
            continue
        sims = reduced @ reduced[row]
        order = np.argsort(sims)[::-1][1 : neighbors + 1]
        print(f"{info['archetype']} ({info['section']}, {twda.deck_date(deck)})")
        for i in order:
            print(f"   {sims[i]:.3f}  {twda.deck_date(decks[i])}  "
                  f"{decks[i].name or '(unnamed)'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", default="2020-01-01")
    parser.add_argument("--until", default="")
    parser.add_argument("--method", choices=["hdbscan", "agglo"],
                        default="hdbscan")
    parser.add_argument("--components", type=int, default=128)
    parser.add_argument("--crypt-weight", type=float, default=0.5)
    parser.add_argument("--type-features", type=float, default=0.0,
                        help="experimental: weight of a card-type totals "
                             "block (try 0.1)")
    parser.add_argument("--min-df", type=int, default=2)
    parser.add_argument("--min-cluster-size", type=int, default=5)
    # 2 won the 2026-07 sweep: 41/44 anchors clustered, no live-anchor merges
    parser.add_argument("--min-samples", type=int, default=2)
    parser.add_argument("--threshold", type=float, default=0.7,
                        help="agglo: cosine distance threshold")
    parser.add_argument("--subcluster", type=float, default=0.8,
                        help="local variant-split threshold for --out "
                             "(0 disables)")
    parser.add_argument("--keep-groups", action="store_true",
                        help="do NOT merge vampire group variants")
    parser.add_argument("--anchors-nn", action="store_true",
                        help="print nearest neighbors of live anchors and exit")
    parser.add_argument("--show-max", type=int, default=40)
    parser.add_argument("--out", type=pathlib.Path, default=None,
                        help="write cluster assignments to this JSON file")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    decks = twda.load_decks(args.since, args.until, args.refresh)
    anchors = twda.load_anchors()
    matrix, vocab = build_matrix(
        decks, args.crypt_weight, args.min_df, not args.keep_groups,
        args.type_features)
    print(f"{len(decks)} decks, {len(vocab)} card features "
          f"(min_df={args.min_df}, crypt_weight={args.crypt_weight})")
    reduced = reduce(matrix, args.components)

    if args.anchors_nn:
        anchors_nn(decks, reduced, anchors)
        return

    if args.method == "hdbscan":
        labels = HDBSCAN(
            min_cluster_size=args.min_cluster_size,
            min_samples=args.min_samples,
        ).fit_predict(reduced)
    else:
        labels = AgglomerativeClustering(
            n_clusters=None,
            metric="cosine",
            linkage="average",
            distance_threshold=args.threshold,
        ).fit_predict(reduced)

    clusters, noise, anchor_rows = report(decks, labels, matrix, vocab,
                                          anchors, args.show_max)

    if args.out:
        def deck_info(row):
            deck = decks[row]
            return {"id": deck.id, "date": twda.deck_date(deck),
                    "name": deck.name, "player": deck.player,
                    "players": deck.event.players_count if deck.event else 0,
                    "event": deck.event.name if deck.event else ""}

        # stable review refs: C1..Cn by decreasing size
        ordered = sorted(clusters.items(), key=lambda kv: -len(kv[1]))
        payload = {
            "params": {
                "since": args.since, "until": args.until,
                "method": args.method, "components": args.components,
                "crypt_weight": args.crypt_weight, "min_df": args.min_df,
                "type_features": args.type_features,
                "min_cluster_size": args.min_cluster_size,
                "min_samples": args.min_samples,
                "subcluster": args.subcluster,
            },
            "clusters": [
                {
                    "ref": f"C{i}",
                    "size": len(rows),
                    "variants": (
                        subclusters(decks, rows, args.crypt_weight,
                                    args.subcluster)
                        if args.subcluster and len(rows) >= 8 else None
                    ),
                    "anchors": sorted(
                        f"{anchor_rows[r]['archetype']} "
                        f"({anchor_rows[r]['section']})"
                        for r in rows if r in anchor_rows
                    ),
                    "cards": top_cards(matrix, vocab, rows, 10),
                    "decks": sorted(
                        (deck_info(r) for r in rows),
                        key=lambda d: d["date"], reverse=True,
                    ),
                }
                for i, (label, rows) in enumerate(ordered, 1)
            ],
            "noise": sorted(
                (deck_info(r) for r in noise),
                key=lambda d: d["date"], reverse=True,
            ),
        }
        args.out.write_text(json.dumps(payload, indent=2))
        print(f"\nassignments written to {args.out}")


if __name__ == "__main__":
    main()
