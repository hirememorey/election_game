# Enhanced Simulation Framework

## Overview

The enhanced simulation framework enables large-scale, automated playtesting of the Election Game with comprehensive analysis capabilities. It is designed to run thousands of games using configurable player personas (AI strategies) and collect detailed results for balance analysis, bug detection, and strategy evaluation.

## Key Features

### Core Framework
- **Configuration-driven:** Simulations are controlled via a YAML config file (`simulation_config.yaml`), supporting multiple experiments in a single run
- **Persona System:** Player strategies are implemented as modular Python classes in the `personas/` directory. Included personas: `RandomPersona`, `EconomicPersona`, `LegislativePersona`, `BalancedPersona`
- **Robust Results Logging:** Results are saved as both CSV and JSON, with a custom encoder that handles all nested types (including sets) for future-proof extensibility
- **First Principles Design:** The framework was built and redteamed from first principles for simplicity, extensibility, and reliability

### Enhanced Analysis Capabilities
- **Comprehensive Metrics:** Win rates, game length statistics, action frequency analysis, and economic performance metrics
- **Multi-format Reporting:** Markdown reports, CSV exports, and console summaries with automatic balance assessment
- **Flexible Analysis:** Support for both individual experiment and cross-experiment analysis
- **Structured Data:** `AnalysisMetrics` dataclass for organized data storage and processing

### Multi-Experiment Support
- **Batch Processing:** Run multiple experiments in a single execution
- **Organized Output:** Each experiment gets its own directory with detailed results
- **Strategy Comparison:** Systematic comparison of different player strategies
- **Flexible Configuration:** Easy experiment definition without code changes

### Improved Robustness
- **Error Handling:** Graceful handling of simulation failures with detailed error reporting
- **Tracing Support:** Optional game state tracing for detailed analysis and debugging
- **Enhanced Logging:** Configurable verbosity levels with actionable error messages
- **Recovery Mechanisms:** Automatic recovery and continuation from failures

## Usage

### Basic Usage
```bash
# Run with default configuration
python3 simulation_runner.py

# Run with custom configuration
python3 simulation_runner.py --config my_config.yaml

# Generate reports
python3 simulation_runner.py --config my_config.yaml --report
```

### Analysis Usage
```python
from analysis import SimulationAnalyzer

# Analyze results
analyzer = SimulationAnalyzer("simulation_results")
analyzer.load_results()
metrics = analyzer.calculate_metrics()
report = analyzer.generate_report()
analyzer.print_summary()
```

### Multi-Experiment Configuration
```yaml
global:
  random_seed: 42
  max_rounds_per_game: 100
  parallel_workers: 0
  output_directory: "simulation_results"

data_collection:
  log_level: "silent"
  save_game_logs: true
  save_final_states: true
  enable_tracing: false

experiments:
  - name: "basic_balance"
    description: "Test basic game balance"
    num_games: 100
    players:
      - name: "Random Bot"
        persona: "random"
      - name: "Economic Bot"
        persona: "economic"
```

## File Structure

```
election/
├── analysis.py                    # Comprehensive analysis module
├── simulation_config.yaml         # Multi-experiment configuration
├── simulation_runner.py           # Multi-experiment support
├── simulation_harness.py          # Error handling and tracing
├── personas/
│   └── base_persona.py           # Enhanced persona interface
├── enhanced_simulation_demo.py    # Comprehensive demonstration
├── test_analysis_simple.py       # Analysis testing
└── test_file_structure.py        # File structure testing
```

## Key Components

### SimulationAnalyzer
- `load_results()`: Flexible file loading with pattern matching
- `calculate_metrics()`: Comprehensive statistical analysis
- `generate_report()`: Markdown-formatted reports
- `print_summary()`: Console-friendly summaries

### SimulationRunner
- `run_simulation_batch()`: Multi-experiment execution
- Enhanced error handling and progress reporting
- Organized output management

### AnalysisMetrics
- Structured data storage for all analysis results
- Support for win rates, game lengths, action frequencies
- Economic analysis and balance assessment

## Extending the Framework

### Add New Personas
Implement a new class in `personas/` inheriting from `BasePersona`:
```python
from personas.base_persona import BasePersona

class MyCustomPersona(BasePersona):
    def choose_action(self, game_state, valid_actions):
        # Implement your strategy here
        return chosen_action
```

### Create Custom Experiments
Update `simulation_config.yaml` to add new experiments:
```yaml
experiments:
  - name: "my_custom_test"
    description: "Custom experiment"
    num_games: 50
    players:
      - name: "Custom Bot"
        persona: "my_custom"
```

### Add Custom Analysis
Extend the `AnalysisMetrics` dataclass and `SimulationAnalyzer` class to add new metrics and analysis capabilities.

## Testing

The framework includes comprehensive testing:
- `test_simulation_framework.py`: Core framework tests
- `test_small_simulation.py`: End-to-end simulation test
- `test_analysis_simple.py`: Analysis module tests
- `test_file_structure.py`: File structure validation
- `enhanced_simulation_demo.py`: Comprehensive demonstration

## Performance Characteristics

- **Speed:** Average simulation time ~0.007 seconds per game
- **Scalability:** Support for parallel processing (configurable)
- **Reliability:** Comprehensive error handling and recovery mechanisms
- **Memory Efficiency:** Organized data structures and output management

## Recent Enhancements

### Phase 1: Enhanced Results Analysis
- Comprehensive metrics calculation with win rates, game lengths, and economic analysis
- Multi-format reporting with automatic balance assessment
- Flexible file loading supporting multiple naming patterns

### Phase 2: Multi-Experiment Support
- Configuration-driven experiment definition
- Organized output with experiment-specific directories
- Systematic strategy comparison capabilities

### Phase 3: Improved Robustness
- Comprehensive error handling throughout the pipeline
- Optional game state tracing for detailed analysis
- Enhanced logging with configurable verbosity

### Phase 4: Enhanced Persona Interface
- Improved base persona with better documentation
- Pre-validated action lists for reliability
- Enhanced error handling in persona implementations

## Demonstration Results

The framework successfully demonstrates:
- **Multi-experiment execution** with organized output
- **Comprehensive analysis** revealing balance insights
- **Performance optimization** with efficient processing
- **Robust error handling** with graceful recovery

Example results from demonstration:
- Economic Bot: 93.3% win rate vs Legislative Bot: 6.7% win rate
- Clear identification of balance issues favoring economic strategies
- Detailed metrics and reporting for actionable insights

---

For more details, see the code in `simulation_runner.py`, `analysis.py`, `personas/`, and the test scripts. The enhanced framework provides a solid foundation for ongoing game balance analysis and development.

## Future Direction: Quantifying Skill vs. Luck

### Objective

The next phase of simulation work is to analyze and tune the game's balance of skill and luck. The goal is to achieve a ratio akin to Texas Hold 'Em, where skill is the dominant factor in long-term success, but a sufficient luck component ensures that any single game is unpredictable and exciting. This requires a systematic approach to measure the impact of player decisions versus random events.

### The Hybrid Path Forward: A Three-Phase Plan

This plan combines two core strategies: "Skill Spectrum Analysis" using AI personas and "Luck Knob Analysis" to perform sensitivity analysis on the game's random elements.

#### Phase 1: Establish the Skill Baseline

This phase answers the question: "As the game is currently designed, what is the raw advantage of skillful play over random chance?"

1.  **Persona Development**:
    *   **`CluelessCarl` (The Baseline)**: This persona represents 0% skill. It understands the rules but makes uniformly random choices from the list of valid actions. It commits random amounts of PC. Its performance is the benchmark for a game outcome driven by pure luck.
    *   **`StrategicSamantha` (The Skilled Proxy)**: This persona represents a skilled human player. It uses complex heuristics, such as tracking opponent resources, estimating their secret objectives based on their actions, and, crucially, **bluffing** in the Secret Commitment system.

2.  **Simulation Experiment: The Skill Delta Test**
    *   **Setup**: Run a large batch of simulations (e.g., 10,000 games) with one `StrategicSamantha` against three `CluelessCarls`.
    *   **Metric**: Measure Samantha's win rate. In a 4-player game, a purely random outcome would yield a 25% win rate. The deviation from this baseline quantifies the "skill edge." A 35% win rate suggests a small edge, while a 75% win rate might indicate the game is too deterministic.

#### Phase 2: Test Strategic Viability

This phase ensures the game has a healthy, balanced meta where multiple strategies can succeed, preventing a single "optimal" strategy from dominating.

1.  **Additional Persona Development**:
    *   **`GreedyGus` (The Economist)**: A one-dimensional persona that prioritizes maximizing its own PC above all else, almost always choosing to Fundraise.
    *   **`LegislativeLarry` (The Specialist)**: A focused persona that only sponsors or supports legislation aligning with its secret mandate, ignoring other opportunities.

2.  **Simulation Experiment: The Meta-Balance Test**
    *   **Setup**: Run 10,000 simulations with one of each of the four personas.
    *   **Metric**: Analyze the win-rate distribution. A healthy meta would see `StrategicSamantha` winning most often, but with `Larry` and `Gus` having a reasonable chance if the game's random events favor their playstyle. If `GreedyGus` consistently wins, it may indicate the game's economy is unbalanced.

#### Phase 3: Tune the Luck Knobs

This phase isolates the impact of specific random mechanics to see how they influence the established skill and meta baselines.

1.  **Identify "Luck Knobs"**:
    *   **Election Randomness**: The dice roll used in election resolution.
    *   **Event Card Impact**: The magnitude of PC or Influence swings from Event Cards.
    *   **Favor Card Pool**: The distribution of powerful vs. weak cards in the Political Favor deck.

2.  **Simulation Experiment: Sensitivity Analysis**
    *   **Setup**: Re-run the "Skill Delta Test" and "Meta-Balance Test" under modified conditions.
    *   **Example Scenario ("Pure Skill Election")**: Set the election dice roll to 0 for all players. The winner is determined solely by deterministic factors like committed PC.
    *   **Metric**: How much does Samantha's win rate change when this luck element is removed? If it jumps from 40% to 80%, it indicates the dice roll has an outsized impact on the game's outcome, potentially invalidating a game's worth of skillful play. This allows for fine-tuning (e.g., changing from a d6 to a d3 roll) to achieve the desired balance.

### Red Teaming & Caveats

*   **Assumption**: AI personas are perfect proxies for human players.
*   **Critique**: This is false. Humans are emotional, irrational, and are influenced by social dynamics not present in the simulation.
*   **Conclusion**: This framework's purpose is not to perfectly simulate a human playgroup, but to **test the mechanical and mathematical robustness of the game's core systems.** It ensures that no single strategy is inherently broken and that the intended skill-based mechanics are not being completely invalidated by random chance. A mechanically sound game is the necessary foundation upon which a rich, human-driven psychological meta can be built. 