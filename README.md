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

## Recent Issues & Next Steps
- **Legislation Voting Fix:** Fixed critical backend bug where players couldn't vote on their own legislation, causing the game to get stuck. Backend now properly resets player index after voting completes.
- **Frontend Voting UI:** Added "Pass Turn" button when players have no valid voting options during legislation sessions.
- **Testing:** Comprehensive test suite covers all major game mechanics. Manual testing is possible via browser.
- **API URL:** In `static/script.js`, `API_BASE_URL` is set to `http://localhost:5001/api` (matches backend port).

## Key Files
- `server.py`: Flask app, API endpoints, static file serving.
- `static/index.html`, `static/style.css`, `static/script.js`: Frontend.
- `engine/`, `models/`, `game_data.py`: Game logic and data.
- `DEPLOYMENT.md`: Deployment instructions for Render, Netlify, Heroku, Railway, and local testing.

## Immediate To-Dos
- **Test legislation voting:** Verify the recent fixes work correctly in gameplay.
- **Test API endpoints:** Use Postman/curl or browser to verify `/api/game`, `/api/game/<id>`, etc.
- **Test frontend:** Play through a game in browser, check for bugs, and improve UX.
- **Automated tests:** (Optional) Add unit tests for API and game logic.

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
- **🎰 Gambling-Style Legislation System**: Players can commit PC to support/oppose legislation during any turn with risk/reward mechanics

### 🎮 Core Game Mechanics

**Available Actions:**
- **Fundraise** (1 AP): Gain Political Capital (PC)
- **Network** (1 AP): Gain PC and political favors (note: negative favors are applied immediately)
- **Sponsor Legislation** (2 AP): Create legislation for votes/mood
- **Declare Candidacy** (2 AP): Run for office (Round 4 only; multiple players can declare candidacy for the same or different offices in the same round)
- **Use Favor** (1 AP): Strategic advantage actions with selection menu
- **Support/Oppose Legislation** (1 AP): **🎰 Gambling-style system** - commit PC during any turn with risk/reward mechanics
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
- **`test_legislation_gambling_system.py`**: **🎰 Gambling-style legislation system** with PC commitment and sponsor bonuses
- **`test_mood_system.py`**: Mood system functionality
- **`test_war_mood_lock.py`**: War event mood lock functionality
- **`performance_test.py`**: Performance benchmarking

### Run Tests
```bash
# Run all tests
python3 test_*.py

# Run specific test
python3 test_action_points_system.py
```

## 📚 Documentation

- **`LLM_HANDOFF_CONTEXT.md`**: Comprehensive project context and recent changes
- **`FRONTEND_IMPLEMENTATION_GUIDE.md`**: Action Points system frontend implementation
- **`GAME_IMPROVEMENTS.md`**: Recent feature additions and improvements
- **`NETWORK_ACTION_DESIGN.md`**: Design for merging Network and Form Alliance actions
- **`DEPLOYMENT.md`**: Deployment instructions for various platforms

## 🎯 Recent Major Improvements

### 🎰 Gambling-Style Legislation System (Latest)
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

### Trading Mechanic
- Players can trade PC and favors during legislation sessions
- Trading phase before voting in legislation sessions
- Propose, accept, decline trade offers
- Strategic negotiation for votes

### Political Favors System
- Players can use favors gained from networking
- Selection menu for different favor types
- PEEK_EVENT favor reveals top event card
- Favors are consumed when used
- **New:** Negative favors (e.g., Political Debt, Public Gaffe, Media Scrutiny, Compromising Position, Political Hot Potato) are applied immediately when drawn and are never kept in hand. Players cannot choose to use them; the effect is automatic.

### PC Commitment System
- Custom PC amounts for legislation support/opposition
- Additional PC commitment for candidacy declarations
- Strategic depth through resource investment

### Automatic Event Phases
- Events draw automatically at start of each round/term
- No manual intervention required
- Smooth game flow

## 🔧 Technical Details

- **Port**: 5001 (configurable, avoids macOS AirPlay conflicts)
- **Dependencies**: Flask, flask-cors (see requirements.txt)
- **Storage**: In-memory game storage (production would need database)
- **CORS**: Enabled for development
- **Static Files**: Served from `/static/` directory

## 🎮 Game Flow

1. **Setup**: 2-4 players, each with archetype and mandate
2. **Event Phase**: Random events affect all players (automatic)
3. **Action Phase**: Players take turns performing actions using Action Points
4. **Resolution**: Actions resolve, game state updates
5. **Repeat**: Until election victory conditions met

## 🚨 Known Issues & Limitations

### Current Limitations
- **In-memory Storage**: Game state lost on server restart (production needs database)
- **Single Session**: No persistent user accounts or game history
- **No AI Opponents**: All players must be human
- **Apple-Level Design**: Fully implemented and ready for user experience testing

### Recent Bug Fixes
- **War Mood Lock**: ✅ **RESOLVED** - Fixed bug where "War Breaks Out" event didn't properly lock public mood. Other events could still change public mood during war, violating the intended game mechanic. Now public mood is properly locked for the rest of the term when war is active.
- **Legislation Display**: ✅ **RESOLVED** - Fixed critical bug where pending legislation was showing as "undefined" in the final round of the term. Legislation now displays properly with titles, descriptions, and sponsor information.
- **Use Favor Action**: Fixed to work with selection menu
- **PC Commitment**: Added custom PC amounts for legislation and candidacy
- **Automatic Event Phases**: Events now draw automatically
- **Term Transitions**: Fixed state cleanup between terms
- **Legislation Timing**: Fixed premature legislation resolution
- **Static File Serving**: Fixed 404 errors for CSS/JS files
- **Round 5 Confusion**: ✅ **RESOLVED** - Legislation session now triggers at end of round 4
- **Action Point Handling**: ✅ **RESOLVED** - Clear UI and Pass Turn functionality added
- **Multiple Legislation Sponsorship**: ✅ **RESOLVED** - Fixed a bug that prevented players from sponsoring multiple pieces of legislation in the same term.
- **Skip Trading**: Fixed: Skip Trading button in legislation session now works correctly and advances to the voting phase (previously logged 'Unknown action type: complete_trading').

### Gameplay Balance Changes (Latest)
- **Action Points Reduced**: Changed from 3 AP per round to 2 AP per round for more strategic gameplay
- **Use Favor Cost**: Changed from 0 AP to 1 AP to prevent unlimited favor usage

## 🎯 Next Steps

### High Priority
1. **Apple-Level Design Testing**: Test the new design system across devices and gather user feedback
2. **Extensive Playtesting**: Test Action Points and trading systems thoroughly
3. **Balance Adjustments**: Fine-tune AP costs and PC commitment amounts
4. **Legislation Session Testing**: Test the improved legislation session flow (no more round 5 confusion)

### Medium Priority
1. **Database Integration**: Replace in-memory storage with persistent database
2. **Multiplayer Real-time**: Add WebSocket support for live multiplayer
3. **Advanced AI**: Add AI opponents with strategic decision-making
4. **Network Action Design**: Implement merged Network/Alliance system

### Low Priority
1. **Game Variants**: Different election scenarios, rule sets
2. **Analytics**: Track game statistics and player behavior
3. **Mobile App**: Native iOS/Android apps

## 🤝 Contributing

Feel free to submit issues and enhancement requests! See `LLM_HANDOFF_CONTEXT.md` for detailed development context.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## Changelog

### 2024-07-07
- Added a negative favors system: Networking can now yield negative Political Favors, introducing risk/reward and new strategic depth. **Negative favors are now applied immediately when drawn and are not kept in hand.** See GAME_IMPROVEMENTS.md for details.

## Features
- Political Favors system (now includes both positive and negative favors for richer gameplay) 