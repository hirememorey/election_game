# Election Game

A digital adaptation of a political strategy board game, featuring AI opponents and comprehensive simulation capabilities.

## Current Status

### ✅ Completed Features
- **Robust Game Engine**: Complete implementation of all game mechanics
- **AI Opponents**: Multiple AI personas (Random, Economic, Legislative, Balanced, Heuristic)
- **Smart AI Behavior**: AI opponents aware of game effects (e.g., avoid Fundraise during stock market crash)
- **Multiple AI Support**: Play against 1-3 AI opponents with different personas
- **CLI Interface**: Text-based human vs AI gameplay with detailed turn logging
- **Minimal Web Interface**: Simplified web UI for human vs AI games
- **Simulation Framework**: Comprehensive testing with 300+ games per experiment
- **Skill vs Luck Analysis**: Quantified game balance (similar to Texas Hold 'Em)
- **Web Deployment**: Functional web interface with backend API

### 🔄 Current Development Phase
We are transitioning to a **Player-First Refactor** to focus on gameplay experience and human vs AI gameplay.

## Quick Start

### For Players
1. **CLI Game**: Run `python3 cli_game.py multi` for 1 vs 3 AI opponents
2. **Web Interface**: Visit `http://localhost:5001/play` for minimal interface
3. **Full Web Game**: Visit `http://localhost:5001/` for complete interface
4. Experience the strategic depth of political campaigning

### CLI Game Usage
```bash
# Play against 3 AI opponents with different personas
python3 cli_game.py multi

# Play against 1 AI opponent
python3 cli_game.py single heuristic

# Available AI personas: random, economic, legislative, balanced, heuristic
python3 cli_game.py single economic

# Features:
# - AI opponents aware of game effects (e.g., avoid Fundraise during stock market crash)
# - Detailed turn logging showing all AI actions
# - Pause between AI turns for better game flow
# - Human player can view their hidden mandate
```

### For Developers
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Start the web server: `python server.py`
4. Test CLI game: `python cli_game.py multi`
5. Run the simulation framework: `python simulation_runner.py`

## Project Structure

```
election/
├── engine/                 # Game engine and mechanics
├── models/                 # Game state and data models
├── personas/              # AI opponent implementations
├── static/                # Web interface files
├── simulation_results/     # Analysis and testing data
├── tests/                 # Automated test suite
└── docs/                  # Documentation
```

## Key Features

### Game Mechanics
- **Action Points System**: Strategic resource management
- **Secret Commitments**: Hidden bidding mechanics
- **Legislation Voting**: Political influence simulation
- **Election Resolution**: Dice-based outcome determination
- **Event Cards**: Dynamic game events

### AI Opponents
- **Random**: Pure chance-based play
- **Economic**: Focuses on fundraising and economic actions
- **Legislative**: Prioritizes legislation and voting
- **Balanced**: Mixed strategic approach
- **Heuristic**: Basic strategic thinking (46.1% win rate vs random)

### Game Modes
- **Single AI**: Play against 1 AI opponent
- **Multiple AI**: Play against 3 AI opponents with different personas
- **CLI Interface**: Text-based gameplay for rapid testing
- **Web Interface**: Browser-based gameplay with real-time updates

### Simulation Framework
- **Configurable Experiments**: YAML-based testing setup
- **Statistical Analysis**: Automated result processing
- **Performance Testing**: 300+ games in under 2 minutes
- **Balance Analysis**: Skill vs luck quantification

## Development Roadmap

### Phase 1: Command-Line Interface (✅ Completed)
- [x] Implement election dice rolls in web version
- [x] Create CLI game interface for human vs AI
- [x] Build human vs AI game orchestration
- [x] Add comprehensive testing framework
- [x] Support multiple AI opponents with different personas

### Phase 2: Minimal Web Interface (✅ Completed)
- [x] Create simplified web UI
- [x] Implement AI opponent selection
- [x] Add real-time game state display
- [x] Ensure mobile compatibility
- [x] Support multiple AI game modes

### Phase 3: Gameplay Iteration
- [ ] Test and refine gameplay balance
- [ ] Collect player feedback
- [ ] Implement rapid iteration cycle
- [ ] Optimize for engagement

## Technical Details

### Backend Architecture
- **Game Engine**: Python-based with clean action/resolver pattern
- **API**: Flask-based REST endpoints
- **State Management**: Immutable game state with clear transitions
- **AI System**: Extensible persona-based AI opponents

### Frontend Architecture
- **Interface**: HTML/CSS/JavaScript
- **Communication**: REST API calls
- **State Management**: Real-time updates via polling
- **Responsive Design**: Mobile and desktop compatible

### Simulation Framework
- **Configuration**: YAML-based experiment setup
- **Execution**: Automated game running with logging
- **Analysis**: Statistical processing and visualization
- **Performance**: Optimized for rapid iteration

## Getting Started for New Developers

### 1. Understand the Vision
Read the following documents:
- `PLAYER_FIRST_REFACTOR_PLAN.md` - Detailed implementation roadmap
- `DEVELOPER_HANDOFF_V2.md`