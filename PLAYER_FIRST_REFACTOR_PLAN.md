# Player-First Refactor Plan

## Vision Statement

**Guiding Principle:** Our primary goal is to test and refine the core gameplay experience. This means ruthlessly simplifying the interface to focus our development effort on game mechanics and AI opponents. We are moving from building a *product* to tuning an *experience*.

## Current State Analysis

### What We Have
- ✅ Robust simulation framework with skill/luck analysis
- ✅ Working game engine with all core mechanics
- ✅ Web deployment infrastructure
- ✅ Multiple AI personas (Random, Economic, Legislative, Balanced, Heuristic)
- ✅ Comprehensive test suite

### What's Blocking Us
- ❌ Complex UI with frontend-backend sync issues
- ❌ Election dice rolls not implemented in web version
- ❌ No way for humans to play against AI opponents
- ❌ UI complexity preventing rapid gameplay iteration

## Implementation Roadmap

### Phase 1: Strip Down to Command-Line Interface (Week 1)

**Goal:** Create a minimal, functional interface that allows human players to play against AI opponents.

#### 1.1 Create Command-Line Game Interface
- **File:** `cli_game.py`
- **Purpose:** Minimal text-based interface for human vs AI gameplay
- **Features:**
  - Display current game state in text format
  - List available actions for human player
  - Accept simple text commands (e.g., "fundraise", "support healthcare 20")
  - Show AI opponent actions
  - Display election results and game outcomes

#### 1.2 Implement Election Dice Rolls in Web Version
- **Files to Modify:**
  - `engine/resolvers.py` (already done in simulation)
  - `cli.py` (web API endpoints)
  - Frontend JavaScript (election resolution)
- **Goal:** Ensure web version matches simulation behavior

#### 1.3 Create Human vs AI Game Mode
- **File:** `human_vs_ai.py`
- **Purpose:** Orchestrate games between human players and AI opponents
- **Features:**
  - Configurable AI persona selection
  - Game state management
  - Turn-by-turn gameplay
  - Result tracking

### Phase 2: Web-Based Minimal Interface (Week 2)

**Goal:** Create a web-deployed version that maintains the simplicity of command-line but adds visual clarity.

#### 2.1 Create Minimal Web UI
- **Files:** `static/minimal.html`, `static/minimal.js`, `static/minimal.css`
- **Design Principles:**
  - Single-page interface
  - Large, clear text
  - Minimal animations
  - Focus on readability over aesthetics
  - Mobile-responsive but desktop-optimized

#### 2.2 Implement Core Game Flow
- **Features:**
  - Display current player and phase
  - Show available actions as large buttons
  - Display game state in clear text format
  - Show AI opponent actions
  - Display results and outcomes

#### 2.3 Add AI Opponent Selection
- **Interface:** Dropdown to select AI persona
- **Options:** Random, Economic, Legislative, Balanced, Heuristic
- **Default:** Heuristic (represents basic skill level)

### Phase 3: Gameplay Testing and Iteration (Week 3-4)

**Goal:** Use the minimal interface to test and refine the core gameplay experience.

#### 3.1 Create Testing Framework
- **File:** `gameplay_testing.py`
- **Purpose:** Automated testing of human vs AI gameplay
- **Features:**
  - Record game outcomes
  - Track win rates by AI persona
  - Identify gameplay issues
  - Measure game length and engagement

#### 3.2 Implement Feedback Collection
- **Features:**
  - Simple rating system (1-5 stars)
  - Text feedback collection
  - Gameplay metrics tracking
  - Issue reporting system

#### 3.3 Create Iteration Cycle
- **Process:**
  1. Play games with different AI opponents
  2. Identify gameplay issues
  3. Make quick adjustments to game mechanics
  4. Re-test with updated mechanics
  5. Repeat until gameplay feels satisfying

## Technical Requirements

### Backend Changes

#### 1. Election Dice Roll Implementation
```python
# In engine/resolvers.py - already implemented for simulation
def resolve_elections(state: GameState, disable_dice_roll: bool = False) -> GameState:
    # ... existing code ...
    if not disable_dice_roll:
        # Add dice roll logic here
        for candidate in candidates:
            dice_roll = random.randint(1, 6)
            scores[candidate.name] += dice_roll
```

#### 2. CLI Game Interface
```python
# New file: cli_game.py
class CLIGame:
    def __init__(self, ai_persona: str = "heuristic"):
        self.harness = SimulationHarness()
        self.ai_persona = get_persona_class(ai_persona)()
    
    def display_game_state(self):
        # Show current state in text format
    
    def get_available_actions(self):
        # Return list of valid actions for human player
    
    def execute_action(self, action_text: str):
        # Parse text command and execute action
```

#### 3. Human vs AI Game Mode
```python
# New file: human_vs_ai.py
class HumanVsAIGame:
    def __init__(self, ai_persona: str = "heuristic"):
        self.cli_game = CLIGame(ai_persona)
    
    def play_game(self):
        # Main game loop
        while not game_over:
            if current_player == human:
                self.handle_human_turn()
            else:
                self.handle_ai_turn()
```

### Frontend Changes

#### 1. Minimal Web Interface
```html
<!-- static/minimal.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Election Game - Minimal</title>
    <link rel="stylesheet" href="minimal.css">
</head>
<body>
    <div id="game-container">
        <div id="game-state"></div>
        <div id="actions"></div>
        <div id="game-log"></div>
    </div>
    <script src="minimal.js"></script>
</body>
</html>
```

#### 2. Simplified JavaScript
```javascript
// static/minimal.js
class MinimalGame {
    constructor() {
        this.gameId = null;
        this.currentState = null;
    }
    
    async startGame(aiPersona) {
        // Initialize game with selected AI
    }
    
    displayGameState() {
        // Update UI with current game state
    }
    
    async executeAction(action) {
        // Send action to backend and update UI
    }
}
```

## Success Metrics

### Phase 1 Success Criteria
- [ ] Human can play complete game against AI opponent
- [ ] Election dice rolls work in web version
- [ ] Game state is clearly displayed
- [ ] Actions are easy to understand and execute

### Phase 2 Success Criteria
- [ ] Web interface loads and functions correctly
- [ ] Gameplay is smooth and responsive
- [ ] AI opponent selection works
- [ ] Interface is mobile-friendly

### Phase 3 Success Criteria
- [ ] Gameplay feels engaging and balanced
- [ ] Win rates are reasonable (not too one-sided)
- [ ] Game length is appropriate (15-30 minutes)
- [ ] Players want to play again

## Risk Mitigation

### Technical Risks
1. **Backend Complexity:** Keep changes minimal and focused
2. **Frontend Bugs:** Use simple, tested patterns
3. **Performance Issues:** Monitor game speed and responsiveness

### Design Risks
1. **Interface Too Simple:** Balance clarity with functionality
2. **Gameplay Imbalance:** Use simulation data to guide adjustments
3. **User Engagement:** Focus on core gameplay loop

## Next Steps for Developers

1. **Start with Phase 1:** Implement the command-line interface first
2. **Test Election Dice Rolls:** Ensure web version matches simulation
3. **Create Human vs AI Mode:** Build the core gameplay experience
4. **Iterate Rapidly:** Make small changes and test frequently
5. **Focus on Feel:** Prioritize gameplay experience over features

## Files to Create/Modify

### New Files
- `cli_game.py` - Command-line game interface
- `human_vs_ai.py` - Human vs AI game orchestration
- `gameplay_testing.py` - Testing and feedback framework
- `static/minimal.html` - Minimal web interface
- `static/minimal.js` - Minimal web JavaScript
- `static/minimal.css` - Minimal web styling

### Modified Files
- `cli.py` - Add election dice roll support
- `engine/resolvers.py` - Ensure dice rolls work in web version
- `simulation_harness.py` - Add human player support
- `models/game_state.py` - Add human player tracking

This plan provides a clear roadmap for implementing the player-first refactor while maintaining the robust simulation framework we've built. 