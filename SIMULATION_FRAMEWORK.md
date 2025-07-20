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