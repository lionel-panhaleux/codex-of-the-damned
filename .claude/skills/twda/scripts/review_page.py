# /// script
# requires-python = ">=3.11"
# dependencies = ["krcg"]
# ///
"""Generate the cluster review & classification editor page.

Input: the JSON written by `cluster.py --out`. Output: a single-file HTML page
(published as a Claude artifact or opened locally) where the owner reviews and
refines the classification: name groups, move decks between groups, create or
delete groups, mark groups as variants of a main group, star representative
decks. Decks link to vdb.im; decks not matching the archetype-page criteria
(20+ players, last 3 years) are greyed. All edits persist in localStorage;
the Export button produces the JSON used as input for page generation.

    uv run review_page.py clusters.json -o review.html
"""

from __future__ import annotations

import argparse
import datetime
import html
import json
import pathlib
import re

from krcg import models

import twda

CRITERIA_PLAYERS = 20  # archetypes/index.html: "at least 20 players
CRITERIA_YEARS = 3  # twice in the last 3 years"

# championship detection on event names; qualifiers ("EC2022 LCQ", "Road to
# the Spanish Nationals") are excluded first, and acronyms need an adjacent
# year so "Charlotte, NC" or "Campina agora tem SAC" don't match
QUALIFIER = re.compile(
    r"qualif|\bLCQ\b|\bFCQ\b|\bNCQ\b|road to|last chance|first chance"
    r"|preparation|warm.?up|side event|store championship", re.I)
CONTINENTAL = re.compile(
    r"\b(?:NAC|SAC|APAC|EC)\s*'?\d{2,4}\b"
    r"|continental championship|european championship", re.I)
NATIONAL = re.compile(
    r"\bNC\s*'?\d{2,4}\b|national championship|nationals\b"
    r"|nazionale|nacional|\bchampionship\b", re.I)


def esc(text: str) -> str:
    return html.escape(text or "", quote=True)


def decklist_data(deck_ids: list[str]) -> dict:
    """Compact embedded decklists (the artifact CSP forbids fetching them).

    {"names": {card_id: [display, type]}, "decks": {id: [[card_id, count]…]}}
    — names are stored once so 1,300 decks stay under ~1 MB. Crypt display
    names carry the capacity; crypt entries come first, sorted by count.
    """
    archive = twda.load_archive()
    cards = twda.load_cards()
    names: dict[int, list] = {}
    decks: dict[str, list] = {}
    for deck_id in deck_ids:
        deck = archive.get(deck_id)
        if not deck:
            continue
        crypt, library = [], []
        for card in deck.cards:
            if card.id not in names:
                if card.kind == models.Card.Kind.CRYPT:
                    capacity = getattr(cards.get(card.id), "capacity", None)
                    display = card.unique_name + (
                        f" ({capacity})" if capacity else "")
                    names[card.id] = [display, "Crypt"]
                else:
                    names[card.id] = [
                        card.unique_name,
                        "/".join(str(t) for t in card.types),
                    ]
            entry = [card.id, card.count]
            if card.kind == models.Card.Kind.CRYPT:
                crypt.append(entry)
            else:
                library.append(entry)
        crypt.sort(key=lambda e: -e[1])
        decks[deck_id] = crypt + library
    return {"names": names, "decks": decks}


def event_flag(event: str) -> str:
    if QUALIFIER.search(event):
        return ""
    if CONTINENTAL.search(event):
        return "CC"
    if NATIONAL.search(event):
        return "NC"
    return ""


def deck_row(deck: dict, cutoff: str) -> str:
    qualifying = deck["players"] >= CRITERIA_PLAYERS and deck["date"] >= cutoff
    name = esc(deck["name"]) or "<em>(unnamed)</em>"
    flag = event_flag(deck.get("event", "")) if qualifying else ""
    flag_html = (
        f'<span class="d-flag {flag.lower()}">{flag}</span>' if flag
        else '<span class="d-flag"></span>'
    )
    return (
        f'<li data-id="{esc(deck["id"])}" data-q="{int(qualifying)}"'
        f'{"" if qualifying else " class=nq"}>'
        f'<input type="checkbox" class="sel" aria-label="select deck">'
        f'<button class="star" aria-pressed="false" '
        f'title="representative">★</button>'
        f'<a href="https://vdb.im/decks/{esc(deck["id"])}" target="_blank" '
        f'rel="noopener" title="{esc(deck.get("event", ""))}">'
        f'<span class="d-date">{deck["date"]}</span>'
        f'<span class="d-name">{name}</span>'
        f'{flag_html}'
        f'<span class="d-players">{deck["players"]}p</span>'
        f'<span class="d-player">{esc(deck["player"])}</span></a></li>'
    )


def card_chips(cards: list[str]) -> str:
    out = []
    for card in cards:
        if card.endswith(" [crypt]"):
            out.append(f'<span class="chip crypt">{esc(card[:-8])}</span>')
        elif card.endswith(" [type total]"):
            out.append(f'<span class="chip total">Σ {esc(card[:-13])}</span>')
        else:
            out.append(f'<span class="chip">{esc(card)}</span>')
    return "".join(out)


def deck_rows(cluster: dict, cutoff: str) -> str:
    """Deck rows, honoring proposed variant sub-groups when present."""
    variants = cluster.get("variants")
    if not variants:
        return "".join(deck_row(deck, cutoff) for deck in cluster["decks"])
    by_id = {deck["id"]: deck for deck in cluster["decks"]}
    out = []
    for i, variant in enumerate(variants):
        decks = [by_id[i] for i in variant["ids"] if i in by_id]
        decks.sort(key=lambda d: d["date"], reverse=True)
        cards = ", ".join(
            c.removesuffix(" [crypt]") for c in variant["cards"][:5]
        )
        out.append(
            f'<li class="vdiv" data-ids="{esc(json.dumps(variant["ids"]))}">'
            f'<span class="v-label">variant {chr(65 + i)} · '
            f'{len(decks)} decks</span>'
            f'<span class="v-cards">{esc(cards)}</span>'
            f'<button class="splitout">split into own group</button></li>'
        )
        out.extend(deck_row(deck, cutoff) for deck in decks)
    return "".join(out)


def group_section(cluster: dict, cutoff: str) -> str:
    ref = cluster["ref"]
    dates = sorted(deck["date"] for deck in cluster["decks"])
    span = f"{dates[0][:7]} → {dates[-1][:7]}" if dates else ""
    anchors = "".join(
        f'<span class="anchor">⚓ {esc(a)}</span>' for a in cluster["anchors"]
    )
    hint = (
        cluster["anchors"][0].split(" (")[0]
        if cluster["anchors"]
        else cluster["cards"][0].removesuffix(" [crypt]")
    )
    rows = deck_rows(cluster, cutoff)
    return f'''
<section class="cluster" id="{ref.lower()}" data-ref="{ref}"
 data-anchors="{esc(json.dumps(cluster["anchors"]))}">
<header class="c-head">
<span class="ref">{ref}</span>
<input class="g-name" placeholder="{esc(hint)}" aria-label="group name">
<span class="size"></span>
<span class="dates">{span}</span>
{anchors}
<label class="variant">variant of
<input class="g-variant" list="groups" placeholder="—"></label>
<button class="rev" aria-pressed="false">reviewed</button>
<button class="del" title="delete group (members go to noise)">✕</button>
</header>
<div class="cards">{card_chips(cluster["cards"])}</div>
<ul class="decks">{rows}</ul>
</section>'''


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=pathlib.Path,
                        help="JSON from cluster.py --out")
    parser.add_argument("-o", "--output", type=pathlib.Path, required=True)
    args = parser.parse_args()

    data = json.loads(args.input.read_text())
    clusters, noise, params = data["clusters"], data["noise"], data["params"]
    today = datetime.date.today()
    cutoff = today.replace(year=today.year - CRITERIA_YEARS).isoformat()
    total = sum(c["size"] for c in clusters) + len(noise)

    toc = "".join(
        f'<a href="#{c["ref"].lower()}" id="toc-{c["ref"].lower()}">'
        f'<span class="t-ref">{c["ref"]}</span>'
        f'<span class="t-size">{c["size"]}</span>'
        f'<span class="t-hint">{esc(c["anchors"][0].split(" (")[0] if c["anchors"] else c["cards"][0].removesuffix(" [crypt]"))}</span>'
        f'<span class="t-q"></span></a>'
        for c in clusters
    )
    sections = "".join(group_section(c, cutoff) for c in clusters)
    noise_rows = "".join(deck_row(d, cutoff) for d in noise)
    all_ids = [d["id"] for c in clusters for d in c["decks"]]
    all_ids += [d["id"] for d in noise]
    decklists = json.dumps(
        decklist_data(all_ids), separators=(",", ":")
    ).replace("</", "<\\/")
    config = json.dumps({
        "cutoff": cutoff, "minPlayers": CRITERIA_PLAYERS,
        "generated": today.isoformat(), "params": params,
    })

    page = (
        HEAD
        + f'''
<div class="wrap">
<nav aria-label="Groups">{toc}<div id="toc-extra"></div></nav>
<main>
<div class="page-head">
<h1>TWDA 5-Year Cluster Review</h1>
<div class="meta">
window <b>{params["since"]} → {today}</b> · {total} decks ·
<b>{len(clusters)} groups</b> · <b>{len(noise)} noise</b> ·
criteria: <b>{CRITERIA_PLAYERS}+ players since {cutoff}</b>
(greyed decks don't qualify) · hover a deck for its list ·
<span id="progress"></span>
</div>
<div class="toolbar">
<input id="filter" type="search"
 placeholder="Filter groups — card, deck name, player, anchor…"
 aria-label="Filter groups">
<button id="export" class="tool">Export</button>
<button id="import" class="tool">Import</button>
</div>
</div>
{sections}
<details class="noise cluster" id="noise" data-ref="noise" open>
<summary>Noise — decks in no group (newest first) ·
<span class="size"></span></summary>
<ul class="decks">{noise_rows}</ul>
</details>
</main>
</div>
<datalist id="groups"></datalist>
<div id="actionbar" hidden>
<span id="selcount"></span>
<input id="movetarget" list="groups" placeholder="move to group…">
<button id="doMove">Move</button>
<button id="newGroup">New group</button>
<button id="toNoise">To noise</button>
<button id="clearSel">Clear</button>
</div>
<dialog id="io">
<h2 id="io-title"></h2>
<textarea id="io-text" spellcheck="false"></textarea>
<div class="io-actions">
<button id="io-copy">Copy</button>
<button id="io-apply" hidden>Apply import</button>
<button id="io-close">Close</button>
</div>
</dialog>
<div id="dlpanel" hidden></div>
<script type="application/json" id="decklists">{decklists}</script>
<script>const CONFIG = {config};</script>
'''
        + SCRIPT
    )
    args.output.write_text(page)
    print(f"{args.output} {args.output.stat().st_size / 1024:.0f} KB")


HEAD = '''<title>TWDA 5-Year Cluster Review</title>
<style>
:root {
  --ground: #FAF8F7; --panel: #FFFFFF; --ink: #1C1817; --muted: #6E625F;
  --accent: #8E2A35; --accent-ink: #FFFFFF; --line: #E5DEDC;
  --chip-bg: #F1EBE9; --hover: #F5EFED; --ok: #3D7A4E; --star: #B8860B; --spice: #1F6E8C;
}
@media (prefers-color-scheme: dark) {
  :root {
    --ground: #171213; --panel: #1F191A; --ink: #EDE7E4; --muted: #9B8D89;
    --accent: #D4707B; --accent-ink: #2A1518; --line: #2E2628;
    --chip-bg: #2A2324; --hover: #292122; --ok: #7FBF8F; --star: #E0B94F; --spice: #6FB7D4;
  }
}
:root[data-theme="dark"] {
  --ground: #171213; --panel: #1F191A; --ink: #EDE7E4; --muted: #9B8D89;
  --accent: #D4707B; --accent-ink: #2A1518; --line: #2E2628;
  --chip-bg: #2A2324; --hover: #292122; --ok: #7FBF8F; --star: #E0B94F; --spice: #6FB7D4;
}
:root[data-theme="light"] {
  --ground: #FAF8F7; --panel: #FFFFFF; --ink: #1C1817; --muted: #6E625F;
  --accent: #8E2A35; --accent-ink: #FFFFFF; --line: #E5DEDC;
  --chip-bg: #F1EBE9; --hover: #F5EFED; --ok: #3D7A4E; --star: #B8860B; --spice: #1F6E8C;
}
* { box-sizing: border-box; }
body {
  background: var(--ground); color: var(--ink); margin: 0;
  font: 15px/1.45 system-ui, -apple-system, "Segoe UI", sans-serif;
}
.wrap { display: flex; max-width: 1280px; margin: 0 auto; }
nav {
  width: 230px; flex: none; position: sticky; top: 0; height: 100vh;
  overflow-y: auto; padding: 16px 8px 40px 16px;
  border-right: 1px solid var(--line);
}
nav a {
  display: grid; grid-template-columns: 2.8em 2em 1fr 1.8em; gap: 5px;
  padding: 2px 6px; border-radius: 4px; text-decoration: none;
  color: var(--ink); font-size: 12.5px; align-items: baseline;
}
nav a.t-variant { padding-left: 20px; }
nav a.t-variant .t-ref::before { content: "↳ "; color: var(--muted); }
.t-q { color: var(--ok); font-weight: 700; text-align: right;
  font-variant-numeric: tabular-nums; }
nav a:hover { background: var(--hover); }
nav a.done .t-ref { color: var(--ok); }
nav a.done .t-ref::after { content: " ✓"; }
.t-ref { color: var(--accent); font-weight: 600;
  font-variant-numeric: tabular-nums; }
.t-size { color: var(--muted); text-align: right;
  font-variant-numeric: tabular-nums; }
.t-hint { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
main { flex: 1; min-width: 0; padding: 0 24px 120px; }
.page-head {
  position: sticky; top: 0; z-index: 3; background: var(--ground);
  padding: 14px 0 10px; border-bottom: 1px solid var(--line);
  margin-bottom: 18px;
}
h1 {
  font: 600 21px/1.2 "Iowan Old Style", Palatino, Georgia, serif;
  margin: 0 0 4px; text-wrap: balance;
}
.meta { color: var(--muted); font-size: 12.5px; }
.meta b { color: var(--ink); font-weight: 600; }
#progress { color: var(--ok); font-weight: 600; }
.toolbar { display: flex; gap: 8px; margin-top: 8px; }
#filter {
  flex: 1; max-width: 420px; padding: 5px 10px;
  border: 1px solid var(--line); border-radius: 6px;
  background: var(--panel); color: var(--ink); font: inherit; font-size: 13px;
}
.tool, #actionbar button, .io-actions button {
  border: 1px solid var(--line); background: var(--panel); color: var(--ink);
  border-radius: 6px; padding: 4px 12px; font: inherit; font-size: 13px;
  cursor: pointer;
}
.tool:hover, #actionbar button:hover, .io-actions button:hover {
  border-color: var(--accent); color: var(--accent);
}
.cluster {
  background: var(--panel); border: 1px solid var(--line); border-radius: 8px;
  padding: 12px 16px 8px; margin-bottom: 16px; scroll-margin-top: 110px;
}
.cluster.as-variant {
  margin-left: 30px; margin-top: -8px;
  border-left: 3px solid var(--accent);
}
.c-head {
  display: flex; flex-wrap: wrap; align-items: center; gap: 10px;
}
.ref { color: var(--accent); font-weight: 700; font-size: 17px; }
.g-name {
  border: none; border-bottom: 1px dashed var(--line); background: none;
  color: var(--ink); font: 600 15px/1.3 inherit; padding: 1px 4px;
  min-width: 12em;
}
.g-name:focus { outline: none; border-bottom-color: var(--accent); }
.size { font-weight: 600; font-size: 13px; }
.size .q { color: var(--ok); }
.size .proven {
  background: var(--ok); color: var(--ground); border-radius: 99px;
  padding: 0 8px; font-size: 11.5px; margin-left: 4px;
}
.dates { color: var(--muted); font-size: 12.5px;
  font-variant-numeric: tabular-nums; }
.anchor {
  background: var(--accent); color: var(--accent-ink); border-radius: 99px;
  padding: 1px 9px; font-size: 12px; font-weight: 600;
}
.variant { color: var(--muted); font-size: 12px; margin-left: auto; }
.g-variant {
  border: 1px solid var(--line); border-radius: 5px; background: none;
  color: var(--ink); font: inherit; font-size: 12px; padding: 1px 6px;
  width: 11em;
}
.rev, .del {
  border: 1px solid var(--line); background: none; color: var(--muted);
  border-radius: 6px; padding: 2px 10px; font: inherit; font-size: 12.5px;
  cursor: pointer;
}
.rev:hover { border-color: var(--ok); color: var(--ok); }
.rev[aria-pressed="true"] {
  background: var(--ok); border-color: var(--ok); color: var(--ground);
}
.del:hover, .del.arm { border-color: var(--accent); color: var(--accent); }
.del.arm { font-weight: 700; }
button:focus-visible, a:focus-visible, input:focus-visible {
  outline: 2px solid var(--accent); outline-offset: 1px;
}
.cards { display: flex; flex-wrap: wrap; gap: 5px; margin: 10px 0; }
.chip {
  border: 1px solid var(--line); background: var(--chip-bg);
  border-radius: 99px; padding: 1px 9px; font-size: 12px;
}
.chip.crypt {
  background: none; border-color: var(--accent); color: var(--accent);
  font-weight: 600;
}
.chip.total { border-style: dashed; font-style: italic; }
.decks { list-style: none; margin: 0 -8px; padding: 0; }
.decks li {
  display: flex; align-items: baseline; gap: 6px; border-radius: 5px;
  padding: 2px 8px;
}
.decks li:hover { background: var(--hover); }
.decks li.nq a { opacity: 0.45; }
.sel { accent-color: var(--accent); }
.star {
  border: none; background: none; color: var(--line); cursor: pointer;
  font-size: 14px; padding: 0 2px;
}
.star:hover { color: var(--star); }
.star[aria-pressed="true"] { color: var(--star); }
.decks a {
  flex: 1; display: grid; grid-template-columns: 6.4em 1fr 2.4em 3em 11em;
  gap: 12px; text-decoration: none; color: var(--ink); align-items: baseline;
  min-width: 0;
}
.d-flag {
  font-size: 10.5px; font-weight: 700; text-align: center;
  border-radius: 4px; align-self: center;
}
.d-flag.nc { border: 1px solid var(--accent); color: var(--accent); }
.d-flag.cc { background: var(--accent); color: var(--accent-ink); }
.decks a:hover .d-name { text-decoration: underline; }
.d-date {
  font-family: ui-monospace, "SF Mono", Menlo, monospace; font-size: 12px;
  color: var(--muted); font-variant-numeric: tabular-nums;
}
.d-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  color: var(--accent); }
.d-players { color: var(--muted); font-size: 12px; text-align: right;
  font-variant-numeric: tabular-nums; }
.d-player { color: var(--muted); font-size: 12.5px; overflow: hidden;
  text-overflow: ellipsis; white-space: nowrap; }
details.noise summary {
  cursor: pointer; font-weight: 600; font-size: 16px; padding: 4px 0;
}
.vdiv {
  border-top: 1px dashed var(--line); margin-top: 4px; padding-top: 4px;
  font-size: 12px; color: var(--muted); align-items: center;
}
.vdiv:hover { background: none; }
.v-label { font-weight: 700; color: var(--ink); white-space: nowrap; }
.v-cards { flex: 1; overflow: hidden; text-overflow: ellipsis;
  white-space: nowrap; font-style: italic; }
.splitout {
  border: 1px solid var(--line); background: none; color: var(--muted);
  border-radius: 5px; padding: 1px 8px; font: inherit; font-size: 11.5px;
  cursor: pointer; white-space: nowrap;
}
.splitout:hover { border-color: var(--accent); color: var(--accent); }
#actionbar {
  position: fixed; bottom: 18px; left: 50%; transform: translateX(-50%);
  display: flex; gap: 8px; align-items: center; z-index: 4;
  background: var(--panel); border: 1px solid var(--accent);
  border-radius: 10px; padding: 10px 14px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.25);
}
#actionbar[hidden] { display: none; }
#selcount { font-weight: 600; font-size: 13px; }
#movetarget {
  border: 1px solid var(--line); border-radius: 6px; background: var(--ground);
  color: var(--ink); font: inherit; font-size: 13px; padding: 4px 8px;
  width: 16em;
}
#io {
  background: var(--panel); color: var(--ink); border: 1px solid var(--line);
  border-radius: 10px; width: min(700px, 90vw);
}
#io::backdrop { background: rgba(0,0,0,0.5); }
#io-text {
  width: 100%; height: 300px; font: 12px/1.4 ui-monospace, Menlo, monospace;
  background: var(--ground); color: var(--ink); border: 1px solid var(--line);
  border-radius: 6px; padding: 8px;
}
.io-actions { display: flex; gap: 8px; margin-top: 8px; }
.hidden { display: none !important; }
#dlpanel {
  position: fixed; z-index: 20; width: 360px; max-height: 76vh;
  overflow: hidden; pointer-events: none;
  background: var(--panel); border: 1px solid var(--line);
  border-radius: 8px; padding: 10px 14px;
  box-shadow: 0 6px 28px rgba(0,0,0,0.3);
  font-size: 12px; line-height: 1.35;
}
#dlpanel .dl-head {
  font-weight: 700; font-size: 12.5px; margin-bottom: 2px;
}
#dlpanel .dl-sub { color: var(--muted); margin-bottom: 6px; }
#dlpanel .dl-cols { column-count: 2; column-gap: 16px; }
#dlpanel h3 {
  font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em;
  color: var(--accent); margin: 6px 0 2px; break-after: avoid;
}
#dlpanel ul { list-style: none; margin: 0; padding: 0; }
#dlpanel li { break-inside: avoid; }
#dlpanel .n { color: var(--muted); font-variant-numeric: tabular-nums; }
#dlpanel li.odd { color: var(--spice); font-weight: 600; }
#dlpanel .odd-n { color: var(--spice); font-weight: 700; }
#dlpanel .pct { color: var(--muted); font-weight: 400; font-size: 10px; }
#dlpanel .dl-missing { margin-top: 6px; color: var(--muted); }
#dlpanel .dl-missing h3 { margin: 0 0 2px; }
#dlpanel .dl-missing span { white-space: nowrap; }
#dlpanel .dl-note {
  color: var(--muted); font-size: 10.5px; margin-top: 6px;
  border-top: 1px solid var(--line); padding-top: 4px;
}
@media (max-width: 800px) {
  nav { display: none; }
  .decks a { grid-template-columns: 6.4em 1fr 2.4em 3em; }
  .d-player { display: none; }
  .cluster.as-variant { margin-left: 14px; }
}
@media (prefers-reduced-motion: no-preference) {
  html { scroll-behavior: smooth; }
}
</style>'''


SCRIPT = r'''<script>
const KEY = "twda-5y-review";
let state = JSON.parse(localStorage.getItem(KEY) || "{}");
// migrate the flat v1 {ref: bool} reviewed map
if (Object.values(state).some(v => typeof v === "boolean")) {
  state = { reviewed: state };
}
state = Object.assign(
  { reviewed: {}, names: {}, variantOf: {}, moves: {}, reps: {},
    extraGroups: {}, deleted: {} },
  state);
const save = () => localStorage.setItem(KEY, JSON.stringify(state));
let baselines = {};  // group ref -> card presence; reset on every edit
const $ = (sel, el) => (el || document).querySelector(sel);
const $$ = (sel, el) => [...(el || document).querySelectorAll(sel)];
const main = $("main");
const noiseUl = $("#noise .decks");

function groupSections() {
  return $$(".cluster[data-ref]").filter(s => s.dataset.ref !== "noise");
}
function groupLabel(sec) {
  const name = $(".g-name", sec) ? $(".g-name", sec).value.trim() : "";
  return sec.dataset.ref + (name ? " — " + name : "");
}
function findGroup(refOrLabel) {
  if (!refOrLabel) return null;
  const ref = refOrLabel.split(" — ")[0].trim();
  if (ref.toLowerCase() === "noise") return $("#noise");
  return groupSections().find(s => s.dataset.ref === ref) || null;
}

function parentRef(ref) {
  const target = state.variantOf[ref];
  if (!target) return null;
  const sec = findGroup(target);
  return sec && !sec.hidden && sec.dataset.ref !== "noise"
    ? sec.dataset.ref : null;
}

function refKey(ref) {
  return (ref[0] === "G" ? 1000000 : 0) + parseInt(ref.slice(1), 10);
}

function reorderAll() {
  const secs = groupSections().filter(s => !s.hidden)
    .sort((a, b) => refKey(a.dataset.ref) - refKey(b.dataset.ref));
  const children = {};
  const roots = [];
  for (const sec of secs) {
    const parent = parentRef(sec.dataset.ref);
    if (parent && parent !== sec.dataset.ref) {
      (children[parent] = children[parent] || []).push(sec);
    } else roots.push(sec);
  }
  const order = [];
  const seen = new Set();
  const visit = (sec, depth) => {
    if (seen.has(sec)) return;
    seen.add(sec); order.push(sec);
    sec.classList.toggle("as-variant", depth > 0);
    const toc = $("#toc-" + sec.id);
    if (toc) toc.classList.toggle("t-variant", depth > 0);
    for (const child of children[sec.dataset.ref] || []) visit(child, depth + 1);
  };
  roots.forEach(sec => visit(sec, 0));
  secs.forEach(sec => visit(sec, 0));  // cycle leftovers become roots
  const nav = $("nav");
  const noiseEl = $("#noise");
  for (const sec of order) {
    main.insertBefore(sec, noiseEl);
    const toc = $("#toc-" + sec.id);
    if (toc) nav.appendChild(toc);
  }
}

function makeExtraGroup(ref, name) {
  const sec = document.createElement("section");
  sec.className = "cluster"; sec.id = ref.toLowerCase();
  sec.dataset.ref = ref; sec.dataset.anchors = "[]";
  sec.innerHTML = `<header class="c-head"><span class="ref">${ref}</span>
    <input class="g-name" placeholder="new group" aria-label="group name">
    <span class="size"></span>
    <label class="variant">variant of
    <input class="g-variant" list="groups" placeholder="—"></label>
    <button class="rev" aria-pressed="false">reviewed</button>
    <button class="del" title="delete group">✕</button></header>
    <ul class="decks"></ul>`;
  main.insertBefore(sec, $("#noise"));
  if (name) $(".g-name", sec).value = name;
  const toc = document.createElement("a");
  toc.href = "#" + ref.toLowerCase(); toc.id = "toc-" + ref.toLowerCase();
  toc.innerHTML = `<span class="t-ref">${ref}</span>
    <span class="t-size"></span><span class="t-hint"></span>
    <span class="t-q"></span>`;
  $("#toc-extra").appendChild(toc);
  wireGroup(sec);
  return sec;
}

function moveDeck(id, targetSec) {
  const li = $(`li[data-id="${CSS.escape(id)}"]`);
  if (li && targetSec) $(".decks", targetSec).appendChild(li);
}

function recount() {
  const options = groupSections().filter(s => !s.hidden).map(groupLabel);
  $("#groups").innerHTML = options.concat("noise")
    .map(o => `<option value="${o.replace(/"/g, "&quot;")}">`).join("");
  // per-section qualifying counts, then combined counts on variant roots
  const own = {};
  for (const sec of groupSections().filter(s => !s.hidden)) {
    own[sec.dataset.ref] = $$(".decks li[data-id]", sec)
      .filter(li => li.dataset.q === "1").length;
  }
  const combined = {};
  for (const [ref, q] of Object.entries(own)) {
    let root = ref;
    const seen = new Set([ref]);
    let parent;
    while ((parent = parentRef(root)) && !seen.has(parent)) {
      seen.add(parent); root = parent;
    }
    combined[root] = (combined[root] || 0) + q;
  }
  for (const sec of groupSections().concat($("#noise"))) {
    const decks = $$(".decks li[data-id]", sec);
    const ref = sec.dataset.ref;
    const q = own[ref] || 0;
    const isRoot = !parentRef(ref);
    const total = combined[ref] || 0;
    const size = $(".size", sec);
    if (size) size.innerHTML = ref === "noise"
      ? `${decks.length} decks`
      : `${decks.length} decks · <span class="q">${q} qualifying</span>` +
        (isRoot && total >= 2
          ? `<span class="proven">proven · ${total}</span>` : "");
    const toc = $("#toc-" + sec.id);
    if (toc) {
      const ts = $(".t-size", toc);
      if (ts) ts.textContent = decks.length;
      const name = $(".g-name", sec);
      const th = $(".t-hint", toc);
      if (name && name.value.trim() && th) th.textContent = name.value.trim();
      const tq = $(".t-q", toc);
      if (tq) tq.textContent = isRoot && total >= 2 ? total : "";
    }
    if (ref !== "noise") {
      sec.dataset.search = (sec.textContent + " " + ref).toLowerCase();
    }
  }
  baselines = {};  // group compositions changed
  let done = 0;
  const secs = groupSections().filter(s => !s.hidden);
  for (const sec of secs) {
    const on = !!state.reviewed[sec.dataset.ref];
    const rev = $(".rev", sec);
    if (rev) rev.setAttribute("aria-pressed", on);
    const toc = $("#toc-" + sec.id);
    if (toc) toc.classList.toggle("done", on);
    if (on) done++;
  }
  $("#progress").textContent = `${done}/${secs.length} reviewed`;
}

function selection() { return $$(".sel:checked"); }
function updateBar() {
  const n = selection().length;
  $("#actionbar").hidden = n === 0;
  $("#selcount").textContent = n + " selected";
}
function clearSelection() {
  selection().forEach(cb => { cb.checked = false; });
  updateBar();
}
function moveSelection(targetSec) {
  if (!targetSec) return;
  for (const cb of selection()) {
    const li = cb.closest("li");
    state.moves[li.dataset.id] = targetSec.dataset.ref;
    $(".decks", targetSec).appendChild(li);
    cb.checked = false;
  }
  save(); recount(); updateBar();
}

function wireGroup(sec) {
  const ref = sec.dataset.ref;
  const name = $(".g-name", sec);
  if (name) name.addEventListener("input", () => {
    state.names[ref] = name.value;
    if (state.extraGroups[ref]) state.extraGroups[ref].name = name.value;
    save(); recount();
  });
  const variant = $(".g-variant", sec);
  if (variant) variant.addEventListener("change", () => {
    const target = findGroup(variant.value);
    state.variantOf[ref] =
      target && target.dataset.ref !== ref ? target.dataset.ref : "";
    // refuse cycles (A variant of B variant of A)
    let cur = ref;
    const seen = new Set([ref]);
    let parent;
    while ((parent = state.variantOf[cur])) {
      if (parent === ref || seen.has(parent)) {
        if (parent === ref) state.variantOf[ref] = "";
        break;
      }
      seen.add(parent); cur = parent;
    }
    variant.value = state.variantOf[ref]
      ? groupLabel(findGroup(state.variantOf[ref])) : "";
    save(); reorderAll(); recount();
  });
  const rev = $(".rev", sec);
  if (rev) rev.addEventListener("click", () => {
    state.reviewed[ref] = !state.reviewed[ref];
    save(); recount();
  });
  const del = $(".del", sec);
  if (del) del.addEventListener("click", () => {
    if (!del.classList.contains("arm")) {
      del.classList.add("arm"); del.textContent = "confirm ✕";
      setTimeout(() => {
        del.classList.remove("arm"); del.textContent = "✕";
      }, 3000);
      return;
    }
    for (const li of $$(".decks li[data-id]", sec)) {
      state.moves[li.dataset.id] = "noise";
      noiseUl.appendChild(li);
    }
    state.deleted[ref] = true;
    sec.hidden = true;
    const toc = $("#toc-" + sec.id);
    if (toc) toc.classList.add("hidden");
    save(); reorderAll(); recount();
  });
}

function exportState() {
  const groups = groupSections().filter(s => !s.hidden).map(sec => ({
    ref: sec.dataset.ref,
    name: ($(".g-name", sec) ? $(".g-name", sec).value.trim() : "") ||
      ($(".g-name", sec) ? $(".g-name", sec).placeholder : ""),
    variant_of: state.variantOf[sec.dataset.ref] || null,
    anchors: JSON.parse(sec.dataset.anchors || "[]"),
    reviewed: !!state.reviewed[sec.dataset.ref],
    decks: $$(".decks li[data-id]", sec).map(li => ({
      id: li.dataset.id,
      qualifying: li.dataset.q === "1",
      representative:
        $(".star", li).getAttribute("aria-pressed") === "true",
    })),
  }));
  return {
    generated: CONFIG.generated, params: CONFIG.params,
    criteria: { min_players: CONFIG.minPlayers, since: CONFIG.cutoff },
    groups,
    noise: $$(".decks li[data-id]", $("#noise")).map(li => li.dataset.id),
    editor_state: state,
  };
}

function openDialog(title, text, importable) {
  $("#io-title").textContent = title;
  $("#io-text").value = text;
  $("#io-apply").hidden = !importable;
  $("#io").showModal();
}

function applyState() {
  for (const [ref, info] of Object.entries(state.extraGroups)) {
    makeExtraGroup(ref, info.name || "");
  }
  for (const [ref, name] of Object.entries(state.names)) {
    const sec = findGroup(ref);
    if (sec && $(".g-name", sec)) $(".g-name", sec).value = name;
  }
  for (const [id, target] of Object.entries(state.moves)) {
    moveDeck(id, findGroup(target));
  }
  for (const ref of Object.keys(state.deleted)) {
    const sec = findGroup(ref);
    if (!sec) continue;
    for (const li of $$(".decks li", sec)) noiseUl.appendChild(li);
    sec.hidden = true;
    const toc = $("#toc-" + sec.id);
    if (toc) toc.classList.add("hidden");
  }
  for (const [ref, target] of Object.entries(state.variantOf)) {
    const sec = findGroup(ref);
    const targetSec = findGroup(target);
    if (sec && targetSec && $(".g-variant", sec)) {
      $(".g-variant", sec).value = groupLabel(targetSec);
    }
  }
  for (const id of Object.keys(state.reps)) {
    const li = $(`li[data-id="${CSS.escape(id)}"]`);
    if (li) $(".star", li).setAttribute("aria-pressed", "true");
  }
}

// ---- wire it all
groupSections().forEach(wireGroup);
applyState();
reorderAll();
recount();

document.addEventListener("change", e => {
  if (e.target.classList.contains("sel")) updateBar();
});
document.addEventListener("click", e => {
  if (e.target.classList.contains("star")) {
    const li = e.target.closest("li");
    const on = e.target.getAttribute("aria-pressed") !== "true";
    e.target.setAttribute("aria-pressed", on);
    if (on) state.reps[li.dataset.id] = true;
    else delete state.reps[li.dataset.id];
    save();
  }
});
$("#doMove").addEventListener("click", () => {
  moveSelection(findGroup($("#movetarget").value));
  $("#movetarget").value = "";
});
$("#movetarget").addEventListener("change", () => {
  const sec = findGroup($("#movetarget").value);
  if (sec) { moveSelection(sec); $("#movetarget").value = ""; }
});
function createGroup() {
  let n = 1;
  while (state.extraGroups["G" + n] || findGroup("G" + n)) n++;
  const ref = "G" + n;
  state.extraGroups[ref] = { name: "" };
  return makeExtraGroup(ref, "");
}
$("#newGroup").addEventListener("click", () => {
  const sec = createGroup();
  moveSelection(sec);
  save(); recount();
  sec.scrollIntoView(); $(".g-name", sec).focus();
});
document.addEventListener("click", e => {
  if (!e.target.classList.contains("splitout")) return;
  const ids = JSON.parse(e.target.closest("li").dataset.ids);
  const sec = createGroup();
  for (const id of ids) {
    state.moves[id] = sec.dataset.ref;
    moveDeck(id, sec);
  }
  e.target.closest("li").remove();
  save(); recount();
  sec.scrollIntoView(); $(".g-name", sec).focus();
});
$("#toNoise").addEventListener("click", () => moveSelection($("#noise")));
$("#clearSel").addEventListener("click", clearSelection);
$("#export").addEventListener("click", () => {
  openDialog("Export — paste this back to Claude",
    JSON.stringify(exportState(), null, 1), false);
});
$("#import").addEventListener("click", () => {
  openDialog("Import — paste a previous export (editor_state)", "", true);
});
$("#io-copy").addEventListener("click", () => {
  navigator.clipboard.writeText($("#io-text").value);
  $("#io-copy").textContent = "Copied ✓";
  setTimeout(() => { $("#io-copy").textContent = "Copy"; }, 1500);
});
$("#io-apply").addEventListener("click", () => {
  try {
    const data = JSON.parse($("#io-text").value);
    localStorage.setItem(KEY,
      JSON.stringify(data.editor_state || data));
    location.reload();
  } catch (err) {
    $("#io-title").textContent = "Import failed: " + err.message;
  }
});
$("#io-close").addEventListener("click", () => $("#io").close());
// ---- decklist hover (data embedded: the artifact CSP blocks fetches)
const TYPE_ORDER = ["Crypt", "Master", "Conviction", "Action", "Ally",
  "Equipment", "Political Action", "Retainer", "Event", "Action Modifier",
  "Action Modifier/Combat", "Action Modifier/Reaction", "Reaction",
  "Reaction/Action Modifier", "Combat", "Combat/Action Modifier", "Power"];
let DL = null;
const panel = $("#dlpanel");
let hoverTimer = null, hoverLi = null;

function groupBaseline(li) {
  const sec = li.closest(".cluster[data-ref]");
  if (!sec || sec.dataset.ref === "noise") return null;
  const ref = sec.dataset.ref;
  if (baselines[ref]) return baselines[ref];
  const members = $$(".decks li[data-id]", sec)
    .map(l => DL.decks[l.dataset.id]).filter(Boolean);
  if (members.length < 3) return null;
  const counts = new Map();
  for (const entries of members) {
    for (const [id, count] of entries) {
      if (!counts.has(id)) counts.set(id, []);
      counts.get(id).push(count);
    }
  }
  const presence = new Map(), median = new Map();
  for (const [id, list] of counts) {
    presence.set(id, list.length);
    list.sort((a, b) => a - b);
    median.set(id, list[Math.floor(list.length / 2)]);
  }
  return (baselines[ref] = { size: members.length, presence, median });
}

function renderDecklist(li) {
  DL = DL || JSON.parse($("#decklists").textContent);
  const entries = DL.decks[li.dataset.id];
  if (!entries) return false;
  const base = groupBaseline(li);
  const groups = new Map();
  let cryptTotal = 0, libTotal = 0;
  for (const [id, count] of entries) {
    const [name, type] = DL.names[id];
    let share = null;
    if (base) share = (base.presence.get(id) || 1) / base.size;
    if (!groups.has(type)) groups.set(type, []);
    groups.get(type).push([name, count, share, id]);
    if (type === "Crypt") cryptTotal += count; else libTotal += count;
  }
  const order = [...groups.keys()].sort((a, b) => {
    const ia = TYPE_ORDER.indexOf(a), ib = TYPE_ORDER.indexOf(b);
    return (ia < 0 ? 99 : ia) - (ib < 0 ? 99 : ib) || a.localeCompare(b);
  });
  const escHtml = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");
  const link = $("a", li);
  const name = $(".d-name", li).textContent || "(unnamed)";
  const sub = `${$(".d-date", li).textContent} · ` +
    `${$(".d-player", li).textContent} · ${link.title || ""}`;
  let out = `<div class="dl-head">${escHtml(name)}</div>` +
    `<div class="dl-sub">${escHtml(sub)}</div><div class="dl-cols">`;
  for (const type of order) {
    const cards = groups.get(type);
    const total = type === "Crypt" ? cryptTotal
      : cards.reduce((a, [, n]) => a + n, 0);
    out += `<h3>${escHtml(type)} (${total})</h3><ul>` + cards.map(
      ([n, c, share, id]) => {
        const odd = share !== null && share < 0.25;
        let hint = odd
          ? ` <span class="pct">${Math.round(share * 100)}%</span>` : "";
        let nCls = "n";
        if (base && !odd) {
          const med = base.median.get(id);
          if ((c >= 2 * med && c - med >= 3) ||
              (2 * c <= med && med - c >= 3)) {
            nCls = "n odd-n";
            hint = ` <span class="pct">med ${med}×</span>`;
          }
        }
        return `<li${odd ? ' class="odd"' : ""}>` +
          `<span class="${nCls}">${c}×</span> ${escHtml(n)}${hint}</li>`;
      }
    ).join("") + "</ul>";
  }
  out += "</div>";
  if (base) {
    const inDeck = new Set(entries.map(([id]) => id));
    const missing = [];
    for (const [id, n] of base.presence) {
      const share = n / base.size;
      if (share >= 0.7 && !inDeck.has(id)) {
        missing.push([DL.names[id][0], share]);
      }
    }
    if (missing.length) {
      missing.sort((a, b) => b[1] - a[1]);
      out += `<div class="dl-missing"><h3>Not played (group staples)</h3>` +
        missing.slice(0, 10).map(([n, s]) =>
          `<span>${escHtml(n)} <span class="pct">` +
          `${Math.round(s * 100)}%</span></span>`).join(" · ") +
        (missing.length > 10 ? ` · +${missing.length - 10} more` : "") +
        `</div>`;
    }
    out += `<div class="dl-note">blue card = played by &lt;25% of this ` +
      `group (n=${base.size}) · blue count = far from group median · ` +
      `staples = in ≥70% of the group</div>`;
  }
  panel.innerHTML = out;
  return true;
}

function placePanel(x, y) {
  panel.hidden = false;
  const rect = panel.getBoundingClientRect();
  let left = x + 18, top = y + 12;
  if (left + rect.width > innerWidth - 8) left = x - rect.width - 18;
  if (left < 8) left = 8;
  if (top + rect.height > innerHeight - 8) {
    top = innerHeight - rect.height - 8;
  }
  panel.style.left = left + "px";
  panel.style.top = Math.max(8, top) + "px";
}

document.addEventListener("mouseover", e => {
  const li = e.target.closest ? e.target.closest(".decks li[data-id]") : null;
  if (li === hoverLi) return;
  clearTimeout(hoverTimer);
  hoverLi = li;
  if (!li) { panel.hidden = true; return; }
  const x = e.clientX, y = e.clientY;
  hoverTimer = setTimeout(() => {
    if (hoverLi === li && renderDecklist(li)) placePanel(x, y);
  }, 200);
});
document.addEventListener("scroll", () => {
  panel.hidden = true; hoverLi = null; clearTimeout(hoverTimer);
}, true);

$("#filter").addEventListener("input", e => {
  const q = e.target.value.trim().toLowerCase();
  for (const sec of groupSections()) {
    const hit = !q || (sec.dataset.search || "").includes(q);
    sec.classList.toggle("hidden", !hit);
    const toc = $("#toc-" + sec.id);
    if (toc && !toc.classList.contains("done"))
      toc.classList.toggle("hidden", !hit && !!q);
  }
});
</script>'''


if __name__ == "__main__":
    main()
