# Writing an archetype page

The authoritative brief for writing (or refreshing) an archetype page for
codex-of-the-damned.org. Follow it exactly. It has two halves: the **mechanics**
(the template contract) and the **style** (how the prose reads). The style half
is the one that gets pages sent back — read it twice.

## Before writing

1. Read two or three existing pages as exemplars of structure and tone. Good
   ones: `top-tier/illegal-brawl.html` (toolbox, rich Variants),
   `new-kids/lasombra-politics.html` and `new-kids/qawiyya-caine.html`
   (owner-edited — treat these as the gold standard for prose style).
2. Read the co-located decklist JSON for your page. Your prose describes THIS
   list. Every card you name must be in it (or be a real observed variant).
3. Ground claims in card text: `curl -s https://api.krcg.org/card/<id-or-name>`.
   You may fetch other TWDA decks: `curl -s https://api.krcg.org/twda/<id>`.
   But see the style rules — checking a card's text is for *you* to get the
   strategy right, NOT so you can recite that text on the page.

## Mechanics — the template contract

```jinja
{% extends "archetypes/_layout.html" %}
{% import "archetypes/_layout-erratum.html" as erratum with context %}
{% import "archetypes/<section>/<slug>.json" as deck_json %}

{% block meta %}
<meta property="decklist" content='{{ deck_json | tojson }}' />
{% endblock %}

{% block archetype_name %}
<h1>{{ <clan_var> }} <Page Name></h1>
{% endblock %}

{% block archetype %}
{% trans trimmed
<param>=card("<Exact Card Name>"),
...
<player>_s_deck=link("/deck-search", _("<Player>'s deck"), id="<twda_id>")
%}
<h2>Highlights</h2>
<p>...</p>
<h2>Tips & Tricks</h2>
<p>...</p>
<h2>Variants</h2>
<p>...</p>
{% endtrans %}
{% endblock %}
```

- ALL body text lives in the single `{% trans trimmed %}` block. Card names,
  deck links, and discipline/clan icons are passed as parameters and referenced
  as `{{ param }}` — never call `card()`/`link()` inside the trans body.
- Card params: alphabetical, snake_case of the name, `card("Exact KRCG Name")`
  as spelled in the decklist JSON. Shorten display with a 2nd arg:
  `card("Aranthebes, The Immortal", "Aranthebes")`. Deck-link params last.
- **Every param you declare must be used in the body.** Cut a sentence, cut its
  param. A leftover `x=card(...)` is dead weight (and shows up in the catalog).
- Discipline icons are globals, usable directly in the body: `{{ pot }}`
  inferior, `{{ POT }}` superior. Codes: abo ani aus cel chi dai dem dom for mal
  mel myt nec obe obf obl obt pot pre pro qui san ser spi tha thn tem vic vis val.
  There is **no icon for strike/reaction keywords** (S:CE, etc.) — write those
  as words, don't invent a global like `{{ sce }}` (it renders as an empty gap).
- Clan icon for the h1 is a global too (`{{ brujah }}`, `{{ lasombra }}`,
  `{{ hecata }}`, `{{ salubri_antitribu }}`, `{{ tzimisce }}`, …, plus `_legacy`
  variants). Pick the crypt's dominant clan.
- `<em>` for the archetype-category word (wall, toolbox, rush…), `<strong>` for
  a named variant. 4-space indent inside `<p>`, lines under ~110 chars.
- Write exactly one file: the page `.html`. The decklist `.json` is generated
  separately (`scripts/page_json.py <twda_id>`).

## Style — how the prose reads

Audience: competent tournament players who know the cards by heart and can
hover/tap any card name to see its full text on the page. Write for a peer, not
a beginner. Concise, concrete, strategic. No hype, no filler.

**0. Never address the reader.** This is the firmest rule (also in the root
CLAUDE.md, site-wide). No "you", no "your". Stay generic and impersonal:
- ✗ "you can bloat with Villein" / "keep your prey low" / "if you win the combat"
- ✓ "one can bloat with Villein" / "the deck keeps the prey low" / "winning the
   combat…" / "Villein refills the pool" (impersonal subject or passive).
Imperatives are fine ("ration the stealth", "hold the lunge"). "One" for the
generic agent; "the deck"/"the player"/"the pilot" where a subject reads better.

**1. Never state deckbuilding copy counts in the generic description.** The
counts vary between instances of the archetype; a number dates the page to one
list. Describe the *role*, not the quantity.
- ✗ "9 copies of Govern the Unaligned grow the crypt, with 5 Villein to refill"
- ✓ "Govern the Unaligned grows the minion base while Villein refills the pool"
- Exceptions, all narrow:
  - A count that is itself the archetype's **signature** — an unusually heavy
    commitment that defines the engine — may stay ("twelve Freak Drive on top
    of her built-in unlock"). Default to omitting; keep only when the number is
    the point.
  - **Variants** may cite specific counts, because there the numbers are the
    information that distinguishes one concrete linked build from another
    ("the control build runs 10 Deflection, 4 Second Tradition, 4 Freak Drive").
  - **In-play board counts** are fine — they describe the game state, not the
    decklist ("once two or three titled vampires are out", "the two wraiths can
    be chump blockers").

**2. Don't explain what cards do.** The hover shows the text; the reader knows
it. Recyling card text is the number-one thing that gets a page rewritten.
- ✗ "Stygian Shroud at superior makes a block attempt fail and forbids that
   minion from trying again"  → ✓ "Stygian Shroud denies motivated blockers"
- ✗ "Shroud of Decay removes 7 cards from the ash heap to burn 3 pool" →
   ✓ "Shroud of Decay is an oust no bounce can stop"
- ✗ dumping the star's stat line (capacity / disciplines / strength / special
   ability) → ✓ name her and give her role: "built around Qawiyya el-Ghaduba
   as a star; she does all the work".
- Keep only what the hover does NOT tell them: the *strategic* reason a card is
  in the deck, non-obvious interactions, board math ("+1 stealth counter comes
  back after the combat end", "strikes climb to 5 and beyond"). When you are not
  sure a mechanic is right, cut it rather than risk reciting it wrong.

**3. Get the strategy right, not just the card text.** Card text tells you what
a card does; it does not tell you *why it is in this deck*. Common traps:
- A tech singleton usually has one specific reason — often to **contest** an
  opponent's copy, or as a metagame answer — not its generic textbook use.
  (Secure Haven in a Red List deck was maindecked to contest, not to shield.)
- Name effects by where they land: Govern grows *minions in play*, not "the
  crypt". A pool-burn/bleed is stopped by a *bounce*, not a "vote block".
- Don't build a cute multi-card combo the deck isn't actually playing. If a
  card's role is "bleeds for 3–4 once the prey is stripped", say that.
- **Out-of-turn Masters cannot be played on one's own turn.** Direct
  Intervention (and any "only usable out of turn" master) can only be played
  during another Methuselah's turn. So a deck bleeding on its OWN turn cannot
  answer the prey's bounce with its own Direct Intervention — that protection
  only exists when the deck acts out of turn (e.g. an Enkil Cog action on
  someone else's turn). A recurring mistake: never write that a deck saves DI to
  cover its own lunge/bleed. DI as reactive defense on opponents' turns
  (cancelling a master they play, or a diablerie via Archon) is fine.

**4. Cross-reference the strategy pages, and use icons.** Three habits that make
a page read like the rest of the site:

- **Link tactical concepts to the fundamentals/strategy pages** on their first
  meaningful mention (once, not every time). These are `link()` params like any
  other. Verified targets and anchors:
  - `sce=link("/strategy/combat", _("S:CE"), _anchor="defence")` — also for
    "combat ends"
  - `grinding=link("/strategy/combat", _("grinding"), _anchor="posture")`
  - `bounce=link("/strategy/fundamentals", _("bounce"), _anchor="bounce")`
  - `lunge=link("/strategy/fundamentals", _("lunge"), _anchor="lunge")`
  - `leeching=link("/strategy/bloat", _("leeching"), _anchor="leeching")`
    (bloat in general: `link("/strategy/bloat", _("bloat"), _anchor="bloat")`)
  - archetype-category words link to `/strategy/archetype-categories` with the
    matching anchor: `toolbox`, `wall`, `vote`, `rush`, `special`, and
    `_("Stealth & Bleed"), _anchor="bleed"`. (You may fold the `<em>category</em>`
    word into this link instead of italicising it.)
  - `classic_deal=link("/strategy/table-talk", _("classic deal"), _anchor="negotiation")`
  - `meta=link("/strategy/articles/advanced/the-game-of-the-game", _("meta"))`
  Anchor is always the `_anchor=` kwarg (not `id=`, which is for deck-search
  links). A `link()` to an unknown page raises in tests — only link pages that
  exist in the nav.

- **Use discipline and clan icons systematically** — on EVERY mention of a
  discipline or clan by name, not just the first. The discipline/clan word is
  always followed by its icon global: "Dominate {{ DOM }}", "both Auspex
  {{ AUS }} and Celerity {{ CEL }}", "the Ventrue {{ ventrue }} grinder",
  "Brujah {{ brujah }} barons". This is deliberate repetition: it helps newer
  players learn to recognise the disciplines and clans. The rule is one-way: a
  discipline or clan named in text WITHOUT its icon is never acceptable; the icon
  standing alone without the word (e.g. a bare `{{ DOM }}` after a card) is fine.
  Match the case to how the deck plays it: superior (uppercase, `{{ DOM }}`) if
  it uses the superior effect, inferior (`{{ dom }}`) otherwise.

- **Make deck links flow with the sentence.** Weave them in grammatically rather
  than tacking on a bare "See X." — "…endures the long game, as in
  {{ marks_deck }}" or "like Mark, for his {{ ec_2026_win }}". Vary the anchor
  text: a player's deck, the event/championship, "the same idea" — not always
  "<Name>'s deck".

**5. Section jobs.** Highlights: what the deck is, how it wins, the engine —
3-5 short paragraphs. Tips & Tricks: play advice, non-obvious lines, meta calls
— 2-4 paragraphs. Variants: only real observed variations (from the group data
you were given); link 1-3 other tournament decks via deck-link params. For a
brand-new archetype with two near-identical lists, say so honestly and keep
Variants short.

**6. The page is the analysis's *output*, not the analysis.** The deep read —
synergy, board-math, copy-count intent, vote counts, discipline spread — is how
you *reach* the conclusions; ship the conclusions, grouped by job, and let a
competent reader infer the rest. Present a module as a bare list to its job
("Organized Resistance, Deep Ecology, Earth Meld → unlock"), not a paragraph on
how the unlocking works; list a card under two jobs to signal versatility instead
of a sentence about it. Keep salience straight — the payload is a Highlight, the
loop that sustains it is a Trick (don't lead with the engine of the finish over
the finish). Vote math, copy-count-as-intent and exhaustive discipline
enumeration are analysis notes — cut them even when correct. Group the singletons
as one bucket of skill-dependent lunge/opportunity tools rather than scattering
them. Frame a tip by matchup, not mechanism. Calibrated against the owner's own
rewrites, which are almost entirely subtractive: they keep the findings and strip
the prose to functional statements.

## Before you hand off

- Page renders: `.venv/bin/python -c "from codex_of_the_damned import app;
  print(app.test_client().get('/en/archetypes/<section>/<slug>.html').status_code)"`
  → 200.
- Every `card("…")` name resolves: `curl -s -o /dev/null -w '%{http_code}'
  https://api.krcg.org/card/<url-encoded-name>` → 200.
- No unused trans params; no invented `{{ globals }}`.
- Re-read your prose against style rules 1 and 2. Cut every copy count and every
  card-text recital that slipped through.
