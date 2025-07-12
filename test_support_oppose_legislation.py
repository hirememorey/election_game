#!/usr/bin/env python3
"""
Test script to verify that support and oppose legislation works correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionSponsorLegislation, ActionSupportLegislation, ActionOpposeLegislation

def test_support_oppose_legislation():
    """Test that support and oppose legislation works correctly."""
    
    # Load game data and create engine
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Start a new game
    state = engine.start_new_game(["Alice", "Bob"])
    
    # Give players enough PC and action points
    for player in state.players:
        player.pc = 50
        state.action_points[player.id] = 10  # Give plenty of action points
    
    print("=== Testing Support/Oppose Legislation ===")
    print(f"Initial phase: {state.current_phase}")
    print(f"Round: {state.round_marker}")
    
    # Alice sponsors legislation
    print("\n--- Alice sponsors Infrastructure Bill ---")
    action1 = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, action1)
    print(f"Alice PC after sponsoring: {state.players[0].pc}")
    print(f"Pending legislation: {state.pending_legislation is not None}")
    if state.pending_legislation:
        print(f"  - Legislation ID: {state.pending_legislation.legislation_id}")
        print(f"  - Sponsor ID: {state.pending_legislation.sponsor_id}")
    
    # Simulate end of round (upkeep) - this moves legislation to term_legislation
    print("\n--- Simulating end of round (upkeep) ---")
    from engine.resolvers import resolve_upkeep
    state = resolve_upkeep(state)
    print(f"Pending legislation after upkeep: {state.pending_legislation is not None}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    if state.term_legislation:
        for i, leg in enumerate(state.term_legislation):
            print(f"  {i+1}. {leg.legislation_id} (sponsored by player {leg.sponsor_id})")
    
    # Set current player to Bob for the test
    state.current_player_index = 1
    
    # Bob tries to oppose the legislation (should work now)
    print("\n--- Bob opposes the Infrastructure Bill ---")
    action2 = ActionOpposeLegislation(player_id=1, legislation_id="INFRASTRUCTURE", oppose_amount=5)
    state = engine.process_action(state, action2)
    print(f"Bob PC after opposing: {state.players[1].pc}")
    
    # Check if the opposition was recorded
    if state.term_legislation:
        for leg in state.term_legislation:
            if leg.legislation_id == "INFRASTRUCTURE":
                print(f"Opposition players: {leg.oppose_players}")
                print(f"Support players: {leg.support_players}")
    
    # Set current player back to Alice for the test
    state.current_player_index = 0
    
    # Alice tries to support her own legislation (should fail)
    print("\n--- Alice tries to support her own legislation ---")
    action3 = ActionSupportLegislation(player_id=0, legislation_id="INFRASTRUCTURE", support_amount=3)
    state = engine.process_action(state, action3)
    print(f"Alice PC after trying to support: {state.players[0].pc}")
    
    print("\n✅ Support/Oppose legislation test completed!")
    print("=" * 60)
    
    return state

if __name__ == "__main__":
    test_support_oppose_legislation() 