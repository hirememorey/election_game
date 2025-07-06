# Election: The Game

A text-based political strategy game where players compete to win an election through various actions and events.

## Description

Election: The Game is a turn-based strategy game where 2-4 players compete in a political election. Players take turns performing actions to gain votes, manage resources, and respond to random events that can affect the campaign.

## Features

- **Multi-player support**: 2-4 players can compete
- **Turn-based gameplay**: Strategic decision making with action points
- **Event system**: Random events that can help or hinder campaigns
- **Resource management**: Balance money, influence, and votes
- **Card-based actions**: Various action cards with different effects
- **CLI interface**: Clean command-line interface for gameplay

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd election
```

2. Make sure you have Python 3.7+ installed:
```bash
python3 --version
```

3. Run the game:
```bash
python3 main.py
```

## How to Play

1. **Setup**: Enter the number of players (2-4) and their names
2. **Game Phases**: 
   - **Event Phase**: Random events occur that affect all players
   - **Action Phase**: Players take turns performing actions using action points
3. **Actions**: Players can perform various actions like:
   - Campaigning to gain votes
   - Fundraising to get money
   - Using special action cards
4. **Winning**: The player with the most votes at the end wins!

## Game Structure

- `main.py` - Main game entry point
- `cli.py` - Command-line interface and user interaction
- `game_data.py` - Game data loading and configuration
- `engine/` - Core game engine and logic
- `models/` - Data models for game state and components

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the [MIT License](LICENSE). 