# Election: A Political Strategy Game

## Overview

Election is a digital adaptation of a political strategy board game. It is a turn-based game where players take on the roles of political actors vying for power. The game is currently in a **CLI-First Development** phase, prioritizing gameplay mechanics, balance, and simulation over a graphical user interface.

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
3.  **Install dependencies:** `pip install -r requirements.txt`

### Running the Game

The game can be played both locally and online through a web-based terminal interface.

#### Local Play (Command Line)

*   **Human vs. 3 AI Opponents:**
    ```bash
    python3 cli_game.py multi
    ```
*   **Human vs. 1 AI Opponent:**
    ```bash
    python3 cli_game.py single <persona>
    ```
    *   Replace `<persona>` with one of the available AI personas: `random`, `economic`, `legislative`, `balanced`, or `heuristic`.

#### Online Play (Web Browser)

The game is also available online through a web-based terminal that provides the same CLI experience as the local version:

*   **Play Online:** Visit the deployed application at [your-render-url] to play in your browser
*   **Features:** Full terminal emulation with keyboard input, real-time game updates, and persistent sessions
*   **Compatibility:** Works on desktop and mobile browsers with keyboard support

#### Running the Web Server Locally

To run the web version locally for development or testing:

```bash
# Install dependencies
pip install -r requirements.txt

# Start the web server
uvicorn server:app --host 0.0.0.0 --port 8000

# Open your browser to http://localhost:8000
```

### Key Directories

*   `engine/`: Contains the core game logic, rules, and action resolvers. The heart of how the game functions.
*   `models/`: Defines the data structures for the game state, players, and other components (`GameState`, `Player`, etc.).
*   `personas/`: Home to the different AI strategies. To create a new AI, you would add a new persona class here.
*   `simulation_results/`: Default output directory for the simulation framework.
*   `static/`: Contains the web frontend files for the online terminal interface.
*   `server.py`: FastAPI web server that bridges the web terminal to the CLI game using WebSockets and pseudoterminals.

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