#!/usr/bin/env python3
"""
Debug script to trace exactly when legislation is being resolved.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionSponsorLegislation, ActionFundraise

def debug_legislation_resolution():
    """Debug exactly when legislation is being resolved."""
    
    # Load game data and create engine
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Start a new game
    state = engine.start_new_game(["Tara", "Harris"])
    
    print("=== Starting Legislation Debug ===")
    print(f"Initial phase: {state.current_phase}")
    print(f"Round: {state.round_marker}")
    
    # Round 1: Tara sponsors legislation
    print("\n--- ROUND 1 ---")
    print("Tara sponsors Infrastructure Bill")
    action = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, action)
    print(f"Phase: {state.current_phase}, Round: {state.round_marker}")
    print(f"Pending legislation: {state.pending_legislation is not None}")
    if state.pending_legislation:
        print(f"  - Legislation ID: {state.pending_legislation.legislation_id}")
        print(f"  - Resolved: {state.pending_legislation.resolved}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    
    # Harris fundraises
    print("Harris fundraises")
    action = ActionFundraise(player_id=1)
    state = engine.process_action(state, action)
    print(f"Phase: {state.current_phase}, Round: {state.round_marker}")
    print(f"Pending legislation: {state.pending_legislation is not None}")
    if state.pending_legislation:
        print(f"  - Legislation ID: {state.pending_legislation.legislation_id}")
        print(f"  - Resolved: {state.pending_legislation.resolved}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    for i, leg in enumerate(state.term_legislation):
        print(f"  Term legislation {i}: {leg.legislation_id}, resolved: {leg.resolved}")
    
    print("\n=== Game Log ===")
    for log_entry in state.turn_log:
        print(log_entry)
    
    return state

if __name__ == "__main__":
    debug_legislation_resolution() 