# Game Refinements Implementation Plan

## Overview

This plan addresses three major criticisms of the current game design:
1. **Dice-based legislation resolution** undermines strategic competence
2. **One action per turn** limits player autonomy and creates slow gameplay
3. **Unstructured trading** can intimidate new players and bog down the game

## Phase 1: Influence System (Remove Dice from Legislation)

### Problem Analysis
- Current system: Dice roll + PC support bonuses determine legislation success
- Issue: Strategic planning can be invalidated by random chance
- Impact: Players feel frustrated when good strategy is thwarted by luck

### Solution: Secret PC Commitment System
Replace dice with a strategic bidding system where players secretly commit PC to support/oppose legislation.

### Implementation Steps

#### 1.1 Modify Legislation Resolution Logic
**File**: `engine/resolvers.py`
**Function**: `resolve_pending_legislation()`

**Changes**:
- Remove dice rolling logic (lines 320-340)
- Remove support bonus calculations
- Add influence commitment resolution
- Calculate success based purely on committed PC vs legislation targets

**New Logic**:
```python
def resolve_pending_legislation(state: GameState) -> GameState:
    """Resolves legislation using secret PC commitments instead of dice."""
    if not state.pending_legislation or state.pending_legislation.resolved:
        return state
    
    pending = state.pending_legislation
    bill = state.legislation_options[pending.legislation_id]
    sponsor = state.get_player_by_id(pending.sponsor_id)
    
    if not sponsor:
        state.add_log("Error: Sponsor not found for pending legislation.")
        return state
    
    state.add_log(f"\n--- Resolving {bill.title} (Influence System) ---")
    
    # Calculate total influence committed
    total_support = sum(pending.support_players.values())
    total_opposition = sum(pending.oppose_players.values())
    net_influence = total_support - total_opposition
    
    # Show committed amounts
    if pending.support_players:
        support_details = []
        for player_id, amount in pending.support_players.items():
            player = state.get_player_by_id(player_id)
            if player:
                support_details.append(f"{player.name} ({amount} PC)")
        state.add_log(f"Support: {', '.join(support_details)}")
    
    if pending.oppose_players:
        oppose_details = []
        for player_id, amount in pending.oppose_players.items():
            player = state.get_player_by_id(player_id)
            if player:
                oppose_details.append(f"{player.name} ({amount} PC)")
        state.add_log(f"Opposition: {', '.join(oppose_details)}")
    
    state.add_log(f"Net influence: {net_influence} PC")
    
    # Determine outcome based on influence vs targets
    outcome = "Failure"
    if net_influence >= bill.crit_target:
        outcome = "Critical Success"
        sponsor.pc += bill.crit_reward
        state.public_mood = min(3, state.public_mood + bill.mood_change)
        state.add_log(f"Critical Success! {sponsor.name} gains {bill.crit_reward} PC.")
    elif net_influence >= bill.success_target:
        outcome = "Success"
        sponsor.pc += bill.success_reward
        state.public_mood = min(3, state.public_mood + bill.mood_change)
        state.add_log(f"Success! {sponsor.name} gains {bill.success_reward} PC.")
    else:
        sponsor.pc -= bill.failure_penalty
        state.add_log(f"Failure! The bill fails. {sponsor.name} loses {bill.failure_penalty} PC.")
    
    # Reward supporters if legislation passed
    passed = outcome in ["Success", "Critical Success"]
    if passed and pending.support_players:
        reward_per_pc = 1  # Supporters get 1 PC back for each PC they spent
        for player_id, amount in pending.support_players.items():
            player = state.get_player_by_id(player_id)
            if player:
                reward = min(amount, reward_per_pc * amount)
                player.pc += reward
                state.add_log(f"{player.name} receives {reward} PC for supporting successful legislation.")
    
    # Record result
    state.last_sponsor_result = {'player_id': sponsor.id, 'passed': passed}
    state.legislation_history.append({
        'sponsor_id': sponsor.id, 
        'leg_id': bill.id, 
        'outcome': outcome,
        'support_players': dict(pending.support_players),
        'oppose_players': dict(pending.oppose_players),
        'net_influence': net_influence
    })
    
    # Mark as resolved
    pending.resolved = True
    state.pending_legislation = None
    
    return state
```

#### 1.2 Update Legislation Data Structure
**File**: `models/components.py`
**Class**: `Legislation`

**Changes**:
- Update success_target and crit_target to represent PC thresholds instead of dice targets
- Add documentation explaining the new influence system

**New Structure**:
```python
@dataclass
class Legislation:
    """Represents a bill that can be sponsored."""
    id: str
    title: str
    cost: int
    # Target for net influence (support - opposition)
    success_target: int  # Minimum net influence needed for success
    crit_target: int     # Minimum net influence needed for critical success
    # Rewards are PC gain for the sponsor
    success_reward: int
    crit_reward: int
    # Penalty is PC loss for the sponsor on failure
    failure_penalty: int
    # Public mood change on success
    mood_change: int = 0
```

#### 1.3 Update Legislation Data
**File**: `game_data.py`
**Function**: `load_legislation()`

**Changes**:
- Adjust success_target and crit_target values for influence system
- Balance based on typical PC amounts players have available

**New Values**:
```python
def load_legislation():
    return {
        "INFRASTRUCTURE": Legislation(id="INFRASTRUCTURE", title="Infrastructure Bill", cost=5, success_target=8, crit_target=15, success_reward=10, crit_reward=12, failure_penalty=0, mood_change=1),
        "CHILDREN": Legislation(id="CHILDREN", title="Protect The Children!", cost=5, success_target=6, crit_target=12, success_reward=8, crit_reward=10, failure_penalty=0, mood_change=1),
        "TAX_CODE": Legislation(id="TAX_CODE", title="Change the Tax Code", cost=10, success_target=12, crit_target=20, success_reward=20, crit_reward=25, failure_penalty=5),
        "MILITARY": Legislation(id="MILITARY", title="Military Funding", cost=8, success_target=10, crit_target=18, success_reward=12, crit_reward=15, failure_penalty=0),
        "HEALTHCARE": Legislation(id="HEALTHCARE", title="Healthcare Overhaul", cost=15, success_target=18, crit_target=30, success_reward=40, crit_reward=45, failure_penalty=10, mood_change=1),
    }
```

#### 1.4 Update Frontend Display
**File**: `static/script.js`
**Function**: `updatePendingLegislationDisplay()`

**Changes**:
- Update legislation display to show influence targets instead of dice targets
- Add explanation of the new system

**New Display**:
```javascript
pendingSection.innerHTML = `
    <h3>Pending Legislation</h3>
    <div class="pending-bill">
        <strong>${bill.title}</strong> (Sponsored by ${sponsor.name})
        <div>Cost: ${bill.cost} PC | Success Target: ${bill.success_target} PC | Crit Target: ${bill.crit_target} PC</div>
        <div class="influence-explanation">Commit PC to support or oppose this legislation</div>
    </div>
`;
```

### Testing Phase 1
**File**: `test_influence_system.py`

**Test Cases**:
1. Legislation passes with sufficient support
2. Legislation fails with insufficient support
3. Critical success with high support
4. Supporters get rewards for successful legislation
5. Sponsor penalties for failed legislation

## Phase 2: Executive Term (Action Points System)

### Problem Analysis
- Current system: One action per turn
- Issue: Slow gameplay, limited strategic expression
- Impact: Players feel constrained, long periods of inactivity

### Solution: Action Points System
Players get 3 Action Points (AP) per turn and can spend them on multiple actions.

### Implementation Steps

#### 2.1 Add Action Points to Game State
**File**: `models/game_state.py`
**Class**: `GameState`

**Changes**:
- Add action_points field to track remaining AP
- Add action_point_costs to track AP costs for actions

**New Fields**:
```python
@dataclass
class GameState:
    # ... existing fields ...
    
    # Action Points System
    action_points: Dict[int, int] = field(default_factory=dict)  # player_id -> remaining AP
    action_point_costs: Dict[str, int] = field(default_factory=dict)  # action_type -> AP cost
```

#### 2.2 Define Action Point Costs
**File**: `engine/engine.py`
**Class**: `GameEngine`

**Changes**:
- Initialize action point costs in constructor
- Add AP validation to process_action

**New Logic**:
```python
def __init__(self, game_data):
    self.game_data = game_data
    # Action point costs
    self.action_point_costs = {
        "ActionFundraise": 1,
        "ActionNetwork": 1,
        "ActionSponsorLegislation": 2,
        "ActionDeclareCandidacy": 2,
        "ActionUseFavor": 0,  # Free action
        "ActionSupportLegislation": 1,
        "ActionOpposeLegislation": 1,
        "ActionProposeTrade": 0,  # Free during trading phase
        "ActionAcceptTrade": 0,   # Free during trading phase
        "ActionDeclineTrade": 0,  # Free during trading phase
        "ActionCompleteTrading": 0,  # Free during trading phase
        "ActionCampaign": 2,  # New action
    }
    # ... existing action_resolvers ...
```

#### 2.3 Add Campaign Action
**File**: `engine/actions.py`

**New Action**:
```python
@dataclass
class ActionCampaign(Action):
    """Campaign for a future office election by placing influence."""
    office_id: str
    influence_amount: int  # PC committed to future election
```

**File**: `engine/resolvers.py`

**New Resolver**:
```python
def resolve_campaign(state: GameState, action: ActionCampaign) -> GameState:
    """Resolve campaign action - place influence on future election."""
    player = state.get_player_by_id(action.player_id)
    if not player: return state
    
    if player.pc < action.influence_amount:
        state.add_log(f"{player.name} doesn't have enough PC to place that much influence.")
        return state
    
    office = state.offices.get(action.office_id)
    if not office:
        state.add_log("Invalid office for campaigning.")
        return state
    
    player.pc -= action.influence_amount
    
    # Create or update campaign influence
    campaign_influence = CampaignInfluence(
        player_id=player.id,
        office_id=action.office_id,
        influence_amount=action.influence_amount
    )
    
    # Add to state (implementation depends on data structure)
    state.campaign_influences.append(campaign_influence)
    
    state.add_log(f"{player.name} campaigns for {office.title} with {action.influence_amount} PC influence.")
    
    return state
```

#### 2.4 Modify Turn Advancement
**File**: `engine/engine.py`
**Method**: `_advance_turn()`

**Changes**:
- Reset action points at start of each player's turn
- Only advance to next player when AP are exhausted
- Handle AP spending validation

**New Logic**:
```python
def _advance_turn(self, state: GameState) -> GameState:
    """Advances to the next player's turn or next action within turn."""
    current_player = state.get_current_player()
    
    # Initialize action points if not set
    if current_player.id not in state.action_points:
        state.action_points[current_player.id] = 3
    
    # If player has action points remaining, stay on their turn
    if state.action_points[current_player.id] > 0:
        return state
    
    # Player has used all AP, advance to next player
    state.current_player_index += 1
    
    # ... existing advancement logic ...
    
    # Reset action points for new player
    if state.current_player_index < len(state.players):
        new_player = state.get_current_player()
        state.action_points[new_player.id] = 3
    
    return state
```

#### 2.5 Update Action Processing
**File**: `engine/engine.py`
**Method**: `process_action()`

**Changes**:
- Add AP cost validation
- Deduct AP when action is taken
- Prevent actions when insufficient AP

**New Logic**:
```python
def process_action(self, state: GameState, action: Action) -> GameState:
    """Routes an action to the correct resolver and advances the game state."""
    state.clear_turn_log()
    player = state.get_player_by_id(action.player_id)
    if not player or state.get_current_player().id != player.id:
        raise ValueError("It's not your turn or the player is invalid.")
    
    # Check action point cost
    action_cost = self.action_point_costs.get(action.__class__.__name__, 0)
    if state.action_points[player.id] < action_cost:
        raise ValueError(f"Not enough action points. Need {action_cost}, have {state.action_points[player.id]}.")
    
    resolver = self.action_resolvers.get(action.__class__.__name__)
    if not resolver:
        raise ValueError(f"No resolver found for action: {action.__class__.__name__}")
    
    # Deduct action points
    state.action_points[player.id] -= action_cost
    
    # The resolver function will handle the logic and return the new state
    new_state = resolver(state, action)
    
    return self._advance_turn(new_state)
```

#### 2.6 Update Frontend for AP System
**File**: `static/script.js`
**Function**: `updateActionButtons()`

**Changes**:
- Show remaining AP
- Display AP costs for each action
- Disable actions when insufficient AP
- Add campaign action option

**New Display**:
```javascript
// Show action points
const actionPointsDiv = document.createElement('div');
actionPointsDiv.className = 'action-points';
actionPointsDiv.innerHTML = `<strong>Action Points: ${currentGameState.action_points[currentPlayer.id] || 3}</strong>`;
actionList.appendChild(actionPointsDiv);

// Update action buttons with AP costs
const actions = [
    {
        type: 'fundraise',
        label: 'Fundraise',
        description: 'Gain Political Capital',
        ap_cost: 1
    },
    {
        type: 'network',
        label: 'Network',
        description: 'Gain PC and political favors',
        ap_cost: 1
    },
    {
        type: 'sponsor_legislation_menu',
        label: 'Sponsor Legislation',
        description: 'Create legislation for votes and mood',
        ap_cost: 2
    },
    {
        type: 'campaign',
        label: 'Campaign',
        description: 'Place influence on future elections',
        ap_cost: 2
    }
];

// Filter actions based on available AP
const availableAP = currentGameState.action_points[currentPlayer.id] || 3;
const availableActions = actions.filter(action => action.ap_cost <= availableAP);
```

### Testing Phase 2
**File**: `test_action_points_system.py`

**Test Cases**:
1. Players get 3 AP per turn
2. Actions cost appropriate AP
3. Players can take multiple actions per turn
4. Turn advances when AP exhausted
5. Campaign action works correctly
6. AP validation prevents invalid actions

## Phase 3: Formalized Bidding (Structured Trading)

### Problem Analysis
- Current system: Open-ended trading can be intimidating
- Issue: New players unsure how to negotiate
- Impact: Game can stall during trading phases

### Solution: Public Offer System
Add structured public bidding while maintaining private deals.

### Implementation Steps

#### 3.1 Add Public Offer System
**File**: `models/game_state.py`
**Class**: `GameState`

**Changes**:
- Add public_offers field to track formal bids
- Add offer_history for transparency

**New Fields**:
```python
@dataclass
class PublicOffer:
    """Represents a public offer made during legislation voting."""
    offerer_id: int
    legislation_id: str
    offered_pc: int
    requested_vote: str  # "support", "oppose", "abstain"
    accepted_by: Optional[int] = None  # player_id who accepted, or None
    round_number: int = 1  # Which round of bidding this is

@dataclass
class GameState:
    # ... existing fields ...
    
    # Formalized Bidding System
    public_offers: List[PublicOffer] = field(default_factory=list)
    offer_history: List[PublicOffer] = field(default_factory=list)
    current_bidding_round: int = 1
```

#### 3.2 Add Public Offer Actions
**File**: `engine/actions.py`

**New Actions**:
```python
@dataclass
class ActionMakePublicOffer(Action):
    """Make a public offer for votes on legislation."""
    legislation_id: str
    offered_pc: int
    requested_vote: str  # "support", "oppose", "abstain"

@dataclass
class ActionAcceptPublicOffer(Action):
    """Accept a public offer from another player."""
    offer_id: int  # Index in public_offers list

@dataclass
class ActionCounterOffer(Action):
    """Make a counter-offer to a public offer."""
    original_offer_id: int
    offered_pc: int
    requested_vote: str
```

#### 3.3 Implement Public Offer Resolution
**File**: `engine/resolvers.py`

**New Resolvers**:
```python
def resolve_make_public_offer(state: GameState, action: ActionMakePublicOffer) -> GameState:
    """Handle making a public offer for votes."""
    player = state.get_player_by_id(action.player_id)
    if not player: return state
    
    if not state.current_trade_phase:
        state.add_log("Public offers are only allowed during the trading phase.")
        return state
    
    if player.pc < action.offered_pc:
        state.add_log("You don't have enough PC to make this offer.")
        return state
    
    # Check if player has already made a public offer for this legislation
    existing_offer = next((offer for offer in state.public_offers 
                          if offer.offerer_id == player.id and 
                          offer.legislation_id == action.legislation_id), None)
    if existing_offer:
        state.add_log("You have already made a public offer for this legislation.")
        return state
    
    # Create the public offer
    public_offer = PublicOffer(
        offerer_id=player.id,
        legislation_id=action.legislation_id,
        offered_pc=action.offered_pc,
        requested_vote=action.requested_vote,
        round_number=state.current_bidding_round
    )
    
    state.public_offers.append(public_offer)
    
    bill = state.legislation_options[action.legislation_id]
    state.add_log(f"{player.name} makes a public offer: {action.offered_pc} PC for a {action.requested_vote} vote on {bill.title}.")
    
    return state

def resolve_accept_public_offer(state: GameState, action: ActionAcceptPublicOffer) -> GameState:
    """Handle accepting a public offer."""
    player = state.get_player_by_id(action.player_id)
    if not player: return state
    
    if action.offer_id >= len(state.public_offers):
        state.add_log("Invalid offer ID.")
        return state
    
    offer = state.public_offers[action.offer_id]
    
    if offer.accepted_by is not None:
        state.add_log("This offer has already been accepted.")
        return state
    
    if offer.offerer_id == player.id:
        state.add_log("You cannot accept your own offer.")
        return state
    
    # Execute the offer
    offerer = state.get_player_by_id(offer.offerer_id)
    if not offerer:
        state.add_log("Offerer not found.")
        return state
    
    # Transfer PC
    offerer.pc -= offer.offered_pc
    player.pc += offer.offered_pc
    
    # Apply the vote
    target_legislation = None
    for legislation in state.term_legislation:
        if legislation.legislation_id == offer.legislation_id:
            target_legislation = legislation
            break
    
    if target_legislation:
        if offer.requested_vote == "support":
            current_support = target_legislation.support_players.get(player.id, 0)
            target_legislation.support_players[player.id] = current_support + 1
        elif offer.requested_vote == "oppose":
            current_oppose = target_legislation.oppose_players.get(player.id, 0)
            target_legislation.oppose_players[player.id] = current_oppose + 1
    
    # Mark offer as accepted
    offer.accepted_by = player.id
    
    bill = state.legislation_options[offer.legislation_id]
    state.add_log(f"{player.name} accepts {offerer.name}'s public offer of {offer.offered_pc} PC for a {offer.requested_vote} vote on {bill.title}.")
    
    return state
```

#### 3.4 Update Trading UI
**File**: `static/script.js`
**Function**: `showTradingActions()`

**Changes**:
- Add public offer section
- Show existing public offers
- Allow making new public offers
- Maintain private trading interface

**New UI Structure**:
```javascript
function showTradingActions() {
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    
    // Show public offers section
    if (currentGameState.public_offers.length > 0) {
        const publicOffersDiv = document.createElement('div');
        publicOffersDiv.className = 'public-offers-section';
        publicOffersDiv.innerHTML = '<h4>Public Offers:</h4>';
        
        currentGameState.public_offers.forEach((offer, index) => {
            if (offer.accepted_by === null) {  // Only show unaccepted offers
                const offerer = currentGameState.players.find(p => p.id === offer.offerer_id);
                const bill = currentGameState.legislation_options[offer.legislation_id];
                
                const offerDiv = document.createElement('div');
                offerDiv.className = 'public-offer';
                offerDiv.innerHTML = `
                    <p><strong>${offerer.name}</strong> offers ${offer.offered_pc} PC for a <strong>${offer.requested_vote}</strong> vote on ${bill.title}</p>
                `;
                
                if (currentPlayer.id !== offer.offerer_id) {
                    const acceptBtn = document.createElement('button');
                    acceptBtn.className = 'action-btn accept-btn';
                    acceptBtn.textContent = 'Accept Public Offer';
                    acceptBtn.addEventListener('click', () => {
                        performAction('accept_public_offer', { offer_id: index });
                    });
                    offerDiv.appendChild(acceptBtn);
                }
                
                publicOffersDiv.appendChild(offerDiv);
            }
        });
        
        actionList.appendChild(publicOffersDiv);
    }
    
    // Add make public offer button
    const makeOfferBtn = document.createElement('button');
    makeOfferBtn.className = 'action-btn';
    makeOfferBtn.textContent = 'Make Public Offer';
    makeOfferBtn.addEventListener('click', () => {
        showPublicOfferMenu();
    });
    actionList.appendChild(makeOfferBtn);
    
    // ... existing private trading interface ...
}
```

#### 3.5 Add Public Offer Menu
**File**: `static/script.js`

**New Function**:
```javascript
function showPublicOfferMenu() {
    const menuDiv = document.createElement('div');
    menuDiv.id = 'public-offer-menu';
    menuDiv.className = 'public-offer-menu';
    
    menuDiv.innerHTML = `
        <h3>Make Public Offer</h3>
        <div class="offer-form">
            <label>Legislation:</label>
            <select id="offer-legislation">
                ${currentGameState.term_legislation.map(leg => {
                    const bill = currentGameState.legislation_options[leg.legislation_id];
                    return `<option value="${leg.legislation_id}">${bill.title}</option>`;
                }).join('')}
            </select>
            
            <label>PC to Offer:</label>
            <input type="number" id="offer-pc" min="1" max="${currentGameState.players[currentGameState.current_player_index].pc}" value="5">
            
            <label>Requested Vote:</label>
            <select id="offer-vote">
                <option value="support">Support</option>
                <option value="oppose">Oppose</option>
                <option value="abstain">Abstain</option>
            </select>
            
            <button class="submit-btn">Make Offer</button>
            <button class="cancel-btn">Cancel</button>
        </div>
    `;
    
    // Add event listeners
    menuDiv.querySelector('.submit-btn').addEventListener('click', () => {
        const legislationId = menuDiv.querySelector('#offer-legislation').value;
        const offeredPc = parseInt(menuDiv.querySelector('#offer-pc').value);
        const requestedVote = menuDiv.querySelector('#offer-vote').value;
        
        performAction('make_public_offer', {
            legislation_id: legislationId,
            offered_pc: offeredPc,
            requested_vote: requestedVote
        });
        
        menuDiv.remove();
    });
    
    menuDiv.querySelector('.cancel-btn').addEventListener('click', () => {
        menuDiv.remove();
    });
    
    document.body.appendChild(menuDiv);
}
```

### Testing Phase 3
**File**: `test_formalized_bidding.py`

**Test Cases**:
1. Players can make public offers
2. Public offers are visible to all players
3. Players can accept public offers
4. Public offers are properly executed
5. Private trading still works
6. Public offers don't interfere with private deals

## Integration and Testing

### Comprehensive Testing
**File**: `test_refinements_integration.py`

**Test Cases**:
1. All three systems work together
2. Influence system with action points
3. Public offers during legislation sessions
4. Campaign action with influence system
5. Performance under new systems
6. Edge cases and error handling

### Balance Testing
**File**: `test_game_balance.py`

**Test Cases**:
1. PC economy with new influence system
2. Action point costs are balanced
3. Public offers don't dominate private trading
4. Campaign action is appropriately powerful
5. Win conditions are still achievable

## Migration Strategy

### Backward Compatibility
- Existing games can continue with current systems
- New games use refined systems
- Gradual transition to avoid disruption

### Data Migration
- No database changes required (in-memory storage)
- Action history may show new action types
- Preserve existing game state structure

## Success Metrics

### Player Engagement
- Reduced downtime between turns
- Increased strategic decision-making
- More negotiation and deal-making
- Higher player satisfaction scores

### Game Balance
- Maintained win rates across player types
- Balanced resource economy
- Meaningful risk/reward decisions
- Strategic depth without complexity

### Technical Quality
- Clean, maintainable code
- Comprehensive test coverage
- Responsive, intuitive UI
- Performance maintained

## Implementation Timeline

### Week 1: Phase 1 (Influence System)
- Remove dice from legislation resolution
- Implement secret PC commitment
- Update frontend display
- Comprehensive testing

### Week 2: Phase 2 (Action Points)
- Add AP system to game state
- Implement campaign action
- Update turn structure
- Frontend AP display

### Week 3: Phase 3 (Formalized Bidding)
- Add public offer system
- Implement structured bidding
- Update trading UI
- Integration testing

### Week 4: Integration and Polish
- Comprehensive integration testing
- Balance adjustments
- UI/UX improvements
- Documentation updates

## Risk Mitigation

### Technical Risks
- **Complexity**: Implement incrementally with thorough testing
- **Performance**: Monitor response times during development
- **Bugs**: Comprehensive test suite for each phase

### Game Design Risks
- **Balance**: Extensive playtesting at each phase
- **Player Confusion**: Clear UI and documentation
- **Meta Shifts**: Monitor for unintended consequences

### Mitigation Strategies
1. **Incremental Implementation**: Each phase is independent
2. **Extensive Testing**: Comprehensive test coverage
3. **Player Feedback**: Regular playtesting sessions
4. **Rollback Plan**: Ability to revert changes if needed

## Conclusion

This implementation plan addresses all three major criticisms while maintaining the core game experience. The refinements will:

1. **Enhance Competence**: Remove random chance from legislation
2. **Increase Autonomy**: Allow multiple actions per turn
3. **Improve Flow**: Provide structured negotiation options

The plan is designed for incremental implementation with comprehensive testing at each stage, ensuring a smooth transition to the improved game systems. 