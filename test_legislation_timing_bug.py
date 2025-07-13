#!/usr/bin/env python3
"""
Test script to reproduce the "There's no pending legislation to oppose" bug.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionSponsorLegislation, ActionOpposeLegislation
from engine.resolvers import resolve_upkeep

def test_legislation_timing_bug():
    """Test to reproduce the legislation timing bug."""
    
    print("🧪 Testing Legislation Timing Bug")
    print("=" * 50)
    
    # Load game data and create engine
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Start a new game
    state = engine.start_new_game(["Alice", "Bob"])
    
    # Give players enough PC and action points
    for player in state.players:
        player.pc = 50
        state.action_points[player.id] = 10
    
    print(f"Initial phase: {state.current_phase}")
    print(f"Round: {state.round_marker}")
    
    # Alice sponsors legislation
    print("\n--- Alice sponsors Infrastructure Bill ---")
    action1 = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, action1)
    
    print(f"Pending legislation after sponsoring: {state.pending_legislation is not None}")
    if state.pending_legislation:
        print(f"  - Legislation ID: {state.pending_legislation.legislation_id}")
        print(f"  - Sponsor ID: {state.pending_legislation.sponsor_id}")
    
    # Simulate end of round (upkeep) - this moves legislation to term_legislation
    print("\n--- Simulating end of round (upkeep) ---")
    state = resolve_upkeep(state)
    
    print(f"Pending legislation after upkeep: {state.pending_legislation is not None}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    if state.term_legislation:
        for i, leg in enumerate(state.term_legislation):
            print(f"  {i+1}. {leg.legislation_id} (sponsored by player {leg.sponsor_id})")
    
    # Set current player to Bob for the test
    state.current_player_index = 1
    
    # Bob tries to oppose the legislation (this should work)
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
    
    # Now test the bug scenario - try to oppose with a non-existent legislation ID
    print("\n--- Testing with non-existent legislation ID ---")
    action3 = ActionOpposeLegislation(player_id=1, legislation_id="NON_EXISTENT", oppose_amount=5)
    state = engine.process_action(state, action3)
    
    print("\n✅ Legislation timing bug test completed!")
    print("=" * 50)
    
    return state

if __name__ == "__main__":
    test_legislation_timing_bug() 