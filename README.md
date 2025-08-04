# ELECTION Game

A competitive political strategy game where players manage Political Capital (PC), sponsor and defeat legislation, form alliances, and compete for political office. Features a **Secret Commitment System** where players secretly fund or fight legislation, leading to dramatic reveals.

## **🎮 Current Status: FULLY PLAYABLE**

The game is now **fully playable** with all major bugs fixed. The action system has been repaired, WebSocket connections work on HTTPS deployments, and the game flows properly from term to term.

### **✅ Recent Fixes Applied:**
- **WebSocket HTTPS Support**: Fixed protocol detection for secure deployments
- **Two-Step Declare Candidacy**: Added additional commitment flow beyond base office cost
- **Cost Calculation Fix**: Fixed committed_pc calculation in election system
- **Missing Action Resolvers**: Added `AcknowledgeAITurn` resolver to engine
- **System Action Resolvers**: Fixed to actually call engine methods instead of just logging
- **Method Name Issues**: Fixed `resolve_legislation_session` to call correct election methods
- **Action Creation**: Fixed missing `player_id` parameter handling
- **Personal Mandate Display**: Added UI to show players their hidden victory conditions

### **🎯 New Features:**
- **Enhanced Declare Candidacy**: Players can now commit additional PC beyond the base office cost
- **Strategic Campaign Funding**: More nuanced election strategies with flexible commitment amounts
- **HTTPS Deployment Ready**: Works on Render and other HTTPS platforms
- **Personal Mandate Display**: Players can view their secret victory conditions during gameplay

## **🚨 Critical Information for Developers**

### **1. Debug Output is Your Best Friend**
The server logs and debug output contain the exact answers you're looking for:
- `"No resolver found for action: X"` → Add the missing resolver
- `"Error creating action from dict"` → Check action constructor parameters
- `"object has no attribute 'X'"` → Check method names and imports

### **2. The Architecture is Actually Sound**
The existing codebase has good separation of concerns. Problems are almost always:
- Missing resolvers in the `action_resolvers` dictionary
- Parameter mismatches in action constructors
- Method name mismatches between components
- Server version issues (old code still running)

### **3. Test the Simplest Possible Explanation First**
When something doesn't work, ask: "What's the simplest possible explanation?"
- AI keeps taking actions → Check if AI thinks it has action points when it doesn't
- Action fails → Check if all required parameters are provided
- Server doesn't respond → Check if server is running the latest code

### **4. Server Version Management is Critical**
After any code change:
```bash
lsof -ti:5001 | xargs kill -9  # Kill server
python3 server.py               # Restart server
```

### **5. The Action System is the Core**
Everything revolves around the action system:
- Actions defined in `engine/actions.py`
- Resolvers in `engine/resolvers.py` and mapped in `engine/engine.py`
- Frontend sends actions via WebSocket
- Missing resolvers = broken functionality

### **6. Frontend Build System Awareness**
The frontend uses Webpack to compile JavaScript:
- Changes to `static/app.js` require `npm run build` to take effect
- Always rebuild after JavaScript changes
- Test the build process before adding complex features

## **🎯 Quick Start**

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   npm install
   ```

2. **Start the Server:**
   ```bash
   python3 server.py
   ```

3. **Open Browser:**
   Navigate to `http://localhost:5001`

4. **Play the Game:**
   - Manage Political Capital (PC)
   - Sponsor and oppose legislation
   - Form secret commitments
   - Compete for political office with strategic funding
   - View your Personal Mandate by clicking "Show/Hide Mandate"

## **🏗️ Architecture Overview**

### **Core Components:**
- **Engine** (`engine/`): Game logic and action processing
- **Models** (`models/`): Game state and data structures
- **Personas** (`personas/`): AI player strategies
- **Server** (`server.py`): WebSocket communication
- **Frontend** (`static/`): React-based UI

### **Key Systems:**
- **Action System**: All game interactions go through actions
- **Secret Commitment System**: Hidden funding mechanics
- **Legislation System**: Bill sponsorship and voting
- **Election System**: Political office competition with flexible funding
- **AI System**: Multiple persona strategies
- **Personal Mandate System**: Hidden victory conditions with UI display

## **🐛 Debugging Guide**

### **Common Issues:**
1. **Server not responding**: Kill and restart server
2. **Action fails**: Check if resolver exists in `action_resolvers`
3. **AI infinite loops**: Check action point validation logic
4. **Missing parameters**: Check action constructor requirements
5. **WebSocket connection fails**: Check protocol (ws:// vs wss://) for HTTPS
6. **Frontend changes not appearing**: Run `npm run build` after JavaScript changes

### **Debug Process:**
1. Read the debug output carefully
2. Test the action system directly
3. Check server version after code changes
4. Assume simple explanations first
5. Trust the existing architecture

## **📊 Game Features**

- **Political Capital Management**: Earn and spend PC strategically
- **Legislation System**: Sponsor, support, and oppose bills
- **Secret Commitments**: Hidden funding creates dramatic reveals
- **Enhanced Election System**: Compete for offices with flexible campaign funding
- **AI Opponents**: Multiple personas with different strategies
- **Multi-term Gameplay**: Progress through multiple terms
- **HTTPS Deployment**: Works on secure platforms like Render
- **Personal Mandate Display**: View your secret victory conditions during gameplay

## **🎯 Development Philosophy**

- **Fix specific bugs, don't rewrite working code**
- **Trust the debug output**
- **Test infrastructure first**
- **Assume simple explanations**
- **The architecture is sound - focus on missing pieces**
- **Understand the build system before making frontend changes**

## **📝 Documentation**

- `PHYSICAL_GAME_SPEC.md`: Complete game rules and mechanics
- `STATE_DRIVEN_REFACTOR.md`: Architecture decisions and state management
- `PLAN_OF_ATTACK.md`: Development strategy and priorities
- `developer_handoff.md`: Critical insights for new developers