let ws;

function connect() {
    ws = new WebSocket(`ws://${window.location.host}/ws`);

    ws.onopen = () => {
        console.log("Connected to the game server.");
    };

    ws.onmessage = (event) => {
        const state = JSON.parse(event.data);
        renderState(state);
    };

    ws.onclose = () => {
        console.log("Disconnected from the game server. Attempting to reconnect...");
        setTimeout(connect, 3000); // Try to reconnect every 3 seconds
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
    };
}

function getActionDescription(action) {
    const type = action.action_type;
    const simpleType = type.replace("ActionInitiate", "").replace("Action", "");

    switch (type) {
        case "ActionInitiateSponsorLegislation":
            return "Sponsor Legislation";
        case "ActionInitiateSupportLegislation":
            return "Support Legislation";
        case "ActionInitiateOpposeLegislation":
            return "Oppose Legislation";
        case "ActionInitiateDeclareCandidacy":
            return "Declare Candidacy";
        case "ActionFundraise":
            return "Fundraise";
        case "ActionNetwork":
            return "Network";
        case "ActionPassTurn":
            return "Pass Turn";
        case "ActionResolveLegislation":
            return "Resolve Legislation";
        case "ActionResolveElections":
            return "Resolve Elections";
        case "ActionAcknowledgeResults":
            return "Start Next Term";
        default:
            return simpleType.replace(/([A-Z])/g, ' $1').trim();
    }
}

function renderState(state) {
    console.log("Received state:", state);

    if (state.error) {
        console.error("Server error:", state.error);
        const logContainer = document.getElementById('log-container');
        const errorElement = document.createElement('div');
        errorElement.className = 'log-entry error';
        errorElement.textContent = `🚨 Server Error: ${state.error}`;
        logContainer.appendChild(errorElement);
        return;
    }
    
    const playersContainer = document.getElementById('players-container');
    playersContainer.innerHTML = '';
    state.players.forEach(player => {
        const playerDiv = document.createElement('div');
        playerDiv.className = `player-info ${player.id === state.current_player_index ? 'current-player' : ''}`;
        
        let officeText = player.current_office ? player.current_office.title : "No Office";
        let archetypeText = player.archetype ? player.archetype.title : 'No Archetype';
        if (state.compromised_players && state.compromised_players.includes(player.id)) {
            archetypeText = `🎭 ${archetypeText} (Revealed)`;
        }

        playerDiv.innerHTML = `
            <div class="player-name">${player.name} ${player.id === state.current_player_index ? ' (Current)' : ''}</div>
            <div class="player-details">
                <span>Political Capital: ${player.pc}</span> | 
                <span>Action Points: ${state.action_points[player.id]}</span> | 
                <span>Favors: ${player.favors.length}</span> |
                <span>Office: ${officeText}</span> |
                <span>Archetype: ${archetypeText}</span>
            </div>
        `;
        playersContainer.appendChild(playerDiv);
    });

    const gameInfoContainer = document.getElementById('game-info-container');
    gameInfoContainer.innerHTML = `
        <div>Round: ${state.round_marker}/4</div>
        <div>Term: ${state.term_counter + 1}/3</div>
        <div>Public Mood: ${state.public_mood}</div>
        <div>Phase: ${state.current_phase}</div>
    `;

    const legislationContainer = document.getElementById('legislation-container');
    legislationContainer.innerHTML = '<h3>Active Legislation</h3>';
    if (state.term_legislation && state.term_legislation.length > 0) {
        state.term_legislation.forEach(leg => {
            const legDetails = state.legislation_options[leg.legislation_id];
            const sponsor = state.players.find(p => p.id === leg.sponsor_id);
            const legDiv = document.createElement('div');
            legDiv.className = 'legislation-item';
            legDiv.innerHTML = `
                <strong>${legDetails.title}</strong> (Sponsored by ${sponsor ? sponsor.name : 'Unknown'})
            `;
            legislationContainer.appendChild(legDiv);
        });
    } else {
        legislationContainer.innerHTML += '<p>None this term.</p>';
    }

    const logContainer = document.getElementById('log-container');
    logContainer.innerHTML = '';
    state.log.forEach(entry => {
        const logElement = document.createElement('div');
        logElement.className = 'log-entry';
        logElement.textContent = entry;
        logContainer.appendChild(logElement);
    });
    logContainer.scrollTop = logContainer.scrollHeight;

    const humanPlayer = state.players.find(p => p.name === "Human");
    const actionsContainer = document.getElementById('actions-container');
    actionsContainer.innerHTML = '';

    if (state.awaiting_acknowledgement) {
        promptForAcknowledgement();
    } else if (humanPlayer && state.current_player_index === humanPlayer.id) {
        if (state.prompt) {
            promptForSubChoice(state.prompt, state.options, state.expects_input);
        } else {
            if (state.valid_actions && state.valid_actions.length > 0) {
                state.valid_actions.forEach(action => {
                    const button = document.createElement('button');
                    button.textContent = getActionDescription(action);
                    button.onclick = () => sendAction(action);
                    actionsContainer.appendChild(button);
                });
            }
        }
    } else {
        actionsContainer.innerHTML = '<div class="prompt">Waiting for AI player...</div>';
    }
}


function promptForSubChoice(promptText, options, expects_input) {
    const actionsContainer = document.getElementById('actions-container');
    actionsContainer.innerHTML = '';

    const promptElement = document.createElement('div');
    promptElement.className = 'prompt';
    promptElement.textContent = promptText;
    actionsContainer.appendChild(promptElement);

    if (expects_input === 'amount') {
        const input = document.createElement('input');
        input.type = 'number';
        input.className = 'input-field';
        input.placeholder = 'Enter amount...';
        
        const submitButton = document.createElement('button');
        submitButton.textContent = 'Submit';
        submitButton.onclick = () => {
            const amount = parseInt(input.value, 10);
            if (!isNaN(amount) && amount > 0) {
                sendAction({ choice: amount });
            } else {
                promptElement.textContent = "Please enter a valid positive number.";
            }
        };
        
        actionsContainer.appendChild(input);
        actionsContainer.appendChild(submitButton);
        input.focus();

    } else if (options && options.length > 0) {
        options.forEach(option => {
            const button = document.createElement('button');
            button.textContent = option.display_name;
            button.onclick = () => sendAction({ choice: option.id });
            actionsContainer.appendChild(button);
        });
    }
}

function promptForAcknowledgement() {
    const actionsContainer = document.getElementById('actions-container');
    actionsContainer.innerHTML = '';

    const promptElement = document.createElement('div');
    promptElement.className = 'prompt';
    promptElement.textContent = "AI has taken its turn. Press Enter to continue...";
    actionsContainer.appendChild(promptElement);

    const ackButton = document.createElement('button');
    ackButton.textContent = "Continue";
    ackButton.onclick = () => sendAcknowledgement();
    actionsContainer.appendChild(ackButton);
    ackButton.focus();

    const enterListener = (event) => {
        if (event.key === 'Enter') {
            document.removeEventListener('keydown', enterListener);
            sendAcknowledgement();
        }
    };
    document.addEventListener('keydown', enterListener);
}

function sendAction(action) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify(action));
    }
}

function sendAcknowledgement() {
    sendAction({ action_type: "AcknowledgeAITurn" });
}

connect(); 