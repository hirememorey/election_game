# Frontend Implementation Guide: Action Points System

## 🎯 Overview

This guide provides step-by-step instructions for implementing the Action Points system UI in the political board game. The backend is fully implemented and tested - this guide covers the frontend implementation only.

## 📋 Prerequisites

- Basic knowledge of HTML, CSS, and JavaScript
- Understanding of the existing game UI structure
- Access to the `static/` directory files

## 🏗️ Current Frontend Structure

### Key Files
- `static/index.html`: Main game interface
- `static/script.js`: Game logic and API communication
- `static/style.css`: Mobile-responsive styling

### Current Action System
Actions are currently displayed in `updateActionButtons()` function in `script.js`. Each action is a button that calls `performAction()` with the action type.

## 🎨 Implementation Tasks

### Task 1: Action Points Display

**Goal**: Show remaining Action Points for the current player

**Location**: `static/script.js` - `updateActionButtons()` function

**Implementation**:
```javascript
function updateActionButtons() {
    const actionList = document.getElementById('action-list');
    actionList.innerHTML = '';
    
    // Get current player and their AP
    const currentPlayer = gameState.players[gameState.current_player_index];
    const remainingAP = gameState.action_points[currentPlayer.id] || 3;
    
    // Add AP display
    const apDisplay = document.createElement('div');
    apDisplay.className = 'action-points-display';
    apDisplay.innerHTML = `
        <div class="turn-info">
            <strong>${currentPlayer.name}'s Turn</strong><br>
            <span class="ap-counter">Action Points: ${remainingAP}/3</span>
        </div>
    `;
    actionList.appendChild(apDisplay);
    
    // Continue with existing action buttons...
}
```

**CSS Addition** (`static/style.css`):
```css
.action-points-display {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px;
    margin: 15px 0;
    border-radius: 10px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.turn-info {
    font-size: 1.1em;
}

.ap-counter {
    font-size: 1.2em;
    font-weight: bold;
    color: #ffd700;
}
```

### Task 2: Action Point Costs

**Goal**: Display AP costs for each action and disable when insufficient

**Implementation**:
```javascript
// Define action costs
const actionCosts = {
    'fundraise': 1,
    'network': 1,
    'sponsor_legislation': 2,
    'declare_candidacy': 2,
    'use_favor': 0,
    'support_legislation': 1,
    'oppose_legislation': 1,
    'campaign': 2,
    'propose_trade': 0,
    'accept_trade': 0,
    'decline_trade': 0,
    'complete_trading': 0
};

// Update action button creation
function createActionButton(actionType, label, description) {
    const button = document.createElement('button');
    const apCost = actionCosts[actionType] || 0;
    const canAfford = remainingAP >= apCost;
    
    button.className = 'action-button';
    button.disabled = !canAfford;
    button.innerHTML = `
        <div class="action-label">${label}</div>
        <div class="action-cost">${apCost} AP</div>
        <div class="action-description">${description}</div>
    `;
    
    if (!canAfford) {
        button.title = `Not enough Action Points. Need ${apCost}, have ${remainingAP}`;
    }
    
    button.onclick = () => performAction(actionType);
    return button;
}
```

**CSS Addition**:
```css
.action-button {
    position: relative;
    padding: 15px;
    margin: 10px 5px;
    border: 2px solid #ddd;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    transition: all 0.3s ease;
    min-width: 120px;
}

.action-button:hover:not(:disabled) {
    border-color: #667eea;
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.action-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    background: #f5f5f5;
}

.action-cost {
    font-size: 0.8em;
    color: #667eea;
    font-weight: bold;
    margin-top: 5px;
}

.action-description {
    font-size: 0.7em;
    color: #666;
    margin-top: 3px;
}
```

### Task 3: Campaign Action UI

**Goal**: Add the new Campaign action with office selection and PC input

**Implementation**:
```javascript
// Add to action buttons array
const actions = [
    // ... existing actions
    {
        type: 'campaign',
        label: 'Campaign',
        description: 'Place influence for future election',
        handler: showCampaignDialog
    }
];

// Campaign dialog function
function showCampaignDialog() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="campaign-modal">
            <h3>Campaign for Office</h3>
            <p>Place influence for a future election by committing PC.</p>
            
            <div class="form-group">
                <label for="campaign-office">Select Office:</label>
                <select id="campaign-office" required>
                    <option value="">Choose an office...</option>
                    <option value="STATE_SENATOR">State Senator</option>
                    <option value="CONGRESS_SEAT">Congress Seat</option>
                    <option value="GOVERNOR">Governor</option>
                    <option value="US_SENATOR">US Senator</option>
                    <option value="PRESIDENT">President</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="campaign-pc">PC to Commit:</label>
                <input type="number" id="campaign-pc" min="1" max="50" required 
                       placeholder="Enter PC amount">
            </div>
            
            <div class="modal-buttons">
                <button onclick="handleCampaignAction()" class="btn-primary">Campaign</button>
                <button onclick="closeModal()" class="btn-secondary">Cancel</button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

// Campaign action handler
function handleCampaignAction() {
    const officeSelect = document.getElementById('campaign-office');
    const pcInput = document.getElementById('campaign-pc');
    
    const officeId = officeSelect.value;
    const influenceAmount = parseInt(pcInput.value);
    
    // Validation
    if (!officeId) {
        alert('Please select an office');
        return;
    }
    
    if (!influenceAmount || influenceAmount <= 0) {
        alert('Please enter a valid PC amount');
        return;
    }
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    if (influenceAmount > currentPlayer.pc) {
        alert(`You only have ${currentPlayer.pc} PC available`);
        return;
    }
    
    // Call API
    performAction('campaign', {
        office_id: officeId,
        influence_amount: influenceAmount
    });
    
    closeModal();
}

// Modal utilities
function closeModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) {
        modal.remove();
    }
}
```

**CSS Addition**:
```css
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.campaign-modal {
    background: white;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    max-width: 400px;
    width: 90%;
}

.form-group {
    margin: 20px 0;
}

.form-group label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
    color: #333;
}

.form-group select,
.form-group input {
    width: 100%;
    padding: 10px;
    border: 2px solid #ddd;
    border-radius: 5px;
    font-size: 16px;
}

.form-group select:focus,
.form-group input:focus {
    border-color: #667eea;
    outline: none;
}

.modal-buttons {
    display: flex;
    gap: 10px;
    justify-content: flex-end;
    margin-top: 20px;
}

.btn-primary {
    background: #667eea;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
}

.btn-secondary {
    background: #6c757d;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
}
```

### Task 4: Turn Status Enhancement

**Goal**: Improve turn status display with AP information

**Implementation**:
```javascript
// Update the existing turn status display
function updateTurnStatus() {
    const turnStatus = document.getElementById('turn-status');
    if (!turnStatus) return;
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    const remainingAP = gameState.action_points[currentPlayer.id] || 3;
    
    turnStatus.innerHTML = `
        <div class="enhanced-turn-status">
            <div class="player-turn">
                <strong>${currentPlayer.name}'s Turn</strong>
            </div>
            <div class="ap-status">
                <span class="ap-icon">⚡</span>
                <span class="ap-text">${remainingAP}/3 Action Points</span>
            </div>
            <div class="phase-info">
                Phase: ${gameState.current_phase.replace('_', ' ')}
            </div>
        </div>
    `;
}
```

**CSS Addition**:
```css
.enhanced-turn-status {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    margin: 15px 0;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
}

.player-turn {
    font-size: 1.3em;
    font-weight: bold;
    margin-bottom: 10px;
}

.ap-status {
    font-size: 1.1em;
    margin-bottom: 8px;
}

.ap-icon {
    margin-right: 8px;
    font-size: 1.2em;
}

.phase-info {
    font-size: 0.9em;
    opacity: 0.9;
}
```

## 🧪 Testing Checklist

### Manual Testing
1. **AP Display**: Verify AP counter shows correctly for current player
2. **AP Costs**: Verify each action shows correct AP cost
3. **AP Validation**: Verify actions are disabled when insufficient AP
4. **Campaign Action**: 
   - Verify office selection dropdown works
   - Verify PC input validation works
   - Verify API call is made correctly
5. **Turn Advancement**: Verify turn status updates when AP are exhausted
6. **Mobile Responsiveness**: Test on mobile devices

### API Testing
```javascript
// Test campaign action
fetch('/api/game/' + gameId + '/action', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        action_type: 'campaign',
        player_id: 0,
        office_id: 'GOVERNOR',
        influence_amount: 5
    })
});
```

## 🐛 Common Issues & Solutions

### Issue 1: AP not updating after actions
**Solution**: Ensure `updateActionButtons()` is called after each action in `performAction()`

### Issue 2: Campaign modal not closing
**Solution**: Add `closeModal()` call after successful API response

### Issue 3: Mobile layout issues
**Solution**: Test CSS media queries and ensure buttons are touch-friendly

### Issue 4: AP validation not working
**Solution**: Check that `actionCosts` object includes all action types

## 📱 Mobile Considerations

- Ensure buttons are at least 44px tall for touch targets
- Use larger fonts on mobile devices
- Test modal dialogs on small screens
- Ensure form inputs are properly sized for mobile keyboards

## ✅ Success Criteria

- [ ] Action Points display shows current player and remaining AP
- [ ] All action buttons show correct AP costs
- [ ] Actions are disabled when insufficient AP
- [ ] Campaign action works with office selection and PC input
- [ ] Turn status updates correctly
- [ ] UI is mobile responsive
- [ ] No console errors during gameplay
- [ ] All existing functionality still works

## 🚀 Next Steps After Implementation

1. **Test thoroughly** with multiple players
2. **Gather feedback** on UI/UX
3. **Optimize performance** if needed
4. **Add animations** for better user experience
5. **Consider accessibility** improvements

---

**Good luck with the implementation! The backend is solid and tested, so focus on creating a smooth, intuitive user experience.** 