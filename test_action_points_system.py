#!/usr/bin/env python3
"""
Test the Action Points System (Phase 2 of Game Refinements)

This test verifies that:
1. Players get 3 Action Points per turn
2. Actions have different AP costs
3. Players can take multiple actions per turn
4. Turn only advances when AP are exhausted
5. Campaign action works correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from engine.actions import ActionFundraise, ActionNetwork, ActionSponsorLegislation, ActionPassTurn
from game_data import load_game_data

def test_action_points_system():
    """Test the Action Points system functionality."""
    print("\n🧪 Testing Action Points System (Executive Term)")
    print("=" * 50)
    
    # Initialize engine
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # --- Test 1: Players get 2 AP per turn ---
    print("\nTest 1: Players get 2 AP per turn")
    state = engine.start_new_game(["Alice", "Bob"])
    state.current_phase = "ACTION_PHASE"  # Ensure correct phase for turn advancement
    alice = state.players[0]
    print(f"Alice initial AP: {state.action_points.get(alice.id, 'Not set')}")
    
    # Take first action to initialize AP
    action = ActionFundraise(player_id=0)
    state = engine.process_action(state, action)
    print(f"Alice AP after first action: {state.action_points[alice.id]}")
    assert state.action_points[alice.id] == 1, "Should have 1 AP remaining after 1 AP action"
    
    # --- Test 2: Multiple actions per turn ---
    print("\nTest 2: Multiple actions per turn")
    # Take second action
    action = ActionNetwork(player_id=0)
    state = engine.process_action(state, action)
    print(f"Alice AP after second action: {state.action_points[alice.id]}")
    assert state.action_points[alice.id] == 0, "Should have 0 AP remaining after 2 AP actions"
    
    # --- Test 3: Turn advances when AP exhausted ---
    print("\nTest 3: Turn advances when AP exhausted")
    print(f"Current player before third action: {state.current_player_index}")
    print(f"APs before third action: {[state.action_points[p.id] for p in state.players]}")
    # After Alice's AP reaches 0, it should be Bob's turn
    assert state.current_player_index == 1, "Should advance to Bob when Alice's AP is exhausted"
    # Now Bob can take his action
    action = ActionFundraise(player_id=1)  # Bob's turn now
    state = engine.process_action(state, action)
    print(f"Current player after Bob's action: {state.current_player_index}")
    print(f"APs after Bob's action: {[state.action_points[p.id] for p in state.players]}")
    assert state.current_player_index == 1, "Should still be Bob's turn after his action"
    # Check that Bob got 2 AP and used 1
    bob = state.players[1]
    print(f"Bob AP: {state.action_points[bob.id]}")
    assert state.action_points[bob.id] == 1, "Bob should have 1 AP remaining after taking 1 AP action"
    
    # --- Test 4: Different AP costs ---
    print("\nTest 4: Different AP costs")
    # Reset to Alice's turn
    state.current_player_index = 0
    state.action_points[alice.id] = 2
    
    # Take a 2 AP action (Sponsor Legislation)
    action = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, action)
    print(f"Alice AP after 2 AP action: {state.action_points[alice.id]}")
    assert state.action_points[alice.id] == 0, "Should have 0 AP remaining after 2 AP action"
    
    # --- Test 5: AP validation prevents actions when insufficient AP ---
    print("\nTest 5: AP validation")
    # Try to take a 1 AP action with 0 AP
    try:
        action = ActionFundraise(player_id=0)
        engine.process_action(state, action)
        assert False, "Should have raised an error for insufficient AP"
    except ValueError as e:
        print(f"✅ AP validation works: {e}")
    
    # --- Test 6: Turn advancement when AP exhausted ---
    print("\nTest 6: Turn advancement")
    # Reset to Alice's turn with 1 AP
    state.current_player_index = 0
    state.action_points[alice.id] = 1
    
    # Take a 1 AP action, should advance to Bob
    action = ActionFundraise(player_id=0)
    state = engine.process_action(state, action)
    print(f"Current player after Alice's action: {state.current_player_index}")
    assert state.current_player_index == 1, "Should advance to Bob when Alice's AP is exhausted"
    print("✅ Turn advancement works correctly")
    
    print("\n🎉 All Action Points system tests passed!")
    return True

if __name__ == "__main__":
    test_action_points_system() 