// Game state management
let currentGameId = null;
let currentGameState = null;
const API_BASE_URL = 'http://localhost:5001/api'; // Change this for production

// DOM elements
const setupScreen = document.getElementById('setup-screen');
const gameScreen = document.getElementById('game-screen');
const startGameBtn = document.getElementById('start-game-btn');
const newGameBtn = document.getElementById('new-game-btn');
const runEventBtn = document.getElementById('run-event-btn');

// Game state elements
const roundInfo = document.getElementById('round-info');
const phaseInfo = document.getElementById('phase-info');
const moodInfo = document.getElementById('mood-info');
const logContent = document.getElementById('log-content');
const currentPlayerName = document.getElementById('current-player-name');
const currentPlayerPc = document.getElementById('current-player-pc');
const currentPlayerOffice = document.getElementById('current-player-office');
const actionList = document.getElementById('action-list');
const eventPhaseSection = document.getElementById('event-phase-section');

// Player identity elements
const currentPlayerArchetypeTitle = document.getElementById('current-player-archetype-title');
const currentPlayerArchetypeDesc = document.getElementById('current-player-archetype-desc');
const currentPlayerMandateTitle = document.getElementById('current-player-mandate-title');
const currentPlayerMandateDesc = document.getElementById('current-player-mandate-desc');

// Event listeners
startGameBtn.addEventListener('click', startNewGame);
newGameBtn.addEventListener('click', showSetupScreen);
runEventBtn.addEventListener('click', runEventPhase);

// API functions
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.error || 'API call failed');
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        showMessage(error.message, 'error');
        throw error;
    }
}

// Game functions
async function startNewGame() {
    const playerNames = [];
    for (let i = 1; i <= 4; i++) {
        const input = document.getElementById(`player${i}`);
        if (input.value.trim()) {
            playerNames.push(input.value.trim());
        }
    }
    
    if (playerNames.length < 2) {
        showMessage('Please enter at least 2 player names', 'error');
        return;
    }
    
    try {
        startGameBtn.disabled = true;
        startGameBtn.textContent = 'Creating Game...';
        
        const result = await apiCall('/game', 'POST', { player_names: playerNames });
        currentGameId = result.game_id;
        currentGameState = result.state;
        
        showGameScreen();
        updateGameDisplay();
    } catch (error) {
        console.error('Failed to start game:', error);
    } finally {
        startGameBtn.disabled = false;
        startGameBtn.textContent = 'Start Game';
    }
}

async function getGameState() {
    if (!currentGameId) return;
    
    try {
        const result = await apiCall(`/game/${currentGameId}`);
        currentGameState = result.state;
        updateGameDisplay();
    } catch (error) {
        console.error('Failed to get game state:', error);
    }
}

async function performAction(actionType, additionalData = {}) {
    if (!currentGameId) return;
    
    try {
        const data = {
            action_type: actionType,
            player_id: currentGameState.current_player_index,
            ...additionalData
        };
        
        const result = await apiCall(`/game/${currentGameId}/action`, 'POST', data);
        currentGameState = result.state;
        updateGameDisplay();
    } catch (error) {
        console.error('Failed to perform action:', error);
    }
}

async function runEventPhase() {
    if (!currentGameId) return;
    
    try {
        runEventBtn.disabled = true;
        runEventBtn.textContent = 'Drawing Event...';
        
        const result = await apiCall(`/game/${currentGameId}/event`, 'POST');
        currentGameState = result.state;
        updateGameDisplay();
    } catch (error) {
        console.error('Failed to run event phase:', error);
    } finally {
        runEventBtn.disabled = false;
        runEventBtn.textContent = 'Draw Event Card';
    }
}

// UI functions
function showSetupScreen() {
    setupScreen.classList.remove('hidden');
    gameScreen.classList.add('hidden');
    currentGameId = null;
    currentGameState = null;
    
    // Clear form
    for (let i = 1; i <= 4; i++) {
        document.getElementById(`player${i}`).value = '';
    }
}

function showGameScreen() {
    setupScreen.classList.add('hidden');
    gameScreen.classList.remove('hidden');
}

function updateGameDisplay() {
    if (!currentGameState) return;
    
    // Update game info
    roundInfo.textContent = `Round ${currentGameState.round_marker}`;
    phaseInfo.textContent = formatPhase(currentGameState.current_phase);
    moodInfo.textContent = `Public Mood: ${formatMood(currentGameState.public_mood)}`;
    
    // Update turn log
    updateTurnLog();
    
    // Update current player info
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    currentPlayerName.textContent = currentPlayer.name;
    currentPlayerPc.textContent = currentPlayer.pc;
    currentPlayerOffice.textContent = currentPlayer.current_office ? currentPlayer.current_office.title : 'None';
    
    // Update player archetype and mandate
    if (currentPlayer.archetype) {
        currentPlayerArchetypeTitle.textContent = currentPlayer.archetype.title;
        currentPlayerArchetypeDesc.textContent = currentPlayer.archetype.description;
    } else {
        currentPlayerArchetypeTitle.textContent = 'Unknown';
        currentPlayerArchetypeDesc.textContent = 'Archetype not found';
    }
    
    if (currentPlayer.mandate) {
        currentPlayerMandateTitle.textContent = currentPlayer.mandate.title;
        currentPlayerMandateDesc.textContent = currentPlayer.mandate.description;
    } else {
        currentPlayerMandateTitle.textContent = 'Unknown';
        currentPlayerMandateDesc.textContent = 'Mandate not found';
    }
    
    // Show pending legislation info
    updatePendingLegislationDisplay();
    
    // Show player favors
    updatePlayerFavorsDisplay();
    
    // Update action buttons
    updateActionButtons();
    
    // Show/hide event phase button
    if (currentGameState.current_phase === 'EVENT_PHASE') {
        eventPhaseSection.classList.remove('hidden');
    } else {
        eventPhaseSection.classList.add('hidden');
    }
}

function updatePendingLegislationDisplay() {
    const pendingSection = document.getElementById('pending-legislation-section');
    if (!pendingSection) return;
    
    // Show term legislation during legislation session
    if (currentGameState.current_phase === 'LEGISLATION_PHASE' && currentGameState.term_legislation && currentGameState.term_legislation.length > 0) {
        const legislationList = currentGameState.term_legislation.map(legislation => {
            const bill = currentGameState.legislation_options[legislation.legislation_id];
            const sponsor = currentGameState.players.find(p => p.id === legislation.sponsor_id);
            const supportTotal = Object.values(legislation.support_players).reduce((sum, val) => sum + val, 0);
            const opposeTotal = Object.values(legislation.oppose_players).reduce((sum, val) => sum + val, 0);
            
            return `
                <div class="pending-bill">
                    <strong>${bill.title}</strong> (Sponsored by ${sponsor.name})
                    <div>Support: ${supportTotal} PC | Opposition: ${opposeTotal} PC</div>
                </div>
            `;
        }).join('');
        
        pendingSection.innerHTML = `
            <h3>Term Legislation</h3>
            ${legislationList}
        `;
        pendingSection.classList.remove('hidden');
        return;
    }
    
    // Show current pending legislation during action phase
    if (currentGameState.pending_legislation && !currentGameState.pending_legislation.resolved) {
        const pending = currentGameState.pending_legislation;
        const bill = currentGameState.legislation_options[pending.legislation_id];
        const sponsor = currentGameState.players.find(p => p.id === pending.sponsor_id);
        
        pendingSection.innerHTML = `
            <h3>Pending Legislation</h3>
            <div class="pending-bill">
                <strong>${bill.title}</strong> (Sponsored by ${sponsor.name})
                <div>Cost: ${bill.cost} PC | Success Target: ${bill.success_target} PC | Crit Target: ${bill.crit_target} PC</div>
                <div class="influence-explanation">Commit PC to support or oppose this legislation</div>
            </div>
        `;
        pendingSection.classList.remove('hidden');
    } else {
        pendingSection.classList.add('hidden');
    }
}

function updatePlayerFavorsDisplay() {
    const favorsSection = document.getElementById('player-favors-section');
    if (!favorsSection) return;
    
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    
    if (currentPlayer.favors && currentPlayer.favors.length > 0) {
        const favorsList = currentPlayer.favors.map(favor => 
            `<div class="favor-item">${favor.description}</div>`
        ).join('');
        
        favorsSection.innerHTML = `
            <h3>Your Political Favors</h3>
            <div class="favors-list">${favorsList}</div>
        `;
        favorsSection.classList.remove('hidden');
    } else {
        favorsSection.classList.add('hidden');
    }
}

function updateTurnLog() {
    logContent.innerHTML = '';
    currentGameState.turn_log.forEach(logEntry => {
        const p = document.createElement('p');
        p.textContent = logEntry;
        logContent.appendChild(p);
    });
    
    // Scroll to bottom
    logContent.scrollTop = logContent.scrollHeight;
}

function updateActionButtons() {
    actionList.innerHTML = '';
    
    if (!currentGameState) return;
    
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    
    // Handle legislation session
    if (currentGameState.legislation_session_active) {
        if (currentGameState.current_trade_phase) {
            showTradingActions();
        } else {
            showLegislationSessionActions();
        }
        return;
    }
    
    // Handle event phase
    if (currentGameState.current_phase === 'EVENT_PHASE') {
        const button = document.createElement('button');
        button.className = 'action-btn';
        button.textContent = 'Draw Event Card';
        button.addEventListener('click', runEventPhase);
        actionList.appendChild(button);
        return;
    }
    
    // Handle action phase
    if (currentGameState.current_phase === 'ACTION_PHASE') {
        // Get current player's remaining Action Points
        const remainingAP = currentGameState.action_points[currentPlayer.id] || 0;
        
        // Add Action Points display
        const apDisplay = document.createElement('div');
        apDisplay.className = 'action-points-display';
        apDisplay.innerHTML = `
            <div class="turn-info">
                <strong>${currentPlayer.name}'s Turn</strong><br>
                <span class="ap-counter">Action Points: ${remainingAP}/3</span>
            </div>
        `;
        actionList.appendChild(apDisplay);
        
        // Define action costs
        const actionCosts = {
            'fundraise': 1,
            'network': 1,
            'sponsor_legislation': 2,
            'sponsor_legislation_menu': 2,
            'declare_candidacy': 2,
            'use_favor': 0,
            'use_favor_menu': 0,
            'support_legislation': 1,
            'oppose_legislation': 1,
            'campaign': 2,
            'propose_trade': 0,
            'accept_trade': 0,
            'decline_trade': 0,
            'complete_trading': 0,
            'pass_turn': 0
        };
        
        const actions = [
            {
                type: 'fundraise',
                label: 'Fundraise',
                description: 'Gain Political Capital'
            },
            {
                type: 'network',
                label: 'Network',
                description: 'Gain PC and political favors'
            },
            {
                type: 'sponsor_legislation_menu',
                label: 'Sponsor Legislation',
                description: 'Create legislation for votes and mood'
            },
            {
                type: 'campaign',
                label: 'Campaign',
                description: 'Place influence for future election'
            }
        ];
        
        // Only show 'Use Favor' if the player has at least one favor
        if (currentPlayer.favors && currentPlayer.favors.length > 0) {
            actions.push({
                type: 'use_favor_menu',
                label: 'Use Favor',
                description: 'Use a political favor for advantage'
            });
        }
        
        // Add candidacy option in round 4
        if (currentGameState.round_marker === 4) {
            Object.values(currentGameState.offices).forEach(office => {
                if (currentPlayer.pc >= office.candidacy_cost) {
                    actions.push({
                        type: 'declare_candidacy',
                        label: `Run for ${office.title}`,
                        description: `Cost: ${office.candidacy_cost} PC`,
                        data: { office_id: office.id, committed_pc: office.candidacy_cost }
                    });
                }
            });
        }
        
        // Add Pass Turn button if player has no AP left
        if (remainingAP === 0) {
            actions.push({
                type: 'pass_turn',
                label: 'Pass Turn',
                description: 'End your turn and advance to next player'
            });
        }
        
        actions.forEach(action => {
            const button = document.createElement('button');
            button.className = 'action-btn';
            
            // Get AP cost for this action
            const apCost = actionCosts[action.type] || 0;
            const canAfford = remainingAP >= apCost;
            
            // Disable button if not enough AP
            button.disabled = !canAfford;
            
            button.innerHTML = `
                <div class="action-label"><strong>${action.label}</strong></div>
                <div class="action-cost">${apCost} AP</div>
                <div class="action-description">${action.description}</div>
            `;
            
            if (!canAfford) {
                button.title = `Not enough Action Points. Need ${apCost}, have ${remainingAP}`;
            }
            
            button.addEventListener('click', () => {
                if (action.type === 'sponsor_legislation_menu') {
                    showLegislationMenu();
                } else if (action.type === 'use_favor_menu') {
                    showFavorMenu();
                } else if (action.type === 'campaign') {
                    showCampaignDialog();
                } else if (action.type === 'declare_candidacy') {
                    const office = currentGameState.offices[action.data.office_id];
                    const minPC = office.candidacy_cost;
                    const maxPC = currentPlayer.pc;
                    let committed = parseInt(prompt(`How much PC do you want to commit (in addition to the ${minPC} PC candidacy cost)? You have ${maxPC} PC.`, '0'));
                    if (isNaN(committed) || committed < 0 || committed + minPC > maxPC) {
                        showMessage('Invalid amount.', 'error');
                        return;
                    }
                    performAction('declare_candidacy', { office_id: office.id, committed_pc: committed });
                } else if (action.type === 'pass_turn') {
                    performAction('pass_turn', {});
                } else {
                    performAction(action.type, action.data || {});
                }
            });
            
            actionList.appendChild(button);
        });
    }
}

function formatPhase(phase) {
    const phaseMap = {
        'EVENT_PHASE': 'Event Phase',
        'ACTION_PHASE': 'Action Phase',
        'UPKEEP_PHASE': 'Upkeep Phase',
        'LEGISLATION_PHASE': 'Legislation Session',
        'ELECTION_PHASE': 'Election Phase'
    };
    return phaseMap[phase] || phase;
}

function formatMood(mood) {
    const moodMap = {
        "-3": 'Very Angry',
        "-2": 'Angry',
        "-1": 'Displeased',
        0: 'Neutral',
        1: 'Pleased',
        2: 'Happy',
        3: 'Ecstatic'
    };
    return moodMap[mood] || 'Neutral';
}

function showLegislationMenu() {
    // Remove existing legislation menu
    const existingMenu = document.getElementById('legislation-menu');
    if (existingMenu) {
        existingMenu.remove();
    }
    
    // Create legislation menu
    const menuDiv = document.createElement('div');
    menuDiv.id = 'legislation-menu';
    menuDiv.className = 'legislation-menu';
    
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    
    menuDiv.innerHTML = `
        <h3>Choose Legislation to Sponsor</h3>
        <div class="legislation-options">
            ${Object.values(currentGameState.legislation_options).map(leg => `
                <button class="legislation-option" data-legislation-id="${leg.id}">
                    <div><strong>${leg.title}</strong></div>
                    <div>Cost: ${leg.cost} PC | Success: ${leg.success_target} PC | Crit: ${leg.crit_target} PC</div>
                    ${leg.mood_change ? `<div>Mood Change: ${leg.mood_change > 0 ? '+' : ''}${leg.mood_change}</div>` : ''}
                </button>
            `).join('')}
        </div>
        <button class="cancel-btn">Cancel</button>
    `;
    
    // Add event listeners
    menuDiv.querySelectorAll('.legislation-option').forEach(button => {
        button.addEventListener('click', () => {
            const legislationId = button.dataset.legislationId;
            performAction('sponsor_legislation', { legislation_id: legislationId });
            menuDiv.remove();
        });
    });
    
    menuDiv.querySelector('.cancel-btn').addEventListener('click', () => {
        menuDiv.remove();
    });
    
    // Insert after action buttons
    const actionButtons = document.querySelector('.action-buttons');
    actionButtons.appendChild(menuDiv);
}

function showFavorMenu() {
    // Remove existing favor menu
    const existingMenu = document.getElementById('favor-menu');
    if (existingMenu) {
        existingMenu.remove();
    }
    
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    
    // Create favor menu
    const menuDiv = document.createElement('div');
    menuDiv.id = 'favor-menu';
    menuDiv.className = 'favor-menu';
    
    menuDiv.innerHTML = `
        <h3>Choose a Favor to Use</h3>
        <div class="favor-options">
            ${currentPlayer.favors.map(favor => `
                <button class="favor-option" data-favor-id="${favor.id}">
                    <div><strong>${favor.description}</strong></div>
                </button>
            `).join('')}
        </div>
        <button class="cancel-btn">Cancel</button>
    `;
    
    // Add event listeners
    menuDiv.querySelectorAll('.favor-option').forEach(button => {
        button.addEventListener('click', () => {
            const favorId = button.dataset.favorId;
            performAction('use_favor', { favor_id: favorId });
            menuDiv.remove();
        });
    });
    
    menuDiv.querySelector('.cancel-btn').addEventListener('click', () => {
        menuDiv.remove();
    });
    
    // Insert after action buttons
    const actionButtons = document.querySelector('.action-buttons');
    actionButtons.appendChild(menuDiv);
}

function showLegislationSessionActions() {
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    
    if (!currentGameState.term_legislation || currentGameState.term_legislation.length === 0) {
        const button = document.createElement('button');
        button.className = 'action-btn';
        button.textContent = 'No legislation to vote on - Continue to Elections';
        button.addEventListener('click', () => {
            // This will be handled by the backend automatically
            showMessage('Moving to elections...', 'info');
        });
        actionList.appendChild(button);
        return;
    }
    
    // Show each piece of legislation for voting
    currentGameState.term_legislation.forEach((legislation, index) => {
        if (legislation.resolved) return; // Skip already resolved legislation
        
        const bill = currentGameState.legislation_options[legislation.legislation_id];
        const sponsor = currentGameState.players.find(p => p.id === legislation.sponsor_id);
        
        const legislationDiv = document.createElement('div');
        legislationDiv.className = 'legislation-session-item';
        legislationDiv.innerHTML = `
            <h4>${bill.title}</h4>
            <p>Sponsored by: ${sponsor.name}</p>
            <p>Cost: ${bill.cost} PC | Success: ${bill.success_target} PC | Crit: ${bill.crit_target} PC</p>
            ${bill.mood_change ? `<p>Mood Change: ${bill.mood_change > 0 ? '+' : ''}${bill.mood_change}</p>` : ''}
        `;
        
        // Only show voting options if player is not the sponsor
        if (currentPlayer.id !== legislation.sponsor_id) {
            const supportBtn = document.createElement('button');
            supportBtn.className = 'action-btn';
            supportBtn.textContent = `Support`;
            supportBtn.addEventListener('click', () => {
                const maxPC = currentPlayer.pc;
                let amount = parseInt(prompt(`How much PC do you want to commit to support? (You have ${maxPC} PC)`, '1'));
                if (isNaN(amount) || amount < 1 || amount > maxPC) {
                    showMessage('Invalid amount.', 'error');
                    return;
                }
                performAction('support_legislation', { 
                    legislation_id: legislation.legislation_id, 
                    support_amount: amount
                });
            });
            legislationDiv.appendChild(supportBtn);
            
            const opposeBtn = document.createElement('button');
            opposeBtn.className = 'action-btn';
            opposeBtn.textContent = `Oppose`;
            opposeBtn.addEventListener('click', () => {
                const maxPC = currentPlayer.pc;
                let amount = parseInt(prompt(`How much PC do you want to commit to oppose? (You have ${maxPC} PC)`, '1'));
                if (isNaN(amount) || amount < 1 || amount > maxPC) {
                    showMessage('Invalid amount.', 'error');
                    return;
                }
                performAction('oppose_legislation', { 
                    legislation_id: legislation.legislation_id, 
                    oppose_amount: amount
                });
            });
            legislationDiv.appendChild(opposeBtn);
        } else {
            const sponsorLabel = document.createElement('p');
            sponsorLabel.textContent = 'You sponsored this legislation';
            sponsorLabel.className = 'sponsor-label';
            legislationDiv.appendChild(sponsorLabel);
        }
        
        actionList.appendChild(legislationDiv);
    });
    
    // Add a continue button
    const continueBtn = document.createElement('button');
    continueBtn.className = 'action-btn continue-btn';
    continueBtn.textContent = 'Continue to Elections';
    continueBtn.addEventListener('click', () => {
        // This will be handled by the backend automatically
        showMessage('Moving to elections...', 'info');
    });
    actionList.appendChild(continueBtn);
}

function showTradingActions() {
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    
    // Show current trade offers for this player
    const myOffers = currentGameState.active_trade_offers.filter(offer => offer.target_id === currentPlayer.id && !offer.accepted && !offer.declined);
    
    if (myOffers.length > 0) {
        const offersDiv = document.createElement('div');
        offersDiv.className = 'trade-offers-section';
        offersDiv.innerHTML = '<h4>Trade Offers for You:</h4>';
        
        myOffers.forEach((offer, index) => {
            const offerer = currentGameState.players.find(p => p.id === offer.offerer_id);
            const bill = currentGameState.legislation_options[offer.legislation_id];
            
            const offerDiv = document.createElement('div');
            offerDiv.className = 'trade-offer';
            offerDiv.innerHTML = `
                <p><strong>${offerer.name}</strong> offers you:</p>
                <p>${offer.offered_pc > 0 ? offer.offered_pc + ' PC' : ''}${offer.offered_pc > 0 && offer.offered_favors.length > 0 ? ' + ' : ''}${offer.offered_favors.length > 0 ? offer.offered_favors.length + ' favor(s)' : ''}</p>
                <p>To <strong>${offer.requested_vote}</strong> ${bill.title}</p>
            `;
            
            const acceptBtn = document.createElement('button');
            acceptBtn.className = 'action-btn accept-btn';
            acceptBtn.textContent = 'Accept';
            acceptBtn.addEventListener('click', () => {
                performAction('accept_trade', { trade_offer_id: currentGameState.active_trade_offers.indexOf(offer) });
            });
            
            const declineBtn = document.createElement('button');
            declineBtn.className = 'action-btn decline-btn';
            declineBtn.textContent = 'Decline';
            declineBtn.addEventListener('click', () => {
                performAction('decline_trade', { trade_offer_id: currentGameState.active_trade_offers.indexOf(offer) });
            });
            
            offerDiv.appendChild(acceptBtn);
            offerDiv.appendChild(declineBtn);
            offersDiv.appendChild(offerDiv);
        });
        
        actionList.appendChild(offersDiv);
    }
    
    // Show legislation available for trading
    if (!currentGameState.term_legislation || currentGameState.term_legislation.length === 0) {
        const button = document.createElement('button');
        button.className = 'action-btn';
        button.textContent = 'No legislation to trade on - Complete Trading';
        button.addEventListener('click', () => {
            performAction('complete_trading', {});
        });
        actionList.appendChild(button);
        return;
    }
    
    // Show each piece of legislation for trading
    currentGameState.term_legislation.forEach((legislation, index) => {
        if (legislation.resolved) return; // Skip already resolved legislation
        
        const bill = currentGameState.legislation_options[legislation.legislation_id];
        const sponsor = currentGameState.players.find(p => p.id === legislation.sponsor_id);
        
        const legislationDiv = document.createElement('div');
        legislationDiv.className = 'legislation-trading-item';
        legislationDiv.innerHTML = `
            <h4>${bill.title}</h4>
            <p>Sponsored by: ${sponsor.name}</p>
            <p>Cost: ${bill.cost} PC | Success: ${bill.success_target} PC | Crit: ${bill.crit_target} PC</p>
            ${bill.mood_change ? `<p>Mood Change: ${bill.mood_change > 0 ? '+' : ''}${bill.mood_change}</p>` : ''}
        `;
        
        // Show trading options for other players (not the sponsor)
        if (currentPlayer.id !== legislation.sponsor_id) {
            const tradeBtn = document.createElement('button');
            tradeBtn.className = 'action-btn';
            tradeBtn.textContent = `Propose Trade for ${bill.title}`;
            tradeBtn.addEventListener('click', () => {
                showTradeProposalMenu(legislation.legislation_id);
            });
            legislationDiv.appendChild(tradeBtn);
        } else {
            const sponsorLabel = document.createElement('p');
            sponsorLabel.textContent = 'You sponsored this legislation';
            sponsorLabel.className = 'sponsor-label';
            legislationDiv.appendChild(sponsorLabel);
        }
        
        actionList.appendChild(legislationDiv);
    });
    
    // Add a complete trading button
    const completeBtn = document.createElement('button');
    completeBtn.className = 'action-btn continue-btn';
    completeBtn.textContent = 'Complete Trading Turn';
    completeBtn.addEventListener('click', () => {
        performAction('complete_trading', {});
    });
    actionList.appendChild(completeBtn);
}

function showTradeProposalMenu(legislationId) {
    // Remove existing trade menu
    const existingMenu = document.getElementById('trade-proposal-menu');
    if (existingMenu) {
        existingMenu.remove();
    }
    
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    const bill = currentGameState.legislation_options[legislationId];
    
    // Create trade proposal menu
    const menuDiv = document.createElement('div');
    menuDiv.id = 'trade-proposal-menu';
    menuDiv.className = 'trade-proposal-menu';
    
    menuDiv.innerHTML = `
        <h3>Propose Trade for ${bill.title}</h3>
        <div class="trade-form">
            <div class="form-group">
                <label>Target Player:</label>
                <select id="trade-target-player">
                    ${currentGameState.players
                        .filter(p => p.id !== currentPlayer.id)
                        .map(p => `<option value="${p.id}">${p.name}</option>`)
                        .join('')}
                </select>
            </div>
            <div class="form-group">
                <label>Offer PC:</label>
                <input type="number" id="trade-offered-pc" min="0" max="${currentPlayer.pc}" value="0">
            </div>
            <div class="form-group">
                <label>Offer Favors:</label>
                <div class="favor-checkboxes">
                    ${currentPlayer.favors.map(favor => `
                        <label>
                            <input type="checkbox" value="${favor.id}"> ${favor.description}
                        </label>
                    `).join('')}
                </div>
            </div>
            <div class="form-group">
                <label>Requested Vote:</label>
                <select id="trade-requested-vote">
                    <option value="support">Support</option>
                    <option value="oppose">Oppose</option>
                    <option value="abstain">Abstain</option>
                </select>
            </div>
        </div>
        <div class="trade-actions">
            <button class="propose-trade-btn">Propose Trade</button>
            <button class="cancel-trade-btn">Cancel</button>
        </div>
    `;
    
    // Add event listeners
    menuDiv.querySelector('.propose-trade-btn').addEventListener('click', () => {
        const targetPlayerId = parseInt(menuDiv.querySelector('#trade-target-player').value);
        const offeredPc = parseInt(menuDiv.querySelector('#trade-offered-pc').value) || 0;
        const offeredFavorIds = Array.from(menuDiv.querySelectorAll('.favor-checkboxes input:checked')).map(cb => cb.value);
        const requestedVote = menuDiv.querySelector('#trade-requested-vote').value;
        
        performAction('propose_trade', {
            target_player_id: targetPlayerId,
            legislation_id: legislationId,
            offered_pc: offeredPc,
            offered_favor_ids: offeredFavorIds,
            requested_vote: requestedVote
        });
        
        menuDiv.remove();
    });
    
    menuDiv.querySelector('.cancel-trade-btn').addEventListener('click', () => {
        menuDiv.remove();
    });
    
    // Insert after action buttons
    const actionButtons = document.querySelector('.action-buttons');
    actionButtons.appendChild(menuDiv);
}

function showCampaignDialog() {
    // Remove existing campaign menu
    const existingMenu = document.getElementById('campaign-menu');
    if (existingMenu) {
        existingMenu.remove();
    }
    
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    
    // Create campaign menu
    const menuDiv = document.createElement('div');
    menuDiv.id = 'campaign-menu';
    menuDiv.className = 'campaign-modal';
    
    menuDiv.innerHTML = `
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
            <input type="number" id="campaign-pc" min="1" max="${currentPlayer.pc}" required 
                   placeholder="Enter PC amount">
        </div>
        
        <div class="modal-buttons">
            <button onclick="handleCampaignAction()" class="btn-primary">Campaign</button>
            <button onclick="closeModal()" class="btn-secondary">Cancel</button>
        </div>
    `;
    
    // Insert after action buttons
    const actionButtons = document.querySelector('.action-buttons');
    actionButtons.appendChild(menuDiv);
}

function handleCampaignAction() {
    const officeSelect = document.getElementById('campaign-office');
    const pcInput = document.getElementById('campaign-pc');
    
    const officeId = officeSelect.value;
    const influenceAmount = parseInt(pcInput.value);
    
    // Validation
    if (!officeId) {
        showMessage('Please select an office', 'error');
        return;
    }
    
    if (!influenceAmount || influenceAmount <= 0) {
        showMessage('Please enter a valid PC amount', 'error');
        return;
    }
    
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    if (influenceAmount > currentPlayer.pc) {
        showMessage(`You only have ${currentPlayer.pc} PC available`, 'error');
        return;
    }
    
    // Call API
    performAction('campaign', {
        office_id: officeId,
        influence_amount: influenceAmount
    });
    
    closeModal();
}

function closeModal() {
    const modal = document.querySelector('.campaign-modal');
    if (modal) {
        modal.remove();
    }
}

function showMessage(message, type = 'success') {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = message;
    
    // Insert at top of game content
    const gameContent = document.querySelector('.game-content');
    gameContent.insertBefore(messageDiv, gameContent.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    showSetupScreen();
}); 