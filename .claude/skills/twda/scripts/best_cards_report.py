# /// script
# requires-python = ">=3.11"
# dependencies = ["krcg"]
# ///
"""Per-category best-cards report over a TWDA date window, with recency
correction and curation flags — the input for a best-cards page refresh.

For every best-cards page (disciplines, sects, paths, clans, and the generic
master/political/no-discipline pages) it emits a ranked candidate list with:
  - decks / copies range over the window (what the page shows)
  - share over the full window AND a recency-fair share: a card released after
    the window opened only had a slice of the window to appear in, so its fair
    denominator is the decks dated on/after max(set release, window start)
  - flags: recent (released in the window), hunting_ground, vampire capacity

Usage:
  uv run best_cards_report.py --since 2021-07-01 -o report.json
"""

from __future__ import annotations

import argparse
import bisect
import collections
import datetime
import json
import pathlib

import twda

# generic discipline pages: page slug -> discipline code
DISCIPLINES = {
    "animalism": "ani",
    "auspex": "aus",
    "blood-sorcery": "tha",
    "celerity": "cel",
    "dominate": "dom",
    "fortitude": "for",
    "necromancy": "nec",
    "obfuscate": "obf",
    "oblivion": "obl",
    "potence": "pot",
    "presence": "pre",
    "protean": "pro",
}
# the four V5 paths: page slug -> path_requirement value
PATHS = {
    "caine": "Caine",
    "death-and-the-soul": "Death and the Soul",
    "cathari": "Cathari",
    "power-and-the-inner-voice": "Power and the Inner Voice",
}
# sect pages keyed by the word that flags the card (loose text net — sect pages
# are themed, not strictly requirement-gated, so this is a candidate net only)
SECTS = {
    "anarch": "Anarch",
    "camarilla": "Camarilla",
    "laibon": "Laibon",
    "sabbat": "Sabbat",
}
# clan pages: page slug -> clan name in the data (legacy/V5 share a name; the
# vampire selection is curated by era, this is only a candidate aid)
CLANS = {
    "ahrimanes": "Ahrimane",
    "akunanse": "Akunanse",
    "assamite-legacy": "Banu Haqim",
    "baali": "Baali",
    "banu-haqim": "Banu Haqim",
    "brujah": "Brujah",
    "brujah-antitribu": "Brujah antitribu",
    "caitiff": "Caitiff",
    "daughters-of-cacophony": "Daughter of Cacophony",
    "gangrel": "Gangrel",
    "gangrel-antitribu": "Gangrel antitribu",
    "gargoyles": "Gargoyle",
    "giovanni": "Giovanni",
    "guruhi": "Guruhi",
    "harbingers-of-skulls": "Harbinger of Skulls",
    "ishtarri": "Ishtarri",
    "kiasyd": "Kiasyd",
    "lasombra": "Lasombra",
    "malkavian": "Malkavian",
    "ministry": "Ministry",
    "nosferatu": "Nosferatu",
    "nosferatu-antitribu": "Nosferatu antitribu",
    "ravnos": "Ravnos",
    "ravnos-legacy": "Ravnos",
    "salubri": "Salubri",
    "salubri-legacy": "Salubri",
    "salubri-antitribu": "Salubri antitribu",
    "toreador": "Toreador",
    "toreador-antitribu": "Toreador antitribu",
    "tremere": "Tremere",
    "tremere-antitribu": "Tremere antitribu",
    "true-brujah": "True Brujah",
    "tzimisce": "Tzimisce",
    "tzimisce-legacy": "Tzimisce",
    "ventrue": "Ventrue",
    "ventrue-antitribu": "Ventrue antitribu",
}


def pctile(values: list[int], q: float) -> int:
    """Nearest-rank percentile of a small integer sample."""
    s = sorted(values)
    idx = min(len(s) - 1, max(0, round(q * (len(s) - 1))))
    return s[idx]


def years_ago(years: int) -> str:
    today = datetime.datetime.now(tz=datetime.UTC).date()
    try:
        return today.replace(year=today.year - years).isoformat()
    except ValueError:
        return today.replace(year=today.year - years, day=28).isoformat()


def release_data(cards) -> tuple[dict[str, str], set[str]]:
    """(merge_key -> earliest ISO legal date, set of V5-format-legal merge_keys).

    Uses krcg's native v5 Card.legal and Card.formats fields directly.
    """
    earliest_of: dict[str, str] = {}
    v5: set[str] = set()
    for c in cards.values():
        keys = {c.unique_name, c.printed_name}
        if c.kind == twda.models.Card.Kind.CRYPT:
            suffix = " (ADV)" if getattr(c, "advanced", False) else ""
            keys.add(c.printed_name + suffix)
        legal = c.legal.isoformat() if getattr(c, "legal", None) else ""
        is_v5 = any(str(f) == "V5" for f in (getattr(c, "formats", None) or []))
        for key in keys:
            if not key:
                continue
            if legal:
                earliest_of[key] = min(earliest_of.get(key, "9999"), legal)
            if is_v5:
                v5.add(key)
    return earliest_of, v5


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--since", default=years_ago(5), help="ISO date, inclusive (default: 5y ago)"
    )
    parser.add_argument("--until", default="")
    parser.add_argument(
        "--recent-since",
        default=years_ago(2),
        help="ISO date cutoff for NEW tag (default: 2y ago)",
    )
    parser.add_argument("--top", type=int, default=30)
    parser.add_argument("--refresh", action="store_true", help="force re-download")
    parser.add_argument("-o", "--output", default="")
    args = parser.parse_args()

    decks = twda.load_decks(args.since, args.until, args.refresh)
    dates = sorted(twda.deck_date(d) for d in decks)
    total = len(decks)
    cards = twda.load_cards()
    releases, v5_legal = release_data(cards)

    # window stats per card (merge_key feature name)
    deck_count: collections.Counter[str] = collections.Counter()
    per_deck_copies: dict[str, list[int]] = collections.defaultdict(list)
    for deck in decks:
        feats: dict[str, int] = {}
        for c in deck.cards:
            feats[twda.merge_key(c)] = feats.get(twda.merge_key(c), 0) + c.count
        for name, n in feats.items():
            deck_count[name] += 1
            per_deck_copies[name].append(n)

    def decks_since(iso: str) -> int:
        # number of window decks dated on/after iso (dates is sorted)
        return total - bisect.bisect_left(dates, iso)

    def card_obj(name: str):
        base = name.removesuffix(" (ADV)")
        try:
            return cards[base]
        except KeyError:
            return None

    def stat(name: str) -> dict | None:
        c = card_obj(name)
        if not c:
            return None
        copies = per_deck_copies[name]
        rel = (
            releases.get(name)
            or releases.get(name.replace(" (ADV)", ""))
            or "1994-01-01"
        )
        window_start = max(rel, args.since)
        denom = max(decks_since(window_start), 1)
        types = [str(t) for t in c.types]
        is_vamp = "Vampire" in types
        disc_req = getattr(c, "discipline_requirement", None)
        disciplines = (
            list(disc_req.disciplines) if disc_req and disc_req.disciplines else []
        )
        clan_req = list(getattr(c, "clan_requirement", None) or [])
        vamp_clan = (
            str(getattr(c, "clan", "")) if is_vamp and getattr(c, "clan", None) else ""
        )
        vamp_disc = (
            [str(d) for d in getattr(c, "disciplines", []) or []] if is_vamp else []
        )
        vamp_path = (
            str(getattr(c, "path", "")) if is_vamp and getattr(c, "path", None) else ""
        )
        base_name = name.replace(" (ADV)", "")
        is_v5 = name in v5_legal or base_name in v5_legal
        path_req = getattr(c, "path_requirement", None) or []
        path_req = [
            str(p) for p in (path_req if isinstance(path_req, list) else [path_req])
        ]
        # typical copies range: 10th-90th percentile trims the outliers the
        # curated pages leave out (a lone 1-of or a 15-of extreme)
        lo, hi = pctile(copies, 0.10), pctile(copies, 0.90)
        return {
            "name": name,
            "decks": deck_count[name],
            "share": round(deck_count[name] / total, 4),
            "share_recent": round(deck_count[name] / denom, 4),
            "copies_min": min(copies),
            "copies_max": max(copies),
            "copies": f"{lo}" if lo == hi else f"{lo}-{hi}",
            "release": rel,
            "recent": rel >= args.recent_since,
            "recent_denom": denom,
            "types": types,
            "disciplines": disciplines,
            "clans": clan_req,
            "clan": vamp_clan,
            "vdisc": vamp_disc,
            "vpath": vamp_path,
            "paths": path_req,
            "vampire": is_vamp,
            "capacity": getattr(c, "capacity", None) if is_vamp else None,
            "v5": is_v5,
            "hunting_ground": "Hunting Ground" in name,
            "text": (c.text or "").replace("\n", " ")[:140],
        }

    stats = {name: s for name in deck_count if (s := stat(name))}

    def ranked(pred, top=args.top, by="share_recent"):
        rows = [s for s in stats.values() if pred(s)]
        rows.sort(key=lambda s: -s[by])
        return rows[:top]

    report: dict[str, object] = {
        "window": {"since": args.since, "until": args.until or "now", "decks": total},
    }
    pages: dict[str, list] = {}
    # discipline pages
    for slug, code in DISCIPLINES.items():
        pages[f"generic/{slug}"] = ranked(
            lambda s, code=code: code in s["disciplines"]
            and not s["vampire"]
            and not s["hunting_ground"]
        )
    # generic specials
    pages["generic/master-cards"] = ranked(
        lambda s: "Master" in s["types"]
        and not s["clans"]
        and not s["paths"]
        and not s["hunting_ground"]
    )
    pages["generic/political-actions"] = ranked(
        lambda s: "Political Action" in s["types"]
    )
    pages["generic/no-discipline"] = ranked(
        lambda s: not s["vampire"]
        and not s["disciplines"]
        and not s["clans"]
        and not s["paths"]
        and "Master" not in s["types"]
        and "Political Action" not in s["types"]
        and not s["hunting_ground"]
    )
    # path pages (library cards requiring the path + the path's vampires, skipping low caps)
    for slug, path in PATHS.items():
        libs = ranked(lambda s, p=path: p in s["paths"] and not s["vampire"], top=40)
        pages[f"paths/{slug}"] = libs
    # sect pages: loose text net (candidate suggestions only)
    for slug, word in SECTS.items():
        pages[f"sects/{slug}"] = ranked(
            lambda s, w=word: (
                f"Requires a {w}" in s["text"]
                or f"Requires an {w}" in s["text"]
                or f"ready {w}" in s["text"]
                or w in s["text"][:40]
            )
            and not s["vampire"]
            and not s["hunting_ground"]
        )
    # clan pages: clan-required library cards, then the clan's vampires (writers
    # curate era/legacy and drop low-cap filler). Two lists per clan.
    for slug, clan in CLANS.items():
        lib = ranked(
            lambda s, c=clan: c in s["clans"]
            and not s["vampire"]
            and not s["hunting_ground"],
            top=40,
        )
        crypt = ranked(lambda s, c=clan: s["clan"] == c, top=25)
        pages[f"clans/{slug}"] = {"library": lib, "crypt": crypt}
    report["pages"] = pages
    report["all"] = stats

    text = json.dumps(report, ensure_ascii=False, indent=1)
    if args.output:
        pathlib.Path(args.output).write_text(text)
        print(
            f"{total} decks in window; wrote {args.output} ({len(stats)} cards, {len(pages)} pages)"
        )
    else:
        print(text[:4000])


if __name__ == "__main__":
    main()
