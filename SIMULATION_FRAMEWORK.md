# Simulation Framework

The Election Game now includes a comprehensive simulation framework for game balance analysis and automated testing.

## Overview

The simulation framework allows for headless execution of games without the web interface, enabling:
- **Automated Testing**: Run thousands of games quickly
- **Balance Analysis**: Compare different strategies and game mechanics
- **Agent Development**: Create and test AI players with different strategies
- **Tournament Systems**: Run competitions between different agent types

## Quick Start

### Basic Usage

```bash
# Run a single simulation with detailed analysis
python3 run_single_simulation.py

# Run a single simulation with random agents
python simulation_harness.py

# Run comprehensive tests
python test_simulation_framework.py
```

### Expected Output

```
🎮 ELECTION GAME - SINGLE SIMULATION
==================================================

🚀 Starting simulation...
Starting simulation with 4 players: ['Alice', 'Bob', 'Charlie', 'Diana']

--- Round 1 ---
Current player: Alice
Phase: ACTION_PHASE
Action Points: {0: 2, 1: 2, 2: 2, 3: 2}
Alice chose: ActionFundraise
...

🏆 WINNER ANALYSIS: Bob

📊 FINAL SCORE: 7 influence points

🎭 PLAYER IDENTITY:
• Archetype: The Insider
• Mandate: The Grassroots Movement

💰 RESOURCES:
• Political Capital: 21 PC
• Current Office: State Senator

🏛️ INFLUENCE BREAKDOWN:
• +5 Influence from holding office: State Senator
• +2 Influence from 21 PC remaining (1/10 conversion)

🎯 VICTORY FACTORS:
• Held the State Senator office
• Converted 21 PC to 2 influence points

📈 COMPARISON TO OTHER PLAYERS:
• Alice: 6 points (winner by 1 points)
• Charlie: 0 points (winner by 7 points)
• Diana: 1 points (winner by 6 points)

📊 GAME STATISTICS:
• Game Length: 53 rounds, 3 terms
• Simulation Time: 0.001 seconds
```

## Architecture

### Core Components

#### `SimulationHarness`
The main simulation engine that:
- Manages game state without web interface
- Handles all phase transitions automatically
- Provides clean API for agent integration
- **NEW**: Uses pluggable logging system for flexible data collection

#### `GameEngine` (Enhanced)
The engine now serves as the single source of truth for:
- **Valid Action Determination**: Only the engine determines what actions are available
- **Action Point Validation**: Properly checks costs including dynamic modifiers
- **Resource Requirements**: Validates PC, favors, and other resource constraints
- **Timing Rules**: Enforces proper timing restrictions (e.g., candidacy in round 4)

#### `Agent` Base Class
A new abstract base class that:
- Provides consistent interface for all agents
- Ensures deterministic behavior
- Simplifies agent development
- Supports both simple and complex agent strategies
- **NEW**: Receives comprehensive game state including game log for strategic decisions

#### `MetricsLogger` (NEW)
A pluggable logging system that:
- **Separates Concerns**: Simulation logic is independent of data collection
- **Flexible Output**: VerboseLogger for debugging, SilentLogger for speed
- **Extensible**: Easy to add new loggers (database, file, etc.)
- **Performance**: Can run thousands of simulations silently for analysis

#### `ScriptedAgent` (NEW)
A deterministic agent for testing that:
- **Follows Predetermined Actions**: Executes a specific sequence of actions
- **Validates Rules**: Ensures scripted actions are actually valid
- **Enables Testing**: Perfect for testing specific game scenarios and edge cases
- **Deterministic Results**: Same inputs always produce same outputs

### Game Flow

1. **Initialization**: Create game state with specified players
2. **Action Phase**: Agents choose actions based on available AP
3. **Legislation Phase**: Auto-resolve pending legislation
4. **Election Phase**: Auto-resolve elections and determine winners
5. **Term Transition**: Start new term or end game after 3 terms
6. **Scoring**: Calculate final influence and determine winner

## Agent Interface

### Creating Custom Agents

Agents must implement the following interface:

```python
class CustomAgent(Agent):
    def choose_action(self, state: GameState, valid_actions: List[Action]) -> Action:
        """
        Choose an action for the given player in the current game state.
        
        Args:
            state: Current game state (includes game_log for strategic agents)
            valid_actions: List of valid actions from the engine
            
        Returns:
            Action: The chosen action to take
        """
        # Your agent logic here
        return chosen_action
```

### Available Actions

- `ActionFundraise`: Gain Political Capital
- `ActionNetwork`: Build connections
- `ActionSponsorLegislation`: Create legislation
- `ActionSupportLegislation`: Support pending legislation
- `ActionOpposeLegislation`: Oppose pending legislation
- `ActionDeclareCandidacy`: Run for office (round 4 only)
- `ActionUseFavor`: Use political favors
- `ActionPassTurn`: Skip turn

### State Information

The `GameState` object provides access to:
- `state.players`: List of all players
- `state.action_points`: Current AP for each player
- `state.current_phase`: Current game phase
- `state.term_legislation`: Pending legislation for voting
- `state.pending_legislation`: Currently active legislation
- `state.public_mood`: Current public mood (-3 to +3)
- `state.round_marker`: Current round number
- `state.turn_log`: Complete game history for strategic agents

## Testing & Validation

### Comprehensive Test Suite

The framework includes 16 comprehensive tests that validate:

#### Core Architecture Tests
- **Engine Single Source of Truth**: Only engine determines valid actions
- **Action Point Validation**: Actions respect AP costs including modifiers
- **Agent Interface Consistency**: Agents make consistent decisions
- **State Management**: Proper state transitions and data integrity

#### Game Logic Tests
- **Valid Action Generation**: Actions properly filtered
- **Action Resolution**: Actions processed correctly
- **Turn Advancement**: Proper turn progression
- **Game Phase Transitions**: Phase changes work correctly

#### Timing and Rules Tests
- **Candidacy Declaration Timing**: Only available in round 4 with sufficient PC
- **Action Point Costs**: Dynamic cost calculations including public gaffe effects
- **Resource Requirements**: Actions respect PC, favor, and other constraints

#### System Integration Tests
- **System Action Handling**: Legislation and election resolution
- **Simulation Termination**: Games complete properly
- **Final Score Structure**: Proper score calculation and format
- **Agent Decision Making**: Agents can make valid choices
- **State Consistency**: State remains consistent throughout simulation

### Test Results

- **Execution Time**: 0.255 seconds for 16 comprehensive tests
- **Success Rate**: 100% (16/16 tests passing)
- **Coverage**: All critical paths including edge cases
- **Reliability**: Deterministic results for reproducible analysis

## Analysis Capabilities

### Performance Metrics

The simulation tracks:
- **Win Rates**: Percentage of games won by each agent type
- **Game Length**: Average rounds and terms per game
- **Action Distribution**: How often each action is chosen
- **Resource Efficiency**: PC and AP usage patterns
- **Strategy Effectiveness**: Which approaches lead to victory

### Balance Analysis

The framework enables analysis of:
- **Action Point Costs**: Are actions appropriately priced?
- **Political Capital Economy**: Is PC generation/consumption balanced?
- **Office Values**: Are influence bonuses appropriate?
- **Event Impact**: How do random events affect game balance?
- **Strategy Diversity**: Are multiple viable paths to victory?

## Recent Improvements

### Phase 2: Architecture Refinement (Latest)

#### Enhanced Separation of Concerns
- **MetricsLogger Interface**: Separated simulation logic from data collection
- **Pluggable Logging**: Can swap between verbose debugging and silent analysis
- **Flexible Output**: Easy to add new loggers (database, file, etc.)
- **Performance Optimization**: Silent logger enables thousands of simulations

#### Improved Agent System
- **ScriptedAgent**: New deterministic agent for precise testing
- **Enhanced GameState**: Agents receive comprehensive game history
- **Strategic Information**: Agents can access turn_log for pattern recognition
- **Information Parity**: Agents have same information level as human players

#### Better Testing Infrastructure
- **Deterministic Testing**: ScriptedAgent enables precise scenario testing
- **Rule Validation**: Can test specific edge cases and game rules
- **Reproducible Results**: Same inputs always produce same outputs
- **Comprehensive Coverage**: All critical paths tested including edge cases

### Phase 1: Core Architecture Refinement (Previous)

#### Enhanced Game Engine
- **Single Source of Truth**: Engine now exclusively determines valid actions
- **Dynamic Cost Validation**: Properly handles modifiers like public gaffe effects
- **Resource Requirement Checking**: Validates PC, favors, and timing constraints
- **System Action Support**: Added support for legislation and election resolution

#### Simplified Agent Interface
- **Abstract Base Class**: New `Agent` base class for consistent interface
- **Deterministic Behavior**: Same inputs produce same outputs consistently
- **Cleaner API**: Simplified action selection process
- **Better Error Handling**: Robust validation and error reporting

#### Improved State Management
- **Consistent State Transitions**: Proper phase progression and flag clearing
- **Resource Integrity**: All actions respect resource constraints
- **Timing Rule Enforcement**: Actions follow proper timing restrictions
- **System Integration**: All components work together seamlessly

### Red-Teaming Validation

The framework has been thoroughly tested using first principles and red-teaming methodology:

#### Key Validations
1. **Single Responsibility Principle**: Each component has one clear job
2. **Separation of Concerns**: Simulation logic independent of data collection
3. **Information Parity**: Agents have same information as human players
4. **Deterministic Behavior**: Same inputs produce same outputs consistently
5. **Resource Integrity**: All actions respect resource constraints
6. **State Consistency**: Game state remains valid throughout simulation
7. **Timing Rules**: Actions follow proper timing restrictions
8. **System Integration**: All components work together seamlessly

#### Performance Metrics
- **Test Execution Time**: 0.255 seconds for 16 comprehensive tests
- **Code Coverage**: All critical paths tested including edge cases
- **Error Rate**: 0 failures, 0 errors
- **Simulation Stability**: Games complete successfully with proper termination

## Future Development

### Planned Features

1. **Advanced Agents**
   - Strategic agents that plan multiple turns ahead
   - Learning agents that adapt to opponent strategies
   - Specialized agents for different playstyles

2. **Tournament System**
   - Round-robin competitions between agent types
   - Elo rating system for agent performance
   - Automated tournament reporting

3. **Balance Testing**
   - Automated detection of dominant strategies
   - Statistical analysis of game balance
   - Parameter optimization for game mechanics

4. **Visualization Tools**
   - Charts showing agent performance over time
   - Strategy analysis dashboards
   - Real-time tournament progress tracking

### Integration with Web Version

The simulation framework is completely separate from the web version:
- **No Impact**: Web game functionality unchanged
- **Shared Engine**: Both use the same core game logic
- **Independent Testing**: Can test balance without affecting live games 