# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Rebuild the best-cards page templates from a signed-off proposal doc.

For each page the proposal lists the cards in final order. This assembles each
template: the existing header (h1 + intro inserts) and every card's existing
prose are REUSED verbatim; the card list, order, and deck/copies figures come
from the proposal + report. Cards with no existing prose get a TODO placeholder
for a writer to fill. Pages absent from `templates/best-cards` (e.g. Samedi) are
emitted with a stub header.

    uv run assemble_best_cards.py proposed.md report.json alltime.json
"""

from __future__ import annotations

import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parents[4]
BEST = REPO / "codex_of_the_damned" / "templates" / "best-cards"

CALL_RE = re.compile(
    r'\{%\s*call\s+layout\.card_column\(\s*"((?:[^"\\]|\\.)*)"[^)]*\)\s*%\}'
    r'(.*?)\{%\s*endcall\s*%\}',
    re.S,
)


def parse_proposal(path: str) -> dict[str, tuple[list[str], bool]]:
    """slug -> (ordered card names, is_all_time)."""
    out: dict[str, tuple[list[str], bool]] = {}
    for sec in re.split(r"(?=^## )", pathlib.Path(path).read_text(), flags=re.M):
        m = re.match(r"## (\S+)\s+\(\d+ cards( · all-time)?\)", sec)
        if not m:
            continue
        cards = re.findall(r"^- (.+?) — ", sec, flags=re.M)
        out[m.group(1)] = (cards, bool(m.group(2)))
    return out


def existing(slug: str) -> tuple[str | None, dict[str, str]]:
    """(header before the first card_column, {card name: inner prose})."""
    path = BEST / f"{slug}.html"
    if not path.exists():
        return None, {}
    text = path.read_text()
    prose = {
        name.replace('\\"', '"'): inner.strip("\n")
        for name, inner in CALL_RE.findall(text)
    }
    head = text.split("{% call", 1)[0].rstrip() if "{% call" in text else None
    return head, prose


def stub_header(slug: str) -> str:
    title = slug.split("/")[-1].replace("-", " ").title()
    warn = (
        '<div class="insert warn">\n'
        "    {% trans trimmed %}This list is compiled from statistics encompassing "
        "30 years,\n    as the clan has not scored enough wins in the last 5 years "
        "for relevant statistics otherwise.{% endtrans %}\n</div>\n"
    )
    return (
        '{% extends "best-cards/_layout.html" %}\n'
        '{% import "best-cards/_layout_card_column.html" as layout with context %}\n\n'
        "{% block content %}\n"
        f"<h1>{{{{ TODO_ICON }}}} {title}</h1>\n"
        f"{warn}"
        '<div class="insert tip">\n    <p>{% trans trimmed %}TODO intro.'
        "{% endtrans %}</p>\n</div>"
    )


def main() -> None:
    proposal, report_path, alltime_path = sys.argv[1], sys.argv[2], sys.argv[3]
    pages = parse_proposal(proposal)
    window = json.loads(pathlib.Path(report_path).read_text())["all"]
    alltime = json.loads(pathlib.Path(alltime_path).read_text())["all"]

    todo: dict[str, list[str]] = {}
    for slug, (cards, red) in pages.items():
        stats = alltime if red else window
        head, prose = existing(slug)
        new_page = head is None
        if new_page:
            head = stub_header(slug)
        blocks = []
        for name in cards:
            s = stats.get(name) or stats.get(name.replace(" (ADV)", "")) or {}
            decks = s.get("decks", 0)
            copies = s.get("copies", "")
            body = prose.get(name)
            if body is None:
                todo.setdefault(slug, []).append(name)
                body = "{% trans trimmed %}\nTODO.\n{% endtrans %}"
            esc = name.replace('"', '\\"')            # e.g. Jason "Son" Newberry
            blocks.append(
                f'{{% call layout.card_column("{esc}", decks={decks}, '
                f'copies="{copies}") %}}\n{body}\n{{% endcall %}}'
            )
        out = head + "\n\n" + "\n\n".join(blocks) + "\n{% endblock %}\n"
        (BEST / f"{slug}.html").write_text(out)

    total_new = sum(len(v) for v in todo.values())
    print(f"assembled {len(pages)} pages; {total_new} cards need prose across "
          f"{len(todo)} pages")
    pathlib.Path(sys.argv[4] if len(sys.argv) > 4 else "todo.json").write_text(
        json.dumps(todo, ensure_ascii=False, indent=1)
    )


if __name__ == "__main__":
    main()
