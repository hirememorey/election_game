// Simplified Phase-Based UI for Election Game

// Game state management
let gameId = null;
let gameState = null;

// Simplified API URL logic - works for both local development and production
function getApiBaseUrl() {
    // If we're on the same hostname as the current page, use the same port
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        // Local development - use port 5001
        return `${window.location.protocol}//${window.location.hostname}:5001/api`;
    } else {
        // Production (Render) - use the same hostname and port as the current page
        return `${window.location.protocol}//${window.location.host}/api`;
    }
}

const API_BASE_URL = getApiBaseUrl();

// Debug logging
console.log('API_BASE_URL:', API_BASE_URL);
console.log('Current location:', window.location.href);

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

// DOM elements - will be initialized after DOM loads
let setupScreen, gameScreen, startGameBtn, newGameBtn, playerForm;
let phaseIndicator, actionContent, primaryActions, quickAccessPanel;

// Initialize DOM elements
function initializeDOMElements() {
    console.log('Initializing DOM elements...');
    setupScreen = document.getElementById('setup-screen');
    gameScreen = document.getElementById('game-screen');
    startGameBtn = document.getElementById('start-game-btn');
    newGameBtn = document.getElementById('new-game-btn');
    playerForm = document.getElementById('player-form');
    
    // Phase-based UI elements
    phaseIndicator = document.getElementById('phase-indicator');
    actionContent = document.getElementById('action-content');
    primaryActions = document.getElementById('primary-actions');
    quickAccessPanel = document.getElementById('quick-access-panel');
    
    console.log('DOM elements initialized:', {
        setupScreen: !!setupScreen,
        gameScreen: !!gameScreen,
        startGameBtn: !!startGameBtn,
        newGameBtn: !!newGameBtn,
        playerForm: !!playerForm,
        phaseIndicator: !!phaseIndicator,
        actionContent: !!actionContent,
        primaryActions: !!primaryActions,
        quickAccessPanel: !!quickAccessPanel
    });
}

// Event listeners
function setupEventListeners() {
    console.log('Setting up event listeners...');
    if (startGameBtn) {
        startGameBtn.addEventListener('click', startNewGame);
        console.log('Start game button listener added');
    }
    if (newGameBtn) {
        newGameBtn.addEventListener('click', showSetupScreen);
        console.log('New game button listener added');
    }
    if (playerForm) {
        playerForm.addEventListener('submit', function(e) {
            e.preventDefault();
            startNewGame();
        });
        console.log('Player form listener added');
    }
}

// Menu dropdown functionality
let menuBtn, menuDropdown, infoBtn, identityBtn;

function setupMenuDropdown() {
    console.log('Setting up menu dropdown...');
    menuBtn = document.getElementById('menu-btn');
    menuDropdown = document.getElementById('menu-dropdown');
    infoBtn = document.getElementById('info-btn');
    identityBtn = document.getElementById('identity-btn');

    if (menuBtn) {
        menuBtn.addEventListener('click', function() {
            menuDropdown.classList.toggle('hidden');
        });
        console.log('Menu button listener added');
    }

    if (infoBtn) {
        infoBtn.addEventListener('click', function() {
            showQuickAccess();
        });
        console.log('Info button listener added');
    }

    if (identityBtn) {
        identityBtn.addEventListener('click', function() {
            showIdentityInfo();
        });
        console.log('Identity button listener added');
    }
}

// Close menu when clicking outside
document.addEventListener('click', function(e) {
    if (menuDropdown && !menuBtn.contains(e.target) && !menuDropdown.contains(e.target)) {
        menuDropdown.classList.add('hidden');
    }
});

// Swipe gesture handling - ENABLED ON MOBILE
let touchStartY = 0;
let touchEndY = 0;

// Enable swipe gestures on all devices
function isMobileDevice() {
    return window.innerWidth <= 600;
}

document.addEventListener('touchstart', function(e) {
    // Enable swipe gestures on all devices
    touchStartY = e.changedTouches[0].screenY;
    console.log('Touch start:', touchStartY);
});

document.addEventListener('touchend', function(e) {
    // Enable swipe gestures on all devices
    touchEndY = e.changedTouches[0].screenY;
    console.log('Touch end:', touchEndY);
    handleSwipe();
});

function handleSwipe() {
    const swipeThreshold = 50;
    const swipeDistance = touchStartY - touchEndY;
    
    console.log('Swipe distance:', swipeDistance);
    
    if (swipeDistance > swipeThreshold) {
        // Swipe up - show quick access panel
        console.log('Swipe up detected - showing quick access panel');
        showQuickAccess();
    } else if (swipeDistance < -swipeThreshold) {
        // Swipe down - hide quick access panel
        console.log('Swipe down detected - hiding quick access panel');
        hideQuickAccess();
    }
}

function showQuickAccess() {
    console.log('showQuickAccess called');
    if (quickAccessPanel) {
        console.log('Quick access panel found, showing...');
        quickAccessPanel.classList.add('show');
        updateQuickAccessContent();
    } else {
        console.log('Quick access panel not found');
    }
}

function hideQuickAccess() {
    console.log('hideQuickAccess called');
    if (quickAccessPanel) {
        console.log('Quick access panel found, hiding...');
        quickAccessPanel.classList.remove('show');
    } else {
        console.log('Quick access panel not found');
    }
}

// Close quick access panel when clicking outside
document.addEventListener('click', function(e) {
    if (quickAccessPanel && quickAccessPanel.classList.contains('show') && 
        !quickAccessPanel.contains(e.target) && 
        infoBtn && !infoBtn.contains(e.target)) {
        hideQuickAccess();
    }
});

// Close quick access panel with escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape' && quickAccessPanel && quickAccessPanel.classList.contains('show')) {
        hideQuickAccess();
    }
});

function updateGameLog() {
    if (!gameState) return;
    const gameLogDiv = document.getElementById('game-log');
    if (!gameLogDiv) return;
    const log = gameState.turn_log || [];
    if (log.length === 0) {
        gameLogDiv.innerHTML = '<div class="game-log-entry">No game events yet.</div>';
    } else {
        // Show only the latest log entry and a 'More' button
        const latestEntry = log[log.length - 1];
        gameLogDiv.innerHTML = `
            <div class="game-log-entry single-line">${latestEntry}</div>
            <button class="btn-secondary btn-small more-log-btn" onclick="showFullGameLog()" aria-label="Show Full Game Log">More</button>
        `;
    }
}

function showFullGameLog() {
    if (!gameState) return;
    const log = gameState.turn_log || [];
    let content = '';
    if (log.length === 0) {
        content = '<div class="game-log-entry">No game events yet.</div>';
    } else {
        content = log.map(entry => `<div class="game-log-entry">${entry}</div>`).join('');
    }
    showModal('Game Log', `<div style='max-height:60vh;overflow-y:auto;'>${content}</div><div class='modal-actions'><button class='btn-secondary' onclick='closeModal()'>Close</button></div>`);
}

function updateQuickAccessContent() {
    if (!gameState || !quickAccessPanel) return;
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    const log = gameState.turn_log || [];
    
    let content = '<div class="identity-section">';
    content += '<h3>Your Identity</h3>';
    
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
    
    // Add game log section
    content += '<div class="log-section">';
    content += '<h3>Game Log</h3>';
    if (log.length === 0) {
        content += '<div class="game-log-entry">No game events yet.</div>';
    } else {
        // Show the last 10 log entries for mobile
        const entries = log.slice(-10).map(entry => `<div class="game-log-entry">${entry}</div>`).join('');
        content += entries;
    }
    content += '</div>';
    
    const quickAccessContent = document.getElementById('quick-access-content');
    if (quickAccessContent) {
        quickAccessContent.innerHTML = content;
    }
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
    console.log('Setting up quick access panel...');
    
    // Setup close button
    const closeButton = document.getElementById('close-quick-access');
    if (closeButton) {
        closeButton.addEventListener('click', hideQuickAccess);
        console.log('Close button listener added');
    }
    
    // Setup info button to show quick access panel
    const infoButton = document.getElementById('info-btn');
    if (infoButton) {
        infoButton.addEventListener('click', showQuickAccess);
        console.log('Info button listener added');
    }
    
    // Setup quick access panel click outside to close
    if (quickAccessPanel) {
        quickAccessPanel.addEventListener('click', function(e) {
            if (e.target === quickAccessPanel) {
                hideQuickAccess();
            }
        });
        console.log('Quick access panel click outside listener added');
    }
    
    // Ensure the panel is hidden initially
    if (quickAccessPanel) {
        quickAccessPanel.classList.remove('show');
    }
}

// Initialize everything when DOM is loaded
window.addEventListener('DOMContentLoaded', function() {
    console.log('DOM loaded, initializing...');
    initializeDOMElements();
    setupEventListeners();
    setupMenuDropdown();
    setupQuickAccessPanel();
    console.log('Initialization complete');
});

// API functions
let isApiCallInProgress = false;

async function apiCall(endpoint, method = 'GET', data = null) {
    if (isApiCallInProgress) {
        console.warn('API call already in progress. Ignoring new request.');
        return null; // Or throw an error, or handle as needed
    }

    isApiCallInProgress = true;
    console.log(`API Call Start: ${method} ${endpoint}`, data);
    try {
        const url = `${API_BASE_URL}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };
        if (data) {
            options.body = JSON.stringify(data);
        }
        const response = await fetch(url, options);
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({ error: 'An unknown error occurred' }));
            console.error('API Error:', response.status, errorData);
            showMessage(errorData.error, 'error');
            return null;
        }
        const responseData = await response.json();
        console.log('API Response:', responseData);
        return responseData;
    } catch (error) {
        console.error('Network or API call error:', error);
        showMessage('Could not connect to the server. Please check your connection.', 'error');
        return null;
    } finally {
        isApiCallInProgress = false;
        console.log(`API Call End: ${method} ${endpoint}`);
    }
}

// Game functions
async function startNewGame() {
    console.log('Attempting to start a new game...');
    const playerInputs = Array.from(document.querySelectorAll('.player-inputs input[type="text"]'));
    const playerNames = playerInputs
        .map(input => input.value.trim())
        .filter(name => name.length > 0);

    if (playerNames.length < 2) {
        showMessage('Please enter at least two player names.', 'error');
        return;
    }

    // Disable the button to prevent multiple clicks
    if(startGameBtn) {
        startGameBtn.disabled = true;
        startGameBtn.textContent = 'Starting...';
    }

    const data = await apiCall('/game', 'POST', { player_names: playerNames });

    // Re-enable the button regardless of outcome
    if(startGameBtn) {
        startGameBtn.disabled = false;
        startGameBtn.textContent = 'Start Game';
    }

    if (data && data.game_id) {
        gameId = data.game_id;
        gameState = data.state;
        showGameScreen();
        updatePhaseUI();
        announceToScreenReader('Game started successfully. It is now ' + gameState.players[gameState.current_player_index].name + "'s turn.");
    } else {
        showMessage('Failed to start the game. Please try again.', 'error');
        // Do not hide the setup screen if the game fails to start
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
        console.log('Action result:', result);
        gameState = result.state;
        console.log('Updated game state PC:', gameState.players[gameState.current_player_index].pc);
        updatePhaseUI();
    } catch (error) {
        console.error('Failed to perform action:', error);
        showMessage(`Action failed: ${error.message}`, 'error');
    }
}

// UI functions
function showSetupScreen() {
    console.log('showSetupScreen called');
    if (setupScreen) {
        setupScreen.classList.remove('hidden');
        console.log('Setup screen shown');
    }
    if (gameScreen) {
        gameScreen.classList.add('hidden');
        console.log('Game screen hidden');
    }
    // Reset game state
    gameId = null;
    gameState = null;
}

function showGameScreen() {
    console.log('showGameScreen called');
    console.log('setupScreen element:', setupScreen);
    console.log('gameScreen element:', gameScreen);
    
    if (setupScreen) {
        setupScreen.classList.add('hidden');
        console.log('Setup screen hidden, classes:', setupScreen.className);
    } else {
        console.error('setupScreen element not found!');
    }
    
    if (gameScreen) {
        gameScreen.classList.remove('hidden');
        console.log('Game screen shown, classes:', gameScreen.className);
    } else {
        console.error('gameScreen element not found!');
    }
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
    const ap = gameState.action_points[currentPlayer.id.toString()] || 0;
    
    actionContent.innerHTML = `
        <div class="text-center">
            <h3>Action Phase</h3>
            <p>You have ${ap} action points remaining.</p>
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
    // Parse the game log to extract election results
    const electionResults = parseElectionResults();
    
    if (electionResults.length === 0) {
        actionContent.innerHTML = `
            <div class="text-center">
                <h3>Election Phase</h3>
                <p>No elections were held this term.</p>
            </div>
        `;
        return;
    }
    
    const resultsHTML = electionResults.map(result => `
        <div class="election-result">
            <div class="election-header">
                <h4>🏛️ ${result.office}</h4>
            </div>
            <div class="election-candidates">
                ${result.candidates.map(candidate => `
                    <div class="candidate-result ${candidate.winner ? 'winner' : 'loser'}">
                        <div class="candidate-name">${candidate.name}</div>
                        <div class="candidate-details">
                            <div class="roll-info">
                                <span class="dice">🎲 ${candidate.roll}</span>
                                <span class="bonus">+${candidate.bonus} (PC)</span>
                                <span class="total">= ${candidate.total}</span>
                            </div>
                            <div class="pc-committed">Committed: ${candidate.committedPC} PC</div>
                        </div>
                        ${candidate.winner ? '<div class="winner-badge">👑 Winner!</div>' : ''}
                    </div>
                `).join('')}
            </div>
            ${result.tiebreaker ? `<div class="tiebreaker-info">${result.tiebreaker}</div>` : ''}
        </div>
    `).join('');
    
    actionContent.innerHTML = `
        <div class="election-results-container">
            <div class="election-results-header">
                <h3>🗳️ Election Results</h3>
                <p>Here are the detailed results from this term's elections:</p>
            </div>
            <div class="election-results-list">
                ${resultsHTML}
            </div>
        </div>
    `;
}

function parseElectionResults() {
    if (!gameState || !gameState.turn_log) return [];
    
    const results = [];
    const log = gameState.turn_log;
    let currentElection = null;
    
    for (let i = 0; i < log.length; i++) {
        const entry = log[i];
        
        // Look for election resolution headers
        if (entry.includes('--- Resolving Election for')) {
            const officeMatch = entry.match(/--- Resolving Election for (.+) ---/);
            if (officeMatch) {
                if (currentElection) {
                    results.push(currentElection);
                }
                currentElection = {
                    office: officeMatch[1],
                    candidates: [],
                    tiebreaker: null
                };
            }
        }
        
        // Look for candidate results
        if (currentElection && entry.includes("'s Score:")) {
            const scoreMatch = entry.match(/(.+)'s Score: (\d+) \(d6\) \+ (\d+) \(PC bonus\) = (\d+)/);
            if (scoreMatch) {
                const [, name, roll, bonus, total] = scoreMatch;
                currentElection.candidates.push({
                    name: name.trim(),
                    roll: parseInt(roll),
                    bonus: parseInt(bonus),
                    total: parseInt(total),
                    committedPC: 0, // Will be filled from previous log entry
                    winner: false
                });
            }
        }
        
        // Look for committed PC reveals
        if (currentElection && entry.includes('reveals') && entry.includes('committed PC')) {
            const pcMatch = entry.match(/(.+) reveals (\d+) committed PC/);
            if (pcMatch) {
                const [, name, pc] = pcMatch;
                const candidate = currentElection.candidates.find(c => c.name === name.trim());
                if (candidate) {
                    candidate.committedPC = parseInt(pc);
                }
            }
        }
        
        // Look for NPC challenger results
        if (currentElection && entry.includes("NPC Challenger's Score:")) {
            const npcMatch = entry.match(/NPC Challenger's Score: (\d+) \(d6\) \+ (\d+) \(NPC bonus\) = (\d+)/);
            if (npcMatch) {
                const [, roll, bonus, total] = npcMatch;
                currentElection.candidates.push({
                    name: 'NPC Challenger',
                    roll: parseInt(roll),
                    bonus: parseInt(bonus),
                    total: parseInt(total),
                    committedPC: 0,
                    winner: false
                });
            }
        }
        
        // Look for winners
        if (currentElection && entry.includes('wins the election for')) {
            const winnerMatch = entry.match(/(.+) wins the election for/);
            if (winnerMatch) {
                const winnerName = winnerMatch[1].trim();
                const candidate = currentElection.candidates.find(c => c.name === winnerName);
                if (candidate) {
                    candidate.winner = true;
                }
            }
        }
        
        // Look for losers
        if (currentElection && entry.includes('loses the election')) {
            const loserMatch = entry.match(/(.+) loses the election/);
            if (loserMatch) {
                const loserName = loserMatch[1].trim();
                const candidate = currentElection.candidates.find(c => c.name === loserName);
                if (candidate) {
                    candidate.winner = false;
                }
            }
        }
        
        // Look for tiebreaker information
        if (currentElection && (entry.includes('Tie in score') || entry.includes('Still tied'))) {
            currentElection.tiebreaker = entry;
        }
    }
    
    // Add the last election if it exists
    if (currentElection) {
        results.push(currentElection);
    }
    
    return results;
}

function updatePrimaryActions() {
    if (!gameState || !primaryActions) return;
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    const availableActions = getAvailableActions(currentPlayer);
    
    primaryActions.innerHTML = '';
    
    // Add Pass Turn button
    const passButton = document.createElement('button');
    passButton.className = 'btn-secondary';
    passButton.textContent = 'Pass Turn';
    passButton.setAttribute('aria-label', 'Pass turn to next player');
    passButton.onclick = passTurn;
    primaryActions.appendChild(passButton);
    
    // Add action buttons
    availableActions.forEach(action => {
        const button = document.createElement('button');
        button.className = 'action-btn';
        button.setAttribute('data-action', action.type);
        button.setAttribute('aria-label', `${action.label} - Cost: ${action.cost} Action Points`);
        
        const icon = document.createElement('span');
        icon.className = 'action-icon';
        icon.textContent = action.icon;
        icon.setAttribute('aria-hidden', 'true');
        
        const label = document.createElement('span');
        label.className = 'action-label';
        label.textContent = action.label;
        
        const cost = document.createElement('span');
        cost.className = 'action-cost';
        cost.textContent = `${action.cost} AP`;
        cost.setAttribute('aria-hidden', 'true');
        
        button.appendChild(icon);
        button.appendChild(label);
        button.appendChild(cost);
        button.onclick = () => handleActionClick(action.type);
        
        primaryActions.appendChild(button);
    });
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
    const log = gameState.turn_log || [];

    let content = '<div class="identity-section">';
    content += '<h3>Your Identity</h3>';

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

    // Add game log section
    content += '<div class="log-section">';
    content += '<h3>Game Log</h3>';
    if (log.length === 0) {
        content += '<div class="game-log-entry">No game events yet.</div>';
    } else {
        // Show the last 10 log entries for mobile
        const entries = log.slice(-10).map(entry => `<div class="game-log-entry">${entry}</div>`).join('');
        content += entries;
    }
    content += '</div>';

    if (isMobileDevice()) {
        // Show in quick access panel for mobile
        if (quickAccessPanel) {
            const quickAccessContent = document.getElementById('quick-access-content');
            if (quickAccessContent) {
                quickAccessContent.innerHTML = content;
                showQuickAccess();
            } else {
                showModal('Game Information', content);
            }
        } else {
            showModal('Game Information', content);
        }
    } else {
        // Always use modal for desktop
        showModal('Game Information', content);
    }
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
                <button class="close-btn" aria-label="Close" onclick="closeModal()">×</button>
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
    initializeDOMElements();
    setupEventListeners();
    setupMenuDropdown();
    setupQuickAccessPanel();
});