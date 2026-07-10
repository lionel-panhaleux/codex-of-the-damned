# Calibration corpus — owner-graded deck analyses

Worked examples for the strategist agent. Each case study pairs an initial analysis with the
owner's corrections (2026-07 calibration sessions). The **general lessons** distilled from the
corrections are the operating heuristics; the case studies show the expected depth. Owner's
grade on round 1: "readings accurate, but a bit shallow" — the missing depth was module-internal
synergy, meta-dating, and copy-count intent.

## General lessons

**Grounding**

- Never reason from remembered card text. Fetch from the KRCG API (`https://api.krcg.org/card/<id-or-name>`)
  before analyzing. Roughly a third of from-memory card readings were wrong in round 1.
- **Date the deck, then read it against its year.** A decklist is a meta answer, not a timeless
  artifact. Check `card-changes-history.md` (errata/nerfs: what did the card do *then*?) and
  `meta-by-year.md` (what were the top threats *then*?). Example: a 2023 list with a tight stealth
  package and anti-ally tech reads correctly only against the pre-nerf Emerald Legion, low-intercept,
  allies-heavy 2023 meta; the same package is likely insufficient against 2025-26 Gangrel walls and
  Organized Resistance Anarch decks. Current trend notes (2026): allies down overall, but Nephandus
  and Hecata zombies/wraiths on the rise.
- **Name the mechanics before the archetype.** ~40% of TWD decks fit no labeled archetype (they
  land in classification.json's `noise` list), and novel/emerging lists are the common assignment.
  Read bottom-up — engine, modules, copy counts — and let identity fall out of that; a known
  archetype is one line of orientation, never a label to force. In case D the pull to call an
  Underbridge Stray ally-swarm a “War Ghoul variant” (shared clan, Fame/Dragonbound, AUS defense)
  buried that it is a different deck with a different engine.
- **A successful block always leads to combat** (rules digest: “Block: Successful attempt to
  prevent an action. Leads to combat.”). A 0-strength ally blocking a bleed does not avoid the
  strike — it enters combat and *survives* on its life, which is exactly why body count and
  life-boosters (Tainted Spring's +1 life, Vagabond Mystic) carry the wall. Never call a small
  blocker “damage-free” or a bleed-block “combat-free.”

**Economy and defense**

- **A&B economy is table stakes, not a finding.** Every competitive deck arranges to act (multiple
  times if possible) and still defend on the opponents' turns (wakes, unlock effects) without
  holding actions back. Don't present it as a deck's distinguishing strength; instead flag the
  *exceptions* (a deck that forgoes it) or unusually cheap ways of achieving it.
- **Bloat-as-sole-defense is a deliberate archetype variant**, not an oversight. Signature: zero
  wakes, zero bounce, heavy leech with a refill loop (e.g. Minion Tap ×7 + Voter Captivation ×8:
  tap each vampire down to 2-3 blood, refill via passed referendums, tap again). Such a list is
  all-forward; its S:CE (e.g. Force of Personality) exists to be cycled, not to hold a line.
- **Bounce is the core anti-bleed defense and a tempo weapon**: a bounced bleed *uses the
  predator's power on the prey*. A deck with reliable bounce doesn't need to open by rushing
  backward — it can spend its aggression disabling the prey's defense instead.
- Copy counts encode the game plan. Info Highway ×5 + Minion Tap ×7 aims at 3-4 big vampires out,
  not 2. Doubling a unique (New Carthage ×2) marks a card the deck *must* land early. A 1× Barrens
  next to Dreams of the Sphinx marks deliberate anti-jam support for a deliberately tight module.
- **Weight focus by how often you'll draw the card.** A single one-off with no fetch is an
  *opportunity* (lunge tool, situational answer), not a core component — don't build the plan on
  it (Frontal Assault ×1 in case D is a single-prey lunge, not the engine). A 1× crypt card is not
  a designated role without a fetch (open without it ~2/3 of games); only the 3-4× star is. Doubled
  *permanents* (The Unmasking ×2, Vagabond Mystic ×2) are near-certain to be drawn and mark
  deliberate structure.
- **Distinguish the engine from its pieces.** Madness Network and Enkil Cog grant out-of-turn
  actions — they are engines. Metro Underground, Mylan Horseed or Homunculus only *unlock*:
  necessary for off-turn play and good A&B support, but a piece, not the engine. Attribute a
  combo's power to the card that grants the effect, not to its enablers.

**Politics**

- The point of playing a political deck is **freedom of damage distribution = table control**.
  Default KRC split: 3 on prey + 1 on **predator**. Hop to the grand-prey when the prey dies this
  turn anyway. Occasionally pay points cross-table — even conceding a VP — to avoid sitting next
  to an unmanageable deck; combat and wall decks are worth removing early, even cross-table, to
  secure the end table.
- Anti-swarm votes (Anarchist Uprising, Ancilla Empowerment) are also the **highest total
  bead-removal** in the game: 10+ counters off the table ≈ 2-3× a KRC. They advance the game even
  with no swarm present.
- Permanent-intercept allies (The Unmasking + Carlton Van Wyk / Ponticulus / legionnaires) force
  stealth onto **votes** too — a reason vote decks carry stealth. Force of Personality superior
  (non-zombie allies cannot block; vampires pay 1 blood to block) is targeted tech against exactly
  this, supplementing permanents like Monastery of Shadows and Creepshow Casino.

**Combat**

- **Rush is a table-control tool, not a win plan.** Targets: bouncers (to open the prey), blockers,
  the predator's key combatant, a cross-table menace. "Disable the whole table" is a poor (or at
  least very difficult) strategic goal; pool damage still has to come from somewhere.
- Analyze a combat module's **internal synergy**, not just its card list: what sets up what
  (Immortal Grapple shuts off S:CE *and dodges*, so the big strikes land); which aim/range cards
  pair (Target Vitals is the piece that couples with ranged Thrown Gate); what the win-the-round
  finishers need (Disarm and Pulled Fangs land easily behind dodge + additional-strike tools);
  what sustains the grind (Taste of Vitae). Pulled Fangs keeps a torpored vampire down *without
  diablerie* — threat management with no blood-hunt exposure.
- **Weakness claims must be posture-aware.** An S:CE-heavy *prey* is only a problem for a deck
  whose plan requires winning combats; if combat is table control and the payload is bleed, enemy
  S:CE on a non-wall is irrelevant. A heavy-S:CE *wall* (2025+ Gangrel) is the real matchup issue.
- **Evaluate a combat line against the defender's standard answers, not in a vacuum.** A
  strike-based plan (Entombment, Disarm, torpor lines) must actually *resolve*: S:CE resolves
  before every other strike (rules digest, Strike Effects) and preempts it entirely; Immortal
  Grapple locks the opponent to hand strikes, so non-hand strikes can't even be played. Before
  crediting a combat line in a matchup, ask what that opponent's archetype does in combat.
- **Swarm attrition is a legitimate S:CE answer.** Disposable bodies sent in series eat the
  S:CE, then the dodge, until a strike lands — numbers go *through* combat defense that would
  wall out a single attacker. When a deck fields many cheap combat-capable minions, don't score
  its combat by one-on-one exchanges.
- **Check whether a disciplineless card package is disciplineless on purpose.** A weapon/combat
  suite with no discipline requirement may exist precisely so *allies* can wield it — who wields
  the module matters as much as what's in it. (Blocking always leads to combat: an ally blocker
  doesn't dodge the fight, it just has to survive it — which is what its life total is for.)
- Even 1-2 points of occasional stealth on a bruise-and-bleed payload (Power of One, An Anarch
  Manifesto) transforms the lunge: the prey needs actual intercept, not just bodies, so you don't
  need to disable *all* their minions before going in.
- **A disciplineless combat package can be deliberate armament for allies.** Allies play any card
  with no Discipline requirement — the rulebook's own combat example is an Underbridge Stray
  striking and being struck. When an ally-swarm deck runs Weighted Walking Stick / Target Vitals /
  Glancing Blow / Lucky Blow / Pulled Fangs, the *allies* are the fighters, not the crypt; check
  who the package is built for before assigning combat to the vampires. Such a swarm rushes through
  S:CE and dodge by attrition (Haven Uncovered ×4 marks one target; the first ally eats the
  combat-end, the next the dodge, the third lands and collects presses), so enemy S:CE is not the
  weakness it is for a single striker.

## Case study A — Lutz Politics (Kelly Schultz, "Platonic Vote", NAC 2023, TWDA 10735)

Archetype: stealth bleed & vote, Malkavian group 4-5 big caps. See
`templates/archetypes/top-tier/lutz-politics.{html,json}`.

Analysis that held up:

- Engine: Info Highway ×5 / Zillah's Valley ×5 accelerate cap-11 Inner Circles; Minion Tap ×7 over
  Villein (post-errata Villein caps at 5 — wasteful on cap 11). Refills: Dmitra's built-in
  referendum, Honor the Elders, Voter Captivation superior.
- Lutz's ping (prey burns 1 pool per passed referendum) turns *every* utility vote — Banishment,
  Disputed Territory, Undele's recursion referendum — into prey damage; vote diversity is
  simultaneously Delaying Tactics insurance, toolbox flexibility, and payload.
- Crypt cohesion: Orlando doubles votes, Stavros swings the 3-vote Prisci Block, Undele recursion,
  Dmitra refill, ICs bleed at 3 (+2 bleed) as the secondary payload.

Owner corrections (the depth that was missing):

- **Forgoing wakes/bounce is Kelly's call, not the archetype**: the archetype normally runs wakes
  and superior AUS bounce. This list is the super-aggressive all-forward variant: bloat so heavy
  it *is* the defense (Tap → VotCap ×8 → Tap loop). Force of Personality as the S:CE fits that: it
  cycles on actions when not needed.
- **Stealth is deliberately tight**, resting on dual-mode cards (FoP, Perfect Paragon: use as
  stealth when needed, cycle on the other mode when not) plus just enough Lost in Crowds /
  Forgotten Labyrinth / Elder Impersonation to avoid jam; The Barrens + Dreams are the anti-jam
  release valves. Tight-but-flexible beats fat-and-jamming.
- **Meta-dating**: 2023 = pre-nerf Emerald Legion everywhere, generally low intercept. The
  full-forward choice is *allowed* by the (bleed-light) meta; the real meta choice is tight
  stealth with an anti-ally angle (FoP superior vs The Unmasking ecosystems). Probably not enough
  stealth for the 2025-26 wall-heavy meta.
- **Banishment** = removal (high-intercept blocker, dangerous rusher, or the prey's bouncer before
  an IC bleed turn) and vote amplifier (strip the lone vampire before Ancient Influence).
- KRC distribution conventions: see General lessons (3+1 predator default, hop, cross-table buys).

## Case study B — Illegal Brawl (Darby Keeney, "Alpha Beta", Origins 2024, TWDA 11440)

Archetype: Anarch Brujah Barons toolbox (bruise & bleed), all group 6, POT/CEL/PRE. See
`templates/archetypes/top-tier/illegal-brawl.{html,json}`.

Analysis that held up:

- The deck's engine is **modality**: Illegalism (bleed 2, free thanks to cel unlock on success),
  Line Brawl (block-or-rush ultimatum / bleed / pool steal), Power of One (+1 bleed *outside* the
  limited-modifier rule, or stealth), three-way combat cards. Nearly every card has a live mode in
  any table state — the toolbox ideal achieved within single cards.
- Line Brawl [cel] pool steal ignores bleed defense entirely (no bounce, no reduction): the
  bounce-proof mode of the payload. Also the right mode when a bounced Carthage-boosted bleed
  would land on the grand-prey and help the prey.
- Latent vote presence: a board of Barons (+New Carthage) carries ~10 votes of cross-table vote
  deterrence, and tactical rushes on opposing big voters can switch a political deck off.

Owner corrections:

- **Bait and Switch ×6 is the core of the deck's viability, not a meta concession** (the
  concession was Organized Resistance). The Baron-up-and-ready loop (Illegalism unlock, Aline,
  Powerbase: LA, Organized Resistance) exists to guarantee a Bait each predator turn: with bounce
  as backbone the deck never has to rush backward first, and the predator's bleeds become prey
  damage. Aggression then goes to disabling the *prey's* bouncers.
- New Carthage matters primarily as a **bleed** enhancer (+1 on all titled Brujah); the votes are
  gravy. Hence ×2 of a unique.
- Combat module synergy (was under-analyzed): Immortal Grapple turns rushes lethal (no S:CE, no
  dodge → Dust Up +2 lands); Dust Up's cel mode is dodge-and/or-strike; Diversion gives extra
  strikes or — for the `for` minority (Saku, Leumeah) — prevention, which is excellent; Bollix
  covers maneuver/press; Target Vitals is the only damage piece that pairs with ranged Thrown
  Gate; Disarm is easy to land behind these and a great threat; Pulled Fangs (a Darby favorite)
  locks a serious threat in torpor without diablerie; Taste of Vitae funds the grind.
- Weakness corrections: S:CE-heavy prey only matters as a *wall* matchup (2024-25 Gangrel wall is
  real — the answer is constant bleed pressure plus Grapple on the key defenders). Gun/range
  modules are the genuine concern, and not only guns: 2024 Banu Haqim combat maneuvers to long
  range to steal with Hunger of Marduk — Thrown Gate + Target Vitals + Bollix maneuvers keep the
  deck on par. Power of One / Anarch Manifesto stealth is *key to the payload*, not a curiosity.

## Case study C — "LaSombra - Gago" (Gustavo Gago, Paulistão Conclave 2023, TWDA 10917)

First blind run of the strategist agent. Owner grade: "very sound", one correction.

- Held up: OBT stealth-bleed wearing the *Reign of Lasombra* label with the vote plan subtracted;
  Charles Delmare as the engine vampire (scarce superior DOM); Capitalist ×4 funding the
  per-turn modifier spend; deliberate ×3/×3/×3 crypt redundancy; thin bloat = no plan B; the
  Deflection-mirror caution (a bounced bleed feeds the grand-prey).
- **Owner correction — the Entombment → Graverobbing/Amaranth line was over-credited.** It does
  not work against S:CE walls (classic Gangrel Resistance): combat-ends resolves before every
  other strike, so the torpor strike never lands. It is equally ineffective against POT Immortal
  Grapple decks: Grapple restricts the opponent to hand strikes, and Entombment is not one. The
  line is real only against decks with neither answer — see the general lesson on evaluating
  combat lines against the defender's standard answers.

## Case study D — "Compromise" (Darby Keeney, Midwest Mayhem Madison 2025, TWDA 12149)

Hard blind test: a noise-classified one-off chosen because the plan is not obvious from a
surface read. The first pass identified all the pieces but misassembled them; owner corrections
produced the right read. The definitive example of "accurate parts, wrong whole".

- First pass, right: Underbridge Stray ×11 + Tainted Spring ×8 (a card in no other TWDA deck) as
  the core; the Stray's triple duty (bleed-blocking wall, wake battery via burn-to-unlock, press
  fuel); slow, low-pool-pressure clock; Fame + Dragonbound as the torpor→pool payload; correct
  2025 meta-dating; found the noise classification and treated it honestly.
- **Miss #1 — who wields the weapons.** The combat package (Weighted Walking Stick, Target
  Vitals, Lucky Blow, Glancing Blow, Pulled Fangs) is deliberately disciplineless so the pumped
  3-life/2-strength Strays fight with it *themselves*. This is an ally-swarm combat deck; the
  vampires (Ludmijla ×4 hub) are support — stealth to land recruits, ANI/AUS/VIC cover. Reading
  it as "wall + vampire combat sub-plan" missed what the core was for.
- **Miss #2 — attrition IS the S:CE answer.** Haven Uncovered ×4 marks the target; Strays
  descend in series — the first eats the S:CE, the second the dodge, the third lands the weapon
  strike with presses fed by the others; Vagabond Mystic ×2 heals the survivors. "Fails against
  S:CE walls" was exactly backwards: going through combat defense by disposable numbers is the
  design.
- **Miss #3 — over-weighted one-ofs and archetype-fitting.** Frontal Assault ×1 is an
  opportunistic lunge, not a payload engine; 1-copy crypt vampires got invented "designated
  roles" they can't reliably play (seen ~1/3 of games, no fetch); and the War Ghoul lineage
  deserved one orientation line, not the spine of the analysis.
- Reviewer catch (FACT): "an ally blocking a bleed → no combat ensues" is false — a successful
  block always leads to combat. The Stray blocker survives the hand strike instead of avoiding
  it; the corrected mechanism makes Tainted Spring's +1 life *more* load-bearing, not less.
- **Owner closure — the bleed is a real secondary clock.** The main plan is the rush, but a
  working rush still needs an oust: Dragonbound + Fame + direct bleeds from the vampires are the
  ousting package once the prey's board is down. The deck *accrues* this clock as the swarm
  strips the board — it does not pivot to it. A removal plan without its finishing clock is
  incomplete — always identify both.
