# Election Game

A strategic political simulation game where players compete for influence through legislation, elections, and political maneuvering.

The game is currently in a rapid development phase. The primary focus is on refining the core gameplay loop and developing AI opponents for a compelling single-player experience.

Our current development strategy is outlined in the [Player-First Refactor Plan](PLAYER_FIRST_REFACTOR_PLAN.md).

## Features

*   **Dynamic Turn-based Gameplay**: Each turn, players choose from a set of actions like fundraising, declaring candidacy, or influencing legislation.
*   **Secret Bidding**: Use your political capital to secretly support or oppose legislation.
*   **Multiple Paths to Victory**: Win by holding office, passing legislation aligned with your archetype, or accumulating the most influence.
*   **Sophisticated Simulation Framework**: A powerful tool for game balance analysis and AI persona development.
*   **Web-based Interface**: Play the game in your browser.

## Getting Started

### Web Version (Recommended for Players)

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Server**:
    ```bash
    python server.py
    ```

3.  **Open in Browser**:
    Navigate to `http://localhost:5000`

### Simulation Framework (For Developers/Analysis)

The project includes a comprehensive simulation framework for game balance analysis:

```bash
# Run all experiments defined in simulation_config.yaml
python3 simulation_runner.py

# Run a test of the simulation framework
python3 test_skill_vs_luck_implementation.py
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

## Development Focus

The project is currently focused on implementing the plan outlined in [`PLAYER_FIRST_REFACTOR_PLAN.md`](PLAYER_FIRST_REFACTOR_PLAN.md). This involves:
1.  **Rule Parity:** Ensuring the web version uses the same dice-roll mechanics proven effective in simulation.
2.  **UI Simplification:** Moving to a developer-focused, command-line-style web UI to accelerate iteration on gameplay.
3.  **AI Opponents:** Implementing server-side AI to allow for robust single-player testing.

## Simulation Framework

The simulation framework is a key part of this project, designed for automated testing and balancing.