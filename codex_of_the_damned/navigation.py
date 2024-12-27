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
            short_path = page.path.split("/")[1:]
            if not self.children and len(short_path) > 2:
                short_path = "/" + "/".join([short_path[0], short_path[-1]])
                yield (
                    short_path,
                    {"self": page, "top": top, "prev": ante, "next": post},
                )
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
                Nav(lazy_gettext("Archetype Categories")),
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
                Nav(
                    lazy_gettext("Articles"),
                    children=[
                        Nav(
                            lazy_gettext("Basic"),
                            children=[
                                Nav(lazy_gettext("Blood, Pool and Grinding Beads")),
                                Nav(lazy_gettext("Combat Primer")),
                                Nav(lazy_gettext("Guide for MTG Players")),
                                Nav(lazy_gettext("What Should I Buy?")),
                            ],
                        ),
                        Nav(
                            lazy_gettext("Advanced"),
                            children=[
                                Nav(lazy_gettext("The Game of the Game")),
                                Nav(lazy_gettext("Playing Montano Baltimore Purge")),
                                Nav(lazy_gettext("Playing Tupdogs & Nephandus")),
                                Nav(lazy_gettext("Combat Modules")),
                            ],
                        ),
                    ],
                ),
            ],
        ),
        Nav(
            lazy_gettext("Archetypes"),
            index=True,
            children=[
                Nav(
                    lazy_gettext("Top Tier"),
                    index=False,
                    children=[
                        Nav("Brujah Resistance"),
                        Nav("Gangrel Thing"),
                        Nav("Guruhi Rush"),
                        Nav("Haqim Royalty"),
                        Nav("Infernal Barons"),
                        Nav("Lasombra Nocturn"),
                        Nav("Lutz Politics"),
                        Nav("Malk' 22"),
                        Nav("Mistress"),
                        Nav("Nananimalism"),
                        Nav("Platinum Revelation"),
                        Nav("Princess Toolbox"),
                        Nav("Stanislava"),
                    ],
                ),
                Nav(
                    lazy_gettext("Runner Ups"),
                    index=False,
                    children=[
                        Nav("Blind Spot"),
                        Nav("Reign of Lasombra"),
                        Nav("The unnamed"),
                        Nav("Tupdogs & Nephandus"),
                    ],
                ),
                Nav(
                    lazy_gettext("New Kids"),
                    index=False,
                    children=[
                        Nav("Animals"),
                        Nav("Banu Politics"),
                        Nav("Chameleon"),
                        Nav("Hesha's Emporium"),
                        Nav("Ravnos Break"),
                        Nav("Salubri Powerbleed"),
                        Nav("Savannah Salt"),
                    ],
                ),
                Nav(
                    lazy_gettext("Archive"),
                    index=False,
                    children=[
                        Nav("Akunanse Toolbox"),
                        Nav("Amaravati Politics"),
                        Nav("Anson Guns"),
                        Nav("Anti Ventrue Grinder"),
                        Nav("Baltimore Purge"),
                        Nav("Bima Dominate"),
                        Nav("Black Hand"),
                        Nav("Cats"),
                        Nav("Council of Doom"),
                        Nav("Cybelotron"),
                        Nav("Daughters Politics"),
                        Nav("DBR"),
                        Nav("Death Star"),
                        Nav("Dementation Bleed"),
                        Nav("Dmitri's Big Band"),
                        Nav("Emerald Legion"),
                        Nav("Enkidu Multirush"),
                        Nav("Euro Brujah"),
                        Nav("Fear Factor"),
                        Nav("Gentlemen With Sticks"),
                        Nav("Ghede Typhonic Beast"),
                        Nav("Giovanni Powerbleed"),
                        Nav("Girls Will Find Inner Circle"),
                        Nav("Goratrix High Tower"),
                        Nav("Guillaume Real Estate"),
                        Nav("Hunters"),
                        Nav("Infernal Princes"),
                        Nav("Ishtarri Politics"),
                        Nav("Khazar's Diary"),
                        Nav("Kiasyd Stealth & Bleed"),
                        Nav("Legacy of Pander"),
                        Nav("Madness Reversal"),
                        Nav("Malgorzata"),
                        Nav("Malk' 94"),
                        Nav("Mind Rape"),
                        Nav("MMPA Politics"),
                        Nav("Nosferatu Royalty"),
                        Nav("Palla Grande"),
                        Nav("Parliament of Shadows"),
                        Nav("Rachel Madness"),
                        Nav("Ravnos Clown Car"),
                        Nav("Rebekka / Jost"),
                        Nav("Renegade Assault"),
                        Nav("Samedi Bleed"),
                        Nav("Saulot Wall"),
                        Nav("Scout"),
                        Nav("Shadow Court Satyrs"),
                        Nav("Shalmath History"),
                        Nav("Shambling Hordes"),
                        Nav("Spell of Life"),
                        Nav("Spirit Marionette"),
                        Nav("Tariq Eats the World"),
                        Nav("The Bleeding Vignes"),
                        Nav("The Dark Side of Politics"),
                        Nav("Tunnel Runners"),
                        Nav("Tzimisce Toolbox"),
                        Nav("War Ghouls"),
                        Nav("Weenie AUS"),
                        Nav("Weenie DOM"),
                    ],
                ),
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
                        Nav(lazy_gettext("Baali")),
                        Nav(lazy_gettext("Banu Haqim")),
                        Nav(lazy_gettext("Brujah")),
                        Nav(lazy_gettext("Caitiff")),
                        Nav(lazy_gettext("Daughters of Cacophony")),
                        Nav(lazy_gettext("Gangrel")),
                        Nav(lazy_gettext("Giovanni")),
                        Nav(lazy_gettext("Guruhi")),
                        Nav(lazy_gettext("Harbingers of Skulls")),
                        Nav(lazy_gettext("Imbued")),
                        Nav(lazy_gettext("Ishtarri")),
                        Nav(lazy_gettext("Kiasyd")),
                        Nav(lazy_gettext("Lasombra")),
                        Nav(lazy_gettext("Malkavian")),
                        Nav(lazy_gettext("Ministry")),
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
