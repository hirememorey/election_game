# LLM Handoff Context: Political Board Game Project

## 🎯 Project Overview

**What this is:** A Python-based political strategy board game with a Flask backend and mobile-friendly web frontend. Players compete in elections through strategic actions, resource management, and political maneuvering.

**Current State:** Fully functional game with rich mechanics and a completely redesigned strategic web interface. **All major bugs have been fixed and new features are fully tested.** **The UI has been overhauled to a three-zone layout for strategic clarity.**

**Architecture:** Clean separation between game logic (Python) and presentation (HTML/CSS/JS), with REST API communication.

## 📝 Recent Gameplay/Codebase Changes (Latest Updates)

### Strategic Three-Zone UI Overhaul (LATEST - Just Completed)
- **Complete UI Redesign**: Implemented a new three-zone layout to enhance strategic decision-making. The vintage poster aesthetic has been streamlined to prioritize clarity.
  - **Zone 1: Player Dashboard (Footer)**: A persistent bottom bar showing the current player's critical stats: Name, Archetype, Mandate, PC, AP (as a meter), and a list of held Favors.
  - **Zone 2: Main Stage (Center)**: The primary interactive area. It displays available actions, event cards, and contextual UI for legislation and trading. It also contains the scrollable Game Log.
  - **Zone 3: Intelligence Briefing (Header)**: A top bar containing a global Game Status Ticker (Round, Phase, Mood) and compact summary cards for all opponents, showing their public PC, favor count, and held offices.
  - **Impact**: Provides players with all necessary information at a glance, separating personal status, global context, and available actions to reduce cognitive load and improve strategic planning.
  - **Status**: Fully implemented and tested with a new smoke test (`test_new_ui_layout.py`).

- **Removed Complex Styling**: The previous "Vintage Political Poster" and "Apple-level" design systems have been replaced with a cleaner, more direct grid-based layout that is more maintainable.

- **JS Refactoring**: The `script.js` file was completely refactored. The monolithic `updateGameDisplay()` function was replaced with modular functions for each zone: `renderPlayerDashboard()`, `renderMainStage()`, and `renderIntelligenceBriefing()`.

### Round 5 Confusion Fix (Previously)
- **Fixed Round Logic**: Legislation session now triggers at the END of round 4, not beginning of round 5.
  - **Files Modified**: `engine/engine.py`

### Recent Critical Bug Fixes (Previously)
- **Trading Action Visibility Fix**: Fixed critical bug where trading actions weren't showing during legislation sessions.
- **Multiple Legislation Sponsorship Fix**: Fixed a bug that prevented players from sponsoring more than one piece of legislation per term.

### Major Gameplay Mechanics Overhaul (Previous)
- **Incumbent/Outsider Public Mood Logic**: Completely redesigned public mood effects to create strategic tension.
  - **Incumbents** (office-holders) **benefit** from **positive** public mood changes
  - **Outsiders** (non-office-holders) **benefit** from **negative** public mood changes
  - **Incumbents** **suffer** from **negative** public mood changes
  - **Outsiders** **suffer** from **positive** public mood changes
  - **Strategic Impact**: Creates natural tension between office-holders and challengers
  - **Motivation**: Incumbents want stability, outsiders want disruption
  - **Files Modified**: `engine/resolvers.py` - Added `apply_public_mood_effect()` function
  - **Updated Events**: Economic Boom, Recession Hits, Unexpected Surplus, Last Bill Hit/Dud, Tech Leap, Natural Disaster, Midterm Fury, Stock Crash, MEDIA_SPIN favor, successful legislation
  - **Testing**: All events now use the new logic with proper incumbent/outsider differentiation

- **Enhanced Turn Status Display**: Improved visual feedback for game state
  - **Phase-Specific Styling**: Different colors for each game phase (Event, Action, Legislation, Election)
  - **Player Information**: Clear display of current player with player number
  - **Action Points Counter**: Prominent display of remaining AP with visual indicators
  - **Turn Status Element**: New HTML element with enhanced styling and animations
  - **Files Modified**: `static/index.html`, `static/script.js`, `static/style.css`
  - **Impact**: Much clearer game state communication and better user experience

- **Action Points System Frontend**: Enhanced UI for the Action Points system
  - **AP Display**: More prominent visual display with gradient background
  - **Action Button Styling**: Better visual hierarchy with prominent AP costs
  - **Disabled State Handling**: Clear visual feedback when actions can't be performed
  - **AP Cost Indicators**: Each action shows its AP cost with enhanced styling
  - **Files Modified**: `static/style.css` - Enhanced AP display and action button styling
  - **Impact**: Better user experience for the Action Points system
  - **Status**: Fully implemented and working

- **Production Deployment**: Successfully deployed to Render with proper configuration
  - **Render Configuration**: Added `render.yaml` for automatic deployment
  - **Dynamic API URLs**: Updated frontend to work in both development and production
  - **Cache Busting**: Added version parameters to force browser cache updates
  - **Test Endpoint**: Added `/api/test` endpoint for deployment verification
  - **Files Modified**: `render.yaml`, `static/script.js`, `static/index.html`, `server.py`
  - **Deployment URL**: https://election-game.onrender.com
  - **Status**: Successfully deployed and accessible

- **Game Data Alignment**: Updated `game_data.py` to match actual game mechanics
  - **Political Favors**: Updated descriptions to match actual implementation
  - **Event Cards**: Fixed problematic cards that referenced non-existent mechanics
  - **Scrutiny Cards**: Updated to be less restrictive and more balanced
  - **Alliance Cards**: Updated to be less restrictive and more balanced
  - **Files Modified**: `game_data.py` - Comprehensive updates to all card types
  - **Impact**: Game data now accurately reflects actual game mechanics

### Major Bug Fixes and Improvements (Previous)
- **Action Points System (Phase 2)**: Players now get 3 Action Points per turn instead of 1 action
  - **Multiple Actions Per Turn**: Players can take multiple actions until AP are exhausted
  - **Variable AP Costs**: Different actions cost different amounts of AP (1-2 AP)
  - **Campaign Action**: New 2 AP action to place influence for future elections
  - **Turn Advancement**: Turn only advances when AP are exhausted
  - **AP Validation**: Prevents actions when insufficient AP
  - **Files Modified**:
    - `models/game_state.py`: Added `action_points` and `campaign_influences` fields
    - `models/components.py`: Added `CampaignInfluence` dataclass
    - `engine/actions.py`: Added `ActionCampaign` class
    - `engine/resolvers.py`: Added `resolve_campaign()` function
    - `engine/engine.py`: Added AP costs, validation, and turn advancement logic
    - `server.py`: Added campaign action handling and state serialization
  - **Testing**: `test_action_points_system.py` provides comprehensive testing
  - **Impact**: Dramatically increases player autonomy and speeds up gameplay
  - **Frontend Status**: **COMPLETE** - Action points display and campaign UI fully implemented

- **Use Favor Action Fixed**: Players can now properly use political favors with a selection menu
  - **Frontend**: Added favor selection UI with `showFavorMenu()` function
  - **Backend**: Fixed favor resolution to properly consume favors and apply effects
  - **PEEK_EVENT Favor**: Now properly reveals the top event card title and description
  - **Files Modified**: `static/script.js`, `static/style.css`, `engine/resolvers.py`

- **PC Commitment System**: Players can now commit custom amounts of PC for strategic advantage
  - **Legislation Support/Oppose**: Players can commit any amount of PC (within their available PC) when supporting/opposing legislation
  - **Candidacy Commitment**: Players can commit additional PC when declaring candidacy for better election chances
  - **Frontend**: Added prompt dialogs for PC amount input
  - **Files Modified**: `static/script.js`, `engine/resolvers.py`

- **Automatic Event Phases**: Event cards are now automatically drawn at the start of each round and term
  - **No Manual Input Required**: Players no longer need to click "Draw Event Card"
  - **Smooth Game Flow**: Events are resolved automatically and effects applied immediately
  - **Files Modified**: `engine/engine.py` - Updated `run_upkeep_phase()` and `run_election_phase()`

- **Term Transition Fixes**: Fixed issues with game state carrying over between terms
  - **Legislation Cleanup**: `pending_legislation` is properly cleared at the start of new terms
  - **Player Index Reset**: `current_player_index` is properly reset for new terms
  - **State Cleanup**: All term-specific state is properly cleared between terms
  - **Files Modified**: `engine/engine.py` - Updated `run_election_phase()`

### Trading Mechanic Implementation (Previous)
- **Feature Added**: Players can now trade PC and favors during legislation sessions in exchange for votes
- **Trading Phase**: New phase added to legislation sessions where players can propose trades before voting
- **Trade Actions**: 
  - `ActionProposeTrade`: Offer PC/favors to another player for their vote
  - `ActionAcceptTrade`: Accept a trade offer from another player
  - `ActionDeclineTrade`: Decline a trade offer
  - `ActionCompleteTrading`: Complete trading turn and move to voting
- **Files Modified**:
  - `models/game_state.py`: Added `TradeOffer` dataclass and trading state tracking
  - `engine/actions.py`: Added new trading action classes
  - `engine/resolvers.py`: Added trading resolution logic (resolve_propose_trade, resolve_accept_trade, etc.)
  - `engine/engine.py`: Updated legislation session flow to include trading phase
  - `server.py`: Added trading API endpoints and state serialization
  - `static/script.js`: Added trading UI (propose trades, accept/decline offers, trading phase)
  - `static/style.css`: Added trading UI styles
- **Testing**: `test_trading_mechanic.py` provides comprehensive testing of the trading system
- **Impact**: Adds negotiation and deal-making to legislation sessions, increasing player interaction and strategic depth

### UI Improvements (Previous)
- **Conditional Action Display**: "Use Favor" action now only appears if the player has favors to use
- **Trading Interface**: Clean, intuitive UI for proposing and responding to trades
- **Mobile Responsive**: All new trading UI components are mobile-friendly
- **Favor Selection Menu**: Clean UI for selecting which favor to use
- **PC Commitment Prompts**: User-friendly prompts for entering PC amounts

### Form Alliance Action Removal (Previous)
- **Action Removed**: The "Form Alliance" action has been completely removed from the game for simplified testing
- **Files Modified**: 
  - `engine/actions.py`: Removed `ActionFormAlliance` class
  - `engine/resolvers.py`: Removed `resolve_form_alliance()` function and imports
  - `engine/engine.py`: Removed from action resolvers mapping
  - `server.py`: Removed API endpoint handling
  - `static/script.js`: Removed from frontend action buttons
  - `cli.py`: Removed from CLI menu and help text
- **Testing**: `test_form_alliance_removal.py` verifies the action is gone and other actions still work
- **Impact**: Players now have a simpler action set: Fundraise, Network, Sponsor Legislation, Declare Candidacy, Use Favor, Support/Oppose Legislation, Trading, Campaign

### Previous Major Fixes
- **Legislation Session Timing:**  
  Legislation is now only resolved at the end of the term, during a dedicated legislation session phase. All sponsored bills are queued in `term_legislation` and resolved together after all players have had a chance to vote. Legislation is not resolved after each round. The frontend and backend are both confirmed to follow this logic.
  - `pending_legislation` is only for the current round, and is moved to `term_legislation` at upkeep.
  - See `test_legislation_timing.py` for a test that verifies this flow.

- **Support/Oppose Legislation Restrictions:**  
  Support and oppose legislation actions are now restricted to only the legislation session phase (end of term). Players cannot support or oppose legislation during rounds 1-3. This prevents premature legislation resolution and ensures all players have a chance to vote on bills during the dedicated session.

- **Frontend/Backend Sync:**  
  The UI and backend are now fully aligned on the legislation session mechanic. The frontend only displays voting options for unresolved legislation during the session, not after each round. Between rounds, queued legislation is not shown unless in the session.

## 🏗️ Technical Architecture

### Backend (Python/Flask)
- **`server.py`**: Flask app serving API endpoints and static files
- **`engine/`**: Core game logic
  - `engine.py`: Main game engine orchestrating turns and phases (updated with automatic event phases)
  - `actions.py`: Action definitions (fundraise, network, legislation, etc.)
  - `resolvers.py`: Action resolution logic (comprehensive game mechanics with favor fixes and incumbent/outsider logic)
- **`models/`**: Data structures
  - `game_state.py`: Game state management (with trading and term transition fixes)
  - `components.py`: Game components (players, offices, etc.)
  - `cards.py`: Card definitions and effects
- **`game_data.py`**: Game data loading and configuration (updated to match actual mechanics)

### Frontend (HTML/CSS/JS)
- **`static/index.html`**: Main game interface (Apple-level design)
- **`static/script.js`**: Game logic and API communication (updated with favor menu, PC commitment, and dynamic API URLs)
- **`static/style.css`**: Apple-inspired design system with SF Pro Display typography

### Deployment Configuration
- **`render.yaml`**: Render deployment configuration for automatic deployment
- **`Procfile`**: Heroku compatibility as backup deployment option
- **Dynamic API URLs**: Frontend automatically detects development vs production environment
- **Cache Busting**: Version parameters force browser cache updates

### API Endpoints
- `POST /api/game`: Create new game
- `GET /api/game/<id>`: Get game state
- `POST /api/game/<id>/action`: Process player action
- `POST /api/game/<id>/event`: Run event phase (now automatic)
- `DELETE /api/game/<id>`: Delete game
- `GET /api/test`: Test endpoint for deployment verification

## 🎮 Core Game Mechanics

### Game Flow
1. **Setup**: 2-4 players, each with archetype and mandate
2. **Event Phase**: Random events affect all players (now automatic)
3. **Action Phase**: Players take turns performing actions using Action Points
4. **Resolution**: Actions resolve, game state updates
5. **Repeat**: Until election victory conditions met

### Current Available Actions
- **Fundraise** (1 AP): Gain Political Capital (PC) - 5 PC base, +2 for Fundraiser archetype, +10 with Hedge Fund Bro ally
- **Network** (1 AP): Gain 2 PC + 1-2 political favors
- **Sponsor Legislation** (2 AP): Create legislation for votes/mood (cost varies by legislation type)
- **Declare Candidacy** (2 AP): Run for office (Round 4 only, cost varies by office + optional PC commitment)
- **Use Favor** (0 AP): Strategic advantage actions (requires having political favors, now with selection menu)
- **Support/Oppose Legislation** (1 AP): Interactive legislation system with custom PC commitment (restricted to legislation session only)
- **Campaign** (2 AP): Place influence for future office elections (NEW)
- **Trading** (0 AP): Propose trades of PC/favors for votes during legislation sessions

### Incumbent/Outsider Public Mood System (NEW)
- **Incumbents** (office-holders) benefit from positive mood changes, suffer from negative
- **Outsiders** (non-office-holders) benefit from negative mood changes, suffer from positive
- **Strategic Tension**: Creates natural opposition between office-holders and challengers
- **Motivation**: Incumbents want stability, outsiders want disruption
- **Events Affected**: Economic Boom, Recession Hits, Unexpected Surplus, Last Bill Hit/Dud, Tech Leap, Natural Disaster, Midterm Fury, Stock Crash, MEDIA_SPIN favor, successful legislation

### Recent Major Improvements
1. **Action Points System**: Players get 3 AP per turn with variable costs for different actions
2. **Political Favors System**: Players can now use favors gained from networking with proper UI
3. **Trading Mechanic**: Players can negotiate deals during legislation sessions for votes
4. **Candidacy Timing**: Only one candidacy per round, prevents clutter
5. **Legislation Support/Opposition**: Players can support/oppose others' legislation with custom PC amounts
6. **Automatic Event Phases**: Smooth game flow with automatic event card drawing
7. **PC Commitment System**: Strategic depth through custom PC investment in actions
8. **Incumbent/Outsider Logic**: Strategic tension through public mood effects
9. **Enhanced UI**: Better turn status display and action points visualization
10. **Production Deployment**: Successfully deployed to Render with proper configuration

## 🚀 Current Status

### ✅ What's Working
- Complete game engine with all core mechanics
- Web interface with mobile responsiveness
- API communication between frontend/backend
- Static file serving (fixed from 404 issues)
- Performance tested (~5-10ms response times)
- All recent improvements integrated and tested
- Form Alliance action successfully removed for simplified testing
- **NEW: Trading mechanic fully implemented and tested**
- **NEW: Use Favor action fully functional with selection menu**
- **NEW: PC commitment system for legislation and candidacy**
- **NEW: Automatic event phases for smooth gameplay**
- **NEW: PEEK_EVENT favor properly reveals top event card**
- **NEW: Term transitions properly clean up game state**
- **NEW: All major bugs fixed and comprehensively tested**
- **NEW: Action Points system backend fully implemented and tested**
- **NEW: Incumbent/outsider public mood logic creates strategic tension**
- **NEW: Enhanced turn status display with phase-specific styling**
- **NEW: Production deployment on Render with proper configuration**
- **NEW: Game data aligned with actual game mechanics**

### 🔧 Technical Details
- **Port**: 5001 (configurable)
- **Dependencies**: Flask, flask-cors (see requirements.txt)
- **Storage**: In-memory game storage (production would need database)
- **CORS**: Enabled for development
- **Static Files**: Served from `/static/` directory
- **Deployment**: Successfully deployed to Render at https://election-game.onrender.com

### 📱 Frontend Features
- **Apple-Level Design System**: Professional, modern interface with SF Pro Display typography
- **Mobile-responsive design** with touch-friendly interactions
- **Real-time game state updates** with smooth animations
- **Context-aware action buttons** with proper states and feedback
- **Player favor management UI** with selection menu
- **Pending legislation display** with enhanced visual hierarchy
- **Turn-based action system** with Action Points visualization
- **Trading interface** with propose/accept/decline functionality
- **Conditional action display** (Use Favor only shows when available)
- **PC commitment prompts** for strategic actions
- **Enhanced turn status display** with phase-specific styling
- **Action Points visualization** with prominent display and cost indicators
- **Dynamic API URL detection** for development vs production
- **Modern card-based layout** with subtle shadows and hover effects
- **Enhanced accessibility** with proper contrast ratios and focus states

## 🧪 Testing Status

### Comprehensive Test Coverage
- **`test_action_points_system.py`**: Action Points system functionality
- **`test_trading_mechanic.py`**: Trading system functionality
- **`test_pc_commitment_and_term_transition.py`**: PC commitment and term transitions
- **`test_legislation_session_fix.py`**: Legislation session PC commitment
- **`test_automatic_event_phase.py`**: Automatic event phase functionality
- **`test_api.py`**: API endpoints and PEEK_EVENT favor
- **`test_form_alliance_removal.py`**: Verifies Form Alliance removal
- **`test_legislation_timing.py`**: Legislation session timing
- **`test_mood_system.py`**: Mood system functionality
- **`performance_test.py`**: Performance benchmarking
- **`test_new_ui_layout.py`**: A smoke test to ensure the core game loop works with the new UI.

### All Tests Passing
- ✅ Trading mechanic works correctly
- ✅ PC commitment system functions properly
- ✅ Term transitions clean up state correctly
- ✅ Automatic event phases work as expected
- ✅ Use Favor action with selection menu
- ✅ PEEK_EVENT favor reveals top event card
- ✅ No leftover legislation between terms
- ✅ Player index properly reset between terms
- ✅ Action Points system backend works correctly
- ✅ **NEW: Core game loop is verified with the new UI via `test_new_ui_layout.py`**.

## 🎯 Strategic Context for Next LLM

### Immediate Opportunities
1. **UI Polish & Animation**: The new layout is functional but spartan. It's a perfect canvas for adding targeted animations, better styling, and UX refinements to bring it to life without clutter.
2. **Game Balance Testing**: The new UI makes it easier to assess the game state. Now is the time for extensive playtesting to evaluate the balance of AP costs, PC commitment, and trading.
3. **Network Action Design Implementation**: See `NETWORK_ACTION_DESIGN.md` for detailed specifications on merging Network and Form Alliance actions into a single, more engaging action system.
4. **Database Integration**: Replace in-memory storage with persistent database.
5. **Multiplayer Real-time**: Add WebSocket support for live multiplayer
6. **Advanced AI**: Add AI opponents with strategic decision-making
7. **Game Variants**: Different election scenarios, rule sets
8. **Analytics**: Track game statistics and player behavior

### Technical Debt to Address
1. **Error Handling**: More robust error handling in API
2. **Validation**: Input validation and sanitization
3. **Testing**: Additional unit tests for edge cases
4. **Documentation**: API documentation and code comments
5. **Security**: Rate limiting, input validation

### Architecture Decisions Made
1. **Separation of Concerns**: Game logic separate from presentation
2. **REST API**: Stateless communication between frontend/backend
3. **Mobile-First**: Responsive design for mobile devices
4. **Extensible Actions**: Action system allows easy addition of new mechanics
5. **State Management**: Centralized game state with clear serialization
6. **Automatic Phases**: Event phases are automatic for smooth gameplay
7. **PC Commitment**: Strategic depth through custom PC investment
8. **Action Points**: Multiple actions per turn with variable costs

## 🔍 Key Files to Understand

### For Game Logic
- `engine/resolvers.py`: Contains all action resolution logic (updated with favor fixes)
- `engine/engine.py`: Main game flow and turn management (updated with automatic event phases)
- `models/game_state.py`: Data structures and state management (updated with trading and term transition fixes)

### For Frontend
- **`static/script.js`**: All frontend game logic and API calls, now refactored into modular, zone-based rendering functions.
- **`static/index.html`**: Game interface structure, now a simple three-zone layout.
- **`static/style.css`**: A new, simpler CSS file implementing the grid-based three-zone design.

### For API
- `server.py`: All API endpoints and request handling
- `game_data.py`: Game configuration and data loading

### For Testing
- `test_*.py`: Comprehensive test suite covering all major functionality
- All tests are passing and provide good coverage of recent changes

## 🛠️ Development Workflow

### Local Development Setup
```bash
# Clone and setup
git clone <repository>
cd election
pip install -r requirements.txt

# Start server (note: port 5000 may be in use by macOS AirPlay)
./start_server.sh
# or manually specify port
PORT=5001 python3 server.py

# Access at http://localhost:5001
```

### Development Environment Notes
- **Port Conflicts**: macOS AirPlay Receiver uses port 5000 by default. Use port 5001 or disable AirPlay in System Preferences
- **Dependencies**: Minimal - just Flask and flask-cors (see requirements.txt)
- **Python Version**: Tested with Python 3.8+
- **Browser Testing**: Chrome/Firefox recommended for development

### Testing Strategy
- **Run all tests**: `python3 test_*.py` to verify everything works
- **Individual tests**: Each test file focuses on specific functionality
- **Manual testing**: Use the web interface for UI testing
- **Performance testing**: `performance_test.py` for response time verification

### Code Organization Patterns
- **Actions**: Add new actions in `engine/actions.py`, implement resolution in `engine/resolvers.py`
- **Game State**: Modify `models/game_state.py` for new state properties
- **Frontend**: Update `static/script.js` for UI logic, `static/style.css` for styling
- **API**: Add endpoints in `server.py`
- **Testing**: Create test files following existing patterns (see test_*.py files)

### Adding New Actions (Step-by-Step)
1. **Define Action Class** in `engine/actions.py`:
   ```python
   @dataclass
   class ActionNewAction(Action):
       # Add any parameters needed
       pass
   ```

2. **Implement Resolver** in `engine/resolvers.py`:
   ```python
   def resolve_new_action(state: GameState, action: ActionNewAction) -> GameState:
       # Implement game logic
       return state
   ```

3. **Register in Engine** in `engine/engine.py`:
   ```python
   self.action_resolvers = {
       # ... existing actions
       "ActionNewAction": resolvers.resolve_new_action,
   }
   ```

4. **Add API Endpoint** in `server.py`:
   ```python
   elif action_type == 'new_action':
       action = ActionNewAction(player_id=player_id)
   ```

5. **Add Frontend Button** in `static/script.js`:
   ```javascript
   { type: 'new_action', label: 'New Action', description: 'Description' }
   ```

6. **Test**: Create a test file following existing patterns

### Deployment
- `DEPLOYMENT.md`: Detailed deployment instructions
- Supports Render, Netlify, Heroku, Railway
- Static file serving configured correctly

## 🎯 Recommended Next Steps

### High Impact, Low Effort
1. **UI Polish**: The new layout is a functional wireframe. The top priority is to apply high-quality styling, transitions, and responsive design improvements to make it visually appealing.
2. **Extensive Playtesting**: Test the game flow and balance with the new, clearer UI.
3. **Balance Adjustments**: Fine-tune AP costs and PC commitment amounts based on playtesting.
4. **Consider Network Action Design**: If Form Alliance is missed, implement the merged Network/Alliance system from `NETWORK_ACTION_DESIGN.md`
5. **Add Sound Effects**: Audio feedback for actions
6. **Game Settings**: Configurable game parameters
7. **Re-enable Form Alliance**: If testing shows simplified actions work well

### Medium Impact, Medium Effort
1. **Database Integration**: PostgreSQL/MongoDB for persistence
2. **User Accounts**: Player registration and profiles
3. **Game Replays**: Watch previous games
4. **Advanced AI**: Smarter computer opponents
5. **Network Action Design**: Implement the merged Network/Alliance system

### High Impact, High Effort
1. **Real-time Multiplayer**: WebSocket-based live games
2. **Mobile App**: Native iOS/Android apps
3. **Advanced Analytics**: Game statistics and insights
4. **Modding System**: User-created content

## 🔧 Technical Patterns to Follow

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
- **Simplified action set** (no Form Alliance) may need balance adjustments

### Potential Balance Issues
- PC commitment amounts may need tuning based on playtesting
- Trading mechanic may need balance adjustments
- Random events could be too swingy
- Player interaction could be enhanced
- **Missing Form Alliance** reduces strategic options - consider Network Action Design

## 📚 Documentation References

- `GAME_IMPROVEMENTS.md`: Recent feature additions and improvements
- `NETWORK_ACTION_DESIGN.md`: Detailed design for merging Network and Form Alliance actions
- `FRONTEND_IMPLEMENTATION_GUIDE.md`: Action Points system frontend implementation

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
- **Multiple actions per turn with Action Points**

## 🚨 Known Issues & Limitations

### Current Limitations
- **In-memory Storage**: Game state is lost on server restart (production needs database)
- **Single Session**: No persistent user accounts or game history
- **No AI Opponents**: All players must be human (or use CLI for testing)
- **Limited Analytics**: No game statistics or performance tracking
- **Missing Form Alliance**: Strategic depth reduced - consider Network Action Design
- **Trading Balance**: Trading mechanic may need balance adjustments based on playtesting
- **PC Commitment Balance**: PC commitment amounts may need tuning
- **Frontend Implementation**: Action Points UI needs completion (see `FRONTEND_IMPLEMENTATION_GUIDE.md`)

### Potential Issues to Watch
- **Port Conflicts**: macOS AirPlay can block port 5000
- **Browser Compatibility**: Tested primarily on Chrome/Firefox
- **Mobile Performance**: Large game states may impact mobile devices
- **Concurrent Games**: Multiple simultaneous games may impact performance
- **Trading Complexity**: Trading phase may slow down legislation sessions
- **PC Commitment UX**: Prompt dialogs may need refinement

### Recent Bug Fixes
- **Action Points System**: Backend fully implemented and tested
- **Use Favor Action**: Fixed to properly work with selection menu
- **PC Commitment**: Added custom PC amounts for legislation and candidacy
- **Automatic Event Phases**: Events now draw automatically
- **PEEK_EVENT Favor**: Now properly reveals top event card
- **Term Transitions**: Fixed state cleanup between terms
- **Legislation Timing**: Fixed premature legislation resolution
- **Support/Oppose Restrictions**: Now properly restricted to legislation session
- **Static File Serving**: Fixed 404 errors for CSS/JS files
- **Player Archetype Display**: Fixed missing archetype information in UI
- **Form Alliance Removal**: Successfully removed for simplified testing
- **Trading Implementation**: Successfully added trading mechanic with comprehensive testing
- **UI Overhaul**: Replaced the previous complex design with a clear, functional, three-zone strategic layout.

## 🎨 Frontend Implementation Requirements: Three-Zone Layout

### Overview
The frontend has been **completely refactored** to a three-zone layout. The previous implementation guides are now obsolete. The new system is simpler and more modular.

### How It Works

The `updateUi()` function in `static/script.js` is the new main rendering entry point. It calls three helper functions, one for each zone:

1.  **`renderIntelligenceBriefing()`**:
    *   Populates the top bar.
    *   Renders the `game-status-ticker` with the current round, phase, and public mood.
    *   Renders a summary card for each opponent in the `intelligence-briefing` div, showing their name, PC, favor count, and office.

2.  **`renderMainStage()`**:
    *   Populates the central content area.
    *   Renders the available action buttons in the `action-list` div based on the current game phase.
    *   Renders the game history into the `game-log` div.
    *   (This function will also be responsible for showing contextual UI like Event Cards or Trading menus in the future).

3.  **`renderPlayerDashboard()`**:
    *   Populates the sticky footer.
    *   Displays the current player's name, archetype, mandate, PC, and favors.
    *   Renders the visual AP meter (`#ap-meter`) showing spent and remaining Action Points.

### Files to Modify for UI Changes
- **`static/script.js`**: Modify the `render...` functions to change what's displayed.
- **`static/style.css`**: Modify the CSS to change the appearance and layout.
- **`static/index.html`**: Only modify this if you need to change the fundamental three-zone structure.

### Success Criteria
- Players can clearly see their own stats, opponent stats, and available actions in their dedicated zones.
- The UI is responsive and functional on mobile.
- The core game loop remains fast and bug-free.

## 🎯 Immediate Development Priorities

1. **UI Polish**: The new layout is a functional wireframe. The top priority is to apply high-quality styling, transitions, and responsive design improvements to make it visually appealing.
2. **Extensive Playtesting**: Test the game flow and balance with the new, clearer UI.
3. **Balance Adjustments**: Fine-tune AP costs and PC commitment amounts based on playtesting.
4. **Consider Network Action Design**: If Form Alliance is missed, implement the merged Network/Alliance system from `NETWORK_ACTION_DESIGN.md`
5. **Database Integration**: For production readiness
6. **Enhanced Testing**: More comprehensive unit tests for edge cases
7. **UI Polish**: Better visual feedback and animations

## [2024-07-07] Negative Favors System
- The Political Favors system now includes negative favors, which can impose temporary or strategic disadvantages on players.
- The backend tracks and resolves all negative favor effects, including debts, public gaffes, media scrutiny, compromising positions, and hot potato.
- The frontend visually distinguishes negative favors and provides special UI for player choices and targeting.
- See GAME_IMPROVEMENTS.md for rationale and details.

#### Media Scrutiny Favor Logic Fix (2024-07-07)
- Media Scrutiny now halves only the base 5 PC from Fundraise actions. Bonuses (archetype, allies) are added after halving. This matches the intended design and ensures consistent, fair application of the effect.

### [2024-07-08] Bug Fix: Skip Trading Button in Legislation Session
- Fixed a frontend bug where clicking "Skip Trading" during the legislation session did nothing and logged `Unknown action type: complete_trading` in the console. The frontend now correctly triggers the `complete_trading` action, allowing the game to proceed to the voting phase as intended.

---

**The project is in excellent shape with a solid foundation, clear architecture, and comprehensive improvements. The UI has been completely overhauled for strategic clarity and maintainability. The next LLM has a strong, simplified base to build upon. The most immediate opportunity is to add high-quality styling and animations to the new functional UI layout.**