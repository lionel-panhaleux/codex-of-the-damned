# VTES Rules Reference

## Object of the Game
Accumulate Victory Points (VP) by ousting rival Methuselahs. Pool = main currency. Methuselah with 0 pool is ousted. Most VP wins; ties have no winner.

## Deck Construction
- Crypt: min 12 cards, no max. Library: 60-90 cards.
- Any number of copies of a card allowed within limits.
- Crypt must use vampires from 1 group or 2 consecutive groups. Group "ANY" ignores restriction.

## Counters
- Pool, blood, life are same counters named by location: pool (on Methuselah), blood (on vampire), life (on ally/retainer).
- Moving counter between locations changes its name. Burning/paying returns to blood bank. Gaining comes from blood bank.
- Blood bank is inexhaustible.

## The Edge
Token representing temporary advantage. Starts uncontrolled in central area.

## Turn Sequence
Clockwise from first Methuselah. Each turn has 5 phases:
1. **Unlock Phase** - Unlock all cards. Resolve "during unlock phase" effects (order chosen by controller). Edge holder may gain 1 pool.
2. **Master Phase** - Take master phase actions.
3. **Minion Phase** - Minions perform actions; can be blocked, leading to combat.
4. **Influence Phase** - Use transfers to gain control of vampires from uncontrolled region.
5. **Discard Phase** - Discard a card and draw, or play an event card.

# Card Types

## Crypt Cards
- **Name:** Unique. Only one copy in play at a time (others contest).
- **Capacity:** Red circle number = age/pool investment/max blood. Higher capacity = older. Blood exceeding capacity drains to blood bank immediately.
- **Uncontrolled vampire:** Has pool counters stacked on it. When stack >= capacity during influence phase, move to ready region (excess drains).
- **Clan:** Symbol on attribute bar. Some cards require/affect specific clans.
- **Disciplines:** Symbols on attribute bar. Square = basic level (plain text effect). Diamond = superior level (may use basic OR superior/bold effect, not both).
- **Multi-Discipline cards:** See Requirements for Playing Cards.
- **Group:** Number restricting crypt construction. Does not restrict stealing vampires through play.
- **Advanced cards:** Have Advanced icon under clan icon. Can be influenced normally or merged with base vampire (see Influence Phase - Advanced).

## Library Cards

### Master Cards
Played by Methuselahs, no icon on attribute bar. Two categories:
- **Regular:** Played during master phase as master phase actions.
- **Out-of-turn:** Played during other Methuselahs' turns, consuming a master phase action from your next master phase. Max 1 out-of-turn master between your turns, even if you regain actions. Cannot play on your own turn. Cost counts even if cancelled.

Master card in play controlled by Methuselah who played it, even if on another Methuselah's card.

**Subtypes:**
- **Location:** Stays in play, usable repeatedly including turn played. Can be burned by effects.
- **Trifle:** On successful play, gain 1 additional master phase action (out-of-turn trifle: gain action in next master phase). Max 1 trifle bonus per master phase; subsequent trifles act as regular.
- **Discipline:** Played on controlled vampire. Gives basic level of new Discipline or upgrades basic to superior. "+1" in red circle means also +1 capacity (no automatic blood for new capacity).
- **Trophy:** Put into play with master phase action. No effect until moved to a vampire. Then controlled by vampire's controller; cannot be re-awarded.

### Minion Cards
Played by minions (vampires and allies). Minion card in play controlled by controller of minion it's on; if not on a controlled card, controlled by Methuselah who played it.

**Types (card can be multiple types):**
- **Action:** Ready unlocked minion plays to perform a non-default action. One action card per action. Cannot modify other actions.
- **Action Modifier:** Acting minion plays to modify their action before resolution. Same action modifier cannot be played twice per action (even at different Discipline level). Some played by "other than acting minion" = same controller's minions only.
- **Ally:** Put into play with starting life from blood bank. Acts independently of recruiting minion.
- **Equipment:** Put into play on acting minion. Burned when bearer is burned.
- **Retainer:** Put into play on acting minion with starting life from blood bank. Burned when last life burned or employer burned.
- **Political Action:** Call referendum as action, or burn during referendum for 1 vote. Only vampires can play.
- **Combat:** Played by minions in combat.
- **Reaction:** Ready unlocked minion plays in response to action by minion of another Methuselah. Same reaction card cannot be played twice per action (even at different Discipline level). Does not lock the playing minion.
- **Reflex:** Cancel specified card played against the minion as it is played.
- **Event:** Played as discard phase action. Each event playable only once per game. Controlled by Methuselah who played it.

### Playing a Card
Announce effects, show card, place in ash heap on resolution. "Put into play" cards go to play area. Action cards are temporarily out of play between play and resolution. Some effects cancel cards "as played" - only these and wake effects allowed during that window. Drawing replacement comes after.

### Drawing Cards
Play a card from hand -> draw replacement from library. Empty library = no draw but continue playing. Hand size default = 7. Hand size changes -> immediately draw up or discard down.

### Requirements
- Clan/Discipline symbols on attribute bar = requirements to play.
- Red drop number = blood cost (vampire must have enough blood).
- White diamond with skull = pool cost (Methuselah must have enough pool).
- Costs paid only with own resources. Minions can access controller's resources (e.g., discard from controller's hand).
- Optional cost reducers usable when played or upon resolution. If card cancelled, reducer not used.

### Targeting
Target must be in play (controlled). Vampires in torpor are eligible targets. Uncontrolled vampires and contested cards are not eligible targets. Targeting a card attached to another does not target the latter.
Sets of counters on a card/Methuselah are never targeted directly; targeted via the card/Methuselah. If not enough counters, affect as many as possible.

### Sequencing
Acting Methuselah plays first (has "impulse"). After playing effects, may play more. Once finished, impulse passes: directed at single Methuselah -> defender first; directed at multiple -> those Methuselahs clockwise; undirected -> prey then predator. Then other Methuselahs clockwise. If any Methuselah uses a card/effect, acting Methuselah gets impulse back.

### Wording Templates
- **"During X, do Y":** Only one Y per X with this card.
- **"Lock X to do Y":** Requires unlocked minion. Cannot be used by locked minions.
- **"Search":** No announcement required. Can fail to find. Shuffle library/crypt afterward.
- **"Cancel a card":** Cancelled card has no effect but is still considered played. Cancelled action card: minion doesn't lock, can replay same card. Cancelled non-action card: cost paid normally. Cancelled combat strike card: must choose another strike.

## Golden Rule
Card text overrides rules.

# Detailed Turn Sequence

## 1. Unlock Phase
Unlock all cards. Then resolve "during unlock phase" effects in chosen order. Edge holder may gain 1 pool.

**Burn Option:** A Methuselah not controlling a minion meeting card requirements (or not a legal target) may discard one burn-option card during ANY Methuselah's unlock phase and replace it. Limit 1 per unlock phase.

**Contested Cards:** Unique cards (all crypt cards are unique). If multiple copies of same unique card in play, all are turned face down (out of play). Contest cost: 1 pool per unlock phase. May yield instead (yielded card burned with everything on it). If all others yield, card unlocks face up next unlock phase. Cannot voluntarily contest with yourself (incoming copy burned).

**Contested Titles:** Some titles are unique (prince/baron of a city, clan justicar, clan Inner Circle, regent). Contested title = vampires treated as untitled but remain controlled and can act/block. Contest cost: 1 blood per unlock phase; may yield (or forced to yield if no blood). Only ready vampires contest; torpor vampires must yield. Yielded title = lost permanently.

## 2. Master Phase
Default: 1 master phase action. Can play master cards or use alternate effects. Order of effects/actions chosen by you. Unused actions are lost. If you played an out-of-turn master card since your last master phase (even if cancelled), you get 1 fewer action.

## 3. Minion Phase
Ready unlocked minions perform actions. Acting locks the minion. Action must resolve before next action. Minion that unlocks during this phase can act again.

**Mandatory actions** must be performed before non-mandatory ones. Vampire with 0 blood must hunt (mandatory). Minion with 2+ different mandatory actions or an impossible mandatory action is "stuck" (cannot act, doesn't block others).

**Same-action restrictions:** Cannot perform action with same named action card more than once per turn. Cannot use same copy of card in play (including own card text) for action more than once per turn.

### Bleed
- **Who:** Any ready minion. Max 1 bleed action per turn per minion.
- **Cost:** None.
- **Target:** Prey (directed). Some effects allow/force bleeding another Methuselah. Cannot bleed yourself.
- **Stealth:** 0.
- **Effect:** Target burns pool = bleed amount (default 1). If bleed succeeds with amount >= 1, acting minion's controller gains the Edge.
- **Limited:** Action modifier cannot increase bleed if already being increased by another action modifier (unless one doesn't count against limit). "(limited)" reminder text.

### Hunt
- **Who:** Any ready vampire. Mandatory for vampire with 0 blood.
- **Cost:** None.
- **Target:** None (undirected).
- **Stealth:** +1.
- **Effect:** Gain blood from blood bank = hunt amount (default 1). Excess drains.

### Equip
- **Who:** Any ready minion.
- **Cost:** As listed (from hand); none (from another of your minions).
- **Target:** None (undirected).
- **Stealth:** +1.
- **From hand:** Place equipment on acting minion. No limit on equipment count.
- **From another minion:** Multiple equipment can be taken in one action (announced at action announcement). Failed = equipment stays.
- If equipment requires Discipline and is put into play by other means, use basic version.

### Employ Retainer
- **Who:** Any ready minion.
- **Cost:** As listed.
- **Target:** None (undirected).
- **Stealth:** +1.
- **Effect:** Place on acting minion with starting life. Cannot be transferred between minions. Burned when last life lost.
- If requires Discipline and put into play by other means, use basic version.

### Recruit Ally
- **Who:** Any ready minion.
- **Cost:** As listed.
- **Target:** None (undirected).
- **Stealth:** +1.
- **Effect:** Place in ready region with starting life. Cannot act this turn (unless brought into play by other means). Burned when last life lost.
- If requires Discipline and put into play by other means, use basic version.

### Political Action
- **Who:** Any ready vampire. Max 1 political action per turn per vampire.
- **Cost:** As listed.
- **Target:** None (undirected).
- **Stealth:** +1.
- **Effect:** Calls a referendum (see Politics).

### Leave Torpor
- **Who:** Vampire in torpor.
- **Cost:** 2 blood.
- **Target:** None (undirected).
- **Stealth:** +1.
- **Effect:** Move to ready region. No longer wounded. If blocked: no combat (torpor vampires can't enter combat). Blocking vampire may diablerise; if they decline (or blocker is ally), action fails (vampire stays in torpor, no cost paid).

### Rescue Vampire from Torpor
- **Who:** Any ready vampire.
- **Cost:** 2 blood (payable by acting vampire, rescued vampire, or split between them - exception to own-resources rule).
- **Target:** Vampire in torpor.
  - Same controller: undirected, +1 stealth.
  - Different controller: directed, 0 stealth.
- **Effect:** Rescued vampire moves to ready region (doesn't lock/unlock). No longer wounded. If blocked: normal combat.

### Diablerise Vampire in Torpor
- **Who:** Any ready vampire.
- **Cost:** None.
- **Target:** Vampire in torpor.
  - Same controller: undirected, +1 stealth.
  - Different controller: directed, 0 stealth.
- **Effect:** Victim is diablerised (see Diablerie). If blocked: normal combat.

### Action Card (or Card in Play)
- **Who:** Any ready minion. Same card from hand/in play: max once per turn.
- **Cost/Target/Effect:** As listed on card.
- **Stealth:** 0 unless noted.
- Special version of basic action: all basic action rules apply except as overridden.

### Become Anarch
- **Who:** Any ready untitled non-Anarch vampire.
- **Cost:** 2 blood (1 blood if controller has another ready Anarch).
- **Target:** None (undirected).
- **Stealth:** +1.
- **Effect:** Vampire becomes Anarch sect.

### Allies Acting "as a Vampire"
When an ally plays a card "as a vampire": treated as vampire for all effects generated by that card (including duration effects). Ally's life = blood for costs. Blood gain/loss = life gain/loss. Capacity treated as 1 for card purposes. Life gained in excess of capacity does NOT drain. Aggravated damage burns life normally. Would-be torpor = burned instead. Only treated as vampire for the card's generated effect, NOT for "the vampire with this card" passive effects.

## Action Resolution Summary

**1. Announce:** Define all details (target, cost, effects). Play action card (set aside out of play). Lock acting minion. Cards played "as action is announced" before regular action modifiers/reactions. Exception: referendum terms chosen only after action succeeds.

**2. Block Attempts:**
- **Directed action** (targets other Methuselah(s) or their stuff): Only targeted Methuselahs' ready unlocked minions can block. Multiple targets: clockwise order.
- **Undirected action:** Prey blocks first, then predator.
- Political actions are always undirected.
- Minion can attempt to block multiple times if no other minion is already blocking.
- Failed attempt -> another can be made. Decision not to block further is final.
- If action target changes (e.g., bleed redirect), block attempts reopen.
- Block succeeds if blocker's intercept >= acting minion's stealth.

**Stealth/Intercept:**
- Default: 0 stealth, 0 intercept.
- Stealth added only when currently blocked with sufficient intercept.
- Intercept added only when acting minion's stealth exceeds blocker's intercept.
- All modifications persist for action duration then reset.
- Stealth/intercept can go below 0.

**Detailed action flow:**
- A. No current block attempt: sequencing applies; blocking Methuselah can declare block attempt; passing = no more block attempts unless target changes; all pass -> C.
- B. Ongoing block attempt: sequencing applies; target cannot change; only blocking Methuselah can force current blocker to attempt; all pass -> resolve: success = action blocked, otherwise -> A.
- C. All blocks declined: sequencing applies; target change -> A; all pass -> action resolves.

Action modifiers (acting minion only) and reaction cards (other Methuselahs' ready unlocked minions only) playable anytime before resolution. Same minion can't play same card twice per action.

**3. Resolution:**
- **Successful:** Pay cost, apply effects.
- **Blocked:** Action card burned. Block resolution (simultaneous): blocker locks + combat with acting minion. If effect ends action before block resolution, neither consequence occurs. Action effects don't happen. Action costs not paid. Action modifier/reaction costs always paid when played.

## Politics

### Referendum
Called when political action succeeds. Three steps:
1. **Choose terms** of referendum.
2. **Polling:** "Before votes" effects first. Then all Methuselahs cast votes/ballots freely, any order. Cast votes cannot be changed. All votes/ballots from a single source must agree (all for or all against).
3. **Resolve:** More for than against = passes. Tied = fails.

### Gaining Votes
- **Political action cards:** Each Methuselah may burn 1 political action card for 1 vote (max 1 per Methuselah). Card used to call referendum provides 1 vote to acting vampire's controller.
- **Titled vampires (ready):** Primogen=1, Prince/Baron=2, Justicar=3, Inner Circle=4.
- **The Edge:** Burn Edge for 1 vote.
- **Other cards:** Action modifiers (acting minion), reaction cards (other Methuselahs' ready unlocked minions), cards in play.
- Minion's votes/ballots usable only when ready. Lock/unlock status irrelevant for voting.

## Combat
Occurs when action is blocked or caused by card effects. Only ready minions participate. Cannot enter combat with own minions. Lock/unlock irrelevant for combat. Two minions = combatants, each opposing the other. Only combat cards playable during combat. Some combat cards played by minions "not involved in current combat" - ANY Methuselah's minions can play those.

### Combat Round (7 steps)
Acting minion has first opportunity at every step.

**1. Before Range:** Play "before range" cards/effects.

**2. Determine Range:** Default = close. Maneuver changes range. Minions alternate maneuvers (cannot play 2 in a row). No default maneuver; must use card/weapon/effect. Using maneuver from strike card/weapon = choosing strike for round (can't use another strike card/weapon to maneuver). Forced maneuver must be used; optional maneuver may be declined.

**3. Before Strikes:** Play "after range, before strikes" cards.

**4. Strike:**
- Each minion gets 1 strike per round (pair). Choose strike: acting minion first. Sources: combat card, weapon, default hand strike, other effect. If maneuver from strike card/weapon used this round, cannot choose different strike for initial strike.
- Resolve simultaneously (except first strike, combat ends).
- Ranged strikes / "R" damage effective at any range. Most other strikes: close only. Defensive strikes (dodge, combat ends): any range.
- Damage -> burn blood/life (see Damage Resolution).
- If either combatant not ready at any point, combat ends immediately.

**Additional Strikes:** Announced after initial pair resolves. Acting minion decides first. Only minions with additional strikes play strike cards. All additional strikes at same range. Any strike choosable (maneuver restriction doesn't apply). Max 1 card/effect for additional strikes per round "(limited)". If only one minion has additional strikes, they strike alone.

**5. Damage Resolution:**
- **Prevent:** Play damage prevention cards one at a time.
- **Mend (vampires):** Burn 1 blood per unprevented damage. Can burn all blood. If damage > blood, vampire is wounded -> torpor after all damage handled.
- **Allies/retainers:** Burn 1 life per damage. 0 life = burned.

**Environmental damage:** Damage not inflicted by a minion as strike or explicit "this minion inflicts" effect. Cannot be dodged (dodge only protects from opponent's strike).

**Aggravated damage:**
- Cannot be mended. Vampire becomes wounded (goes to torpor) unless prevented.
- Aggravated damage on wounded vampire: burn 1 blood per point to prevent destruction. Not enough blood = vampire burned (not diablerie).
- Mixed normal + aggravated: handle normal first (but prevention can target aggravated first).
- Wounded vampire goes to torpor after all damage handled; if aggravated burns them, straight to ash heap (no torpor).

**Immune to damage:** Unprevented damage from that source inflicted unsuccessfully: no blood/life burned, no wounding, no destruction.

**6. Press:** Continue combat or end. Alternate presses (can't play 2 in a row). Uncancelled press to continue = new round.

**7. End of Round:** Play end-of-round effects. Occurs even if combat ends prematurely.

**Retainers in Combat:** Not normally harmed unless employer burned. Attacker can target opposing minion's retainer with a ranged strike at long range only. Announce intended target with strike.

### Strike Effects
- **Hand Strike:** Default strike. Close range. Damage = strength (vampires default strength 1).
- **Dodge:** No damage dealt. Protects dodging minion and possessions (not retainers) from opposing strike effects. Any range. Effective vs first strike.
- **Combat Ends:** Resolves first (before first strike). Ends combat before other strikes/effects resolve. Any range. Not affected by dodge.
- **Steal Blood:** Move blood/life from target to striking minion. Not damage (can't be prevented). Occurs before mend step (stolen blood usable for mending). Excess drains.
- **Destroy Equipment:** Burn opposing minion's equipment (striker chooses which). Equipment usable until effect resolves. "Destroy weapon" variant.
- **Steal Equipment:** Like destroy but equipment moves to striking minion. Cannot be used during current round. Kept after combat.
- **First Strike:** Resolves before normal strikes. If opposing minion burned/torpored, their strike doesn't resolve. If opposing weapon stolen/destroyed, they lose strike. Both first strike = simultaneous. Combat ends still resolves first. Dodge still works.

## Torpor
Wounded vampires (can't mend damage) go to torpor region. Equipment/retainers/cards stay on vampire.

Torpor restrictions: Can only perform "leave torpor" action. Cannot block or play reaction cards. Can play action modifiers during their actions. Still controlled but not ready. Still unlocks in unlock phase. Cannot vote/cast ballots.

## Diablerie
Only ready vampires commit diablerie. Steps (single unit, no interruption):
1. Move all victim's blood to diablerist (excess drains).
2. Diablerist may take victim's equipment.
3. Victim burned (cards/counters on victim also burned).
4. If victim had higher capacity: controller may search library/ash heap/hand for master Discipline card to put on diablerist, then shuffle/draw. Discipline +capacity doesn't give blood.
5. If victim was Red List: diablerist may receive trophies.

### Blood Hunt
After diablerie, automatic immediate referendum for blood hunt. If passes: diablerist burned. Not an action (can't be blocked, no action modifiers/reactions). Otherwise normal referendum rules.

## 4. Influence Phase
Default: 4 transfers per phase. First 3 turns of game: 1st Methuselah gets 1, 2nd gets 2, 3rd gets 3 transfers. Cannot save transfers.

Transfer costs:
- 1 transfer: move 1 pool from your pool to uncontrolled vampire.
- 2 transfers: move 1 blood from uncontrolled vampire to your pool.
- 4 transfers + burn 1 pool: move vampire from crypt to uncontrolled region.

When uncontrolled vampire has blood >= capacity: move face up to ready region, unlocked. Excess drains. Transfers granted by new vampire not usable this turn.

### Advanced Merge
If you control base or advanced vampire and other version is in uncontrolled region: spend 4 transfers + 1 pool to merge (place advanced on top of base). Counters/cards on controlled vampire remain; counters/cards on uncontrolled version burned. Treated as single card until burned. Existing targeting effects carry over.

Merged: base card text still applies, but capacity/Disciplines/etc. from base ignored. Advanced card applies in full (takes precedence on conflicts). Merged-only effects marked with merged icon. Advanced vampire (merged or not) contests other copies normally.

## 5. Discard Phase
Default: 1 discard phase action. Discard a card and draw replacement. Or play an event card (max 1 event per phase). Each event playable only once per game. Unused actions lost.

# Ending the Game
- Ousted (0 pool): all controlled cards removed from game. Rivals' cards you control returned at game end. Your cards others control stay in play.
- Prey ousted (by anyone): gain 1 VP + 6 pool. Exception: if ousted simultaneously with prey, gain VP but not 6 pool.
- Last Methuselah remaining: +1 VP.
- New prey = next Methuselah to left.
- Most VP wins. Tie = no winner.

### Withdrawal
If library empty and less than full hand at turn start: may announce withdrawal during unlock phase. Conditions until next unlock phase: no minion combat, no blood/life lost or spent, no pool lost or spent. Success = 1 VP (predator gets no VP/pool). Fails if any blood/pool lost even if also gained.

# Vampire Sects
Vampire belongs to exactly one sect. Changing sect = leave old, join new.

Max 1 title per vampire. Gaining new title = lose old (even if demotion). Contested title + gain new title = immediately yield contested.

Title requires appropriate sect. Wrong sect/clan = lose title benefit (but keep title unless new title gained or contested, which forces yield).

## Camarilla
Titles: primogen (1 vote, not unique), prince (2 votes, unique per city, contested by same-city titles), justicar (3 votes, unique per clan, clan-only), Inner Circle (4 votes, unique per clan, clan-only).

## Anarch
Some vampires are Anarch by default. Untitled non-Anarch vampire can become Anarch (see Become Anarch action). Being Anarch = sect; no inherent game effect except as defined by cards.

Baron: Anarch-only title, 2 votes, unique per city. Contested by prince/archbishop/baron of same city. Losing Anarch sect = lose title benefit until Anarch again.

## Independent
Vampires not in any major sect. Some start with votes (card text); treat as having titles of their own, not tied to a sect.

# Legacy Sets
Rules below from pre-Fifth Edition sets. Fully compatible.

## Sabbat
Titles: bishop (1 vote, not unique), archbishop (2 votes, unique per city, contested by same-city titles), priscus (see Prisci Block below), cardinal (3 votes, not unique), regent (4 votes, unique).

**Prisci Block:** Prisci collectively have 3 votes. Sub-referendum: each ready priscus = 1 ballot (votes cannot be used). Majority side gets 3 votes in main referendum. Tie = prisci abstain. All votes/ballots from a vampire must agree.

Antitribu clans distinct from non-antitribu counterparts. Clan doesn't automatically change with sect change.

## Laibon
Titles: kholo (2 votes, unique per clan, clan-only), magaji (2 votes, not unique).

## Traits
- **Black Hand:** Enables Black Hand cards.
- **Blood Cursed:** Cannot commit diablerie.
- **Circle:** Blood Brother circle designation. No circle = own circle. Inner Circle is not a Blood Brother circle.
- **Infernal:** Doesn't unlock normally. Controller may burn 1 pool to unlock during unlock phase.
- **Flight:** Enables Flight cards.
- **Red List:** Any Methuselah may mark a Red List minion with master phase action (current turn). Ready vampires can enter combat with marked Red List as +1 stealth directed action costing 1 blood (once per vampire per turn). Burning Red List in combat or directed action (including diablerie): controller may search library/ash heap/hand for master trophy card for that vampire, shuffle/draw. Other unawarded trophies in play may be moved to this vampire. Done before blood hunt referendum.
- **Scarce:** When moved to ready region, controller burns 3 pool per vampire of same clan they already control.
- **Slave:** Slave to specified clan. Cannot perform directed actions if controller has no ready member of that clan. If clan member (same controller) is blocked, controller can lock slave to cancel combat, unlock acting vampire, and have slave enter combat with blocker instead.
- **Sterile:** Cannot perform actions to put new vampires in play.

# Glossary

**Acting Minion:** Minion performing current action.
**Add:** Blood counters added from blood bank by default.
**Additional Strike:** Extra strike in same round, same range as initial.
**Aggravated Damage:** Unmendable damage; can burn wounded vampires. Allies/retainers treat as normal damage.
**Ash Heap:** Discard pile. Actions targeting ash heap = undirected.
**Assamite:** Banu Haqim.
**Attached:** Card put on another card = both attached to each other.
**Bearer:** Minion equipment is on. "Bearer with X" = only that type can use.
**Bleed:** Action burning target Methuselah's pool. Default target: prey.
**Block:** Successful attempt to prevent an action. Leads to combat.
**Blood Bank:** Inexhaustible counter repository.
**Blood Hunt:** Referendum to burn a diablerist.
**Burn:** Card -> owner's ash heap. Counter -> blood bank. Burned/removed-from-game card: everything on it also burned.
**Capacity:** Max blood on vampire; relative age measure.
**Combatant:** Minion in combat.
**Combat Ends:** Strike ending combat before other strikes resolve.
**Contest:** Struggle for unique card/title control.
**Crypt:** Vampire card deck.
**Diablerie:** Burning vampire in torpor by drinking blood. May gain Discipline.
**Directed Action:** Action targeting other Methuselahs or their cards/minions.
**Discard:** Card from hand to ash heap.
**Dodge:** Strike protecting minion (not retainers) from opposing strike.
**Draw:** Library cards -> hand. Crypt cards -> uncontrolled region.
**Edge:** Token for current advantage holder.
**Environmental Damage:** Damage not from a minion.
**Equipment:** Object giving minion bonus/ability.
**Employer:** Minion a retainer is on.
**Event Card:** Library card playable as discard phase action.
**First Strike:** Resolves before normal offensive strikes.
**Follower of Set:** Ministry.
**Hunt:** Vampire action to regain blood.
**Impulse:** Opportunity to play next card/effect (see Sequencing).
**Intercept:** Block succeeds if >= stealth. Playable only when needed.
**Library:** Master/minion/event card deck.
**Life:** Retainer/ally health token.
**Limited:** Bleed increase and additional strikes each limited to 1 source "(limited)".
**Lock:** Turn card sideways.
**"Lock X to do Y":** Cannot be used under wake effect. "Lock X. Do Y." CAN be used under wake.
**Maneuver:** Change range in combat.
**Master Phase Action:** Methuselah's personal activity.
**Minion:** Vampire or ally.
**Minion Card:** Library card that is not master or event.
**Monster:** Any minion/retainer that is neither mortal nor animal. Vampires are monsters.
**Opposing Minion:** The other combatant.
**Out-of-Turn Master Card:** Played during another's turn; uses next master phase action. Max 1 between your turns.
**Performing an Action:** From announcement to resolution.
**Polling:** Vote-casting step of referendum.
**Pool:** Methuselah's influence tokens. 0 pool = ousted.
**Predator:** Methuselah to your right.
**Press:** Continue or end combat.
**Prey:** Methuselah to your left. Ousting prey = 1 VP + 6 pool.
**Reaction Card:** Played by ready unlocked minion in response to another Methuselah's minion's action.
**Ready Minion:** In ready region; can act and block.
**Referendum:** Political action resolution: terms, votes, effects.
**Retainer:** Serves a minion. Cannot act independently. Cannot transfer.
**Sect:** Clans have no default sect. Clan change keeps sect. New vampires default to sire's sect.
**Sire:** Vampire performing action to put new vampire in play.
**Steal (card):** Take permanent control. Stays in same region. Attached card moved to same-type card you control.
**Stealth:** Exceeds intercept = block fails. Playable only when needed.
**Strength:** Hand strike damage (default 1 for vampires).
**Strike:** Combat effort to harm opponent or avoid harm.
**Target:** Card/Methuselah affected by effect. Must be in play. Torpor vampires eligible. Uncontrolled/contested not eligible.
**Thaumaturgy:** Blood Sorcery.
**Title:** Title card is placeholder. Yielded/lost = card burned. Unique title contests paid with blood.
**Torpor Region:** Wounded vampires placed here. Vulnerable to diablerie. Not ready but controlled.
**Transfer:** Influence phase action for pool/vampire movement.
**Unique:** Only 1 copy in play. Duplicates -> contest.
**Unlock:** Restore card to upright position.
**Victory Point (VP):** Ranking measure. 1 VP per ousted prey + 1 VP for last standing. Most VP wins.
**Wake:** Vampire can attempt to block and/or play reaction cards as though unlocked for action duration. Wake effects playable during "as played" window for other reactions. Reaction that unlocks without waking is NOT a wake effect.
**Withdraw:** Leave game attempt when library empty.
**Wounded:** Vampire with unmended damage, or in/heading to torpor.

# Appendix: Imbued

## Imbued
Crypt cards counting as mortal allies, not vampires. Default: 1 strength, 1 bleed. Cost = starting life (like capacity). Have creeds (like clans), virtues (like Disciplines, one level only). At 0 life: incapacitated (not burned). "Burn ally" effects still burn imbued.

## Conviction
Card type played during unlock phase (not master/minion/event). 1 conviction per imbued per unlock phase, playable from hand or ash heap. Imbued entering play with no conviction may gain 1 from library/hand/ash heap. Conviction can be spent (burned) for conviction costs. Max 5 conviction per imbued; excess burned.

## Power
Minion card type, imbued only. Gained as +1 stealth action (like equipment). Imbued unlocks on success. No duplicate powers. "Always on" effects active even when power card locked. Other effects have card type icon indicating usage; lock power card to use (standard rules apply).

## Incapacitated
0 life = incapacitated region (controlled, not ready). Effects unusable by ally being burned = unusable by imbued being incapacitated. Any minion may burn incapacitated imbued and take equipment as directed action; each ready imbued may burn 1 conviction for 1 unpreventable damage to acting minion. Leave incapacitated: burn 3 conviction during unlock phase, gain 1 life (not exceeding starting life). Leaving by any other effect also gains 1 life (capped at starting life).

## Imbued Card Interactions
If you can see the crypt card (uncontrolled, ash heap, in play, searching crypt), target must match parameters (usually excludes imbued). If targeting "blind" (unseen crypt/uncontrolled card), work with whatever found. "Capacity" comparisons use imbued's cost as capacity.

**Compatible:** Bear-Baiting, Brainwash, Cairo Int'l Airport, Clotho's Gift [obf], Effective Management, Gemini, Gisela Harden, Goodnight Sweet Prince, Innocent Bystander, Kindred Intelligence, Lazar Dobrescu (recipient must be vampire), Memory's Fading Glimpse, Petra's Resonance, The Portrait, San Lorenzo de El Escorial, The Soul Gem of Etrius (retrieves imbued; if "younger" puts in play but no blood/life), The Trick of the Danya (recipient must be vampire).

**Incompatible:** Chain of Command, Clotho's Gift [tem], Dreams of the Sphinx, Illusions of the Kindred (imbued = no combat, removed from play), Might of the Camarilla, Recruitment.
