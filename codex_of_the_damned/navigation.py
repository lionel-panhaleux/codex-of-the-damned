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
                Nav(
                    lazy_gettext("Articles"),
                    children=[
                        Nav(
                            lazy_gettext("Basic"),
                            children=[
                                Nav(lazy_gettext("Blood, Pool and Grinding Beads")),
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
                Nav("Anson Guns"),
                Nav("Anti Ventrue Grinder"),
                Nav("Cats"),
                Nav("Dementation Bleed"),
                Nav("Gangrel Barons"),
                Nav("Gentlemen With Sticks"),
                Nav("Guruhi Rush"),
                Nav("Haqim Royalty"),
                Nav("Infernal Ministry"),
                Nav("Infernal Princes"),
                Nav("Lasombra Nocturn"),
                Nav("Lutz Politics"),
                Nav("Malgorzata"),
                Nav("Malkav' 22"),
                Nav("Mistress"),
                Nav("Parliament of Shadows"),
                Nav("Platinum Protocol"),
                Nav("Rebekka / Jost"),
                Nav("Stanislava"),
                Nav("The unnamed"),
                Nav("Tzimisce Toolbox"),
                Nav("War Chantry"),
                Nav(
                    lazy_gettext("Runner Ups"),
                    index=False,
                    children=[
                        Nav("Black Hand"),
                        Nav("Blind Spot"),
                        Nav("Goratrix High Tower"),
                        Nav("Guillaume Real Estate"),
                        Nav("Hunters"),
                        Nav("Nananimalism"),
                        Nav("Palla Grande"),
                        Nav("Saulot Wall"),
                    ],
                ),
                Nav(
                    lazy_gettext("Neonate"),
                    index=False,
                    children=[
                        Nav("Aching Beauty"),
                        Nav("Giovanni Powerbleed"),
                        Nav("Harbinger Legionnaires"),
                        Nav("Infernal Royalty"),
                        Nav("Lasombra Nocturn"),
                        Nav("Lutz Vote"),
                        Nav("Malkavian Dementation"),
                        Nav("Malkavian Dominate"),
                        Nav("Nephandus"),
                        Nav("Nosferatu Primogens"),
                        Nav("Ravnos Clown Car"),
                        Nav("Samedi Rush"),
                        Nav("Stanislava"),
                        Nav("The Capuchin"),
                        Nav("The unnamed"),
                        Nav("Tremere Grinder"),
                        Nav("Tremere Wall"),
                        Nav("Tzimisce Toolbox"),
                        Nav("Ventrue Grinder"),
                        Nav("Ventrue Lawfirm"),
                    ],
                ),
                Nav(
                    lazy_gettext("Bibliodèque"),
                    index=False,
                    children=[
                        Nav("419 Operation"),
                        Nav("Akunanse Toolbox"),
                        Nav("Amaravati Politics"),
                        Nav("Anson Grooming"),
                        Nav("Anu Diptinatpa"),
                        Nav("Arika & Friends"),
                        Nav("Armin the Hammer"),
                        Nav("Ayo Igoli"),
                        Nav("Baltimore Purge"),
                        Nav("Bima Dominate"),
                        Nav("Brujah Debate"),
                        Nav("Carnivalesque"),
                        Nav("Council of Doom"),
                        Nav("Cybele Maleficia"),
                        Nav("Cybelotron"),
                        Nav("Daughters Politics"),
                        Nav("Death Seekers"),
                        Nav("Death Star"),
                        Nav("Dekox Ultimus"),
                        Nav("Dmitri's Big Band"),
                        Nav("Dragon's Breath Rounds"),
                        Nav("Emerald Legion"),
                        Nav("Enkidu Multirush"),
                        Nav("Euro Brujah"),
                        Nav("Extrême Violence"),
                        Nav("Fear Factor"),
                        Nav("First Tradition"),
                        Nav("Ghede Typhonic Beast"),
                        Nav("Giovanni Powerbleed"),
                        Nav("Girls Will Find Inner Circle"),
                        Nav("Hakuna Matata"),
                        Nav("Hermanas"),
                        Nav("Ishtarri Politics"),
                        Nav("Khazar's Diary"),
                        Nav("Kiasyd Stealth & Bleed"),
                        Nav("Kiev Circle"),
                        Nav("Knave's Revenge"),
                        Nav("Legacy of Pander"),
                        Nav("Lorrie Superstar"),
                        Nav("Lutz's Coopt"),
                        Nav("Madness Reversal"),
                        Nav("Malkav' 94"),
                        Nav("Matasuntha"),
                        Nav("Meat Shields"),
                        Nav("Miller Delmo"),
                        Nav("Mind Rape"),
                        Nav("MMPA Politics"),
                        Nav("Mono Valeren"),
                        Nav("Nagagrinder"),
                        Nav("Nakhthorheb"),
                        Nav("Nosferatu Royalty"),
                        Nav("Nuriel"),
                        Nav("Rachel Madness"),
                        Nav("Ravnos Clown Car"),
                        Nav("Renegade Assault"),
                        Nav("Richter & Friends"),
                        Nav("Rock Cats"),
                        Nav("Samedi Bleed"),
                        Nav("Sarrasine Velvet Tongue"),
                        Nav("Scout"),
                        Nav("Shadow Court Satyrs"),
                        Nav("Shalmath History"),
                        Nav("Shambling Hordes"),
                        Nav("Sha's Trio"),
                        Nav("Slaughtermanship"),
                        Nav("Spell of Life"),
                        Nav("Spirit Marionette"),
                        Nav("Storia di Buratino"),
                        Nav("Tariq Eats the World"),
                        Nav("The Bleeding Vignes"),
                        Nav("The Dark Side of Politics"),
                        Nav("Tongue of the Serpent"),
                        Nav("Trap Horrid"),
                        Nav("Trapappa"),
                        Nav("Tunnel Runners"),
                        Nav("Tupdogs & Nephandus"),
                        Nav("Turbo Sensory"),
                        Nav("Ublo's Harem"),
                        Nav("Unacceptable Boon"),
                        Nav("War Ghouls"),
                        Nav("Weenie AUS"),
                        Nav("Weenie DEM"),
                        Nav("Weenie DOM"),
                        Nav("Weenie PRE"),
                        Nav("Weenie VIC"),
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
