#!/usr/bin/env python3
"""
Test the Secret Commitment System implementation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from engine.actions import ActionSponsorLegislation, ActionSupportLegislation, ActionOpposeLegislation
from models.game_state import GameState
import game_data
from engine.ui_actions import UISupportLegislation, UIOpposeLegislation

def test_secret_commitment_system():
    """Test the Secret Commitment System implementation."""
    print("🧪 Testing Secret Commitment System")
    print("=" * 50)
    
    # Initialize game
    game_data_dict = game_data.load_game_data()
    engine = GameEngine(game_data_dict)
    
    # Create a new game with 3 players
    state = engine.start_new_game(["Alice", "Bob", "Charlie"])
    
    # Give players some PC to work with
    for player in state.players:
        player.pc = 50
    
    print(f"Initial PC - Alice: {state.players[0].pc}, Bob: {state.players[1].pc}, Charlie: {state.players[2].pc}")
    
    # Test 1: Sponsor legislation
    print("\n📋 Test 1: Sponsoring Legislation")
    print("-" * 30)
    
    # Alice sponsors legislation
    sponsor_action = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, sponsor_action)
    
    print(f"Alice sponsored Infrastructure Bill")
    print(f"Alice's PC after sponsoring: {state.players[0].pc}")
    
    # Now that a bill is sponsored, check for support/oppose actions
    valid_actions = engine.get_valid_actions(state, state.get_current_player().id)
    action_types = [type(a) for a in valid_actions]
    
    print(f"Valid actions available: {[a.__class__.__name__ for a in valid_actions]}")
    
    assert UISupportLegislation in action_types, "Should be able to support legislation"
    assert UIOpposeLegislation in action_types, "Should be able to oppose legislation"

    
    # Test 2: Players commit to supporting and opposing
    print("\n📋 Test 2: Committing to Legislation")
    print("-" * 40)
    
    # Set Bob as current player
    state.current_player_index = 1
    
    # Bob supports the legislation
    support_action = ActionSupportLegislation(player_id=1, legislation_id="INFRASTRUCTURE", support_amount=10)
    state = engine.process_action(state, support_action)
    
    print(f"Bob committed 10 PC to support")
    print(f"Bob's PC after commitment: {state.players[1].pc}")
    assert state.players[1].pc == 40, "PC should be deducted immediately"

    # Verify the commitment is recorded in the term legislation
    active_bill = None
    for leg in state.term_legislation:
        if leg.legislation_id == "INFRASTRUCTURE":
            active_bill = leg
            break
    
    assert active_bill is not None, "Active bill should be found"
    assert active_bill.support_players.get(1) == 10, "Bob's support not recorded"

    # Set Charlie as current player
    state.current_player_index = 2

    # Charlie opposes the legislation
    oppose_action = ActionOpposeLegislation(player_id=2, legislation_id="INFRASTRUCTURE", oppose_amount=5)
    state = engine.process_action(state, oppose_action)
    print(f"Charlie committed 5 PC to oppose")
    print(f"Charlie's PC after commitment: {state.players[2].pc}")
    assert state.players[2].pc == 45, "PC should be deducted immediately"
    assert active_bill.oppose_players.get(2) == 5, "Charlie's opposition not recorded"

    print("\n✅ Secret commitment test completed!")
    print("=" * 50)


if __name__ == "__main__":
    test_secret_commitment_system() 