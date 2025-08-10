let ws;

function connect() {
    console.log("🔌 Attempting to connect to WebSocket...");
    // Use secure WebSocket (wss) when page is loaded over HTTPS
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

    ws.onopen = () => {
        console.log("✅ WebSocket connection established");
    };

    ws.onmessage = (event) => {
        console.log("📨 Received WebSocket message:", event.data.length, "bytes");
        const state = JSON.parse(event.data);
        console.log("📊 Parsed state:", state);
        renderState(state);
    };

    ws.onclose = () => {
        console.log("❌ WebSocket connection closed. Attempting to reconnect...");
        setTimeout(connect, 3000);
    };

    ws.onerror = (error) => {
        console.error("❌ WebSocket error:", error);
    };
}

function getActionDescription(action) {
    console.log("🔍 Getting action description for:", action);
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
        case "ActionInitiateUseFavor":
            return `Use Favor: ${action.favor_description || action.favor_id}`;
        case "ActionUseFavor":
            return `Use Favor: ${action.favor_description || action.favor_id}`;
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
    console.log("🎨 Starting renderState with:", state);

    if (state.error) {
        console.error("🚨 Server error:", state.error);
        const logContainer = document.getElementById('log-container');
        const errorElement = document.createElement('div');
        errorElement.className = 'log-entry error';
        errorElement.textContent = `🚨 Server Error: ${state.error}`;
        logContainer.appendChild(errorElement);
        return;
    }
    
    console.log("👥 Rendering players...");
    const playersContainer = document.getElementById('players-container');
    console.log("📦 Players container found:", !!playersContainer);
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

    console.log("🎯 Rendering mandate...");
    const mandateContainer = document.getElementById('mandate-container');
    console.log("📦 Mandate container found:", !!mandateContainer);
    if (mandateContainer) {
        // Find the human player's mandate
        const humanPlayer = state.players.find(p => p.name === "Human");
        if (humanPlayer && humanPlayer.mandate) {
            console.log("📋 Human player mandate found:", humanPlayer.mandate);
            mandateContainer.innerHTML = `
                <div class="mandate-card">
                    <div class="mandate-title">${humanPlayer.mandate.title}</div>
                    <div class="mandate-description">${humanPlayer.mandate.description}</div>
                </div>
            `;
        } else {
            console.log("❌ No mandate found for human player");
            mandateContainer.innerHTML = '<p>No mandate assigned.</p>';
        }
    }

    console.log("🎮 Rendering game info...");
    const gameInfoContainer = document.getElementById('game-info-container');
    console.log("📦 Game info container found:", !!gameInfoContainer);
    gameInfoContainer.innerHTML = `
        <div>Round: ${state.round_marker}/4</div>
        <div>Term: ${state.term_counter + 1}/3</div>
        <div>Public Mood: ${state.public_mood}</div>
        <div>Phase: ${state.current_phase}</div>
    `;

    console.log("📜 Rendering legislation...");
    const legislationContainer = document.getElementById('legislation-container');
    console.log("📦 Legislation container found:", !!legislationContainer);
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

    console.log("📝 Rendering log...");
    const logContainer = document.getElementById('log-container');
    console.log("📦 Log container found:", !!logContainer);
    logContainer.innerHTML = '';
    state.log.forEach(entry => {
        const logElement = document.createElement('div');
        logElement.className = 'log-entry';
        logElement.textContent = entry;
        logContainer.appendChild(logElement);
    });
    logContainer.scrollTop = logContainer.scrollHeight;

    console.log("🔍 Finding human player...");
    const humanPlayer = state.players.find(p => p.name === "Human");
    console.log("👤 Human player found:", !!humanPlayer, humanPlayer);
    
    console.log("📦 Getting actions container...");
    const actionsContainer = document.getElementById('actions-container');
    console.log("📦 Actions container found:", !!actionsContainer);
    actionsContainer.innerHTML = '';

    console.log("🤖 Checking for AI acknowledgment...");
    if (state.awaiting_acknowledgement) {
        console.log("⏳ Awaiting AI acknowledgment, showing prompt...");
        promptForAcknowledgement();
    } else if (humanPlayer && state.current_player_index === humanPlayer.id) {
        console.log("✅ Human turn detected!");
        console.log("📋 Checking for prompt...");
        if (state.prompt) {
            console.log("❓ Showing prompt:", state.prompt);
            console.log("📋 State options:", state.options);
            console.log("📋 State expects_input:", state.expects_input);
            promptForSubChoice(state.prompt, state.options, state.expects_input);
        } else {
            console.log("🔘 Checking for valid actions...");
            if (state.valid_actions && state.valid_actions.length > 0) {
                console.log(`✅ Found ${state.valid_actions.length} valid actions:`, state.valid_actions);
                state.valid_actions.forEach(action => {
                    console.log("🔘 Creating button for action:", action);
                    const button = document.createElement('button');
                    button.textContent = getActionDescription(action);
                    button.onclick = () => {
                        console.log("🖱️ Button clicked for action:", action);
                        sendAction(action);
                    };
                    actionsContainer.appendChild(button);
                    console.log("✅ Button added to container");
                });
                console.log("✅ All action buttons created");
            } else {
                console.log("❌ No valid actions found");
            }
        }
    } else {
        console.log("⏳ Not human turn, showing waiting message...");
        actionsContainer.innerHTML = '<div class="prompt">Waiting for AI player...</div>';
    }
    
    console.log("🎨 renderState completed");
}


function promptForSubChoice(promptText, options, expects_input) {
    console.log("🔍 promptForSubChoice called with:", { promptText, options, expects_input });
    
    const actionsContainer = document.getElementById('actions-container');
    console.log("📦 Actions container found:", !!actionsContainer);
    actionsContainer.innerHTML = '';

    const promptElement = document.createElement('div');
    promptElement.className = 'prompt';
    promptElement.textContent = promptText;
    actionsContainer.appendChild(promptElement);
    console.log("✅ Prompt element created:", promptText);

    if (expects_input === 'amount') {
        console.log("💰 Creating amount input...");
        const input = document.createElement('input');
        input.type = 'number';
        input.className = 'input-field';
        input.placeholder = 'Enter amount...';
        
        const submitButton = document.createElement('button');
        submitButton.textContent = 'Submit';
        submitButton.onclick = () => {
            const amount = parseInt(input.value, 10);
            if (!isNaN(amount) && amount > 0) {
                console.log("💰 Sending amount:", amount);
                sendAction({ choice: amount });
            } else {
                promptElement.textContent = "Please enter a valid positive number.";
            }
        };
        
        actionsContainer.appendChild(input);
        actionsContainer.appendChild(submitButton);
        input.focus();
        console.log("✅ Amount input created");

    } else if (options && options.length > 0) {
        console.log(`🔘 Creating ${options.length} option buttons...`);
        options.forEach((option, index) => {
            console.log(`🔘 Creating option ${index + 1}:`, option);
            const button = document.createElement('button');
            button.textContent = option.display_name;
            button.onclick = () => {
                console.log("🖱️ Option clicked:", option);
                sendAction({ choice: option.id });
            };
            actionsContainer.appendChild(button);
            console.log(`✅ Option button ${index + 1} created:`, option.display_name);
        });
        console.log("✅ All option buttons created");
    } else {
        console.log("❌ No options provided or options array is empty");
        console.log("Options:", options);
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

// Add mandate toggle functionality
function setupMandateToggle() {
    const toggleButton = document.getElementById('mandate-toggle');
    const mandateContainer = document.getElementById('mandate-container');
    
    if (toggleButton && mandateContainer) {
        toggleButton.addEventListener('click', () => {
            if (mandateContainer.classList.contains('mandate-hidden')) {
                mandateContainer.classList.remove('mandate-hidden');
                toggleButton.textContent = 'Hide Mandate';
            } else {
                mandateContainer.classList.add('mandate-hidden');
                toggleButton.textContent = 'Show Mandate';
            }
        });
    }
}

connect();
setupMandateToggle(); 