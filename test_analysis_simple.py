#!/usr/bin/env python3
"""
Simple test for the analysis module.
"""

import os
import json
import tempfile
from pathlib import Path

from analysis import SimulationAnalyzer

def test_analysis_module():
    """Test the analysis module with sample data."""
    print("Testing Analysis Module")
    print("=" * 50)
    
    # Create a temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create the expected directory structure
        results_dir = Path(temp_dir) / "test_experiment"
        results_dir.mkdir()
        
        # Create sample results
        sample_results = [
            {
                "winner_name": "Economic Bot",
                "game_length_rounds": 15,
                "game_length_terms": 3,
                "final_state": {
                    "players": [
                        {"name": "Economic Bot", "pc": 10, "influence": 5},
                        {"name": "Random Bot", "pc": 5, "influence": 3}
                    ]
                }
            },
            {
                "winner_name": "Random Bot", 
                "game_length_rounds": 20,
                "game_length_terms": 4,
                "final_state": {
                    "players": [
                        {"name": "Economic Bot", "pc": 8, "influence": 4},
                        {"name": "Random Bot", "pc": 12, "influence": 6}
                    ]
                }
            }
        ]
        
        # Save the results
        results_file = results_dir / "detailed_results_1234567890.json"
        with open(results_file, 'w') as f:
            json.dump(sample_results, f, indent=2)
        
        print(f"Created test results in: {results_file}")
        
        # Test the analyzer
        try:
            analyzer = SimulationAnalyzer(temp_dir)
            analyzer.load_results()
            
            print("✓ Results loaded successfully")
            
            # Calculate metrics
            metrics = analyzer.calculate_metrics()
            print(f"✓ Metrics calculated successfully")
            print(f"  - Total games: {metrics.total_games}")
            print(f"  - Win rates: {metrics.win_rates}")
            print(f"  - Average rounds: {metrics.avg_game_length_rounds:.1f}")
            
            # Generate report
            report = analyzer.generate_report()
            print(f"✓ Report generated successfully")
            print(f"  - Report length: {len(report)} characters")
            
            # Print summary
            analyzer.print_summary()
            print("✓ Summary printed successfully")
            
            return True
            
        except Exception as e:
            print(f"✗ Analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_analysis_module()
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed!") 