const { Terminal } = require('xterm');
const { FitAddon } = require('xterm-addon-fit');

class TerminalUI {
    constructor() {
        this.term = new Terminal({
            cursorBlink: true,
            theme: {
                background: '#1e1e1e',
                foreground: '#d4d4d4',
            }
        });
        this.fitAddon = new FitAddon();
        this.term.loadAddon(this.fitAddon);
        this.term.open(document.getElementById('terminal-container'));
        this.fitAddon.fit();
        window.addEventListener('resize', () => this.fitAddon.fit());
        this.term.writeln('Welcome to Election: The Game!');
        this.term.writeln('Connecting to server...');
        this.inputBuffer = '';
        this.term.onKey(this.onKey.bind(this));
    }

    onKey(e) {
        const ev = e.domEvent;
        if (ev.keyCode === 13) { // Enter
            if (this.onEnter) {
                this.onEnter(this.inputBuffer);
                this.inputBuffer = '';
                this.term.writeln('');
            }
        } else if (ev.keyCode === 8) { // Backspace
            if (this.inputBuffer.length > 0) {
                this.term.write('\b \b');
                this.inputBuffer = this.inputBuffer.slice(0, -1);
            }
        } else {
            this.inputBuffer += e.key;
            this.term.write(e.key);
        }
    }

    displayGameState(state) {
        this.term.writeln('\n\n\x1B[1;3;34m======================================================================\x1B[0m');
        this.term.writeln('\x1B[1;3;34m                              ELECTION: THE GAME\x1B[0m');
        this.term.writeln('\x1B[1;3;34m======================================================================\x1B[0m');
        
        const progress = state.round_marker / 4.0;
        const barLength = 40;
        const filledLength = Math.floor(barLength * progress);
        const bar = '█'.repeat(filledLength) + '░'.repeat(barLength - filledLength);
        this.term.writeln(`\n\x1B[36mGame Progress: [${bar}] ${state.round_marker}/4 Rounds\x1B[0m`);
        this.term.writeln(`\x1B[36mCurrent Phase: ${state.current_phase.replace('_', ' ').toUpperCase()}\x1B[0m`);
        this.term.writeln(`\x1B[36mPublic Mood: ${state.public_mood}\x1B[0m`);

        if (state.log && state.log.length > 0) {
            this.term.writeln('\n\x1B[93m📰 Recent Events:\x1B[0m');
            state.log.slice(-10).forEach(message => { // Show more logs
                if (message.trim()) this.term.writeln(`  \x1B[93m•\x1B[0m ${message}`);
            });
        }
        
        this.term.writeln(`\n\x1B[1m👥 PLAYERS:\x1B[0m`);
        state.players.forEach(p => {
            const officeTitle = p.current_office ? p.current_office.title : "Outsider";
            const isCurrent = p.name === state.current_player ? '\x1B[92m▶▶▶\x1B[0m' : '   ';
            this.term.writeln(`\n  ${isCurrent} \x1B[1m${p.name}\x1B[0m (${p.archetype.title})`);
            const ap = state.action_points[p.id] || 0;
            this.term.writeln(`    \x1B[36m💰 PC: ${p.pc}\x1B[0m | \x1B[94m🏛️  Office: ${officeTitle}\x1B[0m | \x1B[92m⚡ AP: ${ap}\x1B[0m`);
        });

        // If a system action is present, don't show a player's turn.
        const hasSystemAction = state.valid_actions && state.valid_actions.some(a => 
            a.action_type === 'ActionResolveLegislation' || 
            a.action_type === 'ActionResolveElections' ||
            a.action_type === 'ActionAcknowledgeResults'
        );

        if (hasSystemAction) {
            this.term.writeln(`\n\x1B[1;95mSYSTEM ACTION REQUIRED\x1B[0m`);
        } else if (state.current_phase === "ACTION_PHASE") {
            this.term.writeln(`\n\x1B[1;92m🎯 ${state.current_player}'s Turn\x1B[0m`);
        }
    }

    promptForAction(actions) {
        this.term.writeln('\n\x1B[1m🎮 Available Actions:\x1B[0m');
        actions.forEach((action, i) => {
            this.term.writeln(`  \x1B[36m[${i + 1}]\x1B[0m ${this.getActionDescription(action)}`);
        });
        this.term.writeln('\n\x1B[1m🔧 Special Commands:\x1B[0m');
        this.term.writeln(`  \x1B[93m[info]\x1B[0m View detailed game information`);
        this.term.writeln(`  \x1B[93m[help]\x1B[0m Show action descriptions`);
        this.term.writeln(`  \x1B[93m[quit]\x1B[0m Exit the game`);
        this.term.write('\n\x1B[1mEnter your choice: \x1B[0m');
    }

    getActionDescription(action) {
        switch(action.action_type) {
            case 'ActionFundraise': return '\x1B[92m💰 Fundraise\x1B[0m - Gain Political Capital';
            case 'ActionNetwork': return '\x1B[94m🤝 Network\x1B[0m - Gain PC and favors';
            case 'ActionSponsorLegislation': return `\x1B[93m📜 Sponsor Legislation\x1B[0m (Cost: ${action.legislation_id})`;
            case 'ActionDeclareCandidacy': return `\x1B[36m🏛️  Declare Candidacy\x1B[0m (Cost: ${action.committed_pc} PC)`;
            case 'ActionUseFavor': return '\x1B[95m🎁 Use Favor\x1B[0m';
            case 'ActionSupportLegislation': return `\x1B[92m✅ Support Legislation\x1B[0m: ${action.legislation_id}`;
            case 'ActionOpposeLegislation': return `\x1B[91m❌ Oppose Legislation\x1B[0m: ${action.legislation_id}`;
            case 'ActionPassTurn': return '\x1B[93m⏭️  Pass Turn\x1B[0m';
            case 'UISponsorLegislation': return `\x1B[93m📜 Sponsor Legislation\x1B[0m`;
            case 'UIDeclareCandidacy': return `\x1B[36m🏛️  Declare Candidacy\x1B[0m`;
            case 'UISupportLegislation': return `\x1B[92m✅ Support Legislation\x1B[0m`;
            case 'UIOpposeLegislation': return `\x1B[91m❌ Oppose Legislation\x1B[0m`;
            case 'ActionResolveLegislation': return `\x1B[95m⚖️ Resolve Legislation\x1B[0m`;
            case 'ActionResolveElections': return `\x1B[95m🗳️ Resolve Elections\x1B[0m`;
            case 'ActionAcknowledgeResults': return `\x1B[96m🏁 Start Next Term\x1B[0m`;
            default: return `\x1B[97m${action.action_type}\x1B[0m`;
        }
    }
    
    displayHelp() {
        this.term.writeln('\n\x1B[1;3;34m======================================================================\x1B[0m');
        this.term.writeln('\x1B[1;93m❓ ACTION HELP\x1B[0m');
        this.term.writeln('\x1B[1;3;34m======================================================================\x1B[0m');
        this.term.writeln('\x1B[92m💰 Fundraise\x1B[0m: Gain Political Capital');
        this.term.writeln('\x1B[94m🤝 Network\x1B[0m: Build connections to gain PC and favors');
        this.term.writeln('\x1B[93m📜 Sponsor Legislation\x1B[0m: Propose new legislation');
        this.term.writeln('\x1B[36m🏛️  Declare Candidacy\x1B[0m: Run for office');
        this.term.writeln('\x1B[95m🎁 Use Favor\x1B[0m: Call in a political favor');
        this.term.writeln('\x1B[92m✅ Support Legislation\x1B[0m: Commit PC to support a bill');
        this.term.writeln('\x1B[91m❌ Oppose Legislation\x1B[0m: Commit PC to oppose a bill');
        this.term.writeln('\x1B[93m⏭️  Pass Turn\x1B[0m: Skip your turn');
    }

    displayInfo(state) {
        this.term.writeln('\n\x1B[1;3;34m======================================================================\x1B[0m');
        this.term.writeln('\x1B[1;93m📊 GAME INFORMATION\x1B[0m');
        this.term.writeln('\x1B[1;3;34m======================================================================\x1B[0m');
        this.term.writeln(`\x1B[36mRound: ${state.round_marker}/4\x1B[0m`);
        this.term.writeln(`\x1B[36mPhase: ${state.current_phase}\x1B[0m`);
        this.term.writeln(`\x1B[36mPublic Mood: ${state.public_mood}\x1B[0m`);

        const humanPlayer = state.players.find(p => p.name === 'Human');
        if (humanPlayer && humanPlayer.mandate) {
            this.term.writeln('\n\x1B[1m🎯 Your Personal Mandate:\x1B[0m');
            this.term.writeln(`  \x1B[93m${humanPlayer.mandate.title}\x1B[0m`);
            this.term.writeln(`  \x1B[97m${humanPlayer.mandate.description}\x1B[0m`);
        }

        if (state.offices) {
            this.term.writeln('\n\x1B[1m🏛️  Available Offices:\x1B[0m');
            for (const office_id in state.offices) {
                const office = state.offices[office_id];
                this.term.writeln(`  ${office.title} (Tier ${office.tier}) - Cost: ${office.candidacy_cost} PC`);
            }
        }

        if (state.legislation_options) {
            this.term.writeln('\n\x1B[1m📜 Available Legislation:\x1B[0m');
            for (const leg_id in state.legislation_options) {
                const legislation = state.legislation_options[leg_id];
                this.term.writeln(`  ${legislation.title} - Cost: ${legislation.cost} PC`);
            }
        }
    }
}

const ui = new TerminalUI();
const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const socket = new WebSocket(`${protocol}//${window.location.host}/ws`);

let validActions = [];
let currentState = {};
let isAwaitingSubChoice = false;
let lastPlayerName = ''; // New: To track player changes
let isAwaitingAcknowledgement = false; // New: Client-side flag

socket.onopen = () => {
    ui.term.writeln('Connected to server.');
};

socket.onmessage = function(event) {
    const gameState = JSON.parse(event.data);

    // New logic to detect when to pause
    const currentPlayerName = gameState.current_player;
    if (lastPlayerName === 'Human' && currentPlayerName !== 'Human' && !isAwaitingAcknowledgement) {
        isAwaitingAcknowledgement = true;
    }
    lastPlayerName = currentPlayerName;
    
    currentState = gameState;
    ui.displayGameState(gameState);

    if (isAwaitingAcknowledgement) {
        ui.promptToContinue();
        return;
    }

    // Check if the server sent a specific prompt for a sub-choice
    if (gameState.prompt && gameState.valid_actions) {
        isAwaitingSubChoice = true;
        validActions = gameState.valid_actions; // These are now the sub-options
        ui.promptForSubChoice(gameState.prompt, validActions);
    } else if (gameState.valid_actions && gameState.valid_actions.length > 0) {
        isAwaitingSubChoice = false;
        validActions = gameState.valid_actions;
        ui.promptForAction(validActions);
    } else if (!gameState.is_game_over) {
        ui.promptToContinue();
    }
};

ui.promptToContinue = function() {
    this.term.writeln('\n\x1B[1;93mPress [Enter] to continue...\x1B[0m');
}

// New function to handle sub-prompts
ui.promptForSubChoice = function(prompt, options) {
    this.term.writeln(`\n\x1B[1;96m${prompt}\x1B[0m`);
    if (options.length > 0) {
        options.forEach((action, index) => {
            // Use the new display_name field from the backend
            this.term.writeln(`  \x1B[1;93m[${index + 1}]\x1B[0m ${action.display_name}`);
        });
    }
    this.term.write('\nEnter your choice: ');
};


ui.onEnter = (input) => {
    const command = input.trim().toLowerCase();

    if (isAwaitingAcknowledgement) {
        isAwaitingAcknowledgement = false;
        // Re-render the game state without the "continue" prompt
        ui.displayGameState(currentState);
        // After acknowledgement, we might need to prompt for action if it's our turn again
        if (currentState.valid_actions && currentState.valid_actions.length > 0) {
             ui.promptForAction(currentState.valid_actions);
        }
        return;
    }

    // If it's not the human's turn, any 'enter' is a continue.
    if ((!validActions || validActions.length === 0) && !isAwaitingSubChoice) {
        // This logic might need to be adjusted; for now, we prevent sending 'continue'
        // as the server no longer expects it. The game loop is now fully state-driven.
        return;
    }

    if (command === 'help') {
        ui.displayHelp();
        ui.promptForAction(validActions);
        return;
    }
    if (command === 'info') {
        ui.displayInfo(currentState);
        ui.promptForAction(validActions);
        return;
    }
    if (command === 'quit') {
        socket.close();
        ui.term.writeln('Connection closed.');
        return;
    }

    if (isAwaitingSubChoice) {
        // Handle case where we expect a free-form number input (e.g., for PC amount)
        if (currentState.expects_input === "amount") {
            const amount = parseInt(command, 10);
            if (!isNaN(amount) && amount > 0) {
                socket.send(JSON.stringify({
                    action_type: currentState.pending_ui_action.next_action, // Use next_action from state
                    player_id: 0,
                    amount: amount // The key is 'amount' for ActionSubmitAmount
                }));
                isAwaitingSubChoice = false;
                validActions = [];
            } else {
                ui.term.writeln(`\nInvalid amount: ${input}`);
                ui.promptForSubChoice(currentState.prompt, []);
            }
            return;
        }

        const choice = parseInt(command, 10);
        if (validActions && choice > 0 && choice <= validActions.length) {
            const selectedOption = validActions[choice - 1];
            // For sub-choices, we send a simplified object back with the choice as 'id'
            socket.send(JSON.stringify({
                action_type: currentState.pending_ui_action.next_action, // Use next_action from state
                player_id: 0,
                legislation_id: selectedOption.id // The key is 'legislation_id' for ActionSubmitLegislationChoice
            }));
            isAwaitingSubChoice = false;
            validActions = [];
        } else {
            ui.term.writeln(`\nInvalid choice: ${input}`);
            ui.promptForSubChoice(currentState.prompt, validActions);
        }
        return;
    }

    const choice = parseInt(command, 10);
    if (validActions && choice > 0 && choice <= validActions.length) {
        const action = validActions[choice - 1];
        
        // ALL actions are now sent as-is. The backend is fully state-driven.
        socket.send(JSON.stringify(action));
        validActions = []; // Clear actions after sending
    } else {
        ui.term.writeln(`\nInvalid choice: ${input}`);
        ui.promptForAction(validActions);
    }
};

module.exports = { TerminalUI }; 