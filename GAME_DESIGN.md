# Lily Pad Luck - Game Design Document

> A cozy, frog-themed roguelike card game for mobile

---

## Concept Overview

**Lily Pad Luck** is a cute, strategic card game where you play as a little frog melding collections of bugs onto lily pads to score points and clear ponds. Inspired by Hand and Foot Canasta's melding and set-collecting mechanics - reimagined as a single-player roguelike - players draw, meld, and complete **Canasta Stacks** of bug cards through a whimsical journey across a magical pond. Each run is different, with charming frog companions, magical lilies, and sparkling rewards.

**Target Audience:** Women 18-35 who enjoy cozy games, casual strategy, and cute aesthetics
**Platform:** iOS & Android (portrait orientation, one-hand friendly)
**Art Style:** Soft watercolor / cottagecore aesthetic with rounded shapes, pastels, and gentle animations
**Tone:** Relaxing but mentally engaging - "a puzzle wrapped in a hug"

---

## Core Loop

```
 Pick a Pond Path --> Draw & Meld Bugs --> Complete Stacks --> Score Ribbits --> Visit Shops/Events --> Repeat
       |                                                                              |
       +--- Each pond has 3 acts (Garden Pond, Mushroom Marsh, Enchanted Lake) -------+
```

### The Hand and Foot Mechanic

Inspired by Hand and Foot Canasta, each round the player receives **two piles of cards**:

- **The Hand** (11 cards) - Your starting cards. Play from these first.
- **The Foot** (11 cards) - A face-down reserve pile. You "hop to your Foot" (pick it up) once your Hand is empty, unlocking fresh cards and a bonus.

**The strategic tension:** You want to empty your Hand quickly to reach your Foot, but you also need to meld wisely. Rushing burns good cards; waiting too long means you run out of turns before completing enough stacks.

### 1. The Deck - Bug Cards

The deck contains **108 bug cards** (two copies of each, like canasta uses double decks). Cards have two properties:

| Property | Values |
|----------|--------|
| **Bug Type** (color/suit) | Firefly (amber), Butterfly (pink), Ladybug (red), Dragonfly (teal), Beetle (brown), Moth (lavender) |
| **Nectar Value** (rank) | 1-12 (Dewdrop, 2-10, Bloom, Petal, Crown) |

**Special Cards:**
- **Wilds - Chameleon Tongue Cards (x6):** Can substitute for any bug type in a meld. Max 2 wilds per meld (unless a Charm says otherwise).
- **Poison Ivy Cards (x4):** Penalty cards. If stuck in your hand at end of round, -100 Ribbits each. Can be discarded with a special action or melded away by certain Charms.

**Visual Design:**
- Fireflies glow with warm amber, cards shimmer gently
- Butterflies have pastel wings with watercolor patterns
- Ladybugs are round and cheerful with polka dots
- Dragonflies have iridescent teal/purple wings
- Beetles have shiny shell textures with earth tones
- Moths have soft, dusty lavender wings with moon patterns

### 2. Melding - Building on Lily Pads

Instead of playing poker hands, you **meld** groups of 3+ matching bug cards onto **lily pads** (the play area). This is the core action each turn.

**Turn Structure:**
1. **Draw Phase:** Draw 2 cards from the Pond (draw pile) OR pick up the top 5 cards of the Discard Pile (the "Puddle") - but only if you can immediately meld the top card.
2. **Meld Phase:** Place melds of 3+ matching bugs onto lily pads, or add cards to existing melds. You can meld as many groups as you want per turn.
3. **Discard Phase:** Discard 1 card to the Puddle to end your turn.

**Meld Rules:**
- A meld needs **at least 3 cards of the same nectar value** (e.g., three 7s of any bug type)
- You can mix bug types within a meld (it's about the number, not the suit)
- Max **2 Chameleon Tongue wilds** per meld
- You must always have more natural cards than wilds in a meld

### 3. Canasta Stacks - Completing a Lily Pad

When a meld reaches **7 cards**, it becomes a completed **Canasta Stack** - the lily pad blooms! This is the primary scoring goal.

| Stack Type | Requirement | Ribbits | Visual |
|---|---|---|---|
| **Natural Bloom** | 7 cards, NO wilds | 500 | Lily pad blooms with golden flowers |
| **Mixed Bloom** | 7 cards, has wilds | 300 | Lily pad blooms with silver flowers |
| **Wild Bloom** | 7 Chameleon Tongue wilds | 1000 | Lily pad blooms with rainbow flowers (very rare!) |
| **Pure Garden** | 7 cards, all same bug type AND same value | 750 | Lily pad blooms with glowing petals (new mechanic!) |

### 4. Round Scoring

A round ends when a player **goes out** (empties both Hand and Foot, with at least 2 completed Canasta Stacks) or runs out of turns.

| Scoring Element | Ribbits |
|---|---|
| Each Natural Bloom | +500 |
| Each Mixed Bloom | +300 |
| Each Wild Bloom | +1000 |
| Each Pure Garden | +750 |
| **Going Out Bonus** | +200 |
| **Hopped to Foot Bonus** | +100 |
| Card values in completed melds | +Nectar value each |
| Cards left in Hand/Foot (penalty) | -Nectar value each |
| Poison Ivy cards left in hand | -100 each |
| **Charm bonuses** | Varies |

**Round Target:** Each round on the pond map has a **Ribbit Goal** (e.g., "Score 800 Ribbits"). Meet or exceed it to clear the round. Failing costs a life (lily petal).

### 5. The Turn Limit & Tension

Unlike traditional canasta (which is multiplayer), Lily Pad Luck uses a **turn counter** to create tension:

- Each round gives you **12-18 turns** (varies by difficulty/act)
- Displayed as lily pads lighting up around a circular tracker
- Charms can grant bonus turns
- The Puddle (discard pile) pickup is risky but powerful - grabbing 5 cards accelerates your melds but you burn a turn on one big draw
- **Going out before the turn limit** awards bonus Ribbits scaled to remaining turns

### 6. Meld Thresholds (Canasta Opening Rule)

Like Hand and Foot, your **first meld each round** must meet a minimum nectar value total:

| Act | Minimum First Meld |
|-----|-------------------|
| Act 1 | 50 nectar total |
| Act 2 | 90 nectar total |
| Act 3 | 120 nectar total |

This prevents dumping low-value cards early and forces strategic planning about when to start melding.

---

## Key Mechanic - Charms

**Charms** are the heart of the strategy. They are collectible magical items that modify melding, scoring, and card draw in creative ways. Each charm is a cute, animated object displayed alongside your play area. You can hold up to **5 Charms** per run.

### Charm Categories

**Frog Friends** - Tiny companion frogs that grant passive bonuses:
- **Rosie** (pink tree frog) - Butterfly cards count as +2 higher nectar value in melds
- **Mossy** (green bullfrog) - Earns 4 Dewdrops every time you complete a Canasta Stack
- **Sunny** (golden frog) - +50 Ribbits for each Firefly in a completed Natural Bloom
- **Bubbles** (blue poison dart frog) - Dragonfly melds only need 5 cards to become a Canasta Stack
- **Violet** (purple rain frog) - Drawing from the Puddle gives you 7 cards instead of 5
- **Bramble** (brown toad) - Poison Ivy cards become worth +50 Ribbits instead of -100 when melded with Beetles
- **Luna** (white tree frog) - Moth cards count as wilds in melds (but stacks still count as Natural Bloom!)

**Pond Trinkets** - Magical items found around the pond:
- **Moonstone Pebble** - Your first meld each round has no minimum nectar requirement
- **Lucky Clover** - +1 to all nectar values across your entire deck
- **Dewdrop Tiara** - +20 Ribbits per Crown (value 12) card in completed stacks
- **Mushroom Cap** - Completed stacks of Ladybugs score double
- **Glass Jar** - Each time you meld Fireflies, store one. At 5 stored, gain a free Wild Bloom.
- **Silk Cocoon** - When you hop to your Foot, draw 3 extra cards
- **Acorn Cup** - +2 bonus turns each round

**Lily Enchantments** - Powerful but conditional:
- **Blooming Lily** - x2 to ALL scoring if you complete 3+ Canasta Stacks in a round
- **Golden Lily** - Natural Blooms score 750 instead of 500
- **Phantom Lily** - When you meld, a ghost copy of one card is added for free
- **Frost Lily** - Freeze the Puddle: discard pile cannot be picked up by bosses (boss mechanic)
- **Twin Lily** - Start each round with your Hand and Foot as identical copies

### Charm Rarity (indicated by sparkle effects)

| Rarity | Border Color | Drop Rate |
|--------|-------------|-----------|
| Common | Soft green | 60% |
| Uncommon | Lavender | 25% |
| Rare | Rose gold | 12% |
| Legendary | Holographic / rainbow | 3% |

---

## Progression - The Pond Map

Each run follows a branching path across a pond, displayed as lily pads connected by dotted lines (like a garden trail). The player taps to choose their next lily pad.

### Lily Pad Types (Node Types)

| Icon | Type | Description |
|------|------|-------------|
| Bug icon | **Bug Catch** (battle) | Meld cards and complete Canasta Stacks to hit the Ribbit Goal within the turn limit. Failing = losing a life (lily petal). |
| Shopping bag | **Frog Market** | Spend Dewdrops on new Charms, card packs, or removals |
| Sparkle | **Enchantment Pond** | Choose 1 of 3 random buffs to your deck or Charms |
| Treasure chest | **Treasure Toad** | Open a chest for free cards or Charms |
| Question mark | **Mystery Mushroom** | Random event - could be good or bad! |
| Boss crown | **Pond Guardian** (boss) | Tough scoring challenge with unique modifiers |

### Acts

| Act | Theme | Rounds | Boss |
|-----|-------|--------|------|
| **Act 1: The Garden Pond** | Sunny, flowers, easy | 6-8 nodes | Heron (bird that eats frogs - score big to scare it away!) |
| **Act 2: The Mushroom Marsh** | Moody, mushrooms, fungi | 8-10 nodes | Snapping Turtle (adds poison cards to your deck) |
| **Act 3: The Enchanted Lake** | Magical, crystals, moonlight | 10-12 nodes | The Storm (weather-based modifiers each hand) |
| **Secret Act: The Fairy Pond** | Unlockable, ethereal | 8 nodes | Mirror Frog (copies your strategy) |

---

## Card Enhancements

Cards can be upgraded at Enchantment Ponds or through Charm effects:

| Enhancement | Visual | Effect |
|---|---|---|
| **Sparkling** | Glitter overlay | +30 Ribbits when part of a completed stack |
| **Gilded** | Gold foil edges | Counts as 2 cards toward a Canasta Stack |
| **Wild** | Rainbow shimmer | Acts as a Chameleon Tongue but doesn't count against Natural Bloom |
| **Lucky** | Four-leaf clover | 1 in 5 chance to duplicate itself when melded |
| **Glass** | Translucent / crystal | +100 Ribbits, destroyed after the round ends |
| **Botanical** | Flower crown on bug | Earns 6 Dewdrops when melded |
| **Magnetic** | Tiny lightning sparks | When drawn, pull another card of the same value from the deck |

---

## Monetization (Ethical & Cozy-Friendly)

**Premium Purchase ($4.99)** - One-time buy, no ads, full game
- Free version: First act playable with ads between runs
- Premium: All acts, no ads, daily charm gift, cosmetic wardrobe

**Cosmetic Shop (optional IAP):**
- Frog skins (outfits for your frog avatar): flower crown, tiny hat, scarf, glasses
- Card back designs: cherry blossoms, stars, mushrooms, rainbows
- Lily pad trail themes: autumn leaves, snow, spring petals
- Pond backgrounds: night sky, rainy day, sunset
- **NO pay-to-win. NO loot boxes. NO energy systems.**

---

## The Frog Avatar

Players customize a personal frog who sits on the main lily pad during gameplay:

- **Species:** Tree frog, Bullfrog, Dart frog, Rain frog, Toad
- **Colors:** Mint, pink, lavender, peach, sage green, sky blue
- **Accessories:** Bow, flower crown, tiny hat, glasses, scarf, earrings
- **Expressions:** Reacts to gameplay - happy when scoring well, nervous during boss fights, sleepy on menu screen
- **Idle Animations:** Catches a fly, blows a bubble, blinks slowly, adjusts accessory

---

## UI / UX Design Notes

### Layout (Portrait Mode)

```
+---------------------------+
|[Ribbit Goal][Turns][Lives]|   <- Top bar: target, turn counter, lily petal lives
|                           |
| [Charm1][Charm2]...[Charm5]   <- Charm row (tap to inspect)
|                           |
| +------+ +------+ +------+|
| |Meld 1| |Meld 2| |Meld 3||  <- Lily Pad melding area (scrollable)
| | *  *  | | *  * | | *    ||     Shows cards stacked, blooms when 7 reached
| +------+ +------+ +------+|
|                           |
| [MELD] [DRAW POND][PICKUP]|   <- Action: meld selection, draw 2, or grab Puddle
|                           |
| +--+ +--+ +--+ +--+ +--+ |   <- Your Hand (swipeable, tap to select)
| |  | |  | |  | |  | |  | |
| +--+ +--+ +--+ +--+ +--+ |
|                           |
| [Puddle: 3]  [Foot: 11]  |   <- Discard pile count + Foot pile (locked until Hand empty)
| [ Frog Avatar :) ]        |   <- Your frog, reacts to gameplay
+---------------------------+
```

### Key UX Principles

- **One-hand play:** All interactions reachable with thumb in portrait mode
- **Tap to select, tap to meld:** Tap cards to select them, then tap MELD to place them on a lily pad
- **Drag to reorder:** Drag cards in hand to sort by type or value
- **Auto-sort button:** Sorts hand by bug type or by nectar value (toggle)
- **Gentle haptics:** Soft vibration on melds, satisfying buzz on Canasta Stack completion
- **No real-time pressure:** Take as long as you want per turn (turns are limited, not time)
- **Undo button:** Can undo card selection and the most recent meld (once per turn)
- **Meld preview:** Selecting cards highlights which lily pad they'd join, shows point preview
- **Accessibility:** Colorblind-friendly bug type icons + unique shapes per type, scalable text, screen reader support

### Animation & Juice

- Cards hop (like a frog!) when selected
- Melding cards causes them to leap onto the lily pad with a splash
- Completing a Canasta Stack triggers a blooming flower animation on the lily pad
- Hopping to your Foot triggers a celebratory frog jump animation
- Charms wiggle and glow when they activate
- Boss defeat triggers a rain of sparkles and flowers
- Screen transitions are gentle lily pad dissolves
- Picking up the Puddle shows cards flying up like scattered leaves

---

## Audio Design

| Element | Style |
|---------|-------|
| **Background Music** | Lo-fi / acoustic guitar with nature sounds (rain, crickets, gentle water) |
| **Card Play** | Soft "plop" like a raindrop on a lily pad |
| **Score Tally** | Ascending xylophone notes |
| **Big Score** | Musical "ribbit" jingle + sparkle chime |
| **Boss Encounter** | Music shifts to slightly dramatic but still cozy |
| **Menu/Shop** | Gentle ukulele with bird chirps |
| **Frog Sounds** | Cute, cartoonish croaks and chirps (not realistic) |

---

## Progression & Replayability

### Unlockables

- **New Frog Species:** Unlock by completing acts
- **Charm Collection:** Log of all discovered Charms (collectible sticker book style)
- **Card Skins:** Seasonal bug designs unlocked through play
- **Challenge Modes:** Unlocked after first full clear
  - *Speed Pond:* Only 8 turns per round - meld fast!
  - *No Foot:* No Foot pile - you only get your Hand each round
  - *Wild Chaos:* Deck is 50% Chameleon Tongues - build Wild Blooms galore
  - *Poison Garden:* Tons of Poison Ivy cards shuffled in - manage the risk
  - *Charm Storm:* Start with 5 random Charms but Ribbit Goals are doubled
  - *Zen Mode:* No fail state, unlimited turns - just meld and relax

### Daily Challenges

- **Daily Pond:** A seeded run everyone plays - compare scores on leaderboard
- **Weekly Charm Challenge:** Build around a specific charm for bonus rewards
- **Seasonal Events:** Cherry blossom spring event, cozy autumn event, winter wonderland event

### Stats & Collection

- **Frog Journal:** Tracks total Ribbits earned, favorite Charms, best catches
- **Charm Sticker Book:** Collect holographic stickers for each Charm discovered
- **Achievement Lily Pads:** Visual garden that grows as you complete achievements

---

## Technical Considerations

| Aspect | Recommendation |
|--------|---------------|
| **Engine** | Unity (2D) or Godot - both excellent for card games |
| **Languages** | C# (Unity) or GDScript (Godot) |
| **Resolution** | Design for 1080x1920 base, scale for tablets |
| **Save System** | Local save + optional cloud sync |
| **Offline Play** | Fully playable offline |
| **Session Length** | A full run takes ~25-40 minutes, but can save & quit anytime |
| **Install Size** | Target under 200MB |
| **Min OS** | iOS 14+ / Android 8+ |

---

## What Makes This Different From Balatro

| Aspect | Balatro | Lily Pad Luck |
|--------|---------|---------------|
| **Base Card Game** | Poker (hand ranking) | Hand and Foot Canasta (melding & set collection) |
| **Core Action** | Form a single poker hand per play | Meld groups across multiple lily pads over many turns |
| **Pacing** | Quick burst hands | Multi-turn rounds with draw/meld/discard rhythm |
| **Card Mechanic** | Evaluate one 5-card hand at a time | Build up melds incrementally toward 7-card Canasta Stacks |
| **Two-Pile System** | N/A | Hand and Foot - strategic tension of when to exhaust your Hand |
| **Discard Strategy** | N/A | Puddle (discard pile) pickup creates risk/reward decisions |
| **Wild Cards** | Jokers modify scoring | Chameleon Tongues integrated into melds with ratio limits |
| **Penalty Cards** | N/A | Poison Ivy cards add risk management |
| **Scoring** | Per-hand with multipliers | Cumulative across completed stacks + bonuses |
| **Aesthetic** | Poker / casino / retro pixel | Cute frog / nature / cottagecore watercolor |
| **Platform** | Desktop-first | Mobile-first, one-hand portrait play |
| **Avatar** | None | Customizable frog companion with expressions |
| **Narrative** | Minimal | Light story (saving the pond from threats) |
| **Social** | None | Daily challenges + score sharing |

---

## Summary

**Lily Pad Luck** combines the cozy satisfaction of collecting and melding sets with the strategic depth of a roguelike card game. Built on Hand and Foot Canasta's draw-meld-discard rhythm, it offers a fundamentally different experience from poker-based card roguelikes - one centered on building up lily pads over multiple turns rather than evaluating single hands. With ethical monetization, a deep Charm system, and a charming frog-filled world, it's a pond players will want to return to daily.

---

*"Hop in. Meld your bugs. Save the pond."*
