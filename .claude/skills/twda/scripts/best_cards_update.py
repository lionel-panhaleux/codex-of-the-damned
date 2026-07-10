# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Apply refreshed deck/copies figures from a best_cards_report.py run to the
best-cards page templates. Mechanical number layer of a refresh — curation
(add/drop cards, prose) is done separately by hand.

    uv run best_cards_update.py report.json --dry-run
    uv run best_cards_update.py report.json --apply

Each page has `{% call layout.card_column("Card Name", decks=N, copies="X-Y") %}`.
This rewrites decks= and copies= for cards found in the report's `all` table,
and reports: cards whose share collapsed (drop candidates) and names not found.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[4]
BEST = REPO / "codex_of_the_damned" / "templates" / "best-cards"

CALL = re.compile(
    r'card_column\(\s*"((?:[^"\\]|\\.)*)"'  # 1: display/first name
    r'(?:\s*,\s*"((?:[^"\\]|\\.)*)")?'  # 2: optional short name
    r'\s*,\s*decks=(\d+)\s*,\s*copies="([^"]*)"'  # 3: decks  4: copies
)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("report", help="the windowed (e.g. 5y) report")
    ap.add_argument(
        "--alltime", default="", help="all-time report for red-flag clan pages"
    )
    ap.add_argument("--apply", action="store_true")
    ap.add_argument(
        "--drop-below",
        type=float,
        default=0.015,
        help="flag listed cards whose recent share fell below this",
    )
    args = ap.parse_args()

    window_stats = json.loads(pathlib.Path(args.report).read_text())["all"]
    alltime_stats = (
        json.loads(pathlib.Path(args.alltime).read_text())["all"]
        if args.alltime
        else {}
    )
    # red-flag pages compile all-time stats (the "encompassing 30 years" note)
    changed_files = 0
    drops: list[str] = []
    missing: list[str] = []

    for page in sorted(BEST.glob("*/*.html")):
        src = page.read_text()
        red_flag = "encompassing 30 years" in src or "spanning 30" in src
        stats = alltime_stats if (red_flag and alltime_stats) else window_stats

        def repl(m: re.Match) -> str:
            raw = m.group(1).replace('\\"', '"')
            # match the report key: trim stray space, drop crypt group suffix
            candidates = [raw, raw.strip(), re.sub(r"\s*\(G\d+\)\s*$", "", raw).strip()]
            name = next((c for c in candidates if c in stats), raw.strip())
            s = stats.get(name)
            if not s:
                missing.append(f"{page.relative_to(BEST)}: {name!r}")
                return m.group(0)
            if s["share_recent"] < args.drop_below:
                drops.append(
                    f"{page.relative_to(BEST)}: {name} "
                    f"({s['decks']}d, {s['share_recent']:.1%} recent)"
                )
            out = m.group(0)
            out = re.sub(r"decks=\d+", f"decks={s['decks']}", out)
            out = re.sub(r'copies="[^"]*"', f'copies="{s["copies"]}"', out)
            return out

        new = CALL.sub(repl, src)
        if new != src:
            changed_files += 1
            if args.apply:
                page.write_text(new)

    verb = "updated" if args.apply else "would update"
    print(f"{verb} {changed_files} pages")
    print(f"\n{len(missing)} card names not in report (check rename / 0 decks):")
    for m in missing:
        print(f"  {m}")
    print(
        f"\n{len(drops)} listed cards below {args.drop_below:.1%} recent share (drop candidates):"
    )
    for d in sorted(drops):
        print(f"  {d}")


if __name__ == "__main__":
    main()
