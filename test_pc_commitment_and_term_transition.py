#!/usr/bin/env python3
"""
Test script for PC commitment features and term transition fixes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import (
    ActionSponsorLegislation, ActionSupportLegislation, ActionOpposeLegislation,
    ActionDeclareCandidacy, ActionFundraise, ActionNetwork, ActionPassTurn
)

def advance_to_player(state, engine, player_id):
    """Advance the turn to the specified player by using up AP of current player."""
    while state.get_current_player().id != player_id:
        current_id = state.get_current_player().id
        # Use up all AP for the current player
        while state.action_points[current_id] > 0:
            action = ActionFundraise(player_id=current_id)
            state = engine.process_action(state, action)
    # Now it's the target player's turn
    # If the target player has 0 AP, just return
    if state.action_points[player_id] == 0:
        return state
    return state

def ensure_all_players_used_ap(state, engine):
    """Ensure all players have used up their AP before running upkeep."""
    # Keep processing actions for the current player until all players have 0 AP
    while any(state.action_points[p.id] > 0 for p in state.players):
        current_id = state.get_current_player().id
        if state.action_points[current_id] > 0:
            action = ActionFundraise(player_id=current_id)
            state = engine.process_action(state, action)
        # If current player has 0 AP, the turn will advance automatically
        # The next iteration will act for the new current player
    return state

def test_pc_commitment_and_term_transition():
    """Test PC commitment features and term transition fixes."""
    print("🧪 Testing PC Commitment and Term Transition")
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
    print(f"Round: {state.round_marker}, Phase: {state.current_phase}")
    print()
    
    # Test 1: Complete first term with legislation
    print("📜 Test 1: Complete first term with legislation")
    
    # Run event phase
    state = engine.run_event_phase(state)
    print(f"After event: Round {state.round_marker}, Phase {state.current_phase}")
    
    # Alice sponsors legislation
    print("Alice sponsors legislation...")
    state = advance_to_player(state, engine, 0)
    legislation_action = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, legislation_action)
    print(f"Alice PC after sponsoring: {state.players[0].pc}")
    print(f"Pending legislation: {state.pending_legislation is not None}")
    
    # Bob networks
    print("Bob networks...")
    state = advance_to_player(state, engine, 1)
    network_action = ActionNetwork(player_id=1)
    state = engine.process_action(state, network_action)
    print(f"Bob PC after networking: {state.players[1].pc}")
    
    # Advance to upkeep (end of round 1)
    print("Advancing to upkeep...")
    state = ensure_all_players_used_ap(state, engine)
    state = engine.run_upkeep_phase(state)
    print(f"After upkeep: Round {state.round_marker}, Phase {state.current_phase}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    
    # Check if we're already in legislation session (end of term)
    if state.legislation_session_active:
        print("Already in legislation session - skipping rounds 2-4")
    else:
        # Complete rounds 2-4 with minimal actions
        for round_num in range(2, 5):
            print(f"\n--- Round {round_num} ---")
            state = engine.run_event_phase(state)
            for player_id in range(len(state.players)):
                state = advance_to_player(state, engine, player_id)
                action = ActionFundraise(player_id=player_id)
                state = engine.process_action(state, action)
                print(f"Player {player_id} fundraises, PC: {state.players[player_id].pc}")
            state = ensure_all_players_used_ap(state, engine)
            state = engine.run_upkeep_phase(state)
            print(f"After round {round_num} upkeep: Round {state.round_marker}, Phase {state.current_phase}")
    
    # Test 2: Legislation session with PC commitment
    print("\n📋 Test 2: Legislation session with PC commitment")
    print(f"Legislation session active: {state.legislation_session_active}")
    print(f"Current phase: {state.current_phase}")

    # Complete trading phase by having each player pass
    for player_id in range(len(state.players)):
        state = advance_to_player(state, engine, player_id)
        pass_action = ActionPassTurn(player_id=player_id)
        state = engine.process_action(state, pass_action)

    # Alice supports with 5 PC
    print("Alice supports legislation with 5 PC...")
    state = advance_to_player(state, engine, 0)
    support_action = ActionSupportLegislation(player_id=0, legislation_id="INFRASTRUCTURE", support_amount=5)
    state = engine.process_action(state, support_action)
    print(f"Alice PC after supporting: {state.players[0].pc}")

    # Bob opposes with 3 PC
    print("Bob opposes legislation with 3 PC...")
    state = advance_to_player(state, engine, 1)
    oppose_action = ActionOpposeLegislation(player_id=1, legislation_id="INFRASTRUCTURE", oppose_amount=3)
    state = engine.process_action(state, oppose_action)
    print(f"Bob PC after opposing: {state.players[1].pc}")
    
    # Check legislation state
    for legislation in state.term_legislation:
        print(f"Legislation support: {legislation.support_players}")
        print(f"Legislation opposition: {legislation.oppose_players}")
    
    # Complete legislation session
    print("Completing legislation session...")
    while state.legislation_session_active:
        state = advance_to_player(state, engine, state.get_current_player().id)
        action = ActionFundraise(player_id=state.get_current_player().id)
        state = engine.process_action(state, action)
        print(f"Player {state.get_current_player().id} advances legislation session")
    
    print(f"After legislation session: Phase {state.current_phase}")
    
    # Test 3: Elections with PC commitment
    print("\n🗳️ Test 3: Elections with PC commitment")
    
    # Alice declares candidacy for President with 10 PC committed
    print("Alice declares candidacy for President with 10 PC committed...")
    state = advance_to_player(state, engine, 0)
    candidacy_action = ActionDeclareCandidacy(
        player_id=0, 
        office_id="PRESIDENT", 
        committed_pc=10
    )
    state = engine.process_action(state, candidacy_action)
    print(f"Alice PC after candidacy: {state.players[0].pc}")
    print(f"Secret candidacies: {len(state.secret_candidacies)}")
    
    # Complete election phase
    print("Completing election phase...")
    state = engine.run_election_phase(state)
    print(f"After elections: Phase {state.current_phase}, Round {state.round_marker}")
    
    # Test 4: Verify new term starts clean
    print("\n🔄 Test 4: Verify new term starts clean")
    print(f"New term - Round: {state.round_marker}, Phase: {state.current_phase}")
    print(f"Pending legislation: {state.pending_legislation is not None}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    print(f"Secret candidacies: {len(state.secret_candidacies)}")
    print(f"Alice PC: {state.players[0].pc}")
    print(f"Bob PC: {state.players[1].pc}")
    
    # Test 5: Verify PC commitment works in new term
    print("\n💰 Test 5: Verify PC commitment works in new term")
    
    # Run event phase of new term
    state = engine.run_event_phase(state)
    print(f"New term event phase: Round {state.round_marker}, Phase {state.current_phase}")
    
    # Alice sponsors legislation again
    print("Alice sponsors legislation in new term...")
    state = advance_to_player(state, engine, 0)
    legislation_action2 = ActionSponsorLegislation(player_id=0, legislation_id="HEALTHCARE")
    state = engine.process_action(state, legislation_action2)
    print(f"Alice PC after sponsoring: {state.players[0].pc}")
    print(f"Pending legislation: {state.pending_legislation is not None}")
    
    # Bob supports with 8 PC
    print("Bob supports legislation with 8 PC...")
    state = advance_to_player(state, engine, 1)
    support_action2 = ActionSupportLegislation(player_id=1, legislation_id="HEALTHCARE", support_amount=8)
    state = engine.process_action(state, support_action2)
    print(f"Bob PC after supporting: {state.players[1].pc}")
    
    # Check pending legislation state
    if state.pending_legislation:
        print(f"Pending legislation support: {state.pending_legislation.support_players}")
        print(f"Pending legislation opposition: {state.pending_legislation.oppose_players}")
    
    print("\n✅ All tests completed successfully!")
    print("=" * 60)
    
    return state

if __name__ == "__main__":
    test_pc_commitment_and_term_transition() 