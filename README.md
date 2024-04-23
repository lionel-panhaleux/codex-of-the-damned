# Codex of the Damned

[![PyPI version](https://badge.fury.io/py/codex-of-the-damned.svg)](https://badge.fury.io/py/codex-of-the-damned)
[![Validation](https://github.com/lionel-panhaleux/codex-of-the-damned/actions/workflows/validation.yaml/badge.svg)](https://github.com/lionel-panhaleux/codex-of-the-damned/actions)
[![Python version](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/downloads/)
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

### Translating

Install a PO editor like [POEdit](https://poedit.net), call the following command
to generate the messages in the language you're interested in:

```bash
BABEL_LANG=es make po-update
```

Then open the generated catalog file,
`codex_of_the_damned/translations/es/LC_MESSAGES/messages.po`, in your PO editor.


While translating, beware to keep the `HTML` tags like `<p>`, `<em>` as they are,
and make sure you keep the exact same format parameters in the translated text.
They include anything dynamic, from disciplines like `%(cel)s` and clans like
`%(brujah)s`, to cards like `%(alastor)s` and external urls like `%(johns_deck)`.


Once you're done translating, generate the translation files with:

```bash
make po
```

To make a new language accessible in the website, you simply have to add the matching
line in the translation `nav` header of the global layout
`codex_of_the_damned/templates/layout.html`:

```html
<nav role="translation">
    {{ translation('en', "🇬🇧") }}
    {{ translation('fr', "🇫🇷") }}
</nav>
```

### Run a dev server

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

### Production deployment

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

Use [POEdit](https://poedit.net) and [Google Translate](https://translate.google.com) to help with translations.

Run `make po` to build the translation files under `codex-of-the-damned/translations`,
edit them with [POEdit](https://poedit.net), then run `make po` when you're done to streamline them.
