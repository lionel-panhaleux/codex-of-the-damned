#!/usr/bin/env python3
import json
import re
import sys
from warnings import warn

from krcg.deck import Deck
from krcg.vtes import VTES
from krcg import twda


def convert():
    VTES.load_from_vekn()
    VTES.configure()
    current = Deck()

    separator = False
    for line_num, line in enumerate(sys.stdin.readlines(), 1):
        line = line.rstrip()
        if line and len(line) > 2 and set(line).issubset({"=", "-"}):
            separator = True
            continue
        if not separator:
            continue
        # replace the custom `Nxx name` format with a classic `Nx name`
        line = re.sub(r"(\d)xx\s", r"\1x ", line)
        # lower all chars for easier parsing
        name, count, explicit = twda._get_card(line.lower())
        if name and count:
            # discard header lines (most likely card count)
            if name in twda.HEADERS:
                continue
            if not explicit and name in set(
                a.lower() for a in VTES.clans + VTES.disciplines
            ):
                warn(f"[{line_num}] improper discipline [{line}]")
                continue
            try:
                current.update({VTES.get_name(VTES[name]): count})
            except KeyError:
                if not explicit:
                    warn(f"[{line_num}] not parsed: [{line}]")
                else:
                    raise

    json.dump(VTES.deck_to_dict(current, None), sys.stdout, indent=2)


if __name__ == "__main__":
    convert()
