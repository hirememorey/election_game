# Election Game - Mechanics Improvements

## 🎯 Issues Addressed

We've successfully implemented three major missing game mechanics that were identified:

### 1. ✅ **Political Favors System**
**Problem**: Players gained favors from networking but couldn't use them.

**Solution**: 
- Added `ActionUseFavor` action type
- Implemented favor usage with different effects:
  - **Extra Fundraising**: Gain 8 PC
  - **Legislative Influence**: Add 5 PC support to pending legislation
  - **Media Spin**: Improve public mood by +1
  - **Political Pressure**: Target another player to make them lose 3 PC
  - **Generic Favor**: Gain 5 PC (fallback for unknown favor types)
- Frontend shows available favors and allows players to use them
- Favors are consumed when used

### 2. ✅ **Candidacy Timing Restriction**
**Problem**: Players could only run for office in the final round of each turn.

**Solution**:
- Added `candidacy_declared_this_round` flag to GameState
- Only one candidacy can be declared per round
- Flag resets at the start of each new round (during upkeep phase)
- Frontend only shows candidacy options if no candidacy has been declared this round

### 3. ✅ **Legislation Support/Opposition System**
**Problem**: Sponsoring legislation was a solo act - other players couldn't support or oppose.

**Solution**:
- Added `PendingLegislation` class to track legislation waiting for resolution
- Added `ActionSupportLegislation` and `ActionOpposeLegislation` action types
- Legislation now works in two phases:
  1. **Sponsor Phase**: Player sponsors legislation (creates pending legislation)
  2. **Response Phase**: Other players can support or oppose with PC
- Legislation resolution happens at the end of the round (during upkeep)
- Support/opposition affects the final roll for legislation success
- Supporters get rewarded if legislation passes

## 🔧 Technical Implementation

### New Action Types
```python
@dataclass
class ActionUseFavor(Action):
    favor_id: str
    target_player_id: int = -1

@dataclass
class ActionSupportLegislation(Action):
    legislation_id: str
    support_amount: int

@dataclass
class ActionOpposeLegislation(Action):
    legislation_id: str
    oppose_amount: int
```

### New Game State Fields
```python
@dataclass
class GameState:
    # ... existing fields ...
    pending_legislation: Optional[PendingLegislation] = None
    candidacy_declared_this_round: bool = False
```

### New Resolver Functions
- `resolve_use_favor()`: Handles favor usage with different effects
- `resolve_support_legislation()`: Allows players to support pending legislation
- `resolve_oppose_legislation()`: Allows players to oppose pending legislation
- `resolve_pending_legislation()`: Resolves legislation at end of round

## 🎮 Gameplay Flow

### Political Favors
1. Player uses "Network" action → gains a political favor
2. Player can use favor during their turn → favor is consumed
3. Different favors have different effects (PC gain, mood change, etc.)

### Candidacy Timing
1. Only one player can declare candidacy per round
2. Once a candidacy is declared, no other candidacies allowed until next round
3. Candidacy flag resets during upkeep phase

### Legislation Process
1. **Sponsor**: Player sponsors legislation (costs PC, creates pending legislation)
2. **Response**: Other players can support (1 PC) or oppose (1 PC) the legislation
3. **Resolution**: At end of round, legislation is resolved with support/opposition affecting the roll
4. **Rewards**: Sponsor gets rewards if passed, supporters get partial PC back if passed

## 🎨 Frontend Improvements

### New UI Sections
- **Player Favors Section**: Shows current player's available favors
- **Pending Legislation Section**: Shows currently pending legislation details
- **Enhanced Action Buttons**: Context-aware actions based on game state

### Visual Design
- Green-themed favor section with favor cards
- Yellow-themed pending legislation section
- Clear indication of when actions are available/unavailable

## 🧪 Testing

The improvements have been tested and integrated with:
- ✅ Backend API endpoints
- ✅ Frontend JavaScript logic
- ✅ CSS styling for new UI elements
- ✅ Game state management
- ✅ Action resolution system

## 🚀 How to Use

1. **Start the server**: `./start_server.sh`
2. **Open browser**: `http://localhost:5001`
3. **Play the game** with the new mechanics:
   - Use "Network" to gain favors, then use them strategically
   - Only one player can declare candidacy per round
   - Support or oppose other players' legislation
   - Watch legislation resolution at the end of each round

## 🎯 Strategic Implications

### Political Favors
- Favors provide strategic advantages and should be used at optimal times
- Different favor types encourage different play styles
- Favors add depth to the networking action

### Candidacy Timing
- Creates tension around when to declare candidacy
- Prevents multiple candidacies from cluttering the same round
- Makes candidacy declaration more strategic

### Legislation Support/Opposition
- Encourages political alliances and rivalries
- Makes legislation more interactive and engaging
- Adds risk/reward for supporting others' legislation
- Creates negotiation opportunities between players

## 🔮 Future Enhancements

Potential next steps:
1. **Advanced Favor Types**: More complex favor effects
2. **Legislation Negotiation**: Players can negotiate before supporting/opposing
3. **Candidacy Alliances**: Players can support each other's candidacies
4. **Favor Trading**: Players can trade favors with each other
5. **Legislation Amendments**: Players can modify pending legislation

---

**The game now has much richer strategic depth and player interaction!** 🗳️ 