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

        if (state.current_phase === "ACTION_PHASE") {
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
            case 'UISupportLegislation': return `\x1B[92m✅ Support Legislation\x1B[0m`;
            case 'UIOpposeLegislation': return `\x1B[91m❌ Oppose Legislation\x1B[0m`;
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

socket.onopen = () => {
    ui.term.writeln('Connected to server.');
};

socket.onmessage = function(event) {
    const gameState = JSON.parse(event.data);
    currentState = gameState;
    ui.displayGameState(gameState);

    if (gameState.awaiting_ai_acknowledgement) {
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
    options.forEach((action, index) => {
        // Assuming the sub-options have a user-friendly text description
        this.term.writeln(`  \x1B[1;93m[${index + 1}]\x1B[0m ${action.text || action.legislation_id}`);
    });
    this.term.write('\nEnter your choice: ');
};


ui.onEnter = (input) => {
    const command = input.trim().toLowerCase();

    if (currentState.awaiting_ai_acknowledgement) {
        socket.send(JSON.stringify({ action_type: 'AcknowledgeAITurn', player_id: 0 })); // Assuming human is player 0
        return;
    }

    // If it's not the human's turn, any 'enter' is a continue.
    if (!validActions || validActions.length === 0) {
        socket.send(JSON.stringify({ action_type: 'continue' }));
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
        const choice = parseInt(command, 10);
        if (validActions && choice > 0 && choice <= validActions.length) {
            const action = validActions[choice - 1];
            // For sub-choices, we send a simplified object back
            socket.send(JSON.stringify({
                action_type: action.action_type,
                choice: action.legislation_id // Or other identifier like office_id
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
        
        // If it's a UI action, we just send it. The backend will prompt for more.
        if (action.is_ui_action) {
            socket.send(JSON.stringify(action));
        } else {
            // This handles regular, one-step actions
            socket.send(JSON.stringify(action));
        }
        validActions = []; // Clear actions after sending
    } else {
        ui.term.writeln(`\nInvalid choice: ${input}`);
        ui.promptForAction(validActions);
    }
};

module.exports = { TerminalUI }; 