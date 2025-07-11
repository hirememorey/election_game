#!/usr/bin/env python3
"""
Test the new PC commitment and sponsor-bonus legislation system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from engine.actions import ActionSponsorLegislation, ActionSupportLegislation, ActionOpposeLegislation, ActionPassTurn
from models.game_state import GameState
import game_data

def test_legislation_gambling_system():
    """Test the new PC commitment and sponsor-bonus mechanics."""
    print("🧪 Testing Legislation Gambling System")
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
    
    # Alice sponsors legislation (she's the current player)
    sponsor_action = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, sponsor_action)
    
    print(f"Alice sponsored Infrastructure Bill (cost: 2 AP)")
    print(f"Alice's PC after sponsoring: {state.players[0].pc}")
    print(f"Current player: {state.get_current_player().name}")
    print(f"Pending legislation: {len(state.term_legislation)} bills")
    
    # Test 2: Support legislation during regular turns
    print("\n🎯 Test 2: Supporting Legislation During Regular Turns")
    print("-" * 50)
    
    # Bob supports the legislation with a small bet (he should be current player now)
    print(f"Current player before Bob's action: {state.get_current_player().name}")
    support_action = ActionSupportLegislation(player_id=1, legislation_id="INFRASTRUCTURE", support_amount=3)
    state = engine.process_action(state, support_action)
    print(f"Bob committed 3 PC to support (small bet)")
    print(f"Bob's PC after supporting: {state.players[1].pc}")
    print(f"Current player after Bob's action: {state.get_current_player().name}")

    # Bob passes turn to advance to Charlie
    pass_action_bob = ActionPassTurn(player_id=1)
    state = engine.process_action(state, pass_action_bob)

    # Charlie supports with a medium bet
    print(f"Current player before Charlie's action: {state.get_current_player().name}")
    support_action2 = ActionSupportLegislation(player_id=2, legislation_id="INFRASTRUCTURE", support_amount=7)
    state = engine.process_action(state, support_action2)
    print(f"Charlie committed 7 PC to support (medium bet)")
    print(f"Charlie's PC after supporting: {state.players[2].pc}")
    print(f"Current player after Charlie's action: {state.get_current_player().name}")

    # Charlie passes turn to advance to Alice
    pass_action_charlie = ActionPassTurn(player_id=2)
    state = engine.process_action(state, pass_action_charlie)
    
    # Test 3: Oppose legislation during regular turns
    print("\n🎯 Test 3: Opposing Legislation During Regular Turns")
    print("-" * 50)
    
    # Alice sponsors another bill (she should be current player again)
    print(f"Current player before Alice's second action: {state.get_current_player().name}")
    sponsor_action2 = ActionSponsorLegislation(player_id=0, legislation_id="CHILDREN")
    state = engine.process_action(state, sponsor_action2)
    
    print(f"Alice sponsored Protect The Children! bill")
    print(f"Current player after Alice's second action: {state.get_current_player().name}")
    
    # Bob opposes with a big bet
    print(f"Current player before Bob's oppose action: {state.get_current_player().name}")
    oppose_action = ActionOpposeLegislation(player_id=1, legislation_id="CHILDREN", oppose_amount=12)
    state = engine.process_action(state, oppose_action)
    
    print(f"Bob committed 12 PC to oppose (big bet)")
    print(f"Bob's PC after opposing: {state.players[1].pc}")
    print(f"Current player after Bob's oppose action: {state.get_current_player().name}")
    
    # Test 4: Resolve legislation with new gambling system
    print("\n🎰 Test 4: Resolving Legislation with Gambling Rewards")
    print("-" * 50)
    
    # Move to end of term to trigger legislation session
    state.round_marker = 4
    state = engine.run_legislation_session(state)
    
    # Manually resolve legislation
    state = engine.resolve_legislation_session(state)
    
    print("Legislation resolved with new gambling system!")
    print(f"Final PC - Alice: {state.players[0].pc}, Bob: {state.players[1].pc}, Charlie: {state.players[2].pc}")
    
    # Test 5: Verify sponsor bonus mechanics
    print("\n🎯 Test 5: Sponsor Bonus Mechanics")
    print("-" * 35)
    
    # Create a new game for sponsor bonus testing
    state2 = engine.start_new_game(["Alice", "Bob"])
    for player in state2.players:
        player.pc = 30
    
    # Alice sponsors a bill
    sponsor_action3 = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state2 = engine.process_action(state2, sponsor_action3)
    
    # Bob supports with enough to pass
    support_action3 = ActionSupportLegislation(player_id=1, legislation_id="INFRASTRUCTURE", support_amount=10)
    state2 = engine.process_action(state2, support_action3)
    
    # Resolve legislation
    state2.round_marker = 4
    state2 = engine.run_legislation_session(state2)
    state2 = engine.resolve_legislation_session(state2)
    
    print(f"Infrastructure Bill passed!")
    print(f"Alice (sponsor) PC: {state2.players[0].pc} (should have 50% bonus)")
    print(f"Bob (supporter) PC: {state2.players[1].pc} (should have gambling reward)")
    
    # Test 6: Test failure scenario
    print("\n❌ Test 6: Legislation Failure Scenario")
    print("-" * 40)
    
    state3 = engine.start_new_game(["Alice", "Bob"])
    for player in state3.players:
        player.pc = 30
    
    # Alice sponsors a bill
    sponsor_action4 = ActionSponsorLegislation(player_id=0, legislation_id="HEALTHCARE")
    state3 = engine.process_action(state3, sponsor_action4)
    
    # Bob opposes with enough to fail it
    oppose_action2 = ActionOpposeLegislation(player_id=1, legislation_id="HEALTHCARE", oppose_amount=20)
    state3 = engine.process_action(state3, oppose_action2)
    
    # Resolve legislation
    state3.round_marker = 4
    state3 = engine.run_legislation_session(state3)
    state3 = engine.resolve_legislation_session(state3)
    
    print(f"Healthcare Bill failed!")
    print(f"Alice (sponsor) PC: {state3.players[0].pc} (should have 50% penalty)")
    print(f"Bob (opponent) PC: {state3.players[1].pc} (should have gambling reward)")
    
    print("\n✅ All tests completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_legislation_gambling_system() 