# Election: A Political Strategy Game

## Overview

Election is a digital adaptation of a political strategy board game. It is a turn-based game where players take on the roles of political actors vying for power. The game features a web-based terminal interface that provides an immersive command-line experience.

## Recent Updates (Latest)

### ✅ **CLI Game Display Bug Fix**
- **Fixed Duplicated Log Messages**: Resolved issue where AI turn messages were appearing multiple times in the "Recent Events" section of the CLI game display.
- **Improved Log Management**: Enhanced the turn log clearing mechanism in both `cli_game.py` and `human_vs_ai.py` to prevent message duplication.
- **Cleaner User Experience**: Players now see a clean, non-repetitive event log that's easier to follow during gameplay.

### ✅ **Dynamic Legislation Menu System**
- **Improved User Interface**: Consolidated legislation actions into a single "Legislation Actions" menu option for cleaner navigation.
- **Context-Aware Sub-Menus**: Dynamic sub-menus that show different options based on game state (sponsor new bill vs. support/oppose pending legislation).
- **Strategic Commitment System**: Hidden commitment amounts and stance in event log to enhance strategic gameplay and prevent information overload.
- **Bug Prevention**: Added validation to prevent double-sponsoring of legislation, ensuring proper game flow.

### ✅ **Critical Bug Fixes**
- **AI Player Issue Resolved**: Fixed a critical bug where AI players would get stuck during their turn due to incorrect parameter passing in the game session manager.
- **Server Startup**: Fixed missing uvicorn run command that prevented the server from starting properly.
- **Static File Serving**: Corrected the path to JavaScript files in the HTML template.

### ✅ **Testing Improvements**
- **Frontend Unit Tests**: Fixed JavaScript unit tests to handle ANSI color codes properly.
- **End-to-End Testing**: Added comprehensive E2E test framework using Playwright for deployment confidence.
- **All Tests Passing**: Both frontend and backend test suites are now passing.

### ✅ **Deployment Ready**
- **Production Configuration**: Server properly configured for deployment on Render.
- **Health Check Endpoint**: Added `/health` endpoint for monitoring and testing.
- **Static File Optimization**: All static assets properly served and cached.

## Core Game Mechanics & Design Rationale

The game's design has evolved to favor strategic depth and player interaction. Here are the core systems:

### Action Points (AP) System
*   **What it is:** Players receive 2 Action Points per turn, and actions have varying AP costs (1-2 AP). A player's turn continues until they have exhausted their AP.
*   **Design Rationale:** This replaced an old "one action per turn" model. The AP system gives players more autonomy, allows for more complex strategic combinations in a single turn, and increases the overall pace of the game.

### Secret Commitment System
*   **What it is:** When players support or oppose legislation, their contribution of Political Capital (PC) is hidden from other players. All commitments are revealed simultaneously at the end of a Term for a dramatic vote.
*   **Design Rationale:** This system replaced a public bidding mechanic. Public bidding led to a simple "resource race" where the wealthiest player had an unassailable advantage. The secret commitment system elevates the legislative phase into a high-stakes game of political poker, bluffing, and betrayal. Success now depends on a player's ability to read their opponents, not just the size of their treasury.

### Mandates & Scoring
*   **What it is:** Each player has a secret objective (their Mandate). Fulfilling this Mandate provides a significant score bonus at the end of the game.
*   **Design Rationale:** Mandates guide player strategy and create varied gameplay, as different players will be working towards different, sometimes conflicting, goals.

---

## Developer's Guide

### Getting Started

1.  **Clone the repository:** `git clone <repository_url>`
2.  **Navigate to the directory:** `cd election`
3.  **Install Python dependencies:** `pip3 install -r requirements.txt`
4.  **Install Node.js dependencies:** `npm install`

### How to Play

The primary way to play the game is through the web-based terminal interface.

#### Web-Based Terminal

To play the game, start the local web server:

```bash
python3 server.py
```

Then, open your web browser and navigate to `http://localhost:5001`. You will be greeted with a terminal interface where you can play against AI opponents.

### Testing

#### Frontend Tests
```bash
npm test
```

#### Backend Tests
```bash
python3 -m pytest test_*.py
```

#### End-to-End Tests
```bash
npx playwright test test_e2e_gameplay.spec.ts
```

---

### Key Directories

*   `engine/`: Contains the core game logic, rules, and action resolvers. The heart of how the game functions.
*   `models/`: Defines the data structures for the game state, players, and other components (`GameState`, `Player`, etc.).
*   `personas/`: Home to the different AI strategies.
*   `static/`: Contains the web frontend files (`index.html`, `app.js`).
*   `server.py`: The FastAPI web server that provides the game's API and serves the frontend.
*   `game_session.py`: A headless session manager that orchestrates the game flow, connecting the engine to a client (like the web server).

---

## Simulation & Balancing Framework

The most powerful tool for improving the game is the simulation framework. It allows for large-scale, automated playtesting to analyze balance, test strategies, and quantify the impact of luck.

### How to Run Simulations

1.  **Configure the experiment:** Open `simulation_config.yaml` to define the parameters of your test, including the number of games to run and which AI personas to use for the players.
2.  **Run the simulation:**
    ```bash
    python3 simulation_runner.py
    ```
3.  **Analyze the results:** Once the simulation is complete, run the analysis script to process the data from the `simulation_results/` directory.
    ```bash
    python3 analysis.py
    ```

### The Goal: Quantifying and Tuning Skill vs. Luck

The primary goal of the simulation framework is to tune the game's balance. We aim for a ratio of skill-to-luck similar to Texas Hold 'Em, where skill is the dominant long-term factor, but luck ensures any single game is unpredictable.

The strategy for this involves:
1.  **Establishing a Skill Baseline:** Pitting a highly strategic AI (`heuristic`) against purely random ones (`random`) to measure the raw advantage of skillful play.
2.  **Testing Strategic Viability:** Running simulations with a mix of specialized AI personas (`economic`, `legislative`) to ensure no single strategy is dominant.
3.  **Tuning "Luck Knobs":** Systematically adjusting the game's random elements (like election dice rolls or the impact of event cards) and re-running tests to measure how they affect the skill edge.

By iterating through this process, we can fine-tune the game's mechanics to create the most engaging and competitive experience possible.

---

## Deployment

The game is configured for deployment on Render with the following features:

- **Health Check**: `/health` endpoint for monitoring
- **WebSocket Support**: Real-time game updates
- **Static File Serving**: Optimized for production
- **Error Handling**: Comprehensive error handling and logging

### Manual Testing Before Deployment

Before deploying, run this quick manual test:

```bash
# Start the server
python3 server.py

# Open browser to http://localhost:5001
# Verify:
# - Page loads
# - Terminal appears
# - Game state displays
# - Can take an action
# - AI responds
```