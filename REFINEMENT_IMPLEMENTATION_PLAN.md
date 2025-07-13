# Game Refinements Implementation Plan

## Overview

This plan addresses three major criticisms of the current game design:
1.  **Dice-based legislation resolution** undermines strategic competence
2.  **One action per turn** limits player autonomy and creates slow gameplay
3.  **Unstructured trading** can intimidate new players and bog down the game

These are addressed by two primary system designs: the **Secret Commitment System** for legislation and the **Action Points System** for player turns.

## Phase 1: Secret Commitment System (Replaces Dice & Public Bidding)

### Problem Analysis
- Current System: Legislation success is determined by public PC commitments, which can lead to a simple "resource race" where the wealthiest player has an unassailable advantage.
- Issue: This reduces strategic depth, negotiation, and the potential for dramatic reversals. It's a math problem, not a social deduction problem.
- Impact: Players with less PC feel their actions are meaningless. Tension is low.

### Solution: Secret PC Commitment System with Bluffing
Replace the public bidding with a strategic system where players secretly commit PC to support or oppose legislation. This introduces bluffing, betrayal, and social deduction as the core legislative mechanics.

### Implementation Steps

#### 1.1 Create Server-Side Secret Storage
**File**: `server.py`
**Changes**:
- A new global dictionary, `SECRET_COMMITMENTS`, will be created to store commitments outside of the main `GAMES` dictionary.
- The structure will be: `SECRET_COMMITMENTS = { "game_id_1": { "legislation_id_1": [ (player_id, stance, amount), ... ] } }`
- This ensures that secret data is never sent to clients as part of the standard game state polling.

#### 1.2 Modify Action Handling
**File**: `server.py`, `/api/game/<game_id>/action` endpoint
**Function**: `process_action()`
**Changes**:
- When handling the `support_oppose_legislation` action:
    - Do NOT modify the public `game_state` directly.
    - Retrieve the `player_id`, `legislation_id`, `stance` ('support' or 'oppose'), and `amount` from the request.
    - Add this information as a tuple to the `SECRET_COMMITMENTS` dictionary under the correct `game_id` and `legislation_id`.
    - Return the standard `game_state` to the client *without* the secret information. The acting player's client will provide confirmation based on the successful API call.

#### 1.3 Update Legislation Resolution Logic
**File**: `engine/engine.py` (Or wherever `resolve_legislation_session` is)
**Function**: `resolve_legislation_session()`
**Changes**:
- This function (and only this function) will now need access to the secret commitments for the game being resolved.
- For each piece of term legislation:
    - Retrieve all secret commitment tuples for that bill from the `SECRET_COMMITMENTS` dictionary.
    - Tally the total support and opposition PC.
    - **Crucially, add each individual commitment to the public game log** so the reveal is clear. E.g., `state.add_log(f"REVEAL: Player {player.name} supported with {amount} PC.")`
    - Determine the outcome (Success, Critical Success, Failure) based on the net influence.
    - Apply rewards and penalties as before.
    - Clear the secret commitments for that bill from the `SECRET_COMMITMENTS` dictionary after it is resolved.

#### 1.4 Update Game State Models
**File**: `models/game_state.py`
**Changes**:
- The `PendingLegislation` object no longer needs to store `support_players` and `oppose_players`. This data is now secret and managed entirely on the server until the reveal. The class can be simplified or removed depending on its other uses. `term_legislation` will just be a list of legislation IDs to be resolved.

#### 1.5 Update Frontend UI/UX
**File**: `static/script.js`
**Changes**:
- **Action Confirmation**: When a player successfully calls the `support_oppose_legislation` action, the frontend should display a clear, private confirmation message (e.g., "Your secret commitment of 12 PC to Support has been registered.").
- **Public Indication (Optional)**: To enhance intrigue, when a commitment is made, the UI for *all other players* could show a subtle, generic indicator on the bill, like a small colored cube representing the player who acted, without revealing their stance or amount.
- **Resolution Log**: The `updateLog()` function must be able to parse and dramatically display the reveal from the game log. This is the payoff moment and should be a major point of focus in the UI.

### Testing Phase 1
**File**: `test_secret_commitment_system.py` (New test file)
**Test Cases**:
1.  Verify commitments are stored secretly and not exposed in the main game state endpoint.
2.  Test that the resolution function correctly tallies secret support and opposition.
3.  Test that multiple secret commitments from the same player to the same bill are correctly aggregated.
4.  Test that the game log accurately reflects all secret commitments during the reveal.
5.  Test that secret data is correctly cleared after resolution.

## Phase 2: Executive Term (Action Points System)

### Problem Analysis
- Current system: One action per turn
- Issue: Slow gameplay, limited strategic expression
- Impact: Players feel constrained and the game pace can drag, especially in the early rounds. 