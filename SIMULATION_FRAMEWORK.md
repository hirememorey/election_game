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
# Run a single simulation with random agents
python simulation_harness.py
```

### Expected Output

```
Testing Simulation Harness...
Starting simulation with 4 players: ['Alice', 'Bob', 'Charlie', 'Diana']

--- Round 1 ---
Current player: Alice
Phase: ACTION_PHASE
Action Points: {0: 2, 1: 2, 2: 2, 3: 2}
Alice chose: ActionFundraise
...

--- Simulation Complete ---
Winner: Alice
Rounds: 44, Terms: 3
Final Scores: {...}
Simulation Time: 0.002s
```

## Architecture

### Core Components

#### `SimulationHarness`
The main simulation engine that:
- Manages game state without web interface
- Handles all phase transitions automatically
- Provides clean API for agent integration
- Tracks comprehensive game metrics

#### `RandomAgent`
A simple agent that:
- Chooses actions randomly from available options
- Respects action point costs
- Provides baseline performance for comparison

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
def custom_agent(state: GameState, player_id: int) -> Action:
    """
    Choose an action for the given player in the current game state.
    
    Args:
        state: Current game state
        player_id: ID of the player making the decision
        
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
- `ActionDeclareCandidacy`: Run for office
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
- **Parallel Development**: Can develop new features in simulation first

## Technical Details

### Performance

- **Speed**: ~0.002 seconds per complete game
- **Scalability**: Can run thousands of games per minute
- **Memory**: Minimal memory footprint for large-scale testing
- **Reliability**: Deterministic results for reproducible analysis

### Error Handling

- **Action Validation**: Prevents invalid actions
- **State Consistency**: Maintains game state integrity
- **Graceful Degradation**: Handles edge cases without crashing
- **Comprehensive Logging**: Detailed logs for debugging

### Testing

The framework includes:
- **Unit Tests**: Individual component testing
- **Integration Tests**: Full game flow testing
- **Performance Tests**: Speed and memory testing
- **Balance Tests**: Statistical analysis of game outcomes

## Contributing

To contribute to the simulation framework:

1. **Create New Agents**: Implement new agent strategies
2. **Add Analysis Tools**: Create new metrics and visualizations
3. **Improve Performance**: Optimize simulation speed
4. **Extend Capabilities**: Add new testing features

See the main `README.md` for general contribution guidelines. 