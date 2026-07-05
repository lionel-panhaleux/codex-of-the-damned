"""Offline lint of the navigation tree — no network."""

import collections

from codex_of_the_damned import navigation


def test_no_duplicate_paths():
    """Templates link archetypes by their subsection-less shortcut
    (e.g. /archetypes/malk-22, so links survive moves between subsections).
    Building HELPER with dict() silently keeps the last entry on collision,
    so page names must be unique across subsections.
    """
    counts = collections.Counter(path for path, _ in navigation.STRUCTURE.walk())
    duplicates = sorted(path for path, count in counts.items() if count > 1)
    assert not duplicates, f"duplicate navigation paths: {duplicates}"
