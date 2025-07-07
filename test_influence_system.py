#!/usr/bin/env python3
"""
Test script for the Influence System (dice-free legislation resolution).
Covers all major and edge cases for PC commitment, support, opposition, and war penalty.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionSponsorLegislation, ActionSupportLegislation, ActionOpposeLegislation, ActionFundraise
from engine import resolvers

# --- First Principles & Red Teaming ---
# 1. Legislation should pass if net influence >= success_target
# 2. Critical success if net influence >= crit_target
# 3. Failure if net influence < success_target
# 4. Supporters are rewarded if bill passes
# 5. Sponsor is penalized if bill fails
# 6. War penalty reduces net influence
# 7. Edge: Negative net influence, zero support, only opposition, etc.

def test_influence_system():
    print("\n🧪 Testing Influence System (Dice-Free Legislation Resolution)")
    print("=" * 60)
    
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Start a new game with 3 players
    state = engine.start_new_game(["Alice", "Bob", "Charlie"])
    
    # Give players PC for testing
    for p in state.players:
        p.pc = 20
    
    # --- Test 1: Pass at Success Threshold ---
    print("\nTest 1: Legislation passes at success threshold")
    state = engine.start_new_game(["Alice", "Bob"])
    for p in state.players:
        p.pc = 20
    action = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, action)
    # Advance to legislation session and resolve
    if state.pending_legislation is not None:
        state.term_legislation.append(state.pending_legislation)
        state.pending_legislation = None
    state.legislation_session_active = True
    # Now Bob supports with 8 PC (success_target) - during legislation session
    support_action = ActionSupportLegislation(player_id=1, legislation_id="INFRASTRUCTURE", support_amount=8)
    state = engine.process_action(state, support_action)
    # Debug: Check pending legislation state
    print(f"Pending legislation support: {state.pending_legislation.support_players if state.pending_legislation else 'None'}")
    print(f"Pending legislation oppose: {state.pending_legislation.oppose_players if state.pending_legislation else 'None'}")
    # Debug: Check term legislation state
    print(f"Term legislation count: {len(state.term_legislation)}")
    for i, leg in enumerate(state.term_legislation):
        print(f"  Term legislation {i}: support={leg.support_players}, oppose={leg.oppose_players}, resolved={leg.resolved}")
    # Simulate voting phase: advance turn for each player
    for _ in range(len(state.players)):
        # Use a dummy action to advance the turn (e.g., fundraise)
        dummy_action = ActionFundraise(player_id=state.current_player_index)
        state = engine.process_action(state, dummy_action)
    # Debug: Check legislation history
    print(f"Legislation history count: {len(state.legislation_history)}")
    if state.legislation_history:
        print(f"Last legislation history: {state.legislation_history[-1]}")
    # Should be "Success"
    outcome = state.legislation_history[-1]['outcome']
    print(f"Outcome: {outcome}")
    assert outcome == "Success", "Should pass at success threshold"
    
    # --- Test 2: Critical Success at crit_target ---
    print("\nTest 2: Critical success at crit_target")
    state = engine.start_new_game(["Alice", "Bob"])
    for p in state.players:
        p.pc = 20
    action = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, action)
    if state.pending_legislation is not None:
        state.term_legislation.append(state.pending_legislation)
        state.pending_legislation = None
    state.legislation_session_active = True
    support_action = ActionSupportLegislation(player_id=1, legislation_id="INFRASTRUCTURE", support_amount=15)
    state = engine.process_action(state, support_action)
    # Simulate voting phase: advance turn for each player
    for _ in range(len(state.players)):
        # Use a dummy action to advance the turn (e.g., fundraise)
        dummy_action = ActionFundraise(player_id=state.current_player_index)
        state = engine.process_action(state, dummy_action)
    outcome = state.legislation_history[-1]['outcome']
    print(f"Outcome: {outcome}")
    assert outcome == "Critical Success", "Should be critical at crit_target"
    
    # --- Test 3: Failure below threshold ---
    print("\nTest 3: Failure below threshold")
    state = engine.start_new_game(["Alice", "Bob"])
    for p in state.players:
        p.pc = 20
    action = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, action)
    if state.pending_legislation is not None:
        state.term_legislation.append(state.pending_legislation)
        state.pending_legislation = None
    state.legislation_session_active = True
    # Bob supports with 5 PC (below threshold)
    support_action = ActionSupportLegislation(player_id=1, legislation_id="INFRASTRUCTURE", support_amount=5)
    state = engine.process_action(state, support_action)
    # Simulate voting phase: advance turn for each player
    for _ in range(len(state.players)):
        # Use a dummy action to advance the turn (e.g., fundraise)
        dummy_action = ActionFundraise(player_id=state.current_player_index)
        state = engine.process_action(state, dummy_action)
    outcome = state.legislation_history[-1]['outcome']
    print(f"Outcome: {outcome}")
    assert outcome == "Failure", "Should fail below threshold"
    
    # --- Test 4: Supporters rewarded on pass ---
    print("\nTest 4: Supporters rewarded on pass")
    state = engine.start_new_game(["Alice", "Bob"])
    for p in state.players:
        p.pc = 20
    action = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, action)
    if state.pending_legislation is not None:
        state.term_legislation.append(state.pending_legislation)
        state.pending_legislation = None
    state.legislation_session_active = True
    support_action = ActionSupportLegislation(player_id=1, legislation_id="INFRASTRUCTURE", support_amount=8)
    state = engine.process_action(state, support_action)
    # Simulate voting phase: advance turn for each player
    for _ in range(len(state.players)):
        # Use a dummy action to advance the turn (e.g., fundraise)
        dummy_action = ActionFundraise(player_id=state.current_player_index)
        state = engine.process_action(state, dummy_action)
    bob = state.players[1]
    print(f"Bob PC after support and reward: {bob.pc}")
    assert bob.pc > 12, "Supporter should be rewarded on pass"
    
    # --- Test 5: Sponsor penalized on failure ---
    print("\nTest 5: Sponsor penalized on failure")
    state = engine.start_new_game(["Alice", "Bob"])
    for p in state.players:
        p.pc = 20
    print(f"Alice initial PC: {state.players[0].pc}")
    action = ActionSponsorLegislation(player_id=0, legislation_id="TAX_CODE")
    state = engine.process_action(state, action)
    print(f"Alice PC after sponsorship cost: {state.players[0].pc}")
    # No support
    if state.pending_legislation is not None:
        state.term_legislation.append(state.pending_legislation)
        state.pending_legislation = None
    state.legislation_session_active = True
    print(f"Legislation session active: {state.legislation_session_active}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    # Directly resolve legislation (same logic as engine)
    for legislation in state.term_legislation:
        if not legislation.resolved:
            state.pending_legislation = legislation
            state = resolvers.resolve_pending_legislation(state)
    state.term_legislation.clear()
    alice = state.players[0]
    print(f"Alice PC after failed sponsorship: {alice.pc}")
    print(f"Legislation history: {state.legislation_history[-1] if state.legislation_history else 'None'}")
    assert alice.pc < 10, "Sponsor should be penalized on failure"
    
    # --- Test 6: War penalty applies ---
    print("\nTest 6: War penalty applies")
    state = engine.start_new_game(["Alice", "Bob"])
    for p in state.players:
        p.pc = 20
    action = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, action)
    if state.pending_legislation is not None:
        state.term_legislation.append(state.pending_legislation)
        state.pending_legislation = None
    state.legislation_session_active = True
    state.active_effects.add("WAR_BREAKS_OUT")
    support_action = ActionSupportLegislation(player_id=1, legislation_id="INFRASTRUCTURE", support_amount=8)
    state = engine.process_action(state, support_action)
    # Simulate voting phase: advance turn for each player
    for _ in range(len(state.players)):
        # Use a dummy action to advance the turn (e.g., fundraise)
        dummy_action = ActionFundraise(player_id=state.current_player_index)
        state = engine.process_action(state, dummy_action)
    outcome = state.legislation_history[-1]['outcome']
    print(f"Outcome with war penalty: {outcome}")
    assert outcome == "Failure", "War penalty should reduce net influence and cause failure"
    
    # --- Test 7: Only opposition (negative net influence) ---
    print("\nTest 7: Only opposition (negative net influence)")
    state = engine.start_new_game(["Alice", "Bob"])
    for p in state.players:
        p.pc = 20
    action = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, action)
    if state.pending_legislation is not None:
        state.term_legislation.append(state.pending_legislation)
        state.pending_legislation = None
    state.legislation_session_active = True
    oppose_action = ActionOpposeLegislation(player_id=1, legislation_id="INFRASTRUCTURE", oppose_amount=5)
    state = engine.process_action(state, oppose_action)
    # Simulate voting phase: advance turn for each player
    for _ in range(len(state.players)):
        # Use a dummy action to advance the turn (e.g., fundraise)
        dummy_action = ActionFundraise(player_id=state.current_player_index)
        state = engine.process_action(state, dummy_action)
    outcome = state.legislation_history[-1]['outcome']
    print(f"Outcome with only opposition: {outcome}")
    assert outcome == "Failure", "Should fail with only opposition"
    
    # --- Test 8: Zero support and opposition ---
    print("\nTest 8: Zero support and opposition")
    state = engine.start_new_game(["Alice", "Bob"])
    for p in state.players:
        p.pc = 20
    action = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, action)
    if state.pending_legislation is not None:
        state.term_legislation.append(state.pending_legislation)
        state.pending_legislation = None
    state.legislation_session_active = True
    # Simulate voting phase: advance turn for each player
    for _ in range(len(state.players)):
        # Use a dummy action to advance the turn (e.g., fundraise)
        dummy_action = ActionFundraise(player_id=state.current_player_index)
        state = engine.process_action(state, dummy_action)
    outcome = state.legislation_history[-1]['outcome']
    print(f"Outcome with zero support/opposition: {outcome}")
    assert outcome == "Failure", "Should fail with zero support/opposition"
    
    print("\n🎉 Influence System tests completed!")

if __name__ == "__main__":
    test_influence_system() 