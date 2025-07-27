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
from engine.ui_actions import UISupportLegislation, UIOpposeLegislation

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
    
    # Check that support/oppose actions are now available
    valid_actions = engine.get_valid_actions(state, state.get_current_player().id)
    action_types = [type(a) for a in valid_actions]
    assert UISupportLegislation in action_types
    assert UIOpposeLegislation in action_types

    # Bob supports the legislation
    print("\n--- Bob supports the bill ---")
    
    # Set the current player to Bob
    state.current_player_index = 1
    
    # In the new flow, this would be a two-step process.
    # Here, we'll construct the action directly to test the engine.
    action2 = ActionSupportLegislation(
        player_id=1,
        legislation_id="INFRASTRUCTURE",
        support_amount=10
    )
    state = engine.process_action(state, action2)
    print(f"Bob PC after supporting: {state.players[1].pc}")
    assert state.players[1].pc == 40, "Bob's PC should be deducted by 10"

    # Check the internal state of the term legislation
    active_bill = None
    for leg in state.term_legislation:
        if leg.legislation_id == "INFRASTRUCTURE":
            active_bill = leg
            break
    assert active_bill is not None
    assert active_bill.support_players[1] == 10, "Bob's support should be recorded"

    
    # Alice opposes the legislation
    print("\n--- Alice opposes the bill ---")
    
    # Set the current player to Alice
    state.current_player_index = 0
    
    action3 = ActionOpposeLegislation(
        player_id=0,
        legislation_id="INFRASTRUCTURE",
        oppose_amount=5
    )
    state = engine.process_action(state, action3)
    print(f"Alice PC after opposing: {state.players[0].pc}")
    assert state.players[0].pc == 40, "Alice's PC should be deducted by 5"
    assert active_bill.oppose_players[0] == 5, "Alice's opposition should be recorded"

    print("\n✅ Support/Oppose Legislation test passed!")
    print("=" * 60)
    
    return state

if __name__ == "__main__":
    test_support_oppose_legislation() 