# /// script
# requires-python = ">=3.11"
# dependencies = ["krcg"]
# ///
"""Best cards: per-card play stats over a TWDA date window.

    uv run best_cards.py --since 2020-01-01 --top 20
    uv run best_cards.py --since 2023-01-01 --type Master --top 40
"""

from __future__ import annotations

import argparse
import collections

import twda


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--since", default="2020-01-01", help="ISO date, inclusive")
    parser.add_argument("--until", default="", help="ISO date, exclusive")
    parser.add_argument("--top", type=int, default=20, help="cards per section")
    parser.add_argument("--type", default="", help="only this card type")
    parser.add_argument("--refresh", action="store_true", help="force re-download")
    args = parser.parse_args()

    decks = twda.load_decks(args.since, args.until, args.refresh)
    total = len(decks)
    print(f"{total} decks from {args.since or 'origin'} to {args.until or 'now'}\n")

    # deck share (in how many decks) and total copies, per card name
    deck_count: collections.Counter[str] = collections.Counter()
    copies: collections.Counter[str] = collections.Counter()
    types: dict[str, str] = {}
    for deck in decks:
        features: dict[str, int] = {}
        for card in deck.cards:
            name = twda.merge_key(card)
            features[name] = features.get(name, 0) + card.count
            types[name] = "/".join(card.types)
        for name, count in features.items():
            deck_count[name] += 1
            copies[name] += count

    sections: dict[str, list[str]] = collections.defaultdict(list)
    for name in deck_count:
        sections[types[name]].append(name)

    for section in sorted(sections, key=lambda s: -len(sections[s])):
        if args.type and args.type.lower() not in section.lower():
            continue
        print(f"== {section} ==")
        ranked = sorted(sections[section], key=lambda n: -deck_count[n])
        for name in ranked[: args.top]:
            share = deck_count[name] / total
            print(f"  {share:6.1%}  {deck_count[name]:4d} decks  "
                  f"{copies[name]:5d} copies  {name}")
        print()


if __name__ == "__main__":
    main()
