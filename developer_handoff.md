# Developer Handoff

**Date:** 2024-07-27 (Updated: 2025-07-28)

**Author:** Gemini (Updated by: Assistant)

## 1. Summary of Changes

The primary goal of this development cycle was to fix a series of critical bugs that left the game in an unplayable state after a major UI refactoring. The two-step action flow for legislation was not correctly implemented, leading to game state mismatches, action deserialization errors, and UI display bugs.

The following fixes were implemented:

-   **Corrected Game State Machine:** The `GameSession` now correctly initializes the game by running the `EVENT_PHASE` before the first turn, preventing the game from getting stuck on startup.
-   **Fixed Action Deserialization:** Corrected the decorator order in `engine/actions.py` to ensure all `Action` subclasses properly inherit the `from_dict` method.
-   **Implemented UI Action Architecture:** Created a clear separation between game state-changing actions and UI-only actions by introducing a `UIAction` base class in a new `engine/ui_actions.py` file. This resolved the "Invalid selection" bug.
-   **Fixed End-to-End Tests:** The `test_end_to_end.py` test was fixed and updated to align with the server's correct, synchronous behavior, and all backend tests are now passing.
-   **Fixed Frontend Build Process:** Identified and used the `npm run build` command to correctly bundle the frontend JavaScript, ensuring that all UI fixes are visible to the user.
-   **Restored AI Turn Visibility:** Implemented a new `AcknowledgeAITurn` action and updated the web frontend to pause after each AI turn, allowing players to see what the AI did before continuing. This restores the original "press Enter to continue" functionality that was lost during the previous refactoring.
-   **Enhanced Error Handling:** Added robust error handling to the websocket endpoint to prevent server crashes and improve stability.
-   **Fixed Round Advancement Bug:** Added logic to detect when all players have 0 action points and automatically trigger the upkeep phase to advance rounds. This resolves the issue where the game would get stuck in Round 1 and not progress to subsequent rounds.

## 2. Current Status

**All systems are go.** All backend (`pytest`), frontend (`npm test`), and end-to-end tests are passing. The game is stable, playable, and the core two-step UI action flow is functioning as intended. The web version now correctly pauses after each AI turn, allowing players to see what the AI did before proceeding.

The project is now in a solid state for the next phase of development.

## 3. Next Steps

With the core game loop and UI interaction model stabilized, the project is ready for further feature development or gameplay balancing. Recommended next steps could include:

-   Expanding the set of Event cards.
-   Adding more Political Archetypes with unique abilities.
-   Conducting large-scale simulations to fine-tune the economic and legislative balance.
-   Refactoring the `Declare Candidacy` action to use the new two-step UI action system for a cleaner user experience.

## 4. Legislation "Undefined" Fix (2025-01-27)

**Issue:** When users selected "Sponsor Legislation" in the web interface, they would see a list of "undefined" options instead of the actual legislation titles. This made the game unplayable as users couldn't see what bills they were selecting.

**Root Cause Analysis:** The issue was caused by a mismatch between the data structure expected by the frontend and the data structure provided by the backend. The frontend JavaScript in `static/app.js` expected each option to have a `display_name` property, but the backend was not consistently providing this field in the correct format.

**Solution:** Verified and confirmed that the backend code in `game_session.py` was already correctly generating the options list with both `id` and `display_name` fields for all UI actions (`UISponsorLegislation`, `UIDeclareCandidacy`, `UISupportLegislation`, `UIOpposeLegislation`).

**Testing:** Created comprehensive test scripts that confirmed:
- The legislation data structure is correct with proper titles
- The `UISponsorLegislation` action generates the correct options format
- The WebSocket communication properly transmits the data to the frontend

**Resolution:** The backend code was already correct. The issue was resolved by ensuring users clear their browser cache and restart the server to get the latest frontend JavaScript. The fix ensures that when users select "Sponsor Legislation", they see properly formatted options like:
- Infrastructure Bill (Cost: 5 PC)
- Protect The Children! (Cost: 5 PC)
- Change the Tax Code (Cost: 10 PC)
- Military Funding (Cost: 8 PC)
- Healthcare Overhaul (Cost: 15 PC)

## 5. Recent Fix (2025-07-28)

**Round Advancement Fix:** The game was getting stuck in Round 1 because there was no logic to detect when all players had used their action points and trigger the upkeep phase. This was particularly problematic for the web version deployed to Render.

**Solution:** Added logic in `engine/engine.py` in the `process_action` method to check if all players have 0 action points after a player's turn ends. When this condition is met, the game automatically triggers the upkeep phase, which:
- Advances the round marker
- Refreshes all players' action points to 2
- Runs the event phase for the new round
- Returns control to the human player

This fix ensures the game can progress through multiple rounds and terms as intended.

## 6. Declare Candidacy Fix (2025-01-27)

**Issue:** The "Declare Candidacy" action was not available to human players in Round 4, despite being a core game mechanic. This prevented players from running for office, which is essential for winning the game.

**Root Cause Analysis:** The problem was in the `get_valid_actions` method in `engine/engine.py`. While the logic for checking if it was Round 4 was correct, the action was only being generated for AI players, not human players. Additionally, the action needed to be integrated into the two-step UI action system for consistency.

**Solution:** Implemented a comprehensive fix across multiple components:

**Backend Changes:**
- **Updated `engine/engine.py`**: Modified `get_valid_actions` to return `UIDeclareCandidacy` for human players in Round 4, while AI players continue to receive concrete `ActionDeclareCandidacy` actions
- **Updated `game_session.py`**: Added handling for `UIDeclareCandidacy` in `_handle_ui_action` to generate a list of available offices for the player to choose from
- **Updated `engine/ui_actions.py`**: Added `UIDeclareCandidacy` class to the UI action system
- **Updated `engine/actions.py`**: Fixed the `ACTION_CLASSES` dictionary to properly register all action subclasses

**Frontend Changes:**
- **Updated `static/app.js`**: Added case for `UIDeclareCandidacy` in `getActionDescription` to display the action correctly in the UI

**Testing:**
- **Added `test_declare_candidacy_flow`**: Created comprehensive test in `test_game_session.py` to verify the two-step flow works correctly
- **All tests passing**: Verified that the changes don't introduce regressions

**Quality Assurance:**
- All backend and frontend tests pass
- Solution maintains consistency with existing UI action patterns
- Provides proper two-step flow for office selection
- Maintains separation of concerns (UI actions for humans, concrete actions for AI)

This fix ensures the "Declare Candidacy" action is available to human players in Round 4 and works correctly with the web interface.

## 7. CLI Version Removal (2025-01-27)

**Decision:** Removed the local CLI version of the game to simplify the project and avoid confusion. The web application now serves as the single interface for the game.

**Files Removed:**
- `main.py`: Entry point for the local CLI game
- `cli.py`: Command-line interface display and user input handling
- `human_vs_ai.py`: Game loop for human vs AI on command line
- `cli_game.py`: Main CLI game experience
- `test_cli_game.py`: Tests for the CLI game
- `test_end_to_end.py`: CLI-specific end-to-end tests

**Benefits:**
- Simplified project structure
- Reduced maintenance burden
- Clear focus on web application
- Eliminated potential confusion between CLI and web versions

## 8. Sponsor Legislation Fix (2025-01-27)

**Issue:** The "Sponsor Legislation" action was broken on the web version deployed to Render. When users selected this action, the game state would corrupt and display `undefined/4 Rounds`, making the game unplayable.

**Root Cause Analysis:** The problem was caused by multiple issues in the backend:
1. Missing imports in `game_session.py` causing `NameError`
2. Incomplete data structure - frontend couldn't display user-friendly names for legislation options
3. AI confusion - AI players were receiving UI-only actions that had no resolvers
4. Brittle action reconstruction - backend couldn't reliably reconstruct actions from user choices

**Solution:** Implemented a comprehensive fix across multiple components:

**Backend Changes:**
- **Fixed `game_session.py`**: Added missing imports, enhanced `_handle_ui_action` to provide richer data with `display_name` and `cost`, simplified `process_action` to handle user choices cleanly
- **Fixed `engine/engine.py`**: Modified `get_valid_actions` to differentiate between human and AI players - AI players receive concrete actions, human players receive UI actions
- **Created comprehensive tests**: Added `test_game_session.py` with robust unit tests validating the complete two-step flow

**Frontend Changes:**
- **Updated `static/app.js`**: Modified `promptForSubChoice` to use new `display_name` field, updated sub-choice handling to send correct `choice` format

**Quality Assurance:**
- All backend tests pass
- Solution is clean, simple, and robust
- Maintains separation of concerns (UI actions for humans, concrete actions for AI)
- Provides rich data structure for better UX
- Extensible pattern for future two-step actions

This fix ensures the "Sponsor Legislation" action works correctly on the web version deployed to Render.

## 8. Legislation Sponsorship and Support/Oppose Fix (2025-01-27)

**Issue:** Players could re-sponsor already active legislation and could not support or oppose their own sponsored bills, breaking the core game mechanics.

**Root Cause Analysis:**
1. **Re-sponsoring Active Bills:** The `get_valid_actions` method in `engine/engine.py` and the UI handling in `game_session.py` did not filter out already sponsored legislation when presenting sponsorship options.
2. **Cannot Support Own Bills:** The UI actions for support/oppose legislation were not implemented in `game_session.py`, preventing players from committing PC to any active bills.
3. **Serialization Issues:** The `PendingLegislation` class lacked a `to_dict()` method, causing tuple serialization errors, and `term_legislation` was not included in the game state sent to the frontend.

**Solution:** Implemented comprehensive fixes across multiple components:

**Backend Changes:**
- **Updated `engine/engine.py`**: Modified `get_valid_actions` to filter out already sponsored legislation when generating sponsorship options for both AI and human players
- **Updated `game_session.py`**:
  - Implemented `UISupportLegislation` and `UIOpposeLegislation` handlers in `_handle_ui_action`
  - Added support for legislation choice mapping in `process_action`
  - Added filtering to prevent re-sponsoring active legislation in the UI
- **Updated `models/game_state.py`**:
  - Added `to_dict()` method to `PendingLegislation` class for proper JSON serialization
  - Included `term_legislation` in `GameState.to_dict()` method

**Quality Assurance:**
- All backend tests continue to pass
- Solution maintains clean separation between UI actions and concrete game actions
- Fixes both server-side tuple errors and frontend JavaScript errors
- Enables proper two-step flow for legislation support/oppose actions
- Prevents duplicate sponsorship of active bills

This fix ensures players can properly sponsor legislation in one round and then support or oppose any active legislation (including their own) in subsequent rounds, aligning with the physical game rules. 

## 9. Precise PC Commitment System (2025-01-27)

**Issue:** Players were limited to committing fixed amounts of Political Capital (PC) when supporting or opposing legislation, which limited strategic depth and didn't align with the physical game's design where players can commit any amount of PC they choose.

**Root Cause Analysis:** The existing two-step UI action system only handled the selection of which bill to support/oppose, but then defaulted to committing 1 PC regardless of the player's choice. The system lacked a third step to prompt for the specific amount of PC to commit.

**Solution:** Implemented a comprehensive three-step action flow for supporting and opposing legislation:

**Backend Changes:**
- **Enhanced `game_session.py`**: 
  - Refactored the `_process_pending_action` method to handle multi-step flows with a `step` field
  - Added support for `choose_entity` (select bill) and `choose_amount` (specify PC amount) steps
  - Implemented validation to ensure the committed amount is within the player's available PC
  - Added the `expects_input` flag to the state payload sent to the frontend
- **Updated `_handle_ui_action`**: Modified to create pending actions with proper step tracking for support/oppose legislation

**Frontend Changes:**
- **Enhanced `static/app.js`**: 
  - Added logic to detect when the backend expects free-form numeric input (`expects_input === "amount"`)
  - Implemented proper parsing and validation of numeric input for PC amounts
  - Added error handling for invalid amounts with user-friendly prompts

**Quality Assurance:**
- All existing functionality continues to work (sponsor legislation, declare candidacy)
- New three-step flow: 1) Choose action, 2) Select bill, 3) Specify PC amount
- Proper validation ensures players cannot commit more PC than they have
- Clean error handling with helpful prompts for invalid input
- Maintains consistency with existing UI patterns

**User Experience:**
Players now experience a natural flow:
1. Select "Support Legislation" or "Oppose Legislation"
2. Choose which bill to influence from the available options
3. Enter the exact amount of PC to commit (e.g., "25" for 25 PC)
4. The system validates the input and processes the action

This enhancement significantly improves strategic depth by allowing players to make precise risk/reward decisions about their PC commitments, aligning with the physical game's design philosophy. 