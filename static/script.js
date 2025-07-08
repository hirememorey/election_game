// Game state management
let gameId = null;
let gameState = null;

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
        
        gameId = result.game_id;
        gameState = result.state;
        
        showGameScreen();
        updateUi();
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
    if (!gameId) return;
    
    try {
        const result = await apiCall(`/game/${gameId}`);
        gameState = result.state;
        updateUi();
    } catch (error) {
        console.error('Failed to get game state:', error);
    }
}

async function performAction(actionType, additionalData = {}) {
    if (!gameId) return;
    
    try {
        const data = {
            action_type: actionType,
            player_id: gameState.players[gameState.current_player_index].id,
            ...additionalData
        };
        
        const result = await apiCall(`/game/${gameId}/action`, 'POST', data);
        gameState = result.state;
        updateUi();
    } catch (error) {
        console.error('Failed to perform action:', error);
    }
}

async function runEventPhase() {
    if (!gameId) return;
    
    try {
        if (runEventBtn) {
            runEventBtn.disabled = true;
            const btnText = runEventBtn.querySelector('.btn-text');
            if (btnText) btnText.textContent = 'Drawing Event...';
        }
        
        const result = await apiCall(`/game/${gameId}/event`, 'POST');
        gameState = result.state;
        updateUi();
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
    gameId = null;
    gameState = null;
    
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

function updateUi() {
    if (!gameState) return;

    renderIntelligenceBriefing();
    renderMainStage();
    renderPlayerDashboard();
}

function renderIntelligenceBriefing() {
    const briefingDiv = document.getElementById('intelligence-briefing');
    briefingDiv.innerHTML = ''; // Clear previous state

    gameState.players.forEach(player => {
        if (player.id !== gameState.players[gameState.current_player_index].id) {
            const opponentSummary = document.createElement('div');
            opponentSummary.className = 'opponent-summary';
            opponentSummary.innerHTML = `
                <h4>${player.name}</h4>
                <p>PC: ${player.pc}</p>
                <p>Favors: ${player.favors.length}</p>
                <p>Office: ${player.office || 'None'}</p>
            `;
            briefingDiv.appendChild(opponentSummary);
        }
    });

    const gameStatusTicker = document.getElementById('game-status-ticker');
    gameStatusTicker.innerHTML = `Round: ${gameState.round_marker} | Phase: ${gameState.current_phase} | Public Mood: ${gameState.public_mood}`;
}

function renderMainStage() {
    const actionList = document.getElementById('action-list');
    actionList.innerHTML = '';

    const availableActions = getAvailableActions(gameState.current_phase);
    availableActions.forEach(actionInfo => {
        const button = document.createElement('button');
        button.innerText = actionInfo.label;
        button.className = 'action-button';
        button.onclick = () => performAction(actionInfo.type, actionInfo.params);
        
        // Simple disabling logic for now
        const currentPlayer = gameState.players[gameState.current_player_index];
        const apLeft = gameState.action_points[currentPlayer.id];
        if (apLeft < (actionInfo.ap_cost || 1)) {
            button.disabled = true;
        }

        actionList.appendChild(button);
    });
    
    // Render game log
    const logDiv = document.getElementById('game-log');
    logDiv.innerHTML = gameState.log.map(entry => `<p>${entry}</p>`).join('');
    logDiv.scrollTop = logDiv.scrollHeight;
}

function renderPlayerDashboard() {
    const dashboardDiv = document.getElementById('player-dashboard');
    const currentPlayer = gameState.players[gameState.current_player_index];
    
    dashboardDiv.innerHTML = `
        <div class="dashboard-section">
            <h3>${currentPlayer.name} (${currentPlayer.archetype.name})</h3>
            <p>${currentPlayer.mandate.name}: ${currentPlayer.mandate.description}</p>
        </div>
        <div class="dashboard-section">
            <h3>PC: ${currentPlayer.pc}</h3>
        </div>
        <div class="dashboard-section">
            <h3>Action Points</h3>
            <div id="ap-meter"></div>
        </div>
        <div class="dashboard-section">
            <h3>Favors</h3>
            <p>${currentPlayer.favors.map(f => f.name).join(', ') || 'None'}</p>
        </div>
    `;

    const apMeter = document.getElementById('ap-meter');
    const totalAp = 3;
    const spentAp = totalAp - gameState.action_points[currentPlayer.id];

    for (let i = 0; i < totalAp; i++) {
        const pip = document.createElement('div');
        pip.className = 'ap-pip';
        if (i < spentAp) {
            pip.classList.add('spent');
        }
        apMeter.appendChild(pip);
    }
}

async function performAction(actionType, params = {}) {
    try {
        const response = await fetch(`/api/game/${gameId}/action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action_type: actionType,
                player_id: gameState.players[gameState.current_player_index].id,
                ...params,
            }),
        });
        const data = await response.json();
        gameId = data.game_id; // Corrected from data.id to data.game_id
        gameState = data.state;
        if (data.error) {
            alert(data.error);
            return;
        }
        updateUi();
    } catch (error) {
        console.error('Error performing action:', error);
    }
}

function getAvailableActions(phase) {
    // This function will be expanded to be more context-aware
    const actions = [
        { type: 'fundraise', label: 'Fundraise', ap_cost: 1 },
        { type: 'network', label: 'Network', ap_cost: 1 },
        { type: 'sponsor_legislation', label: 'Sponsor Legislation', ap_cost: 2, params: { legislation_id: 'INFRASTRUCTURE' } }, // Example param
        { type: 'declare_candidacy', label: 'Declare Candidacy', ap_cost: 2, params: { office_id: 'PRESIDENT' } }, // Example param
        { type: 'use_favor', label: 'Use Favor', ap_cost: 0 },
        { type: 'pass_turn', label: 'Pass Turn', ap_cost: 1}
    ];

    if (phase === 'ACTION_PHASE') {
        return actions;
    }
    // Add logic for other phases
    return [];
}

function updateTurnStatus() {
    const turnStatus = document.getElementById('turn-status');
    if (!turnStatus || !gameState) return;
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    const remainingAP = gameState.action_points?.[currentPlayer.id] || 3;
    const phase = gameState.current_phase;
    const round = gameState.round_marker;
    
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
                <span class="player-number">Player ${gameState.current_player_index + 1}</span>
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
    if (!gameState) return;
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    
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
    if (!pendingSection || !gameState) return;
    
    if (gameState.current_phase === 'LEGISLATION_PHASE' && gameState.term_legislation && gameState.term_legislation.length > 0) {
        pendingSection.classList.remove('hidden');
        pendingSection.innerHTML = `
            <div class="section-header">
                <h3>Pending Legislation</h3>
            </div>
            <div class="legislation-list">
                ${gameState.term_legislation.map(legislation => {
                    const bill = gameState.legislation_options[legislation.legislation_id];
                    const sponsor = gameState.players.find(p => p.id === legislation.sponsor_id);
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
    if (!favorsSection || !gameState) return;
    
    const currentPlayer = gameState.players[gameState.current_player_index];
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
    if (!logContent || !gameState) return;
    
    const logs = gameState.turn_log || [];
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
    const actionList = document.getElementById('action-list');
    if (!actionList || !gameState) return;
    
    actionList.innerHTML = '';
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    const remainingAP = gameState.action_points?.[currentPlayer.id] || 0;
    const phase = gameState.current_phase;
    
    // Show different UI based on game phase
    if (phase === 'LEGISLATION_PHASE' && gameState.legislation_session_active) {
        // Legislation session - show voting options
        showLegislationSessionUI();
        return;
    }
    
    // Normal action phase - show regular actions
    showRegularActionUI(remainingAP);
}

function showLegislationSessionUI() {
    const actionList = document.getElementById('action-list');
    
    // Add legislation session header
    const sessionHeader = document.createElement('div');
    sessionHeader.className = 'legislation-session-header';
    sessionHeader.innerHTML = `
        <div class="session-info">
            <h3>🗳️ Legislation Session</h3>
            <p>Vote on bills sponsored this term. Trading phase first, then voting.</p>
        </div>
    `;
    actionList.appendChild(sessionHeader);
    
    if (gameState.current_trade_phase) {
        // Trading phase
        showTradingPhaseUI();
    } else {
        // Voting phase
        showVotingPhaseUI();
    }
}

function showTradingPhaseUI() {
    const actionList = document.getElementById('action-list');
    
    const tradingHeader = document.createElement('div');
    tradingHeader.className = 'trading-phase-header';
    tradingHeader.innerHTML = `
        <div class="phase-info">
            <h4>🤝 Trading Phase</h4>
            <p>Propose trades for votes on legislation</p>
        </div>
    `;
    actionList.appendChild(tradingHeader);
    
    // Add trading actions
    const actions = [
        { type: 'propose_trade', label: 'Propose Trade', description: 'Offer PC/favors for votes' },
        { type: 'complete_trading', label: 'Skip Trading', description: 'Move to voting phase' }
    ];
    
    actions.forEach(action => {
        const button = document.createElement('button');
        button.className = 'action-button trading-action';
        button.innerHTML = `
            <div class="action-label">${action.label}</div>
            <div class="action-description">${action.description}</div>
        `;
        button.onclick = () => handleActionClick(action.type);
        actionList.appendChild(button);
    });
}

function showVotingPhaseUI() {
    const actionList = document.getElementById('action-list');
    
    const votingHeader = document.createElement('div');
    votingHeader.className = 'voting-phase-header';
    votingHeader.innerHTML = `
        <div class="phase-info">
            <h4>🗳️ Voting Phase</h4>
            <p>Vote on legislation</p>
        </div>
    `;
    actionList.appendChild(votingHeader);
    
    // Show legislation to vote on
    if (gameState.term_legislation && gameState.term_legislation.length > 0) {
        gameState.term_legislation.forEach(legislation => {
            if (!legislation.resolved) {
                const legislationCard = document.createElement('div');
                legislationCard.className = 'legislation-card';
                legislationCard.innerHTML = `
                    <div class="legislation-info">
                        <h5>${legislation.title}</h5>
                        <p>${legislation.description}</p>
                        <p><strong>Sponsored by:</strong> ${gameState.players[legislation.sponsor_id].name}</p>
                    </div>
                    <div class="voting-actions">
                        <button onclick="performAction('support_legislation', {legislation_id: '${legislation.id}', support_amount: 1})" class="vote-btn support-btn">
                            Support
                        </button>
                        <button onclick="performAction('oppose_legislation', {legislation_id: '${legislation.id}', oppose_amount: 1})" class="vote-btn oppose-btn">
                            Oppose
                        </button>
                    </div>
                `;
                actionList.appendChild(legislationCard);
            }
        });
    } else {
        const noLegislation = document.createElement('div');
        noLegislation.className = 'no-legislation';
        noLegislation.innerHTML = `
            <p>No legislation to vote on. Moving to elections.</p>
        `;
        actionList.appendChild(noLegislation);
    }
}

function showRegularActionUI(remainingAP) {
    const actionList = document.getElementById('action-list');
    
    // Add AP display
    const apDisplay = document.createElement('div');
    apDisplay.className = 'action-points-display';
    apDisplay.innerHTML = `
        <div class="ap-info">
            <span class="ap-icon">⚡</span>
            <span class="ap-text">${remainingAP}/3 Action Points</span>
        </div>
    `;
    actionList.appendChild(apDisplay);
    
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
    
    // Show available actions
    const actions = [
        { type: 'fundraise', label: 'Fundraise', description: 'Gain Political Capital' },
        { type: 'network', label: 'Network', description: 'Gain PC and political favors' },
        { type: 'sponsor_legislation', label: 'Sponsor Legislation', description: 'Create legislation for votes/mood' },
        { type: 'campaign', label: 'Campaign', description: 'Place influence for future elections' },
        { type: 'use_favor', label: 'Use Favor', description: 'Strategic advantage actions' }
    ];
    
    // Only show declare candidacy in round 4
    if (gameState.round_marker === 4) {
        actions.push({ type: 'declare_candidacy', label: 'Declare Candidacy', description: 'Run for office' });
    }
    
    actions.forEach(action => {
        const apCost = actionCosts[action.type] || 0;
        const canAfford = remainingAP >= apCost;
        
        const button = document.createElement('button');
        button.className = `action-button ${canAfford ? '' : 'disabled'}`;
        button.disabled = !canAfford;
        button.innerHTML = `
            <div class="action-label">${action.label}</div>
            <div class="action-cost">${apCost} AP</div>
            <div class="action-description">${action.description}</div>
        `;
        
        if (!canAfford) {
            button.title = `Not enough Action Points. Need ${apCost}, have ${remainingAP}`;
        }
        
        button.onclick = () => handleActionClick(action.type);
        actionList.appendChild(button);
    });
    
    // Add Pass Turn button if no AP left
    if (remainingAP === 0) {
        const passButton = document.createElement('button');
        passButton.className = 'action-button pass-turn-btn';
        passButton.innerHTML = `
            <div class="action-label">Pass Turn</div>
            <div class="action-cost">0 AP</div>
            <div class="action-description">End your turn</div>
        `;
        passButton.onclick = () => handleActionClick('pass_turn');
        actionList.appendChild(passButton);
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
        case 'complete_trading':
            performAction('complete_trading');
            break;
        case 'pass_turn':
            performAction('pass_turn');
            break;
        default:
            console.log('Unknown action type:', actionType);
    }
}

function updateEventPhaseButton() {
    if (!eventPhaseSection || !gameState) return;
    
    if (gameState.current_phase === 'event_phase') {
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
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    const modal = document.createElement('div');
    modal.id = 'legislation-menu';
    modal.className = 'legislation-menu';
    
    modal.innerHTML = `
        <h3>Choose Legislation to Sponsor</h3>
        <div class="legislation-options">
            ${Object.values(gameState.legislation_options).map(leg => `
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
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    const modal = document.createElement('div');
    modal.id = 'favor-menu';
    modal.className = 'favor-menu';
    
    modal.innerHTML = `
        <h3>Choose a Favor to Use</h3>
        <div class="favor-options">
            ${currentPlayer.favors.map(favor => {
                const isNegative = favor.id.startsWith('POLITICAL_DEBT') || 
                                  favor.id.startsWith('PUBLIC_GAFFE') || 
                                  favor.id.startsWith('MEDIA_SCRUTINY') || 
                                  favor.id.startsWith('COMPROMISING_POSITION') || 
                                  favor.id.startsWith('POLITICAL_HOT_POTATO');
                
                return `
                    <button class="favor-option ${isNegative ? 'negative-favor' : ''}" 
                            data-favor-id="${favor.id}" 
                            data-favor-description="${favor.description}"
                            data-is-negative="${isNegative}">
                        <div><strong>${favor.description}</strong></div>
                        ${isNegative ? '<div class="negative-indicator">⚠️ Negative Effect</div>' : ''}
                    </button>
                `;
            }).join('')}
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
            const isNegative = button.dataset.isNegative === 'true';
            
            // Handle different types of favors
            if (favorId === 'COMPROMISING_POSITION') {
                showCompromisingPositionChoice(favorId, favorDescription, overlay);
            } else if (favorDescription.includes('Target player') || 
                      favorDescription.includes('Choose one player') ||
                      favorDescription.includes('pass this card to another player')) {
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

function showCompromisingPositionChoice(favorId, favorDescription, parentOverlay) {
    // Remove the parent modal
    parentOverlay.remove();
    
    // Create new modal for choice selection
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    const modal = document.createElement('div');
    modal.className = 'campaign-modal';
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    
    modal.innerHTML = `
        <h3>Compromising Position</h3>
        <p>${favorDescription}</p>
        
        <div class="form-group">
            <label>Choose your response:</label>
            <div class="choice-options">
                <button class="choice-btn" data-choice="discard_favors">
                    <strong>Discard Two Political Favors</strong>
                    <div class="choice-desc">Lose two of your political favors to keep your archetype secret.</div>
                </button>
                <button class="choice-btn" data-choice="reveal_archetype">
                    <strong>Reveal Your Archetype</strong>
                    <div class="choice-desc">All players will know your archetype and its special abilities.</div>
                </button>
            </div>
        </div>
        
        <div class="modal-buttons">
            <button class="btn-secondary cancel-btn">Cancel</button>
        </div>
    `;
    
    // Add event listeners
    modal.querySelectorAll('.choice-btn').forEach(button => {
        button.addEventListener('click', () => {
            const choice = button.dataset.choice;
            
            performAction('use_favor', { 
                favor_id: favorId,
                choice: choice
            });
            
            overlay.remove();
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
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    const otherPlayers = gameState.players.filter(p => p.id !== currentPlayer.id);
    
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
    if (!gameState || !gameState.term_legislation) return;
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    const availableLegislation = gameState.term_legislation.filter(l => 
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
                const bill = gameState.legislation_options[legislation.legislation_id];
                const sponsor = gameState.players.find(p => p.id === legislation.sponsor_id);
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
    if (!gameState || !gameState.term_legislation) return;
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    const availableLegislation = gameState.term_legislation.filter(l => 
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
                const bill = gameState.legislation_options[legislation.legislation_id];
                const sponsor = gameState.players.find(p => p.id === legislation.sponsor_id);
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
    const currentPlayer = gameState.players[gameState.current_player_index];
    
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
    if (!gameState || !gameState.term_legislation) return;
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    const availableLegislation = gameState.term_legislation.filter(l => 
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
                    const bill = gameState.legislation_options[legislation.legislation_id];
                    const sponsor = gameState.players.find(p => p.id === legislation.sponsor_id);
                    return `<option value="${legislation.legislation_id}">${bill.title} (${sponsor.name})</option>`;
                }).join('')}
            </select>
        </div>
        
        <div class="form-group">
            <label for="trade-target-player">Target Player:</label>
            <select id="trade-target-player" required>
                <option value="">Choose player...</option>
                ${gameState.players
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
    const currentPlayer = gameState.players[gameState.current_player_index];
    
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
                ${Object.values(gameState.offices || {}).map(office => {
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
        
        const office = gameState.offices[officeId];
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
    // Correctly wire up the buttons
    document.getElementById('start-game-button').addEventListener('click', startGame);
    document.getElementById('add-player-button').addEventListener('click', addPlayerInput);

    // Initial setup with 2 players
    const playerInputs = document.getElementById('player-inputs');
    playerInputs.innerHTML = ''; // Clear existing
    addPlayerInput();
    addPlayerInput();
}); 