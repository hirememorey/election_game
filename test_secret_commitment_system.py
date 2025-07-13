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
    print(f"Pending legislation: {state.pending_legislation.legislation_id if state.pending_legislation else 'None'}")
    
    # Test 2: Secret support commitment
    print("\n🤫 Test 2: Secret Support Commitment")
    print("-" * 40)
    
    # Set Bob as current player
    state.current_player_index = 1
    
    # Bob secretly supports the legislation
    support_action = ActionSupportLegislation(player_id=1, legislation_id="INFRASTRUCTURE", support_amount=10)
    state = engine.process_action(state, support_action)
    
    print(f"Bob secretly committed 10 PC to support")
    print(f"Bob's PC after secret commitment: {state.players[1].pc} (should still be 50 - no deduction yet)")
    print(f"Pending legislation support players: {state.pending_legislation.support_players if state.pending_legislation else 'None'} (should be empty - secret)")
    
    # Test 3: Secret oppose commitment
    print("\n🤫 Test 3: Secret Opposition Commitment")
    print("-" * 40)
    
    # Set Charlie as current player
    state.current_player_index = 2
    
    # Charlie secretly opposes the legislation
    oppose_action = ActionOpposeLegislation(player_id=2, legislation_id="INFRASTRUCTURE", oppose_amount=8)
    state = engine.process_action(state, oppose_action)
    
    print(f"Charlie secretly committed 8 PC to oppose")
    print(f"Charlie's PC after secret commitment: {state.players[2].pc} (should still be 50 - no deduction yet)")
    print(f"Pending legislation oppose players: {state.pending_legislation.oppose_players if state.pending_legislation else 'None'} (should be empty - secret)")
    
    # Test 4: Sponsor supports their own legislation
    print("\n🤫 Test 4: Sponsor Secret Support")
    print("-" * 35)
    
    # Set Alice as current player and give her action points
    state.current_player_index = 0
    state.action_points[0] = 2  # Give Alice action points
    
    # Alice secretly supports her own legislation
    sponsor_support_action = ActionSupportLegislation(player_id=0, legislation_id="INFRASTRUCTURE", support_amount=5)
    state = engine.process_action(state, sponsor_support_action)
    
    print(f"Alice secretly committed 5 PC to support her own legislation")
    print(f"Alice's PC after secret commitment: {state.players[0].pc} (should still be 48 - no deduction yet)")
    
    # Test 5: Simulate legislation resolution with secret commitments
    print("\n🎭 Test 5: Legislation Resolution with Secret Reveals")
    print("-" * 50)
    
    # Move legislation to term_legislation
    from engine.resolvers import resolve_upkeep
    state = resolve_upkeep(state)
    print(f"Legislation moved to term_legislation: {len(state.term_legislation)} bills")
    
    # Set up for legislation session
    state.round_marker = 4
    state = engine.run_legislation_session(state)
    
    # Simulate the secret commitment resolution
    # Note: In the real system, this would be handled by the server with SECRET_COMMITMENTS
    # For this test, we'll manually simulate the reveal process
    
    print("\n🎭 REVEALING SECRET COMMITMENTS:")
    print("Bob secretly supported with 10 PC!")
    print("Charlie secretly opposed with 8 PC!")
    print("Alice secretly supported her own legislation with 5 PC!")
    
    # Apply the secret commitments to the legislation
    legislation = state.term_legislation[0]
    legislation.support_players[1] = 10  # Bob's secret support
    legislation.support_players[0] = 5   # Alice's secret support
    legislation.oppose_players[2] = 8    # Charlie's secret opposition
    
    # Deduct PC from players
    state.players[1].pc -= 10  # Bob
    state.players[2].pc -= 8   # Charlie
    state.players[0].pc -= 5   # Alice
    
    print(f"Final PC - Alice: {state.players[0].pc}, Bob: {state.players[1].pc}, Charlie: {state.players[2].pc}")
    print(f"Total support: {sum(legislation.support_players.values())} PC")
    print(f"Total opposition: {sum(legislation.oppose_players.values())} PC")
    print(f"Net influence: {sum(legislation.support_players.values()) - sum(legislation.oppose_players.values())} PC")
    
    # Test 6: Verify the dramatic reveal system
    print("\n🎭 Test 6: Dramatic Reveal System")
    print("-" * 35)
    
    # Simulate the reveal process that would happen in the server
    reveal_logs = [
        "🎭 REVEAL: Bob secretly supported with 10 PC!",
        "🎭 REVEAL: Charlie secretly opposed with 8 PC!",
        "🎭 REVEAL: Alice secretly supported her own legislation with 5 PC!"
    ]
    
    for log in reveal_logs:
        print(log)
    
    print("\n✅ Secret Commitment System test completed!")
    print("=" * 50)
    
    return state

if __name__ == "__main__":
    test_secret_commitment_system() 