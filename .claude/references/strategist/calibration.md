# Calibration corpus — owner-graded analyses

Working notes distilling the owner's feedback from graded strategist runs (2026-07). The
**general lessons** are the operating heuristics; the **case studies** keep only the
deck-specific facts and the grading verdicts — every generalizable correction has been folded
into the lessons or into `modules.md`. The bar, set on round 1 ("accurate but a bit shallow"):
module-internal synergy, meta-dating, copy-count intent, posture-aware weaknesses.

## General lessons

**Grounding**

- Never reason from remembered card text. Fetch from the KRCG API
  (`https://api.krcg.org/card/<id-or-name>`) before analyzing. Roughly a third of from-memory
  card readings were wrong in round 1.
- **Read the whole card object, not just `card_text`.** For allies and retainers the *recruit
  requirement* lives in the `clans` / `disciplines` fields, not the ability text (Tunnel Runner →
  `clans:['Akunanse']`; War Ghoul → `clans:['Tzimisce']`; Raven Spy → `disc:['ani']`). Missing it
  inverted a whole advice pass (case F): a "requirement-free" read made the one card that
  bypasses the gate look redundant when it was the deck's only legal recruiter. Check the fields
  before judging who can bring an ally into play (Piper: requirements apply as normal).
- **Date the deck, then read it against its year.** A decklist is a meta answer, not a timeless
  artifact. Check `card-changes-history.md` (what did the card do *then*?) and `meta-by-year.md`
  (what were the top threats *then*?). A 2023 list with tight stealth and anti-ally tech reads
  correctly only against the pre-nerf Emerald Legion, low-intercept 2023 meta; the same package
  is likely insufficient against 2025-26 Gangrel walls. Trend notes (2026): allies down overall,
  Nephandus and Hecata zombies/wraiths rising.
- **Name the mechanics before the archetype.** ~40% of TWD decks fit no labeled archetype (the
  classification's `noise` list), and novel lists are the common assignment. Read bottom-up —
  engine, modules, copy counts — and let identity fall out; a known archetype is one line of
  orientation, never a label to force. Drop the frame the moment the engine diverges: lineage
  must never become the spine of the analysis (case D's "War Ghoul variant" pull buried a
  different deck with a different engine).

**Base mechanics — the free verbs.** The rules give every deck a card-free strategic layer;
card slots only make sense relative to it.

- **The Edge is an economy.** Its holder may gain 1 pool every unlock phase (a quiet 10-15 pool
  over a game), it is a vote, and some cards spend it (Inside Dirt). Track who holds it, who can
  take it (any successful bleed — including a bounced one: the *acting minion's controller*
  gains it), and whether a deck is built to hold or to spend it.
- **Torpor is a cost, not an endgame.** The base recovery loop — leave torpor (2 blood, +1
  stealth) or be rescued (2 blood, split freely), then hunt (free action, 1 blood) — is a
  resilience plan in itself. A deck with no combat defense but thick blood regeneration
  (hunting grounds, Jake Washington-class, The Coven) is reading correctly: the regeneration
  IS the combat defense — accept torpor, refuel on base verbs (owner's read, case E).
- **Every ready minion is a bleed for 1.** The payload floor: width is a clock with zero cards
  in hand, and bouncing a 1-bleed is a losing trade. Swarms pressure a table by existing;
  clearing "weak bodies" is never free for the prey.
- **Hunting prices blood in actions** (base rate: one action per blood). Blood spent is actions
  spent later — hunt-rate improvements and leech loops change that exchange rate, which is
  their real value.
- **A successful block always leads to combat.** A 0-strength ally blocking a bleed does not
  avoid the strike — it enters combat and *survives* on its life, which is why body count and
  life-boosters (Tainted Spring, Vagabond Mystic) carry a wall. Never call a small blocker
  "damage-free".

**Economy and defense**

- **A&B economy is table stakes, not a finding.** Every competitive deck acts and still defends
  on the opponents' turns. Flag the *exceptions* (all-forward builds) or unusually cheap ways of
  achieving it, not the norm.
- **Bloat-as-sole-defense is a deliberate archetype variant.** Signature: zero wakes, zero
  bounce, heavy leech with a refill loop (Minion Tap ×7 + Voter Captivation ×8: tap to 2-3
  blood, refill via referendums, tap again). Its S:CE exists to be cycled, not to hold a line.
- **Bounce is the core anti-bleed defense and a tempo weapon**: a bounced bleed *uses the
  predator's power on the prey*. A deck with reliable bounce doesn't open by rushing backward —
  it spends its aggression disabling the prey's defense instead.
- **Copy counts are hard evidence in both directions — weight focus by draw frequency.**
  5×+7× core = the game plan (Info Highway + Minion Tap aims at 3-4 big vampires, not 2). A
  doubled unique = must land early; doubled support permanents = deliberate load-bearing
  structure; 1× beside a fetch = searchable answer; a bare 1× action = opportunity or lunge,
  never a core engine; a 1× crypt card = toolbox texture, not a designated role, unless
  something fetches or cycles toward it (only the 3-4× star is a role). A 1× anti-jam card
  (Barrens next to Dreams) marks a deliberately tight module.
- **Distinguish the engine from its pieces.** Madness Network and Enkil Cog grant out-of-turn
  actions — engines. Metro Underground, Mylan Horseed, Homunculus only *unlock* — necessary
  enablers, good A&B support, but pieces. Attribute a combo's power to the card that grants the
  effect.

**Politics**

- The point of playing politics is **freedom of damage distribution = table control**. Default
  KRC split: 3 on prey + 1 on **predator**. Hop to the grand-prey when the prey dies this turn
  anyway. Occasionally pay points cross-table — even conceding a VP — to avoid sitting next to
  an unmanageable deck; combat and wall decks are worth removing early, even cross-table.
- Anti-swarm votes (Anarchist Uprising, Ancilla Empowerment) are also the **highest total
  bead-removal** in the game (10+ counters ≈ 2-3× a KRC) — they advance the game with no swarm
  present.
- Permanent-intercept allies (The Unmasking + Carlton Van Wyk / Ponticulus / legionnaires)
  force stealth onto **votes** too. Force of Personality superior (allies cannot block; vampires
  pay 1 blood to block) is targeted tech against exactly this.

**Combat**

- **Rush is a table-control tool, not a win plan** (bouncers, blockers, the predator's key
  combatant, a cross-table menace). "Disable the whole table" is a poor strategic goal; pool
  damage still has to come from somewhere — a removal plan without its finishing clock is
  incomplete, always identify both (case D).
- Analyze a combat module's **internal synergy**, not its card list: what sets up what, which
  aim/range cards pair, what the win-the-round finishers need, what sustains the grind. The
  reference packages and their internal logic live in `modules.md` (Combat section).
- **Weakness claims must be posture-aware.** Enemy S:CE only matters if the plan requires
  winning combats; an S:CE *wall* as prey is a real matchup issue, S:CE on a non-wall is not.
- **Evaluate a combat line against the defender's standard answers.** A strike-based plan must
  *resolve*: S:CE resolves before every other strike and preempts it; Immortal Grapple locks the
  opponent to hand strikes. Ask what that opponent's archetype does in combat first.
- **Swarm attrition is a legitimate S:CE answer.** Disposable bodies in series eat the S:CE,
  then the dodge, until a strike lands (case D: Haven Uncovered marks the target, the swarm
  descends). Don't score a many-cheap-minions deck by one-on-one exchanges.
- **Check who a disciplineless package is for.** Allies play any card with no discipline
  requirement — a disciplineless weapon suite may be deliberate ally armament (case D: the
  Strays are the fighters, the vampires are support). Who wields the module matters as much as
  what's in it.
- Even 1-2 points of occasional stealth on a bruise-and-bleed payload (Power of One, An Anarch
  Manifesto) transforms the lunge: the prey needs actual intercept, not bodies — no need to
  disable *all* their minions before going in.

## Case studies (grading history; corrections generalized above)

**A — Lutz Politics (Kelly Schultz, NAC 2023, TWDA 10735).** Stealth bleed & vote, Malkavian
G4-5 Inner Circles. Held up: the ramp (Info Highway/Zillah ×5 each), Minion Tap over post-errata
Villein on cap 11, Lutz's ping turning utility votes into payload, crypt cohesion. Owner
corrections: wakeless/bounceless is *Kelly's* all-forward variant, not the archetype (which
normally runs wakes + AUS bounce) — the Tap→VotCap×8→Tap loop is the defense; stealth is
deliberately *tight* on dual-mode cards (Force of Personality, Perfect Paragon cycle on their
other mode) with Barrens/Dreams as release valves; the real meta call was anti-ally tech (FoP
superior) in the pre-nerf-Emerald, low-intercept 2023 field — likely not enough stealth for
2025-26; Banishment = removal AND vote amplifier (strip the lone vampire before Ancient
Influence).

**B — Illegal Brawl (Darby Keeney, Origins 2024, TWDA 11440).** Anarch Brujah Barons toolbox,
all G6, POT/CEL/PRE. Held up: modality as the engine (Illegalism / Line Brawl / Power of One /
three-way combat cards — every card live in any table state), Line Brawl's bounce-proof pool
steal, latent Baron vote deterrence. Owner corrections: **Bait and Switch ×6 is the core of
viability** (the meta concession was Organized Resistance) — the Baron-up-and-ready loop exists
to guarantee a bounce each predator turn, freeing aggression for the prey's bouncers; New
Carthage is primarily a bleed enhancer (votes are gravy — hence ×2 of a unique); the combat
module's internal synergy was under-analyzed (now in `modules.md`: POT grapple kit, Marduk
theft-at-range as the 2024 range concern); Power of One / Anarch Manifesto stealth is key to
the payload.

**C — "LaSombra - Gago" (Paulistão Conclave 2023, TWDA 10917).** First blind run; owner grade
"very sound", one correction. Held up: OBT stealth-bleed wearing the Reign of Lasombra label
with the vote plan subtracted; Charles Delmare as engine vampire (scarce superior DOM);
Capitalist ×4 funding the modifier spend; thin bloat = no plan B. Correction: the Entombment →
Graverobbing line was over-credited — dead against S:CE (resolves first) and against Immortal
Grapple (hand strikes only); real only against decks with neither answer.

**D — "Compromise" (Darby Keeney, Midwest Mayhem 2025, TWDA 12149).** Hard test, noise-classified
one-off: pieces right, whole wrong on first pass — the definitive "accurate parts, wrong whole".
Underbridge Stray ×11 + Tainted Spring ×8 (unique to this deck in the TWDA) correctly identified
as the core, but: the disciplineless weapon package is wielded by the *Strays* (ally-swarm combat
deck, vampires are support); Haven Uncovered ×4 + serial Stray attrition IS the S:CE answer;
Frontal Assault ×1 and 1× crypt vampires were over-weighted. Owner closure: the light bleed is a
real secondary clock the deck *accrues* as the swarm strips the board — Fame + Dragonbound +
direct bleeds are the oust. Full engine entry: `modules.md` → Ally-armed combat swarm.

**E — "Esquina da Sujeira" (Fillip CG 2026, TWDA 13252).** First clean pass ("all good") — the
positive anchor. Edge → Inside Dirt engine (bounce-proof 3-pool burns interleaved with Computer
Hacking re-arms), clan gate explaining the mixed crypt, all-forward chassis read as identity,
lineage tuning (Dirt 15→8, Hacking added, wakes dropped). Owner answers: thin raw pool is
exactly why the archetype stays niche — fast alone doesn't win all tables, and no bounce/bleed
defense is a structural drawback vs top-tier S&B (fast AND defended); blood regeneration is the
combat defense (see free verbs); the loop fires multiple times per turn — 4-5 minions is the
goal.

**F — Petaniqua Tunnel Runner brew (advisor mode, VDB draft, 2026-07).** First advice run:
mechanics verification mostly excellent (Piper once-per-turn + dormant recruits + Charisma
excluded by ruling; infernal 1-pool tax; Contagion as bounce-proof pressure; Computer Hacking
as the missing payload), but one inverted recommendation from misreading the card object:
Tunnel Runner requires Akunanse (`clans` field), so advanced Petaniqua's requirement-bypass was
the deck's *only* recruiter, not dead weight — the player's merge plan was right. Lessons:
read the structured fields (Grounding), and when a player's plan looks redundant, check their
premise before overruling it. Merge assembly tools (Legacy / Epiphany): `modules.md`.
