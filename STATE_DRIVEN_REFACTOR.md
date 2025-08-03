# State-Driven Architecture Refactor

## 1. Purpose & Motivation

This document outlines a plan to refactor the game's core architecture. The primary motivation is to address the recurring "whack-a-mole" problem, where fixing one bug introduces new, unforeseen issues. This indicates that the current architecture is brittle and difficult to maintain.

The goal is to create a **stable, maintainable, and predictable** game engine by adhering to modern software design principles.

### Current Shortcomings:

*   **Tangled Logic:** Game logic is spread across `GameSession`, `GameEngine`, and even the frontend, making it difficult to trace the flow of data and control.
*   **Complex Action Flows:** The current "two-step" and "three-step" action system is complex and has been a frequent source of bugs.
*   **Brittle Client-Server Communication:** The communication between the client and server is "chatty" and relies on a complex sequence of messages, making it prone to getting out of sync.

## 2. Core Architectural Principles

The new architecture will be guided by the following principles:

1.  **Pure Game Engine:** The `GameEngine` will be a collection of pure functions. Its only job is to take the current game state and an action, and produce the *next* game state. It will have no side effects and no knowledge of the outside world (UI, network, etc.).
2.  **Single Source of Truth:** The `GameState` object will be the one and only authority on the current state of the game. All parts of the system will read from this state.
3.  **Unidirectional Data Flow:** Information will flow in a single, predictable direction: `UI -> Action -> Server (GameSession) -> Engine -> New GameState -> UI`.
4.  **"Dumb" UI:** The frontend's main job will be to render the state it's given and send user actions to the backend. It will not contain complex game logic.

## 3. Proposed Architecture

*   **`GameState` (`models/game_state.py`):** A comprehensive, serializable data class that represents all information about the game at a single point in time.
*   **`GameEngine` (`engine/engine.py`):** A stateless service class containing pure functions. The main functions will be `process_action(state: GameState, action: Action) -> GameState` and `get_valid_actions(state: GameState, player_id: int) -> List[Action]`.
*   **`GameSession` (`game_session.py`):** The "conductor." It will hold the single `GameState` instance. It will manage the game lifecycle, handle incoming actions from the UI, call the `GameEngine`, and run AI turns. It will be the only component with side effects.
*   **`server.py`:** The network layer. It will handle websocket connections and pass validated user action data to the `GameSession`.
*   **`static/app.js`:** The UI layer. It will receive a full `GameState` object, render it, and present the `valid_actions` to the user.

## 4. Execution Plan

1.  **~~Create `STATE_DRIVEN_REFACTOR.md`~~:** **Done.** This document.
2.  **~~Establish a Test-Driven Foundation~~:** **Done.**
    *   ~~Create a new test file, `test_state_driven_flow.py`.~~ **Done.**
    *   ~~Write a "golden path" test for a single, complete round of a 2-player game. This test will initially fail but will serve as our guide.~~ **Done.** The initial test for a single action is passing.
    *   **Update:** The comprehensive end-of-term test (`test_term_flow.py`) is also now passing, validating the full game loop.
3.  **Refactor the Core Engine (`engine.py`):**
    *   ~~Strip all stateful logic from `GameEngine`.~~ **Done.**
    *   ~~Rewrite `process_action` to be a pure function that accepts `GameState` as its first argument.~~ **Done.**
    *   **Update:** Turn-advancement logic has been separated from `process_action`, and all action resolvers now correctly deduct AP. The engine is now stateless.
4.  **Refactor the Session Manager (`game_session.py`):** **In Progress.**
    *   ~~Make `GameSession` the sole owner of the `GameState` object.~~ **Done.**
    *   ~~Rewrite its methods to follow the new unidirectional flow.~~ **Done.**
    *   **Update:** The `GameSession` has been significantly simplified. The complex, stateful logic for handling multi-step UI actions (`pending_ui_action`) has been removed. `GameSession` now acts as a clean "conductor," passing actions directly to the pure `GameEngine`.
5.  **Simplify the Frontend (`static/app.js`):** **In Progress.**
    *   ~~Remove complex logic for interpreting multi-step server responses.~~ **Done.**
    *   ~~Update the rendering logic to work from the single, comprehensive `GameState` object.~~ **Done.**
    *   **Update:** The frontend no longer relies on the backend to manage UI presentation state (like pausing for AI turns). Multi-step actions are now driven by a `pending_ui_action` object within the `GameState`, making the client a "dumber" and more robust renderer of the state.
6.  **Establish a New UI Action Pattern:** **Done.**
    *   A new pattern for handling multi-step UI actions has been established and proven for the "Support Legislation" flow.
    *   **New `GameState` field:** `pending_ui_action` was added to `GameState` to hold the state of the UI interaction.
    *   **New `GameEngine` actions and resolvers:** The engine now uses a chain of actions (`ActionInitiate...`, `ActionSubmit...`) and corresponding resolvers to manage the UI flow in a purely functional way.
    *   This pattern is now ready to be applied to the remaining UI actions (`OpposeLegislation`, `SponsorLegislation`, `DeclareCandidacy`).
7.  **Iterate and Expand:** Once the "golden path" test passes, incrementally add tests for more complex scenarios (e.g., end-of-term logic) and refactor the code to make them pass.

## 5. Desired Outcome

*   A stable game that is no longer prone to cascading bugs.
*   A codebase that is easier to understand, maintain, and extend.
*   A clear separation of concerns that allows for independent development and testing of the game logic and the UI. 