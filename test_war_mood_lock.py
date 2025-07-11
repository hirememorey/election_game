#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.game_state import GameState
from models.components import Player, Office
from models.cards import PoliticalArchetype, PersonalMandate, Deck
from engine.resolvers import apply_public_mood_effect, _event_war_breaks_out, _event_tech_leap, _event_natural_disaster
from game_data import load_offices, load_archetypes, load_personal_mandates

def test_war_mood_lock():
    """Test that war properly locks public mood and prevents other events from changing it."""
    
    print("🧪 Testing War Mood Lock Bug Fix")
    print("=" * 50)
    
    # Load game data
    offices = load_offices()
    archetypes = load_archetypes()
    mandates = load_personal_mandates()
    
    # Create test players
    player1 = Player(
        id=1,
        name="Test Player 1",
        archetype=archetypes[0],
        mandate=mandates[0],
        pc=20,
        current_office=None
    )
    
    player2 = Player(
        id=2,
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
        public_mood=0  # Start at neutral
    )
    
    print(f"Initial public mood: {state.public_mood}")
    
    # Test 1: Normal mood change before war
    print("\n📊 Test 1: Normal mood change (before war)")
    print("-" * 40)
    
    # Apply a positive mood change
    state = apply_public_mood_effect(state, mood_change=1, pc_bonus=3)
    print(f"After +1 mood change: {state.public_mood}")
    
    # Apply a negative mood change
    state = apply_public_mood_effect(state, mood_change=-1, pc_bonus=3)
    print(f"After -1 mood change: {state.public_mood}")
    
    # Test 2: War breaks out
    print("\n📊 Test 2: War breaks out")
    print("-" * 40)
    
    # Trigger war event
    state = _event_war_breaks_out(state)
    print(f"After war event: {state.public_mood}")
    print(f"Active effects: {state.active_effects}")
    
    # Test 3: Try to change mood during war
    print("\n📊 Test 3: Attempt mood changes during war")
    print("-" * 40)
    
    # Try positive mood change
    state = apply_public_mood_effect(state, mood_change=1, pc_bonus=3)
    print(f"After +1 mood change attempt: {state.public_mood}")
    
    # Try negative mood change
    state = apply_public_mood_effect(state, mood_change=-1, pc_bonus=3)
    print(f"After -1 mood change attempt: {state.public_mood}")
    
    # Test 4: Other events that should be blocked
    print("\n📊 Test 4: Other events during war")
    print("-" * 40)
    
    # Try tech leap event (should be blocked)
    state = _event_tech_leap(state)
    print(f"After tech leap event: {state.public_mood}")
    
    # Try natural disaster event (should be blocked)
    state = _event_natural_disaster(state)
    print(f"After natural disaster event: {state.public_mood}")
    
    # Test 5: Verify log messages
    print("\n📊 Test 5: Log messages")
    print("-" * 40)
    
    # Print relevant log messages
    for message in state.turn_log:
        if "Public Mood" in message or "War" in message:
            print(f"  {message}")
    
    # Test 6: Verify war effect is cleared at term end
    print("\n📊 Test 6: War effect clearing")
    print("-" * 40)
    
    # Simulate term end by clearing active effects
    state.active_effects.clear()
    print(f"After clearing effects: {state.active_effects}")
    
    # Try mood change again (should work now)
    state = apply_public_mood_effect(state, mood_change=1, pc_bonus=3)
    print(f"After +1 mood change (war cleared): {state.public_mood}")
    
    print("\n✅ War mood lock test completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_war_mood_lock() 