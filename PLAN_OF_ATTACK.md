# Plan of Attack: ELECTION Game Development

## **🎯 Current Status: PLAYABLE**

The game is now **fully playable** with all major bugs fixed. The action system has been repaired and the game flows properly from term to term.

### **✅ Recent Achievements:**
- **Missing Action Resolvers**: Added `AcknowledgeAITurn` resolver to engine
- **System Action Resolvers**: Fixed to actually call engine methods instead of just logging
- **Method Name Issues**: Fixed `resolve_legislation_session` to call correct election methods
- **Action Creation**: Fixed missing `player_id` parameter handling

## **🚨 Critical Insights for Future Development**

### **The Real Problems Were Simple, Not Complex**

**What We Initially Thought**: The game had fundamental architectural issues requiring major refactoring.

**What We Actually Found**: The problems were simple infrastructure issues:
- Missing resolvers in the `action_resolvers` dictionary
- Parameter mismatches in action constructors
- Method name mismatches between components
- Server version issues (old code still running)

### **Debug Output Was Already Telling Us the Truth**

**What We Initially Ignored**: The debug output showing "No resolver found for action: AcknowledgeAITurn"

**What We Should Have Done**: Immediately trust the debug output and fix the missing resolvers first.

### **The Architecture Was Actually Sound**

**What We Initially Assumed**: The existing architecture needed major refactoring.

**What We Actually Found**: The architecture was well-designed with good separation of concerns. The problems were specific bugs, not fundamental flaws.

## **🎯 Development Philosophy**

### **1. Trust the Debug Output**
- The debug output contains the exact answers you're looking for
- When you see "No resolver found for action: X" → Add the missing resolver
- When you see "Error creating action from dict" → Check action constructor parameters

### **2. Test the Simplest Possible Explanation First**
- AI keeps taking actions → Check if AI thinks it has action points when it doesn't
- Action fails → Check if all required parameters are provided
- Server doesn't respond → Check if server is running the latest code

### **3. Fix Specific Bugs, Don't Rewrite Working Code**
- The existing codebase is 90% working
- Focus on the missing 10% rather than rewriting the working parts
- Trust the existing architecture and patterns

### **4. Server Version Management is Critical**
- Always restart the server after code changes
- The server process holds old code in memory
- Use `lsof -ti:5001 | xargs kill -9` to ensure clean restarts

## **🔧 Action System is the Core**

Everything in this game revolves around the action system:
- **Actions defined in**: `engine/actions.py`
- **Resolvers in**: `engine/resolvers.py` and mapped in `engine/engine.py`
- **Frontend sends actions via**: WebSocket
- **Missing resolvers = broken functionality**

### **Common Action System Issues:**
1. **Missing Resolvers**: Action exists but no resolver in `action_resolvers` dictionary
2. **Parameter Mismatches**: Action constructor expects different parameters than provided
3. **Method Name Issues**: Resolver calls non-existent methods
4. **Server Version Issues**: Old code still running in server process

## **📋 Development Process**

### **Phase 1: Immediate Assessment (First 30 minutes)**
1. **Kill and restart server** - Ensure latest code is running
2. **Read debug output carefully** - Look for missing resolvers or parameter errors
3. **Test action system directly** - Create simple test to verify all actions have resolvers
4. **Check server version** - Verify server is running latest code

### **Phase 2: Fix Infrastructure Issues (Day 1-2)**
1. **Add missing resolvers** to `action_resolvers` dictionary
2. **Fix parameter mismatches** in action constructors
3. **Implement stub system action resolvers** to actually call engine methods
4. **Fix method name issues** between components

### **Phase 3: Systematic Bug Fixes (Day 2-3)**
1. **Fix action creation** to handle missing parameters
2. **Implement system action resolvers** properly
3. **Remove AI acknowledgment complexity** if causing issues
4. **Test each fix individually** before moving to next

### **Phase 4: Comprehensive Testing (Day 3)**
1. **Test complete game flow** from term to term
2. **Test all action types** to ensure they work
3. **Test error handling** for edge cases
4. **Test server restarts** to ensure changes persist

## **🐛 Debugging Guide**

### **Common Issues and Solutions:**

#### **1. "No resolver found for action: X"**
- **Problem**: Action exists but no resolver in dictionary
- **Solution**: Add resolver to `action_resolvers` in `engine/engine.py`
- **Example**: `"AcknowledgeAITurn": resolvers.resolve_acknowledge_ai_turn`

#### **2. "Error creating action from dict"**
- **Problem**: Action constructor expects different parameters
- **Solution**: Check action constructor in `engine/actions.py` and fix parameter handling
- **Example**: Add missing `player_id` parameter in `game_session.py`

#### **3. "object has no attribute 'X'"**
- **Problem**: Method name mismatch between components
- **Solution**: Check method names and imports
- **Example**: `run_election_phase` doesn't exist, should be `resolve_elections_session`

#### **4. Server not responding to changes**
- **Problem**: Server running old code
- **Solution**: Kill and restart server
- **Command**: `lsof -ti:5001 | xargs kill -9 && python3 server.py`

### **Debug Process:**
1. **Read debug output carefully** - it often contains the exact answer
2. **Test components in isolation** - don't debug through complex systems
3. **Check server version** after any code changes
4. **Assume simple explanations** first
5. **Trust the existing architecture** - focus on missing pieces

## **🎮 Testing Strategy**

### **Unit Tests**
- Test all action resolvers individually
- Test action creation with various parameters
- Test state transitions for each action type

### **Integration Tests**
- Test complete action flow from frontend to backend
- Test WebSocket communication for all action types
- Test server restart and state persistence

### **End-to-End Tests**
- Test complete game flow from term to term
- Test all major game features (legislation, elections, etc.)
- Test error recovery scenarios

## **📊 Success Metrics**

### **Functional Requirements**
- [x] Complete turn-to-turn gameplay works
- [x] No infinite loops or stuck states
- [x] All actions process correctly
- [x] Clear error messages when things go wrong
- [x] Smooth transitions between all game phases

### **Technical Requirements**
- [x] All actions have resolvers
- [x] No parameter mismatches in action creation
- [x] No method name mismatches between components
- [x] Server restarts properly with latest code
- [x] Debug output is clear and helpful

## **🚀 Future Development**

### **Immediate Priorities**
1. **Monitor for new missing resolvers** - Add comprehensive testing
2. **Improve error messages** - Make debugging easier for future developers
3. **Add action system validation** - Prevent missing resolvers in future
4. **Document action system** - Clear documentation for all actions and resolvers

### **Long-term Goals**
1. **Automated testing** for action coverage
2. **Action system validation** to catch missing resolvers
3. **Better error handling** for edge cases
4. **Performance optimization** for large games

## **🎯 Key Lessons Learned**

### **1. Trust the Debug Output**
The debug output was telling us exactly what was wrong, but we were looking for complex explanations.

### **2. The Architecture Was Sound**
The existing codebase had good separation of concerns. The problems were specific bugs, not fundamental flaws.

### **3. Simple Explanations Are Usually Correct**
The simplest explanation for a bug is usually the right one. Check basic variable references before diving into complex debugging.

### **4. Test Infrastructure First**
Always test basic functionality before assuming complex problems. Server version issues are common and easy to fix.

### **5. Fix Specific Bugs, Don't Rewrite Working Code**
The game was 90% working. Focus on the missing 10% rather than rewriting the working parts.

## **📝 Documentation**

- `README.md`: Current status and quick start guide
- `developer_handoff.md`: Critical insights for new developers
- `PHYSICAL_GAME_SPEC.md`: Complete game rules and mechanics
- `STATE_DRIVEN_REFACTOR.md`: Architecture decisions and state management

The key insight is that this project is much closer to working than it appears. The problems are simple infrastructure issues, not complex architectural flaws. Future developers should focus on the missing pieces rather than rewriting the working parts. 