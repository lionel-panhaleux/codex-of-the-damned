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
                        Nav(lazy_gettext("The Game of the Game")),
                        Nav(lazy_gettext("Playing Montano Baltimore Purge")),
                    ],
                ),
            ],
        ),
        Nav(
            lazy_gettext("Archetypes"),
            index=True,
            children=[
                Nav("AAA"),
                Nav("Akunanse Wall"),
                Nav("Amaravati Politics"),
                Nav("Anti ventrue Grinder"),
                Nav("Baltimore Purge"),
                Nav("Bima Dominate"),
                Nav("Black Hand"),
                Nav("Cats"),
                Nav("Council of Doom"),
                Nav("Cybelotron"),
                Nav("Daughters Politics"),
                Nav("Death Star"),
                Nav("Dmitri's Big Band"),
                Nav("Emerald Legion"),
                Nav("Euro Brujah"),
                Nav("Girls Will Find Inner Circle"),
                Nav("Goratrix High Tower"),
                Nav("Guruhi Rush"),
                Nav("Hunters"),
                Nav("Ishtarri Politics"),
                Nav("Jost Powerbleed"),
                Nav("Khazar's Diary"),
                Nav("Kiasyd Stealth & Bleed"),
                Nav("Lasombra Nocturn"),
                Nav("Lutz Politics"),
                Nav("Madness Reversal"),
                Nav("Mind Rape"),
                Nav("Mistress"),
                Nav("Nananimalism"),
                Nav("Nephandii"),
                Nav("Nosferatu Royalty"),
                Nav("Rachel Madness"),
                Nav("Ravnos Clown Car"),
                Nav("Renegade Assault"),
                Nav("Saulot & Friends"),
                Nav("Scout"),
                Nav("Shambling Hordes"),
                Nav("Spirit Marionette"),
                Nav("Stanislava"),
                Nav("Team Jacob"),
                Nav("The Bleeding Vignes"),
                Nav("The Dark Side of Politics"),
                Nav("The unnamed"),
                Nav("Tupdogs"),
                Nav("Tzimisce Toolbox"),
                Nav("Tzimisce Wall"),
                Nav("Ventrue Royalty"),
                Nav("War Chantry"),
                Nav("War Ghouls"),
                Nav("Weenie AUS"),
                Nav("Weenie DEM"),
                Nav("Weenie DOM"),
                Nav(
                    lazy_gettext("Bibliodèque"),
                    index=False,
                    children=[
                        Nav("419 Operation"),
                        Nav("Akunanse Classic"),
                        Nav("Anson Grooming"),
                        Nav("Anson Guns"),
                        Nav("Anu Diptinatpa"),
                        Nav("Armin the Hammer"),
                        Nav("Army of Allah"),
                        Nav("Aviary"),
                        Nav("Ayo Igoli"),
                        Nav("Baltimore Purge"),
                        Nav("Better Gentlemen"),
                        Nav("Big Cock"),
                        Nav("Bima Dominate"),
                        Nav("Brujah Debate"),
                        Nav("Carna"),
                        Nav("Carnivalesque"),
                        Nav("Collier of Love"),
                        Nav("Cybele Great Beast"),
                        Nav("Cybele Maleficia"),
                        Nav("Daughters"),
                        Nav("Death Seekers"),
                        Nav("Dekox Ultimus"),
                        Nav("Dominarium"),
                        Nav("Dragon's Breath Rounds"),
                        Nav("Emerald Legionnaire"),
                        Nav("Enkidu Multirush"),
                        Nav("Euro Brujah"),
                        Nav("Extrême Violence"),
                        Nav("Family Business"),
                        Nav("Fat Usurper"),
                        Nav("Fear Factor"),
                        Nav("Fear of the Dard"),
                        Nav("First Tradition"),
                        Nav("Frosties Gogo"),
                        Nav("Ghede Typhonic Beast"),
                        Nav("Girls' Immortal Grapple"),
                        Nav("Girls Will Find Inner Circle"),
                        Nav("Guillaume Giovanni"),
                        Nav("Hakuna Matata"),
                        Nav("He-who-shall-not-be-named"),
                        Nav("Hermanas"),
                        Nav("Howler & Friends"),
                        Nav("Imbued"),
                        Nav("Isabel & Boys"),
                        Nav("Kiev Circle"),
                        Nav("Knave's Revenge"),
                        Nav("Koudéta"),
                        Nav("Legacy of Pander"),
                        Nav("Lorrie Superstar"),
                        Nav("Lutz's Coopt"),
                        Nav("Malgorzata & Friends"),
                        Nav("Malkavian Royalty"),
                        Nav("Matasuntha"),
                        Nav("Meat Shields"),
                        Nav("Midcap DEM"),
                        Nav("Miller Delmo"),
                        Nav("Mono Valeren"),
                        Nav("Muricia & Friends"),
                        Nav("Nagagrinder"),
                        Nav("Nakhtoreb"),
                        Nav("Nephandii"),
                        Nav("No Secret Box of Tools"),
                        Nav("Nosferatu Royalty"),
                        Nav("Nuriel"),
                        Nav("Order 66"),
                        Nav("Ozmo 94"),
                        Nav("Palla Grande"),
                        Nav("Piper War Ghoul"),
                        Nav("Red Army"),
                        Nav("Reversal"),
                        Nav("Richter & Friends"),
                        Nav("Rock Cats"),
                        Nav("Sarrasine Velvet Tongue"),
                        Nav("Seraph's Ambitions"),
                        Nav("Sha's Trio"),
                        Nav("Shadow Court Satyrs"),
                        Nav("Slaughtermanship"),
                        Nav("Spell of Life"),
                        Nav("Spirit Marionette"),
                        Nav("Stanislava"),
                        Nav("Storia di Buratino"),
                        Nav("Summon a Shal"),
                        Nav("Tariq Eats the World"),
                        Nav("Tongue of the Serpent"),
                        Nav("Torchon brûlant"),
                        Nav("Trap Horrid"),
                        Nav("Trapappa"),
                        Nav("Tuna Tunnel"),
                        Nav("Tunnel Runners"),
                        Nav("Tupdogs"),
                        Nav("Turbo Sensory"),
                        Nav("Ublo's Harem"),
                        Nav("Una Circus"),
                        Nav("Unacceptable Boon"),
                        Nav("Unmada Crescendo"),
                        Nav("Warding Pan"),
                        Nav("Weenie ANI"),
                        Nav("Weenie AUS"),
                        Nav("Weenie DEM"),
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
