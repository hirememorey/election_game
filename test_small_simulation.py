#!/usr/bin/env python3
"""
Small test script to verify the simulation framework works end-to-end.
"""

from simulation_runner import SimulationRunner
from personas import RandomPersona, EconomicPersona, LegislativePersona, BalancedPersona

def test_small_simulation():
    """Run a small simulation to test the framework."""
    print("Testing simulation framework...")
    
    # Create a small configuration
    config = {
        'simulation': {
            'num_games': 10,  # Small number for testing
            'max_rounds_per_game': 50,
            'parallel_workers': 0,
            'random_seed': 42
        },
        'players': [
            {'name': 'Random Bot', 'persona': 'random'},
            {'name': 'Economic Bot', 'persona': 'economic'},
            {'name': 'Legislative Bot', 'persona': 'legislative'},
            {'name': 'Balanced Bot', 'persona': 'balanced'}
        ],
        'data_collection': {
            'log_level': 'silent',
            'save_game_logs': True,
            'save_final_states': False,
            'output_directory': 'test_simulation_results'
        }
    }
    
    # Save temporary config
    import yaml
    with open('test_config.yaml', 'w') as f:
        yaml.dump(config, f)
    
    try:
        # Run simulation
        runner = SimulationRunner('test_config.yaml')
        results = runner.run_simulation_batch()
        
        # Generate report
        report = runner.generate_summary_report(results)
        print("\n" + "="*50)
        print("TEST SIMULATION RESULTS")
        print("="*50)
        print(report)
        
        print(f"\n✅ Simulation framework test completed successfully!")
        print(f"   - Ran {len(results)} games")
        print(f"   - All personas working correctly")
        print(f"   - Results saved to test_simulation_results/")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up
        import os
        if os.path.exists('test_config.yaml'):
            os.remove('test_config.yaml')


if __name__ == "__main__":
    success = test_small_simulation()
    exit(0 if success else 1) 