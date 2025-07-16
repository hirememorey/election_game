# Election: The Game - Web Version

A political board game now playable in your web browser! This is a mobile-friendly web interface for the Election game, built with Flask backend and vanilla JavaScript frontend.

## 🎮 Current Status

✅ **FIXED**: Static file serving (CSS/JS 404 errors resolved)  
✅ **WORKING**: All API endpoints tested and functional  
✅ **READY**: Game is playable in browser on any device  
✅ **MOBILE**: Responsive design for iPhone and other mobile devices  
✅ **APPLE-LEVEL DESIGN**: Professional, modern interface with Apple-inspired design system  
- All blue gradient bars have been removed for a cleaner, more information-dense interface.
- The UI is now more compact, with full-width identity cards and neutral backgrounds for all status bars.

## 🚀 Quick Start

### Option 1: Using the startup script (Recommended)
```bash
./start_server.sh
```

### Option 2: Manual startup
```bash
PORT=5001 python3 server.py
```

### Option 3: Test everything first
```bash
python3 test_api.py
```

Then open your browser to: **http://localhost:5001**

## 🎯 How to Play

1. **Start the server** using one of the methods above
2. **Open your browser** to `http://localhost:5001`
3. **Enter player names** (2-4 players)
4. **Click "Start Game"** to begin
5. **Use action buttons** to play:
   - Fundraise: Gain Political Capital (PC)
   - Network: Build connections
   - Form Alliance: Seek powerful allies
   - Sponsor Legislation: Pass laws (requires 5+ PC)
   - Declare Candidacy: Run for office
6. **Draw Event Cards** during the Event Phase
7. **Win** by achieving your mandate or winning the Presidency!

## 📱 Mobile Support

The game is fully optimized for mobile devices:
- Responsive design that works on iPhone, Android, tablets
- Touch-friendly buttons and interface
- Optimized for portrait and landscape orientations
- Works offline once loaded (except for API calls)

## 🔧 Technical Details

### Backend (Flask)
- **Port**: 5001 (configurable via PORT environment variable)
- **API Base**: `http://localhost:5001/api`
- **Static Files**: Served from `/static/` directory
- **CORS**: Enabled for development

### Frontend (Vanilla JS)
- **Framework**: No framework - pure HTML/CSS/JavaScript
- **API Communication**: REST API calls to Flask backend
- **State Management**: Client-side game state management
- **Mobile**: Responsive CSS with mobile-first design
- **Design System**: Apple-level design with SF Pro Display typography and modern UI

### Key Files
- `server.py` - Flask backend with API endpoints
- `static/index.html` - Main game interface with Apple-level design
- `static/script.js` - Game logic and API communication
- `static/style.css` - Apple-inspired design system with SF Pro Display typography
- `engine/` - Core game logic (reused from CLI version)
- `models/` - Game data models

## 🧪 Testing

Run the automated test suite:
```bash
python3 test_api.py
```

This tests:
- ✅ Static file serving (CSS, JS, HTML)
- ✅ Main page loading
- ✅ Game creation API
- ✅ Game state retrieval
- ✅ Action processing

## 🚀 Deployment

### Local Development
- Server runs on `http://localhost:5001`
- API available at `http://localhost:5001/api`
- Static files at `http://localhost:5001/static/`

### Production Deployment
See `DEPLOYMENT.md` for detailed instructions on:
- Render
- Netlify
- Heroku
- Railway
- VPS deployment

**Important**: Update `API_BASE_URL` in `static/script.js` for production deployment.

## 🐛 Recent Fixes

### Static File 404 Issue (RESOLVED)
**Problem**: CSS and JS files returning 404 errors  
**Root Cause**: HTML was using relative paths instead of Flask static paths  
**Solution**: Updated `static/index.html` to use `/static/` paths:
- `style.css` → `/static/style.css`
- `script.js` → `/static/script.js`

### API Port Mismatch (RESOLVED)
**Problem**: Frontend trying to connect to port 5000, server on 5001

**Solution**: For local development, always use port 5001 for the backend server. Port 5000 is reserved by macOS AirPlay Receiver.

## 🎯 Next Steps

### Immediate (Ready to implement)
1. **Add game persistence** - Save games to database/file
2. **Multiplayer support** - Real-time updates between players
3. **Game history** - View past games and results
4. **Sound effects** - Audio feedback for actions

### Future Enhancements
1. **AI opponents** - Play against computer players
2. **Tournament mode** - Multiple games with scoring
3. **Custom scenarios** - User-created game setups
4. **Analytics** - Game statistics and analysis

## 🛠️ Development

### Adding New Features
1. **Backend**: Add new endpoints in `server.py`
2. **Frontend**: Update `static/script.js` for new UI
3. **Styling**: Modify `static/style.css` for new elements
4. **Testing**: Add tests to `test_api.py`

### File Structure
```
election/
├── server.py          # Flask backend
├── static/            # Frontend files
│   ├── index.html     # Main game page
│   ├── script.js      # Game logic
│   └── style.css      # Styling
├── engine/            # Core game logic
├── models/            # Data models
├── test_api.py        # API tests
├── start_server.sh    # Startup script
└── requirements.txt   # Python dependencies
```

## 🎉 Success!

Your Election game is now fully functional as a web application! The static file serving issue has been resolved, all API endpoints are working, and the game is ready to play on any device with a web browser.

**Happy campaigning!** 🗳️ 

## UI/UX Updates
- The header is now minimal, showing only the game title and New Game button.
- All game state information (round, phase, mood, AP, PC, office) is consolidated in the compact game state bar for clarity.
- Redundant displays of Action Points, round, phase, and mood have been removed for a cleaner interface. 