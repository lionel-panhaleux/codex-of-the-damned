# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Fetch a TWDA deck from the KRCG API and emit an archetype-page decklist JSON.

`api.krcg.org/twda/<id>` serves the KRCG v5 deck schema (flat `cards` list and
nested `event` object), while `static/js/decklist.js` expects the grouped
`crypt`/`library` format used by every archetype `.json` file (matching
`toDecklist()` in `static/js/deck-search.js`). This script converts the API
payload to that format and strips leading parenthesized tags from the deck name.

Usage: uv run scripts/page_json.py <twda_id> [-o output.json]
"""

import argparse
import json
import re
import sys
import urllib.request

API = "https://api.krcg.org/twda/"

LIBRARY_ORDER = [
    "Master",
    "Conviction",
    "Action",
    "Ally",
    "Equipment",
    "Political Action",
    "Retainer",
    "Power",
    "Action Modifier",
    "Reaction",
    "Combat",
    "Event",
]


def _card_name(card: dict) -> str:
    suffix = card.get("unicity_suffix") or ""
    return f"{card['printed_name']} ({suffix})" if suffix else card["printed_name"]


def _sort_cards(cards: list[dict]) -> list[dict]:
    return sorted(cards, key=lambda c: (-c["count"], c["name"].lower()))


def to_decklist(deck: dict) -> dict:
    """Convert a KRCG v5 deck dict into the `static/js/decklist.js` schema."""
    if "crypt" in deck and "library" in deck and "cards" not in deck:
        return deck
    crypt: list[dict] = []
    sections: dict[str, list[dict]] = {}
    for card in deck["cards"]:
        info = {"id": card["id"], "name": _card_name(card), "count": card["count"]}
        if card["kind"] == "Crypt":
            crypt.append(info)
        else:
            card_type = "/".join(card["types"])
            sections.setdefault(card_type, []).append(info)

    def section_rank(card_type: str) -> tuple[int, str]:
        head = card_type.split("/")[0]
        idx = LIBRARY_ORDER.index(head) if head in LIBRARY_ORDER else len(LIBRARY_ORDER)
        return (idx, card_type)

    library = [
        {
            "type": card_type,
            "count": sum(c["count"] for c in cards),
            "cards": _sort_cards(cards),
        }
        for card_type, cards in sorted(
            sections.items(), key=lambda kv: section_rank(kv[0])
        )
    ]
    event = deck.get("event") or {}
    out: dict = {
        "crypt": {"count": sum(c["count"] for c in crypt), "cards": _sort_cards(crypt)},
        "library": {
            "count": sum(s["count"] for s in library),
            "cards": library,
        },
        "id": deck.get("id"),
        "name": re.sub(r"^\s*\([^)]*\)\s*", "", deck.get("name") or "").strip(),
    }
    if deck.get("player"):
        out["player"] = deck["player"]
    if deck.get("author"):
        out["author"] = deck["author"]
    if event.get("name"):
        out["event"] = event["name"]
    if event.get("place"):
        out["place"] = event["place"]
    if event.get("date"):
        out["date"] = event["date"]
    if event.get("players_count"):
        out["players_count"] = event["players_count"]
    if deck.get("score"):
        out["score"] = deck["score"]
    if deck.get("comment"):
        out["comments"] = deck["comment"]
    return out


def fetch(twda_id: str) -> dict:
    with urllib.request.urlopen(API + twda_id) as resp:
        deck = json.load(resp)
    return to_decklist(deck)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("twda_id")
    parser.add_argument("-o", "--output", help="output file (default: stdout)")
    args = parser.parse_args()
    deck = fetch(args.twda_id)
    text = json.dumps(deck, indent=4, sort_keys=True, ensure_ascii=False)
    if args.output:
        with open(args.output, "w") as f:
            f.write(text)
    else:
        sys.stdout.write(text)


if __name__ == "__main__":
    main()
