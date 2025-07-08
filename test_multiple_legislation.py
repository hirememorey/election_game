#!/usr/bin/env python3
"""
Test script to verify that multiple pieces of legislation can be sponsored.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionSponsorLegislation

def test_multiple_legislation():
    """Test that multiple pieces of legislation can be sponsored."""
    
    # Load game data and create engine
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Start a new game
    state = engine.start_new_game(["Alice", "Bob"])
    
    # Give players enough PC and action points
    for player in state.players:
        player.pc = 50
        state.action_points[player.id] = 10  # Give plenty of action points
    
    print("=== Testing Multiple Legislation Sponsorship ===")
    print(f"Initial phase: {state.current_phase}")
    print(f"Round: {state.round_marker}")
    
    # Alice sponsors first legislation
    print("\n--- Alice sponsors Infrastructure Bill ---")
    action1 = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, action1)
    print(f"Alice PC after sponsoring: {state.players[0].pc}")
    print(f"Pending legislation: {state.pending_legislation is not None}")
    if state.pending_legislation:
        print(f"  - Legislation ID: {state.pending_legislation.legislation_id}")
        print(f"  - Sponsor ID: {state.pending_legislation.sponsor_id}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    
    # Alice sponsors second legislation (this should now work!)
    print("\n--- Alice sponsors Healthcare Bill ---")
    action2 = ActionSponsorLegislation(player_id=0, legislation_id="HEALTHCARE")
    state = engine.process_action(state, action2)
    print(f"Alice PC after sponsoring second bill: {state.players[0].pc}")
    print(f"Pending legislation: {state.pending_legislation is not None}")
    if state.pending_legislation:
        print(f"  - Legislation ID: {state.pending_legislation.legislation_id}")
        print(f"  - Sponsor ID: {state.pending_legislation.sponsor_id}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    
    # Check term legislation
    if state.term_legislation:
        print("\nTerm legislation:")
        for i, leg in enumerate(state.term_legislation):
            print(f"  {i+1}. {leg.legislation_id} (sponsored by player {leg.sponsor_id})")
    
    # Bob sponsors third legislation
    print("\n--- Bob sponsors Military Funding ---")
    action3 = ActionSponsorLegislation(player_id=1, legislation_id="MILITARY")
    state = engine.process_action(state, action3)
    print(f"Bob PC after sponsoring: {state.players[1].pc}")
    print(f"Pending legislation: {state.pending_legislation is not None}")
    if state.pending_legislation:
        print(f"  - Legislation ID: {state.pending_legislation.legislation_id}")
        print(f"  - Sponsor ID: {state.pending_legislation.sponsor_id}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    
    # Check final term legislation
    if state.term_legislation:
        print("\nFinal term legislation:")
        for i, leg in enumerate(state.term_legislation):
            print(f"  {i+1}. {leg.legislation_id} (sponsored by player {leg.sponsor_id})")
    
    print("\n✅ Multiple legislation sponsorship test completed!")
    print("=" * 60)
    
    return state

if __name__ == "__main__":
    test_multiple_legislation() 