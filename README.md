# Election: The Game

A competitive political strategy game where players manage resources, sponsor and defeat legislation, form alliances, and compete for political office.

## Features

- **Secret Commitment System**: Players secretly fund or fight legislation, leading to dramatic reveals and strategic gameplay
- **Multiple AI Personas**: Play against different AI opponents with unique strategies
- **Web Interface**: Modern terminal-style web UI with real-time game updates
- **Political Capital Management**: Strategic resource management with PC (Political Capital)
- **Office Competition**: Run for various political offices with different benefits
- **Event System**: Dynamic events that affect gameplay and strategy

## Quick Start

### Web Version (Recommended)

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

### Command Line Version

For a simpler experience, you can also run:
```bash
python3 main.py
```

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
- `main.py`: Command-line entry point

### Testing
```bash
# Backend tests
pytest

# Frontend tests
npm test

# End-to-end tests
python3 test_end_to_end.py
```

### Building for Production
```bash
npm run build
```

## Recent Updates

- **Round Advancement Fix**: Fixed critical bug where the game would get stuck in Round 1. The game now properly advances through rounds when all players use their action points
- **AI Turn Visibility**: The web version now pauses after each AI action, allowing players to see what the AI did before continuing
- **Enhanced Error Handling**: Improved server stability and error recovery
- **UI Improvements**: Better game state display and action prompts
- **Bug Fixes**: Resolved issues with action processing and game state management

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.