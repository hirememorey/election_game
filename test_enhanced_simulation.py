#!/usr/bin/env python3
"""
Test script for the enhanced simulation framework.

This script tests the new features:
1. Analysis module
2. Multi-experiment configuration
3. Error handling and tracing
4. Enhanced persona interface
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from simulation_runner import SimulationRunner
from analysis import SimulationAnalyzer


def test_enhanced_simulation():
    """Test the enhanced simulation framework."""
    print("Testing Enhanced Simulation Framework")
    print("=" * 50)
    
    # Create a temporary directory for test results
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Using temporary directory: {temp_dir}")
        
        # Create a minimal test configuration
        test_config = {
            'global': {
                'random_seed': 42,
                'max_rounds_per_game': 50,
                'parallel_workers': 0,
                'output_directory': temp_dir
            },
            'data_collection': {
                'log_level': 'silent',
                'save_game_logs': True,
                'save_final_states': True,
                'enable_tracing': True  # Enable tracing for testing
            },
            'analysis': {
                'generate_reports': True,
                'report_format': 'markdown',
                'create_visualizations': False,
                'output_directory': os.path.join(temp_dir, 'analysis')
            },
            'experiments': [
                {
                    'name': 'test_basic_balance',
                    'description': 'Test basic balance with 2 players',
                    'num_games': 10,  # Small number for testing
                    'players': [
                        {'name': 'Random Bot 1', 'persona': 'random'},
                        {'name': 'Economic Bot 1', 'persona': 'economic'}
                    ]
                },
                {
                    'name': 'test_legislative_vs_economic',
                    'description': 'Test legislative vs economic strategies',
                    'num_games': 10,
                    'players': [
                        {'name': 'Legislative Bot', 'persona': 'legislative'},
                        {'name': 'Economic Bot', 'persona': 'economic'}
                    ]
                }
            ]
        }
        
        # Write test configuration to temporary file
        config_path = os.path.join(temp_dir, 'test_config.yaml')
        import yaml
        with open(config_path, 'w') as f:
            yaml.dump(test_config, f)
        
        print(f"Created test configuration: {config_path}")
        
        # Test 1: Run simulations
        print("\n1. Testing Multi-Experiment Simulation")
        print("-" * 40)
        
        try:
            runner = SimulationRunner(config_path)
            all_results = runner.run_simulation_batch()
            
            print(f"✓ Simulations completed successfully")
            print(f"  - Experiments run: {len(all_results)}")
            for exp_name, results in all_results.items():
                print(f"  - {exp_name}: {len(results)} games")
            
        except Exception as e:
            print(f"✗ Simulation failed: {e}")
            return False
        
        # Test 2: Analysis
        print("\n2. Testing Analysis Module")
        print("-" * 40)
        
        try:
            # Find the actual results directory (it will be a subdirectory)
            results_dirs = [d for d in Path(temp_dir).iterdir() if d.is_dir()]
            if results_dirs:
                results_dir = results_dirs[0]  # Use the first experiment directory
                print(f"Found results in: {results_dir}")
                
                analyzer = SimulationAnalyzer(str(results_dir))
                
                # Test loading results
                analyzer.load_results()
                print(f"✓ Results loaded successfully")
                
                # Test metrics calculation
                metrics = analyzer.calculate_metrics()
                print(f"✓ Metrics calculated successfully")
                print(f"  - Total games: {metrics.total_games}")
                print(f"  - Win rates: {len(metrics.win_rates)} personas")
                
                # Test report generation
                report = analyzer.generate_report()
                print(f"✓ Report generated successfully")
                print(f"  - Report length: {len(report)} characters")
                
                # Test summary printing
                analyzer.print_summary()
                print(f"✓ Summary printed successfully")
            else:
                print("⚠ No results directories found")
                return False
            
        except Exception as e:
            print(f"✗ Analysis failed: {e}")
            return False
        
        # Test 3: Error Handling
        print("\n3. Testing Error Handling")
        print("-" * 40)
        
        try:
            # Test with invalid configuration
            invalid_config = {
                'global': {'random_seed': 42},
                'experiments': []  # No experiments
            }
            
            invalid_config_path = os.path.join(temp_dir, 'invalid_config.yaml')
            with open(invalid_config_path, 'w') as f:
                yaml.dump(invalid_config, f)
            
            runner = SimulationRunner(invalid_config_path)
            results = runner.run_simulation_batch()
            
            if not results:
                print("✓ Error handling works correctly (no experiments = empty results)")
            else:
                print("✗ Error handling failed (should have empty results)")
                return False
                
        except Exception as e:
            print(f"✓ Error handling works correctly: {e}")
        
        # Test 4: Tracing
        print("\n4. Testing Tracing Feature")
        print("-" * 40)
        
        try:
            # Check if trace logs were created
            trace_files = list(Path(temp_dir).glob("**/*detailed_results_*.json"))
            if trace_files:
                print(f"✓ Trace files created: {len(trace_files)}")
                
                # Check if any trace logs contain tracing information
                import json
                with open(trace_files[0], 'r') as f:
                    data = json.load(f)
                
                if data and len(data) > 0:
                    first_result = data[0]
                    if 'game_log' in first_result and first_result['game_log']:
                        print("✓ Trace logs contain detailed information")
                    else:
                        print("⚠ Trace logs may not contain expected detail")
                else:
                    print("⚠ Trace files appear empty")
            else:
                print("✗ No trace files found")
                return False
                
        except Exception as e:
            print(f"✗ Tracing test failed: {e}")
            return False
        
        print("\n" + "=" * 50)
        print("✓ All tests passed! Enhanced simulation framework is working.")
        print("=" * 50)
        
        return True


def test_analysis_standalone():
    """Test the analysis module with sample data."""
    print("\nTesting Analysis Module with Sample Data")
    print("-" * 40)
    
    # Create sample results data
    sample_results = [
        {
            'winner_id': 0,
            'winner_name': 'Economic Bot',
            'game_length_rounds': 20,
            'game_length_terms': 5,
            'final_scores': {0: 100, 1: 80},
            'game_log': ['Player 0 chose: ActionFundraise', 'Player 1 chose: ActionNetwork'],
            'simulation_time_seconds': 0.5,
            'final_state': {
                'players': [
                    {'name': 'Economic Bot', 'pc': 50, 'influence': 100},
                    {'name': 'Random Bot', 'pc': 30, 'influence': 80}
                ]
            }
        },
        {
            'winner_id': 1,
            'winner_name': 'Random Bot',
            'game_length_rounds': 18,
            'game_length_terms': 4,
            'final_scores': {0: 70, 1: 90},
            'game_log': ['Player 1 chose: ActionSponsorLegislation'],
            'simulation_time_seconds': 0.4,
            'final_state': {
                'players': [
                    {'name': 'Economic Bot', 'pc': 40, 'influence': 70},
                    {'name': 'Random Bot', 'pc': 45, 'influence': 90}
                ]
            }
        }
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write sample results
        import json
        results_path = os.path.join(temp_dir, 'detailed_results_1234567890.json')
        with open(results_path, 'w') as f:
            json.dump(sample_results, f)
        
        # Test analysis
        analyzer = SimulationAnalyzer(temp_dir)
        analyzer.load_results('1234567890')
        metrics = analyzer.calculate_metrics()
        
        print(f"✓ Sample analysis completed")
        print(f"  - Total games: {metrics.total_games}")
        print(f"  - Win rates: {metrics.win_rates}")
        print(f"  - Average rounds: {metrics.avg_game_length_rounds:.1f}")
        
        # Test report generation
        report = analyzer.generate_report()
        print(f"✓ Sample report generated ({len(report)} characters)")
        
        return True


if __name__ == "__main__":
    print("Enhanced Simulation Framework Test Suite")
    print("=" * 60)
    
    # Test 1: Full simulation framework
    success1 = test_enhanced_simulation()
    
    # Test 2: Standalone analysis
    success2 = test_analysis_standalone()
    
    if success1 and success2:
        print("\n🎉 All tests passed! The enhanced simulation framework is ready.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1) 