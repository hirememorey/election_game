# ELECTION Game: Path Forward

**Date:** May 9, 2026
**Status:** Playable prototype with critical balance and depth issues
**Decision:** Pursue as a physical board game; digital version becomes simulation/playtesting tool

---

## Current State Summary

- **Codebase:** ~124K LOC across Python backend + JS frontend
- **Working features:** Full action system, WebSocket multiplayer, AI personas, simulation harness (8 experiment types, 300+ games each), deployed to Render
- **Physical spec:** Complete manufacturing document (`PHYSICAL_GAME_SPEC.md`) with BOM — clay composite chips, velvet Chamber Bags, linen board
- **Simulation data:** 8 experiment sets covering random baseline, skill delta, economic vs legislative, balanced strategy, and more

---

## The Core Strength

The **Chamber Bag** (secret commitment system) + **Personal Mandates** (hidden asymmetric victory conditions) is the game's identity. It creates:

1. **Information asymmetry** — you know your commitment, not others'
2. **Bluffing / double-bluff** — big commitment or feint?
3. **Bet sizing** — the gambling-style reward multipliers (1x / 1.5x / 2x) reward bigger commitments
4. **Dramatic tension** at reveal — the emotional climax of each term
5. **Divergent incentives** — the War Hawk wants Military Funding to crit; the Environmentalist wants Infrastructure to pass twice; their objectives silently collide

This mechanic is genuinely good. It's a physical-moment mechanic that doesn't work on a screen — the velvet bag, the hidden drop, the sound of chips, the dramatic upend. That's a product, not a feature.

---

## The Five Critical Problems

### 1. The Economic Strategy Dominates Everything

**Evidence:** Simulation data is unambiguous:

| Experiment | Economic Bot Win Rate | Notes |
|---|---|---|
| economic_vs_legislative | **96.4%** (482/500) | Economic bots nearly shut out legislative bots |
| basic_balance_test | **59.8%** (598/1000) | Economic beats all comers including balanced |
| balanced_strategy_test | Balanced Bot wins, but Economic Bot is 2nd | Even balanced strategy defaults to accumulation |

**Root cause:** Fundraising generates 5 PC per action at 1 AP — a 5:1 return. Sponsor Legislation costs 2 AP + the bill cost. The PC economy rewards accumulation over expenditure. In a game called *Election*, the optimal strategy is "don't engage with election mechanics, just hoard capital."

### 2. The Election System Is Mechanically Shallow

Current election: commit PC → add a d6 roll → highest total wins. That's a coin flip with a bidding war, not a strategic system. Compare to legislation (sponsor, support/oppose secretly, multi-tier success thresholds, mood effects, gambling multipliers) — elections have no comparable depth.

The NPC Challenger is a band-aid: a fixed-strength AI opponent that occasionally steals an office. It's a tax on not committing enough PC, which loops back to "just accumulate more PC."

### 3. Too Few Decision Points

2 AP per turn × 4 rounds × 3 terms = **24 total actions per player**. Of those, ~8-12 are likely Fundraise (because it's dominant). That leaves ~12-16 non-trivial decisions across an entire game. For comparison:

| Game | Approximate Decision Points |
|---|---|
| ELECTION (current) | 24 |
| Catan | 40-50 |
| Ticket to Ride | 50-60 |
| Twilight Struggle | 60+ |

The AP economy is too tight for the number of systems the game wants you to engage with.

### 4. Secret Commitments Aren't Secret in the Digital Version

The physical game's social theater — watching someone's face as they drop chips, the sound of heavy chips hitting velvet, the collective breath before the reveal — doesn't translate to a screen. The digital "secrecy" is just UI occlusion; the server tracks everything in plain dicts. This works for human-vs-AI but would need a fundamentally different architecture for multiplayer.

The digital version's value is as a **simulation and playtesting tool**, not as the product itself.

### 5. Mandate System Has Implementation Gaps

Five mandates in `scoring.py` are stubbed as "completed if president," defeating the purpose of hidden asymmetric objectives:

| Mandate | Intended Condition | Actual Implementation |
|---|---|---|
| MINIMALIST | Win presidency with ≤20 PC committed | Just checks if president |
| OPPORTUNIST | Win presidency without ever being incumbent | Just checks if president |
| PRINCIPLED LEADER | Win presidency without ever holding Governor | Just checks if president |
| KINGMAKER | Support 2+ successful bills by presidency winner | `presidency_winner_id` not set before evaluation |
| STATESMAN | Hold Governor or US Senator at game end | Correctly implemented |

---

## The Five Changes

### Change 1: Fix the Economy — Make Spending Beat Hoarding

**A. Add PC Decay (Inflation Mechanic)**
At the start of each Term, every player loses 1 PC per 10 PC they hold (rounded down). This punishes hoarding and creates time pressure to spend. A player sitting on 40 PC loses 4 PC per term — not crippling, but it makes "do nothing" a losing strategy over time.

**B. Reduce Fundraise to 3 PC (from 5)**
This makes Network (2 PC + favor) comparatively more attractive and slows the accumulation curve. At 5 PC/action, Fundraise is strictly dominant over Network. At 3 PC, the favor draw becomes the real value proposition.

**C. Increase Legislation Failure Penalties**
Current penalties are too low (0 for Infrastructure and Children, 5 for Tax Code). Make the gamble real:

| Legislation | Current Failure Penalty | Proposed Failure Penalty |
|---|---|---|
| Infrastructure Bill | 0 | 3 |
| Protect The Children! | 0 | 3 |
| Military Funding | 0 | 5 |
| Change the Tax Code | 5 | 8 |
| Healthcare Overhaul | 10 | 15 |

Higher failure penalties create genuine risk/reward tension. Currently, sponsoring low-cost legislation is nearly free — if it fails, who cares? With real penalties, the sponsor must actively campaign for support, which drives the social interaction the game is built for.

### Change 2: Deepen Elections — The Game's Namesake Should Be Its Best System

Replace the current "commit PC + d6" election with a **two-phase election system**:

**Phase 1 — The Campaign (Rounds 1-3):**
- New action: **Campaign** (Cost: 1 AP). Place a Campaign Token on a specific office track. This is public — visible to all players. It signals intent.
- Each Campaign Token on an office track is worth 3 PC in the final election score.
- Players can campaign for offices they don't end up running for — creating bluffing and blocking dynamics.

**Phase 2 — The Vote (Round 4):**
- Declare candidacy as currently implemented.
- Final election score = (Committed PC) + (Campaign Tokens × 3) + (d6).
- This creates **time vs. money** tension: a player with fewer PC but more Campaign Tokens can beat a wealthy opponent who didn't invest time in campaigning.
- Campaign Tokens are visible, creating public signaling. Committed PC is secret (via Chamber Bag), creating private information. The d6 adds just enough variance to prevent deterministic outcomes.

**Why this works:** It mirrors real elections — you can't just buy your way in; you have to show up and campaign. It gives players something meaningful to do with their AP in Rounds 1-3 beyond fundraise. And it creates a public information layer (Campaign Tokens) that interacts with the private information layer (secret PC commitments) — exactly the kind of system that makes the Chamber Bag mechanic sing.

### Change 3: Increase Decision Density — 3 AP Per Turn

Change from 2 AP to 3 AP per turn. This gives players room to fundraise *and* do something else in the same turn. At 2 AP, the choice between "Fundraise" and "literally anything else" is almost always Fundraise. At 3 AP, you can:

- Fundraise + Support Legislation
- Network + Campaign
- Sponsor Legislation + Fundraise
- Campaign + Campaign (double down on an office)
- Support + Oppose (play both sides of a bill)

The decision tree branches meaningfully. Total actions per player becomes 36 (3 AP × 4 rounds × 3 terms) — closer to the genre benchmark.

### Change 4: Fix the Mandate Stubs

Each stubbed mandate needs proper tracking:

| Mandate | Required Tracking |
|---|---|
| MINIMALIST | Track `committed_pc` in the final election. Completed only if `committed_pc ≤ 20` AND player holds presidency. |
| OPPORTUNIST | Track `was_ever_incumbent` boolean per player. Set to `True` whenever a player gains an office. Completed only if president AND `was_ever_incumbent == False`. |
| PRINCIPLED LEADER | Track `offices_held_history: Set[str]` per player. Completed only if president AND `"GOVERNOR" not in offices_held_history`. |
| KINGMAKER | Set `presidency_winner_id` *before* evaluating mandates. Count `legislation_history` entries where `sponsor_id == presidency_winner_id` AND `outcome in ["Success", "Critical Success"]` AND `player_id in support_players`. Completed if count ≥ 2. |

These are straightforward state additions to `Player` and `GameState`. The simulation harness can validate them immediately.

### Change 5: Reduce to 2 Terms

Three terms at 4 rounds each is too long for a social deception game. The genre benchmark is 30-60 minutes. Cut to **2 Terms** and tighten the arc:

- **Term 1:** Positioning. Campaign, fundraise, sponsor low-cost legislation, signal (or bluff) about mandate objectives.
- **Term 2:** Endgame. High-stakes legislation, final elections, mandate reveals. Everything accelerates.

At 2 terms × 4 rounds × 3 AP = 24 actions per player. With the Campaign mechanic and reduced Fundraise value, ~12-16 of those are non-fundraise decisions. Every choice matters more. The Chamber Bag reveals happen twice instead of three times — but each one carries more weight because the game is shorter and the stakes are higher.

---

## Implementation Sequence

| Step | Time | What | Deliverable |
|---|---|---|---|
| **1. Implement economy fixes** | 1 day | Changes 1A-C in `game_data.py` and `engine/resolvers.py`. Add PC decay to `resolve_upkeep`. | Updated game data + resolver |
| **2. Implement Campaign action** | 1-2 days | New action class, resolver, AP cost mapping, campaign token tracking on GameState, election score calculation update. | Working Campaign system |
| **3. Increase to 3 AP** | 30 min | Change `base_ap_per_turn` in `game_config.yaml` and `start_new_game` in `engine.py`. | Config change |
| **4. Fix mandate stubs** | 1 day | Add tracking fields to `Player` and `GameState`, update `scoring.py` for all 4 mandates. | Correct mandate evaluation |
| **5. Reduce to 2 terms** | 30 min | Change `is_game_over` threshold from 3 to 2. Update `game_config.yaml`. | Config change |
| **6. Run 10K sim games** | 1 hour | Execute simulation harness across all 8 experiment types with new parameters. | Balance data |
| **7. Analyze and iterate** | 1-2 days | Compare new results to baseline. Adjust numbers (PC decay rate, Campaign token value, Fundraise output) based on data. | Balanced game |
| **8. Build paper prototype** | 1-2 days | Print cards on cardstock, use poker chips, use a cloth bag. Playtest with 2-3 people. | Physical playtest |
| **9. Iterate on physical feedback** | 2-3 sessions | The sim tells you if it's balanced. The playtest tells you if it's fun. The Chamber Bag reveal is either electric or anticlimactic — you won't know until you feel it. | Playtest notes |
| **10. Decide: self-publish or pitch** | Post-playtest | See "Publishing Path" below. | Strategic decision |

---

## Publishing Path (Post-Playtest)

### Option A: Self-Publish via Kickstarter

- **Upfront cost:** $5-15K (prototype, art, manufacturing minimums)
- **Timeline:** 6-12 months from funded campaign to delivery
- **Margin:** You keep 40-60% of retail after fulfillment
- **Control:** Full creative and commercial control
- **Risk:** You're the publisher — customer service, shipping, reprints
- **Comparable campaigns:** *Cosmic Encounter* (FGG), *The Resistance* (Indie Boards & Cards), *Sheriff of Nottingham* (Arcane Wonders)

### Option B: Pitch to Publishers

- **Target publishers:** Oink Games, Stellar Factory, Button Shy, Level 99 Games, Dire Wolf
- **Timeline:** 12-24 months from signed deal to shelf
- **Margin:** 5-8% royalties on wholesale
- **Control:** Publisher owns the game; you're the designer
- **Risk:** Low financial risk, but loss of creative control and much lower per-unit return
- **Your pitch asset:** The simulation harness is unprecedented in board game design. No publisher sees a designer walk in with 10,000 simulated games proving balance. That's your "Sovereign Artifact" for this domain.

### Option C: Hybrid — Print-and-Play First

- **Upfront cost:** $0-500 (PDF design, drive traffic via BoardGameGeek)
- **Timeline:** 2-4 weeks to create a print-and-play PDF
- **Margin:** $0 direct, but builds audience and playtest data
- **Control:** Full
- **Risk:** Minimal. This is the lowest-investment path and generates real-world feedback before committing to manufacturing or a publisher pitch. The simulation harness + print-and-play community feedback is the strongest possible validation before a Kickstarter or publisher meeting.

---

## Key Metrics to Track (Post-Changes)

| Metric | Current | Target | How to Measure |
|---|---|---|---|
| Economic Bot win rate (vs balanced) | 59.8% | 30-35% | `basic_balance_test` simulation |
| Economic vs Legislative win rate | 96.4% | 45-55% | `economic_vs_legislative` simulation |
| Heuristic vs Random win rate | 46.1% (with dice) | 40-50% | `skill_delta_test` simulation |
| Average game length (terms) | 5-7 | 2 (after change) | All simulations |
| Fundraise action frequency | ~50% of all actions | ~30% | Instrument action log in sim |
| Average non-fundraise actions per game | ~12-16 | ~18-22 | Instrument action log in sim |

---

## Why This Project, Why Now

The honest question is whether this deserves energy during Phase 6. The answer depends on what the game is *for*:

**If it's a creative exercise that might become a product** — the 2-3 weekend investment to get a paper prototype is worth it. The simulation harness already exists. The manufacturing spec already exists. The fixes are concrete. The Chamber Bag mechanic is real.

**If it's a distraction from the search** — it's a distraction. The pipeline is compounding. Every weekend spent on game design is a weekend not spent on the Casey Hancock prep, the SmithRx recon brief, or the Santangelo DM.

**The synthesis:** Treat this as the same way you treat the NBA moonshot — a Strategic Thread, not the Main Quest. The paper prototype is a 2-weekend project. If the Chamber Bag reveal is electric in physical playtest, it's worth pursuing further. If it's anticlimactic, archive it with honor and move on. The simulation harness alone — the ability to prove game balance with data — is a rare capability that differentiates this from every other "I have a board game idea" pitch in the world.
