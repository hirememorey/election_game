# Simulation Framework

## Overview

The simulation framework enables large-scale, automated playtesting of the Election Game. It is designed to run thousands of games using configurable player personas (AI strategies) and collect detailed results for balance analysis, bug detection, and strategy evaluation.

## Key Features

- **Configuration-driven:** Simulations are controlled via a YAML config file (`simulation_config.yaml`), specifying the number of games, player personas, and data collection options.
- **Persona System:** Player strategies are implemented as modular Python classes in the `personas/` directory. Included personas: `RandomPersona`, `EconomicPersona`, `LegislativePersona`, `BalancedPersona`.
- **Robust Results Logging:** Results are saved as both CSV and JSON, with a custom encoder that handles all nested types (including sets) for future-proof extensibility.
- **First Principles Design:** The framework was built and redteamed from first principles for simplicity, extensibility, and reliability. All assumptions about serialization, agent design, and configuration were challenged and validated.

## Usage

1. **Configure the Simulation**
   - Edit `simulation_config.yaml` to set the number of games, player personas, and output options.

2. **Run Simulations**
   - Execute the runner: `python3 simulation_runner.py` or use the test script: `python3 test_small_simulation.py`

3. **Analyze Results**
   - Results are saved in the specified output directory as CSV and JSON. The JSON output is fully serializable, even for complex nested game state objects.

## Extending the Framework

- **Add New Personas:** Implement a new class in `personas/` inheriting from `BasePersona`.
- **Change Config:** Update `simulation_config.yaml` to use new personas or adjust simulation parameters.
- **Serialization:** The framework uses a custom JSON encoder to ensure all data (including sets, tuples, and nested objects) is saved without error.

## Testing

- The framework includes comprehensive tests in `test_simulation_framework.py` and a small end-to-end test in `test_small_simulation.py`.
- All new features and bugfixes are validated using these tests.

## Recent Improvements

- Switched to direct dataclass serialization with a custom encoder for robust JSON output.
- Redteamed all serialization and agent assumptions for future extensibility.
- Modularized persona system for easy strategy experimentation.

---

For more details, see the code in `simulation_runner.py`, `personas/`, and the test scripts. 