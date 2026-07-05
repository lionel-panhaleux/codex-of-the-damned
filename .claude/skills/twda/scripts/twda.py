"""Shared TWDA data layer, built on the krcg library.

The TWDA is fetched daily-fresh from KRCG static (v5 typed JSON) and decoded
into `krcg.models.Deck` objects; the package's bundled snapshot is the offline
fallback. Also loads the "anchors": the archetype decklist JSONs checked into
this repo (templates/archetypes/*/*.json), each carrying the TWDA id of its
example deck.
"""

from __future__ import annotations

import json
import pathlib
import time
import urllib.request

import msgspec.json
from krcg import loader
from krcg import models
from krcg import twda as krcg_twda

TWDA_URL = "https://static.krcg.org/data/v5/twda.json"
CACHE = pathlib.Path.home() / ".cache" / "codex-twda"
CACHE_TTL = 86400  # upstream rebuilds daily
# scripts/ -> twda/ -> skills/ -> .claude/ -> repo root
REPO = pathlib.Path(__file__).resolve().parents[4]
ARCHETYPES = REPO / "codex_of_the_damned" / "templates" / "archetypes"


def load_archive(refresh: bool = False) -> dict[str, models.Deck]:
    """The full TWDA keyed by deck id, daily-cached from KRCG static."""
    CACHE.mkdir(parents=True, exist_ok=True)
    path = CACHE / "twda-v5.json"
    stale = not path.exists() or time.time() - path.stat().st_mtime > CACHE_TTL
    if refresh or stale:
        try:
            urllib.request.urlretrieve(TWDA_URL, path)
        except OSError:
            pass  # offline: keep a stale file if we have one
    if path.exists():
        try:
            return msgspec.json.decode(
                path.read_bytes(), type=krcg_twda.DecksArchive
            )
        except msgspec.ValidationError:
            pass  # static data ahead of the installed krcg: use its snapshot
    return krcg_twda.load()


def load_cards():
    """The full card library (CardDict, indexable by id or name).

    Built from krcg's bundled VEKN CSVs, pickle-cached per version — offline
    and fast after the first call."""
    return loader.load()


def deck_date(deck: models.Deck) -> str:
    """Event date as an ISO string (every TWDA deck has one)."""
    return deck.event.date.isoformat() if deck.event and deck.event.date else ""


def load_decks(
    since: str = "", until: str = "", refresh: bool = False
) -> list[models.Deck]:
    """TWD decks, filtered by ISO date strings (since inclusive, until exclusive)."""
    decks = list(load_archive(refresh).values())
    if since:
        decks = [d for d in decks if deck_date(d) >= since]
    if until:
        decks = [d for d in decks if deck_date(d) < until]
    return decks


def merge_key(card: models.CardInDeck, merge_groups: bool = True) -> str:
    """Feature name for a deck entry.

    With merge_groups, crypt group variants collapse ("Theo Bell (G6)" ->
    "Theo Bell"): re-grouped prints of a star vampire define the same
    archetype. (ADV) stays distinct — advanced vampires play differently."""
    if merge_groups and card.kind == models.Card.Kind.CRYPT:
        advanced = " (ADV)" if "ADV" in card.suffix else ""
        return card.printed_name + advanced
    return card.unique_name


def crypt_features(deck: models.Deck, merge_groups: bool = True) -> dict[str, int]:
    """Crypt as {name: count}."""
    out: dict[str, int] = {}
    for card in deck.cards:
        if card.kind == models.Card.Kind.CRYPT:
            name = merge_key(card, merge_groups)
            out[name] = out.get(name, 0) + card.count
    return out


def library_features(deck: models.Deck) -> dict[str, int]:
    """Library as {name: count}."""
    out: dict[str, int] = {}
    for card in deck.cards:
        if card.kind == models.Card.Kind.LIBRARY:
            out[card.unique_name] = out.get(card.unique_name, 0) + card.count
    return out


def type_features(deck: models.Deck) -> dict[str, int]:
    """Library card-type totals as {type: copies} (e.g. how ally-heavy a deck
    is). Functionally similar cards (Freakish Conglomeration / Gravebound
    Drone…) split card-level features; type totals recover the shared angle."""
    out: dict[str, int] = {}
    for card in deck.cards:
        if card.kind == models.Card.Kind.LIBRARY:
            for card_type in card.types:
                out[str(card_type)] = out.get(str(card_type), 0) + card.count
    return out


def load_anchors() -> dict[str, dict]:
    """TWDA id -> {archetype, section} from the repo's archetype pages.

    `archetype` is the page slug (unique site-wide), `section` is one of
    top-tier / runner-ups / new-kids / archive. A handful of old archive
    decklists predate the TWDA and carry no id — they are skipped.
    """
    out: dict[str, dict] = {}
    for path in sorted(ARCHETYPES.glob("*/*.json")):
        deck_id = json.loads(path.read_text()).get("id")
        if deck_id:
            out[str(deck_id)] = {
                "archetype": path.stem,
                "section": path.parent.name,
            }
    return out
