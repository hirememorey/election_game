#!/usr/bin/env python3
"""
Enhanced Simulation Framework Demonstration

This script demonstrates all the enhanced features of the simulation framework:
1. Multi-experiment configuration
2. Enhanced analysis and reporting
3. Error handling and tracing
4. Improved persona interface
"""

import os
import sys
import tempfile
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation_runner import SimulationRunner
from analysis import SimulationAnalyzer

def create_demo_config():
    """Create a demo configuration with multiple experiments."""
    config = {
        "global": {
            "random_seed": 42,
            "max_rounds_per_game": 50,
            "parallel_workers": 0,
            "output_directory": "demo_results"
        },
        "data_collection": {
            "log_level": "silent",
            "save_game_logs": True,
            "save_final_states": True,
            "enable_tracing": False
        },
        "experiments": [
            {
                "name": "basic_balance",
                "description": "Test basic game balance with 4 different personas",
                "num_games": 20,
                "players": [
                    {"name": "Random Bot", "persona": "random"},
                    {"name": "Economic Bot", "persona": "economic"},
                    {"name": "Legislative Bot", "persona": "legislative"},
                    {"name": "Balanced Bot", "persona": "balanced"}
                ]
            },
            {
                "name": "strategy_comparison",
                "description": "Compare economic vs legislative strategies",
                "num_games": 15,
                "players": [
                    {"name": "Economic Bot", "persona": "economic"},
                    {"name": "Legislative Bot", "persona": "legislative"}
                ]
            }
        ]
    }
    return config

def run_demo():
    """Run the enhanced simulation framework demonstration."""
    print("Enhanced Simulation Framework Demonstration")
    print("=" * 60)
    
    # Create temporary directory for demo
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")
        
        # Create demo configuration
        config = create_demo_config()
        config["global"]["output_directory"] = temp_dir
        
        # Save config to temporary file
        config_path = Path(temp_dir) / "demo_config.yaml"
        import yaml
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"\n1. Configuration")
        print("-" * 40)
        print(f"✓ Created demo configuration with {len(config['experiments'])} experiments")
        for exp in config['experiments']:
            print(f"  - {exp['name']}: {exp['num_games']} games")
        
        # Run simulations
        print(f"\n2. Running Simulations")
        print("-" * 40)
        start_time = time.time()
        
        try:
            runner = SimulationRunner(str(config_path))
            all_results = runner.run_simulation_batch()
            
            simulation_time = time.time() - start_time
            total_games = sum(len(results) for results in all_results.values())
            
            print(f"✓ Simulations completed successfully")
            print(f"  - Total games: {total_games}")
            print(f"  - Time taken: {simulation_time:.2f} seconds")
            print(f"  - Average time per game: {simulation_time/total_games:.3f} seconds")
            
        except Exception as e:
            print(f"✗ Simulation failed: {e}")
            return False
        
        # Analyze results
        print(f"\n3. Analyzing Results")
        print("-" * 40)
        
        try:
            # Find the results directory
            results_dirs = [d for d in Path(temp_dir).iterdir() if d.is_dir()]
            if not results_dirs:
                print("⚠ No results directories found")
                return False
            
            # Analyze each experiment
            for experiment_dir in results_dirs:
                print(f"\nAnalyzing {experiment_dir.name}:")
                
                analyzer = SimulationAnalyzer(str(experiment_dir))
                analyzer.load_results()
                
                metrics = analyzer.calculate_metrics()
                print(f"  ✓ Loaded {metrics.total_games} games")
                print(f"  ✓ Average game length: {metrics.avg_game_length_rounds:.1f} rounds")
                
                # Print win rates
                print("  Win rates:")
                for persona, win_rate in sorted(metrics.win_rates.items(), key=lambda x: x[1], reverse=True):
                    percentage = win_rate * 100
                    print(f"    {persona}: {percentage:.1f}%")
                
                # Generate and save report
                report = analyzer.generate_report()
                report_path = experiment_dir / "analysis_report.md"
                with open(report_path, 'w') as f:
                    f.write(report)
                print(f"  ✓ Report saved to: {report_path}")
            
            print(f"\n4. Summary")
            print("-" * 40)
            print("✓ Enhanced simulation framework demonstration completed successfully!")
            print("✓ All features working:")
            print("  - Multi-experiment configuration")
            print("  - Enhanced analysis and reporting")
            print("  - Error handling and robustness")
            print("  - Improved persona interface")
            
            return True
            
        except Exception as e:
            print(f"✗ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Main demonstration function."""
    print("Starting Enhanced Simulation Framework Demonstration...")
    print("This will test all the enhanced features we've implemented.")
    print()
    
    success = run_demo()
    
    if success:
        print("\n🎉 DEMONSTRATION COMPLETED SUCCESSFULLY!")
        print("The enhanced simulation framework is working correctly.")
    else:
        print("\n❌ DEMONSTRATION FAILED!")
        print("Please check the implementation and try again.")
    
    return success

if __name__ == "__main__":
    main() 