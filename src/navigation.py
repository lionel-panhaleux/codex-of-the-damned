import collections
import re
import unidecode
from flask_babel import lazy_gettext


Page = collections.namedtuple("Page", ["name", "path", "url"])


class Nav:
    def __init__(self, name, index=False, children=None):
        self.name = name
        self.index = index
        self.children = children or []

    def page(self, path):
        res = unidecode.unidecode(str(self.name))
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
    # TRANSLATORS: please abide by BCP translation choices for game terms when possible.
    lazy_gettext("Home"),
    index=True,
    children=[
        Nav(
            lazy_gettext("Online Play"),
            index=True,
            children=[
                Nav(lazy_gettext("LackeyCCG")),
                Nav(lazy_gettext("Tabletop Simulator")),
                Nav(lazy_gettext("V:TES Online")),
            ],
        ),
        Nav(
            lazy_gettext("Strategy"),
            index=True,
            children=[
                Nav(lazy_gettext("Fundamentals")),
                Nav(lazy_gettext("Combat")),
                Nav(lazy_gettext("Bloat")),
                Nav(lazy_gettext("Deck building")),
                Nav(lazy_gettext("Archetypes")),
                Nav(lazy_gettext("Table Talk")),
                Nav(
                    lazy_gettext("Deck guides"),
                    children=[
                        Nav(lazy_gettext("Den of Fiends")),
                        Nav(lazy_gettext("Libertine Ball")),
                        Nav(lazy_gettext("Pact with Nephandi")),
                        Nav(lazy_gettext("Parliament of Shadows")),
                    ],
                ),
            ],
        ),
        Nav(
            lazy_gettext("Archetypes"),
            index=True,
            children=[
                Nav(lazy_gettext("AAA")),
                Nav(lazy_gettext("Akunanse Wall")),
                Nav(lazy_gettext("Amaravati Politics")),
                Nav(lazy_gettext("Anti ventrue Grinder")),
                Nav(lazy_gettext("Baltimore Purge")),
                Nav(lazy_gettext("Bima Dominate")),
                Nav(lazy_gettext("Black Hand")),
                Nav(lazy_gettext("Cats")),
                Nav(lazy_gettext("Council of Doom")),
                Nav(lazy_gettext("Cybelotron")),
                Nav(lazy_gettext("Daughters Politics")),
                Nav(lazy_gettext("Death Star")),
                Nav(lazy_gettext("Dmitri's Big Band")),
                Nav(lazy_gettext("Emerald Legion")),
                Nav(lazy_gettext("Euro Brujah")),
                Nav(lazy_gettext("Girls Will Find Inner Circle")),
                Nav(lazy_gettext("Goratrix High Tower")),
                Nav(lazy_gettext("Guruhi Rush")),
                Nav(lazy_gettext("Hunters")),
                Nav(lazy_gettext("Ishtarri Politics")),
                Nav(lazy_gettext("Jost Powerbleed")),
                Nav(lazy_gettext("Khazar's Diary")),
                Nav(lazy_gettext("Kiasyd Stealth & Bleed")),
                Nav(lazy_gettext("Lasombra Nocturn")),
                Nav(lazy_gettext("Lutz Politics")),
                Nav(lazy_gettext("Madness Reversal")),
                Nav(lazy_gettext("Mind Rape")),
                Nav(lazy_gettext("Mistress")),
                Nav(lazy_gettext("Nananimalism")),
                Nav(lazy_gettext("Nephandii")),
                Nav(lazy_gettext("Nosferatu Royalty")),
                Nav(lazy_gettext("Rachel Madness")),
                Nav(lazy_gettext("Ravnos Clown Car")),
                Nav(lazy_gettext("Renegade Assault")),
                Nav(lazy_gettext("Saulot & Friends")),
                Nav(lazy_gettext("Scout")),
                Nav(lazy_gettext("Shambling Hordes")),
                Nav(lazy_gettext("Spirit Marionette")),
                Nav(lazy_gettext("Stanislava")),
                Nav(lazy_gettext("Team Jacob")),
                Nav(lazy_gettext("The Bleeding Vignes")),
                Nav(lazy_gettext("The Dark Side of Politics")),
                Nav(lazy_gettext("The unnamed")),
                Nav(lazy_gettext("Tupdogs")),
                Nav(lazy_gettext("Tzimisce Toolbox")),
                Nav(lazy_gettext("Tzimisce Wall")),
                Nav(lazy_gettext("Ventrue Royalty")),
                Nav(lazy_gettext("War Chantry")),
                Nav(lazy_gettext("War Ghouls")),
                Nav(lazy_gettext("Weenie AUS")),
                Nav(lazy_gettext("Weenie DEM")),
                Nav(lazy_gettext("Weenie DOM")),
            ],
        ),
        Nav(
            lazy_gettext("Best Cards"),
            index=True,
            children=[
                Nav(
                    lazy_gettext("Generic"),
                    children=[
                        Nav(lazy_gettext("Master cards")),
                        Nav(lazy_gettext("Political actions")),
                        Nav(lazy_gettext("No discipline")),
                        Nav(lazy_gettext("Animalism")),
                        Nav(lazy_gettext("Auspex")),
                        Nav(lazy_gettext("Celerity")),
                        Nav(lazy_gettext("Dominate")),
                        Nav(lazy_gettext("Fortitude")),
                        Nav(lazy_gettext("Necromancy")),
                        Nav(lazy_gettext("Obfuscate")),
                        Nav(lazy_gettext("Potence")),
                        Nav(lazy_gettext("Presence")),
                    ],
                ),
                Nav(
                    lazy_gettext("Sects"),
                    children=[
                        Nav(lazy_gettext("Anarch")),
                        Nav(lazy_gettext("Camarilla")),
                        Nav(lazy_gettext("Laibon")),
                        Nav(lazy_gettext("Sabbat")),
                    ],
                ),
                Nav(
                    lazy_gettext("Clans"),
                    children=[
                        Nav(lazy_gettext("Ahrimanes")),
                        Nav(lazy_gettext("Akunanse")),
                        Nav(lazy_gettext("Assamite")),
                        Nav(lazy_gettext("Baali")),
                        Nav(lazy_gettext("Brujah")),
                        Nav(lazy_gettext("Caitiff")),
                        Nav(lazy_gettext("Daughters of Cacophony")),
                        Nav(lazy_gettext("Followers of Set")),
                        Nav(lazy_gettext("Gangrel")),
                        Nav(lazy_gettext("Giovanni")),
                        Nav(lazy_gettext("Guruhi")),
                        Nav(lazy_gettext("Harbingers of Skulls")),
                        Nav(lazy_gettext("Imbued")),
                        Nav(lazy_gettext("Ishtarri")),
                        Nav(lazy_gettext("Kiasyd")),
                        Nav(lazy_gettext("Lasombra")),
                        Nav(lazy_gettext("Malkavian")),
                        Nav(lazy_gettext("Nosferatu")),
                        Nav(lazy_gettext("Ravnos")),
                        Nav(lazy_gettext("Salubri")),
                        Nav(lazy_gettext("Toreador")),
                        Nav(lazy_gettext("Tremere")),
                        Nav(lazy_gettext("True Brujah")),
                        Nav(lazy_gettext("Tzimisce")),
                        Nav(lazy_gettext("Ventrue")),
                    ],
                ),
            ],
        ),
        Nav(lazy_gettext("Deck Search"), index=True),
        Nav(lazy_gettext("Card Search"), index=True),
    ],
)


HELPER = dict(STRUCTURE.walk())
