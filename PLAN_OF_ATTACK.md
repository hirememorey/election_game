# Plan of Attack: Ensuring Complete Term-to-Term Gameplay

## Current Status Summary

The game has been successfully stabilized from a critical startup crash, but there's a remaining issue where the human player cannot interact with the game despite the backend logic being correct.

### Issues Resolved ✅
1. **Player Dataclass Conflict**: Fixed `is_incumbent` property conflict in `models/components.py`
2. **Action Registration**: Fixed missing decorators on `AcknowledgeAITurn` and `ActionSupportLegislation` in `engine/actions.py`
3. **Frontend DOM Elements**: Updated `static/index.html` to include all required elements
4. **Server Startup**: Server now starts cleanly without crashes

### Current Issue 🔍
**Problem**: The human player cannot interact with the game (no action buttons appear) despite the backend being fully functional.

**Evidence**:
- Backend debug shows: `Is human turn? True`, `Valid actions for human: 4`
- Frontend receives state updates but no action buttons appear
- Server logs are clean with no errors
- WebSocket communication is working

**Root Cause Hypothesis**: The issue is likely in the frontend JavaScript rendering, not the backend logic.

## Detailed Plan of Attack

### Phase 1: Frontend Debugging (Priority: HIGH)

#### 1.1 Browser Console Investigation
- **Action**: Open browser dev tools and check for JavaScript errors
- **Expected**: May find runtime errors preventing button rendering
- **If Found**: Fix the specific JavaScript error

#### 1.2 DOM Element Verification
- **Action**: Verify that `actions-container` element exists and is accessible
- **Method**: Add `console.log(document.getElementById('actions-container'))` to frontend
- **Expected**: Should return the DOM element, not null

#### 1.3 State Data Verification
- **Action**: Add debugging to frontend to log received state data
- **Method**: Add `console.log('State received:', state)` in `renderState` function
- **Expected**: Should see valid actions in the state object

#### 1.4 Conditional Logic Testing
- **Action**: Test the exact condition that determines when to show actions
- **Method**: Add logging for `humanPlayer`, `state.current_player_index`, and the comparison
- **Expected**: Should see `humanPlayer` found and condition evaluating to `true`

### Phase 2: Frontend Code Analysis (Priority: HIGH)

#### 2.1 Bundle Verification
- **Action**: Verify the bundled JavaScript contains the latest code
- **Method**: Check `static/dist/bundle.js` for the `renderState` function
- **Expected**: Should contain the correct logic for showing action buttons

#### 2.2 CSS Visibility Check
- **Action**: Verify action buttons aren't being rendered but hidden by CSS
- **Method**: Inspect DOM for button elements that might be invisible
- **Expected**: Should find visible button elements or confirm they're not being created

#### 2.3 Event Handler Verification
- **Action**: Test if action buttons are created but click handlers don't work
- **Method**: Add test click handlers to verify button creation
- **Expected**: Should see buttons respond to clicks

### Phase 3: Backend Verification (Priority: MEDIUM)

#### 3.1 WebSocket Message Verification
- **Action**: Verify the exact JSON being sent to frontend
- **Method**: Add logging in `get_state_for_client()` to print the sent data
- **Expected**: Should see `valid_actions` array with 4 actions

#### 3.2 Action Serialization Test
- **Action**: Verify action objects serialize correctly
- **Method**: Test `action.to_dict()` for each action type
- **Expected**: Should produce valid JSON for each action

### Phase 4: Integration Testing (Priority: MEDIUM)

#### 4.1 Manual End-to-End Test
- **Action**: Perform complete manual test once frontend is fixed
- **Steps**:
  1. Start server and open browser
  2. Verify action buttons appear
  3. Click "Sponsor Legislation" 
  4. Select a bill to sponsor
  5. Play through all 4 rounds
  6. Verify end-of-term resolution phases
  7. Confirm transition to next term

#### 4.2 Term Transition Validation
- **Action**: Specifically test the term-to-term transition
- **Method**: Play through complete term and observe transition
- **Expected**: Should see "Resolve Legislation" → "Resolve Elections" → "Start Next Term"

### Phase 5: Automated Testing (Priority: LOW)

#### 5.1 Create End-to-End Test
- **Action**: Write automated test that validates complete gameplay
- **Method**: Use browser automation (Playwright/Selenium) to test full flow
- **Expected**: Should pass consistently

#### 5.2 Unit Test Coverage
- **Action**: Add unit tests for critical game flow components
- **Method**: Test `GameSession`, `GameEngine`, and action processing
- **Expected**: Should have good coverage of core logic

## Implementation Strategy

### Immediate Next Steps (Do First)
1. **Browser Console Check**: Open dev tools and look for JavaScript errors
2. **DOM Verification**: Add `console.log` to verify `actions-container` exists
3. **State Logging**: Add logging to see what state data is received
4. **Conditional Debugging**: Add logging to test the human player condition

### If Frontend Issues Found
1. Fix the specific JavaScript error or DOM issue
2. Rebuild frontend with `npm run build`
3. Test manually in browser
4. If working, proceed to Phase 4

### If Frontend Issues Not Found
1. Add more detailed backend logging
2. Verify WebSocket message format
3. Check for any serialization issues
4. Test with a simple frontend test case

## Key Insights from Previous Work

### The "Reality-First" Approach Works
- Starting with `python3 server.py` immediately revealed the critical startup crash
- Server logs provided the most valuable diagnostic information
- Manual testing was more effective than complex integration tests

### Common Failure Points
1. **Action Registration**: Missing `@_register_action` decorators cause "Unknown action type" errors
2. **Dataclass Conflicts**: Property/field conflicts cause "can't set attribute" errors
3. **DOM Element Mismatches**: Frontend expecting elements that don't exist in HTML
4. **Bundle Issues**: Old JavaScript being cached by browser

### Debugging Philosophy
- **Start Simple**: Always begin with the smoke test (run the application)
- **Trust the Logs**: Server logs often contain the exact error information needed
- **Isolate Issues**: Test backend and frontend separately before integration
- **Manual Validation**: Don't rely solely on automated tests for complex UI flows

## Success Criteria

The game is working correctly when:
1. ✅ Server starts without errors
2. ✅ Browser connects and receives game state
3. ✅ Human player sees action buttons (Fundraise, Network, Sponsor Legislation, Pass Turn)
4. ✅ Human player can click actions and see appropriate responses
5. ✅ Game progresses through all 4 rounds of a term
6. ✅ End-of-term resolution phases appear (Resolve Legislation, Resolve Elections)
7. ✅ Game transitions smoothly to the next term
8. ✅ Complete term-to-term gameplay works without interruption

## Files to Monitor

### Critical Files
- `static/app.js` - Frontend logic
- `static/index.html` - DOM structure
- `game_session.py` - Game flow management
- `engine/actions.py` - Action definitions
- `models/components.py` - Data models

### Log Files
- `server.log` - Server-side errors and WebSocket activity
- Browser console - Frontend errors and state data

## Fallback Plan

If the frontend issues prove intractable:
1. Create a minimal test frontend that only displays the raw state data
2. Verify the backend is sending correct data
3. Gradually rebuild the frontend from scratch
4. Use the working backend as the foundation

This approach ensures we can isolate whether the issue is in the backend logic or frontend rendering. 