# /// script
# requires-python = ">=3.11"
# dependencies = ["krcg"]
# ///
"""Rebuild the owner's classification from a clustering run + editor state.

The review page's Export embeds the raw editor state (names, moves, variant
links, representatives, deletions). This script applies that state to the base
clustering — the same logic as the page — to produce data/classification.json
deterministically. Groups keep the page's order (variants nested after their
main); per-group anchors are recomputed from final membership.

    uv run apply_review.py ../data/clusters.json \
        ../data/review-2026-07-05.editor-state.json \
        --generated 2026-07-05 -o ../data/classification.json
"""

from __future__ import annotations

import argparse
import datetime
import json
import pathlib

import twda

CRITERIA_PLAYERS = 20
CRITERIA_YEARS = 3


def ref_key(ref: str):
    return (ref[0] == "G", int(ref[1:]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("clusters", type=pathlib.Path,
                        help="JSON from cluster.py --out")
    parser.add_argument("state", type=pathlib.Path,
                        help="editor_state JSON (from the page export)")
    parser.add_argument("--generated", required=True,
                        help="export date (ISO) — sets the criteria cutoff")
    parser.add_argument("-o", "--output", type=pathlib.Path, required=True)
    args = parser.parse_args()

    data = json.loads(args.clusters.read_text())
    state = json.loads(args.state.read_text())
    generated = datetime.date.fromisoformat(args.generated)
    cutoff = generated.replace(year=generated.year - CRITERIA_YEARS).isoformat()

    deck_info = {d["id"]: d for c in data["clusters"] for d in c["decks"]}
    deck_info.update({d["id"]: d for d in data["noise"]})

    # base assignment, then moves, then deletions sweep the rest to noise
    assign = {d["id"]: c["ref"] for c in data["clusters"] for d in c["decks"]}
    assign.update({d["id"]: "noise" for d in data["noise"]})
    known = {c["ref"] for c in data["clusters"]} | set(state["extraGroups"])
    for deck_id, target in state["moves"].items():
        if deck_id not in assign or (target != "noise" and target not in known):
            print(f"warning: ignoring move {deck_id} -> {target}")
            continue
        assign[deck_id] = target
    deleted = set(state["deleted"])
    for deck_id, ref in assign.items():
        if ref in deleted:
            assign[deck_id] = "noise"

    # page order: numeric C then G roots, variants nested after their main
    live = sorted((r for r in known if r not in deleted), key=ref_key)
    variant_of = {
        ref: target
        for ref, target in state["variantOf"].items()
        if ref in live and target in live and ref != target
    }
    children: dict[str, list[str]] = {}
    roots = []
    for ref in live:
        parent = variant_of.get(ref)
        if parent:
            children.setdefault(parent, []).append(ref)
        else:
            roots.append(ref)
    order: list[str] = []

    def visit(ref: str) -> None:
        if ref in order:
            return
        order.append(ref)
        for child in children.get(ref, []):
            visit(child)

    for ref in roots:
        visit(ref)
    for ref in live:  # cycle leftovers become roots
        visit(ref)

    anchors = twda.load_anchors()
    members: dict[str, list[str]] = {}
    for deck_id, ref in assign.items():
        members.setdefault(ref, []).append(deck_id)

    # unnamed groups keep their page placeholder: anchor slug or top card;
    # extra groups may carry their name in extraGroups only
    def default_name(ref: str) -> str:
        extra = state["extraGroups"].get(ref, {}).get("name")
        if extra:
            return extra
        cluster = next((c for c in data["clusters"] if c["ref"] == ref), None)
        if not cluster:
            return ""
        if cluster["anchors"]:
            return cluster["anchors"][0].split(" (")[0]
        return cluster["cards"][0].removesuffix(" [crypt]")

    def deck_entry(deck_id: str) -> dict:
        info = deck_info[deck_id]
        return {
            "id": deck_id,
            "date": info["date"],
            "name": info["name"],
            "players": info["players"],
            "qualifying": (
                info["players"] >= CRITERIA_PLAYERS and info["date"] >= cutoff
            ),
            "representative": bool(state["reps"].get(deck_id)),
        }

    groups = []
    for ref in order:
        ids = sorted(members.get(ref, []),
                     key=lambda i: deck_info[i]["date"], reverse=True)
        groups.append({
            "ref": ref,
            "name": state["names"].get(ref) or default_name(ref),
            "variant_of": variant_of.get(ref),
            "anchors": sorted(
                f"{anchors[i]['archetype']} ({anchors[i]['section']})"
                for i in ids if i in anchors
            ),
            "reviewed": bool(state["reviewed"].get(ref)),
            "decks": [deck_entry(i) for i in ids],
        })

    noise = sorted(members.get("noise", []),
                   key=lambda i: deck_info[i]["date"], reverse=True)
    payload = {
        "generated": args.generated,
        "params": data["params"],
        "criteria": {"min_players": CRITERIA_PLAYERS, "since": cutoff},
        "groups": groups,
        "noise": [deck_entry(i) for i in noise],
        "editor_state": state,
    }
    args.output.write_text(json.dumps(payload, indent=1))

    total = sum(len(g["decks"]) for g in groups) + len(noise)
    qualifying = sum(1 for g in groups for d in g["decks"] if d["qualifying"])
    print(f"{args.output}: {len(groups)} groups "
          f"({len(roots)} archetypes, {len(groups) - len(roots)} variants), "
          f"{total - len(noise)} decks classified + {len(noise)} noise "
          f"= {total} total, {qualifying} qualifying in groups")


if __name__ == "__main__":
    main()
