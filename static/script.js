// Simplified Phase-Based UI for Election Game

// Game state management
let gameId = null;
let gameState = null;

// Simplified API URL logic
const API_BASE_URL = `${window.location.protocol}//${window.location.host}/api`;

// Debug logging
console.log('API_BASE_URL:', API_BASE_URL);

// Accessibility helper
function announceToScreenReader(message) {
    const srAnnouncements = document.getElementById('sr-announcements');
    if (srAnnouncements) {
        srAnnouncements.textContent = message;
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
const playerForm = document.getElementById('player-form');

// Phase-based UI elements
const phaseIndicator = document.getElementById('phase-indicator');
const actionContent = document.getElementById('action-content');
const primaryActions = document.getElementById('primary-actions');
const quickAccessPanel = document.getElementById('quick-access-panel');

// Event listeners
if (startGameBtn) {
    startGameBtn.addEventListener('click', startNewGame);
}
if (newGameBtn) {
    newGameBtn.addEventListener('click', showSetupScreen);
}
if (playerForm) {
    playerForm.addEventListener('submit', function(e) {
        e.preventDefault();
        startNewGame();
    });
}

// Swipe gesture handling
let touchStartY = 0;
let touchEndY = 0;

document.addEventListener('touchstart', function(e) {
    touchStartY = e.changedTouches[0].screenY;
});

document.addEventListener('touchend', function(e) {
    touchEndY = e.changedTouches[0].screenY;
    handleSwipe();
});

function handleSwipe() {
    const swipeThreshold = 50;
    const swipeDistance = touchStartY - touchEndY;
    
    if (swipeDistance > swipeThreshold) {
        // Swipe up - show quick access panel
        showQuickAccess();
    } else if (swipeDistance < -swipeThreshold) {
        // Swipe down - hide quick access panel
        hideQuickAccess();
    }
}

function showQuickAccess() {
    quickAccessPanel.classList.add('show');
    updateQuickAccessContent();
}

function hideQuickAccess() {
    quickAccessPanel.classList.remove('show');
}

function updateGameLog() {
    if (!gameState) return;
    const gameLogDiv = document.getElementById('game-log');
    if (!gameLogDiv) return;
    const log = gameState.turn_log || [];
    if (log.length === 0) {
        gameLogDiv.innerHTML = '<div class="game-log-entry">No game events yet.</div>';
    } else {
        // Show the last 20 log entries for context
        const entries = log.slice(-20).map(entry => `<div class="game-log-entry">${entry}</div>`).join('');
        gameLogDiv.innerHTML = entries;
    }
}

function updateQuickAccessContent() {
    if (!gameState) return;
    const quickAccessDiv = document.getElementById('quick-access-content');
    if (!quickAccessDiv) return;
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    const log = gameState.turn_log || [];
    
    let html = '<div class="identity-section">';
    html += '<h3>Your Identity</h3>';
    
    // Display archetype
    if (currentPlayer.archetype) {
        html += `<div class="identity-card archetype-card">`;
        html += `<div class="card-header">🎭 ${currentPlayer.archetype.title}</div>`;
        html += `<div class="card-description">${currentPlayer.archetype.description}</div>`;
        html += '</div>';
    }
    
    // Display mandate (mission)
    if (currentPlayer.mandate) {
        html += `<div class="identity-card mandate-card">`;
        html += `<div class="card-header">🎯 ${currentPlayer.mandate.title}</div>`;
        html += `<div class="card-description">${currentPlayer.mandate.description}</div>`;
        html += '</div>';
    }
    
    html += '</div>';
    
    // Add game log section
    html += '<div class="log-section">';
    html += '<h3>Game Log</h3>';
    if (log.length === 0) {
        html += '<div class="game-log-entry">No game events yet.</div>';
    } else {
        log.forEach(entry => {
            html += `<div class="game-log-entry">${entry}</div>`;
        });
    }
    html += '</div>';
    
    quickAccessDiv.innerHTML = html;
}

// Ensure log updates after every phase/action
function updatePhaseUI() {
    updatePhaseDisplay();
    updateGameLog();
    updateActionArea();
    updatePrimaryActions();
    updateQuickAccessContent();
}

// Ensure quick access panel opens on swipe/click
function setupQuickAccessPanel() {
    const panel = document.getElementById('quick-access-panel');
    const closeBtn = document.getElementById('close-quick-access');
    const gameInfoBtn = document.getElementById('game-info-btn');
    if (closeBtn) closeBtn.onclick = hideQuickAccess;
    if (gameInfoBtn) gameInfoBtn.onclick = showQuickAccess;
    
    // Swipe up gesture for touch devices
    let startY = null;
    document.body.addEventListener('touchstart', function(e) {
        if (e.touches.length === 1) {
            startY = e.touches[0].clientY;
        }
    });
    document.body.addEventListener('touchend', function(e) {
        if (startY !== null && e.changedTouches.length === 1) {
            const endY = e.changedTouches[0].clientY;
            if (startY - endY > 60) {
                showQuickAccess();
            }
            startY = null;
        }
    });
    
    // Keyboard shortcut (G key) for desktop
    document.addEventListener('keydown', function(e) {
        if (e.key.toLowerCase() === 'g' && !e.ctrlKey && !e.altKey && !e.metaKey) {
            e.preventDefault();
            showQuickAccess();
        }
    });
}

// Call setupQuickAccessPanel on load
window.addEventListener('DOMContentLoaded', setupQuickAccessPanel);

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
    const playerInputs = document.querySelectorAll('input[name^="player"]');
    
    playerInputs.forEach(input => {
        if (input.value.trim()) {
            playerNames.push(input.value.trim());
        }
    });
    
    console.log('Player names:', playerNames);
    
    if (playerNames.length < 2) {
        showMessage('Please enter at least 2 player names', 'error');
        return;
    }
    
    try {
        if (startGameBtn) {
            startGameBtn.disabled = true;
            startGameBtn.textContent = 'Creating Game...';
        }
        
        console.log('Making API call to create game...');
        const result = await apiCall('/game', 'POST', { player_names: playerNames });
        console.log('API call successful:', result);
        
        gameId = result.game_id;
        gameState = result.state;
        
        showGameScreen();
        updatePhaseUI();
    } catch (error) {
        console.error('Failed to start game:', error);
        showMessage(`Failed to start game: ${error.message}`, 'error');
    } finally {
        if (startGameBtn) {
            startGameBtn.disabled = false;
            startGameBtn.textContent = 'Start Game';
        }
    }
}

async function getGameState() {
    if (!gameId) return;
    
    try {
        const result = await apiCall(`/game/${gameId}`);
        gameState = result.state;
        updatePhaseUI();
    } catch (error) {
        console.error('Failed to get game state:', error);
    }
}

async function performAction(actionType, additionalData = {}) {
    if (!gameId) return;
    
    if (!gameState || !gameState.players) {
        console.error('Game state not available for action');
        showMessage('Game state not available. Please refresh the page.', 'error');
        return;
    }
    
    try {
        const data = {
            action_type: actionType,
            player_id: gameState.players[gameState.current_player_index].id,
            ...additionalData
        };
        
        const result = await apiCall(`/game/${gameId}/action`, 'POST', data);
        gameState = result.state;
        updatePhaseUI();
    } catch (error) {
        console.error('Failed to perform action:', error);
    }
}

// UI functions
function showSetupScreen() {
    setupScreen.classList.remove('hidden');
    gameScreen.classList.add('hidden');
}

function showGameScreen() {
    setupScreen.classList.add('hidden');
    gameScreen.classList.remove('hidden');
}

function updatePhaseUI() {
    if (!gameState) return;
    
    updatePhaseDisplay();
    updateGameLog();
    updateActionArea();
    updatePrimaryActions();
    updateQuickAccessContent();
}

function updatePhaseDisplay() {
    if (!gameState) return;
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    const phase = gameState.current_phase;
    const round = gameState.round_marker;
    const ap = gameState.action_points[currentPlayer.id.toString()] || 0;
    
    const phaseTitle = getPhaseTitle(phase);
    const phaseSubtitle = getPhaseSubtitle(phase, round);
    
    phaseIndicator.innerHTML = `
        <div class="phase-title">${phaseTitle}</div>
        <div class="phase-subtitle">${phaseSubtitle}</div>
        <div class="player-turn">
            <div class="player-avatar">${getPlayerAvatar(currentPlayer)}</div>
            <div class="player-info">
                <div class="player-name">${currentPlayer.name}</div>
                <div class="player-stats">PC: ${currentPlayer.pc} | Office: ${getPlayerOffice(currentPlayer)}</div>
            </div>
        </div>
        <div class="action-points">
            <span class="ap-icon">⚡</span>
            <span>${ap} AP</span>
        </div>
    `;
}

function getPhaseTitle(phase) {
    const phaseTitles = {
        'EVENT_PHASE': 'Event Phase',
        'ACTION_PHASE': 'Action Phase',
        'LEGISLATION_PHASE': 'Legislation Session',
        'ELECTION_PHASE': 'Election Phase'
    };
    return phaseTitles[phase] || 'Game Phase';
}

function getPhaseSubtitle(phase, round) {
    if (phase === 'EVENT_PHASE') {
        return 'Drawing event card...';
    } else if (phase === 'ACTION_PHASE') {
        return `Round ${round} - Choose your actions`;
    } else if (phase === 'LEGISLATION_PHASE') {
        return 'Voting on legislation';
    } else if (phase === 'ELECTION_PHASE') {
        return 'Elections are being held';
    }
    return '';
}

function updateActionArea() {
    if (!gameState) return;
    
    const phase = gameState.current_phase;
    const currentPlayer = gameState.players[gameState.current_player_index];
    
    if (phase === 'EVENT_PHASE') {
        showEventPhaseUI();
    } else if (phase === 'ACTION_PHASE') {
        showActionPhaseUI(currentPlayer);
    } else if (phase === 'LEGISLATION_PHASE') {
        showLegislationPhaseUI();
    } else if (phase === 'ELECTION_PHASE') {
        showElectionPhaseUI();
    }
}

function showEventPhaseUI() {
    actionContent.innerHTML = `
        <div class="text-center">
            <h3>Event Phase</h3>
            <p>An event card will be drawn automatically.</p>
        </div>
    `;
}

function showActionPhaseUI(currentPlayer) {
    const availableActions = getAvailableActions(currentPlayer);
    const ap = gameState.action_points[currentPlayer.id.toString()] || 0;
    
    if (availableActions.length === 0) {
        actionContent.innerHTML = `
            <div class="text-center">
                <h3>No Actions Available</h3>
                <p>You have no action points remaining.</p>
            </div>
        `;
        return;
    }
    
    const actionGrid = availableActions.map(action => `
        <button class="action-btn" onclick="handleActionClick('${action.type}')" ${action.disabled ? 'disabled' : ''}>
            <div class="action-icon">${action.icon}</div>
            <div class="action-label">${action.label}</div>
            <div class="action-cost">${action.cost} AP</div>
        </button>
    `).join('');
    
    actionContent.innerHTML = `
        <div class="text-center">
            <h3>Choose Your Action</h3>
            <p>You have ${ap} action points remaining.</p>
            <div class="action-grid">
                ${actionGrid}
            </div>
            <div class="identity-button-container">
                <button class="btn-secondary btn-small" onclick="showIdentityInfo()">
                    <span class="btn-icon">🎭</span>
                    <span class="btn-text">View Identity</span>
                </button>
            </div>
        </div>
    `;
}

function showLegislationPhaseUI() {
    // Collect all unresolved legislation
    let allLegislation = [];
    if (gameState.pending_legislation && !gameState.pending_legislation.resolved) {
        allLegislation.push(gameState.pending_legislation);
    }
    if (Array.isArray(gameState.term_legislation)) {
        allLegislation = allLegislation.concat(gameState.term_legislation.filter(leg => !leg.resolved));
    }

    if (allLegislation.length === 0) {
        actionContent.innerHTML = `
            <div class="text-center">
                <h3>No Legislation to Vote On</h3>
                <p>There are no pending bills to vote on.</p>
            </div>
        `;
        return;
    }

    const legislationCards = allLegislation.map(legislation => {
        const legislationData = gameState.legislation_options[legislation.legislation_id];
        if (!legislationData) return '';
        return `
            <div class="legislation-card">
                <div class="legislation-header">
                    <div class="legislation-title">${legislationData.title}</div>
                    <div class="legislation-sponsor">Sponsored by ${getPlayerName(legislation.sponsor_id)}</div>
                </div>
                <div class="legislation-description">${legislationData.description || ''}</div>
                <div class="legislation-actions">
                    <button class="btn-primary" onclick="showLegislationSupportMenu('${legislation.legislation_id}')">
                        Support
                    </button>
                    <button class="btn-secondary" onclick="showLegislationOpposeMenu('${legislation.legislation_id}')">
                        Oppose
                    </button>
                    <button class="btn-secondary" onclick="passTurn()">
                        Pass Turn
                    </button>
                </div>
            </div>
        `;
    }).join('');

    actionContent.innerHTML = `
        <div class="text-center">
            <h3>Legislation Session</h3>
            <p>Vote on the pending legislation.</p>
            ${legislationCards}
        </div>
    `;
}

function showElectionPhaseUI() {
    actionContent.innerHTML = `
        <div class="text-center">
            <h3>Election Phase</h3>
            <p>Elections are being held. Results will be shown shortly.</p>
        </div>
    `;
}

function updatePrimaryActions() {
    if (!gameState) return;
    
    const phase = gameState.current_phase;
    let actions = [];
    
    if (phase === 'EVENT_PHASE') {
        actions.push({
            label: 'Draw Event Card',
            icon: '🎲',
            action: 'runEventPhase'
        });
    } else if (phase === 'ACTION_PHASE') {
        const currentPlayer = gameState.players[gameState.current_player_index];
        const ap = gameState.action_points[currentPlayer.id.toString()] || 0;
        if (ap === 0) {
            actions.push({
                label: 'Pass Turn',
                icon: '⏭️',
                action: 'passTurn'
            });
        }
    } else if (gameState.awaiting_legislation_resolution) {
        actions.push({
            label: 'Resolve Legislation',
            icon: '📋',
            action: 'resolveLegislation'
        });
    } else if (gameState.awaiting_election_resolution) {
        actions.push({
            label: 'Resolve Elections',
            icon: '🗳️',
            action: 'resolveElections'
        });
    }
    
    const actionButtons = actions.map(action => `
        <button class="btn-primary btn-large" onclick="${action.action}()">
            <span class="btn-icon">${action.icon}</span>
            <span class="btn-text">${action.label}</span>
        </button>
    `).join('');
    
    primaryActions.innerHTML = actionButtons;
}

function getAvailableActions(currentPlayer) {
    const actions = [];
    const ap = gameState.action_points[currentPlayer.id.toString()] || 0;
    
    if (ap >= 1) {
        actions.push({
            type: 'fundraise',
            label: 'Fundraise',
            icon: '💰',
            cost: 1,
            disabled: false
        });
        
        actions.push({
            type: 'network',
            label: 'Network',
            icon: '🤝',
            cost: 1,
            disabled: false
        });
        
        actions.push({
            type: 'use_favor',
            label: 'Use Favor',
            icon: '🎭',
            cost: 1,
            disabled: currentPlayer.favors.length === 0
        });
        
        // Add support/oppose legislation actions if there's pending legislation
        const pendingLegislation = gameState.pending_legislation;
        const termLegislation = gameState.term_legislation || [];
        
        if (pendingLegislation || termLegislation.length > 0) {
            // Check if there's legislation the current player can support/oppose (including their own)
            const availableLegislation = [];
            
            if (pendingLegislation) {
                availableLegislation.push(pendingLegislation);
            }
            
            termLegislation.forEach(leg => {
                availableLegislation.push(leg);
            });
            
            if (availableLegislation.length > 0) {
                actions.push({
                    type: 'support_legislation',
                    label: 'Support Legislation',
                    icon: '✅',
                    cost: 1,
                    disabled: false
                });
                
                actions.push({
                    type: 'oppose_legislation',
                    label: 'Oppose Legislation',
                    icon: '❌',
                    cost: 1,
                    disabled: false
                });
            }
        }
    }
    
    if (ap >= 2) {
        actions.push({
            type: 'sponsor_legislation',
            label: 'Sponsor Legislation',
            icon: '📜',
            cost: 2,
            disabled: false
        });
        
        actions.push({
            type: 'campaign',
            label: 'Campaign',
            icon: '🎯',
            cost: 2,
            disabled: false
        });
        
        if (gameState.round_marker === 4) {
            actions.push({
                type: 'declare_candidacy',
                label: 'Declare Candidacy',
                icon: '🏛️',
                cost: 2,
                disabled: false
            });
        }
    }
    
    return actions;
}

function getPlayerAvatar(player) {
    return player.name.charAt(0).toUpperCase();
}

function getPlayerName(playerId) {
    const player = gameState.players.find(p => p.id === playerId);
    return player ? player.name : 'Unknown';
}

function getPlayerOffice(player) {
    // Use current_office for display
    if (player.current_office && player.current_office.title) {
        return player.current_office.title;
    }
    return 'None';
}

// Action handlers
function handleActionClick(actionType) {
    switch (actionType) {
        case 'fundraise':
            performAction('fundraise');
            break;
        case 'network':
            performAction('network');
            break;
        case 'use_favor':
            showFavorMenu();
            break;
        case 'sponsor_legislation':
            showLegislationMenu();
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
        case 'declare_candidacy':
            showCandidacyMenu();
            break;
        default:
            console.error('Unknown action type:', actionType);
    }
}

async function runEventPhase() {
    if (!gameId) return;
    
    try {
        const result = await apiCall(`/game/${gameId}/event`, 'POST');
        gameState = result.state;
        updatePhaseUI();
    } catch (error) {
        console.error('Failed to run event phase:', error);
    }
}

async function passTurn() {
    await performAction('pass_turn');
}

async function resolveLegislation() {
    if (!gameId) return;
    
    try {
        const result = await apiCall(`/game/${gameId}/resolve_legislation`, 'POST');
        gameState = result.state;
        updatePhaseUI();
    } catch (error) {
        console.error('Failed to resolve legislation:', error);
    }
}

async function resolveElections() {
    if (!gameId) return;
    
    try {
        const result = await apiCall(`/game/${gameId}/resolve_elections`, 'POST');
        gameState = result.state;
        updatePhaseUI();
    } catch (error) {
        console.error('Failed to resolve elections:', error);
    }
}

// Modal functions
function showFavorMenu() {
    const currentPlayer = gameState.players[gameState.current_player_index];
    
    if (currentPlayer.favors.length === 0) {
        showMessage('You have no favors to use', 'info');
        return;
    }
    
    const favorOptions = currentPlayer.favors.map(favor => `
        <button class="action-btn" onclick="useFavor('${favor.id}')">
            <div class="action-icon">🎭</div>
            <div class="action-label">${favor.description}</div>
        </button>
    `).join('');
    
    showModal('Use Favor', `
        <div class="text-center">
            <p>Choose a favor to use:</p>
            <div class="action-grid">
                ${favorOptions}
            </div>
        </div>
    `);
}

function showLegislationMenu() {
    // Convert legislation_options object to array
    const legislationArray = Object.values(gameState.legislation_options);
    const legislationOptions = legislationArray.map(legislation => `
        <button class="action-btn" onclick="sponsorLegislation('${legislation.id}')">
            <div class="action-icon">📜</div>
            <div class="action-label">${legislation.title}</div>
            <div class="action-cost">2 AP</div>
            <div class="legislation-details">
                <div class="legislation-cost">Cost: ${legislation.cost} PC</div>
                <div class="legislation-thresholds">
                    <div>Success: ${legislation.success_target}+ PC</div>
                    <div>Critical: ${legislation.crit_target}+ PC</div>
                </div>
                <div class="legislation-rewards">
                    <div>Success: +${legislation.success_reward} PC</div>
                    <div>Critical: +${legislation.crit_reward} PC</div>
                    ${legislation.failure_penalty > 0 ? `<div>Failure: -${legislation.failure_penalty} PC</div>` : ''}
                </div>
            </div>
        </button>
    `).join('');
    
    showModal('Sponsor Legislation', `
        <div class="text-center">
            <p>Choose legislation to sponsor:</p>
            <div class="action-grid">
                ${legislationOptions}
            </div>
        </div>
    `);
}

function showCampaignDialog() {
    // Get office data from game state
    const offices = gameState.offices || {};
    const officeEntries = Object.entries(offices);
    
    const officeOptions = officeEntries.map(([id, office]) => `
        <option value="${id}">${office.title} (Candidacy Cost: ${office.candidacy_cost} PC)</option>
    `).join('');
    
    showModal('Campaign', `
        <div class="form-group">
            <label for="campaign-office">Office:</label>
            <select id="campaign-office">
                <option value="">Select an office...</option>
                ${officeOptions}
            </select>
        </div>
        <div class="form-group">
            <label for="campaign-pc">PC to Commit:</label>
            <input type="number" id="campaign-pc" min="1" max="50" required placeholder="Enter PC amount">
        </div>
        <div class="modal-actions">
            <button class="btn-primary" onclick="handleCampaignAction()">Campaign</button>
            <button class="btn-secondary" onclick="closeModal()">Cancel</button>
        </div>
    `);
}

function showCandidacyMenu() {
    // Get office data from game state
    const offices = gameState.offices || {};
    const officeEntries = Object.entries(offices);
    
    const officeOptions = officeEntries.map(([id, office]) => `
        <option value="${id}">${office.title} (Cost: ${office.candidacy_cost} PC)</option>
    `).join('');
    
    showModal('Declare Candidacy', `
        <div class="form-group">
            <label for="candidacy-office">Office:</label>
            <select id="candidacy-office">
                <option value="">Select an office...</option>
                ${officeOptions}
            </select>
        </div>
        <div class="form-group">
            <label for="candidacy-pc">Additional PC to Commit:</label>
            <input type="number" id="candidacy-pc" min="0" max="50" required placeholder="Enter PC amount">
        </div>
        <div class="modal-actions">
            <button class="btn-primary" onclick="handleCandidacyAction()">Declare Candidacy</button>
            <button class="btn-secondary" onclick="closeModal()">Cancel</button>
        </div>
    `);
}

async function showLegislationOpposeMenu() {
    await getGameState(); // Always fetch latest state
    const currentPlayer = gameState.players[gameState.current_player_index];
    const pendingLegislation = gameState.pending_legislation;
    const termLegislation = gameState.term_legislation || [];
    
    console.log('DEBUG: showLegislationOpposeMenu called');
    console.log('DEBUG: currentPlayer.id:', currentPlayer.id);
    console.log('DEBUG: pendingLegislation:', pendingLegislation);
    console.log('DEBUG: termLegislation:', termLegislation);
    
    // Find legislation the current player can oppose (including their own)
    const availableLegislation = [];
    
    if (pendingLegislation) {
        const legislationData = gameState.legislation_options[pendingLegislation.legislation_id];
        availableLegislation.push({
            id: pendingLegislation.legislation_id,
            title: legislationData ? legislationData.title : pendingLegislation.legislation_id,
            sponsor: getPlayerName(pendingLegislation.sponsor_id),
            isOwn: pendingLegislation.sponsor_id === currentPlayer.id
        });
    }
    
    termLegislation.forEach(leg => {
        const legislationData = gameState.legislation_options[leg.legislation_id];
        availableLegislation.push({
            id: leg.legislation_id,
            title: legislationData ? legislationData.title : leg.legislation_id,
            sponsor: getPlayerName(leg.sponsor_id),
            isOwn: leg.sponsor_id === currentPlayer.id
        });
    });
    
    console.log('DEBUG: availableLegislation:', availableLegislation);
    
    if (availableLegislation.length === 0) {
        showMessage('No legislation available to oppose', 'info');
        return;
    }
    
    const legislationOptions = availableLegislation.map(leg => `
        <option value="${leg.id}">${leg.title} (sponsored by ${leg.sponsor})${leg.isOwn ? ' - YOUR BILL' : ''}</option>
    `).join('');
    
    showModal('🤫 Secret Opposition Commitment', `
        <div class="secret-commitment-notice">
            <p><strong>⚠️ Secret Commitment:</strong> Your opposition will be hidden from other players until the legislation reveal.</p>
        </div>
        <div class="form-group">
            <label for="oppose-legislation">Choose Legislation:</label>
            <select id="oppose-legislation">
                <option value="">Select legislation...</option>
                ${legislationOptions}
            </select>
        </div>
        <div class="form-group">
            <label for="oppose-pc">PC to Commit (Secret):</label>
            <input type="number" id="oppose-pc" min="1" max="50" required placeholder="Enter PC amount">
        </div>
        <div class="modal-actions">
            <button class="btn-primary" onclick="handleOpposeAction()">🤫 Secretly Oppose</button>
            <button class="btn-secondary" onclick="closeModal()">Cancel</button>
        </div>
    `);
}

async function showLegislationSupportMenu() {
    await getGameState(); // Always fetch latest state
    const currentPlayer = gameState.players[gameState.current_player_index];
    const pendingLegislation = gameState.pending_legislation;
    const termLegislation = gameState.term_legislation || [];
    
    // Find legislation the current player can support (including their own)
    const availableLegislation = [];
    
    if (pendingLegislation) {
        const legislationData = gameState.legislation_options[pendingLegislation.legislation_id];
        availableLegislation.push({
            id: pendingLegislation.legislation_id,
            title: legislationData ? legislationData.title : pendingLegislation.legislation_id,
            sponsor: getPlayerName(pendingLegislation.sponsor_id),
            isOwn: pendingLegislation.sponsor_id === currentPlayer.id
        });
    }
    
    termLegislation.forEach(leg => {
        const legislationData = gameState.legislation_options[leg.legislation_id];
        availableLegislation.push({
            id: leg.legislation_id,
            title: legislationData ? legislationData.title : leg.legislation_id,
            sponsor: getPlayerName(leg.sponsor_id),
            isOwn: leg.sponsor_id === currentPlayer.id
        });
    });
    
    if (availableLegislation.length === 0) {
        showMessage('No legislation available to support', 'info');
        return;
    }
    
    const legislationOptions = availableLegislation.map(leg => `
        <option value="${leg.id}">${leg.title} (sponsored by ${leg.sponsor})${leg.isOwn ? ' - YOUR BILL' : ''}</option>
    `).join('');
    
    showModal('🤫 Secret Support Commitment', `
        <div class="secret-commitment-notice">
            <p><strong>⚠️ Secret Commitment:</strong> Your support will be hidden from other players until the legislation reveal.</p>
        </div>
        <div class="form-group">
            <label for="support-legislation">Choose Legislation:</label>
            <select id="support-legislation">
                <option value="">Select legislation...</option>
                ${legislationOptions}
            </select>
        </div>
        <div class="form-group">
            <label for="support-pc">PC to Commit (Secret):</label>
            <input type="number" id="support-pc" min="1" max="50" required placeholder="Enter PC amount">
        </div>
        <div class="modal-actions">
            <button class="btn-primary" onclick="handleSupportAction()">🤫 Secretly Support</button>
            <button class="btn-secondary" onclick="closeModal()">Cancel</button>
        </div>
    `);
}

function showIdentityInfo() {
    if (!gameState) return;
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    let content = '<div class="identity-modal">';
    
    // Display archetype
    if (currentPlayer.archetype) {
        content += `<div class="identity-card archetype-card">`;
        content += `<div class="card-header">🎭 ${currentPlayer.archetype.title}</div>`;
        content += `<div class="card-description">${currentPlayer.archetype.description}</div>`;
        content += '</div>';
    }
    
    // Display mandate (mission)
    if (currentPlayer.mandate) {
        content += `<div class="identity-card mandate-card">`;
        content += `<div class="card-header">🎯 ${currentPlayer.mandate.title}</div>`;
        content += `<div class="card-description">${currentPlayer.mandate.description}</div>`;
        content += '</div>';
    }
    
    content += '</div>';
    
    showModal('Your Identity', content);
}

// Favor IDs that require a target player
const favorsRequiringTarget = ['POLITICAL_PRESSURE', 'POLITICAL_DEBT', 'POLITICAL_HOT_POTATO'];

async function useFavor(favorId) {
    // Find the favor object to get its id and description
    const currentPlayer = gameState.players[gameState.current_player_index];
    const favor = currentPlayer.favors.find(f => f.id === favorId);
    if (!favor) {
        showMessage('Favor not found', 'error');
        return;
    }
    // If this favor requires a target, prompt for target player
    if (favorsRequiringTarget.includes(favorId)) {
        // Show a modal to select a target player (excluding self)
        const otherPlayers = gameState.players.filter(p => p.id !== currentPlayer.id);
        if (otherPlayers.length === 0) {
            showMessage('No valid target players', 'error');
            return;
        }
        const playerOptions = otherPlayers.map(p => `
            <option value="${p.id}">${p.name}</option>
        `).join('');
        showModal('Select Target Player', `
            <div class="form-group">
                <label for="target-player-select">Choose a player to target:</label>
                <select id="target-player-select">
                    <option value="">Select player...</option>
                    ${playerOptions}
                </select>
            </div>
            <div class="modal-actions">
                <button class="btn-primary" onclick="handleTargetFavorAction('${favorId}')">Use Favor</button>
                <button class="btn-secondary" onclick="closeModal()">Cancel</button>
            </div>
        `);
        return;
    }
    // Otherwise, use the favor immediately
    closeModal();
    await performAction('use_favor', { favor_id: favorId });
}

// Handler for using a favor with a selected target
async function handleTargetFavorAction(favorId) {
    const select = document.getElementById('target-player-select');
    const targetId = select ? parseInt(select.value) : null;
    if (!targetId) {
        showMessage('Please select a target player', 'error');
        return;
    }
    closeModal();
    await performAction('use_favor', { favor_id: favorId, target_player_id: targetId });
}

async function sponsorLegislation(legislationId) {
    closeModal();
    await performAction('sponsor_legislation', { legislation_id: legislationId });
}

async function handleCampaignAction() {
    const officeSelect = document.getElementById('campaign-office');
    const pcInput = document.getElementById('campaign-pc');
    
    const officeId = officeSelect.value;
    const influenceAmount = parseInt(pcInput.value);
    
    if (!officeId || !influenceAmount || influenceAmount <= 0) {
        showMessage('Please enter valid values', 'error');
        return;
    }
    
    closeModal();
    await performAction('campaign', {
        office_id: officeId,
        influence_amount: influenceAmount
    });
}

async function handleCandidacyAction() {
    const officeSelect = document.getElementById('candidacy-office');
    const pcInput = document.getElementById('candidacy-pc');
    
    const officeId = officeSelect.value;
    const additionalPc = parseInt(pcInput.value) || 0;
    
    if (!officeId) {
        showMessage('Please select an office', 'error');
        return;
    }
    
    closeModal();
    await performAction('declare_candidacy', {
        office_id: officeId,
        additional_pc: additionalPc
    });
}

async function handleSupportAction() {
    const legislationSelect = document.getElementById('support-legislation');
    const pcInput = document.getElementById('support-pc');
    
    const legislationId = legislationSelect.value;
    const pcAmount = parseInt(pcInput.value);
    
    if (!legislationId) {
        showMessage('Please select legislation to support', 'error');
        return;
    }
    
    if (!pcAmount || pcAmount <= 0) {
        showMessage('Please enter a valid PC amount', 'error');
        return;
    }
    
    closeModal();
    
    // NEW: Secret Commitment System - provide clear confirmation
    const legislationData = gameState.legislation_options[legislationId];
    const legislationTitle = legislationData ? legislationData.title : legislationId;
    
    showMessage(`🤫 Your secret commitment of ${pcAmount} PC to support "${legislationTitle}" has been registered. Other players will not see your stance until the reveal.`, 'success');
    
    await performAction('support_legislation', {
        legislation_id: legislationId,
        support_amount: pcAmount
    });
}

async function handleOpposeAction() {
    const legislationSelect = document.getElementById('oppose-legislation');
    const pcInput = document.getElementById('oppose-pc');
    
    const legislationId = legislationSelect.value;
    const pcAmount = parseInt(pcInput.value);
    
    if (!legislationId) {
        showMessage('Please select legislation to oppose', 'error');
        return;
    }
    
    if (!pcAmount || pcAmount <= 0) {
        showMessage('Please enter a valid PC amount', 'error');
        return;
    }
    
    closeModal();
    
    // NEW: Secret Commitment System - provide clear confirmation
    const legislationData = gameState.legislation_options[legislationId];
    const legislationTitle = legislationData ? legislationData.title : legislationId;
    
    showMessage(`🤫 Your secret commitment of ${pcAmount} PC to oppose "${legislationTitle}" has been registered. Other players will not see your stance until the reveal.`, 'success');
    
    await performAction('oppose_legislation', {
        legislation_id: legislationId,
        oppose_amount: pcAmount
    });
}

// Modal utilities
function showModal(title, content) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h3 class="modal-title">${title}</h3>
            </div>
            ${content}
        </div>
    `;
    
    modal.addEventListener('click', function(e) {
        if (e.target === modal) {
            closeModal();
        }
    });
    
    document.body.appendChild(modal);
}

function closeModal() {
    const modal = document.querySelector('.modal-overlay');
    if (modal) {
        modal.remove();
    }
}

// Message system
function showMessage(message, type = 'success') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.innerHTML = `
        <span class="message-icon">${getMessageIcon(type)}</span>
        <span class="message-text">${message}</span>
    `;
    
    document.body.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.remove();
    }, 3000);
}

function getMessageIcon(type) {
    const icons = {
        success: '✅',
        error: '❌',
        info: 'ℹ️'
    };
    return icons[type] || icons.info;
}

// Initial setup
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, simplified phase-based UI ready');
}); 