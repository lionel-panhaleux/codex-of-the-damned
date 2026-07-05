"""Offline lint of the Jinja templates — no network, no rendering.

Jinja renders undefined variables as empty strings, so a `{{ var }}` used in a
`{% trans %}` block without a matching declaration in the tag header (and absent
from ``BASE_CONTEXT``) silently vanishes from the prose. Catch it here instead.
"""

import pathlib
import re

import pytest

from codex_of_the_damned import BASE_CONTEXT

TEMPLATES = pathlib.Path(__file__).parent.parent / "codex_of_the_damned" / "templates"
TEMPLATE_FILES = sorted(
    path.relative_to(TEMPLATES).as_posix() for path in TEMPLATES.rglob("*.html")
)

# variables the index() route adds to BASE_CONTEXT on every render
CONTEXT_KEYS = set(BASE_CONTEXT) | {"lang", "section"}

TRANS_RE = re.compile(
    r"\{%-?\s*trans(?P<header>.*?)-?%\}(?P<body>.*?)\{%-?\s*endtrans\s*-?%\}",
    re.DOTALL,
)
VAR_RE = re.compile(r"\{\{\s*([^\W\d]\w*)\s*\}\}")
STRING_RE = re.compile(r"\"[^\"]*\"|'[^']*'")
DECLARATION_RE = re.compile(r"^\s*(?:(?:trimmed|notrimmed)\s+)?([^\W\d]\w*)\s*=")


def declared_variables(header):
    """Names assigned in a trans tag header, e.g. ``trans trimmed foo=card("Foo")``."""
    header = STRING_RE.sub("''", header)
    declarations = [""]
    depth = 0
    for char in header:
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif char == "," and depth == 0:
            declarations.append("")
            continue
        declarations[-1] += char
    names = set()
    for declaration in declarations:
        match = DECLARATION_RE.match(declaration)
        if match:
            names.add(match.group(1))
    return names


@pytest.mark.parametrize("template", TEMPLATE_FILES)
def test_trans_variables(template):
    source = (TEMPLATES / template).read_text()
    errors = []
    for block in TRANS_RE.finditer(source):
        declared = declared_variables(block.group("header"))
        for variable in VAR_RE.finditer(block.group("body")):
            name = variable.group(1)
            if name in declared or name in CONTEXT_KEYS:
                continue
            line = source.count("\n", 0, block.start("body") + variable.start()) + 1
            errors.append(f"{template}:{line}: undeclared {{{{ {name} }}}}")
    assert not errors, "\n".join(errors)
