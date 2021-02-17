import copy
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

BASE_CONTEXT = {
    "CONVICTION": flask.Markup("<i>¤</i>"),
    "CONVICTION_1": flask.Markup("<i>¤</i>"),
    "CONVICTION_2": flask.Markup("<i>¤¤</i>"),
    "CONVICTION_3": flask.Markup("<i>¤¤¤</i>"),
    "CONVICTION_4": flask.Markup("<i>¤¤¤¤</i>"),
    "CONVICTION_5": flask.Markup("<i>¤¤¤¤¤</i>"),
    "ACTION": flask.Markup("<i>0</i>"),
    "ACTION_MODIFIER": flask.Markup("<i>1</i>"),
    "REACTION": flask.Markup("<i>7</i>"),
    "COMBAT": flask.Markup("<i>4</i>"),
    "REFLEX": flask.Markup("<i>6</i>"),
    "FLIGHT": flask.Markup("<i>^</i>"),
    "MERGED": flask.Markup("<i>µ</i>"),
    "abo": flask.Markup("<i>w</i>"),
    "ABO": flask.Markup("<i>W</i>"),
    "ani": flask.Markup("<i>i</i>"),
    "ANI": flask.Markup("<i>I</i>"),
    "aus": flask.Markup("<i>a</i>"),
    "AUS": flask.Markup("<i>A</i>"),
    "cel": flask.Markup("<i>c</i>"),
    "CEL": flask.Markup("<i>C</i>"),
    "chi": flask.Markup("<i>k</i>"),
    "CHI": flask.Markup("<i>K</i>"),
    "dai": flask.Markup("<i>y</i>"),
    "DAI": flask.Markup("<i>Y</i>"),
    "dem": flask.Markup("<i>e</i>"),
    "DEM": flask.Markup("<i>E</i>"),
    "dom": flask.Markup("<i>d</i>"),
    "DOM": flask.Markup("<i>D</i>"),
    "for": flask.Markup("<i>f</i>"),
    "FOR": flask.Markup("<i>F</i>"),
    "mal": flask.Markup("<i>â</i>"),
    "MAL": flask.Markup("<i>ã</i>"),
    "mel": flask.Markup("<i>m</i>"),
    "MEL": flask.Markup("<i>M</i>"),
    "myt": flask.Markup("<i>x</i>"),
    "MYT": flask.Markup("<i>X</i>"),
    "nec": flask.Markup("<i>n</i>"),
    "NEC": flask.Markup("<i>N</i>"),
    "obe": flask.Markup("<i>b</i>"),
    "OBE": flask.Markup("<i>B</i>"),
    "obf": flask.Markup("<i>o</i>"),
    "OBF": flask.Markup("<i>O</i>"),
    "obt": flask.Markup("<i>$</i>"),
    "OBT": flask.Markup("<i>£</i>"),
    "pot": flask.Markup("<i>p</i>"),
    "POT": flask.Markup("<i>P</i>"),
    "pre": flask.Markup("<i>r</i>"),
    "PRE": flask.Markup("<i>R</i>"),
    "pro": flask.Markup("<i>j</i>"),
    "PRO": flask.Markup("<i>J</i>"),
    "qui": flask.Markup("<i>q</i>"),
    "QUI": flask.Markup("<i>Q</i>"),
    "san": flask.Markup("<i>g</i>"),
    "SAN": flask.Markup("<i>G</i>"),
    "ser": flask.Markup("<i>s</i>"),
    "SER": flask.Markup("<i>S</i>"),
    "spi": flask.Markup("<i>z</i>"),
    "SPI": flask.Markup("<i>Z</i>"),
    "str": flask.Markup("<i>à</i>"),
    "STR": flask.Markup("<i>á</i>"),
    "tem": flask.Markup("<i>?</i>"),
    "TEM": flask.Markup("<i>!</i>"),
    "thn": flask.Markup("<i>h</i>"),
    "THN": flask.Markup("<i>H</i>"),
    "tha": flask.Markup("<i>t</i>"),
    "THA": flask.Markup("<i>T</i>"),
    "val": flask.Markup("<i>l</i>"),
    "VAL": flask.Markup("<i>L</i>"),
    "vic": flask.Markup("<i>v</i>"),
    "VIC": flask.Markup("<i>V</i>"),
    "vis": flask.Markup("<i>u</i>"),
    "VIS": flask.Markup("<i>U</i>"),
    "vin": flask.Markup("<i>)</i>"),
    "def": flask.Markup("<i>@</i>"),
    "jus": flask.Markup("<i>%</i>"),
    "inn": flask.Markup("<i>#</i>"),
    "mar": flask.Markup("<i>&</i>"),
    "ven": flask.Markup("<i>(</i>"),
    "red": flask.Markup("<i>*</i>"),
    # clans
    "abomination": flask.Markup('<span class="krcg-clan">A</span>'),
    "ahrimane": flask.Markup('<span class="krcg-clan">B</span>'),
    "akunanse": flask.Markup('<span class="krcg-clan">C</span>'),
    "assamite": flask.Markup('<span class="krcg-clan">D</span>'),
    "baali": flask.Markup('<span class="krcg-clan">E</span>'),
    "blood_brother": flask.Markup('<span class="krcg-clan">F</span>'),
    "brujah": flask.Markup('<span class="krcg-clan">G</span>'),
    "brujah_antitribu": flask.Markup('<span class="krcg-clan">H</span>'),
    "caitiff": flask.Markup('<span class="krcg-clan">I</span>'),
    "daughter_of_cacophony": flask.Markup('<span class="krcg-clan">J</span>'),
    "follower_of_set": flask.Markup('<span class="krcg-clan">K</span>'),
    "gangrel": flask.Markup('<span class="krcg-clan">L</span>'),
    "gangrel_antitribu": flask.Markup('<span class="krcg-clan">M</span>'),
    "gargoyle": flask.Markup('<span class="krcg-clan">N</span>'),
    "giovanni": flask.Markup('<span class="krcg-clan">O</span>'),
    "guruhi": flask.Markup('<span class="krcg-clan">P</span>'),
    "harbinger_of_skulls": flask.Markup('<span class="krcg-clan">Q</span>'),
    "ishtarri": flask.Markup('<span class="krcg-clan">R</span>'),
    "kiasyd": flask.Markup('<span class="krcg-clan">S</span>'),
    "lasombra": flask.Markup('<span class="krcg-clan">T</span>'),
    "malkavian": flask.Markup('<span class="krcg-clan">q</span>'),
    "malkavian_legacy": flask.Markup('<span class="krcg-clan">U</span>'),
    "malkavian_antitribu": flask.Markup('<span class="krcg-clan">V</span>'),
    "nagaraja": flask.Markup('<span class="krcg-clan">W</span>'),
    "nosferatu": flask.Markup('<span class="krcg-clan">s</span>'),
    "nosferatu_legacy": flask.Markup('<span class="krcg-clan">X</span>'),
    "nosferatu_antitribu": flask.Markup('<span class="krcg-clan">Y</span>'),
    "osebo": flask.Markup('<span class="krcg-clan">Z</span>'),
    "pander": flask.Markup('<span class="krcg-clan">a</span>'),
    "ravnos": flask.Markup('<span class="krcg-clan">b</span>'),
    "salubri": flask.Markup('<span class="krcg-clan">c</span>'),
    "salubri_antitribu": flask.Markup('<span class="krcg-clan">d</span>'),
    "samedi": flask.Markup('<span class="krcg-clan">e</span>'),
    "toreador": flask.Markup('<span class="krcg-clan">t</span>'),
    "toreador_legacy": flask.Markup('<span class="krcg-clan">f</span>'),
    "toreador_antitribu": flask.Markup('<span class="krcg-clan">g</span>'),
    "tremere_legacy": flask.Markup('<span class="krcg-clan">h</span>'),
    "tremere": flask.Markup('<span class="krcg-clan">u</span>'),
    "tremere_antitribu": flask.Markup('<span class="krcg-clan">i</span>'),
    "true_brujah": flask.Markup('<span class="krcg-clan">j</span>'),
    "tzimisce": flask.Markup('<span class="krcg-clan">k</span>'),
    "ventrue": flask.Markup('<span class="krcg-clan">v</span>'),
    "ventrue_legacy": flask.Markup('<span class="krcg-clan">l</span>'),
    "ventrue_antitribu": flask.Markup('<span class="krcg-clan">m</span>'),
    "avenger": flask.Markup('<span class="krcg-clan">1</span>'),
    "defender": flask.Markup('<span class="krcg-clan">2</span>'),
    "innocent": flask.Markup('<span class="krcg-clan">3</span>'),
    "judge": flask.Markup('<span class="krcg-clan">4</span>'),
    "martyr": flask.Markup('<span class="krcg-clan">5</span>'),
    "redeemer": flask.Markup('<span class="krcg-clan">6</span>'),
    "visionary": flask.Markup('<span class="krcg-clan">7</span>'),
}


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
    return flask.redirect(f"https://static.krcg.org/card/{image}")


# Default route
@app.route("/")
@app.route("/<path:page>")
@app.route("/<lang_code>/<path:page>")
def index(lang_code=None, page=None):
    redirect = False
    if not page:
        page = "index.html"
        redirect = True
    if not lang_code or lang_code not in app.config["SUPPORTED_LANGUAGES"].keys():
        if lang_code:
            page = lang_code + "/" + page
        lang_code = (
            flask.request.accept_languages.best_match(
                app.config["SUPPORTED_LANGUAGES"].keys()
            )
            or "en"
        )
        page = "/" + lang_code + "/" + page
        redirect = True
    if redirect:
        return flask.redirect(page, 301)

    flask.g.lang_code = lang_code
    context = copy.copy(BASE_CONTEXT)
    context["lang"] = lang_code

    # use card image as og_image for card-search
    if "card-search" in page:
        card = flask.request.args.get("card")
        if card:
            image_name = unidecode.unidecode(card).lower()
            image_name = (
                image_name[4:] + "the" if image_name[:4] == "the " else image_name
            )
            image_name, _ = re.subn(r"""\s|,|\.|-|—|'|:|\(|\)|"|!""", "", image_name)
            context["og_image"] = f"http://static.krcg.org/card/{image_name}.jpg"
            context[
                "og_image_secure"
            ] = f"https://static.krcg.org/card/{image_name}.jpg"
            context["og_description"] = "Official card text and rulings"
            context["og_title"] = card
            context["og_image_dimensions"] = ["358", "500"]
    return flask.render_template(page, **context)


def _i18n_url(page, _anchor=None, locale=None, **params):
    url = "/" + (locale or get_locale()) + page.url
    if params:
        url += "?" + urllib.parse.urlencode(params)
    if _anchor:
        url += "#" + _anchor
    return url


def _link(page, name=None, _anchor=None, _class=None, locale=None, **params):
    if not page or not page.url:
        return ""
    name = name or page.name
    url = _i18n_url(page, _anchor, locale, **params)
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

    def i18n_url(page, _anchor=None, **params):
        return _i18n_url(
            navigation.HELPER.get(page, {}).get("self"), _anchor=_anchor, **params
        )

    def link(page, name=None, _anchor=None, **params):
        return _link(
            navigation.HELPER.get(page, {}).get("self"),
            name=name,
            _anchor=_anchor,
            **params,
        )

    def translation(locale, name):
        return _link(
            navigation.HELPER.get(path, {}).get("self"),
            name=name,
            locale=locale,
            _class="translation-link",
        )

    def top():
        return _link(navigation.HELPER.get(path, {}).get("top"))

    def next():
        return _link(navigation.HELPER.get(path, {}).get("next"), _class="next")

    def prev():
        return _link(navigation.HELPER.get(path, {}).get("prev"), _class="prev")

    def external(url, name, icon=None, color=None):
        if color:
            style = f' style="color: {color};"'
        else:
            style = ""
        if icon:
            span = f'<span class="brand-icon"{style}>{icon}</span> '
        else:
            span = ""
        return flask.Markup(f'<a target="_blank" href="{url}">{span}{name}</a>')

    return dict(
        i18n_url=i18n_url,
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
            '<span class="krcg-card"{data_name}>{name}</span>'.format(
                data_name=f' data-name="{name}"'
                if display_name or re.search(r" |-", name)
                else "",
                # replace spaces and hyphens with non-breakable versions in card names
                name=(display_name or name).replace(" ", " ").replace("-", "‑"),
            )
        )

    def card_image(name, hover=True):
        img = (
            '<img src="https://static.krcg.org/card/{fname}.jpg"'
            ' alt="{name}" class="krcg-card" data-name="{name}"'
        )
        if not hover:
            img += " data-nohover=true"
        img += "/>"
        return flask.Markup(img.format(name=name, fname=file_name(name)))

    return dict(card=card, card_image=card_image)
