import copy
import pkg_resources
import urllib.parse
import re
import unidecode

import flask
import flask_babel
import jinja2.exceptions

from . import config
from . import navigation

version = pkg_resources.Environment()["codex-of-the-damned"][0].version
app = flask.Flask(__name__, template_folder="templates")
app.jinja_env.policies["ext.i18n.trimmed"] = True
babel = flask_babel.Babel(app)
config.configure_app(app)

BASE_CONTEXT = {
    "version": version,
    "CONVICTION": flask.Markup('<span class="krcg-icon">¤</span>'),
    "CONVICTION_1": flask.Markup('<span class="krcg-icon">¤</span>'),
    "CONVICTION_2": flask.Markup('<span class="krcg-icon">¤¤</span>'),
    "CONVICTION_3": flask.Markup('<span class="krcg-icon">¤¤¤</span>'),
    "CONVICTION_4": flask.Markup('<span class="krcg-icon">¤¤¤¤</span>'),
    "CONVICTION_5": flask.Markup('<span class="krcg-icon">¤¤¤¤¤</span>'),
    "ACTION": flask.Markup('<span class="krcg-icon">0</span>'),
    "ACTION_MODIFIER": flask.Markup('<span class="krcg-icon">1</span>'),
    "REACTION": flask.Markup('<span class="krcg-icon">7</span>'),
    "COMBAT": flask.Markup('<span class="krcg-icon">4</span>'),
    "REFLEX": flask.Markup('<span class="krcg-icon">6</span>'),
    "FLIGHT": flask.Markup('<span class="krcg-icon">^</span>'),
    "MERGED": flask.Markup('<span class="krcg-icon">µ</span>'),
    "POWER": flask.Markup('<span class="krcg-icon">§</span>'),
    "abo": flask.Markup('<span class="krcg-icon">w</span>'),
    "ABO": flask.Markup('<span class="krcg-icon">W</span>'),
    "ani": flask.Markup('<span class="krcg-icon">i</span>'),
    "ANI": flask.Markup('<span class="krcg-icon">I</span>'),
    "aus": flask.Markup('<span class="krcg-icon">a</span>'),
    "AUS": flask.Markup('<span class="krcg-icon">A</span>'),
    "cel": flask.Markup('<span class="krcg-icon">c</span>'),
    "CEL": flask.Markup('<span class="krcg-icon">C</span>'),
    "chi": flask.Markup('<span class="krcg-icon">k</span>'),
    "CHI": flask.Markup('<span class="krcg-icon">K</span>'),
    "dai": flask.Markup('<span class="krcg-icon">y</span>'),
    "DAI": flask.Markup('<span class="krcg-icon">Y</span>'),
    "dem": flask.Markup('<span class="krcg-icon">e</span>'),
    "DEM": flask.Markup('<span class="krcg-icon">E</span>'),
    "dom": flask.Markup('<span class="krcg-icon">d</span>'),
    "DOM": flask.Markup('<span class="krcg-icon">D</span>'),
    "for": flask.Markup('<span class="krcg-icon">f</span>'),
    "FOR": flask.Markup('<span class="krcg-icon">F</span>'),
    "mal": flask.Markup('<span class="krcg-icon">â</span>'),
    "MAL": flask.Markup('<span class="krcg-icon">ã</span>'),
    "mel": flask.Markup('<span class="krcg-icon">m</span>'),
    "MEL": flask.Markup('<span class="krcg-icon">M</span>'),
    "myt": flask.Markup('<span class="krcg-icon">x</span>'),
    "MYT": flask.Markup('<span class="krcg-icon">X</span>'),
    "nec": flask.Markup('<span class="krcg-icon">n</span>'),
    "NEC": flask.Markup('<span class="krcg-icon">N</span>'),
    "obe": flask.Markup('<span class="krcg-icon">b</span>'),
    "OBE": flask.Markup('<span class="krcg-icon">B</span>'),
    "obf": flask.Markup('<span class="krcg-icon">o</span>'),
    "OBF": flask.Markup('<span class="krcg-icon">O</span>'),
    "obt": flask.Markup('<span class="krcg-icon">$</span>'),
    "OBT": flask.Markup('<span class="krcg-icon">£</span>'),
    "pot": flask.Markup('<span class="krcg-icon">p</span>'),
    "POT": flask.Markup('<span class="krcg-icon">P</span>'),
    "pre": flask.Markup('<span class="krcg-icon">r</span>'),
    "PRE": flask.Markup('<span class="krcg-icon">R</span>'),
    "pro": flask.Markup('<span class="krcg-icon">j</span>'),
    "PRO": flask.Markup('<span class="krcg-icon">J</span>'),
    "qui": flask.Markup('<span class="krcg-icon">q</span>'),
    "QUI": flask.Markup('<span class="krcg-icon">Q</span>'),
    "san": flask.Markup('<span class="krcg-icon">g</span>'),
    "SAN": flask.Markup('<span class="krcg-icon">G</span>'),
    "ser": flask.Markup('<span class="krcg-icon">s</span>'),
    "SER": flask.Markup('<span class="krcg-icon">S</span>'),
    "spi": flask.Markup('<span class="krcg-icon">z</span>'),
    "SPI": flask.Markup('<span class="krcg-icon">Z</span>'),
    "str": flask.Markup('<span class="krcg-icon">à</span>'),
    "STR": flask.Markup('<span class="krcg-icon">á</span>'),
    "tem": flask.Markup('<span class="krcg-icon">?</span>'),
    "TEM": flask.Markup('<span class="krcg-icon">!</span>'),
    "thn": flask.Markup('<span class="krcg-icon">h</span>'),
    "THN": flask.Markup('<span class="krcg-icon">H</span>'),
    "tha": flask.Markup('<span class="krcg-icon">t</span>'),
    "THA": flask.Markup('<span class="krcg-icon">T</span>'),
    "val": flask.Markup('<span class="krcg-icon">l</span>'),
    "VAL": flask.Markup('<span class="krcg-icon">L</span>'),
    "vic": flask.Markup('<span class="krcg-icon">v</span>'),
    "VIC": flask.Markup('<span class="krcg-icon">V</span>'),
    "vis": flask.Markup('<span class="krcg-icon">u</span>'),
    "VIS": flask.Markup('<span class="krcg-icon">U</span>'),
    "vin": flask.Markup('<span class="krcg-icon">)</span>'),
    "def": flask.Markup('<span class="krcg-icon">@</span>'),
    "jus": flask.Markup('<span class="krcg-icon">%</span>'),
    "inn": flask.Markup('<span class="krcg-icon">#</span>'),
    "mar": flask.Markup('<span class="krcg-icon">&</span>'),
    "ven": flask.Markup('<span class="krcg-icon">(</span>'),
    "red": flask.Markup('<span class="krcg-icon">*</span>'),
    # clans
    "abomination": flask.Markup('<span class="krcg-clan">A</span>'),
    "ahrimane": flask.Markup('<span class="krcg-clan">B</span>'),
    "akunanse": flask.Markup('<span class="krcg-clan">C</span>'),
    "assamite": flask.Markup('<span class="krcg-clan">n</span>'),
    "assamite_legacy": flask.Markup('<span class="krcg-clan">D</span>'),
    "baali": flask.Markup('<span class="krcg-clan">E</span>'),
    "banu_haqim": flask.Markup('<span class="krcg-clan">n</span>'),
    "blood_brother": flask.Markup('<span class="krcg-clan">F</span>'),
    "brujah": flask.Markup('<span class="krcg-clan">G</span>'),
    "brujah_antitribu": flask.Markup('<span class="krcg-clan">H</span>'),
    "caitiff": flask.Markup('<span class="krcg-clan">I</span>'),
    "daughter": flask.Markup('<span class="krcg-clan">J</span>'),
    "daughter_of_cacophony": flask.Markup('<span class="krcg-clan">J</span>'),
    "follower_of_set": flask.Markup('<span class="krcg-clan">r</span>'),
    "follower_of_set_legacy": flask.Markup('<span class="krcg-clan">K</span>'),
    "gangrel": flask.Markup('<span class="krcg-clan">p</span>'),
    "gangrel_antitribu": flask.Markup('<span class="krcg-clan">M</span>'),
    "gargoyle": flask.Markup('<span class="krcg-clan">N</span>'),
    "giovanni": flask.Markup('<span class="krcg-clan">O</span>'),
    "guruhi": flask.Markup('<span class="krcg-clan">P</span>'),
    "harbinger": flask.Markup('<span class="krcg-clan">Q</span>'),
    "harbinger_of_skulls": flask.Markup('<span class="krcg-clan">Q</span>'),
    "ishtarri": flask.Markup('<span class="krcg-clan">R</span>'),
    "kiasyd": flask.Markup('<span class="krcg-clan">S</span>'),
    "lasombra": flask.Markup('<span class="krcg-clan">w</span>'),
    "malkavian": flask.Markup('<span class="krcg-clan">q</span>'),
    "malkavian_legacy": flask.Markup('<span class="krcg-clan">U</span>'),
    "malkavian_antitribu": flask.Markup('<span class="krcg-clan">V</span>'),
    "ministry": flask.Markup('<span class="krcg-clan">r</span>'),
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


# Serve sitemap template
# code used from https://gist.github.com/Julian-Nash/aa3041b47183176ca9ff81c8382b655a
@app.route("/sitemap.xml")
def sitemap():
    host_components = urllib.parse.urlparse(flask.request.host_url)
    host_base = host_components.scheme + "://" + host_components.netloc

    urls = [host_base + p["self"].url for p in navigation.HELPER.values()]

    xml_sitemap = flask.render_template("sitemap.xml", urls=urls, host_base=host_base)
    response = flask.make_response(xml_sitemap)
    response.headers["Content-Type"] = "application/xml"

    return response


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
        # if there is no valid lang code, the variable stores the path root
        # put it back in path
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
    section = page.split("/", 1)[0]
    section = section.split(".", 1)[0]
    if section != page:
        context["section"] = section
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


def _link(
    page, name=None, _anchor=None, _class=None, _prefix=None, locale=None, **params
):
    if not page or not page.url:
        return ""
    name = name or page.name
    url = _i18n_url(page, _anchor, locale, **params)
    if _class:
        _class = f"class={_class} "
    else:
        _class = ""
    if _prefix:
        name = f"{BASE_CONTEXT[_prefix]} &nbsp {name}"
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

    def title():
        try:
            if navigation.HELPER.get(path, {}).get("self").path != "":
                name = navigation.HELPER.get(path, {}).get("self").name
                return f"CotD — {name}"
        except AttributeError:
            pass
        return "Codex of the Damned"

    return dict(
        i18n_url=i18n_url,
        link=link,
        translation=translation,
        title=title,
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
