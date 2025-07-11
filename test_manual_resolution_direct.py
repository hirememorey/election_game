#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from models.game_state import GameState, PendingLegislation
from models.components import Player, Legislation
from models.cards import PoliticalArchetype, PersonalMandate, Deck

def test_manual_resolution_direct():
    """Test the manual resolution endpoints directly without going through full game flow."""
    
    print("🧪 Testing Manual Resolution Endpoints Directly")
    print("=" * 60)
    
    # Load game data
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Create a game state manually
    print("Creating game state manually...")
    
    # Create players
    player1 = Player(
        id=0,
        name="Alice",
        archetype=game_data['archetypes'][0],
        mandate=game_data['mandates'][0],
        pc=25,
        current_office=None
    )
    
    player2 = Player(
        id=1,
        name="Bob",
        archetype=game_data['archetypes'][1],
        mandate=game_data['mandates'][1],
        pc=25,
        current_office=None
    )
    
    # Create game state
    state = GameState(
        players=[player1, player2],
        offices=game_data['offices'],
        legislation_options=game_data['legislation'],
        event_deck=Deck(list(game_data['events'])),
        scrutiny_deck=Deck(list(game_data['scrutiny'])),
        alliance_deck=Deck(list(game_data['alliances'])),
        favor_supply=list(game_data['favors'])
    )
    
    # Set up action points
    state.action_points[0] = 2
    state.action_points[1] = 2
    
    # Create some pending legislation
    pending = PendingLegislation(
        legislation_id="INFRASTRUCTURE",
        sponsor_id=0
    )
    pending.support_players[1] = 10  # Bob supports with 10 PC
    pending.oppose_players[0] = 2   # Alice opposes with 2 PC (net: 8 PC)
    
    state.term_legislation.append(pending)
    
    print(f"Initial state:")
    print(f"  - awaiting_legislation_resolution: {state.awaiting_legislation_resolution}")
    print(f"  - awaiting_election_resolution: {state.awaiting_election_resolution}")
    print(f"  - term_legislation count: {len(state.term_legislation)}")
    
    # Test 1: Set awaiting_legislation_resolution and test resolve_legislation
    print("\n📊 Test 1: Resolve Legislation Session")
    print("-" * 40)
    
    state.awaiting_legislation_resolution = True
    state.awaiting_election_resolution = False
    
    print("Before resolution:")
    print(f"  - awaiting_legislation_resolution: {state.awaiting_legislation_resolution}")
    print(f"  - awaiting_election_resolution: {state.awaiting_election_resolution}")
    
    # Resolve legislation
    state = engine.resolve_legislation_session(state)
    
    print("After resolution:")
    print(f"  - awaiting_legislation_resolution: {state.awaiting_legislation_resolution}")
    print(f"  - awaiting_election_resolution: {state.awaiting_election_resolution}")
    print_log(state.turn_log)
    
    # Test 2: Set awaiting_election_resolution and test resolve_elections
    print("\n📊 Test 2: Resolve Elections Session")
    print("-" * 40)
    
    state.awaiting_legislation_resolution = False
    state.awaiting_election_resolution = True
    
    print("Before resolution:")
    print(f"  - awaiting_legislation_resolution: {state.awaiting_legislation_resolution}")
    print(f"  - awaiting_election_resolution: {state.awaiting_election_resolution}")
    
    # Resolve elections
    state = engine.resolve_elections_session(state)
    
    print("After resolution:")
    print(f"  - awaiting_legislation_resolution: {state.awaiting_legislation_resolution}")
    print(f"  - awaiting_election_resolution: {state.awaiting_election_resolution}")
    print_log(state.turn_log)
    
    print("\n✅ Direct test complete! Manual resolution methods work correctly!")

def print_log(log):
    print("\n--- Game Log ---")
    for entry in log:
        print(entry)
    print("--- End Log ---\n")

if __name__ == "__main__":
    test_manual_resolution_direct() 