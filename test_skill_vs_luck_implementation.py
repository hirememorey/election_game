#!/usr/bin/env python3
"""
Test script for the Skill vs Luck implementation.

This script tests:
1. HeuristicPersona creation and basic functionality
2. Dice roll disable functionality in elections
3. Basic simulation with the new components
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from personas import HeuristicPersona, RandomPersona
from simulation_harness import SimulationHarness, SilentLogger
from models.game_state import GameState
from engine.actions import ActionFundraise, ActionPassTurn
import random

def test_heuristic_persona():
    """Test that HeuristicPersona works correctly."""
    print("Testing HeuristicPersona...")
    
    # Create a heuristic persona
    persona = HeuristicPersona("Test Heuristic", random_seed=42)
    
    # Test basic functionality
    assert persona.name == "Test Heuristic"
    assert persona.random is not None
    
    # Test action priority
    fundraise_action = ActionFundraise(player_id=0)
    pass_action = ActionPassTurn(player_id=0)
    
    fundraise_priority = persona.get_action_priority(fundraise_action)
    pass_priority = persona.get_action_priority(pass_action)
    
    # Fundraise should have higher priority than pass
    assert fundraise_priority > pass_priority
    
    print("✅ HeuristicPersona basic functionality works")

def test_dice_roll_disable():
    """Test that dice roll disable functionality works."""
    print("Testing dice roll disable functionality...")
    
    # Create two harnesses - one with dice, one without
    harness_with_dice = SimulationHarness(disable_dice_roll=False)
    harness_without_dice = SimulationHarness(disable_dice_roll=True)
    
    # Verify the configuration is set correctly
    assert harness_with_dice.disable_dice_roll == False
    assert harness_without_dice.disable_dice_roll == True
    
    print("✅ Dice roll disable configuration works")

def test_basic_simulation():
    """Test a basic simulation with the new components."""
    print("Testing basic simulation with HeuristicPersona...")
    
    # Create agents: 1 Heuristic vs 3 Random
    agents = [
        HeuristicPersona("Heuristic Bot", random_seed=42),
        RandomPersona("Random Bot 1", random_seed=43),
        RandomPersona("Random Bot 2", random_seed=44),
        RandomPersona("Random Bot 3", random_seed=45)
    ]
    
    player_names = ["Heuristic Bot", "Random Bot 1", "Random Bot 2", "Random Bot 3"]
    
    # Run a quick simulation
    harness = SimulationHarness()
    result = harness.run_simulation(
        agents, player_names, max_rounds=50, logger=SilentLogger()
    )
    
    # Verify we got a result
    assert result is not None
    assert result.winner_name is not None
    assert result.game_length_rounds > 0
    
    print(f"✅ Basic simulation completed successfully")
    print(f"   Winner: {result.winner_name}")
    print(f"   Game length: {result.game_length_rounds} rounds, {result.game_length_terms} terms")

def test_skill_delta_experiment():
    """Test the skill delta experiment (1 Heuristic vs 3 Random)."""
    print("Testing skill delta experiment...")
    
    # Create agents: 1 Heuristic vs 3 Random
    agents = [
        HeuristicPersona("Heuristic Bot", random_seed=42),
        RandomPersona("Random Bot 1", random_seed=43),
        RandomPersona("Random Bot 2", random_seed=44),
        RandomPersona("Random Bot 3", random_seed=45)
    ]
    
    player_names = ["Heuristic Bot", "Random Bot 1", "Random Bot 2", "Random Bot 3"]
    
    # Run multiple games to get statistics
    num_games = 50
    heuristic_wins = 0
    
    harness = SimulationHarness()
    
    for i in range(num_games):
        result = harness.run_simulation(
            agents, player_names, max_rounds=50, logger=SilentLogger()
        )
        
        if result.winner_name == "Heuristic Bot":
            heuristic_wins += 1
    
    win_rate = (heuristic_wins / num_games) * 100
    print(f"✅ Skill delta experiment completed")
    print(f"   Heuristic Bot wins: {heuristic_wins}/{num_games} ({win_rate:.1f}%)")
    
    # In a 4-player game, random chance would be 25%
    # We expect the heuristic player to do better than 25%
    if win_rate > 25:
        print(f"   ✅ Heuristic player shows skill advantage ({win_rate:.1f}% > 25%)")
    else:
        print(f"   ⚠️  Heuristic player win rate ({win_rate:.1f}%) is close to random chance (25%)")

def test_dice_roll_comparison():
    """Test the impact of dice rolls by comparing with and without dice."""
    print("Testing dice roll impact...")
    
    # Create agents
    agents = [
        HeuristicPersona("Heuristic Bot", random_seed=42),
        RandomPersona("Random Bot 1", random_seed=43),
        RandomPersona("Random Bot 2", random_seed=44),
        RandomPersona("Random Bot 3", random_seed=45)
    ]
    
    player_names = ["Heuristic Bot", "Random Bot 1", "Random Bot 2", "Random Bot 3"]
    
    # Test with dice rolls
    harness_with_dice = SimulationHarness(disable_dice_roll=False)
    heuristic_wins_with_dice = 0
    
    # Test without dice rolls
    harness_without_dice = SimulationHarness(disable_dice_roll=True)
    heuristic_wins_without_dice = 0
    
    num_games = 30  # Smaller sample for faster testing
    
    for i in range(num_games):
        # Game with dice
        result_with_dice = harness_with_dice.run_simulation(
            agents, player_names, max_rounds=50, logger=SilentLogger()
        )
        if result_with_dice.winner_name == "Heuristic Bot":
            heuristic_wins_with_dice += 1
        
        # Game without dice
        result_without_dice = harness_without_dice.run_simulation(
            agents, player_names, max_rounds=50, logger=SilentLogger()
        )
        if result_without_dice.winner_name == "Heuristic Bot":
            heuristic_wins_without_dice += 1
    
    win_rate_with_dice = (heuristic_wins_with_dice / num_games) * 100
    win_rate_without_dice = (heuristic_wins_without_dice / num_games) * 100
    
    print(f"✅ Dice roll comparison completed")
    print(f"   With dice rolls: {heuristic_wins_with_dice}/{num_games} ({win_rate_with_dice:.1f}%)")
    print(f"   Without dice rolls: {heuristic_wins_without_dice}/{num_games} ({win_rate_without_dice:.1f}%)")
    
    # Calculate the impact of dice rolls
    dice_impact = win_rate_without_dice - win_rate_with_dice
    print(f"   Dice roll impact: {dice_impact:+.1f} percentage points")
    
    if abs(dice_impact) > 5:
        print(f"   ✅ Dice rolls have significant impact ({dice_impact:+.1f} points)")
    else:
        print(f"   ⚠️  Dice rolls have minimal impact ({dice_impact:+.1f} points)")

def main():
    """Run all tests."""
    print("🧪 Testing Skill vs Luck Implementation")
    print("=" * 50)
    
    try:
        test_heuristic_persona()
        test_dice_roll_disable()
        test_basic_simulation()
        test_skill_delta_experiment()
        test_dice_roll_comparison()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! Implementation is working correctly.")
        print("\nNext steps:")
        print("1. Run the full simulation with: python simulation_runner.py")
        print("2. Analyze results to understand skill vs luck balance")
        print("3. Adjust game mechanics based on findings")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 