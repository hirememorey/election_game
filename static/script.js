// Game state management
let currentGameId = null;
let currentGameState = null;
let isAnimating = false;

// Simplified API URL logic - always use the current domain
const API_BASE_URL = `${window.location.protocol}//${window.location.host}/api`;

// Debug logging
console.log('API_BASE_URL:', API_BASE_URL);
console.log('Current hostname:', window.location.hostname);
console.log('Current protocol:', window.location.protocol);
console.log('Current host:', window.location.host);
console.log('Full URL:', window.location.href);

// Accessibility helper
function announceToScreenReader(message) {
    const srAnnouncements = document.getElementById('sr-announcements');
    if (srAnnouncements) {
        srAnnouncements.textContent = message;
        // Clear after a short delay
        setTimeout(() => {
            srAnnouncements.textContent = '';
        }, 1000);
    }
}

// DOM elements
const setupScreen = document.getElementById('setup-screen');
const gameScreen = document.getElementById('game-screen');
const startGameBtn = document.getElementById('start-game-btn');
const newGameBtn = document.getElementById('new-game-btn');
const runEventBtn = document.getElementById('run-event-btn');
const playerForm = document.getElementById('player-form');

// Game state elements
const roundInfo = document.getElementById('round-info');
const phaseInfo = document.getElementById('phase-info');
const moodInfo = document.getElementById('mood-info');
const logContent = document.getElementById('log-content');
const currentPlayerName = document.getElementById('current-player-name');
const currentPlayerPc = document.getElementById('current-player-pc');
const currentPlayerOffice = document.getElementById('current-player-office');
const currentPlayerAvatar = document.getElementById('current-player-avatar');
const actionList = document.getElementById('action-list');
const eventPhaseSection = document.getElementById('event-phase-section');
const actionPointsDisplay = document.getElementById('action-points-display');
const clearLogBtn = document.getElementById('clear-log-btn');

// Player identity elements
const currentPlayerArchetypeTitle = document.getElementById('current-player-archetype-title');
const currentPlayerArchetypeDesc = document.getElementById('current-player-archetype-desc');
const currentPlayerMandateTitle = document.getElementById('current-player-mandate-title');
const currentPlayerMandateDesc = document.getElementById('current-player-mandate-desc');

// Event listeners
if (startGameBtn) {
    startGameBtn.addEventListener('click', startNewGame);
}
if (newGameBtn) {
    newGameBtn.addEventListener('click', showSetupScreen);
}
if (runEventBtn) {
    runEventBtn.addEventListener('click', runEventPhase);
}
if (playerForm) {
    playerForm.addEventListener('submit', function(e) {
        e.preventDefault();
        startNewGame();
    });
}
if (clearLogBtn) {
    clearLogBtn.addEventListener('click', clearGameLog);
}

// API functions
async function apiCall(endpoint, method = 'GET', data = null) {
    try {
        console.log(`API Call: ${method} ${API_BASE_URL}${endpoint}`);
        if (data) {
            console.log('Request data:', data);
        }
        
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
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        const result = await response.json();
        console.log('Response data:', result);
        
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
    console.log('startNewGame called');
    
    const playerNames = [];
    for (let i = 1; i <= 4; i++) {
        const input = document.getElementById(`player${i}`);
        if (input && input.value.trim()) {
            playerNames.push(input.value.trim());
        }
    }
    
    console.log('Player names:', playerNames);
    
    if (playerNames.length < 2) {
        showMessage('Please enter at least 2 player names', 'error');
        return;
    }
    
    try {
        if (startGameBtn) {
            startGameBtn.disabled = true;
            const btnText = startGameBtn.querySelector('.btn-text');
            if (btnText) btnText.textContent = 'Creating Game...';
        }
        
        console.log('Making API call to create game...');
        const result = await apiCall('/game', 'POST', { player_names: playerNames });
        console.log('API call successful:', result);
        
        currentGameId = result.game_id;
        currentGameState = result.state;
        
        showGameScreen();
        updateGameDisplay();
    } catch (error) {
        console.error('Failed to start game:', error);
        showMessage(`Failed to start game: ${error.message}`, 'error');
    } finally {
        if (startGameBtn) {
            startGameBtn.disabled = false;
            const btnText = startGameBtn.querySelector('.btn-text');
            if (btnText) btnText.textContent = 'Start Game';
        }
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
        if (runEventBtn) {
            runEventBtn.disabled = true;
            const btnText = runEventBtn.querySelector('.btn-text');
            if (btnText) btnText.textContent = 'Drawing Event...';
        }
        
        const result = await apiCall(`/game/${currentGameId}/event`, 'POST');
        currentGameState = result.state;
        updateGameDisplay();
    } catch (error) {
        console.error('Failed to run event phase:', error);
    } finally {
        if (runEventBtn) {
            runEventBtn.disabled = false;
            const btnText = runEventBtn.querySelector('.btn-text');
            if (btnText) btnText.textContent = 'Draw Event Card';
        }
    }
}

// UI functions
function showSetupScreen() {
    if (setupScreen) setupScreen.classList.remove('hidden');
    if (gameScreen) gameScreen.classList.add('hidden');
    currentGameId = null;
    currentGameState = null;
    
    // Clear form
    for (let i = 1; i <= 4; i++) {
        const input = document.getElementById(`player${i}`);
        if (input) input.value = '';
    }
}

function showGameScreen() {
    if (setupScreen) setupScreen.classList.add('hidden');
    if (gameScreen) gameScreen.classList.remove('hidden');
}

function updateGameDisplay() {
    if (!currentGameState) return;
    
    // Update enhanced turn status
    updateTurnStatus();
    
    // Update game info
    if (roundInfo) roundInfo.textContent = `Round ${currentGameState.round_marker}`;
    if (phaseInfo) phaseInfo.textContent = formatPhase(currentGameState.current_phase);
    if (moodInfo) moodInfo.textContent = `Public Mood: ${formatMood(currentGameState.public_mood)}`;
    
    // Update turn log
    updateTurnLog();
    
    // Update current player info
    updateCurrentPlayerInfo();
    
    // Update action buttons
    updateActionButtons();
    
    // Update pending legislation
    updatePendingLegislationDisplay();
    
    // Update player favors
    updatePlayerFavorsDisplay();
    
    // Update event phase button
    updateEventPhaseButton();
}

function updateTurnStatus() {
    const turnStatus = document.getElementById('turn-status');
    if (!turnStatus || !currentGameState) return;
    
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    const remainingAP = currentGameState.action_points?.[currentPlayer.id] || 3;
    const phase = currentGameState.current_phase;
    const round = currentGameState.round_marker;
    
    // Get phase-specific styling and description
    let phaseClass = '';
    let phaseDescription = '';
    switch (phase) {
        case 'event_phase':
            phaseClass = 'event-phase-status';
            phaseDescription = 'Event Phase - Drawing event cards';
            break;
        case 'action_phase':
            phaseClass = 'action-phase-status';
            phaseDescription = 'Action Phase - Taking strategic actions';
            break;
        case 'LEGISLATION_PHASE':
            phaseClass = 'legislation-session-status';
            phaseDescription = 'Legislation Session - Voting on bills';
            break;
        case 'election_phase':
            phaseClass = 'election-phase-status';
            phaseDescription = 'Election Phase - Determining winners';
            break;
    }
    
    // Announce turn change to screen readers
    announceToScreenReader(`${currentPlayer.name}'s turn. ${phaseDescription}. ${remainingAP} action points remaining.`);
    
    turnStatus.innerHTML = `
        <div class="turn-status-content">
            <div class="player-turn">
                <span class="player-icon" aria-hidden="true">👤</span>
                <span class="player-name">${currentPlayer.name}</span>
                <span class="player-number">Player ${currentGameState.current_player_index + 1}</span>
            </div>
            
            <div class="phase-indicator ${phaseClass}">
                <span class="phase-icon" aria-hidden="true">${getPhaseIcon(phase)}</span>
                <span class="phase-text">${formatPhase(phase)}</span>
            </div>
            
            <div class="ap-display">
                <span class="ap-icon" aria-hidden="true">⚡</span>
                <span class="ap-text">${remainingAP}/3 Action Points</span>
            </div>
            
            <div class="round-info">
                <span class="round-icon" aria-hidden="true">📊</span>
                <span class="round-text">Round ${round}</span>
            </div>
        </div>
    `;
    
    // Add subtle animation for turn changes
    if (!isAnimating) {
        isAnimating = true;
        turnStatus.style.transform = 'scale(1.02)';
        setTimeout(() => {
            turnStatus.style.transform = 'scale(1)';
            isAnimating = false;
        }, 200);
    }
}

function getPhaseIcon(phase) {
    const icons = {
        'event_phase': '🎲',
        'action_phase': '⚡',
        'LEGISLATION_PHASE': '📋',
        'election_phase': '🗳️'
    };
    return icons[phase] || '⚡';
}

function updateCurrentPlayerInfo() {
    if (!currentGameState) return;
    
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    
    if (currentPlayerName) currentPlayerName.textContent = currentPlayer.name;
    if (currentPlayerPc) currentPlayerPc.textContent = currentPlayer.pc;
    if (currentPlayerOffice) {
        const office = currentPlayer.current_office;
        currentPlayerOffice.textContent = office ? office.title : 'None';
    }
    
    // Update player avatar
    if (currentPlayerAvatar) {
        currentPlayerAvatar.textContent = getPlayerAvatar(currentPlayer);
    }
    
    // Update archetype and mandate - now using embedded data from player object
    if (currentPlayerArchetypeTitle) {
        const archetype = currentPlayer.archetype;
        currentPlayerArchetypeTitle.textContent = archetype ? archetype.title : 'Loading...';
        if (currentPlayerArchetypeDesc) {
            currentPlayerArchetypeDesc.textContent = archetype ? archetype.description : 'Loading...';
        }
    }
    
    if (currentPlayerMandateTitle) {
        const mandate = currentPlayer.mandate;
        currentPlayerMandateTitle.textContent = mandate ? mandate.title : 'Loading...';
        if (currentPlayerMandateDesc) {
            currentPlayerMandateDesc.textContent = mandate ? mandate.description : 'Loading...';
        }
    }
}

function getPlayerAvatar(player) {
    // Simple avatar based on player name
    const avatars = ['👤', '👨‍💼', '👩‍💼', '👨‍⚖️', '👩‍⚖️', '👨‍🎓', '👩‍🎓'];
    const index = player.name.length % avatars.length;
    return avatars[index];
}

function updatePendingLegislationDisplay() {
    const pendingSection = document.getElementById('pending-legislation-section');
    if (!pendingSection || !currentGameState) return;
    
    if (currentGameState.current_phase === 'LEGISLATION_PHASE' && currentGameState.term_legislation && currentGameState.term_legislation.length > 0) {
        pendingSection.classList.remove('hidden');
        pendingSection.innerHTML = `
            <div class="section-header">
                <h3>Pending Legislation</h3>
            </div>
            <div class="legislation-list">
                ${currentGameState.term_legislation.map(legislation => {
                    const bill = currentGameState.legislation_options[legislation.legislation_id];
                    const sponsor = currentGameState.players.find(p => p.id === legislation.sponsor_id);
                    return `
                        <div class="legislation-item">
                            <div class="legislation-header">
                                <h4>${bill.title}</h4>
                                <span class="sponsor">Sponsored by ${sponsor.name}</span>
                            </div>
                            <div class="legislation-details">
                                <span class="cost">Cost: ${bill.cost} PC</span>
                                <span class="target">Success Target: ${bill.success_target}</span>
                                <span class="crit-target">Crit Target: ${bill.crit_target}</span>
                            </div>
                        </div>
                    `;
                }).join('')}
            </div>
        `;
    } else {
        pendingSection.classList.add('hidden');
    }
}

function updatePlayerFavorsDisplay() {
    const favorsSection = document.getElementById('player-favors-section');
    if (!favorsSection || !currentGameState) return;
    
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    const favors = currentPlayer.favors || [];
    
    if (favors.length > 0) {
        favorsSection.classList.remove('hidden');
        favorsSection.innerHTML = `
            <div class="section-header">
                <h3>Political Favors</h3>
            </div>
            <div class="favors-list">
                ${favors.map(favor => `
                    <div class="favor-item">
                        <span class="favor-icon">🎁</span>
                        <span class="favor-text">${favor.description}</span>
                    </div>
                `).join('')}
            </div>
        `;
    } else {
        favorsSection.classList.add('hidden');
    }
}

function updateTurnLog() {
    if (!logContent || !currentGameState) return;
    
    const logs = currentGameState.turn_log || [];
    logContent.innerHTML = logs.map(log => `<p>${log}</p>`).join('');
    
    // Auto-scroll to bottom
    logContent.scrollTop = logContent.scrollHeight;
}

function clearGameLog() {
    if (logContent) {
        logContent.innerHTML = '';
    }
}

function updateActionButtons() {
    if (!actionList || !currentGameState) return;
    
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    const remainingAP = currentGameState.action_points?.[currentPlayer.id] || 3;
    
    // Update action points display
    if (actionPointsDisplay) {
        actionPointsDisplay.innerHTML = `
            <span class="ap-icon">⚡</span>
            <span class="ap-text">${remainingAP}/3 AP</span>
        `;
    }
    
    // Clear existing actions
    actionList.innerHTML = '';
    
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
    
    // Define available actions based on game state
    const actions = [];
    
    // Basic actions
    actions.push({
        type: 'fundraise',
        label: 'Fundraise',
        description: 'Gain Political Capital',
        ap_cost: 1
    });
    
    actions.push({
        type: 'network',
        label: 'Network',
        description: 'Gain PC and political favors',
        ap_cost: 1
    });
    
    actions.push({
        type: 'sponsor_legislation',
        label: 'Sponsor Legislation',
        description: 'Create legislation for votes and mood',
        ap_cost: 2
    });
    
    // Campaign action (new)
    actions.push({
        type: 'campaign',
        label: 'Campaign',
        description: 'Place influence for future election',
        ap_cost: 2
    });
    
    // Use Favor (only if player has favors)
    const favors = currentPlayer.favors || [];
    if (favors.length > 0) {
        actions.push({
            type: 'use_favor',
            label: 'Use Favor',
            description: 'Use a political favor',
            ap_cost: 0
        });
    }
    
    // Declare Candidacy (only in Round 4)
    if (currentGameState.round_marker === 4) {
        actions.push({
            type: 'declare_candidacy',
            label: 'Declare Candidacy',
            description: 'Run for office',
            ap_cost: 2
        });
    }
    
    // Legislation session actions
    if (currentGameState.current_phase === 'LEGISLATION_PHASE' && currentGameState.term_legislation && currentGameState.term_legislation.length > 0) {
        actions.push({
            type: 'support_legislation',
            label: 'Support Legislation',
            description: 'Support pending legislation',
            ap_cost: 1
        });
        
        actions.push({
            type: 'oppose_legislation',
            label: 'Oppose Legislation',
            description: 'Oppose pending legislation',
            ap_cost: 1
        });
        
        // Trading actions
        actions.push({
            type: 'propose_trade',
            label: 'Propose Trade',
            description: 'Propose a trade for votes',
            ap_cost: 0
        });
    }
    
    // Create action buttons
    actions.forEach(action => {
        const canAfford = remainingAP >= action.ap_cost;
        const button = document.createElement('button');
        button.className = 'action-btn';
        button.disabled = !canAfford;
        button.setAttribute('aria-label', `${action.label}: ${action.description}. Cost: ${action.ap_cost} Action Points.`);
        
        button.innerHTML = `
            <div class="action-label">${action.label}</div>
            <div class="action-cost">${action.ap_cost} AP</div>
            <div class="action-description">${action.description}</div>
        `;
        
        if (!canAfford) {
            button.title = `Not enough Action Points. Need ${action.ap_cost}, have ${remainingAP}`;
            button.setAttribute('aria-describedby', 'insufficient-ap');
        }
        
        button.onclick = () => {
            // Add click feedback
            button.style.transform = 'scale(0.98)';
            setTimeout(() => {
                button.style.transform = '';
            }, 150);
            
            handleActionClick(action.type);
        };
        
        actionList.appendChild(button);
    });
    
    // Add insufficient AP message for screen readers
    if (actions.some(action => remainingAP < action.ap_cost)) {
        const insufficientMsg = document.createElement('div');
        insufficientMsg.id = 'insufficient-ap';
        insufficientMsg.className = 'sr-only';
        insufficientMsg.textContent = 'Some actions are disabled due to insufficient Action Points.';
        actionList.appendChild(insufficientMsg);
    }
}

function handleActionClick(actionType) {
    switch (actionType) {
        case 'fundraise':
            performAction('fundraise');
            break;
        case 'network':
            performAction('network');
            break;
        case 'sponsor_legislation':
            showLegislationMenu();
            break;
        case 'declare_candidacy':
            showCandidacyMenu();
            break;
        case 'use_favor':
            showFavorMenu();
            break;
        case 'support_legislation':
            showLegislationSupportMenu();
            break;
        case 'oppose_legislation':
            showLegislationOpposeMenu();
            break;
        case 'campaign':
            showCampaignDialog();
            break;
        case 'propose_trade':
            showTradeProposalMenu();
            break;
        default:
            console.log('Unknown action type:', actionType);
    }
}

function updateEventPhaseButton() {
    if (!eventPhaseSection || !currentGameState) return;
    
    if (currentGameState.current_phase === 'event_phase') {
        eventPhaseSection.classList.remove('hidden');
    } else {
        eventPhaseSection.classList.add('hidden');
    }
}

function formatPhase(phase) {
    const phaseMap = {
        'event_phase': 'Event Phase',
        'action_phase': 'Action Phase',
        'LEGISLATION_PHASE': 'Legislation Session',
        'election_phase': 'Election Phase'
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
    
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    const modal = document.createElement('div');
    modal.id = 'legislation-menu';
    modal.className = 'legislation-menu';
    
    modal.innerHTML = `
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
        <div class="modal-buttons">
            <button class="btn-secondary cancel-btn">Cancel</button>
        </div>
    `;
    
    // Add event listeners
    modal.querySelectorAll('.legislation-option').forEach(button => {
        button.addEventListener('click', () => {
            const legislationId = button.dataset.legislationId;
            performAction('sponsor_legislation', { legislation_id: legislationId });
            overlay.remove();
        });
    });
    
    modal.querySelector('.cancel-btn').addEventListener('click', () => {
        overlay.remove();
    });
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
}

function showFavorMenu() {
    // Remove existing favor menu
    const existingMenu = document.getElementById('favor-menu');
    if (existingMenu) {
        existingMenu.remove();
    }
    
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    const modal = document.createElement('div');
    modal.id = 'favor-menu';
    modal.className = 'favor-menu';
    
    modal.innerHTML = `
        <h3>Choose a Favor to Use</h3>
        <div class="favor-options">
            ${currentPlayer.favors.map(favor => `
                <button class="favor-option" data-favor-id="${favor.id}" data-favor-description="${favor.description}">
                    <div><strong>${favor.description}</strong></div>
                </button>
            `).join('')}
        </div>
        <div class="modal-buttons">
            <button class="btn-secondary cancel-btn">Cancel</button>
        </div>
    `;
    
    // Add event listeners
    modal.querySelectorAll('.favor-option').forEach(button => {
        button.addEventListener('click', () => {
            const favorId = button.dataset.favorId;
            const favorDescription = button.dataset.favorDescription;
            
            // Check if this favor requires a target
            if (favorDescription.includes('Target player') || favorDescription.includes('Choose one player')) {
                showTargetPlayerSelection(favorId, favorDescription, overlay);
            } else {
                // No target needed, use favor directly
                performAction('use_favor', { favor_id: favorId });
                overlay.remove();
            }
        });
    });
    
    modal.querySelector('.cancel-btn').addEventListener('click', () => {
        overlay.remove();
    });
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
}

function showTargetPlayerSelection(favorId, favorDescription, parentOverlay) {
    // Remove the parent modal
    parentOverlay.remove();
    
    // Create new modal for player selection
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    const modal = document.createElement('div');
    modal.className = 'campaign-modal';
    
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    const otherPlayers = currentGameState.players.filter(p => p.id !== currentPlayer.id);
    
    modal.innerHTML = `
        <h3>Select Target Player</h3>
        <p>${favorDescription}</p>
        
        <div class="form-group">
            <label for="target-player">Choose a player to target:</label>
            <select id="target-player" required>
                <option value="">Select a player...</option>
                ${otherPlayers.map(player => `
                    <option value="${player.id}">${player.name}</option>
                `).join('')}
            </select>
        </div>
        
        <div class="modal-buttons">
            <button class="btn-primary use-favor-btn">Use Favor</button>
            <button class="btn-secondary cancel-btn">Cancel</button>
        </div>
    `;
    
    // Add event listeners
    modal.querySelector('.use-favor-btn').addEventListener('click', () => {
        const targetPlayerId = parseInt(modal.querySelector('#target-player').value);
        
        if (!targetPlayerId) {
            showMessage('Please select a target player', 'error');
            return;
        }
        
        performAction('use_favor', { 
            favor_id: favorId,
            target_player_id: targetPlayerId
        });
        
        overlay.remove();
    });
    
    modal.querySelector('.cancel-btn').addEventListener('click', () => {
        overlay.remove();
    });
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
}

function showLegislationSupportMenu() {
    if (!currentGameState || !currentGameState.term_legislation) return;
    
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    const availableLegislation = currentGameState.term_legislation.filter(l => 
        !l.resolved && l.sponsor_id !== currentPlayer.id
    );
    
    if (availableLegislation.length === 0) {
        showMessage('No legislation available to support', 'error');
        return;
    }
    
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    const modal = document.createElement('div');
    modal.className = 'legislation-menu';
    
    modal.innerHTML = `
        <h3>Support Legislation</h3>
        <div class="legislation-options">
            ${availableLegislation.map(legislation => {
                const bill = currentGameState.legislation_options[legislation.legislation_id];
                const sponsor = currentGameState.players.find(p => p.id === legislation.sponsor_id);
                return `
                    <button class="legislation-option" data-legislation-id="${legislation.legislation_id}">
                        <div><strong>${bill.title}</strong></div>
                        <div>Sponsored by: ${sponsor.name}</div>
                        <div>Cost: ${bill.cost} PC | Success: ${bill.success_target} PC</div>
                    </button>
                `;
            }).join('')}
        </div>
        <div class="modal-buttons">
            <button class="btn-secondary cancel-btn">Cancel</button>
        </div>
    `;
    
    // Add event listeners
    modal.querySelectorAll('.legislation-option').forEach(button => {
        button.addEventListener('click', () => {
            const legislationId = button.dataset.legislationId;
            const maxPC = currentPlayer.pc;
            const amount = prompt(`How much PC do you want to commit to support? (You have ${maxPC} PC)`, '1');
            
            if (amount && !isNaN(amount) && parseInt(amount) > 0 && parseInt(amount) <= maxPC) {
                performAction('support_legislation', { 
                    legislation_id: legislationId, 
                    support_amount: parseInt(amount)
                });
            } else if (amount !== null) {
                showMessage('Invalid amount', 'error');
            }
            overlay.remove();
        });
    });
    
    modal.querySelector('.cancel-btn').addEventListener('click', () => {
        overlay.remove();
    });
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
}

function showLegislationOpposeMenu() {
    if (!currentGameState || !currentGameState.term_legislation) return;
    
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    const availableLegislation = currentGameState.term_legislation.filter(l => 
        !l.resolved && l.sponsor_id !== currentPlayer.id
    );
    
    if (availableLegislation.length === 0) {
        showMessage('No legislation available to oppose', 'error');
        return;
    }
    
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    const modal = document.createElement('div');
    modal.className = 'legislation-menu';
    
    modal.innerHTML = `
        <h3>Oppose Legislation</h3>
        <div class="legislation-options">
            ${availableLegislation.map(legislation => {
                const bill = currentGameState.legislation_options[legislation.legislation_id];
                const sponsor = currentGameState.players.find(p => p.id === legislation.sponsor_id);
                return `
                    <button class="legislation-option" data-legislation-id="${legislation.legislation_id}">
                        <div><strong>${bill.title}</strong></div>
                        <div>Sponsored by: ${sponsor.name}</div>
                        <div>Cost: ${bill.cost} PC | Success: ${bill.success_target} PC</div>
                    </button>
                `;
            }).join('')}
        </div>
        <div class="modal-buttons">
            <button class="btn-secondary cancel-btn">Cancel</button>
        </div>
    `;
    
    // Add event listeners
    modal.querySelectorAll('.legislation-option').forEach(button => {
        button.addEventListener('click', () => {
            const legislationId = button.dataset.legislationId;
            const maxPC = currentPlayer.pc;
            const amount = prompt(`How much PC do you want to commit to oppose? (You have ${maxPC} PC)`, '1');
            
            if (amount && !isNaN(amount) && parseInt(amount) > 0 && parseInt(amount) <= maxPC) {
                performAction('oppose_legislation', { 
                    legislation_id: legislationId, 
                    oppose_amount: parseInt(amount)
                });
            } else if (amount !== null) {
                showMessage('Invalid amount', 'error');
            }
            overlay.remove();
        });
    });
    
    modal.querySelector('.cancel-btn').addEventListener('click', () => {
        overlay.remove();
    });
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
}

function showCampaignDialog() {
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    const modal = document.createElement('div');
    modal.className = 'campaign-modal';
    
    modal.innerHTML = `
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
            <button class="btn-primary campaign-btn">Campaign</button>
            <button class="btn-secondary cancel-btn">Cancel</button>
        </div>
    `;
    
    // Add event listeners
    modal.querySelector('.campaign-btn').addEventListener('click', () => {
        const officeSelect = modal.querySelector('#campaign-office');
        const pcInput = modal.querySelector('#campaign-pc');
        
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
        
        if (influenceAmount > currentPlayer.pc) {
            showMessage(`You only have ${currentPlayer.pc} PC available`, 'error');
            return;
        }
        
        // Call API
        performAction('campaign', {
            office_id: officeId,
            influence_amount: influenceAmount
        });
        
        overlay.remove();
    });
    
    modal.querySelector('.cancel-btn').addEventListener('click', () => {
        overlay.remove();
    });
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
}

function showTradeProposalMenu() {
    if (!currentGameState || !currentGameState.term_legislation) return;
    
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    const availableLegislation = currentGameState.term_legislation.filter(l => 
        !l.resolved && l.sponsor_id !== currentPlayer.id
    );
    
    if (availableLegislation.length === 0) {
        showMessage('No legislation available for trading', 'error');
        return;
    }
    
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    const modal = document.createElement('div');
    modal.className = 'trade-proposal-menu';
    
    modal.innerHTML = `
        <h3>Propose Trade</h3>
        <div class="form-group">
            <label for="trade-legislation">Select Legislation:</label>
            <select id="trade-legislation" required>
                <option value="">Choose legislation...</option>
                ${availableLegislation.map(legislation => {
                    const bill = currentGameState.legislation_options[legislation.legislation_id];
                    const sponsor = currentGameState.players.find(p => p.id === legislation.sponsor_id);
                    return `<option value="${legislation.legislation_id}">${bill.title} (${sponsor.name})</option>`;
                }).join('')}
            </select>
        </div>
        
        <div class="form-group">
            <label for="trade-target-player">Target Player:</label>
            <select id="trade-target-player" required>
                <option value="">Choose player...</option>
                ${currentGameState.players
                    .filter(p => p.id !== currentPlayer.id)
                    .map(p => `<option value="${p.id}">${p.name}</option>`)
                    .join('')}
            </select>
        </div>
        
        <div class="form-group">
            <label for="trade-offered-pc">Offer PC:</label>
            <input type="number" id="trade-offered-pc" min="0" max="${currentPlayer.pc}" value="0">
        </div>
        
        <div class="form-group">
            <label for="trade-requested-vote">Requested Vote:</label>
            <select id="trade-requested-vote" required>
                <option value="support">Support</option>
                <option value="oppose">Oppose</option>
                <option value="abstain">Abstain</option>
            </select>
        </div>
        
        <div class="modal-buttons">
            <button class="btn-primary propose-btn">Propose Trade</button>
            <button class="btn-secondary cancel-btn">Cancel</button>
        </div>
    `;
    
    // Add event listeners
    modal.querySelector('.propose-btn').addEventListener('click', () => {
        const legislationId = modal.querySelector('#trade-legislation').value;
        const targetPlayerId = parseInt(modal.querySelector('#trade-target-player').value);
        const offeredPc = parseInt(modal.querySelector('#trade-offered-pc').value) || 0;
        const requestedVote = modal.querySelector('#trade-requested-vote').value;
        
        if (!legislationId || !targetPlayerId || !requestedVote) {
            showMessage('Please fill in all required fields', 'error');
            return;
        }
        
        performAction('propose_trade', {
            target_player_id: targetPlayerId,
            legislation_id: legislationId,
            offered_pc: offeredPc,
            requested_vote: requestedVote
        });
        
        overlay.remove();
    });
    
    modal.querySelector('.cancel-btn').addEventListener('click', () => {
        overlay.remove();
    });
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
}

function showCandidacyMenu() {
    const currentPlayer = currentGameState.players[currentGameState.current_player_index];
    
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    const modal = document.createElement('div');
    modal.className = 'campaign-modal';
    
    modal.innerHTML = `
        <h3>Declare Candidacy</h3>
        <p>Run for office by committing PC to your campaign.</p>
        
        <div class="form-group">
            <label for="candidacy-office">Select Office:</label>
            <select id="candidacy-office" required>
                <option value="">Choose an office...</option>
                ${Object.values(currentGameState.offices || {}).map(office => {
                    const canAfford = currentPlayer.pc >= office.candidacy_cost;
                    return `<option value="${office.id}" ${!canAfford ? 'disabled' : ''}>
                        ${office.title} (Cost: ${office.candidacy_cost} PC)${!canAfford ? ' - Cannot Afford' : ''}
                    </option>`;
                }).join('')}
            </select>
        </div>
        
        <div class="form-group">
            <label for="candidacy-pc">Additional PC to Commit:</label>
            <input type="number" id="candidacy-pc" min="0" max="${currentPlayer.pc}" value="0" 
                   placeholder="Enter additional PC amount">
        </div>
        
        <div class="modal-buttons">
            <button class="btn-primary candidacy-btn">Declare Candidacy</button>
            <button class="btn-secondary cancel-btn">Cancel</button>
        </div>
    `;
    
    // Add event listeners
    modal.querySelector('.candidacy-btn').addEventListener('click', () => {
        const officeSelect = modal.querySelector('#candidacy-office');
        const pcInput = modal.querySelector('#candidacy-pc');
        
        const officeId = officeSelect.value;
        const additionalPc = parseInt(pcInput.value) || 0;
        
        if (!officeId) {
            showMessage('Please select an office', 'error');
            return;
        }
        
        const office = currentGameState.offices[officeId];
        const totalCost = office.candidacy_cost + additionalPc;
        
        if (totalCost > currentPlayer.pc) {
            showMessage(`You only have ${currentPlayer.pc} PC available`, 'error');
            return;
        }
        
        performAction('declare_candidacy', {
            office_id: officeId,
            committed_pc: additionalPc
        });
        
        overlay.remove();
    });
    
    modal.querySelector('.cancel-btn').addEventListener('click', () => {
        overlay.remove();
    });
    
    overlay.appendChild(modal);
    document.body.appendChild(overlay);
}

function showMessage(message, type = 'success') {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.setAttribute('role', 'alert');
    messageDiv.setAttribute('aria-live', 'polite');
    
    // Add icon based on type
    const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
    messageDiv.innerHTML = `
        <span class="message-icon" aria-hidden="true">${icon}</span>
        <span class="message-text">${message}</span>
    `;
    
    // Insert at top of game content
    const gameContent = document.querySelector('.game-content');
    if (gameContent) {
        gameContent.insertBefore(messageDiv, gameContent.firstChild);
    }
    
    // Announce to screen readers
    announceToScreenReader(`${type}: ${message}`);
    
    // Add entrance animation
    messageDiv.style.transform = 'translateY(-20px)';
    messageDiv.style.opacity = '0';
    
    setTimeout(() => {
        messageDiv.style.transform = 'translateY(0)';
        messageDiv.style.opacity = '1';
    }, 10);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageDiv.parentNode) {
            messageDiv.style.transform = 'translateY(-20px)';
            messageDiv.style.opacity = '0';
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.remove();
                }
            }, 300);
        }
    }, 5000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    showSetupScreen();
}); 