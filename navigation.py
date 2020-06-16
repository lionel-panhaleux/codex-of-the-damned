import urllib.parse
import collections
import re
import unidecode
from flask_babel import gettext

# ######################################################################################
# NAVIGATION
# ######################################################################################
Page = collections.namedtuple("Page", ["name", "path", "url"])


class Nav:
    def __init__(self, name, index=False, children=None):
        self.name = name
        self.index = index
        self.children = children or []

    def page(self, path):
        res = unidecode.unidecode(self.name)
        res = re.sub(r"[^\sa-zA-Z0-9]", "", res).lower().strip()
        res = re.sub(r"\s+", "-", res)
        if res == "home":
            res = path
        else:
            res = path + "/" + res
        if not self.children:
            url = res + ".html"
        elif self.index:
            url = res + "/index.html"
        else:
            url = None
        return Page(self.name, res, url)

    def walk(self, path=None, top=None, ante=None, post=None):
        page = self.page(path or "")
        if not self.children or self.index:
            yield (page.path, {"self": page, "top": top, "prev": ante, "next": post})
        if self.index:
            top = page
        for i, child in enumerate(self.children):
            if i > 0:
                ante = self.children[i - 1].page(page.path)
            else:
                ante = None
            if i < len(self.children) - 1:
                post = self.children[i + 1].page(page.path)
            else:
                post = None
            yield from child.walk(path=page.path, top=top, ante=ante, post=post)


STRUCTURE = Nav(
    gettext("Home"),
    index=True,
    children=[
        Nav(
            gettext("Strategy"),
            index=True,
            children=[
                Nav(gettext("Fundamentals")),
                Nav(gettext("Combat")),
                Nav(gettext("Bloat")),
                Nav(gettext("Deck building")),
                Nav(gettext("Archetypes")),
                Nav(gettext("Table Talk")),
                Nav(
                    gettext("Deck guides"),
                    children=[
                        Nav(gettext("Den of Fiends")),
                        Nav(gettext("Libertine Ball")),
                        Nav(gettext("Pact with Nephandi")),
                        Nav(gettext("Parliament of Shadows")),
                    ],
                ),
            ],
        ),
        Nav(
            gettext("Archetypes"),
            index=True,
            children=[
                Nav(gettext("AAA")),
                Nav(gettext("Akunanse Wall")),
                Nav(gettext("Amaravati Politics")),
                Nav(gettext("Anti ventrue Grinder")),
                Nav(gettext("Baltimore Purge")),
                Nav(gettext("Bima Dominate")),
                Nav(gettext("Black Hand")),
                Nav(gettext("Cats")),
                Nav(gettext("Council of Doom")),
                Nav(gettext("Cybelotron")),
                Nav(gettext("Daughters Politics")),
                Nav(gettext("Death Star")),
                Nav(gettext("Dmitri's Big Band")),
                Nav(gettext("Emerald Legion")),
                Nav(gettext("Euro Brujah")),
                Nav(gettext("Girls Will Find Inner Circle")),
                Nav(gettext("Goratrix High Tower")),
                Nav(gettext("Guruhi Rush")),
                Nav(gettext("Hunters")),
                Nav(gettext("Ishtarri Politics")),
                Nav(gettext("Jost Powerbleed")),
                Nav(gettext("Khazar's Diary")),
                Nav(gettext("Kiasyd Stealth & Bleed")),
                Nav(gettext("Lasombra Nocturn")),
                Nav(gettext("Lutz Politics")),
                Nav(gettext("Madness Reversal")),
                Nav(gettext("Mind Rape")),
                Nav(gettext("Mistress")),
                Nav(gettext("Nananimalism")),
                Nav(gettext("Nephandii")),
                Nav(gettext("Nosferatu Royalty")),
                Nav(gettext("Rachel Madness")),
                Nav(gettext("Ravnos Clown Car")),
                Nav(gettext("Renegade Assault")),
                Nav(gettext("Saulot & Friends")),
                Nav(gettext("Scout")),
                Nav(gettext("Shambling Hordes")),
                Nav(gettext("Spirit Marionette")),
                Nav(gettext("Stanislava")),
                Nav(gettext("Team Jacob")),
                Nav(gettext("The Bleeding Vignes")),
                Nav(gettext("The Dark Side of Politics")),
                Nav(gettext("The unnamed")),
                Nav(gettext("Tupdogs")),
                Nav(gettext("Tzimisce Toolbox")),
                Nav(gettext("Tzimisce Wall")),
                Nav(gettext("Ventrue Royalty")),
                Nav(gettext("War Chantry")),
                Nav(gettext("War Ghouls")),
                Nav(gettext("Weenie AUS")),
                Nav(gettext("Weenie DEM")),
                Nav(gettext("Weenie DOM")),
            ],
        ),
        Nav(
            gettext("Best Cards"),
            index=True,
            children=[
                Nav(
                    gettext("Generic"),
                    children=[
                        Nav(gettext("Master")),
                        Nav(gettext("Political action")),
                        Nav(gettext("No discipline")),
                        Nav(gettext("Animalism")),
                        Nav(gettext("Auspex")),
                        Nav(gettext("Celerity")),
                        Nav(gettext("Dominate")),
                        Nav(gettext("Fortitude")),
                        Nav(gettext("Necromancy")),
                        Nav(gettext("Obfuscate")),
                        Nav(gettext("Potence")),
                        Nav(gettext("Presence")),
                    ],
                ),
                Nav(
                    gettext("Sects"),
                    children=[
                        Nav(gettext("Anarch")),
                        Nav(gettext("Camarilla")),
                        Nav(gettext("Laibon")),
                        Nav(gettext("Sabbat")),
                    ],
                ),
                Nav(
                    gettext("Clans"),
                    children=[
                        Nav(gettext("Ahrimanes")),
                        Nav(gettext("Akunanse")),
                        Nav(gettext("Assamite")),
                        Nav(gettext("Baali")),
                        Nav(gettext("Brujah")),
                        Nav(gettext("Caitiff")),
                        Nav(gettext("Daughters of Cacophony")),
                        Nav(gettext("Followers of Set")),
                        Nav(gettext("Gangrel")),
                        Nav(gettext("Giovanni")),
                        Nav(gettext("Guruhi")),
                        Nav(gettext("Harbingers of Skulls")),
                        Nav(gettext("Imbued")),
                        Nav(gettext("Ishtarri")),
                        Nav(gettext("Kiasyd")),
                        Nav(gettext("Lasombra")),
                        Nav(gettext("Malkavian")),
                        Nav(gettext("Nosferatu")),
                        Nav(gettext("Ravnos")),
                        Nav(gettext("Salubri")),
                        Nav(gettext("Toreador")),
                        Nav(gettext("Tremere")),
                        Nav(gettext("True Brujah")),
                        Nav(gettext("Tzimisce")),
                        Nav(gettext("Ventrue")),
                    ],
                ),
            ],
        ),
        Nav(gettext("Deck Search"), index=True),
        Nav(gettext("Card Search"), index=True),
    ],
)


HELPER = dict(STRUCTURE.walk())
