# Election Game - Major Improvements & Features

## 🎯 Overview

This document tracks the major improvements and features that have been implemented in the Election game. The game has evolved from a basic CLI game to a sophisticated web-based political strategy game with rich mechanics.

## ✅ Recently Implemented Features

### [2025-07-15] Event Log Collapse with 'More' Button (Mobile Usability)
**Status:** Completed and deployed

**What it does:**
- Collapses the event log to a single line showing only the latest entry, with a 'More' button to view the full log in a modal.
- Prevents the event log from covering or pushing down action buttons on mobile.
- Dramatically improves mobile usability and declutters the main game screen.

**Technical Implementation:**
- Updated `static/script.js` to show only the latest log entry and a 'More' button.
- Added `showFullGameLog()` to display all log entries in a modal using the existing modal system.
- Updated `static/style.css` to style the single-line log and 'More' button for mobile.

**Impact:**
- Action buttons are always visible and accessible on mobile.
- Players can still access the full event log at any time via the 'More' button.

### [2025-07-14] Mobile Swipe Gesture Fix (CRITICAL)
**Status:** Completed and deployed

**What it does:**
- **Fixes critical mobile usability issue** where swipe-up gestures were interfering with action visibility
- Disables swipe gestures on mobile devices (width ≤ 600px) to prevent interference with action buttons
- Adds dedicated identity button (🎭) in header for easy access to player identity information
- Replaces problematic quick access panel with modal-based identity display on mobile
- Ensures all action buttons remain visible and accessible on mobile devices

**Technical Implementation:**
- Added `isMobileDevice()` function to detect mobile screens (width ≤ 600px)
- Modified touch event listeners to return early on mobile devices
- Added identity button to header in `static/index.html`
- Enhanced `showIdentityInfo()` function to display comprehensive modal with identity and game log
- Disabled quick access panel on mobile via CSS (`display: none !important`)
- Added mobile-specific modal styles for better usability

**Impact:**
- **Resolves critical mobile usability issue** - all actions now clearly visible
- **Improves mobile user experience** with dedicated identity access
- **Maintains desktop/tablet functionality** - swipe gestures still work on larger screens
- **Enhances accessibility** with clear, non-interfering mobile interface

### [2025-07-14] Mobile UI Optimization (CSS)
**Status:** Completed and deployed

**What it does:**
- Adds new mobile-specific CSS for better spacing, button sizing, and log handling on small screens.
- Prevents the game log from overlapping with action buttons.
- Reduces excessive vertical spacing and scrolling.
- Improves header icon sizing and spacing for touch.
- Ensures the UI adapts well to both small and very small screens.

**Technical Implementation:**
- Added new `@media (max-width: 600px)` and `@media (max-width: 400px)` rules to `static/style.css`.
- Action buttons/cards are more compact and easier to tap.
- Game log is more readable and does not overlap with actions.
- Header icons are easier to tap and not crowded.

**Impact:**
- Dramatically improves mobile usability and visual polish.
- Reduces the need for scrolling and makes the UI feel more app-like.

### 1. **🤫 Secret Commitment Legislation System** - COMPLETED
**Status**: **COMPLETED** - Fully implemented and tested, replaces previous "Gambling-Style" system.

**What it does**:
- Elevates the legislation phase from a resource race to a high-stakes game of political poker, bluffing, and betrayal.
- **Secret Contributions**: Players no longer commit PC publicly. All contributions to support or oppose legislation are made secretly.
- **Bluffing & Betrayal**: Enables advanced strategies where players can publicly promise support while secretly opposing a bill, or bluff about the amount of their contribution to force other players to spend their resources.
- **Dramatic Reveals**: At the end of a term, all secret contributions are revealed simultaneously, creating climactic moments of truth and shocking betrayals.
- **Strategic Depth**: Success now depends on a player's ability to read their opponents and manage trust, not just on the size of their treasury.

**Technical Implementation (COMPLETED):**
- **Backend**: `SECRET_COMMITMENTS` storage in `server.py` holds secret commitments separate from main `GameState`
- **Action Processing**: `support/oppose` actions store commitments in secret storage, no public state changes
- **Legislation Resolution**: `resolve_legislation` function reveals all secret commitments dramatically at term end
- **Frontend**: Enhanced UI with secret commitment notices and confirmation messages for acting players
- **Testing**: Comprehensive test coverage validates all secret commitment scenarios

**Files Modified**:
- `server.py`: Added `SECRET_COMMITMENTS` storage and updated action processing
- `engine/resolvers.py`: Updated support/oppose resolvers to validate actions without changing public state
- `static/script.js`: Enhanced UI with secret commitment notices and confirmation messages
- `static/style.css`: Added styling for secret commitment notices
- `test_secret_commitment_system.py`: Comprehensive test coverage

**Impact**: Fundamentally shifts the game's focus towards social deduction and player interaction, creating dramatic moments of revelation and betrayal.

### 2. **Action Points System (Phase 2)** - COMPLETED
**Status**: Backend fully implemented and tested, frontend enhanced with Apple-level design

**What it does**:
- Players get 2 Action Points per turn instead of 1 action
- Multiple actions per turn until AP are exhausted
- Variable AP costs for different actions (1-2 AP)
- Campaign action for placing influence for future elections
- Automatic turn advancement when AP exhausted
- AP validation prevents actions when insufficient AP

**Technical Implementation**:
- `models/game_state.py`: Added `action_points` and `campaign_influences` fields
- `models/components.py`: Added `CampaignInfluence` dataclass
- `engine/actions.py`: Added `ActionCampaign` class
- `engine/resolvers.py`: Added `resolve_campaign()` function
- `engine/engine.py`: Added AP costs, validation, and turn advancement logic
- `server.py`: Added campaign action handling and state serialization

**Testing**: `test_action_points_system.py` provides comprehensive testing
**Impact**: Dramatically increases player autonomy and speeds up gameplay
**Frontend Status**: **ENHANCED** - Apple-level design system implemented

### 3. **Trading Mechanic** - REMOVED
**Status**: Successfully removed to streamline gameplay

**What it did**:
- Players could trade PC and favors during legislation sessions
- Trading phase before voting in legislation sessions
- Propose, accept, decline trade offers
- Strategic negotiation for votes

**Why removed**:
- Simplified the legislation session flow
- Reduced complexity for better game balance
- Legislation now resolves immediately after the action phase
- Streamlined gameplay experience

**Technical Changes**:
- `models/game_state.py`: Removed `TradeOffer` dataclass and trading state tracking
- `engine/actions.py`: Removed trading action classes
- `engine/resolvers.py`: Removed trading resolution logic
- `engine/engine.py`: Updated legislation session flow to remove trading phase
- `server.py`: Removed trading API endpoints
- `static/script.js`: Removed trading UI
- `static/style.css`: Removed trading UI styles

**Impact**: Simplified legislation sessions for faster, more focused gameplay

### 4. **🏛️ Enhanced Election Results Display** - COMPLETED
**Status**: **COMPLETED** - Fully implemented and tested

**What it does**:
- Provides detailed election results showing dice rolls, PC bonuses, and final scores
- Displays results for all contested offices in a single view
- Clean, card-based layout with clear winner highlighting
- Responsive design with clear visual hierarchy

**Technical Implementation**:
- **Backend**: Enhanced election resolution with detailed logging in `engine/resolvers.py`
- **Frontend**: Parses game log to extract and display election results in `static/script.js`
- **UI**: Added `parseElectionResults()` function and enhanced `showElectionPhaseUI()`
- **CSS**: Added election results styling in `static/style.css`

**Features**:
- **Dice Rolls**: Shows the actual dice roll for each candidate
- **PC Bonuses**: Displays committed PC converted to election bonuses
- **Final Scores**: Shows total scores and highlights the winner
- **Visual Design**: Clean, card-based layout with clear winner highlighting
- **Multiple Offices**: Displays results for all contested offices in a single view

**Files Modified**:
- `static/script.js`: Added election results parsing and display logic
- `static/style.css`: Added election results styling
- `engine/resolvers.py`: Enhanced election logging for detailed results

**Impact**: Provides players with clear, detailed feedback on election outcomes, enhancing the strategic understanding of the game

### 5. **Political Favors System** - COMPLETED
**Status**: Fully implemented and tested

**What it does**:
- Players can use favors gained from networking
- Selection menu for different favor types
- PEEK_EVENT favor reveals top event card
- Favors are consumed when used
- **New:** Negative favors (e.g., Political Debt, Public Gaffe, Media Scrutiny, Compromising Position, Political Hot Potato) are applied immediately when drawn and are never kept in hand. Players cannot choose to use them; the effect is automatic. The frontend no longer shows negative favors in the favor menu.

**Negative Favors List:**
- **Political Debt:** You owe a political debt to another player. They can force you to abstain or vote with them on future legislation.
- **Public Gaffe:** Your next public action (Sponsor Legislation, Declare Candidacy, or Campaign) costs +1 AP due to damage control.
- **Media Scrutiny:** For the remainder of this round, all PC gained from Fundraise actions is halved (rounded down).
- **Compromising Position:** Choose one: discard two of your Political Favors, or reveal your Player Archetype to all players. (If drawn, archetype is revealed automatically.)
- **Political Hot Potato:** You've been handed a politically toxic dossier. Pass this card to another player. Whoever holds it when the next Upkeep Phase begins loses 5 Influence. (If drawn, it is immediately passed to a random other player.)

**Technical Implementation**:
- `engine/resolvers.py`: Negative favors are now applied immediately in `resolve_network()`
- `static/script.js`: Favor menu only shows positive favors
- `engine/actions.py`: Added `ActionUseFavor` class
- `engine/resolvers.py`: Added `resolve_use_favor()` with different favor effects
- `server.py`: Added favor action handling
- `static/script.js`: Added favor selection UI with `showFavorMenu()` function
- `static/style.css`: Added favor menu styles

**Testing**: `test_api.py` includes favor system testing
**Impact**: Adds strategic depth to networking actions

### 6. **PC Commitment System** - COMPLETED
**Status**: Fully implemented and tested

**What it does**:
- Custom PC amounts for legislation support/opposition
- Additional PC commitment for candidacy declarations
- Strategic depth through resource investment

**Technical Implementation**:
- `engine/resolvers.py`: Updated legislation and candidacy resolvers to accept custom PC amounts
- `static/script.js`: Added prompt dialogs for PC amount input
- `static/style.css`: Added dialog styling

**Testing**: `test_pc_commitment_and_term_transition.py` provides comprehensive testing
**Impact**: Adds strategic depth to legislation and candidacy actions

### 7. **Automatic Event Phases** - COMPLETED
**Status**: Fully implemented and tested

**What it does**:
- Events draw automatically at start of each round/term
- No manual intervention required
- Smooth game flow

**Technical Implementation**:
- `engine/engine.py`: Updated `run_upkeep_phase()` and `run_election_phase()` to automatically draw events

**Testing**: `test_automatic_event_phase.py` provides comprehensive testing
**Impact**: Eliminates manual event drawing, improves game flow

### 8. **Term Transition Fixes** - COMPLETED
**Status**: Fully implemented and tested

**What it does**:
- Proper state cleanup between terms
- Legislation cleanup: `pending_legislation` is properly cleared
- Player index reset: `current_player_index` is properly reset
- All term-specific state is properly cleared

**Technical Implementation**:
- `engine/engine.py`: Updated `run_election_phase()` to properly clean up state

**Testing**: `test_pc_commitment_and_term_transition.py` includes term transition testing
**Impact**: Prevents state corruption between terms

### 9. **Legislation Session Timing** - COMPLETED
**Status**: Fully implemented and tested

**What it does**:
- Legislation is only resolved at the end of the term during a dedicated session
- All sponsored bills are queued in `term_legislation` and resolved together
- Support/Oppose actions are restricted to legislation session only

**Technical Implementation**:
- `engine/engine.py`: Updated legislation flow to use dedicated session
- `static/script.js`: Updated frontend to only show voting during session

**Testing**: `test_legislation_timing.py` provides comprehensive testing
**Impact**: Ensures all players have a chance to vote on bills

### 10. **Form Alliance Action Removal** - COMPLETED
**Status**: Successfully removed for simplified testing

**What it does**:
- Removed Form Alliance action to simplify the action set
- Players now have: Fundraise, Network, Sponsor Legislation, Declare Candidacy, Use Favor, Support/Oppose Legislation, Trading, Campaign

**Technical Implementation**:
- `engine/actions.py`: Removed `ActionFormAlliance` class
- `engine/resolvers.py`: Removed `resolve_form_alliance()` function
- `engine/engine.py`: Removed from action resolvers mapping
- `server.py`: Removed API endpoint handling
- `static/script.js`: Removed from frontend action buttons
- `cli.py`: Removed from CLI menu

**Testing**: `test_form_alliance_removal.py` verifies the action is gone
**Impact**: Simplified action set for easier testing and balance

### 11. **Round 5 Confusion Fix** - COMPLETED
**Status**: Fully implemented and tested

**What it does**:
- Fixes the confusing round 5 state where legislation session would trigger
- Legislation session now triggers at the END of round 4 (not beginning of round 5)
- Clear game flow: Rounds 1-4 = actions, then legislation session, then elections
- Improved legislation session UI with clear trading and voting phases
- Added Pass Turn functionality for better user experience

**Technical Implementation**:
- `engine/engine.py`: Fixed round logic in `run_upkeep_phase()` to trigger legislation at end of round 4
- `engine/engine.py`: Enhanced `run_legislation_session()` to clear action points during legislation
- `static/script.js`: Added phase-specific UI for legislation sessions
- `static/script.js`: Added Pass Turn button when players have 0 AP
- `static/style.css`: Added styling for legislation session UI components

**Testing**: Manual testing confirms improved game flow
**Impact**: Much clearer game flow and better user experience

### 12. **Action Points System Fixes** - COMPLETED
**Status**: Fully implemented and tested

**What it does**:
- Fixed AP management during legislation session voting phase
- Fixed AP management during election phase
- Ensures players can vote on legislation during legislation sessions
- Ensures players can declare candidacy during election phase
- Proper AP granting at phase transitions

**Technical Implementation**:
- `engine/engine.py`: Added AP granting (1 AP) at start of voting phase in legislation session
- `engine/engine.py`: Added AP granting (3 AP) at start of election phase
- `test_pc_commitment_and_term_transition.py`: Updated to properly advance through trading phase before voting

**Testing**: `test_pc_commitment_and_term_transition.py` now passes all tests
**Impact**: Resolves AP validation errors and ensures smooth gameplay flow

### 13. **🎰 Gambling-Style Legislation System** - DEPRECATED
**Status**: Replaced by the **Secret Commitment Legislation System**.
**What it did**:
- Allowed players to commit PC to support/oppose legislation during any turn.
- Featured risk/reward mechanics with a tiered system for "bets".
- Offered a bonus to the legislation's sponsor on success and a penalty on failure.
- **Reason for deprecation**: While functional, this system promoted a "who has more money" dynamic. The new Secret Commitment system promotes more engaging social deduction, bluffing, and strategic depth.

### Frontend Legislation Menu Race Condition Fix
- The support/oppose legislation menus now always fetch the latest game state before displaying options, preventing bugs where players saw 'no pending legislation' due to stale state.
- This ensures menus are always accurate and up-to-date.

### [2025-07-14] Action Points Bugfix for Support/Oppose Legislation
**Status:** Completed and tested

**What it does:**
- Fixes a bug where supporting or opposing legislation did not consume Action Points (AP), allowing players to exceed their per-turn AP limit.
- Now, both support and oppose actions properly consume 1 AP each, and the turn advances to the next player when a player's AP reaches 0.
- Test coverage improved: Automated tests now verify that AP is consumed and the turn advances as expected after these actions.

**Technical Implementation:**
- Updated `server.py` to ensure support/oppose actions are processed through the engine, which handles AP validation and deduction.
- Confirmed in `engine/engine.py` that AP costs are correct and turn advancement is automatic when AP reaches 0.
- Updated test script (`test_ap_fix.py`) to reflect the correct turn advancement behavior and AP consumption.

**Impact:**
- Prevents players from exceeding their AP limit per turn.
- Ensures consistent and fair turn order and resource management.
- Automated tests now pass for AP consumption and turn advancement for support/oppose legislation actions.

## 🎮 Gameplay Improvements

### Enhanced Strategic Depth
- **Multiple Actions Per Turn**: Action Points system allows multiple actions per turn
- **Resource Management**: PC commitment system adds strategic investment decisions
- **Negotiation**: Trading mechanic adds deal-making to legislation sessions
- **Favor Strategy**: Political favors provide strategic advantages
- **Campaign Planning**: Campaign action allows influence placement for future elections

### Improved Game Flow
- **Automatic Events**: No manual event drawing required
- **Smooth Transitions**: Proper state cleanup between terms
- **Clear Phases**: Legislation sessions are clearly defined
- **Better Feedback**: Enhanced UI with action costs and turn status
- **Apple-Level Design**: Professional, modern interface with excellent user experience
- **Clear Round Logic**: No more round 5 confusion - legislation triggers at end of round 4
- **Pass Turn Functionality**: Players can always advance their turn, even with 0 AP

### Enhanced Player Interaction
- **Trading**: Players can negotiate deals during legislation sessions
- **Legislation Support/Opposition**: Players can support or oppose others' legislation
- **Strategic Alliances**: PC commitment allows for strategic cooperation

## 🧪 Testing Coverage

### Comprehensive Test Suite
- **`test_action_points_system.py`**: Action Points system functionality
- **`test_trading_mechanic.py`**: Trading system functionality
- **`test_pc_commitment_and_term_transition.py`**: PC commitment and term transitions
- **`test_automatic_event_phase.py`**: Automatic event phase functionality
- **`test_api.py`**: API endpoints and favor system
- **`test_legislation_timing.py`**: Legislation session timing
- **`test_mood_system.py`**: Mood system functionality
- **`test_form_alliance_removal.py`**: Verifies Form Alliance removal
- **`performance_test.py`**: Performance benchmarking
- **`test_ap_fix.py`**: Action Points bugfix testing

### All Tests Passing
- ✅ Trading mechanic works correctly
- ✅ PC commitment system functions properly
- ✅ Term transitions clean up state correctly
- ✅ Automatic event phases work as expected
- ✅ Use Favor action with selection menu
- ✅ PEEK_EVENT favor reveals top event card
- ✅ No leftover legislation between terms
- ✅ Player index properly reset between terms
- ✅ AP consumption and turn advancement for support/oppose legislation actions are fixed

### 🧪 Automated Frontend Testing (COMPLETED)
**Status**: **COMPLETED** - Comprehensive Playwright tests validate game playability

**What it does**:
- **Full Game Flow Validation**: Tests complete game flow from creation to term transitions
- **Cross-Browser Compatibility**: Tests pass on Chromium, Firefox, and WebKit
- **Stuck Prevention**: Ensures game never gets stuck when players have no valid actions
- **Secret Commitment Validation**: Tests verify secret commitment mechanics work correctly
- **Error Handling**: Validates proper error messages for invalid actions
- **Performance**: All tests complete in under 6 seconds per browser

**Technical Implementation**:
- **Playwright Integration**: Comprehensive automated testing using Playwright
- **Test Coverage**: `tests/election-game.spec.ts` provides full frontend validation
- **Test Scenarios**:
  - Full game flow is playable and never gets stuck
  - Secret commitment system works correctly
  - Game never gets stuck when players have no valid actions
  - Error handling works correctly

**Files Added**:
- `tests/election-game.spec.ts`: Comprehensive Playwright test suite
- `playwright.config.ts`: Playwright configuration
- `package.json`: Added Playwright dependencies

**Impact**: Provides confidence that the game is stable and playable across different browsers and scenarios, preventing regressions and ensuring quality.

## 🎯 Strategic Implications

### Action Points System
- **Player Autonomy**: Players have more control over their turn
- **Strategic Planning**: Multiple actions allow for complex strategies
- **Resource Management**: AP costs create strategic trade-offs
- **Campaign Planning**: Campaign action allows long-term planning

### Trading Mechanic
- **Negotiation**: Players must negotiate for votes
- **Risk/Reward**: Trading involves strategic risk assessment
- **Player Interaction**: Encourages communication and deal-making
- **Legislation Strategy**: Trading affects legislation outcomes

### Political Favors
- **Strategic Depth**: Favors provide unique advantages
- **Resource Management**: Favors are limited and must be used strategically
- **Information Advantage**: PEEK_EVENT favor provides information advantage
- **Networking Value**: Makes networking action more valuable

### PC Commitment System
- **Strategic Investment**: Players must decide how much PC to commit
- **Risk Assessment**: Higher commitments mean higher risk/reward
- **Legislation Strategy**: Support/opposition amounts affect outcomes
- **Candidacy Strategy**: Additional PC can improve election chances

## 🚀 Performance Improvements

### Response Times
- **API Endpoints**: ~5-10ms response times
- **Game State Updates**: Efficient state management
- **Frontend Performance**: Optimized UI updates
- **Mobile Responsiveness**: Touch-friendly interface

### Code Quality
- **Clean Architecture**: Separation of concerns between frontend/backend
- **Comprehensive Testing**: All major features have test coverage
- **Error Handling**: Robust error handling in API
- **Documentation**: Clear documentation for all features

## 🎯 Next Development Priorities

### High Priority
1. **Frontend Implementation**: Complete Action Points system UI (see `FRONTEND_IMPLEMENTATION_GUIDE.md`)
2. **Extensive Playtesting**: Test Action Points and trading systems thoroughly
3. **Balance Adjustments**: Fine-tune AP costs and PC commitment amounts based on playtesting

### Medium Priority
1. **Network Action Design**: Implement merged Network/Alliance system from `NETWORK_ACTION_DESIGN.md`
2. **Database Integration**: Replace in-memory storage with persistent database
3. **Enhanced Testing**: More comprehensive unit tests for edge cases
4. **UI Polish**: Better visual feedback and animations

### Low Priority
1. **Game Variants**: Different election scenarios, rule sets
2. **Analytics**: Track game statistics and player behavior
3. **Mobile App**: Native iOS/Android apps
4. **Advanced AI**: Add AI opponents with strategic decision-making

## 🔧 Technical Patterns Established

### Action System
- All game actions inherit from base `Action` class
- Actions are processed through `engine.process_action()`
- Resolution logic in `resolvers.py` maintains consistency
- Follow the pattern in `test_form_alliance_removal.py` for adding/removing actions

### State Management
- Game state is immutable (new state created for each action)
- Clear serialization for API communication
- State includes all necessary game information
- Term transitions properly clean up state

### Frontend-Backend Communication
- REST API with JSON payloads
- Frontend polls for state updates
- Error handling with user-friendly messages
- PC commitment uses prompt dialogs for user input

### Mobile Responsiveness
- CSS Grid and Flexbox for layouts
- Touch-friendly button sizes
- Responsive typography and spacing
- Favor selection menu is mobile-friendly

## 🎮 Game Balance Considerations

### Current Balance
- Political Capital (PC) is the primary resource
- Actions have clear costs and benefits
- Random events add unpredictability
- Favor system adds strategic depth
- **PC commitment system adds strategic depth**
- **Trading mechanic adds negotiation**
- **Action Points system adds player autonomy**

### Potential Balance Issues
- PC commitment amounts may need tuning based on playtesting
- Trading mechanic may need balance adjustments
- Random events could be too swingy
- Player interaction could be enhanced
- **Missing Form Alliance** reduces strategic options - consider Network Action Design

## 📚 Documentation References

- `LLM_HANDOFF_CONTEXT.md`: Comprehensive project context and recent changes
- `FRONTEND_IMPLEMENTATION_GUIDE.md`: Action Points system frontend implementation
- `NETWORK_ACTION_DESIGN.md`: Detailed design for merging Network and Form Alliance actions
- `DEPLOYMENT.md`: Deployment instructions for various platforms

## 🎯 Success Metrics

### Technical
- Response times under 50ms
- Zero 404 errors for static files
- All API endpoints working correctly
- Mobile compatibility across devices
- **All tests passing**

### Gameplay
- Engaging strategic depth
- Balanced action choices
- Clear player feedback
- Smooth game flow
- **Successful negotiation and deal-making during legislation sessions**
- **Strategic PC commitment decisions**
- **Smooth automatic event phases**

## [2024-07-07] Major Update: Negative Favors System

#### Media Scrutiny Fix (2024-07-07)
- The Media Scrutiny negative favor now halves only the base 5 PC from Fundraise actions. Any bonuses (such as archetype or ally bonuses) are added after halving the base amount. This ensures the effect is fair and consistent with the intended design.

### Overview
A new set of **negative Political Favors** has been added to the game to balance the Network action and introduce meaningful risk/reward. Players who Network now have a chance to draw negative favors, which introduce temporary or strategic disadvantages.

### New Negative Favors
- **Political Debt:** Owe a political debt to another player, who can force you to abstain or vote with them on legislation.
- **Public Gaffe:** Your next public action (Sponsor Legislation, Declare Candidacy, or Campaign) costs +1 AP.
- **Media Scrutiny:** All PC gained from Fundraise actions this round is halved.
- **Compromising Position:** Choose to discard two Political Favors or reveal your Archetype to all players.
- **Political Hot Potato:** Pass this to another player; whoever holds it at Upkeep loses 5 Influence.

### Rationale
- **Strategic Depth:** Players must now weigh the risk of drawing a negative favor when Networking, making Fundraising a more attractive and safe alternative in some situations.
- **Player Interaction:** Negative favors often involve other players, increasing negotiation, leverage, and emergent diplomacy.
- **Game Balance:** The Network action is no longer strictly superior to Fundraising, and the overall favor economy is more dynamic.

### Implementation Notes
- All negative favors are fully integrated in both backend and frontend.
- The UI visually distinguishes negative favors and provides special handling for choices (e.g., Compromising Position).
- Comprehensive tests confirm the new system works as intended.

## [2024-07-08] Bug Fix: Skip Trading Button in Legislation Session

- Fixed a frontend bug where clicking "Skip Trading" during the legislation session did nothing and logged `Unknown action type: complete_trading` in the console.
- The frontend now correctly triggers the `complete_trading` action, allowing the game to proceed to the voting phase as intended.

---

**The game has evolved significantly with rich mechanics, comprehensive testing, and a solid foundation for future development. All major features are implemented and tested, with clear next steps for continued improvement.** 🗳️ 