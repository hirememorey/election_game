# Network Action Design: Merged Action System

## Overview

This document outlines the design for merging the current "Network" and "Form Alliance" actions into a single, more engaging "Network" action that offers players strategic choices and psychological tension.

## Current State Analysis

### Existing Actions

**Network (Current)**
- Cost: 2 Political Capital
- Effect: Gain 1-2 political favors
- Risk: Low
- Strategic Value: Tactical, immediate benefits

**Form Alliance (Current)**
- Cost: 5 Political Capital  
- Effect: Gain a powerful ally with potential weaknesses
- Risk: High (ally can betray or have hidden agendas)
- Strategic Value: Strategic, long-term investment

### Problems with Current System
1. **Action Bloat**: Two similar actions compete for player attention
2. **Clear Dominance**: Network is often preferred due to lower cost and immediate benefits
3. **Missed Opportunities**: Form Alliance's psychological elements aren't leveraged
4. **Reduced Tension**: Players don't face meaningful risk/reward decisions

## Proposed Design: Thrilling Network Action

### Core Concept

Transform "Network" into a single action that offers players a choice between:
1. **Safe Networking**: Low-cost, immediate benefits (current Network behavior)
2. **Risky Alliance**: High-cost, high-reward with psychological tension (current Form Alliance behavior)

### Action Structure

```python
class NetworkAction(Action):
    name = "Network"
    base_cost = 2  # Minimum cost
    
    def __init__(self, network_type="safe"):
        self.network_type = network_type  # "safe" or "risky"
        self.cost = 2 if network_type == "safe" else 5
```

### Player Choice Flow

1. **Player selects "Network" action**
2. **System presents choice**:
   - "Safe Networking" (2 PC) - Gain 1-2 political favors
   - "Risky Alliance" (5 PC) - Gain powerful ally with potential betrayal
3. **Player makes choice**
4. **Action resolves with appropriate effects**

## Implementation Specifications

### Backend Changes

#### 1. Action Definition (`engine/actions.py`)

```python
class NetworkAction(Action):
    name = "Network"
    description = "Build political connections or form strategic alliances"
    
    def __init__(self, network_type="safe"):
        super().__init__()
        self.network_type = network_type
        self.cost = 2 if network_type == "safe" else 5
        self.description = self._get_description()
    
    def _get_description(self):
        if self.network_type == "safe":
            return "Safe Networking (2 PC): Gain 1-2 political favors"
        else:
            return "Risky Alliance (5 PC): Gain powerful ally with potential betrayal"
```

#### 2. Action Resolution (`engine/resolvers.py`)

```python
def resolve_network_action(game_state, player_id, network_type):
    """
    Resolve network action based on player's choice.
    
    Args:
        game_state: Current game state
        player_id: ID of player taking action
        network_type: "safe" or "risky"
    
    Returns:
        Updated game state with effects applied
    """
    if network_type == "safe":
        return resolve_safe_networking(game_state, player_id)
    else:
        return resolve_risky_alliance(game_state, player_id)

def resolve_safe_networking(game_state, player_id):
    """Resolve safe networking (current Network action logic)"""
    # Existing network logic here
    favors_gained = random.randint(1, 2)
    # Apply favor gain logic...
    return updated_game_state

def resolve_risky_alliance(game_state, player_id):
    """Resolve risky alliance (current Form Alliance logic)"""
    # Existing form alliance logic here
    # Include betrayal mechanics, hidden agendas, etc.
    return updated_game_state
```

#### 3. API Endpoint Updates (`server.py`)

```python
@app.route('/api/game/<game_id>/action', methods=['POST'])
def process_action(game_id):
    data = request.get_json()
    action_type = data.get('action')
    
    if action_type == 'network':
        network_type = data.get('network_type', 'safe')
        # Validate network_type is 'safe' or 'risky'
        if network_type not in ['safe', 'risky']:
            return jsonify({'error': 'Invalid network type'}), 400
        
        # Process network action with type
        result = engine.process_action(game_state, player_id, 
                                     NetworkAction(network_type))
```

### Frontend Changes

#### 1. Action Button (`static/script.js`)

```javascript
function createNetworkActionButton() {
    const button = document.createElement('button');
    button.textContent = 'Network';
    button.className = 'action-button network-button';
    button.onclick = showNetworkChoice;
    return button;
}

function showNetworkChoice() {
    // Create modal or dropdown with two options
    const choiceModal = document.createElement('div');
    choiceModal.className = 'network-choice-modal';
    
    const safeOption = document.createElement('button');
    safeOption.textContent = 'Safe Networking (2 PC)';
    safeOption.onclick = () => performNetworkAction('safe');
    
    const riskyOption = document.createElement('button');
    riskyOption.textContent = 'Risky Alliance (5 PC)';
    riskyOption.onclick = () => performNetworkAction('risky');
    
    choiceModal.appendChild(safeOption);
    choiceModal.appendChild(riskyOption);
    document.body.appendChild(choiceModal);
}

function performNetworkAction(networkType) {
    const actionData = {
        action: 'network',
        network_type: networkType
    };
    
    fetch(`/api/game/${gameId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(actionData)
    })
    .then(response => response.json())
    .then(data => {
        updateGameState(data);
        hideNetworkChoice();
    });
}
```

#### 2. CSS Styling (`static/style.css`)

```css
.network-choice-modal {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    border: 2px solid #333;
    border-radius: 8px;
    padding: 20px;
    z-index: 1000;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
}

.network-choice-modal button {
    display: block;
    width: 100%;
    margin: 10px 0;
    padding: 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 16px;
}

.network-choice-modal button:first-child {
    background: #4CAF50; /* Green for safe */
    color: white;
}

.network-choice-modal button:last-child {
    background: #f44336; /* Red for risky */
    color: white;
}
```

## Psychological Design Elements

### Risk/Reward Tension

1. **Safe Networking**:
   - Immediate, predictable benefits
   - Low risk, low reward
   - Tactical value

2. **Risky Alliance**:
   - High potential rewards
   - Risk of betrayal or hidden agendas
   - Strategic, long-term value
   - Creates memorable moments

### Player Decision Factors

- **Resource Availability**: Can player afford 5 PC?
- **Game Phase**: Early game favors safe, late game may favor risky
- **Player Psychology**: Risk-averse vs. risk-seeking players
- **Current Position**: Desperate players may choose risky options

## Implementation Checklist

### Phase 1: Backend Foundation
- [ ] Update `NetworkAction` class to support network_type parameter
- [ ] Modify action resolution logic in `resolvers.py`
- [ ] Update API endpoint to handle network_type parameter
- [ ] Remove `FormAllianceAction` class
- [ ] Update action validation logic

### Phase 2: Frontend Integration
- [ ] Create network choice UI (modal/dropdown)
- [ ] Update action button to trigger choice interface
- [ ] Modify API calls to include network_type
- [ ] Add CSS styling for choice interface
- [ ] Test both choice paths

### Phase 3: Testing & Polish
- [ ] Create unit tests for both network types
- [ ] Test edge cases (insufficient PC, invalid choices)
- [ ] Verify UI responsiveness on mobile
- [ ] Test game balance with new action structure
- [ ] Update documentation

## Balance Considerations

### Cost Structure
- **Safe Networking**: 2 PC for 1-2 favors (current balance)
- **Risky Alliance**: 5 PC for powerful ally + risk (current balance)

### Strategic Impact
- Maintains current game balance
- Adds meaningful choice without power creep
- Preserves existing psychological elements
- Reduces action complexity while maintaining depth

## Migration Strategy

### Backward Compatibility
- Existing games can continue with current actions
- New games use merged action system
- Gradual transition to avoid disruption

### Data Migration
- No database changes required (in-memory storage)
- Action history may show "Network (Safe)" or "Network (Risky)"
- Preserve existing game state structure

## Success Metrics

### Player Engagement
- Increased use of alliance mechanics
- More strategic decision-making
- Reduced action paralysis from too many choices

### Game Balance
- Maintained win rates across player types
- Balanced resource economy
- Meaningful risk/reward decisions

### Technical Quality
- Clean, maintainable code
- Comprehensive test coverage
- Responsive, intuitive UI

## Future Enhancements

### Potential Expansions
1. **Multiple Alliance Types**: Different risk levels and rewards
2. **Dynamic Costs**: Costs based on game state or player position
3. **Alliance Consequences**: Long-term effects of alliance choices
4. **Player Reputation**: Track alliance reliability for future games

### Advanced Features
1. **Alliance Betrayal Mechanics**: More sophisticated betrayal systems
2. **Alliance Benefits**: Unique abilities or resources from allies
3. **Alliance Politics**: Multi-player alliance dynamics
4. **Historical Tracking**: Record of alliance success/failure rates

---

## Implementation Notes for Developers

1. **Start with Backend**: Implement the action logic before touching the frontend
2. **Test Thoroughly**: Both network types should be extensively tested
3. **Consider UX**: The choice interface should be intuitive and quick
4. **Maintain Balance**: Don't change the underlying mechanics, just the presentation
5. **Document Changes**: Update any relevant documentation or comments

This design transforms two competing actions into a single, more engaging choice that maintains all existing functionality while adding meaningful strategic depth and psychological tension. 