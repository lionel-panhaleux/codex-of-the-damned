# Codex of the Damned

[![PyPI version](https://badge.fury.io/py/codex-of-the-damned.svg)](https://badge.fury.io/py/codex-of-the-damned)
[![Validation](https://github.com/lionel-panhaleux/codex-of-the-damned/workflows/Validation/badge.svg)](https://github.com/lionel-panhaleux/codex-of-the-damned/actions)
[![Python version](https://img.shields.io/badge/python-3.8-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-blue)](https://opensource.org/licenses/MIT)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

This site is a compilation of Vampire: the Eternal Struggle strategy resources.
The site is publicly available at [codex-of-the-damned.org](http://www.codex-of-the-damned.org).

Portions of the materials are the copyrights and trademarks of Paradox Interactive AB,
and are used with permission. All rights reserved.
For more information please visit [www.worldofdarkness.com](http://www.worldofdarkness.com.).

![Dark Pack](codex_of_the_damned/static/img/dark-pack.png)

## Contributing

Contributions are welcome. Pull Requests will be merged if they respect the general style.
Issues will be dealt with as quickly as possible.

This site uses [Flask](https://flask.palletsprojects.com) and [Babel](http://babel.pocoo.org)
to generate pages dynamically and handle internationalisation.

## Installation

To install a working developpment version of the site, use `pip`:

```bash
python3 -m venv venv
pip install -e ".[dev]"
```

There is a make command to update translations:

```bash
make po
```

You can run the development version of the site using the `codex` entrypoint:

```bash
$ codex
 * Serving Flask app "codex_of_the_damned" (lazy loading)
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

You can set the `DEBUG` environment variable to activate the debug mode:

```bash
DEBUG=1 codex
```

To run the production server, you'll need a web server like
[uWSGI](https://uwsgi-docs.readthedocs.io):

```bash
uwsgi --module codex_of_the_damned:app
```

or [Gunicorn](https://gunicorn.org):

```bash
gunicorn codex_of_the_damned:app
```

## Useful tools

### Icons

Convert icons from raster to SVG using `imagemagick` and `potrace`,
depending on the icon, smoothing may be better or not:

```bash
convert -morphology Smooth Octagon:2 clan-ahrimanes.gif clan-ahrimanes.svg
```

### Google Translate

Use python and Google Translate to help with translation:

```python
import clipboard
import pprint
import re

def pre():
    s = "".join(s[1:-1] for s in clipboard.paste().split("\n"))
    s = re.sub(r"%\(([^\)]*)\)s", r"§K3PX\1§", s)
    clipboard.copy(s)

def post():
    s = clipboard.paste()
    s = pprint.pformat(re.sub(r"§K3PX([^§]*)§", r"%(\1)s", s), width=120)
    s = re.sub(
            r"(^')|('$)",
            '"',
            re.sub(r"^\s*", "", s[1:-1], flags=re.MULTILINE),
            flags=re.MULTILINE
        ).replace("\\n", "")
    clipboard.copy(s)

# usage:
#  > copy paragraph to translate from the PO file
# pre()
# > copy translation
# post()
# > copy result to the PO file
```
