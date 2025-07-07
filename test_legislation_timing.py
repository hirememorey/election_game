#!/usr/bin/env python3
"""
Test script to track when legislation is being resolved.
This will help us understand why legislation is still being resolved after every round.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionSponsorLegislation, ActionSupportLegislation, ActionFundraise
from models.game_state import GameState

def test_legislation_timing():
    """Test to see when legislation gets resolved, including the full term and session phase."""
    
    # Load game data and create engine
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Start a new game
    state = engine.start_new_game(["Alice", "Bob"])
    
    print("=== Starting Legislation Timing Test ===")
    print(f"Initial phase: {state.current_phase}")
    print(f"Round: {state.round_marker}")
    
    # Run event phase
    print("\n--- Running Event Phase ---")
    state = engine.run_event_phase(state)
    print(f"Phase after event: {state.current_phase}")
    
    # Simulate 4 rounds of actions
    for round_num in range(1, 5):
        print(f"\n=== ROUND {round_num} ===")
        # Player 1 sponsors legislation in round 1 and 3
        if round_num in [1, 3]:
            print(f"- Alice sponsors INFRASTRUCTURE (round {round_num})")
            action = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
            state = engine.process_action(state, action)
        else:
            print(f"- Alice fundraises (round {round_num})")
            action = ActionFundraise(player_id=0)
            state = engine.process_action(state, action)
        # Player 2 supports legislation if pending, else fundraises
        if state.pending_legislation:
            print(f"- Bob supports INFRASTRUCTURE (round {round_num})")
            action = ActionSupportLegislation(player_id=1, legislation_id="INFRASTRUCTURE", support_amount=3)
            state = engine.process_action(state, action)
        else:
            print(f"- Bob fundraises (round {round_num})")
            action = ActionFundraise(player_id=1)
            state = engine.process_action(state, action)
        print(f"  Phase: {state.current_phase}, Round: {state.round_marker}")
        print(f"  Pending legislation: {state.pending_legislation is not None}")
        print(f"  Term legislation count: {len(state.term_legislation)}")
        if state.term_legislation:
            for i, leg in enumerate(state.term_legislation):
                print(f"    Term legislation {i}: {leg.legislation_id}, resolved: {leg.resolved}")
        print(f"  Legislation session active: {state.legislation_session_active}")
    
    # After 4 rounds, we should be in the legislation session
    print("\n=== After 4 rounds ===")
    print(f"Current phase: {state.current_phase}")
    print(f"Legislation session active: {state.legislation_session_active}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    for i, leg in enumerate(state.term_legislation):
        print(f"  Term legislation {i}: {leg.legislation_id}, resolved: {leg.resolved}")
    
    # Simulate all players voting (just fundraise to advance turns)
    while state.legislation_session_active:
        print(f"\n- Player {state.current_player_index} votes (simulated by fundraise)")
        action = ActionFundraise(player_id=state.current_player_index)
        state = engine.process_action(state, action)
        print(f"  Phase: {state.current_phase}, Legislation session active: {state.legislation_session_active}")
        for i, leg in enumerate(state.term_legislation):
            print(f"    Term legislation {i}: {leg.legislation_id}, resolved: {leg.resolved}")
    
    print("\n=== After legislation session ===")
    print(f"Current phase: {state.current_phase}")
    print(f"Term legislation count: {len(state.term_legislation)}")
    print(f"Legislation session active: {state.legislation_session_active}")
    print(f"Legislation history: {state.legislation_history}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_legislation_timing() 