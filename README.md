# ELECTION: The Game

> **Note for Developers:** This project is currently undergoing a significant architectural refactor towards a state-driven design. Please read the [**`STATE_DRIVEN_REFACTOR.md`**](STATE_DRIVEN_REFACTOR.md) document before starting any new work to understand the new architectural principles and execution plan.

## Overview

A competitive political strategy game where players manage resources, sponsor and defeat legislation, form alliances, and compete for political office.

## Features

- **Secret Commitment System**: Players secretly fund or fight legislation, leading to dramatic reveals and strategic gameplay
- **Multiple AI Personas**: Play against different AI opponents with unique strategies
- **Web Interface**: Modern terminal-style web UI with real-time game updates
- **Political Capital Management**: Strategic resource management with PC (Political Capital)
- **Office Competition**: Run for various political offices with different benefits
- **Event System**: Dynamic events that affect gameplay and strategy

## Quick Start

### Web Version

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   npm install
   ```

2. Build the frontend:
   ```bash
   npm run build
   ```

3. Start the server:
   ```bash
   python3 server.py
   ```

4. Open your browser to `http://127.0.0.1:5001`

The web version features:
- Real-time game updates
- AI turn visibility (press Enter to continue after each AI action)
- Modern terminal-style interface
- Full game state display

## Game Rules

### Objective
Win by having the most **Influence** at the end of the final term. Influence is gained by holding political office and achieving your secret **Personal Mandate**.

### Core Mechanics
- **Political Capital (PC)**: Your primary resource for actions
- **Action Points (AP)**: Limited actions per turn (2 AP per turn)
- **Secret Commitments**: Privately support or oppose legislation
- **Office Competition**: Run for political offices with unique benefits

### Actions
- **Fundraise**: Gain 5 PC
- **Network**: Gain 2 PC and draw a Political Favor
- **Sponsor Legislation**: Pay PC to propose bills
- **Support/Oppose Legislation**: Secretly commit PC to bills
- **Declare Candidacy**: Run for office (Round 4 only)
- **Use Favor**: Play special ability cards

## Development

### Project Structure
- `engine/`: Core game logic and action processing
- `models/`: Data structures for game state
- `personas/`: AI player personalities
- `static/`: Web frontend files
- `server.py`: Web server for the browser version

### Testing
```bash
# Backend tests
python3 -m unittest discover -s .

# Frontend tests
npm test
```

### Building for Production
```bash
npm run build
```

## Recent Updates

- **Precise PC Commitment System**: Players can now specify exact amounts of Political Capital when supporting or opposing legislation, rather than being limited to fixed amounts. This enhances strategic depth by allowing players to commit precisely the amount of PC they want to risk on each bill.
- **Legislation "Undefined" Fix**: Fixed critical issue where users would see "undefined" options when selecting legislation to sponsor. The backend was correctly generating the data, but users needed to clear browser cache and restart the server to get the latest frontend JavaScript
- **Legislation Sponsorship & Support/Oppose Fix**: Fixed critical issues where players could re-sponsor active legislation and couldn't support/oppose their own bills. Players can now properly sponsor legislation in one round and support/oppose any active legislation (including their own) in subsequent rounds
- **Declare Candidacy Fix**: Fixed critical bug where the "Declare Candidacy" action was not available in Round 4. Implemented proper two-step UI flow for office selection
- **CLI Version Removal**: Simplified the project by removing the local CLI version to focus on the web application
- **Round Advancement Fix**: Fixed critical bug where the game would get stuck in Round 1. The game now properly advances through rounds when all players use their action points
- **AI Turn Visibility**: The web version now pauses after each AI action, allowing players to see what the AI did before continuing
- **Enhanced Error Handling**: Improved server stability and error recovery
- **UI Improvements**: Better game state display and action prompts
- **Bug Fixes**: Resolved issues with action processing and game state management

## Architectural Overview

This project follows a state-driven architecture to ensure stability and maintainability. The core components and their responsibilities are:

- **`server.py` (The Conductor):** Manages the websocket connection and the overall game loop. It is responsible for the *pacing* of the game, receiving actions from the client, running AI turns one-by-one, and sending state updates back to the client. It ensures the "press enter to continue" flow by waiting for client acknowledgements.
- **`game_session.py` (The Game Master):** A stateful "GM" that holds the canonical `GameState` object. It exposes simple, non-looping methods like `process_human_action()` and `process_ai_turn()` which the server uses to advance the game by one discrete step. It knows the status of the game but is not responsible for the loop itself.
- **`engine/engine.py` (The Rulebook):** A pure, stateless set of functions that enforces the rules of the game. It takes a `GameState` and an `Action` and returns a *new* `GameState`. It has no knowledge of turns, rounds, or game flow.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.