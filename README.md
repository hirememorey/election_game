# Election Game

A digital adaptation of a political strategy board game, featuring AI opponents and comprehensive simulation capabilities.

## Current Status

### ✅ Completed Features
- **Robust Game Engine**: Complete implementation of all game mechanics
- **AI Opponents**: Multiple AI personas (Random, Economic, Legislative, Balanced, Heuristic)
- **Simulation Framework**: Comprehensive testing with 300+ games per experiment
- **Skill vs Luck Analysis**: Quantified game balance (similar to Texas Hold 'Em)
- **Web Deployment**: Functional web interface with backend API

### 🔄 Current Development Phase
We are transitioning to a **Player-First Refactor** to focus on gameplay experience and human vs AI gameplay.

## Quick Start

### For Players
1. Visit the deployed web application
2. Start a new game
3. Play against AI opponents
4. Experience the strategic depth of political campaigning

### For Developers
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the simulation framework: `python simulation_runner.py`
4. Start the web server: `python cli.py`

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

### Simulation Framework
- **Configurable Experiments**: YAML-based testing setup
- **Statistical Analysis**: Automated result processing
- **Performance Testing**: 300+ games in under 2 minutes
- **Balance Analysis**: Skill vs luck quantification

## Development Roadmap

### Phase 1: Command-Line Interface (Current)
- [ ] Implement election dice rolls in web version
- [ ] Create CLI game interface for human vs AI
- [ ] Build human vs AI game orchestration
- [ ] Add comprehensive testing framework

### Phase 2: Minimal Web Interface
- [ ] Create simplified web UI
- [ ] Implement AI opponent selection
- [ ] Add real-time game state display
- [ ] Ensure mobile compatibility

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
- `DEVELOPER_HANDOFF_V2.md` - Current state and next steps
- `IMPLEMENTATION_CHECKLIST.md` - Task tracking and success criteria

### 2. Set Up Development Environment
```bash
# Clone the repository
git clone <repository-url>
cd election

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Start development server
python cli.py
```

### 3. Start with Phase 1
1. **Implement Election Dice Rolls**: Update `engine/resolvers.py` for web version
2. **Create CLI Interface**: Build `cli_game.py` for human vs AI gameplay
3. **Test Thoroughly**: Use the simulation framework to validate changes

### 4. Follow Development Guidelines
- **Start Simple**: Begin with command-line interface
- **Test Frequently**: Use the robust simulation framework
- **Iterate Rapidly**: Make small, focused changes
- **Focus on Feel**: Prioritize gameplay experience

## Contributing

### Development Process
1. **Read the Documentation**: Understand the current state and vision
2. **Follow the Checklist**: Use `IMPLEMENTATION_CHECKLIST.md` for guidance
3. **Test Thoroughly**: Leverage the simulation framework
4. **Document Changes**: Update relevant documentation

### Code Standards
- **Python**: Follow PEP 8 guidelines
- **JavaScript**: Use consistent formatting
- **Testing**: Maintain comprehensive test coverage
- **Documentation**: Keep docs updated with changes

## Key Documents

- `PLAYER_FIRST_REFACTOR_PLAN.md` - Implementation roadmap
- `DEVELOPER_HANDOFF_V2.md` - Current state and next steps
- `IMPLEMENTATION_CHECKLIST.md` - Task tracking
- `SKILL_VS_LUCK_IMPLEMENTATION_SUMMARY.md` - Analysis results
- `SIMULATION_FRAMEWORK.md` - Testing framework documentation

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions or issues:
1. Check the documentation in the `docs/` directory
2. Review the implementation checklist
3. Run the simulation framework to validate behavior
4. Create an issue with detailed information