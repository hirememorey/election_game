#!/usr/bin/env python3
"""
Test script to verify legislation session PC commitment fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionSupportLegislation, ActionOpposeLegislation, ActionFundraise

def test_legislation_session_pc_commitment():
    """Test that PC commitment works correctly in legislation session."""
    print("🧪 Testing Legislation Session PC Commitment")
    print("=" * 50)
    
    # Load game data and create engine
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Start a new game with 2 players
    state = engine.start_new_game(["Alice", "Bob"])
    
    # Give players some resources for testing
    state.players[0].pc = 30  # Alice
    state.players[1].pc = 25  # Bob
    
    print(f"Initial state:")
    print(f"Alice: {state.players[0].pc} PC")
    print(f"Bob: {state.players[1].pc} PC")
    print()
    
    # Set up legislation session
    state.round_marker = 4
    state.current_phase = "LEGISLATION_PHASE"
    state.legislation_session_active = True
    state.current_trade_phase = False  # Skip trading, go straight to voting
    
    # Add some legislation to vote on
    from models.game_state import PendingLegislation
    state.term_legislation.append(PendingLegislation(
        legislation_id="INFRASTRUCTURE",
        sponsor_id=1  # Bob sponsors, Alice can support/oppose
    ))
    
    print("📋 Test: Legislation session PC commitment")
    print(f"Legislation session active: {state.legislation_session_active}")
    print(f"Current phase: {state.current_phase}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    
    # Alice supports with 5 PC (Bob's legislation)
    print("\nAlice supports Bob's legislation with 5 PC...")
    support_action = ActionSupportLegislation(player_id=0, legislation_id="INFRASTRUCTURE", support_amount=5)
    state = engine.process_action(state, support_action)
    print(f"Alice PC after supporting: {state.players[0].pc}")
    
    # Bob opposes with 3 PC (can't oppose own legislation, so this should fail)
    print("Bob tries to oppose his own legislation with 3 PC...")
    oppose_action = ActionOpposeLegislation(player_id=1, legislation_id="INFRASTRUCTURE", oppose_amount=3)
    state = engine.process_action(state, oppose_action)
    print(f"Bob PC after trying to oppose: {state.players[1].pc}")
    
    # Check legislation state
    for i, legislation in enumerate(state.term_legislation):
        print(f"\nLegislation {i}:")
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
    
    print("\n✅ Legislation session PC commitment test completed!")
    return state

if __name__ == "__main__":
    test_legislation_session_pc_commitment() 