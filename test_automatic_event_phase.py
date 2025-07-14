#!/usr/bin/env python3
"""
Test script to verify automatic event phase at the start of each round and term.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionFundraise

def test_automatic_event_phase():
    """Test that event phases are automatic at the start of each round and term."""
    print("🧪 Testing Automatic Event Phase")
    print("=" * 50)
    
    # Load game data and create engine
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Start a new game with 2 players
    state = engine.start_new_game(["Alice", "Bob"])
    
    print(f"Initial state:")
    print(f"Round: {state.round_marker}, Phase: {state.current_phase}")
    print()
    
    # Test 1: First round should start with event phase already completed
    print("📋 Test 1: First round event phase")
    print(f"After game start: Round {state.round_marker}, Phase {state.current_phase}")
    
    # Run the event phase first to get to ACTION_PHASE
    print("\nRunning event phase...")
    state = engine.run_event_phase(state)
    print(f"After event phase: Round {state.round_marker}, Phase {state.current_phase}")
    
    # Complete first round
    print("\nCompleting first round...")
    # Take actions for each player in turn order
    for _ in range(len(state.players)):
        current_player = state.current_player_index
        action = ActionFundraise(player_id=current_player)
        state = engine.process_action(state, action)
        print(f"Player {current_player} fundraises, PC: {state.players[current_player].pc}")
    
    # This should trigger upkeep and automatically start round 2 with event phase
    print(f"After first round: Round {state.round_marker}, Phase {state.current_phase}")
    
    # Complete second round
    print("\nCompleting second round...")
    for _ in range(len(state.players)):
        current_player = state.current_player_index
        action = ActionFundraise(player_id=current_player)
        state = engine.process_action(state, action)
        print(f"Player {current_player} fundraises, PC: {state.players[current_player].pc}")
    
    print(f"After second round: Round {state.round_marker}, Phase {state.current_phase}")
    
    # Complete third round
    print("\nCompleting third round...")
    for _ in range(len(state.players)):
        current_player = state.current_player_index
        action = ActionFundraise(player_id=current_player)
        state = engine.process_action(state, action)
        print(f"Player {current_player} fundraises, PC: {state.players[current_player].pc}")
    
    print(f"After third round: Round {state.round_marker}, Phase {state.current_phase}")
    
    # Complete fourth round (end of term)
    print("\nCompleting fourth round (end of term)...")
    for _ in range(len(state.players)):
        current_player = state.current_player_index
        action = ActionFundraise(player_id=current_player)
        state = engine.process_action(state, action)
        print(f"Player {current_player} fundraises, PC: {state.players[current_player].pc}")
    
    print(f"After fourth round: Round {state.round_marker}, Phase {state.current_phase}")
    
    # Complete election phase (should automatically start new term with event phase)
    print("\nCompleting election phase...")
    state = engine.run_election_phase(state)
    print(f"After election phase: Round {state.round_marker}, Phase {state.current_phase}")
    
    # Test 2: New term should start with event phase already completed
    print("\n📋 Test 2: New term event phase")
    print(f"New term: Round {state.round_marker}, Phase {state.current_phase}")
    
    # Complete first round of new term
    print("\nCompleting first round of new term...")
    for _ in range(len(state.players)):
        current_player = state.current_player_index
        action = ActionFundraise(player_id=current_player)
        state = engine.process_action(state, action)
        print(f"Player {current_player} fundraises, PC: {state.players[current_player].pc}")
    
    print(f"After first round of new term: Round {state.round_marker}, Phase {state.current_phase}")
    
    print("\n✅ Automatic event phase test completed!")
    print("=" * 50)
    
    return state

if __name__ == "__main__":
    test_automatic_event_phase() 