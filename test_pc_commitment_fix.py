#!/usr/bin/env python3
"""
Test script to verify that PC commitments are properly deducted immediately when made.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionSponsorLegislation, ActionSupportLegislation, ActionOpposeLegislation

def test_pc_commitment_deduction():
    """Test that PC is deducted immediately when commitments are made."""
    print("🧪 Testing PC Commitment Deduction Fix")
    print("=" * 50)
    
    # Load game data and create engine
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Start a new game with 2 players
    state = engine.start_new_game(["Alice", "Bob"])
    
    # Give players some PC to work with
    state.players[0].pc = 25  # Alice
    state.players[1].pc = 30  # Bob
    
    print(f"Initial PC - Alice: {state.players[0].pc}, Bob: {state.players[1].pc}")
    
    # Test 1: Sponsor legislation
    print("\n📋 Test 1: Sponsoring Legislation")
    print("-" * 30)
    
    # Alice sponsors legislation
    sponsor_action = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, sponsor_action)
    
    print(f"Alice sponsored Infrastructure Bill")
    print(f"Alice's PC after sponsoring: {state.players[0].pc}")
    
    # Test 2: Support commitment - PC should be deducted immediately
    print("\n🤫 Test 2: Support Commitment - PC Deduction")
    print("-" * 45)
    
    # Advance to Bob's turn
    state.current_player_index = 1
    state.action_points[1] = 2  # Give Bob action points
    
    # Bob supports with 15 PC
    support_action = ActionSupportLegislation(player_id=1, legislation_id="INFRASTRUCTURE", support_amount=15)
    state = engine.process_action(state, support_action)
    
    print(f"Bob committed 15 PC to support")
    print(f"Bob's PC after supporting: {state.players[1].pc} (should be 15)")
    
    # Verify Bob's PC was deducted
    expected_pc = 30 - 15  # Initial PC - committed amount
    if state.players[1].pc == expected_pc:
        print("✅ PASS: Bob's PC was properly deducted immediately")
    else:
        print(f"❌ FAIL: Bob's PC should be {expected_pc}, but is {state.players[1].pc}")
    
    # Test 3: Oppose commitment - PC should be deducted immediately
    print("\n🤫 Test 3: Oppose Commitment - PC Deduction")
    print("-" * 45)
    
    # Advance to Alice's turn
    state.current_player_index = 0
    state.action_points[0] = 2  # Give Alice action points
    
    # Alice opposes with 10 PC
    oppose_action = ActionOpposeLegislation(player_id=0, legislation_id="INFRASTRUCTURE", oppose_amount=10)
    state = engine.process_action(state, oppose_action)
    
    print(f"Alice committed 10 PC to oppose")
    print(f"Alice's PC after opposing: {state.players[0].pc} (should be 10)")
    
    # Verify Alice's PC was deducted
    expected_pc = 20 - 10  # PC after sponsoring - committed amount
    if state.players[0].pc == expected_pc:
        print("✅ PASS: Alice's PC was properly deducted immediately")
    else:
        print(f"❌ FAIL: Alice's PC should be {expected_pc}, but is {state.players[0].pc}")
    
    # Test 4: Try to commit more PC than available
    print("\n🚫 Test 4: Over-commitment Prevention")
    print("-" * 35)
    
    # Advance to Bob's turn
    state.current_player_index = 1
    state.action_points[1] = 2  # Give Bob action points
    
    # Bob tries to support with 20 PC (only has 15 left)
    support_action2 = ActionSupportLegislation(player_id=1, legislation_id="INFRASTRUCTURE", support_amount=20)
    state = engine.process_action(state, support_action2)
    
    print(f"Bob tried to commit 20 PC (only has 15 left)")
    print(f"Bob's PC after failed attempt: {state.players[1].pc} (should still be 15)")
    
    # Verify Bob's PC wasn't deducted
    if state.players[1].pc == 15:
        print("✅ PASS: Bob's PC was not deducted for invalid commitment")
    else:
        print(f"❌ FAIL: Bob's PC should be 15, but is {state.players[1].pc}")
    
    # Test 5: Verify secret commitments are stored
    print("\n🔍 Test 5: Secret Commitment Storage")
    print("-" * 35)
    
    # Check that the secret commitments are stored (this would be in server.py)
    print("Secret commitments should be stored in SECRET_COMMITMENTS")
    print("This will be verified during the reveal phase")
    
    print("\n✅ PC Commitment Deduction Fix Test Completed!")
    return state

if __name__ == "__main__":
    test_pc_commitment_deduction() 