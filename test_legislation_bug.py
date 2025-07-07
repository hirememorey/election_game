#!/usr/bin/env python3
"""
Test script to reproduce the legislation resolution bug after round 2.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionSponsorLegislation, ActionFundraise

def test_legislation_after_round_2():
    """Test to reproduce the bug where legislation is resolved after round 2."""
    
    # Load game data and create engine
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Start a new game
    state = engine.start_new_game(["Tara", "Harris"])
    
    print("=== Starting Legislation Bug Test ===")
    print(f"Initial phase: {state.current_phase}")
    print(f"Round: {state.round_marker}")
    
    # Round 1: Tara sponsors legislation
    print("\n--- ROUND 1 ---")
    print("Tara sponsors Infrastructure Bill")
    action = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, action)
    print(f"Phase: {state.current_phase}, Round: {state.round_marker}")
    print(f"Pending legislation: {state.pending_legislation is not None}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    
    # Harris fundraises
    print("Harris fundraises")
    action = ActionFundraise(player_id=1)
    state = engine.process_action(state, action)
    print(f"Phase: {state.current_phase}, Round: {state.round_marker}")
    print(f"Pending legislation: {state.pending_legislation is not None}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    
    # Round 2: Tara fundraises
    print("\n--- ROUND 2 ---")
    print("Tara fundraises")
    action = ActionFundraise(player_id=0)
    state = engine.process_action(state, action)
    print(f"Phase: {state.current_phase}, Round: {state.round_marker}")
    print(f"Pending legislation: {state.pending_legislation is not None}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    
    # Harris fundraises
    print("Harris fundraises")
    action = ActionFundraise(player_id=1)
    state = engine.process_action(state, action)
    print(f"Phase: {state.current_phase}, Round: {state.round_marker}")
    print(f"Pending legislation: {state.pending_legislation is not None}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    
    print("\n=== Final State ===")
    print(f"Current phase: {state.current_phase}")
    print(f"Round: {state.round_marker}")
    print(f"Pending legislation: {state.pending_legislation is not None}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    print(f"Legislation session active: {state.legislation_session_active}")
    
    print("\n=== Game Log ===")
    for log_entry in state.turn_log:
        print(log_entry)
    
    return state

if __name__ == "__main__":
    test_legislation_after_round_2() 