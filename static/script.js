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

// DOM elements - updated to match HTML structure
const setupScreen = document.getElementById('setup-screen');
const gameScreen = document.getElementById('game-screen');
const startGameBtn = document.getElementById('start-game-btn'); // Fixed ID
const newGameBtn = document.getElementById('new-game-btn');
const runEventBtn = document.getElementById('run-event-btn');
const playerForm = document.getElementById('player-form');

// Manual resolution elements
const manualResolutionSection = document.getElementById('manual-resolution-section');
const resolveLegislationBtn = document.getElementById('resolve-legislation-btn');
const resolveElectionsBtn = document.getElementById('resolve-elections-btn');

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

// Event listeners - updated to match actual HTML structure
if (startGameBtn) {
    console.log('Start game button found, adding click listener');
    startGameBtn.addEventListener('click', startNewGame); // Fixed function name
} else {
    console.error('Start game button not found');
}
if (newGameBtn) {
    newGameBtn.addEventListener('click', showSetupScreen);
}
if (runEventBtn) {
    runEventBtn.addEventListener('click', runEventPhase);
}
if (playerForm) {
    console.log('Player form found, adding submit listener');
    playerForm.addEventListener('submit', function(e) {
        console.log('Form submitted');
        e.preventDefault();
        startNewGame(); // Fixed function name
    });
} else {
    console.error('Player form not found');
}
if (clearLogBtn) {
    clearLogBtn.addEventListener('click', clearGameLog);
}

// Manual resolution event listeners
if (resolveLegislationBtn) {
    resolveLegislationBtn.addEventListener('click', resolveLegislation);
}
if (resolveElectionsBtn) {
    resolveElectionsBtn.addEventListener('click', resolveElections);
}

// Initial setup when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, game ready');
});

// Player input handling is done via the form structure

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
        updateUi();
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
        updateUi();
    } catch (error) {
        console.error('Failed to get game state:', error);
    }
}

async function performAction(actionType, additionalData = {}) {
    if (!gameId) return;
    
    // Check if gameState is available
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

// Manual resolution functions
async function resolveLegislation() {
    if (!gameId) return;
    
    try {
        if (resolveLegislationBtn) {
            resolveLegislationBtn.disabled = true;
            const btnText = resolveLegislationBtn.querySelector('.btn-text');
            if (btnText) btnText.textContent = 'Resolving...';
        }
        
        console.log('Resolving legislation...');
        const result = await apiCall(`/game/${gameId}/resolve_legislation`, 'POST');
        gameState = result.state;
        updateUi();
        
        showMessage('Legislation resolved successfully!', 'success');
    } catch (error) {
        console.error('Failed to resolve legislation:', error);
        showMessage(`Failed to resolve legislation: ${error.message}`, 'error');
    } finally {
        if (resolveLegislationBtn) {
            resolveLegislationBtn.disabled = false;
            const btnText = resolveLegislationBtn.querySelector('.btn-text');
            if (btnText) btnText.textContent = 'Resolve Legislation';
        }
    }
}

async function resolveElections() {
    if (!gameId) return;
    
    try {
        if (resolveElectionsBtn) {
            resolveElectionsBtn.disabled = true;
            const btnText = resolveElectionsBtn.querySelector('.btn-text');
            if (btnText) btnText.textContent = 'Resolving...';
        }
        
        console.log('Resolving elections...');
        const result = await apiCall(`/game/${gameId}/resolve_elections`, 'POST');
        gameState = result.state;
        updateUi();
        
        showMessage('Elections resolved successfully!', 'success');
    } catch (error) {
        console.error('Failed to resolve elections:', error);
        showMessage(`Failed to resolve elections: ${error.message}`, 'error');
    } finally {
        if (resolveElectionsBtn) {
            resolveElectionsBtn.disabled = false;
            const btnText = resolveElectionsBtn.querySelector('.btn-text');
            if (btnText) btnText.textContent = 'Resolve Elections';
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
    const form = document.getElementById('player-form');
    if (form) {
        form.reset();
    }
}

function showGameScreen() {
    if (setupScreen) setupScreen.classList.add('hidden');
    if (gameScreen) gameScreen.classList.remove('hidden');
}

function updateUi() {
    if (!gameState) return;
    
    // Safety check for required game state properties
    if (!gameState.players || !Array.isArray(gameState.players) || gameState.players.length === 0) {
        console.error('Game state missing players array');
        return;
    }
    
    if (typeof gameState.current_player_index !== 'number' || gameState.current_player_index < 0 || gameState.current_player_index >= gameState.players.length) {
        console.error('Invalid current player index:', gameState.current_player_index);
        return;
    }

    renderIntelligenceBriefing();
    renderMainStage();
    renderPlayerDashboard();
    updatePendingLegislationDisplay(); // Call this function here
    updateCompactGameStateBar(); // Add this new function call
    
    // Update manual resolution buttons visibility
    updateManualResolutionButtons();
}

function updateCompactGameStateBar() {
    if (!gameState) return;
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    const remainingAP = gameState.action_points?.[currentPlayer.id] || 2;
    
    // Update compact player info
    const playerNameCompact = document.getElementById('current-player-name-compact');
    const playerPcCompact = document.getElementById('current-player-pc-compact');
    const playerOfficeCompact = document.getElementById('current-player-office-compact');
    const playerAvatarCompact = document.getElementById('current-player-avatar-compact');
    
    if (playerNameCompact) {
        playerNameCompact.textContent = currentPlayer.name;
    }
    if (playerPcCompact) {
        playerPcCompact.textContent = currentPlayer.pc || 0;
    }
    if (playerOfficeCompact) {
        playerOfficeCompact.textContent = currentPlayer.office || 'None';
    }
    if (playerAvatarCompact) {
        playerAvatarCompact.textContent = getPlayerAvatar(currentPlayer);
    }
    
    // Update compact game meta
    const roundInfoCompact = document.getElementById('round-info-compact');
    const phaseInfoCompact = document.getElementById('phase-info-compact');
    const moodInfoCompact = document.getElementById('mood-info-compact');
    
    if (roundInfoCompact) {
        roundInfoCompact.textContent = `Round ${gameState.round_marker || 1}`;
    }
    if (phaseInfoCompact) {
        phaseInfoCompact.textContent = formatPhase(gameState.current_phase || 'Unknown');
    }
    if (moodInfoCompact) {
        moodInfoCompact.textContent = `Mood: ${formatMood(gameState.public_mood || 0)}`;
    }
    
    // Update compact action points
    const actionPointsCompact = document.getElementById('action-points-compact');
    if (actionPointsCompact) {
        const apTextCompact = actionPointsCompact.querySelector('.ap-text-compact');
        if (apTextCompact) {
            apTextCompact.textContent = `${remainingAP}/2 AP`;
        }
    }
}

function updateManualResolutionButtons() {
    if (!gameState || !manualResolutionSection) return;
    
    // Check if we should show the manual resolution section
    const shouldShowLegislation = gameState.awaiting_legislation_resolution === true;
    const shouldShowElections = gameState.awaiting_election_resolution === true;
    
    console.log('Manual resolution flags:', {
        awaiting_legislation_resolution: gameState.awaiting_legislation_resolution,
        awaiting_election_resolution: gameState.awaiting_election_resolution
    });
    
    if (shouldShowLegislation || shouldShowElections) {
        // Show the manual resolution section
        manualResolutionSection.classList.remove('hidden');
        
        // Show/hide individual buttons based on flags
        if (resolveLegislationBtn) {
            if (shouldShowLegislation) {
                resolveLegislationBtn.classList.remove('hidden');
                resolveLegislationBtn.disabled = false;
            } else {
                resolveLegislationBtn.classList.add('hidden');
            }
        }
        
        if (resolveElectionsBtn) {
            if (shouldShowElections) {
                resolveElectionsBtn.classList.remove('hidden');
                resolveElectionsBtn.disabled = false;
            } else {
                resolveElectionsBtn.classList.add('hidden');
            }
        }
        
        // Hide the event phase button when manual resolution is active
        if (eventPhaseSection) {
            eventPhaseSection.classList.add('hidden');
        }
    } else {
        // Hide the manual resolution section
        manualResolutionSection.classList.add('hidden');
        
        // Show the event phase button when manual resolution is not active
        updateEventPhaseButton();
    }
}

function renderIntelligenceBriefing() {
    // Update game meta information instead of intelligence briefing
    if (roundInfo) {
        roundInfo.textContent = `Round ${gameState.round_marker || 1}`;
    }
    if (phaseInfo) {
        phaseInfo.textContent = formatPhase(gameState.current_phase || 'Unknown');
    }
    if (moodInfo) {
        moodInfo.textContent = `Public Mood: ${formatMood(gameState.public_mood || 0)}`;
    }
}

function renderMainStage() {
    // Update action buttons
    updateActionButtons();
    
    // Update game log
    if (logContent) {
        const logToShow = (gameState.turn_log && Array.isArray(gameState.turn_log) && gameState.turn_log.length > 0)
            ? gameState.turn_log
            : (gameState.log && Array.isArray(gameState.log) ? gameState.log : []);
        if (logToShow.length > 0) {
            logContent.innerHTML = logToShow.map(entry => `<p>${entry}</p>`).join('');
            logContent.scrollTop = logContent.scrollHeight;
        } else {
            logContent.innerHTML = '<p>Game log will appear here...</p>';
        }
    }
}

function renderPlayerDashboard() {
    // Update current player information
    updateCurrentPlayerInfo();
    
    // Update player identity cards
    const currentPlayer = gameState.players[gameState.current_player_index];
    
    if (currentPlayerArchetypeTitle) {
        currentPlayerArchetypeTitle.textContent = currentPlayer.archetype ? currentPlayer.archetype.title : 'Unknown';
    }
    if (currentPlayerArchetypeDesc) {
        currentPlayerArchetypeDesc.textContent = currentPlayer.archetype ? currentPlayer.archetype.description : '';
    }
    if (currentPlayerMandateTitle) {
        currentPlayerMandateTitle.textContent = currentPlayer.mandate ? currentPlayer.mandate.title : 'Unknown';
    }
    if (currentPlayerMandateDesc) {
        currentPlayerMandateDesc.textContent = currentPlayer.mandate ? currentPlayer.mandate.description : 'No mandate';
    }
    
    // Update action points display
    if (actionPointsDisplay) {
        const remainingAP = gameState.action_points ? gameState.action_points[currentPlayer.id] || 2 : 2;
        const apText = actionPointsDisplay.querySelector('.ap-text');
        if (apText) {
            apText.textContent = `${remainingAP}/2 AP`;
        }
    }
    
    // Update player favors display
    updatePlayerFavorsDisplay();
}

// Remove this duplicate function - it's overriding the correct one above

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
    const remainingAP = gameState.action_points?.[currentPlayer.id] || 2;
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
                <span class="ap-text">${remainingAP}/2 Action Points</span>
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
    
    // Show legislation whenever it exists, not just during legislation phase
    if (gameState.term_legislation && gameState.term_legislation.length > 0) {
        pendingSection.classList.remove('hidden');
        
        // Determine if we're in legislation phase for different styling
        const isLegislationPhase = gameState.current_phase === 'LEGISLATION_PHASE';
        const phaseClass = isLegislationPhase ? 'legislation-phase' : 'pending-legislation';
        
        pendingSection.innerHTML = `
            <div class="section-header">
                <h3>🗳️ ${isLegislationPhase ? 'Legislation Session' : 'Pending Legislation'} (PC Gambling System)</h3>
                <p class="system-explanation">${isLegislationPhase ? 'Vote on bills sponsored this term.' : 'Legislation will be voted on during the legislation session.'} Commit PC to support or oppose legislation. Bigger commitments = bigger rewards!</p>
            </div>
            <div class="legislation-list ${phaseClass}">
                ${gameState.term_legislation.map(legislation => {
                    const bill = gameState.legislation_options[legislation.legislation_id];
                    const sponsor = gameState.players.find(p => p.id === legislation.sponsor_id);
                    
                    // Safety check for undefined bill
                    if (!bill) {
                        console.error('Legislation not found:', legislation.legislation_id);
                        return `
                            <div class="legislation-item">
                                <div class="legislation-header">
                                    <h4>Unknown Legislation</h4>
                                    <span class="sponsor">Sponsored by ${sponsor ? sponsor.name : 'Unknown'}</span>
                                </div>
                                <div class="legislation-details">
                                    <span class="error">Error: Legislation data not found</span>
                                </div>
                            </div>
                        `;
                    }
                    
                    // Calculate current support and opposition
                    const totalSupport = Object.values(legislation.support_players).reduce((sum, amount) => sum + amount, 0);
                    const totalOpposition = Object.values(legislation.oppose_players).reduce((sum, amount) => sum + amount, 0);
                    const netInfluence = totalSupport - totalOpposition;
                    
                    // Show current commitments
                    const supportDetails = Object.entries(legislation.support_players).map(([playerId, amount]) => {
                        const player = gameState.players.find(p => p.id === parseInt(playerId));
                        return player ? `${player.name} (${amount} PC)` : `Player ${playerId} (${amount} PC)`;
                    }).join(', ');
                    
                    const opposeDetails = Object.entries(legislation.oppose_players).map(([playerId, amount]) => {
                        const player = gameState.players.find(p => p.id === parseInt(playerId));
                        return player ? `${player.name} (${amount} PC)` : `Player ${playerId} (${amount} PC)`;
                    }).join(', ');
                    
                    return `
                        <div class="legislation-item gambling-legislation">
                            <div class="legislation-header">
                                <h4>${bill.title}</h4>
                                <span class="sponsor">Sponsored by ${sponsor ? sponsor.name : 'Unknown'}</span>
                            </div>
                            <div class="legislation-details">
                                <div class="target-info">
                                    <span class="cost">Cost: ${bill.cost} PC</span>
                                    <span class="target">Success Target: ${bill.success_target} PC</span>
                                    <span class="crit-target">Crit Target: ${bill.crit_target} PC</span>
                                </div>
                                <div class="current-status">
                                    <div class="influence-tracker">
                                        <span class="support">Support: ${totalSupport} PC</span>
                                        <span class="opposition">Opposition: ${totalOpposition} PC</span>
                                        <span class="net-influence">Net: ${netInfluence} PC</span>
                                    </div>
                                    <div class="commitment-details">
                                        ${supportDetails ? `<div class="supporters">Supporters: ${supportDetails}</div>` : ''}
                                        ${opposeDetails ? `<div class="opponents">Opponents: ${opposeDetails}</div>` : ''}
                                    </div>
                                </div>
                                <div class="reward-info">
                                    <div class="sponsor-bonus">
                                        <strong>🎯 Sponsor Bonus:</strong> 50% bonus on success, 50% penalty on failure
                                    </div>
                                    <div class="commitment-rewards">
                                        <strong>💰 Commitment Rewards:</strong>
                                        <ul>
                                            <li>Small bet (1-4 PC): 1x reward</li>
                                            <li>Medium bet (5-9 PC): 1.5x reward</li>
                                            <li>Big bet (10+ PC): 2x reward</li>
                                        </ul>
                                    </div>
                                </div>
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
    const allFavors = currentPlayer.favors || [];
    
    // Filter out negative favors since they're applied immediately
    const negativeFavorIds = ["POLITICAL_DEBT", "PUBLIC_GAFFE", "MEDIA_SCRUTINY", "COMPROMISING_POSITION", "POLITICAL_HOT_POTATO"];
    const positiveFavors = allFavors.filter(favor => !negativeFavorIds.includes(favor.id));
    
    if (positiveFavors.length > 0) {
        favorsSection.classList.remove('hidden');
        favorsSection.innerHTML = `
            <div class="section-header">
                <h3>Political Favors</h3>
            </div>
            <div class="favors-list">
                ${positiveFavors.map(favor => `
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
    const currentPlayer = gameState.players[gameState.current_player_index];
    
    // DEBUG: Print out legislation IDs and options
    if (window && window.console) {
        console.log('DEBUG: term_legislation:', gameState.term_legislation.map(l => l.legislation_id));
        console.log('DEBUG: legislation_options keys:', Object.keys(gameState.legislation_options));
        console.log('DEBUG: legislation_options:', gameState.legislation_options);
    }
    
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
        let hasVotableLegislation = false;
        
        gameState.term_legislation.forEach(legislation => {
            if (!legislation.resolved) {
                const bill = gameState.legislation_options[legislation.legislation_id];
                const sponsor = gameState.players.find(p => p.id === legislation.sponsor_id);
                const isCurrentPlayerSponsor = legislation.sponsor_id === currentPlayer.id;
                
                // Safety check for undefined bill
                if (!bill) {
                    console.error('Legislation not found:', legislation.legislation_id);
                    const legislationCard = document.createElement('div');
                    legislationCard.className = 'legislation-card error';
                    legislationCard.innerHTML = `
                        <div class="legislation-info">
                            <h5>Unknown Legislation</h5>
                            <p>Error: Legislation data not found</p>
                            <p><strong>Sponsored by:</strong> ${sponsor ? sponsor.name : 'Unknown'}</p>
                        </div>
                        <div class="voting-actions">
                            <button disabled class="vote-btn support-btn">
                                Support
                            </button>
                            <button disabled class="vote-btn oppose-btn">
                                Oppose
                            </button>
                        </div>
                    `;
                    actionList.appendChild(legislationCard);
                    return;
                }
                
                const legislationCard = document.createElement('div');
                legislationCard.className = 'legislation-card';
                
                if (isCurrentPlayerSponsor) {
                    // Current player is the sponsor - show disabled buttons with explanation
                    legislationCard.innerHTML = `
                        <div class="legislation-info">
                            <h5>${bill.title}</h5>
                            <p>${bill.description}</p>
                            <p><strong>Sponsored by:</strong> ${sponsor ? sponsor.name : 'Unknown'} (You)</p>
                            <p class="sponsor-note">You cannot vote on your own legislation</p>
                        </div>
                        <div class="voting-actions">
                            <button disabled class="vote-btn support-btn">
                                Support
                            </button>
                            <button disabled class="vote-btn oppose-btn">
                                Oppose
                            </button>
                        </div>
                    `;
                } else {
                    // Current player can vote on this legislation
                    hasVotableLegislation = true;
                    legislationCard.innerHTML = `
                        <div class="legislation-info">
                            <h5>${bill.title}</h5>
                            <p>${bill.description}</p>
                            <p><strong>Sponsored by:</strong> ${sponsor ? sponsor.name : 'Unknown'}</p>
                        </div>
                        <div class="voting-actions">
                            <button onclick="performAction('support_legislation', {legislation_id: '${legislation.legislation_id}', support_amount: 1})" class="vote-btn support-btn">
                                Support
                            </button>
                            <button onclick="performAction('oppose_legislation', {legislation_id: '${legislation.legislation_id}', oppose_amount: 1})" class="vote-btn oppose-btn">
                                Oppose
                            </button>
                        </div>
                    `;
                }
                actionList.appendChild(legislationCard);
            }
        });
        
        // If current player can't vote on any legislation, show pass turn option
        if (!hasVotableLegislation) {
            const passTurnCard = document.createElement('div');
            passTurnCard.className = 'legislation-card';
            passTurnCard.innerHTML = `
                <div class="legislation-info">
                    <h5>No Legislation to Vote On</h5>
                    <p>You cannot vote on your own legislation. All available legislation was sponsored by you.</p>
                </div>
                <div class="voting-actions">
                    <button onclick="performAction('pass_turn', {})" class="vote-btn pass-turn-btn">
                        Pass Turn
                    </button>
                </div>
            `;
            actionList.appendChild(passTurnCard);
        }
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
            <span class="ap-text">${remainingAP}/2 Action Points</span>
        </div>
    `;
    actionList.appendChild(apDisplay);
    
    // Define action costs
    const actionCosts = {
        'fundraise': 1,
        'network': 1,
        'sponsor_legislation': 2,
        'declare_candidacy': 2,
        'use_favor': 1,
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
    
    // Add legislation support/oppose actions if there's pending legislation
    if (gameState.term_legislation && gameState.term_legislation.length > 0) {
        const currentPlayer = gameState.players[gameState.current_player_index];
        const votableLegislation = gameState.term_legislation.filter(legislation => 
            legislation.sponsor_id !== currentPlayer.id && !legislation.resolved
        );
        
        if (votableLegislation.length > 0) {
            actions.push(
                { type: 'support_legislation', label: 'Support Legislation', description: 'Commit PC to support bills (gambling rewards!)' },
                { type: 'oppose_legislation', label: 'Oppose Legislation', description: 'Commit PC to oppose bills (gambling rewards!)' }
            );
        }
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
    // Check if gameState is available
    if (!gameState || !gameState.players) {
        console.error('Game state not available for legislation menu');
        showMessage('Game state not available. Please refresh the page.', 'error');
        return;
    }
    
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
    // Check if gameState is available
    if (!gameState || !gameState.players) {
        console.error('Game state not available for favor menu');
        showMessage('Game state not available. Please refresh the page.', 'error');
        return;
    }
    
    // Remove existing favor menu
    const existingMenu = document.getElementById('favor-menu');
    if (existingMenu) {
        existingMenu.remove();
    }
    
    const currentPlayer = gameState.players[gameState.current_player_index];
    
    // Filter out negative favors since they're applied immediately
    const negativeFavorIds = ["POLITICAL_DEBT", "PUBLIC_GAFFE", "MEDIA_SCRUTINY", "COMPROMISING_POSITION", "POLITICAL_HOT_POTATO"];
    const positiveFavors = currentPlayer.favors.filter(favor => !negativeFavorIds.includes(favor.id));
    
    if (positiveFavors.length === 0) {
        showMessage('You have no usable favors. Negative favors are applied immediately when drawn.', 'info');
        return;
    }
    
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    const modal = document.createElement('div');
    modal.id = 'favor-menu';
    modal.className = 'favor-menu';
    
    modal.innerHTML = `
        <h3>Choose a Favor to Use</h3>
        <p class="favor-menu-note">Note: Negative favors are applied immediately when drawn during Networking.</p>
        <div class="favor-options">
            ${positiveFavors.map(favor => {
                return `
                    <button class="favor-option" 
                            data-favor-id="${favor.id}" 
                            data-favor-description="${favor.description}">
                        <div><strong>${favor.description}</strong></div>
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
            
            // Handle different types of positive favors
            if (favorDescription.includes('Target player') || 
                favorDescription.includes('Choose one player')) {
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
    modal.className = 'legislation-menu gambling-menu';
    
    modal.innerHTML = `
        <h3>🎯 Support Legislation (PC Gambling)</h3>
        <div class="gambling-info">
            <p><strong>💰 Commitment Rewards:</strong></p>
            <ul>
                <li>Small bet (1-4 PC): 1x reward</li>
                <li>Medium bet (5-9 PC): 1.5x reward</li>
                <li>Big bet (10+ PC): 2x reward</li>
            </ul>
            <p><em>Rewards are paid if the legislation passes!</em></p>
        </div>
        <div class="legislation-options">
            ${availableLegislation.map(legislation => {
                const bill = gameState.legislation_options[legislation.legislation_id];
                const sponsor = gameState.players.find(p => p.id === legislation.sponsor_id);
                
                // Calculate current support and opposition
                const totalSupport = Object.values(legislation.support_players).reduce((sum, amount) => sum + amount, 0);
                const totalOpposition = Object.values(legislation.oppose_players).reduce((sum, amount) => sum + amount, 0);
                const netInfluence = totalSupport - totalOpposition;
                const currentCommitment = legislation.support_players[currentPlayer.id] || 0;
                
                // Safety check for undefined bill
                if (!bill) {
                    console.error('Legislation not found:', legislation.legislation_id);
                    return `
                        <button class="legislation-option error" data-legislation-id="${legislation.legislation_id}" disabled>
                            <div><strong>Unknown Legislation</strong></div>
                            <div>Sponsored by: ${sponsor ? sponsor.name : 'Unknown'}</div>
                            <div>Error: Legislation data not found</div>
                        </button>
                    `;
                }
                
                return `
                    <button class="legislation-option gambling-option" data-legislation-id="${legislation.legislation_id}">
                        <div class="legislation-header">
                            <div><strong>${bill.title}</strong></div>
                            <div class="sponsor">Sponsored by: ${sponsor ? sponsor.name : 'Unknown'}</div>
                        </div>
                        <div class="legislation-details">
                            <div class="targets">
                                <span>Success: ${bill.success_target} PC</span>
                                <span>Crit: ${bill.crit_target} PC</span>
                            </div>
                            <div class="current-status">
                                <span class="support">Support: ${totalSupport} PC</span>
                                <span class="opposition">Opposition: ${totalOpposition} PC</span>
                                <span class="net">Net: ${netInfluence} PC</span>
                            </div>
                            ${currentCommitment > 0 ? `<div class="your-commitment">Your commitment: ${currentCommitment} PC</div>` : ''}
                        </div>
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
            const currentCommitment = gameState.term_legislation.find(l => l.legislation_id === legislationId)?.support_players[currentPlayer.id] || 0;
            
            const amount = prompt(
                `How much PC do you want to commit to support?\n\n` +
                `You have: ${maxPC} PC\n` +
                `Current commitment: ${currentCommitment} PC\n\n` +
                `Rewards if legislation passes:\n` +
                `• 1-4 PC: 1x reward\n` +
                `• 5-9 PC: 1.5x reward\n` +
                `• 10+ PC: 2x reward\n\n` +
                `Enter amount:`, 
                '1'
            );
            
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
    modal.className = 'legislation-menu gambling-menu';
    
    modal.innerHTML = `
        <h3>🎯 Oppose Legislation (PC Gambling)</h3>
        <div class="gambling-info">
            <p><strong>💰 Commitment Rewards:</strong></p>
            <ul>
                <li>Small bet (1-4 PC): 1x reward</li>
                <li>Medium bet (5-9 PC): 1.5x reward</li>
                <li>Big bet (10+ PC): 2x reward</li>
            </ul>
            <p><em>Rewards are paid if the legislation fails!</em></p>
        </div>
        <div class="legislation-options">
            ${availableLegislation.map(legislation => {
                const bill = gameState.legislation_options[legislation.legislation_id];
                const sponsor = gameState.players.find(p => p.id === legislation.sponsor_id);
                
                // Calculate current support and opposition
                const totalSupport = Object.values(legislation.support_players).reduce((sum, amount) => sum + amount, 0);
                const totalOpposition = Object.values(legislation.oppose_players).reduce((sum, amount) => sum + amount, 0);
                const netInfluence = totalSupport - totalOpposition;
                const currentCommitment = legislation.oppose_players[currentPlayer.id] || 0;
                
                // Safety check for undefined bill
                if (!bill) {
                    console.error('Legislation not found:', legislation.legislation_id);
                    return `
                        <button class="legislation-option error" data-legislation-id="${legislation.legislation_id}" disabled>
                            <div><strong>Unknown Legislation</strong></div>
                            <div>Sponsored by: ${sponsor ? sponsor.name : 'Unknown'}</div>
                            <div>Error: Legislation data not found</div>
                        </button>
                    `;
                }
                
                return `
                    <button class="legislation-option gambling-option" data-legislation-id="${legislation.legislation_id}">
                        <div class="legislation-header">
                            <div><strong>${bill.title}</strong></div>
                            <div class="sponsor">Sponsored by: ${sponsor ? sponsor.name : 'Unknown'}</div>
                        </div>
                        <div class="legislation-details">
                            <div class="targets">
                                <span>Success: ${bill.success_target} PC</span>
                                <span>Crit: ${bill.crit_target} PC</span>
                            </div>
                            <div class="current-status">
                                <span class="support">Support: ${totalSupport} PC</span>
                                <span class="opposition">Opposition: ${totalOpposition} PC</span>
                                <span class="net">Net: ${netInfluence} PC</span>
                            </div>
                            ${currentCommitment > 0 ? `<div class="your-commitment">Your commitment: ${currentCommitment} PC</div>` : ''}
                        </div>
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
            const currentCommitment = gameState.term_legislation.find(l => l.legislation_id === legislationId)?.oppose_players[currentPlayer.id] || 0;
            
            const amount = prompt(
                `How much PC do you want to commit to oppose?\n\n` +
                `You have: ${maxPC} PC\n` +
                `Current commitment: ${currentCommitment} PC\n\n` +
                `Rewards if legislation fails:\n` +
                `• 1-4 PC: 1x reward\n` +
                `• 5-9 PC: 1.5x reward\n` +
                `• 10+ PC: 2x reward\n\n` +
                `Enter amount:`, 
                '1'
            );
            
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
    // Check if gameState is available
    if (!gameState || !gameState.players) {
        console.error('Game state not available for campaign dialog');
        showMessage('Game state not available. Please refresh the page.', 'error');
        return;
    }
    
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
                    
                    // Safety check for undefined bill
                    if (!bill) {
                        console.error('Legislation not found:', legislation.legislation_id);
                        return `<option value="${legislation.legislation_id}" disabled>Unknown Legislation (${sponsor ? sponsor.name : 'Unknown'})</option>`;
                    }
                    
                    return `<option value="${legislation.legislation_id}">${bill.title} (${sponsor ? sponsor.name : 'Unknown'})</option>`;
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

function toggleSection(sectionId) {
    const section = document.querySelector(`.${sectionId}`);
    if (!section) return;
    section.classList.toggle('collapsed');
    // Update toggle arrow
    const toggle = document.getElementById(`${sectionId}-toggle`);
    if (toggle) {
        if (section.classList.contains('collapsed')) {
            toggle.textContent = '►';
        } else {
            toggle.textContent = '▼';
        }
    }
}

// On DOMContentLoaded, ensure all collapsible sections are expanded by default
// (could be collapsed by default on mobile if desired)
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.collapsible-section').forEach(section => {
        section.classList.remove('collapsed');
    });
});

// Initialize
// Event listeners are already set up at the top of the file 