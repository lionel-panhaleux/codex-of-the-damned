# /// script
# requires-python = ">=3.11"
# dependencies = ["scikit-learn>=1.4"]
# ///
"""Score a clustering run against the owner's curated classification.

The labels (data/classification.json) are the benchmark: any pipeline change
must improve — or at least not degrade — these scores before being adopted.

    uv run benchmark.py ../data/clusters.json ../data/classification.json

Reports ARI at two granularities (groups as-is, variants merged into their
main archetype), plus coverage counts. Also prints the archetype tier table
(qualifying decks per archetype, criteria from the classification).
"""

from __future__ import annotations

import argparse
import json
import pathlib

from sklearn.metrics import adjusted_rand_score


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("clusters", type=pathlib.Path)
    parser.add_argument("classification", type=pathlib.Path)
    parser.add_argument("--tiers", action="store_true",
                        help="print the archetype tier table and exit")
    args = parser.parse_args()

    truth = json.loads(args.classification.read_text())
    label = {}  # deck id -> group ref
    root = {}  # deck id -> root archetype ref
    parents = {g["ref"]: g["variant_of"] for g in truth["groups"]}
    names = {g["ref"]: g["name"] for g in truth["groups"]}

    def root_of(ref):
        seen = set()
        while parents.get(ref) and ref not in seen:
            seen.add(ref)
            ref = parents[ref]
        return ref

    for group in truth["groups"]:
        for deck in group["decks"]:
            label[deck["id"]] = group["ref"]
            root[deck["id"]] = root_of(group["ref"])

    if args.tiers:
        table = {}
        for group in truth["groups"]:
            r = root_of(group["ref"])
            entry = table.setdefault(r, {"name": names[r], "decks": 0, "q": 0})
            entry["decks"] += len(group["decks"])
            entry["q"] += sum(1 for d in group["decks"] if d["qualifying"])
        ranked = sorted(table.values(), key=lambda e: -e["q"])
        crit = truth["criteria"]
        print(f"qualifying = {crit['min_players']}+ players since"
              f" {crit['since']}; proven = 2+ qualifying")
        for entry in ranked:
            if entry["q"] < 2:
                break
            print(f"  {entry['q']:3d} qualifying  {entry['decks']:3d} total"
                  f"  {entry['name']}")
        proven = sum(1 for e in table.values() if e["q"] >= 2)
        print(f"{proven} proven archetypes / {len(table)} total")
        return

    pred_data = json.loads(args.clusters.read_text())
    pred = {d["id"]: c["ref"]
            for c in pred_data["clusters"] for d in c["decks"]}

    both = [i for i in label if i in pred]
    ari_groups = adjusted_rand_score(
        [pred[i] for i in both], [label[i] for i in both])
    ari_roots = adjusted_rand_score(
        [pred[i] for i in both], [root[i] for i in both])
    pred_noise = {d["id"] for d in pred_data["noise"]}
    truth_noise = {d["id"] for d in truth["noise"]}
    print(f"decks labeled: {len(label)}, clustered by run: {len(both)} "
          f"({len(both) / len(label):.0%} coverage)")
    print(f"ARI vs groups (variants distinct): {ari_groups:.3f}")
    print(f"ARI vs archetypes (variants merged): {ari_roots:.3f}")
    print(f"noise agreement: {len(pred_noise & truth_noise)} decks noise in "
          f"both, {len(pred_noise - truth_noise)} rescued by owner, "
          f"{len(truth_noise - pred_noise)} demoted to noise by owner")


if __name__ == "__main__":
    main()
