# "Player-First" Refactor Implementation Plan

## Guiding Principle
Our primary goal is to test and refine the core gameplay experience. This means ruthlessly simplifying the interface to focus our development effort on game mechanics and AI opponents. We are moving from building a *product* to tuning an *experience*.

This plan is broken into three phases designed to incrementally achieve this vision.

---

### Phase 1: Implement Election Dice Rolls (Rule Parity)

**First Principle:** The live game must operate under the same rules as our successful simulations. The most critical missing piece is the element of luck in elections.

**Tasks:**

1.  **The Goal:** Implement the d6 dice roll in the web version's election phase. Our simulations proved this is a key factor in the skill/luck balance.
2.  **Backend Verification (Minor Change):**
    *   **File to Check:** `server.py`.
    *   **Endpoint:** The `resolve_elections` function, which handles the `POST /api/game/<game_id>/resolve_elections` call.
    *   **Action:** Verify that this endpoint calls the engine's election resolution session *without* disabling the dice roll. The default behavior (`disable_dice_roll=False`) is what we want.
3.  **State Management (Already Done):**
    *   The `resolve_elections` function in `engine/resolvers.py` has already been updated to include `dice_rolls` and final scores in the `last_election_results` dictionary within the `GameState`. This data should be ready for the frontend.
4.  **Frontend (Visual Feedback):**
    *   **Files to Check:** The JavaScript file responsible for rendering the election results screen (likely in `static/js/`).
    *   **Action:** Modify the UI to display the full election calculation: `[Player Name]: [PC Committed] PC + [Dice Roll] (dice) = [Final Score]`. This makes the luck element transparent and exciting for the player.

---

### Phase 2: The "Dev-Focused" UI (Radical Simplification)

**First Principle:** The simplest interface that allows for gameplay is the best interface for rapid tuning. We will trade graphical complexity for development speed.

**Tasks:**

1.  **The Goal:** Replace the current complex UI with a minimal, text-based "command-line" style interface that is still deployed on the web.
2.  **The Vision:** Imagine a single web page with two main elements:
    *   A **Game Log:** A simple, scrolling text area that displays the `game_state.turn_log`.
    *   An **Action Prompt:** When it's the human player's turn, this area displays a numbered list of valid actions and a simple input box. The player types a number and hits "Enter" to take their turn.
3.  **Implementation Steps:**
    *   **Create New UI:** Create a new, minimal `index_dev.html` and a corresponding `main_dev.js`. This is simpler than modifying the existing complex UI.
    *   **JavaScript Logic:**
        1.  On page load, and after every action, fetch the full game state from the `GET /api/game/<game_id>` endpoint.
        2.  Render the `game_state.turn_log` into the Game Log `<div>`.
        3.  If it's the human player's turn, render the `valid_actions` as a numbered list in the Action Prompt.
        4.  When the player submits a number, find the corresponding action in the `valid_actions` array, construct the action payload, and `POST` it to the `/api/game/<game_id>/action` endpoint.
4.  **The Benefit:** This eliminates nearly all frontend dependencies and state management bugs, allowing us to focus 100% of our effort on the game engine and AI.

---

### Phase 3: Introduce AI Opponents (The "Playtest" Feature)

**First Principle:** To test if a game is fun, a human must be able to play it against a competent opponent. We will bring our simulated personas to life.

**Tasks:**

1.  **The Goal:** Allow a human to start a game and play against AI-controlled opponents that use the personas from our simulation framework (e.g., `HeuristicPersona`).
2.  **Implementation Steps:**
    1.  **Designate AI Players:**
        *   Modify the `Player` model in `models/player.py` to include a boolean `is_ai` flag.
        *   On the new simplified "New Game" page, allow the user to designate which players will be human and which will be AI.
    2.  **Instantiate AI "Brains":**
        *   When a new game is created in `server.py`, if a player has `is_ai=True`, create an instance of the chosen persona (e.g., `HeuristicPersona()`) and associate it with that player's ID in a server-side dictionary.
    3.  **Create the Server-Side AI Loop:**
        *   This is the most critical part. The logic must live in `server.py`, right after an action is processed.
        *   After any turn (human or AI), check if the *new* `current_player` is an AI.
        *   If it is, **enter a loop that runs on the server**:
            a. Get valid actions for the AI player: `engine.get_valid_actions()`.
            b. Use the AI's persona to choose an action: `action = persona.choose_action(...)`.
            c. Process that action: `engine.process_action(action)`.
            d. Add a message to the game log showing the AI's action.
            e. Check the new `current_player`. If they are *also* an AI, the loop continues.
        *   The loop only breaks when the `current_player` is human.
        *   Finally, the server sends the complete, updated `GameState` back to the human player's browser, showing the result of their action and all subsequent AI actions. 