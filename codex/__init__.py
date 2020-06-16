import urllib.parse
import collections
import re
import unidecode

import flask
from flask_babel import Babel
from flask_babel import gettext

# Importing configuration
from codex.config import configure_app

# Importing navigation
from codex.navigation import *


app = flask.Flask(__name__, template_folder="templates")
babel = Babel(app)
configure_app(app)

# Retrieving locale and timezone information
@babel.localeselector
def get_locale():
    return flask.g.get("lang_code", app.config["BABEL_DEFAULT_LOCALE"])


@babel.timezoneselector
def get_timezone():
    user = flask.g.get("user", None)
    if user is not None:
        return user.timezone


# Managing the currently used language
@app.url_defaults
def add_language_code(endpoint, values):
    if "lang_code" in values:
        return
    if app.url_map.is_endpoint_expecting(endpoint, "lang_code"):
        values["lang_code"] = (
            getattr(flask.g, "lang_code", None) or app.config["BABEL_DEFAULT_LOCALE"]
        )


# set the language code from the request
@app.url_value_preprocessor
def get_lang_code(endpoint, values):
    if values is not None:
        flask.g.lang_code = values.pop("lang_code", app.config["BABEL_DEFAULT_LOCALE"])


# ensure_lang_support function executes before each request
# it is helpful to verify if the provided language is supported by the application
@app.before_request
def ensure_lang_support():
    lang_code = flask.g.get("lang_code", None)
    if lang_code and lang_code not in app.config["SUPPORTED_LANGUAGES"].keys():
        return flask.abort(404)


# Defining Errors
@app.errorhandler(404)
def page_not_found(error):
    return flask.render_template("404.html"), 404


# Default route
@app.route("/")
@app.route("/<path:page>")
@app.route("/<lang_code>/<path:page>")
def index(lang_code=app.config["BABEL_DEFAULT_LOCALE"], page="index.html"):
    return flask.render_template(page, language=flask.g.get("lang_code"))

def _link(page, name=None, _class=None, locale=None, _anchor=None, **params):
    if not page or not page.url:
        return ""
    name = name or page.name
    url = "/" + (locale or get_locale()) + page.url
    if params:
        url += "?" + urllib.parse.urlencode(params)
    if _anchor:
        url += "#" + _anchor
    if _class:
        _class = f"class={_class} "
    else:
        _class = ""
    return flask.Markup(f'<a {_class}href="{url}">{name}</a>')

@app.context_processor
def linker():
    path = flask.request.path[3:]
    if path[-11:] == "/index.html":
        path = path[:-11]
    if path[-5:] == ".html":
        path = path[:-5]
    if path[-1:] == "/":
        path = path[:-1]

    def link(page, name=None, _anchor=None, **params):
        return _link(HELPER[page]["self"], name=name, _anchor=_anchor, **params)

    def translation(locale, name):
        return _link(HELPER[path]["self"], name=name, locale=locale)

    def top():
        return _link(HELPER[path]["top"])

    def next():
        return _link(HELPER[path]["next"], _class="next")

    def prev():
        return _link(HELPER[path]["prev"], _class="prev")

    return dict(link=link, translation=translation, top=top, next=next, prev=prev)


def file_name(name):
    name = unidecode.unidecode(name).lower()
    if name[:4] == "the ":
        name = name[4:] + "the"
    name = re.sub(r"[^a-zA-Z0-9]", "", name)
    return name


@app.context_processor
def display_card():
    def card(name, display_name=None):
        return flask.Markup(
            """<span class="card" onclick="dC('{fname}')">{name}</span>""".format(
                name=display_name or name, fname=file_name(name)
            )
        )

    return dict(card=card)
