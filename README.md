# LLM/Developer Handoff Context

## Project Overview
- **What it is:** A Python-based political board game, now with a Flask backend and a mobile-friendly web frontend.
- **Goal:** Make the game playable on iPhone (and other devices) via a web browser.

## Current State
- **Backend:** Flask API (`server.py`) exposes game logic and serves static files.
- **Frontend:** HTML/CSS/JS in `static/` folder, mobile-optimized, interacts with backend via REST API.
- **Game Logic:** All core logic is in Python (`engine/`, `models/`, etc.), reused from the CLI version.
- **Deployment:** Local server works on custom port (e.g., 5001). Deployment instructions are in `DEPLOYMENT.md`.

## Recent Issues & Next Steps
- **Static files 404:** When accessing `/`, the server returns 404 for `/script.js` and `/style.css`. Likely cause: Flask static file serving config.
- **Testing:** No automated tests for API or frontend yet. Manual testing is possible via browser.
- **API URL:** In `static/script.js`, `API_BASE_URL` is set to `http://localhost:5000/api` (should match backend port and deployment URL).

## Key Files
- `server.py`: Flask app, API endpoints, static file serving.
- `static/index.html`, `static/style.css`, `static/script.js`: Frontend.
- `engine/`, `models/`, `game_data.py`: Game logic and data.
- `DEPLOYMENT.md`: Deployment instructions for Render, Netlify, Heroku, Railway, and local testing.

## Immediate To-Dos
- **Fix static file serving:** Ensure `/script.js` and `/style.css` are served correctly (Flask's `static_folder` config or explicit routes).
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
- **Action Points System**: Players get 3 AP per turn with variable costs
- **Trading Mechanic**: Players can trade PC/favors for votes during legislation sessions
- **Political Favors System**: Players can use favors with selection menu
- **PC Commitment System**: Custom PC amounts for legislation and candidacy
- **Automatic Event Phases**: Events draw automatically for smooth gameplay
- **Term Transition Fixes**: Proper state cleanup between terms

### 🎮 Core Game Mechanics

**Available Actions:**
- **Fundraise** (1 AP): Gain Political Capital (PC)
- **Network** (1 AP): Gain PC and political favors
- **Sponsor Legislation** (2 AP): Create legislation for votes/mood
- **Declare Candidacy** (2 AP): Run for office (Round 4 only)
- **Use Favor** (0 AP): Strategic advantage actions with selection menu
- **Support/Oppose Legislation** (1 AP): Interactive legislation system with custom PC commitment
- **Campaign** (2 AP): Place influence for future elections
- **Trading** (0 AP): Propose trades of PC/favors for votes during legislation sessions

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
- `DELETE /api/game/<id>`: Delete game

## 🧪 Testing

### Comprehensive Test Coverage
- **`test_action_points_system.py`**: Action Points system functionality
- **`test_trading_mechanic.py`**: Trading system functionality
- **`test_pc_commitment_and_term_transition.py`**: PC commitment and term transitions
- **`test_automatic_event_phase.py`**: Automatic event phase functionality
- **`test_api.py`**: API endpoints and favor system
- **`test_legislation_timing.py`**: Legislation session timing
- **`test_mood_system.py`**: Mood system functionality
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

### Action Points System (Phase 2)
- Players get 3 Action Points per turn instead of 1 action
- Multiple actions per turn until AP are exhausted
- Variable AP costs for different actions (1-2 AP)
- Campaign action for placing influence
- Automatic turn advancement when AP exhausted
- **Status**: Backend fully implemented, frontend enhanced with Apple-level design

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
- **Use Favor Action**: Fixed to work with selection menu
- **PC Commitment**: Added custom PC amounts for legislation and candidacy
- **Automatic Event Phases**: Events now draw automatically
- **Term Transitions**: Fixed state cleanup between terms
- **Legislation Timing**: Fixed premature legislation resolution
- **Static File Serving**: Fixed 404 errors for CSS/JS files
- **Round 5 Confusion**: ✅ **RESOLVED** - Legislation session now triggers at end of round 4
- **Action Point Handling**: ✅ **RESOLVED** - Clear UI and Pass Turn functionality added

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