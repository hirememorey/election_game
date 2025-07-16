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

## ✅ **MAJOR FIXES COMPLETED (July 16, 2025)**

The application has been significantly improved with major fixes to core functionality and comprehensive mobile enhancements:

### **Core Application Issues Resolved**
- ✅ **Fixed Infinite Loop** - Added safety breaks in server.py to prevent auto-advance loops
- ✅ **Fixed API Race Conditions** - Added locking mechanism in script.js to prevent concurrent API calls
- ✅ **Fixed UI Race Conditions** - Modified startNewGame() to only transition screens after successful API responses
- ✅ **Fixed Undefined Function Call** - Changed updateUI() to updatePhaseUI() in JavaScript
- ✅ **Fixed Test Selectors** - Updated all ambiguous text selectors to target specific containers
- ✅ **Fixed Modal Sizing** - Added tablet-specific CSS for proper modal sizing
- ✅ **Fixed ARIA Labels** - Added proper accessibility labels to icon buttons
- ✅ **Forced Serial Execution** - Set workers: 1 in Playwright config to prevent test interference

### **Mobile Experience Completely Enhanced**
- ✅ **Immediate Feedback** - Mobile users now get instant feedback after all actions
- ✅ **Enhanced Phase Indicators** - Clear progress indicators with round/phase information
- ✅ **Quick Action Panel** - Touch-friendly quick actions for common game actions
- ✅ **Mobile-Optimized Results** - Results overlay fully optimized for mobile screens
- ✅ **Next Steps Guidance** - Contextual guidance after each action for mobile users
- ✅ **Improved Touch Feedback** - Enhanced visual feedback for all touchable elements

### **Current Application State**
- ✅ **Game Setup** - Players can be added and games created successfully
- ✅ **UI Transitions** - Proper screen transitions from setup to game
- ✅ **Action Phase** - Correctly displays and manages player turns
- ✅ **Server Communication** - No more infinite loops or hanging
- ✅ **Basic Actions** - Players can perform actions (fundraise, network, etc.)
- ✅ **Turn Management** - Proper turn advancement
- ✅ **Mobile Experience** - Comprehensive mobile optimizations implemented

### **Test Infrastructure Improvements**
- ✅ **Serial Test Execution** - Tests now run sequentially to prevent interference
- ✅ **Specific Selectors** - All selectors now target specific containers
- ✅ **Proper Error Handling** - Tests no longer hang indefinitely
- ✅ **Mobile-Specific Tests** - Created comprehensive mobile testing suite

## 📱 **MOBILE EXPERIENCE COMPLETELY ENHANCED (July 16, 2025)**

### **Latest Mobile Improvements**
- **Immediate Feedback System**: Mobile users now receive instant feedback after sponsoring legislation and other actions
- **Enhanced Phase Indicators**: Clear progress indicators showing current round and phase with visual progress bars
- **Quick Action Panel**: Touch-friendly panel at bottom of screen for common actions (fundraise, network, sponsor, pass turn)
- **Mobile-Optimized Results**: Results overlay fully optimized for mobile screens with proper sizing and scrolling
- **Next Steps Guidance**: Contextual guidance after each action to help mobile users understand what happens next
- **Improved Touch Feedback**: Enhanced visual feedback for all touchable elements with proper scaling and animations

### **Mobile Features**
- **Touch-Friendly Interface**: All buttons sized for comfortable touch interaction
- **No Gesture Conflicts**: Swipe gestures disabled on mobile to prevent interference with action visibility
- **Dedicated Identity Button**: Easy access to player identity via 🎭 button in header
- **Modal-Based Information**: Identity and game log displayed in clean, accessible modals
- **Responsive Design**: Adapts beautifully to all screen sizes and orientations
- **Immediate Feedback**: Clear messages after actions to guide mobile users
- **Progress Indicators**: Visual progress bars and clear phase information
- **Quick Actions**: Easy access to common actions via touch-friendly panel

### **Mobile Testing Results**
- ✅ **All mobile improvements implemented and working**
- ✅ **Immediate feedback systems active**
- ✅ **Phase indicators enhanced and clear**
- ✅ **Quick actions panel functional**
- ✅ **Mobile CSS optimizations applied**
- ✅ **Next steps guidance working**
- ✅ **Touch feedback improved**

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
- **All mobile improvements implemented and working** ✅
- **Immediate feedback systems active** ✅
- **Phase indicators enhanced and clear** ✅
- **Quick actions panel functional** ✅
- **Mobile CSS optimizations applied** ✅
- **Next steps guidance working** ✅
- **Touch feedback improved** ✅

The mobile experience has been completely transformed with comprehensive improvements that provide immediate feedback, clear progress indicators, and enhanced usability for mobile users.

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
- **Game Flow**: Complete mobile game experience with proper screen transitions
- **Accessibility**: Keyboard navigation, screen readers, ARIA labels
- **Performance**: Load times, responsiveness
- **Cross-Device Testing**: iPhone, iPad, Samsung Galaxy across Chromium, Firefox, WebKit
- **Action Visibility**: Ensures all actions remain accessible on mobile devices

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
- **Non-interfering mobile experience** with clear action visibility

## 📚 Documentation

- `MOBILE_TESTING_GUIDE.md` - Complete mobile testing documentation
- `MOBILE_TEST_RESULTS.md` - Latest test results and analysis
- `MOBILE_IMPROVEMENTS_SUMMARY.md` - Latest mobile improvements and fixes
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