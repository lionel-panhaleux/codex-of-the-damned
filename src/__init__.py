import urllib.parse
import re
import unidecode

import flask
import flask_babel
import jinja2.exceptions

from . import config
from . import navigation


app = flask.Flask(__name__, template_folder="templates")
app.jinja_env.policies["ext.i18n.trimmed"] = True
babel = flask_babel.Babel(app)
config.configure_app(app)


def main():
    app.run()


# Retrieving locale and timezone information
@babel.localeselector
def get_locale():
    return flask.g.get("lang_code", app.config["BABEL_DEFAULT_LOCALE"])


@babel.timezoneselector
def get_timezone():
    user = flask.g.get("user", None)
    if user is not None:
        return user.timezone


# Defining Errors
@app.errorhandler(jinja2.exceptions.TemplateNotFound)
@app.errorhandler(404)
def page_not_found(error):
    return flask.render_template("404.html"), 404


# favicon redirection - need when serving card images directly
@app.route("/favicon.ico")
def favicon():
    return flask.redirect(flask.url_for("static", filename="img/favicon.ico"))


# retrocompatibility for card images
@app.route("/card-images/<path:image>")
def card_image(image):
    return flask.redirect(flask.url_for("static", filename=f"img/card-images/{image}"))


# Default route
@app.route("/")
@app.route("/<path:page>")
@app.route("/<lang_code>/<path:page>")
def index(lang_code=app.config["BABEL_DEFAULT_LOCALE"], page="index.html"):
    if lang_code not in app.config["SUPPORTED_LANGUAGES"].keys():
        page = lang_code + "/" + page
        lang_code = app.config["BABEL_DEFAULT_LOCALE"]
    flask.g.lang_code = lang_code
    context = {"language": flask.g.get("lang_code")}

    # use card image as og_image for card-search
    if page[:11] == "card-search":
        card = flask.request.args.get("card")
        if card:
            image_name = unidecode.unidecode(card).lower()
            image_name = (
                image_name[4:] + "the" if image_name[:4] == "the " else image_name
            )
            image_name, _ = re.subn(r"""\s|,|\.|-|—|'|:|\(|\)|"|!""", "", image_name)
            context["og_image"] = flask.url_for(
                "static", filename=f"img/card-images/{image_name}.jpg"
            )

    return flask.render_template(page, **context)


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
    path = flask.request.path
    if path[1:3] in app.config["SUPPORTED_LANGUAGES"].keys():
        path = path[3:]
    if path[-11:] == "/index.html":
        path = path[:-11]
    if path[-5:] == ".html":
        path = path[:-5]
    if path[-1:] == "/":
        path = path[:-1]

    def link(page, name=None, _anchor=None, **params):
        return _link(
            navigation.HELPER.get(page, {}).get("self"),
            name=name,
            _anchor=_anchor,
            **params,
        )

    def translation(locale, name):
        return _link(
            navigation.HELPER.get(path, {}).get("self"), name=name, locale=locale
        )

    def top():
        return _link(navigation.HELPER.get(path, {}).get("top"))

    def next():
        return _link(navigation.HELPER.get(path, {}).get("next"), _class="next")

    def prev():
        return _link(navigation.HELPER.get(path, {}).get("prev"), _class="prev")

    def external(url, name):
        return flask.Markup(f'<a target="_blank" href="{url}">{name}</a>')

    return dict(
        link=link,
        translation=translation,
        top=top,
        next=next,
        prev=prev,
        external=external,
    )


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
