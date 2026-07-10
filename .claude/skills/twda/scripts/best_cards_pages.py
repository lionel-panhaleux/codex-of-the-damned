# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Assign each card to ONE best-cards page and emit the proposed, ordered
contents per page — the curation layer of a refresh.

Reads a best_cards_report.py JSON (--report) and its all-time companion
(--alltime, used for the red-flag clan pages). Single-category precedence:

    Clan > Path > Sect > Discipline > Generic(by type)

Ordering on a page: vampires first (clan pages), then library; each block by
deck frequency, highest first. Page size is trimmed to a multiple of four (the
column-4 layout): >= 4 cards, most >= 8, prolific ones 12+. Master is largest.

    uv run best_cards_pages.py --report r.json --alltime a.json -o pages.md
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re

# discipline code -> generic page slug (the 15 pages that exist)
DISC_SLUG = {
    "ani": "animalism", "aus": "auspex", "tha": "blood-sorcery", "cel": "celerity",
    "dom": "dominate", "for": "fortitude", "nec": "necromancy", "obf": "obfuscate",
    "obl": "oblivion", "pot": "potence", "pre": "presence", "pro": "protean",
}
# clan-signature disciplines with no generic page: their cards fold into the
# clan page (legacy split by V5-legality still applies for these).
UNIQUE_DISC_CLAN = {
    "val": "Salubri antitribu", "vis": "Gargoyle", "myt": "Kiasyd",
    "tem": "True Brujah", "dai": "Baali", "ser": "Ministry",
    "mel": "Daughter of Cacophony", "spi": "Ahrimane", "thn": "Samedi",
    "dem": "Malkavian", "obt": "Lasombra",
}
# legacy-only disciplines of the V5-reworked clans: the V5 version DROPPED the
# discipline, so its cards belong on the LEGACY page even when reprinted in V5.
UNIQUE_DISC_LEGACY = {
    "vic": "tzimisce-legacy", "qui": "assamite-legacy",
    "obe": "salubri-legacy", "chi": "ravnos-legacy",
}
SECT_WORDS = ("anarch", "camarilla", "sabbat", "laibon")
# cards whose NAME carries a sect word but which are NOT sect cards (generic
# masters any deck plays) — skip themed-sect detection so they fall through to
# their real category. Unlike Anarch Revolt / Anarch Railroad, which ARE Anarch.
THEME_EXCLUDE = {"Smiling Jack, The Anarch", "Anarch Troublemaker"}
# clan name in the data -> page slug (antitribu distinct; legacy shares V5 slug
# for library cards — legacy vampire pages are curated by era separately)
CLAN_SLUG = {
    "Ahrimane": "ahrimanes", "Akunanse": "akunanse", "Baali": "baali",
    "Banu Haqim": "banu-haqim", "Brujah": "brujah", "Brujah antitribu": "brujah-antitribu",
    "Caitiff": "caitiff", "Daughter of Cacophony": "daughters-of-cacophony",
    "Gangrel": "gangrel", "Gangrel antitribu": "gangrel-antitribu", "Gargoyle": "gargoyles",
    "Giovanni": "giovanni", "Guruhi": "guruhi", "Harbinger of Skulls": "harbingers-of-skulls",
    "Ishtarri": "ishtarri", "Kiasyd": "kiasyd", "Lasombra": "lasombra", "Malkavian": "malkavian",
    "Ministry": "ministry", "Nosferatu": "nosferatu", "Nosferatu antitribu": "nosferatu-antitribu",
    "Ravnos": "ravnos", "Salubri": "salubri", "Salubri antitribu": "salubri-antitribu",
    "Toreador": "toreador", "Toreador antitribu": "toreador-antitribu", "Tremere": "tremere",
    "Tremere antitribu": "tremere-antitribu", "True Brujah": "true-brujah", "Tzimisce": "tzimisce",
    "Ventrue": "ventrue", "Ventrue antitribu": "ventrue-antitribu", "Samedi": "samedi",
    "Hecata": "hecata",
}
# curation overrides for cards whose sect/clan home is not detectable from a
# requirement, name, or discipline — e.g. Garibaldi-Meucci Museum has no Anarch
# requirement but only works with Anarchs, so it belongs on the Anarch page.
MANUAL_PAGE = {
    "Garibaldi-Meucci Museum": "sects/anarch",
}
PATH_SLUG = {
    "Caine": "caine", "Death and the Soul": "death-and-the-soul",
    "Cathari": "cathari", "Power and the Inner Voice": "power-and-the-inner-voice",
}
# clans reworked in V5 with a separate legacy page: clan name -> legacy slug.
# A card/vampire lands on the V5 page if V5-format legal, else the legacy page
# (generic clan cards reprinted in V5 go V5; un-reprinted ones stay legacy).
LEGACY_SLUG = {
    "Banu Haqim": "assamite-legacy", "Ravnos": "ravnos-legacy",
    "Salubri": "salubri-legacy", "Tzimisce": "tzimisce-legacy",
}
# these clan pages compile all-time stats (rarely played in the 5y window)
RED_FLAG = {
    "ahrimanes", "akunanse", "assamite-legacy", "brujah-antitribu", "caitiff",
    "daughters-of-cacophony", "imbued", "ishtarri", "nosferatu-antitribu",
    "ravnos-legacy", "salubri-legacy", "salubri-antitribu", "samedi",
    "toreador-antitribu", "true-brujah",
}


def sect_of(text: str) -> str | None:
    """The sect a card requires, from its requirement text (incl. titles)."""
    t = text
    tl = t.lower()
    def req(word):  # "Requires a/an [ready/titled] <word>"
        return bool(re.search(rf"requires an? (?:ready |titled )?{word}", tl))
    if req("anarch") or "requires a baron" in tl or req("baron"):
        return "anarch"
    if (req("camarilla") or req("prince") or req("justicar")
            or "inner circle" in tl and "requires" in tl):
        return "camarilla"
    if (req("sabbat") or req("archbishop") or req("cardinal") or req("priscus")
            or req("bishop") or req("templar")):
        return "sabbat"
    if req("laibon") or req("magaji") or req("kholo"):
        return "laibon"
    return None


def clan_page(clan: str, v5: bool) -> str | None:
    """The clan's page slug, routing to the legacy page when not V5-legal."""
    if clan in LEGACY_SLUG and not v5:
        return f"clans/{LEGACY_SLUG[clan]}"
    return f"clans/{CLAN_SLUG[clan]}" if clan in CLAN_SLUG else None


def ability_text(s: dict) -> str:
    """The vampire's special-ability text, minus the sect/flavour label."""
    return re.sub(
        r"^(anarch|camarilla|sabbat|independent|laibon)[.:]?\s*",
        "", (s.get("text") or "").strip(), flags=re.I,
    ).strip()


def is_star_vampire(s: dict) -> bool:
    """Show stars, not crypt-fillers: high capacity (power) or ANY real special
    ability. A filler is a mid/low-cap vampire with a blank ability box (just a
    sect label), frequent only because it rounds out crypts — those are dropped;
    the frequency bar then trims low-play ability vampires."""
    cap = s.get("capacity") or 0
    return cap >= 7 or bool(ability_text(s))


def themed_sect(name: str) -> str | None:
    """A sect a card is themed to (its name carries the sect word), for cards
    with no hard requirement — e.g. Anarch Revolt, Anarch Railroad."""
    if name in THEME_EXCLUDE:
        return None
    nl = name.lower()
    for word in SECT_WORDS:
        if re.search(rf"\b{word}\b", nl):
            return word
    return None


def page_of(s: dict) -> str | None:
    """The single page a card belongs to, by precedence (Path > Clan)."""
    if s["name"] in MANUAL_PAGE:                     # curation override
        return MANUAL_PAGE[s["name"]]
    if s["hunting_ground"]:                          # omitted from every list
        return None
    if s["vampire"]:
        if not is_star_vampire(s):
            return None
        if s.get("vpath") in PATH_SLUG:              # Path > Clan for vampires too
            return f"paths/{PATH_SLUG[s['vpath']]}"
        return clan_page(s.get("clan", ""), s.get("v5", False))
    for path in s["paths"]:                          # Path (before Clan)
        if path in PATH_SLUG:
            return f"paths/{PATH_SLUG[path]}"
    for clan in s["clans"]:                          # Clan (requirement)
        page = clan_page(clan, s.get("v5", False))
        if page:
            return page
    sect = sect_of(s.get("text", ""))                # Sect (requirement)
    if sect:
        return f"sects/{sect}"
    for disc in s["disciplines"]:                    # Discipline
        if disc in DISC_SLUG:
            return f"generic/{DISC_SLUG[disc]}"
        if disc in UNIQUE_DISC_LEGACY:               # legacy-only clan discipline
            return f"clans/{UNIQUE_DISC_LEGACY[disc]}"
        if disc in UNIQUE_DISC_CLAN:                 # clan-signature discipline
            page = clan_page(UNIQUE_DISC_CLAN[disc], s.get("v5", False))
            if page:
                return page
    theme = themed_sect(s["name"])                   # Sect (theme, weak)
    if theme:
        return f"sects/{theme}"
    if "Master" in s["types"]:                       # Generic
        return "generic/master-cards"
    if "Political Action" in s["types"]:
        return "generic/political-actions"
    if not s["disciplines"]:
        return "generic/no-discipline"
    return None


def round4(n: int) -> int:
    """Nearest multiple of four (ties round up)."""
    return int(n / 4 + 0.5) * 4


def qualify(rows: list, frac: float) -> tuple[list, list]:
    """(cards within `frac` of the block's top by raw decks OR recency share,
    ordered by frequency; the whole block ordered by frequency)."""
    by_decks = sorted(rows, key=lambda r: -r["decks"])
    if not by_decks:
        return [], []
    top_d = by_decks[0]["decks"] or 1
    top_r = max((r["share_recent"] for r in rows), default=0.0) or 1e-9
    qual = [
        r for r in by_decks
        if r["decks"] >= frac * top_d or r["share_recent"] >= frac * top_r
    ]
    return qual, by_decks


def sized(rows: list, frac: float, cap: int, min_n: int) -> list:
    """A single-block page (disciplines, sects): frequency order, nearest
    multiple of four, >= min_n, capped, padded from the next-most-played."""
    qual, by_decks = qualify(rows, frac)
    n = min(max(min_n, round4(len(qual))), cap, len(by_decks))
    chosen = qual[:n]
    chosen += [r for r in by_decks if r not in qual][: n - len(chosen)]
    return sorted(chosen, key=lambda r: -r["decks"])


def sized_both(vamps: list, libs: list, frac: float, cap_each: int = 12) -> list:
    """A page with both vampires and library (clans, paths): each block >= 4 and
    frequency-ordered; the COMBINED total is rounded to a multiple of four by
    nudging the library block (keeping >= 4 there when it can)."""
    def block(rows):
        qual, by_decks = qualify(rows, frac)
        chosen = qual[:cap_each]
        chosen += [r for r in by_decks if r not in qual][: max(0, 4 - len(chosen))]
        return sorted(chosen, key=lambda r: -r["decks"]), by_decks

    v, _ = block(vamps)
    lib, lib_all = block(libs)
    rem = (len(v) + len(lib)) % 4
    if rem >= 2:                                   # round up: add library cards
        lib += [r for r in lib_all if r not in lib][: 4 - rem]
    elif rem == 1:                                 # round down: drop a weak library card
        lib = lib[: len(lib) - min(1, max(0, len(lib) - 4))]
    return v + sorted(lib, key=lambda r: -r["decks"])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", required=True)
    ap.add_argument("--alltime", default="")
    ap.add_argument("--frac", type=float, default=0.30,
                    help="cutoff for clans/sects/paths; disciplines use 0.20, "
                         "pure generic (master/no-discipline/political) 0.15")
    ap.add_argument("-o", "--output", default="")
    args = ap.parse_args()

    disc_pages = {f"generic/{s}" for s in DISC_SLUG.values()}
    pure_generic = {"generic/master-cards", "generic/no-discipline", "generic/political-actions"}

    def frac_for(slug: str) -> float:
        if slug in pure_generic:
            return 0.15
        if slug in disc_pages:
            return 0.20
        return args.frac

    window = json.loads(pathlib.Path(args.report).read_text())["all"]
    alltime = json.loads(pathlib.Path(args.alltime).read_text())["all"] if args.alltime else {}

    def buckets(stats: dict) -> dict[str, list]:
        out: dict[str, list] = {}
        for s in stats.values():
            slug = page_of(s)
            if slug:
                out.setdefault(slug, []).append(s)
        return out

    win, allt = buckets(window), buckets(alltime) if alltime else {}

    lines = ["# Proposed best-cards page contents — 2026-07\n",
             "One card per page (Path > Clan > Sect > Discipline > Generic; themed",
             "cards and clan-signature disciplines fold into their sect/clan). Clan",
             "pages: stars only (cap ≥7 or a real ability), vampires then library,",
             "each block sized against its OWN top card. `r`=recency-fair share;",
             "NEW=first printed in the last ~2 years.\n",
             "**· all-time** in a heading = a red-flagged page (clan too rarely",
             "played for 5-year stats): it compiles the full 30-year archive and",
             "MUST carry the red 'insufficient recent data' warning when built.\n"]

    for slug in sorted(set(win) | set(allt) | {f"clans/{v}" for v in CLAN_SLUG.values()}
                       | {f"clans/{v}" for v in LEGACY_SLUG.values()},
                       key=lambda x: (x.split("/")[0], x)):
        red = slug.split("/", 1)[1] in RED_FLAG
        rows = (allt if (red and allt) else win).get(slug, [])
        if not rows:
            continue
        vamps = [r for r in rows if r["vampire"]]
        libs = [r for r in rows if not r["vampire"]]
        frac = frac_for(slug)
        if slug.startswith(("clans/", "paths/")):   # vampires + library
            ordered = sized_both(vamps, libs, frac)
        else:                                        # deep discipline / sect / master pages
            cap = 40 if slug == "generic/master-cards" else 24
            ordered = sized(libs, frac, cap, min_n=8)
        lines.append(f"## {slug}  ({len(ordered)} cards{' · all-time' if red and allt else ''})")
        for r in ordered:
            kind = f"cap{r['capacity']} vampire" if r["vampire"] else "/".join(r["types"])[:12]
            tag = " · NEW" if r["recent"] else ""
            lines.append(f"- {r['name']} — {r['decks']}d, {r['share_recent']:.0%}r [{kind}]{tag}")
        lines.append("")

    text = "\n".join(lines)
    if args.output:
        pathlib.Path(args.output).write_text(text)
        print(f"wrote {args.output}")
    else:
        print(text[:3000])


if __name__ == "__main__":
    main()
