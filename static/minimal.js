// Minimal JavaScript for Election Game

class MinimalGame {
    constructor() {
        this.gameId = null;
        this.currentState = null;
        this.pollingInterval = null;
        this.isProcessingAction = false;
    }
    
    async startGame(playerName, gameMode, aiConfig) {
        try {
            console.log('Starting new game...');
            
            let endpoint = '/api/game/new_vs_ai';
            let requestBody = {
                player_name: playerName
            };
            
            if (gameMode === 'multiple') {
                endpoint = '/api/game/new_vs_multiple_ai';
                requestBody.ai_personas = aiConfig;
            } else {
                requestBody.ai_persona = aiConfig;
            }
            
            // Create a new game with the specified configuration
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestBody)
            });
            
            if (!response.ok) {
                throw new Error(`Failed to create game: ${response.status}`);
            }
            
            const data = await response.json();
            this.gameId = data.game_id;
            this.currentState = data.state;
            
            console.log('Game created successfully:', this.gameId);
            
            // Start polling for game state updates
            this.startPolling();
            
            // Update the UI
            this.updateGameDisplay();
            
        } catch (error) {
            console.error('Error starting game:', error);
            alert('Failed to start game. Please try again.');
        }
    }
    
    async performAction(actionType, actionData = {}) {
        if (this.isProcessingAction) {
            return; // Prevent multiple simultaneous actions
        }
        
        this.isProcessingAction = true;
        
        try {
            const response = await fetch(`/api/game/${this.gameId}/action`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    action_type: actionType,
                    ...actionData
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Action failed');
            }
            
            const data = await response.json();
            this.currentState = data.state;
            this.updateGameDisplay();
            
        } catch (error) {
            console.error('Error performing action:', error);
            alert(`Action failed: ${error.message}`);
        } finally {
            this.isProcessingAction = false;
        }
    }
    
    async getGameState() {
        if (!this.gameId) return;
        
        try {
            const response = await fetch(`/api/game/${this.gameId}`);
            
            if (!response.ok) {
                throw new Error(`Failed to get game state: ${response.status}`);
            }
            
            const data = await response.json();
            this.currentState = data.state;
            this.updateGameDisplay();
            
        } catch (error) {
            console.error('Error getting game state:', error);
        }
    }
    
    startPolling() {
        // Poll every 2 seconds for game state updates
        this.pollingInterval = setInterval(() => {
            this.getGameState();
        }, 2000);
    }
    
    stopPolling() {
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }
    }
    
    updateGameDisplay() {
        if (!this.currentState) return;
        
        // Update game info
        const currentPlayer = this.currentState.players[this.currentState.current_player_index];
        document.getElementById('current-player').textContent = `Current Player: ${currentPlayer.name}`;
        document.getElementById('game-phase').textContent = `Phase: ${this.currentState.current_phase}`;
        document.getElementById('round-info').textContent = `Round: ${this.currentState.round_marker}/4`;
        
        // Update players info
        this.updatePlayersDisplay();
        
        // Update actions
        this.updateActionsDisplay();
        
        // Update game log
        this.updateGameLog();
    }
    
    updatePlayersDisplay() {
        const playersInfo = document.getElementById('players-info');
        playersInfo.innerHTML = '';
        
        this.currentState.players.forEach((player, index) => {
            const isCurrentPlayer = index === this.currentState.current_player_index;
            const actionPoints = this.currentState.action_points[player.id] || 0;
            
            const playerCard = document.createElement('div');
            playerCard.className = `player-card ${isCurrentPlayer ? 'current' : ''}`;
            
            playerCard.innerHTML = `
                <h3>${player.name} (${player.archetype.title})</h3>
                <div class="player-stats">
                    <div class="stat">
                        <div class="stat-label">PC</div>
                        <div class="stat-value">${player.pc}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">AP</div>
                        <div class="stat-value">${actionPoints}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Office</div>
                        <div class="stat-value">${player.current_office ? player.current_office.title : 'None'}</div>
                    </div>
                    <div class="stat">
                        <div class="stat-label">Favors</div>
                        <div class="stat-value">${player.favors ? player.favors.length : 0}</div>
                    </div>
                </div>
            `;
            
            playersInfo.appendChild(playerCard);
        });
    }
    
    updateActionsDisplay() {
        const actionsList = document.getElementById('actions-list');
        actionsList.innerHTML = '';
        
        // Only show actions if it's the human player's turn
        const currentPlayer = this.currentState.players[this.currentState.current_player_index];
        const isHumanTurn = currentPlayer.name !== 'AI-1' && currentPlayer.name !== 'AI-2';
        
        if (!isHumanTurn || this.currentState.current_phase !== 'ACTION_PHASE') {
            actionsList.innerHTML = '<p>Waiting for other players...</p>';
            return;
        }
        
        // Get valid actions from the server
        this.getValidActions().then(actions => {
            if (actions.length === 0) {
                actionsList.innerHTML = '<p>No actions available.</p>';
                return;
            }
            
            actions.forEach(action => {
                const actionBtn = document.createElement('button');
                actionBtn.className = 'action-btn';
                actionBtn.textContent = this.getActionDescription(action);
                actionBtn.onclick = () => this.handleActionClick(action);
                actionsList.appendChild(actionBtn);
            });
        });
    }
    
    async getValidActions() {
        // For now, we'll use a simplified approach
        // In a full implementation, this would call the server to get valid actions
        const currentPlayer = this.currentState.players[this.currentState.current_player_index];
        const actionPoints = this.currentState.action_points[currentPlayer.id] || 0;
        
        const actions = [];
        
        // Basic actions that are always available
        if (actionPoints >= 1) {
            actions.push({ type: 'fundraise', cost: 1 });
            actions.push({ type: 'network', cost: 1 });
        }
        
        if (actionPoints >= 2) {
            actions.push({ type: 'sponsor_legislation', cost: 2 });
        }
        
        // Round 4 only actions
        if (this.currentState.round_marker === 4 && actionPoints >= 2) {
            actions.push({ type: 'declare_candidacy', cost: 2 });
        }
        
        // Use favor action
        if (actionPoints >= 1 && currentPlayer.favors && currentPlayer.favors.length > 0) {
            actions.push({ type: 'use_favor', cost: 1 });
        }
        
        // Support/oppose legislation
        if (this.currentState.pending_legislation && actionPoints >= 1) {
            actions.push({ type: 'support_legislation', cost: 1 });
            actions.push({ type: 'oppose_legislation', cost: 1 });
        }
        
        return actions;
    }
    
    getActionDescription(action) {
        const descriptions = {
            'fundraise': 'Fundraise (Gain PC)',
            'network': 'Network (Gain PC + Favor)',
            'sponsor_legislation': 'Sponsor Legislation',
            'declare_candidacy': 'Declare Candidacy',
            'use_favor': 'Use Political Favor',
            'support_legislation': 'Support Legislation',
            'oppose_legislation': 'Oppose Legislation'
        };
        
        return descriptions[action.type] || action.type;
    }
    
    async handleActionClick(action) {
        try {
            if (action.type === 'fundraise') {
                await this.performAction('fundraise');
            } else if (action.type === 'network') {
                await this.performAction('network');
            } else if (action.type === 'sponsor_legislation') {
                // For now, use a simple prompt
                const legislationId = prompt('Enter legislation ID (e.g., INFRASTRUCTURE):');
                if (legislationId) {
                    await this.performAction('sponsor_legislation', { legislation_id: legislationId });
                }
            } else if (action.type === 'declare_candidacy') {
                const officeId = prompt('Enter office ID (e.g., PRESIDENT):');
                const committedPc = parseInt(prompt('Enter PC to commit:') || '0');
                if (officeId && committedPc >= 0) {
                    await this.performAction('declare_candidacy', { 
                        office_id: officeId, 
                        committed_pc: committedPc 
                    });
                }
            } else if (action.type === 'use_favor') {
                const favorId = prompt('Enter favor ID:');
                if (favorId) {
                    await this.performAction('use_favor', { favor_id: favorId });
                }
            } else if (action.type === 'support_legislation') {
                const amount = parseInt(prompt('Enter PC amount to commit:') || '0');
                if (amount > 0) {
                    await this.performAction('support_legislation', { 
                        legislation_id: this.currentState.pending_legislation.legislation_id,
                        support_amount: amount 
                    });
                }
            } else if (action.type === 'oppose_legislation') {
                const amount = parseInt(prompt('Enter PC amount to commit:') || '0');
                if (amount > 0) {
                    await this.performAction('oppose_legislation', { 
                        legislation_id: this.currentState.pending_legislation.legislation_id,
                        oppose_amount: amount 
                    });
                }
            }
        } catch (error) {
            console.error('Error handling action:', error);
        }
    }
    
    updateGameLog() {
        const gameLog = document.getElementById('game-log');
        gameLog.innerHTML = '';
        
        if (this.currentState.turn_log && this.currentState.turn_log.length > 0) {
            // Show the last 10 log entries
            const recentLogs = this.currentState.turn_log.slice(-10);
            
            recentLogs.forEach(logEntry => {
                const logDiv = document.createElement('div');
                logDiv.className = 'log-entry';
                logDiv.textContent = logEntry;
                gameLog.appendChild(logDiv);
            });
        } else {
            gameLog.innerHTML = '<p>No recent events.</p>';
        }
    }
}

// Global game instance
let game = new MinimalGame();

// UI Functions
function showSetup() {
    document.getElementById('setup-screen').classList.remove('hidden');
    document.getElementById('game-screen').classList.add('hidden');
    game.stopPolling();
    game = new MinimalGame();
}

function showGame() {
    document.getElementById('setup-screen').classList.add('hidden');
    document.getElementById('game-screen').classList.remove('hidden');
}

function startGame() {
    const playerName = document.getElementById('player-name').value.trim() || 'Human';
    const gameMode = document.querySelector('input[name="game-mode"]:checked').value;
    
    let aiConfig;
    if (gameMode === 'multiple') {
        const aiPersonas = Array.from(document.querySelectorAll('.ai-persona-select')).map(select => select.value);
        aiConfig = aiPersonas;
    } else {
        aiConfig = document.getElementById('ai-persona').value;
    }
    
    game.startGame(playerName, gameMode, aiConfig);
    showGame();
}

function showHelp() {
    document.getElementById('help-modal').classList.remove('hidden');
}

function hideHelp() {
    document.getElementById('help-modal').classList.add('hidden');
}

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    // Set up event listeners
    document.getElementById('player-name').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            startGame();
        }
    });
    
    // Handle game mode selection
    const gameModeRadios = document.querySelectorAll('input[name="game-mode"]');
    const singleAiOptions = document.getElementById('single-ai-options');
    const multipleAiOptions = document.getElementById('multiple-ai-options');
    
    gameModeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.value === 'single') {
                singleAiOptions.classList.remove('hidden');
                multipleAiOptions.classList.add('hidden');
            } else {
                singleAiOptions.classList.add('hidden');
                multipleAiOptions.classList.remove('hidden');
            }
        });
    });
    
    // Close modal when clicking outside
    document.getElementById('help-modal').addEventListener('click', function(e) {
        if (e.target === this) {
            hideHelp();
        }
    });
}); 