# /// script
# requires-python = ">=3.11"
# dependencies = ["krcg"]
# ///
"""Disambiguate group-ambiguous crypt cards on the built best-cards pages.

merge_key collapses group variants, so a star reprinted across groups (Theo Bell
G2 Camarilla vs G6 Anarch — genuinely different cards) shows one merged count
under a bare name. This rewrites each such card_column to the group actually
played (its suffix in the name, its own deck count / copies), using the page's
window (all-time for red-flag pages, else 5 years).

    uv run disambiguate_crypt.py [--apply]
"""

from __future__ import annotations

import collections
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import twda  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[4]
BEST = REPO / "codex_of_the_damned" / "templates" / "best-cards"
CRYPT = twda.models.Card.Kind.CRYPT
SINCE = "2021-07-01"


def group_stats(decks):
    """(name,unique_name) -> (deck count, sorted per-deck copies)."""
    dc: collections.Counter = collections.Counter()
    copies: dict = collections.defaultdict(list)
    for d in decks:
        per: dict = {}
        for c in d.cards:
            if c.kind == CRYPT:
                per[(c.printed_name, c.unique_name)] = per.get(
                    (c.printed_name, c.unique_name), 0
                ) + c.count
        for key, n in per.items():
            dc[key] += 1
            copies[key].append(n)
    return dc, copies


def pctile(vals, q):
    s = sorted(vals)
    return s[min(len(s) - 1, max(0, round(q * (len(s) - 1))))]


def main():
    apply = "--apply" in sys.argv
    window = twda.load_decks(SINCE, "")
    alltime = twda.load_decks("", "")
    win_dc, win_cp = group_stats(window)
    all_dc, all_cp = group_stats(alltime)

    # printed_name -> set of unique_names (only multi-printing names matter)
    printings: dict = collections.defaultdict(set)
    for pname, uname in set(win_dc) | set(all_dc):
        printings[pname].add(uname)
    ambiguous = {p for p, u in printings.items() if len(u) > 1}

    call = re.compile(r'card_column\(\s*"((?:[^"\\]|\\.)*)"\s*,\s*decks=(\d+)\s*,\s*copies="([^"]*)"')
    changed = 0
    for page in sorted(BEST.glob("*/*.html")):
        src = page.read_text()
        red = "encompassing 30 years" in src or "spanning 30" in src
        dc, cp = (all_dc, all_cp) if red else (win_dc, win_cp)

        def repl(m):
            nonlocal changed
            name = m.group(1).replace('\\"', '"')
            base = re.sub(r"\s*\(G\d+\)\s*$", "", name)
            if base not in ambiguous:
                return m.group(0)
            # dominant printing of this name in the page's window
            cand = [(dc[(base, u)], u) for u in printings[base] if (base, u) in dc]
            if not cand:
                return m.group(0)
            n, uname = max(cand)
            copies = cp[(base, uname)]
            lo, hi = pctile(copies, 0.10), pctile(copies, 0.90)
            crange = f"{lo}" if lo == hi else f"{lo}-{hi}"
            if uname == name and n == int(m.group(2)):
                return m.group(0)
            changed += 1
            print(f"  {page.relative_to(BEST)}: {name!r} {m.group(2)}d "
                  f"-> {uname!r} {n}d")
            return f'card_column("{uname}", decks={n}, copies="{crange}"'

        new = call.sub(repl, src)
        if apply and new != src:
            page.write_text(new)
    print(f"{'rewrote' if apply else 'would rewrite'} {changed} crypt entries "
          f"({len(ambiguous)} ambiguous names known)")


if __name__ == "__main__":
    main()
