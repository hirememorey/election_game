#!/usr/bin/env python3
"""
Analyze the skill vs luck simulation results.
"""

import csv
import os
from collections import Counter

def analyze_results(csv_file):
    """Analyze the results from a CSV file."""
    if not os.path.exists(csv_file):
        print(f"File not found: {csv_file}")
        return None
    
    winners = []
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            winners.append(row['winner_name'])
    
    total_games = len(winners)
    winner_counts = Counter(winners)
    
    print(f"\nResults from {os.path.basename(csv_file)}:")
    print(f"Total games: {total_games}")
    
    for winner, count in winner_counts.most_common():
        percentage = (count / total_games) * 100
        print(f"  {winner}: {count} wins ({percentage:.1f}%)")
    
    return winner_counts

def main():
    """Analyze both skill delta experiments."""
    print("🧪 Skill vs Luck Analysis")
    print("=" * 50)
    
    # Analyze with dice rolls
    with_dice_file = "simulation_results/skill_delta_test/skill_delta_test_simulation_results_*.csv"
    with_dice_files = [f for f in os.listdir("simulation_results/skill_delta_test") if f.endswith('.csv')]
    if with_dice_files:
        with_dice_file = f"simulation_results/skill_delta_test/{with_dice_files[0]}"
        with_dice_results = analyze_results(with_dice_file)
    
    # Analyze without dice rolls
    no_dice_file = "simulation_results/skill_delta_test_no_dice/skill_delta_test_no_dice_simulation_results_*.csv"
    no_dice_files = [f for f in os.listdir("simulation_results/skill_delta_test_no_dice") if f.endswith('.csv')]
    if no_dice_files:
        no_dice_file = f"simulation_results/skill_delta_test_no_dice/{no_dice_files[0]}"
        no_dice_results = analyze_results(no_dice_file)
    
    # Compare results
    if with_dice_results and no_dice_results:
        print("\n" + "=" * 50)
        print("COMPARISON")
        print("=" * 50)
        
        heuristic_with_dice = with_dice_results.get("Heuristic Bot", 0)
        heuristic_without_dice = no_dice_results.get("Heuristic Bot", 0)
        
        total_with_dice = sum(with_dice_results.values())
        total_without_dice = sum(no_dice_results.values())
        
        win_rate_with_dice = (heuristic_with_dice / total_with_dice) * 100
        win_rate_without_dice = (heuristic_without_dice / total_without_dice) * 100
        
        print(f"Heuristic Bot win rate with dice: {win_rate_with_dice:.1f}%")
        print(f"Heuristic Bot win rate without dice: {win_rate_without_dice:.1f}%")
        
        dice_impact = win_rate_without_dice - win_rate_with_dice
        print(f"Dice roll impact: {dice_impact:+.1f} percentage points")
        
        # Expected random chance in 4-player game
        expected_random = 25.0
        print(f"Expected random chance: {expected_random:.1f}%")
        
        print(f"\nSkill advantage with dice: {win_rate_with_dice - expected_random:+.1f} points")
        print(f"Skill advantage without dice: {win_rate_without_dice - expected_random:+.1f} points")
        
        if win_rate_with_dice > expected_random:
            print("✅ Heuristic player shows skill advantage with dice")
        else:
            print("⚠️  Heuristic player win rate close to random with dice")
            
        if win_rate_without_dice > expected_random:
            print("✅ Heuristic player shows skill advantage without dice")
        else:
            print("⚠️  Heuristic player win rate close to random without dice")

if __name__ == "__main__":
    main() 