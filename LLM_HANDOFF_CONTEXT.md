# LLM Handoff Context: Political Board Game Project

## 🎯 Project Overview

**What this is:** A Python-based political strategy board game with a Flask backend and mobile-friendly web frontend. Players compete in elections through strategic actions, resource management, and political maneuvering.

**Current State:** Fully functional game with rich mechanics, web interface, and comprehensive improvements to core gameplay systems. **All major bugs have been fixed and new features are fully tested.** **Action Points system backend is complete, frontend needs implementation.**

**Architecture:** Clean separation between game logic (Python) and presentation (HTML/CSS/JS), with REST API communication.

## 📝 Recent Gameplay/Codebase Changes (Latest Updates)

### Major Bug Fixes and Improvements (NEW - Latest)
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
  - **Frontend Status**: **NEEDS IMPLEMENTATION** - Action points display and campaign UI not yet added

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
  - `resolvers.py`: Action resolution logic (comprehensive game mechanics with favor fixes)
- **`models/`**: Data structures
  - `game_state.py`: Game state management (with trading and term transition fixes)
  - `components.py`: Game components (players, offices, etc.)
  - `cards.py`: Card definitions and effects
- **`game_data.py`**: Game data loading and configuration

### Frontend (HTML/CSS/JS)
- **`static/index.html`**: Main game interface
- **`static/script.js`**: Game logic and API communication (updated with favor menu and PC commitment)
- **`static/style.css`**: Mobile-responsive styling (updated with favor menu styles)

### API Endpoints
- `POST /api/game`: Create new game
- `GET /api/game/<id>`: Get game state
- `POST /api/game/<id>/action`: Process player action
- `POST /api/game/<id>/event`: Run event phase (now automatic)
- `DELETE /api/game/<id>`: Delete game

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

### Recent Major Improvements
1. **Action Points System**: Players get 3 AP per turn with variable costs for different actions
2. **Political Favors System**: Players can now use favors gained from networking with proper UI
3. **Trading Mechanic**: Players can negotiate deals during legislation sessions for votes
4. **Candidacy Timing**: Only one candidacy per round, prevents clutter
5. **Legislation Support/Opposition**: Players can support/oppose others' legislation with custom PC amounts
6. **Automatic Event Phases**: Smooth game flow with automatic event card drawing
7. **PC Commitment System**: Strategic depth through custom PC investment in actions

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

### 🔧 Technical Details
- **Port**: 5001 (configurable)
- **Dependencies**: Flask, flask-cors (see requirements.txt)
- **Storage**: In-memory game storage (production would need database)
- **CORS**: Enabled for development
- **Static Files**: Served from `/static/` directory

### 📱 Frontend Features
- Mobile-responsive design
- Real-time game state updates
- Context-aware action buttons
- Player favor management UI with selection menu
- Pending legislation display
- Turn-based action system
- Trading interface with propose/accept/decline functionality
- Conditional action display (Use Favor only shows when available)
- PC commitment prompts for strategic actions

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

## 🎯 Strategic Context for Next LLM

### Immediate Opportunities
1. **Frontend Implementation**: Complete the Action Points system UI (see `FRONTEND_IMPLEMENTATION_GUIDE.md`)
2. **Game Balance Testing**: The PC commitment system and trading mechanic are ready for extensive playtesting to evaluate balance
3. **Network Action Design Implementation**: See `NETWORK_ACTION_DESIGN.md` for detailed specifications on merging Network and Form Alliance actions into a single, more engaging action system
4. **Re-enable Form Alliance**: If testing shows the simplified action set works well, consider re-implementing Form Alliance or the merged Network design
5. **Database Integration**: Replace in-memory storage with persistent database
6. **Multiplayer Real-time**: Add WebSocket support for live multiplayer
7. **Advanced AI**: Add AI opponents with strategic decision-making
8. **Game Variants**: Different election scenarios, rule sets
9. **Analytics**: Track game statistics and player behavior

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
- `models/game_state.py`: Data structures and state management (updated with trading and term fixes)

### For Frontend
- `static/script.js`: All frontend game logic and API calls (updated with favor menu and PC commitment)
- `static/index.html`: Game interface structure
- `static/style.css`: Mobile-responsive styling (updated with favor menu styles)

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
1. **Frontend Implementation**: Complete Action Points system UI (see `FRONTEND_IMPLEMENTATION_GUIDE.md`)
2. **Game Balance Testing**: Extensive playtesting of PC commitment and trading systems
3. **Improve UI/UX**: Better visual feedback and animations
4. **Add Sound Effects**: Audio feedback for actions
5. **Game Settings**: Configurable game parameters
6. **Re-enable Form Alliance**: If testing shows simplified actions work well

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

## 🔄 Re-enabling Form Alliance (If Needed)

If you want to re-enable the Form Alliance action:

1. **Restore Action Class** in `engine/actions.py`:
   ```python
   @dataclass
   class ActionFormAlliance(Action):
       pass
   ```

2. **Restore Resolver** in `engine/resolvers.py`:
   ```python
   def resolve_form_alliance(state: GameState, action: ActionFormAlliance) -> GameState:
       # Copy from git history or NETWORK_ACTION_DESIGN.md
   ```

3. **Update Imports** in all affected files
4. **Restore Frontend Button** in `static/script.js`
5. **Restore CLI Option** in `cli.py`
6. **Test**: Run `test_form_alliance_removal.py` to verify restoration

## 🎨 Frontend Implementation Requirements: Action Points System

### Overview
The Action Points system has been fully implemented in the backend but **requires frontend implementation**. This is a high-priority task that will complete Phase 2 of the game refinements.

### What Needs to Be Implemented

#### 1. Action Points Display
**Location**: `static/script.js` - `updateActionButtons()` function
**Requirements**:
- Show remaining Action Points for current player
- Display AP costs for each action button
- Disable actions when insufficient AP
- Clear visual indication of whose turn it is

**Implementation Pattern**:
```javascript
// Add to updateActionButtons()
const currentPlayer = gameState.players[gameState.current_player_index];
const remainingAP = gameState.action_points[currentPlayer.id] || 3;

// Show AP display
const apDisplay = document.createElement('div');
apDisplay.className = 'action-points-display';
apDisplay.innerHTML = `
    <strong>${currentPlayer.name}'s Turn</strong><br>
    Action Points: ${remainingAP}/3
`;
actionList.appendChild(apDisplay);

// Update action buttons with AP costs
const actions = [
    { type: 'fundraise', label: 'Fundraise', ap_cost: 1, description: 'Gain Political Capital' },
    { type: 'network', label: 'Network', ap_cost: 1, description: 'Gain PC and favors' },
    { type: 'sponsor_legislation', label: 'Sponsor Legislation', ap_cost: 2, description: 'Create legislation' },
    { type: 'campaign', label: 'Campaign', ap_cost: 2, description: 'Place influence for future election' },
    // ... other actions
];

// Disable actions when insufficient AP
const canAfford = remainingAP >= action.ap_cost;
button.disabled = !canAfford;
```

#### 2. Campaign Action UI
**Location**: `static/script.js` - Add new action button and handler
**Requirements**:
- Office selection dropdown (STATE_SENATOR, CONGRESS_SEAT, GOVERNOR, US_SENATOR, PRESIDENT)
- PC amount input field
- Validation (must have enough PC)
- Clear success/error feedback

**Implementation Pattern**:
```javascript
// Add to actions array
{ type: 'campaign', label: 'Campaign', ap_cost: 2, description: 'Place influence for future election' }

// Add campaign handler
function handleCampaignAction() {
    const officeSelect = document.getElementById('campaign-office');
    const pcInput = document.getElementById('campaign-pc');
    
    const officeId = officeSelect.value;
    const influenceAmount = parseInt(pcInput.value);
    
    if (!officeId || !influenceAmount || influenceAmount <= 0) {
        alert('Please select an office and enter a valid PC amount');
        return;
    }
    
    // Call API
    performAction('campaign', {
        office_id: officeId,
        influence_amount: influenceAmount
    });
}

// Add campaign modal/dialog
function showCampaignDialog() {
    const modal = document.createElement('div');
    modal.className = 'campaign-modal';
    modal.innerHTML = `
        <h3>Campaign for Office</h3>
        <select id="campaign-office">
            <option value="">Select Office...</option>
            <option value="STATE_SENATOR">State Senator</option>
            <option value="CONGRESS_SEAT">Congress Seat</option>
            <option value="GOVERNOR">Governor</option>
            <option value="US_SENATOR">US Senator</option>
            <option value="PRESIDENT">President</option>
        </select>
        <input type="number" id="campaign-pc" placeholder="PC to commit" min="1">
        <button onclick="handleCampaignAction()">Campaign</button>
        <button onclick="closeModal()">Cancel</button>
    `;
    document.body.appendChild(modal);
}
```

#### 3. Turn Status Display
**Location**: `static/script.js` - `updateGameState()` function
**Requirements**:
- Clear indication of current player
- Remaining AP display
- Turn phase information
- Visual feedback for turn transitions

**Implementation Pattern**:
```javascript
// Add to updateGameState()
const turnStatus = document.getElementById('turn-status');
const currentPlayer = gameState.players[gameState.current_player_index];
const remainingAP = gameState.action_points[currentPlayer.id] || 3;

turnStatus.innerHTML = `
    <div class="turn-info">
        <strong>Current Turn:</strong> ${currentPlayer.name}<br>
        <strong>Action Points:</strong> ${remainingAP}/3<br>
        <strong>Phase:</strong> ${gameState.current_phase}
    </div>
`;
```

#### 4. CSS Styling
**Location**: `static/style.css`
**Requirements**:
- Action points display styling
- Campaign modal styling
- Disabled action button styling
- Turn status styling
- Mobile responsive design

**Implementation Pattern**:
```css
.action-points-display {
    background: #f0f0f0;
    padding: 10px;
    margin: 10px 0;
    border-radius: 5px;
    text-align: center;
    font-weight: bold;
}

.campaign-modal {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 20px;
    border: 2px solid #333;
    border-radius: 10px;
    z-index: 1000;
}

.action-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.turn-info {
    background: #e8f4fd;
    padding: 15px;
    border-radius: 8px;
    margin: 10px 0;
}
```

### API Integration
The backend already provides all necessary data:
- `gameState.action_points`: Object mapping player_id to remaining AP
- `gameState.campaign_influences`: Array of campaign influences
- Campaign action endpoint: `POST /api/game/<id>/action` with `action_type: 'campaign'`

### Testing Requirements
1. **AP Display**: Verify AP are shown correctly for current player
2. **AP Validation**: Verify actions are disabled when insufficient AP
3. **Campaign Action**: Verify office selection and PC input work
4. **Turn Advancement**: Verify turn status updates correctly
5. **Mobile Responsiveness**: Verify UI works on mobile devices

### Files to Modify
- `static/script.js`: Main implementation
- `static/style.css`: Styling
- `static/index.html`: May need minor updates for new elements

### Success Criteria
- Players can see their remaining Action Points
- Action buttons show AP costs and are disabled when insufficient
- Campaign action works with office selection and PC input
- Turn status is clear and updates correctly
- UI is mobile responsive and user-friendly

## 🎯 Immediate Development Priorities

1. **Frontend Implementation**: Complete the Action Points system UI (see Frontend Implementation Requirements section above)
2. **Extensive Playtesting**: Test the Action Points system and PC commitment systems thoroughly
3. **Balance Adjustments**: Fine-tune AP costs and PC commitment amounts based on playtesting
4. **Consider Network Action Design**: If Form Alliance is missed, implement the merged Network/Alliance system from `NETWORK_ACTION_DESIGN.md`
5. **Database Integration**: For production readiness
6. **Enhanced Testing**: More comprehensive unit tests for edge cases
7. **UI Polish**: Better visual feedback and animations

---

**The project is in excellent shape with a solid foundation, clear architecture, and comprehensive improvements. All major bugs have been fixed, new features are fully functional and tested, and the game is ready for extensive playtesting. The next LLM has a strong base to build upon with clear technical patterns and strategic direction established. The most immediate opportunity is completing the Action Points system frontend implementation and extensive playtesting of the new PC commitment and trading systems to ensure they enhance rather than detract from the game experience.**