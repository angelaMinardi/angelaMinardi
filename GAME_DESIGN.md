# Lily Pad Luck - Game Design Document

> A cozy, frog-themed roguelike card game for mobile

---

## Concept Overview

**Lily Pad Luck** is a cute, strategic card game where you play as a little frog building the ultimate hand of bug cards to leap across enchanted lily pads. Inspired by the roguelike deck-building genre, players collect, combine, and power up cards through a whimsical journey across a magical pond. Each run is different, with charming frog companions, magical lilies, and sparkling rewards.

**Target Audience:** Women 18-35 who enjoy cozy games, casual strategy, and cute aesthetics
**Platform:** iOS & Android (portrait orientation, one-hand friendly)
**Art Style:** Soft watercolor / cottagecore aesthetic with rounded shapes, pastels, and gentle animations
**Tone:** Relaxing but mentally engaging - "a puzzle wrapped in a hug"

---

## Core Loop

```
 Pick a Pond Path --> Play Bug Cards --> Score Ribbits --> Earn Dewdrops --> Visit Shops/Events --> Repeat
       |                                                                          |
       +--- Each pond has 3 acts (Small Pond, Garden Pond, Enchanted Lake) -------+
```

### 1. The Deck - Bug Cards (instead of playing cards)

Instead of a traditional 52-card poker deck, players use a **Bug Deck** themed around insects a frog would catch. Cards have two properties:

| Property | Values |
|----------|--------|
| **Bug Type** (suit equivalent) | Firefly, Butterfly, Ladybug, Dragonfly |
| **Nectar Value** (rank equivalent) | 1 - 13 (Dewdrop, 2-10, Bloom, Petal, Crown) |

**Visual Design:**
- Fireflies glow with warm amber, cards shimmer gently
- Butterflies have pastel wings with watercolor patterns
- Ladybugs are round and cheerful with polka dots
- Dragonflies have iridescent teal/purple wings

### 2. Hand Combos - "Catches"

Players are dealt bug cards and form **Catches** (hand types) to score points, called **Ribbits**. Similar to poker hands but with frog-themed names:

| Catch Name | Combo | Base Ribbits | Multiplier |
|---|---|---|---|
| **Single Snack** | 1 card | 5 | x1 |
| **Double Hop** | Pair | 10 | x2 |
| **Triple Splash** | Three of a kind | 30 | x3 |
| **Lily Line** | Straight (5 in sequence) | 30 | x4 |
| **Garden Patch** | Flush (5 same bug type) | 35 | x4 |
| **Puddle House** | Full house | 40 | x4 |
| **Quad Croak** | Four of a kind | 60 | x7 |
| **Lily Line Garden** | Straight flush | 100 | x8 |
| **Royal Pond** | Royal flush equivalent | 100 | x8 |
| **Five Flies** | Five of a kind (with wilds) | 120 | x12 |

### 3. Scoring

**Ribbits = (Base Ribbits + Card Nectar Values) x Multiplier**

Each card played adds its nectar value to the base. Charms (jokers) modify these scores in wild, stackable ways.

---

## Key Mechanic - Charms (Joker Equivalent)

**Charms** are the heart of the strategy. They are collectible magical items that modify scoring in creative ways. Each charm is a cute, animated object that sits on a lily pad above your hand.

### Charm Categories

**Frog Friends** - Tiny companion frogs that grant passive bonuses:
- **Rosie** (pink tree frog) - +3 Mult when you play Butterflies
- **Mossy** (green bullfrog) - Earns 4 Dewdrops per hand played
- **Sunny** (golden frog) - +20 Ribbits when hand contains a Firefly
- **Bubbles** (blue poison dart frog) - Each Dragonfly card gives +2 Mult
- **Violet** (purple rain frog) - x1.5 Mult if hand has exactly 4 cards

**Pond Trinkets** - Magical items found around the pond:
- **Moonstone Pebble** - x2 Mult on the first hand of each round
- **Lucky Clover** - +1 to all Nectar values
- **Dewdrop Tiara** - +10 Ribbits for every card above 10
- **Mushroom Cap** - Retrigger all Ladybug cards once
- **Glass Jar** - Collect Fireflies; at 5, gain x4 Mult and release them

**Lily Enchantments** - Powerful but conditional:
- **Blooming Lily** - x3 Mult if you score exactly a Garden Patch
- **Golden Lily** - Converts all Dewdrop earnings to double value
- **Phantom Lily** - Creates a ghost copy of your highest card

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
| Bug icon | **Bug Catch** (battle) | Score enough Ribbits to pass. 3-4 hands per round. Failing = losing a life (lily petal). |
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
| **Sparkling** | Glitter overlay | +30 Ribbits |
| **Gilded** | Gold foil edges | +3 Mult |
| **Wild** | Rainbow shimmer | Counts as all bug types |
| **Lucky** | Four-leaf clover | 1 in 5 chance to x2 final score |
| **Glass** | Translucent / crystal | +100 Ribbits, destroyed after scoring |
| **Botanical** | Flower crown on bug | Earns 6 Dewdrops when played |

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
|  [Ribbits Goal]  [Lives]  |   <- Top bar: score target + lily petal lives
|                           |
|  [ Charm 1 ][ Charm 2 ]  |   <- Charm slots (scrollable, up to 5 visible)
|  [ Charm 3 ][ Charm 4 ]  |
|                           |
|   +----+  +----+  +----+  |
|   |Bug |  |Bug |  |Bug |  |   <- Selected cards (played area)
|   +----+  +----+  +----+  |
|                           |
|  [  PLAY HAND  ] [DISCARD]|   <- Action buttons
|                           |
|  +--+ +--+ +--+ +--+ +--+|   <- Hand of cards (swipeable)
|  |  | |  | |  | |  | |  ||
|  +--+ +--+ +--+ +--+ +--+|
|                           |
|  [ Frog Avatar :) ]       |   <- Your frog at the bottom
+---------------------------+
```

### Key UX Principles

- **One-hand play:** All interactions reachable with thumb in portrait mode
- **Drag to select:** Drag finger across cards to select multiple, tap to deselect
- **Gentle haptics:** Soft vibration on card plays, satisfying buzz on big scores
- **No time pressure:** Take as long as you want per hand
- **Undo button:** Can undo card selection (not card play) freely
- **Accessibility:** Colorblind-friendly bug type icons, scalable text, screen reader support

### Animation & Juice

- Cards hop (like a frog!) when selected
- Scoring triggers ripple effects on the pond background
- Big scores cause your frog to do a happy leap
- Charms wiggle and glow when they activate
- Boss defeat triggers a rain of sparkles and flowers
- Screen transitions are gentle lily pad dissolves

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
  - *Speed Pond:* Timer-based rounds
  - *Tiny Deck:* Start with only 10 cards
  - *Charm Storm:* Start with 5 random charms but harder scoring goals
  - *Zen Mode:* No fail state, just build combos and relax

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

| Balatro | Lily Pad Luck |
|---------|---------------|
| Poker aesthetic, casino chips | Cute frog / nature / cottagecore aesthetic |
| Abstract / retro pixel art | Soft watercolor art style |
| Traditional playing cards | Bug-themed cards with nature suits |
| Jokers | Charms (Frog Friends, Trinkets, Enchantments) |
| Planet/Tarot/Spectral cards | Enchantment Pond upgrades + Treasure Toad finds |
| Antes & blinds | Pond Guardians & themed boss encounters |
| Dark/neon color palette | Pastel / warm / nature color palette |
| No avatar / character | Customizable frog companion with expressions |
| Desktop-first design | Mobile-first, one-hand portrait play |
| Gender-neutral marketing | Marketed toward women with cozy game aesthetics |
| Minimal narrative | Light narrative (saving the pond from threats) |
| No social features | Daily challenges + score sharing |

---

## Summary

**Lily Pad Luck** takes the deeply satisfying combo-building loop of roguelike card games and wraps it in a charming, accessible, frog-themed package. It respects the player's time and wallet with ethical monetization, rewards creativity with a deep charm system, and creates a cozy world players will want to return to daily. Every ribbit counts!

---

*"Hop in. Build your deck. Save the pond."*
