#!/usr/bin/env python3
"""
Rapid Iteration Tool for Election Game

This tool allows quick testing of different game configurations and parameters
for rapid gameplay iteration and balance testing.
"""

import sys
import time
import subprocess
from typing import Dict, Any, List, Optional
from config_loader import get_config, update_config, save_config, validate_config


class RapidIterationTool:
    """
    Tool for rapid iteration on game parameters and configurations.
    """
    
    def __init__(self):
        self.config = get_config()
        self.test_results = []
    
    def run_quick_test(self, config_changes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run a quick test with optional configuration changes.
        
        Args:
            config_changes: Dictionary of config changes to apply
            
        Returns:
            Test results dictionary
        """
        # Apply configuration changes
        if config_changes:
            for key_path, value in config_changes.items():
                update_config(key_path, value)
        
        # Validate configuration
        if not validate_config():
            print("❌ Configuration validation failed!")
            return {"success": False, "error": "Invalid configuration"}
        
        # Run a quick simulation
        try:
            print("🔄 Running quick test...")
            start_time = time.time()
            
            # Run simulation with current config
            result = self._run_simulation_test()
            
            end_time = time.time()
            duration = end_time - start_time
            
            result["duration"] = duration
            result["config_changes"] = config_changes or {}
            
            self.test_results.append(result)
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _run_simulation_test(self) -> Dict[str, Any]:
        """
        Run a simulation test with current configuration.
        
        Returns:
            Test results
        """
        # This would integrate with the simulation framework
        # For now, we'll simulate basic metrics
        
        # Simulate win rates based on current AI weights
        ai_config = self.config.get_ai_config()
        fundraise_weight = ai_config.get('fundraise_weight', 1.0)
        network_weight = ai_config.get('network_weight', 1.0)
        
        # Simple simulation of win rates
        base_win_rate = 0.46  # Current heuristic win rate
        win_rate_modifier = (fundraise_weight + network_weight) / 2.0
        simulated_win_rate = min(0.8, max(0.1, base_win_rate * win_rate_modifier))
        
        return {
            "success": True,
            "simulated_win_rate": simulated_win_rate,
            "ai_weights": {
                "fundraise": fundraise_weight,
                "network": network_weight
            },
            "game_balance_score": self._calculate_balance_score()
        }
    
    def _calculate_balance_score(self) -> float:
        """Calculate a simple balance score based on current configuration."""
        score = 0.0
        
        # Check action point balance
        ap_config = self.config.get_action_points_config()
        base_ap = ap_config.get('base_ap_per_turn', 2)
        if 1 <= base_ap <= 3:
            score += 2.0
        elif base_ap == 2:
            score += 3.0  # Optimal value
        
        # Check PC economy balance
        pc_config = self.config.get_political_capital_config()
        fundraise_pc = pc_config.get('base_fundraise_pc', 5)
        network_pc = pc_config.get('base_network_pc', 2)
        
        if fundraise_pc > network_pc:
            score += 1.0  # Fundraising should be more rewarding
        
        if 3 <= fundraise_pc <= 7:
            score += 1.0
        
        if 1 <= network_pc <= 4:
            score += 1.0
        
        # Check legislation balance
        leg_config = self.config.get_legislation_config()
        success_target = leg_config.get('base_success_target', 15)
        if 10 <= success_target <= 20:
            score += 1.0
        
        return min(10.0, score)
    
    def compare_configurations(self, config_sets: List[Dict[str, Any]]) -> None:
        """
        Compare multiple configurations and their results.
        
        Args:
            config_sets: List of configuration dictionaries to test
        """
        print("🔬 Comparing configurations...")
        print("="*60)
        
        results = []
        for i, config_set in enumerate(config_sets):
            print(f"\n📊 Testing Configuration {i+1}:")
            for key, value in config_set.items():
                print(f"  {key}: {value}")
            
            result = self.run_quick_test(config_set)
            results.append(result)
            
            if result["success"]:
                print(f"  ✅ Win Rate: {result['simulated_win_rate']:.2%}")
                print(f"  📈 Balance Score: {result['game_balance_score']:.1f}/10")
            else:
                print(f"  ❌ Error: {result.get('error', 'Unknown error')}")
        
        # Find best configuration
        valid_results = [r for r in results if r["success"]]
        if valid_results:
            best_result = max(valid_results, key=lambda x: x["game_balance_score"])
            print(f"\n🏆 Best Configuration:")
            print(f"  Balance Score: {best_result['game_balance_score']:.1f}/10")
            print(f"  Win Rate: {best_result['simulated_win_rate']:.2%}")
    
    def interactive_tuning(self) -> None:
        """Interactive configuration tuning mode."""
        print("🎛️  Interactive Configuration Tuning")
        print("="*40)
        
        while True:
            print("\nCurrent Configuration:")
            self.config.print_config_summary()
            
            print("\nOptions:")
            print("1. Modify Action Points")
            print("2. Modify Political Capital")
            print("3. Modify AI Behavior")
            print("4. Modify Legislation")
            print("5. Run Quick Test")
            print("6. Save Configuration")
            print("7. Exit")
            
            choice = input("\nEnter choice (1-7): ").strip()
            
            if choice == "1":
                self._tune_action_points()
            elif choice == "2":
                self._tune_political_capital()
            elif choice == "3":
                self._tune_ai_behavior()
            elif choice == "4":
                self._tune_legislation()
            elif choice == "5":
                result = self.run_quick_test()
                if result["success"]:
                    print(f"✅ Test completed in {result['duration']:.2f}s")
                    print(f"📈 Balance Score: {result['game_balance_score']:.1f}/10")
                else:
                    print(f"❌ Test failed: {result.get('error', 'Unknown error')}")
            elif choice == "6":
                save_config()
                print("💾 Configuration saved!")
            elif choice == "7":
                break
            else:
                print("❌ Invalid choice. Please enter 1-7.")
    
    def _tune_action_points(self) -> None:
        """Interactive tuning for action points."""
        print("\n🎯 Action Points Tuning")
        print("-" * 20)
        
        current_ap = self.config.get_int('action_points.base_ap_per_turn', 2)
        print(f"Current base AP per turn: {current_ap}")
        
        new_ap = input("Enter new base AP per turn (1-4): ").strip()
        try:
            new_ap = int(new_ap)
            if 1 <= new_ap <= 4:
                update_config('action_points.base_ap_per_turn', new_ap)
                print(f"✅ Updated to {new_ap} AP per turn")
            else:
                print("❌ AP must be between 1 and 4")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def _tune_political_capital(self) -> None:
        """Interactive tuning for political capital."""
        print("\n💰 Political Capital Tuning")
        print("-" * 25)
        
        current_fundraise = self.config.get_int('political_capital.base_fundraise_pc', 5)
        current_network = self.config.get_int('political_capital.base_network_pc', 2)
        
        print(f"Current Fundraise PC: {current_fundraise}")
        print(f"Current Network PC: {current_network}")
        
        new_fundraise = input("Enter new Fundraise PC (3-8): ").strip()
        try:
            new_fundraise = int(new_fundraise)
            if 3 <= new_fundraise <= 8:
                update_config('political_capital.base_fundraise_pc', new_fundraise)
                print(f"✅ Updated Fundraise PC to {new_fundraise}")
            else:
                print("❌ Fundraise PC must be between 3 and 8")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def _tune_ai_behavior(self) -> None:
        """Interactive tuning for AI behavior."""
        print("\n🤖 AI Behavior Tuning")
        print("-" * 18)
        
        current_fundraise_weight = self.config.get_float('ai.fundraise_weight', 1.0)
        current_network_weight = self.config.get_float('ai.network_weight', 1.0)
        
        print(f"Current Fundraise Weight: {current_fundraise_weight}")
        print(f"Current Network Weight: {current_network_weight}")
        
        new_fundraise_weight = input("Enter new Fundraise Weight (0.5-2.0): ").strip()
        try:
            new_fundraise_weight = float(new_fundraise_weight)
            if 0.5 <= new_fundraise_weight <= 2.0:
                update_config('ai.fundraise_weight', new_fundraise_weight)
                print(f"✅ Updated Fundraise Weight to {new_fundraise_weight}")
            else:
                print("❌ Weight must be between 0.5 and 2.0")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def _tune_legislation(self) -> None:
        """Interactive tuning for legislation."""
        print("\n📜 Legislation Tuning")
        print("-" * 18)
        
        current_success_target = self.config.get_int('legislation.base_success_target', 15)
        print(f"Current Success Target: {current_success_target}")
        
        new_success_target = input("Enter new Success Target (10-25): ").strip()
        try:
            new_success_target = int(new_success_target)
            if 10 <= new_success_target <= 25:
                update_config('legislation.base_success_target', new_success_target)
                print(f"✅ Updated Success Target to {new_success_target}")
            else:
                print("❌ Success Target must be between 10 and 25")
        except ValueError:
            print("❌ Please enter a valid number")
    
    def run_preset_tests(self) -> None:
        """Run a series of preset configuration tests."""
        print("🧪 Running Preset Configuration Tests")
        print("="*40)
        
        presets = [
            {
                "name": "Conservative (Low AP, High PC)",
                "changes": {
                    "action_points.base_ap_per_turn": 1,
                    "political_capital.base_fundraise_pc": 8,
                    "political_capital.base_network_pc": 3
                }
            },
            {
                "name": "Aggressive (High AP, Low PC)",
                "changes": {
                    "action_points.base_ap_per_turn": 3,
                    "political_capital.base_fundraise_pc": 3,
                    "political_capital.base_network_pc": 1
                }
            },
            {
                "name": "Balanced (Current)",
                "changes": {}
            },
            {
                "name": "Legislation Focus",
                "changes": {
                    "legislation.base_success_target": 12,
                    "legislation.success_reward_multiplier": 1.5
                }
            }
        ]
        
        for preset in presets:
            print(f"\n📊 Testing: {preset['name']}")
            result = self.run_quick_test(preset['changes'])
            
            if result["success"]:
                print(f"  ✅ Win Rate: {result['simulated_win_rate']:.2%}")
                print(f"  📈 Balance Score: {result['game_balance_score']:.1f}/10")
            else:
                print(f"  ❌ Error: {result.get('error', 'Unknown error')}")


def main():
    """Main entry point for the rapid iteration tool."""
    tool = RapidIterationTool()
    
    if len(sys.argv) < 2:
        print("🎛️  Rapid Iteration Tool for Election Game")
        print("="*40)
        print("Usage:")
        print("  python3 rapid_iteration.py interactive")
        print("  python3 rapid_iteration.py presets")
        print("  python3 rapid_iteration.py test")
        return
    
    mode = sys.argv[1].lower()
    
    if mode == "interactive":
        tool.interactive_tuning()
    elif mode == "presets":
        tool.run_preset_tests()
    elif mode == "test":
        result = tool.run_quick_test()
        if result["success"]:
            print(f"✅ Quick test completed in {result['duration']:.2f}s")
            print(f"📈 Balance Score: {result['game_balance_score']:.1f}/10")
        else:
            print(f"❌ Test failed: {result.get('error', 'Unknown error')}")
    else:
        print("❌ Invalid mode. Use 'interactive', 'presets', or 'test'")


if __name__ == "__main__":
    main() 