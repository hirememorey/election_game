# LLM/Developer Handoff Context

## Project Overview
- **What it is:** A Python-based political board game, now with a Flask backend and a mobile-friendly web frontend.
- **Goal:** Make the game playable on iPhone (and other devices) via a web browser.

## Current State
- **Backend:** Flask API (`server.py`) exposes game logic and serves static files.
- **Frontend:** HTML/CSS/JS in `static/` folder, mobile-optimized, interacts with backend via REST API.
- **Game Logic:** All core logic is in Python (`engine/`, `models/`, etc.), reused from the CLI version.
- **Deployment:** Local server works on custom port (e.g., 5001). Deployment instructions are in `DEPLOYMENT.md`.

## Recent Issues & Next Steps
- **Static files 404:** When accessing `/`, the server returns 404 for `/script.js` and `/style.css`. Likely cause: Flask static file serving config.
- **Testing:** No automated tests for API or frontend yet. Manual testing is possible via browser.
- **API URL:** In `static/script.js`, `API_BASE_URL` is set to `http://localhost:5000/api` (should match backend port and deployment URL).

## Key Files
- `server.py`: Flask app, API endpoints, static file serving.
- `static/index.html`, `static/style.css`, `static/script.js`: Frontend.
- `engine/`, `models/`, `game_data.py`: Game logic and data.
- `DEPLOYMENT.md`: Deployment instructions for Render, Netlify, Heroku, Railway, and local testing.

## Immediate To-Dos
- **Fix static file serving:** Ensure `/script.js` and `/style.css` are served correctly (Flask's `static_folder` config or explicit routes).
- **Test API endpoints:** Use Postman/curl or browser to verify `/api/game`, `/api/game/<id>`, etc.
- **Test frontend:** Play through a game in browser, check for bugs, and improve UX.
- **Automated tests:** (Optional) Add unit tests for API and game logic.

## How to Run Locally
```bash
pip install -r requirements.txt
PORT=5001 python3 server.py
# Visit http://localhost:5001 in your browser
```

## How to Deploy
See `DEPLOYMENT.md` for step-by-step instructions for Render, Netlify, etc.

---

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