# Election Game

A digital adaptation of a political strategy board game, featuring AI opponents and comprehensive simulation capabilities.

## Current Status

### ✅ Completed Features
- **Robust Game Engine**: Complete implementation of all game mechanics
- **AI Opponents**: Multiple AI personas (Random, Economic, Legislative, Balanced, Heuristic)
- **Smart AI Behavior**: AI opponents aware of game effects (e.g., avoid Fundraise during stock market crash)
- **Multiple AI Support**: Play against 1-3 AI opponents with different personas
- **CLI Interface**: Text-based human vs AI gameplay with detailed turn logging
- **Simulation Framework**: Comprehensive testing with 300+ games per experiment
- **Skill vs Luck Analysis**: Quantified game balance (similar to Texas Hold 'Em)

### 🔄 Current Development Phase
We are transitioning to a **CLI-First Development** approach to focus on gameplay experience and rapid iteration.

## Quick Start

### For Players
1. **CLI Game**: Run `python3 cli_game.py multi` for 1 vs 3 AI opponents
2. **Single AI**: Run `python3 cli_game.py single heuristic` for 1 vs 1 gameplay
3. Experience the strategic depth of political campaigning

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
3. Test CLI game: `python3 cli_game.py multi`
4. Run the simulation framework: `python3 simulation_runner.py`

## Project Structure

```
election/
├── engine/                 # Game engine and mechanics
├── models/                 # Game state and data models
├── personas/              # AI opponent implementations
├── simulation_results/     # Analysis and testing data
├── cli_game.py           # Main CLI game interface
├── human_vs_ai.py        # Human vs AI game orchestration
├── server.py              # Core game logic (no Flask)
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

### Simulation Framework
- **Configurable Experiments**: YAML-based testing setup
- **Statistical Analysis**: Automated result processing
- **Performance Testing**: 300+ games in under 2 minutes
- **Balance Analysis**: Skill vs luck quantification

## Development Roadmap

### Phase 1: CLI-First Development (✅ Completed)
- [x] Remove web UI complexity
- [x] Focus on command-line interface
- [x] Enhance CLI experience with better formatting
- [x] Support multiple AI opponents with different personas

### Phase 2: Gameplay Iteration (🔄 In Progress)
- [ ] Test and refine gameplay balance
- [ ] Collect player feedback
- [ ] Implement rapid iteration cycle
- [ ] Optimize for engagement

### Phase 3: Configuration-Driven Design (🔄 In Progress)
- [ ] Externalize game parameters
- [ ] Create formal iteration loop
- [ ] Establish gameplay lab framework
- [ ] Implement rapid testing capabilities

## Technical Details

### Backend Architecture
- **Game Engine**: Python-based with clean action/resolver pattern
- **CLI Interface**: Text-based with rich formatting
- **State Management**: Immutable game state with clear transitions
- **AI System**: Extensible persona-based AI opponents

### Simulation Framework
- **Configuration**: YAML-based experiment setup
- **Execution**: Automated game running with logging
- **Analysis**: Statistical processing and visualization
- **Performance**: Optimized for rapid iteration

## Getting Started for New Developers

### 1. Understand the Vision
Read the following documents:
- `PLAYER_FIRST_REFACTOR_PLAN.md` - Detailed implementation roadmap
- `DEVELOPER_HANDOFF_V2.md` - Current project status
- `SIMULATION_FRAMEWORK.md` - Testing and analysis framework

### 2. Set Up Development Environment
```bash
# Clone and setup
git clone <repository>
cd election
pip install -r requirements.txt

# Test the CLI game
python3 cli_game.py multi
```

### 3. Run Simulations
```bash
# Run simulation framework
python3 simulation_runner.py

# Analyze results
python3 analysis.py
```

## Game Balance Considerations

### Current Balance
- Political Capital (PC) is the primary resource
- Actions have clear costs and benefits
- Random events add unpredictability
- Favor system adds strategic depth
- **PC commitment system adds strategic depth**
- **Action Points system adds player autonomy**

### Potential Balance Issues
- PC commitment amounts may need tuning based on playtesting
- Random events could be too swingy
- Player interaction could be enhanced

## 🎯 Strategic Context for Next Development

### Immediate Opportunities
1. **Gameplay Testing**: Use CLI to test and refine game mechanics
2. **AI Behavior**: Improve AI decision-making and strategy
3. **Balance Analysis**: Use simulation framework for quantitative analysis
4. **Configuration System**: Externalize game parameters for rapid iteration

### Technical Debt to Address
1. **Error Handling**: More robust error handling in CLI
2. **Validation**: Input validation and sanitization
3. **Testing**: Additional unit tests for edge cases
4. **Documentation**: Code comments and API documentation

## 🚀 Next Steps

### High Impact, Low Effort
1. **Enhance CLI Experience**: Better formatting, colors, and user experience
2. **Game Balance Testing**: Extensive playtesting of core systems
3. **Configuration System**: Externalize game parameters
4. **Rapid Iteration**: Implement formal testing and iteration loop

### Medium Impact, Medium Effort
1. **Advanced AI**: Smarter computer opponents
2. **Game Variants**: Different election scenarios, rule sets
3. **Analytics**: Track game statistics and player behavior
4. **Performance Optimization**: Improve simulation speed

### High Impact, High Effort
1. **Real-time Multiplayer**: WebSocket-based live games
2. **Mobile App**: Native iOS/Android apps
3. **Advanced Analytics**: Game statistics and insights
4. **Modding System**: User-created content

## 🎮 Game Balance Considerations

### Current Balance
- Political Capital (PC) is the primary resource
- Actions have clear costs and benefits
- Random events add unpredictability
- Favor system adds strategic depth
- **PC commitment system adds strategic depth**
- **Action Points system adds player autonomy**

### Potential Balance Issues
- PC commitment amounts may need tuning based on playtesting
- Random events could be too swingy
- Player interaction could be enhanced

## 📚 Documentation References

- `LLM_HANDOFF_CONTEXT.md`: Comprehensive project context and recent changes
- `SIMULATION_FRAMEWORK.md`: Testing and analysis framework
- `AI_IMPROVEMENTS.md`: AI behavior enhancements

## 🎯 Success Metrics

### Technical
- CLI responsiveness and user experience
- All game mechanics working correctly
- AI opponents making intelligent decisions
- Simulation framework providing useful insights

### Gameplay
- Engaging strategic depth
- Balanced action choices
- Clear player feedback
- Smooth game flow
- **Successful secret commitment mechanics**
- **Strategic PC commitment decisions**
- **Smooth automatic event phases**

## 🚨 Known Issues & Limitations

### Current Limitations
- **In-memory Storage**: Game state is lost on server restart (production needs database)
- **Single Session**: No persistent user accounts or game history
- **Limited Analytics**: No game statistics or performance tracking

### Potential Issues to Watch
- **AI Balance**: AI opponents may need further tuning
- **Game Length**: Games may be too long or short
- **Complexity**: Game mechanics may be too complex for new players

---

**The project is in excellent shape with a solid foundation, clear architecture, and comprehensive improvements. All major bugs have been fixed, new features are fully functional and tested, and the game is ready for extensive playtesting. The CLI-first approach provides a strong base for rapid iteration and gameplay refinement.** 🗳️