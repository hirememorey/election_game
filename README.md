# Election: The Political Strategy Game

A sophisticated political strategy board game with Apple-level design, featuring secret commitment mechanics, action points, and political archetypes.

## 🎮 Game Overview

**Election: The Game** is a strategic political simulation where players compete for power through legislation, campaigning, and political maneuvering. The game features:

- **Secret Commitment System**: Players secretly commit Political Capital (PC) to support/oppose legislation
- **Action Points**: Strategic resource management with 2 AP per turn
- **Political Archetypes**: Unique abilities for each player (Insider, Populist, etc.)
- **Multi-Phase Gameplay**: Event → Action → Legislation → Election cycles
- **Mobile-Optimized**: Fully responsive design with touch-friendly interface

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js (for mobile testing)

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/election-game.git
cd election-game

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright for mobile testing (optional)
npm install -g playwright
npx playwright install
```

### Running the Game
```bash
# Start the server
PORT=5001 python3 server.py

# Open in browser
open http://localhost:5001
```

## 📱 Mobile Testing

The game includes comprehensive mobile testing to ensure optimal mobile experience:

### Running Mobile Tests
```bash
# Run all mobile tests
./run-mobile-tests.sh

# Run specific test file
npx playwright test tests/mobile-ui-elements.spec.ts

# View test results
npx playwright show-report test-results/mobile/usability-report
```

### Mobile Test Results (Latest)
- **47/63 tests passing** (74.6% success rate)
- **Excellent mobile usability** (8.5/10 score)
- **Touch-friendly interface** with proper button sizes
- **Responsive design** that works across orientations
- **Intuitive gestures** (swipe up for game info)

See `MOBILE_TEST_RESULTS.md` for detailed results.

## 🎯 Game Features

### Core Mechanics
- **Political Capital (PC)**: Primary resource for actions and commitments
- **Action Points (AP)**: Limited actions per turn (2 AP)
- **Secret Commitments**: Hidden PC allocation for dramatic reveals
- **Legislation Voting**: Support/oppose bills with PC stakes
- **Election Cycles**: Win votes to gain power and influence

### Player Archetypes
- **Insider**: Political establishment with network advantages
- **Populist**: Grassroots support and campaign bonuses
- **Reformer**: Legislative expertise and policy influence
- **Strategist**: Information gathering and tactical advantages

### Game Phases
1. **Event Phase**: Random events affecting all players
2. **Action Phase**: Players take actions using AP
3. **Legislation Phase**: Vote on bills with PC commitments
4. **Election Phase**: Determine winners and losers

## 🛠️ Development

### Project Structure
```
election/
├── static/           # Frontend assets
│   ├── index.html   # Main game interface
│   ├── script.js    # Game logic
│   └── style.css    # Apple-level styling
├── engine/          # Game engine
│   ├── engine.py    # Core game logic
│   ├── actions.py   # Action definitions
│   └── resolvers.py # Phase resolution
├── models/          # Data models
│   ├── game_state.py
│   ├── cards.py
│   └── components.py
├── tests/           # Test suite
│   ├── mobile-ui-elements.spec.ts
│   ├── mobile-usability.spec.ts
│   └── mobile-config.ts
└── server.py        # Flask server
```

### Key Technologies
- **Backend**: Python Flask
- **Frontend**: Vanilla JavaScript with Apple-level CSS
- **Testing**: Playwright for mobile testing
- **Design**: Responsive, touch-friendly interface

## 📋 Testing

### Mobile Usability Tests
The comprehensive mobile testing suite covers:

- **Touch Interactions**: Button sizes, spacing, gestures
- **Responsive Design**: Orientation changes, text readability
- **Game Flow**: Complete mobile game experience
- **Accessibility**: Keyboard navigation, screen readers
- **Performance**: Load times, responsiveness

### Running Tests
```bash
# Mobile tests only
./run-mobile-tests.sh

# All tests
npx playwright test

# Specific browser
npx playwright test --project=chromium
```

## 🎨 Design Philosophy

The game features **Apple-level design** with:
- **Minimalist interface** with clear information hierarchy
- **Touch-first design** optimized for mobile devices
- **Responsive layout** that adapts to any screen size
- **Intuitive interactions** with natural gestures
- **Accessible design** supporting keyboard and screen readers

## 📚 Documentation

- `MOBILE_TESTING_GUIDE.md` - Complete mobile testing documentation
- `MOBILE_TEST_RESULTS.md` - Latest test results and analysis
- `DEVELOPER_HANDOFF.md` - Technical implementation details
- `GAME_IMPROVEMENTS.md` - Future enhancement plans

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Run mobile tests: `./run-mobile-tests.sh`
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Election: The Game** - Where political strategy meets mobile gaming excellence. 