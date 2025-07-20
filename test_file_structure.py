#!/usr/bin/env python3
"""
Test to verify the file structure and fix analysis module.
"""

import os
import tempfile
from pathlib import Path

def test_file_structure():
    """Test the file structure that the simulation creates."""
    print("Testing File Structure")
    print("=" * 50)
    
    # Create a temporary directory structure like the simulation would
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"Created temp directory: {temp_dir}")
        
        # Create the structure that the simulation creates
        experiment_dir = Path(temp_dir) / "basic_balance"
        experiment_dir.mkdir()
        
        # Create the files that the simulation would create
        timestamp = "1234567890"
        
        # Create the detailed results file
        detailed_file = experiment_dir / f"basic_balance_detailed_results_{timestamp}.json"
        with open(detailed_file, 'w') as f:
            f.write('{"test": "data"}')
        
        # Create the CSV file
        csv_file = experiment_dir / f"basic_balance_simulation_results_{timestamp}.csv"
        with open(csv_file, 'w') as f:
            f.write("game_id,winner_id,winner_name,game_length_rounds,game_length_terms,simulation_time_seconds\n")
            f.write("0,0,Test Bot,10,2,0.1\n")
        
        print(f"Created files:")
        print(f"  - {detailed_file}")
        print(f"  - {csv_file}")
        
        # List all files in the experiment directory
        print(f"\nFiles in {experiment_dir}:")
        for file in experiment_dir.iterdir():
            print(f"  - {file.name}")
        
        # Test the analysis module
        from analysis import SimulationAnalyzer
        
        try:
            analyzer = SimulationAnalyzer(str(experiment_dir))
            analyzer.load_results()
            print(f"\n✓ Analysis module loaded results successfully")
            return True
        except Exception as e:
            print(f"\n✗ Analysis failed: {e}")
            return False

if __name__ == "__main__":
    success = test_file_structure()
    if success:
        print("\n✅ File structure test passed!")
    else:
        print("\n❌ File structure test failed!") 