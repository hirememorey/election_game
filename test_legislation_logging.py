#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.game_state import GameState, PendingLegislation
from models.components import Player, Office, Legislation
from models.cards import PoliticalArchetype, PersonalMandate, Deck
from engine.resolvers import resolve_pending_legislation
from game_data import load_offices, load_archetypes, load_personal_mandates

def test_legislation_logging():
    """Test that legislation results are properly logged to the game log."""
    
    print("🧪 Testing Legislation Logging")
    print("=" * 50)
    
    # Load game data
    offices = load_offices()
    archetypes = load_archetypes()
    mandates = load_personal_mandates()
    
    # Create test players
    player1 = Player(
        id=0,
        name="Test Player 1",
        archetype=archetypes[0],
        mandate=mandates[0],
        pc=20,
        current_office=None
    )
    
    player2 = Player(
        id=1,
        name="Test Player 2", 
        archetype=archetypes[1],
        mandate=mandates[1],
        pc=20,
        current_office=None
    )
    
    # Create initial game state
    state = GameState(
        players=[player1, player2],
        offices=offices,
        legislation_options={},
        event_deck=Deck(),
        scrutiny_deck=Deck(),
        alliance_deck=Deck(),
        favor_supply=[],
        public_mood=0
    )
    
    # Add some test legislation
    test_bill = Legislation(
        id="TEST_BILL",
        title="Test Infrastructure Bill",
        cost=5,
        success_target=8,
        crit_target=15,
        success_reward=10,
        crit_reward=12,
        failure_penalty=0,
        mood_change=1
    )
    state.legislation_options["TEST_BILL"] = test_bill
    
    # Create pending legislation
    pending = PendingLegislation(
        legislation_id="TEST_BILL",
        sponsor_id=0
    )
    
    # Add some support and opposition
    pending.support_players[1] = 10  # Player 2 supports with 10 PC
    pending.oppose_players[0] = 2   # Player 1 opposes with 2 PC (net: 8 PC)
    
    state.pending_legislation = pending
    
    print(f"Initial game log entries: {len(state.turn_log)}")
    print(f"Pending legislation: {state.pending_legislation is not None}")
    
    # Resolve the legislation
    print("\n📊 Resolving Legislation")
    print("-" * 40)
    
    state = resolve_pending_legislation(state)
    
    print(f"After resolution - game log entries: {len(state.turn_log)}")
    print(f"Pending legislation resolved: {state.pending_legislation is None}")
    
    # Check the log entries
    print("\n📊 Game Log Entries")
    print("-" * 40)
    
    for i, log_entry in enumerate(state.turn_log):
        print(f"{i+1}. {log_entry}")
    
    # Check if we have the expected log entries
    expected_entries = [
        "--- Resolving Test Infrastructure Bill (Influence System) ---",
        "Support: Test Player 2 (10 PC)",
        "Opposition: Test Player 1 (2 PC)",
        "Net influence: 8 PC",
        "Success! Test Player 1 gains 10 PC.",
        "Test Player 2 receives 10 PC for supporting successful legislation."
    ]
    
    print("\n📊 Checking for Expected Log Entries")
    print("-" * 40)
    
    found_entries = []
    for expected in expected_entries:
        found = any(expected in entry for entry in state.turn_log)
        found_entries.append(found)
        print(f"'{expected}': {'✅ Found' if found else '❌ Missing'}")
    
    all_found = all(found_entries)
    print(f"\nOverall result: {'✅ All expected entries found' if all_found else '❌ Some entries missing'}")
    
    # Check legislation history
    print(f"\n📊 Legislation History")
    print("-" * 40)
    print(f"History entries: {len(state.legislation_history)}")
    if state.legislation_history:
        for entry in state.legislation_history:
            print(f"  - {entry}")
    
    print("\n✅ Legislation logging test completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_legislation_logging() 