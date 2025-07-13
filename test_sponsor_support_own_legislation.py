#!/usr/bin/env python3
"""
Test script to verify that sponsors can now support their own legislation with additional PC commitment.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionSponsorLegislation, ActionSupportLegislation, ActionOpposeLegislation, ActionFundraise

def advance_to_player(state, engine, target_player_id):
    """Helper function to advance to a specific player's turn."""
    while state.current_player_index != target_player_id:
        # Use a dummy action to advance the turn
        action = ActionFundraise(player_id=state.current_player_index)
        state = engine.process_action(state, action)
    return state

def test_sponsor_support_own_legislation():
    """Test that sponsors can support their own legislation with additional PC commitment."""
    print("🧪 Testing Sponsor Support Own Legislation")
    print("=" * 60)
    
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
    
    # Test 1: Alice sponsors legislation
    print("📜 Test 1: Alice sponsors legislation")
    print("-" * 40)
    
    # Ensure Alice is the current player
    state = advance_to_player(state, engine, 0)
    
    # Alice sponsors Infrastructure Bill
    sponsor_action = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, sponsor_action)
    print(f"Alice PC after sponsoring: {state.players[0].pc}")
    print(f"Pending legislation: {state.pending_legislation is not None}")
    if state.pending_legislation:
        print(f"  - Legislation ID: {state.pending_legislation.legislation_id}")
        print(f"  - Sponsor ID: {state.pending_legislation.sponsor_id}")
        print(f"  - Support players: {state.pending_legislation.support_players}")
        print(f"  - Oppose players: {state.pending_legislation.oppose_players}")
    
    # Test 2: Alice supports her own legislation
    print("\n✅ Test 2: Alice supports her own legislation")
    print("-" * 50)
    
    # Ensure Alice is still the current player
    state = advance_to_player(state, engine, 0)
    
    # Alice supports her own legislation with 5 PC
    support_action = ActionSupportLegislation(player_id=0, legislation_id="INFRASTRUCTURE", support_amount=5)
    state = engine.process_action(state, support_action)
    print(f"Alice PC after supporting own legislation: {state.players[0].pc}")
    
    if state.pending_legislation:
        print(f"  - Support players: {state.pending_legislation.support_players}")
        print(f"  - Oppose players: {state.pending_legislation.oppose_players}")
    
    # Test 3: Alice supports her own legislation again (additional commitment)
    print("\n💰 Test 3: Alice commits additional PC to her legislation")
    print("-" * 60)
    
    # Ensure Alice is still the current player
    state = advance_to_player(state, engine, 0)
    
    # Alice supports her own legislation with another 3 PC
    support_action2 = ActionSupportLegislation(player_id=0, legislation_id="INFRASTRUCTURE", support_amount=3)
    state = engine.process_action(state, support_action2)
    print(f"Alice PC after additional support: {state.players[0].pc}")
    
    if state.pending_legislation:
        print(f"  - Support players: {state.pending_legislation.support_players}")
        print(f"  - Total support: {sum(state.pending_legislation.support_players.values())} PC")
    
    # Test 4: Bob opposes Alice's legislation
    print("\n❌ Test 4: Bob opposes Alice's legislation")
    print("-" * 50)
    
    # Ensure Bob is the current player
    state = advance_to_player(state, engine, 1)
    
    # Bob opposes Alice's legislation with 4 PC
    oppose_action = ActionOpposeLegislation(player_id=1, legislation_id="INFRASTRUCTURE", oppose_amount=4)
    state = engine.process_action(state, oppose_action)
    print(f"Bob PC after opposing: {state.players[1].pc}")
    
    if state.pending_legislation:
        print(f"  - Support players: {state.pending_legislation.support_players}")
        print(f"  - Oppose players: {state.pending_legislation.oppose_players}")
        print(f"  - Net influence: {sum(state.pending_legislation.support_players.values()) - sum(state.pending_legislation.oppose_players.values())} PC")
    
    # Test 5: Alice opposes her own legislation (strategic move)
    print("\n🎭 Test 5: Alice opposes her own legislation (strategic move)")
    print("-" * 60)
    
    # Ensure Alice is the current player
    state = advance_to_player(state, engine, 0)
    
    # Alice opposes her own legislation with 2 PC (for strategic reasons)
    oppose_action2 = ActionOpposeLegislation(player_id=0, legislation_id="INFRASTRUCTURE", oppose_amount=2)
    state = engine.process_action(state, oppose_action2)
    print(f"Alice PC after opposing own legislation: {state.players[0].pc}")
    
    if state.pending_legislation:
        print(f"  - Support players: {state.pending_legislation.support_players}")
        print(f"  - Oppose players: {state.pending_legislation.oppose_players}")
        print(f"  - Net influence: {sum(state.pending_legislation.support_players.values()) - sum(state.pending_legislation.oppose_players.values())} PC")
    
    # Test 6: Verify legislation resolution works with sponsor support
    print("\n📊 Test 6: Verify legislation resolution with sponsor support")
    print("-" * 60)
    
    # Move legislation to term legislation for resolution
    if state.pending_legislation:
        state.term_legislation.append(state.pending_legislation)
        state.pending_legislation = None
    
    # Resolve the legislation
    from engine import resolvers
    for legislation in state.term_legislation:
        if not legislation.resolved:
            state.pending_legislation = legislation
            state = resolvers.resolve_pending_legislation(state)
            break
    
    print(f"Final Alice PC: {state.players[0].pc}")
    print(f"Final Bob PC: {state.players[1].pc}")
    
    print("\n✅ Sponsor support own legislation test completed!")
    print("=" * 60)
    
    return state

if __name__ == "__main__":
    test_sponsor_support_own_legislation() 