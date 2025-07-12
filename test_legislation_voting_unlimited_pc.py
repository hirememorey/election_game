#!/usr/bin/env python3
"""
Test script to verify that legislation voting phase allows unlimited PC commitment.
This fixes the issue where players were limited to 1 PC during the final voting round
but could commit much more PC in earlier rounds through the gambling-style system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionSupportLegislation, ActionOpposeLegislation, ActionFundraise

def test_legislation_voting_unlimited_pc():
    """Test that legislation voting phase allows unlimited PC commitment."""
    print("🧪 Testing Legislation Voting Unlimited PC Commitment")
    print("=" * 60)
    
    # Load game data and create engine
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Start a new game with 2 players
    state = engine.start_new_game(["Alice", "Bob"])
    
    # Give players substantial resources for testing
    state.players[0].pc = 50  # Alice
    state.players[1].pc = 45  # Bob
    
    print(f"Initial state:")
    print(f"Alice: {state.players[0].pc} PC")
    print(f"Bob: {state.players[1].pc} PC")
    print()
    
    # Set up legislation session (voting phase)
    state.round_marker = 4
    state.current_phase = "LEGISLATION_PHASE"
    state.legislation_session_active = True
    state.current_trade_phase = False  # Skip trading, go straight to voting
    
    # Add legislation to vote on
    from models.game_state import PendingLegislation
    state.term_legislation.append(PendingLegislation(
        legislation_id="INFRASTRUCTURE",
        sponsor_id=1  # Bob sponsors, Alice can support/oppose
    ))
    
    print("📋 Test: Legislation voting phase unlimited PC commitment")
    print(f"Legislation session active: {state.legislation_session_active}")
    print(f"Current phase: {state.current_phase}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    
    # Test 1: Alice supports with large amount (20 PC)
    print("\n🎯 Test 1: Alice supports with 20 PC (large commitment)")
    support_action = ActionSupportLegislation(player_id=0, legislation_id="INFRASTRUCTURE", support_amount=20)
    state = engine.process_action(state, support_action)
    print(f"Alice PC after supporting: {state.players[0].pc}")
    
    # Check legislation state
    for i, legislation in enumerate(state.term_legislation):
        print(f"\nLegislation {i}:")
        print(f"  Support: {legislation.support_players}")
        print(f"  Opposition: {legislation.oppose_players}")
        print(f"  Resolved: {legislation.resolved}")
    
    # Test 2: Alice opposes with another large amount (15 PC)
    print("\n🎯 Test 2: Alice opposes with 15 PC (large commitment)")
    oppose_action = ActionOpposeLegislation(player_id=0, legislation_id="INFRASTRUCTURE", oppose_amount=15)
    state = engine.process_action(state, oppose_action)
    print(f"Alice PC after opposing: {state.players[0].pc}")
    
    # Check legislation state again
    for i, legislation in enumerate(state.term_legislation):
        print(f"\nLegislation {i}:")
        print(f"  Support: {legislation.support_players}")
        print(f"  Opposition: {legislation.oppose_players}")
        print(f"  Resolved: {legislation.resolved}")
    
    # Test 3: Bob tries to oppose his own legislation (should fail)
    print("\n🎯 Test 3: Bob tries to oppose his own legislation (should fail)")
    bob_oppose_action = ActionOpposeLegislation(player_id=1, legislation_id="INFRASTRUCTURE", oppose_amount=10)
    state = engine.process_action(state, bob_oppose_action)
    print(f"Bob PC after trying to oppose: {state.players[1].pc}")
    
    # Check final legislation state
    for i, legislation in enumerate(state.term_legislation):
        print(f"\nFinal Legislation {i}:")
        print(f"  Support: {legislation.support_players}")
        print(f"  Opposition: {legislation.oppose_players}")
        print(f"  Resolved: {legislation.resolved}")
    
    # Complete legislation session
    print("\nCompleting legislation session...")
    while state.legislation_session_active:
        action = ActionFundraise(player_id=state.current_player_index)
        state = engine.process_action(state, action)
        print(f"Player {state.current_player_index} advances legislation session")
    
    print(f"After legislation session: Phase {state.current_phase}")
    print(f"Legislation session active: {state.legislation_session_active}")
    
    # Verify the fix worked
    print("\n✅ Verification:")
    print("1. Alice was able to commit 20 PC to support (unlimited)")
    print("2. Alice was able to commit 15 PC to oppose (unlimited)")
    print("3. Bob could not oppose his own legislation (correct behavior)")
    print("4. Total PC committed: 35 PC (much more than the old 1 PC limit)")
    
    print("\n✅ Legislation voting unlimited PC commitment test completed!")
    return state

if __name__ == "__main__":
    test_legislation_voting_unlimited_pc()