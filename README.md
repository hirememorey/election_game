# Election Game

A strategic political simulation game where players compete for influence through legislation, elections, and political maneuvering.

## Features

- **Secret Commitment System**: Players secretly commit Political Capital to support or oppose legislation
- **Action Points System**: Strategic resource management with limited actions per turn
- **Multiple Office Types**: President, Senators, Governors, and more with different influence values
- **Hidden Funder Mandates**: Unique victory conditions for each player
- **Event Cards**: Dynamic events that affect gameplay
- **Mobile-Optimized**: Responsive design with touch-friendly controls

## Quick Start

### Web Version (Recommended for Players)

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Server**:
   ```bash
   python server.py
   ```

3. **Open in Browser**:
   Navigate to `http://localhost:5000`

### Simulation Framework (For Developers/Analysis)

The project now includes a comprehensive simulation framework for game balance analysis:

```bash
# Run a single simulation with detailed winner analysis
python3 run_single_simulation.py

# Run a basic simulation with random agents
python simulation_harness.py

# The simulation framework supports:
# - Headless game execution
# - Agent-based testing
# - Tournament systems
# - Balance analysis
# - Detailed winner analysis and reasoning
```

## Game Mechanics

### Core Systems

- **Political Capital (PC)**: Primary resource used for actions and commitments
- **Action Points (AP)**: Limited actions per turn (2 AP per player per round)
- **Influence**: Victory is determined by total influence points
- **Offices**: Holding political offices grants influence bonuses

### Actions Available

- **Fundraise**: Gain Political Capital
- **Network**: Build connections and gain advantages
- **Sponsor Legislation**: Create bills for voting
- **Support/Oppose Legislation**: Commit PC to influence outcomes
- **Declare Candidacy**: Run for political office
- **Use Favor**: Leverage political connections

### Victory Conditions

Players earn influence through:
- **Office Bonuses**: President (25), US Senator (15), Governor (10), etc.
- **PC Conversion**: Remaining PC converts to influence (10:1 ratio)
- **Hidden Funder Mandates**: Unique objectives worth 15 influence each

## Development

### Project Structure

```
election/
├── server.py              # Main web server
├── run_single_simulation.py  # Single simulation with detailed analysis
├── simulation_harness.py  # Game balance analysis framework
├── engine/               # Core game logic
├── models/              # Data structures
├── resolvers/           # Game event resolution
├── static/             # Frontend assets
└── templates/          # HTML templates
```

### Key Components

- **GameEngine**: Core game state management
- **SimulationHarness**: Automated testing framework with pluggable logging
- **MetricsLogger**: Flexible data collection system
- **ScriptedAgent**: Deterministic agent for precise testing
- **Action System**: Modular action implementation
- **Scoring System**: Influence calculation and victory determination

## Deployment

### Local Development
```bash
python server.py
```

### Production Deployment
See `DEPLOYMENT.md` for detailed deployment instructions.

## Documentation

- `DEVELOPER_HANDOFF.md` - Development context and recent changes
- `GAME_IMPROVEMENTS.md` - Feature evolution and improvements
- `MOBILE_IMPROVEMENTS_SUMMARY.md` - Mobile UX enhancements
- `PHYSICAL_GAME_SPEC.md` - Original board game design
- `DEPLOYMENT.md` - Production deployment guide
- `SIMULATION_FRAMEWORK.md` - Comprehensive simulation framework documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly (both web and simulation)
5. Submit a pull request

## License

This project is licensed under the MIT License.