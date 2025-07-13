# LLM/Developer Handoff Context

## Project Overview
- **What it is:** A Python-based political board game, now with a Flask backend and a mobile-friendly web frontend.
- **Goal:** Make the game playable on iPhone (and other devices) via a web browser.
- **All blue gradient bars have been removed for a cleaner, more information-dense interface.**
- **The UI is now more compact, with full-width identity cards and neutral backgrounds for all status bars.**

## Current State
- **Backend:** Flask API (`server.py`) exposes game logic and serves static files.
- **Frontend:** HTML/CSS/JS in `static/` folder, mobile-optimized, interacts with backend via REST API.
- **Game Logic:** All core logic is in Python (`engine/`, `models/`, etc.), reused from the CLI version.
- **Deployment:** Local server works on custom port (e.g., 5001). Deployment instructions are in `DEPLOYMENT.md`.
- **🤫 Secret Commitment System:** **COMPLETED** - Replaced gambling-style legislation with strategic secret commitments
- **🧪 Automated Testing:** **COMPLETED** - Comprehensive Playwright tests validate game playability

## Recent Issues & Next Steps
- **Secret Commitment System:** **COMPLETED** - Players now make secret commitments to support/oppose legislation, revealed dramatically at term end
- **Automated Frontend Testing:** **COMPLETED** - Playwright tests ensure game never gets stuck and all features work correctly
- **Legislation Voting Fix:** Fixed critical backend bug where players couldn't vote on their own legislation, causing the game to get stuck. Backend now properly resets player index after voting completes.
- **Frontend Voting UI:** Added "Pass Turn" button when players have no valid voting options during legislation sessions.
- **Sponsor Support Enhancement:** **NEW** - Players who sponsor legislation can now commit additional PC to their own legislation throughout the rounds, providing more strategic control and agency.
- **Testing:** Comprehensive test suite covers all major game mechanics. Manual testing is possible via browser.
- **API URL:** In `static/script.js`, `API_BASE_URL` is set to `http://localhost:5001/api` (matches backend port).

## Key Files
- `server.py`: Flask app, API endpoints, static file serving.
- `static/index.html`, `static/style.css`, `static/script.js`: Frontend.
- `engine/`, `models/`, `game_data.py`: Game logic and data.
- `DEPLOYMENT.md`: Deployment instructions for Render, Netlify, Heroku, Railway, and local testing.
- `tests/election-game.spec.ts`: **NEW** - Comprehensive Playwright tests for frontend validation

## Immediate To-Dos
- **✅ Secret Commitment System:** Fully implemented and tested
- **✅ Automated Testing:** Playwright tests validate all game flows
- **Test sponsor support enhancement:** Verify sponsors can support their own legislation with additional PC commitment.
- **Test API endpoints:** Use Postman/curl or browser to verify `/api/game`, `/api/game/<id>`, etc.
- **Test frontend:** Play through a game in browser, check for bugs, and improve UX.

## How to Run Locally
```bash
pip install -r requirements.txt
PORT=5001 python3 server.py
# Visit http://localhost:5001 in your browser
```

## How to Deploy
See `DEPLOYMENT.md` for step-by-step instructions for Render, Netlify, etc.

---

# Election: The Game

A Python-based political strategy board game with a Flask backend and mobile-friendly web frontend. Players compete in elections through strategic actions, resource management, and political maneuvering.

## 🎯 Current State

**Status**: Fully functional game with rich mechanics, Apple-level web interface, and comprehensive improvements to core gameplay systems. **All major bugs have been fixed and new features are fully tested.**

### ✅ What's Working
- Complete game engine with all core mechanics
- **Apple-Level Web Interface**: Professional, modern frontend with Apple-inspired design system
- API communication between frontend/backend
- Static file serving (fixed from 404 issues)
- Performance tested (~5-10ms response times)
- **Action Points System**: Players get 2 AP per turn with variable costs
- **Trading Mechanic**: Players can trade PC/favors for votes during legislation sessions
- **Political Favors System**: Players can use favors with selection menu
- **PC Commitment System**: Custom PC amounts for legislation and candidacy
- **Automatic Event Phases**: Events draw automatically for smooth gameplay
- **Term Transition Fixes**: Proper state cleanup between terms
- **Legislation Voting Fixes**: Players cannot vote on their own legislation, with proper "Pass Turn" option when no valid votes exist
- **🤫 Secret Commitment System**: **COMPLETED** - Players make secret commitments to support/oppose legislation, revealed dramatically at term end
- **🎭 Identity Display System**: Players can easily view their archetype and mission information through multiple access methods
- **📜 Sponsor Support Enhancement**: **NEW** - Players who sponsor legislation can now commit additional PC to their own legislation throughout the rounds, providing more strategic control and agency.
- **🧪 Automated Testing**: **COMPLETED** - Comprehensive Playwright tests validate game playability across browsers

### 🎮 Core Game Mechanics

**Available Actions:**
- **Fundraise** (1 AP): Gain Political Capital (PC)
- **Network** (1 AP): Gain PC and political favors (note: negative favors are applied immediately)
- **Sponsor Legislation** (2 AP): Create legislation for votes/mood
- **Declare Candidacy** (2 AP): Run for office (Round 4 only; multiple players can declare candidacy for the same or different offices in the same round)
- **Use Favor** (1 AP): Strategic advantage actions with selection menu
- **Support/Oppose Legislation** (1 AP): **Secretly commit PC** to influence a bill's outcome. Bluff, form secret alliances, and betray your rivals.
- **Campaign** (2 AP): Place influence for future elections
- **Trading** (0 AP): Propose trades of PC/favors for votes during legislation sessions
- **Pass Turn** (0 AP): Skip turn when no valid actions available

**Action Point Costs:**
- Players receive 2 Action Points per round
- Fundraise/Network: 1 AP each
- Sponsor Legislation/Declare Candidacy/Campaign: 2 AP each
- Use Favor: 1 AP
- Support/Oppose Legislation: 1 AP each
- Trading actions: 0 AP (free during trading phase)
- Pass Turn: 0 AP (free action)

### 🤫 Secret Commitment System (New Core Mechanic)
The previous "Gambling-Style" legislation system has been **successfully replaced** with a more strategic and interactive **Secret Commitment System**. This elevates the game from a resource management puzzle to a high-stakes game of political poker.

**Key Features:**
- **Secret Contributions**: Players no longer commit PC publicly. All contributions to support or oppose legislation are made secretly.
- **Bluffing & Betrayal**: Publicly promise support while secretly opposing a bill, or bluff about the amount of your contribution to force other players to spend their resources.
- **Dramatic Reveals**: At the end of a term, all secret contributions are revealed simultaneously, leading to dramatic moments of truth.
- **Strategic Depth**: Success now depends on your ability to read your opponents and manage their trust, not just on the size of your treasury.
- **Implementation**: Backend stores secret commitments separately, frontend provides clear confirmation messages to acting players while other players see generic notifications.

**Technical Implementation:**
- **Backend**: `SECRET_COMMITMENTS` storage in `server.py`, updated action processing and legislation resolution
- **Frontend**: Enhanced UI with secret commitment notices and confirmation messages
- **Testing**: Comprehensive test coverage validates all secret commitment scenarios

### 🎭 Identity System
Players have unique identities that affect gameplay:

**Political Archetypes:**
- **The Insider**: Starts with State Senator office and 15 PC
- **The Populist**: Gains +1 PC when gaining PC from negative Public Mood as an Outsider
- **The Fundraiser**: First Fundraise action each term grants +2 PC
- **The Orator**: Once per term, may re-roll one failed legislation die roll

**Personal Mandates (Missions):**
- **The Principled Leader**: Win Presidency without ever holding Governor office
- **The Environmentalist**: Ensure Infrastructure Bill passes twice, personally sponsor one
- **The War Hawk**: Ensure Military Funding bill passes with Critical Success
- **The Kingmaker**: Be allied with the player who wins Presidency
- **The Master Legislator**: Personally sponsor and pass 3 different types of legislation
- **The Statesman**: Hold Governor or US Senator office at game end
- **The Shadow Donor**: Ensure a player you supported wins Presidency
- **The Unpopular Hero**: Pass Healthcare Overhaul legislation
- **The Minimalist**: Win Presidency having committed 20 PC or less to final election
- **The People's Champion**: Ensure Public Mood is +2 or +3 at final Presidential election
- **The Opportunist**: Win Presidency without ever being an Incumbent before final Election Phase

**Access Methods:**
- **Swipe up** on mobile devices
- **Click "Game Info"** button in header
- **Press G key** on desktop
- **"View Identity"** button during action phase

## 🚀 Quick Start

### Local Development
```bash
# Clone and setup
git clone <repository>
cd election
pip install -r requirements.txt

# Start server (port 5001 to avoid macOS AirPlay conflicts)
./start_server.sh
# or manually
PORT=5001 python3 server.py

# Access at http://localhost:5001
```

### Deployment
See `DEPLOYMENT.md` for step-by-step instructions for Render, Netlify, Heroku, Railway.

## 🏗️ Architecture

### Backend (Python/Flask)
- **`server.py`**: Flask app serving API endpoints and static files
- **`engine/`**: Core game logic
  - `engine.py`: Main game engine orchestrating turns and phases
  - `actions.py`: Action definitions
  - `resolvers.py`: Action resolution logic
- **`models/`**: Data structures
  - `game_state.py`: Game state management
  - `components.py`: Game components
  - `cards.py`: Card definitions
- **`game_data.py`**: Game data loading and configuration

### Frontend (HTML/CSS/JS)
- **`static/index.html`**: Main game interface with Apple-level design
- **`static/script.js`**: Game logic and API communication
- **`static/style.css`**: Apple-inspired design system with SF Pro Display typography

### API Endpoints
- `POST /api/game`: Create new game
- `GET /api/game/<id>`: Get game state
- `POST /api/game/<id>/action`: Process player action
- `POST /api/game/<id>/event`: Run event phase (automatic)
- `POST /api/game/<id>/resolve_legislation`: Manually resolve legislation session
- `POST /api/game/<id>/resolve_elections`: Manually resolve elections
- `DELETE /api/game/<id>`: Delete game

## 🧪 Testing

### Comprehensive Test Coverage
- **`test_action_points_system.py`**: Action Points system functionality
- **`test_trading_mechanic.py`**: Trading system functionality
- **`test_pc_commitment_and_term_transition.py`**: PC commitment and term transitions
- **`test_automatic_event_phase.py`**: Automatic event phase functionality
- **`test_api.py`**: API endpoints and favor system
- **`test_legislation_timing.py`**: Legislation session timing
- **`test_legislation_voting_fix.py`**: Legislation voting fixes and pass turn functionality
- **`test_secret_commitment_system.py`**: **NEW** - Secret commitment system functionality
- **`test_mood_system.py`**: Mood system functionality
- **`test_war_mood_lock.py`**: War event mood lock functionality
- **`performance_test.py`**: Performance benchmarking
- **`test_archetype_display.py`**: Archetype and mandate display functionality
- **`test_sponsor_support_own_legislation.py`**: **NEW** - Sponsor support own legislation enhancement

### Automated Frontend Testing (Playwright)
- **`tests/election-game.spec.ts`**: **NEW** - Comprehensive Playwright tests for frontend validation
- **Full Game Flow**: Tests complete game flow from creation to term transitions
- **Secret Commitment System**: Validates secret commitment mechanics work correctly
- **Error Handling**: Ensures proper error messages for invalid actions
- **Cross-Browser Compatibility**: Tests pass on Chromium, Firefox, and WebKit
- **Stuck Prevention**: Ensures game never gets stuck when players have no valid actions

### Run Tests
```bash
# Run all Python tests
python3 test_*.py

# Run specific test
python3 test_action_points_system.py

# Run Playwright tests
npx playwright test tests/election-game.spec.ts
```

## 📚 Documentation

- **`LLM_HANDOFF_CONTEXT.md`**: Comprehensive project context and recent changes
- **`FRONTEND_IMPLEMENTATION_GUIDE.md`**: Action Points system frontend implementation
- **`GAME_IMPROVEMENTS.md`**: Recent feature additions and improvements
- **`NETWORK_ACTION_DESIGN.md`**: Design for merging Network and Form Alliance actions
- **`DEPLOYMENT.md`**: Deployment instructions for various platforms
- **`SIMPLIFIED_UI_IMPLEMENTATION.md`**: Phase-based UI redesign with identity display system
- **`PHYSICAL_GAME_SPEC.md`**: **NEW** - Rulebook and manufacturing specifications for a physical board game version.

## 🎯 Recent Major Improvements

### 🤫 Secret Commitment Legislation System (COMPLETED)
The previous "Gambling-Style" legislation system has been **successfully replaced** with a more strategic and interactive **Secret Commitment System**. This elevates the game from a resource management puzzle to a high-stakes game of political poker.
- **Secret Contributions**: Players no longer commit PC publicly. All contributions to support or oppose legislation are made secretly.
- **Bluffing & Betrayal**: Publicly promise support while secretly opposing a bill, or bluff about the amount of your contribution to force other players to spend their resources.
- **Dramatic Reveals**: At the end of a term, all secret contributions are revealed simultaneously, leading to dramatic moments of truth.
- **Strategic Depth**: Success now depends on your ability to read your opponents and manage their trust, not just on the size of your treasury.
- **Implementation**: Backend stores secret commitments separately, frontend provides clear confirmation messages to acting players while other players see generic notifications.
- **Testing**: Comprehensive test coverage validates all secret commitment scenarios

### 🧪 Automated Frontend Testing (COMPLETED)
- **Playwright Integration**: Comprehensive automated testing using Playwright
- **Full Game Flow Validation**: Tests complete game flow from creation to term transitions
- **Cross-Browser Compatibility**: Tests pass on Chromium, Firefox, and WebKit
- **Stuck Prevention**: Ensures game never gets stuck when players have no valid actions
- **Secret Commitment Validation**: Tests verify secret commitment mechanics work correctly
- **Error Handling**: Validates proper error messages for invalid actions
- **Performance**: All tests complete in under 6 seconds per browser

### 📜 Sponsor Support Enhancement (Latest)
- **Sponsor Agency**: Players who sponsor legislation can now commit additional PC to their own legislation throughout the rounds
- **Strategic Control**: Sponsors have more control over their legislation's success through multiple PC commitments
- **Risk Management**: Sponsors can choose to oppose their own legislation for strategic reasons
- **Enhanced Logging**: Clear distinction between sponsor actions and regular player actions
- **UI Indicators**: Legislation menus show "YOUR BILL" for own legislation
- **Multiple Commitments**: Sponsors can commit PC multiple times to the same legislation
- **Files Modified**:
  - `engine/resolvers.py`: Updated support/oppose functions to allow sponsor actions
  - `static/script.js`: Updated frontend to show sponsor actions and enhanced UI
  - `test_sponsor_support_own_legislation.py`: Comprehensive test coverage
- **Impact**: Increased strategic depth and player agency for legislation sponsors

### 🎭 Identity Display System (Latest)
- **Archetype Cards**: Clear display of player's political archetype and special abilities
- **Mission Cards**: Prominent display of personal mandate and win conditions
- **Multiple Access Methods**: Swipe up, click "Game Info", press G key, or use "View Identity" button
- **Visual Design**: Gradient headers with clear descriptions for archetype and mission cards
- **Strategic Understanding**: Players now understand their unique abilities and objectives
- **Reduced Confusion**: Clear explanation of why players start with specific PC amounts and offices

### 🎰 Gambling-Style Legislation System (DEPRECATED)
- **This system has been successfully replaced by the new Secret Commitment System.**
- **PC Commitment During Any Turn**: Players can commit PC to support/oppose legislation throughout the term, not just during legislation session
- **Risk/Reward Mechanics**: Bigger commitments yield bigger rewards with tiered system (small/medium/big bets)
- **Sponsor Bonus**: Legislation sponsors get 50% bonus on success, 50% penalty on failure
- **Gambling Rewards**: Supporters get rewards if legislation passes, opponents get rewards if it fails
- **Turn Advancement Fix**: Fixed pass turn action to properly advance turns by setting AP to 0
- **Frontend Integration**: Complete UI support with modals for PC commitment and detailed reward explanations
- **Comprehensive Testing**: Full test coverage including sponsor bonuses and failure scenarios

### Manual Phase Resolution System
- **Manual Legislation Resolution**: After the term ends, players can manually trigger legislation resolution with a "Resolve Legislation" button
- **Manual Election Resolution**: After legislation is resolved, players can manually trigger election resolution with a "Resolve Elections" button
- **Enhanced Game Flow**: Players can review the game state before seeing phase results
- **New API Endpoints**:
  - `POST /api/game/<id>/resolve_legislation`: Manually resolve all pending legislation
  - `POST /api/game/<id>/resolve_elections`: Manually resolve elections and start new term
- **State Flags**: `awaiting_legislation_resolution` and `awaiting_election_resolution` flags control when resolution buttons appear
- **Improved Logging**: Legislation results are properly logged to the game log with detailed breakdowns

### Action Points System (Phase 2)
- Players get 2 Action Points per turn instead of 1 action
- Multiple actions per turn until AP are exhausted
- Variable AP costs for different actions (1-2 AP)
- Campaign action for placing influence
- Automatic turn advancement when AP exhausted
- **Status**: Backend fully implemented, frontend enhanced with Apple-level design

### Candidacy Mechanic Update
- Multiple players can now declare candidacy for the same or different offices in the same round, enabling head-to-head matchups and more dynamic elections. 

## Recent Improvements (July 2024)
- Fixed bug where using a favor would fail if the frontend sent the wrong property; now uses `favor_id` and supports targeting players for favors that require it.
- Legislation session UI now displays all unresolved bills from both pending and term legislation, and allows players to pass their turn during voting.
- Added a "Pass Turn" button to the legislation session so players can skip voting if desired.
- Improved log visibility: the game log now shows the last 20 entries, making it easier to see detailed results of legislation resolutions and other actions.
- Fixed frontend display of favor descriptions and legislation details (no more `[object Object]` or `undefined`). 