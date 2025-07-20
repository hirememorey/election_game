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

## Game Actions

Players can take the following actions during their turn:

- **Fundraise** (1 AP): Gain Political Capital (PC) - 5 PC base, +2 for Fundraiser archetype, +10 with Hedge Fund Bro ally
- **Network** (1 AP): Gain 2 PC + 1-2 political favors
- **Sponsor Legislation** (2 AP): Create legislation for votes/mood (cost varies by legislation type)
- **Declare Candidacy** (2 AP): Run for office (Round 4 only, cost varies by office + optional PC commitment)
- **Use Favor** (1 AP): Strategic advantage actions (requires having political favors, now with selection menu)
- **Support/Oppose Legislation** (1 AP): **🎰 Gambling-style system** - commit PC during any turn with risk/reward mechanics
- **Trading** (0 AP): Propose trades of PC/favors for votes during legislation sessions

## 🛠️ Development

### Project Structure
```