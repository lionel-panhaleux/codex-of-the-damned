# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Fetch a TWDA deck from the KRCG API and emit an archetype-page decklist JSON.

The archetype pages' co-located .json files are exactly the KRCG API TWDA
format (https://api.krcg.org/twda/<id>), pretty-printed — only the deck `name`
is sometimes hand-cleaned afterwards (e.g. leading "(Wall)" tags stripped).

Usage: uv run scripts/page_json.py <twda_id> [-o output.json]
"""

import argparse
import json
import re
import sys
import urllib.request

API = "https://api.krcg.org/twda/"


def fetch(twda_id: str) -> dict:
    with urllib.request.urlopen(API + twda_id) as resp:
        deck = json.load(resp)
    # strip leading parenthesized tags owners tend to clean out of names
    deck["name"] = re.sub(r"^\s*\([^)]*\)\s*", "", deck.get("name") or "").strip()
    return deck


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
