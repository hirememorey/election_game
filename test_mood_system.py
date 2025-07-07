#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.game_state import GameState
from models.components import Player, Office
from models.cards import PoliticalArchetype, PersonalMandate, Deck
from engine.resolvers import resolve_upkeep
from game_data import load_offices, load_archetypes, load_personal_mandates

def test_public_mood_system():
    """Test the public mood system to verify it works correctly."""
    
    print("🧪 Testing Public Mood System")
    print("=" * 50)
    
    # Load game data
    offices = load_offices()
    archetypes = load_archetypes()
    mandates = load_personal_mandates()
    
    # Create test players - use President (0 income) to isolate mood effect
    incumbent = Player(
        id=1,
        name="Incumbent Player",
        archetype=archetypes[0],  # INSIDER
        mandate=mandates[0],      # PRINCIPLED_LEADER
        pc=20,
        current_office=offices["PRESIDENT"]  # President has 0 income
    )
    
    outsider = Player(
        id=2,
        name="Outsider Player", 
        archetype=archetypes[1],  # POPULIST
        mandate=mandates[1],      # ENVIRONMENTALIST
        pc=20,
        current_office=None  # No office = outsider
    )
    
    # Test scenarios
    test_scenarios = [
        (-3, "Very Bad Mood"),
        (-2, "Bad Mood"), 
        (-1, "Slightly Bad Mood"),
        (0, "Neutral Mood"),
        (1, "Slightly Good Mood"),
        (2, "Good Mood"),
        (3, "Very Good Mood")
    ]
    
    for mood, description in test_scenarios:
        print(f"\n📊 Testing: {description} (Mood: {mood})")
        print("-" * 40)
        
        # Create fresh game state for each test
        state = GameState(
            players=[incumbent, outsider],
            offices=offices,
            legislation_options={},
            event_deck=Deck(),
            scrutiny_deck=Deck(),
            alliance_deck=Deck(),
            favor_supply=[],
            public_mood=mood
        )
        
        # Record initial PC values
        incumbent_initial_pc = incumbent.pc
        outsider_initial_pc = outsider.pc
        
        print(f"Before upkeep:")
        print(f"  Incumbent PC: {incumbent_initial_pc}")
        print(f"  Outsider PC: {outsider_initial_pc}")
        
        # Run upkeep phase
        state = resolve_upkeep(state)
        
        # Calculate changes
        incumbent_change = incumbent.pc - incumbent_initial_pc
        outsider_change = outsider.pc - outsider_initial_pc
        
        print(f"After upkeep:")
        print(f"  Incumbent PC: {incumbent.pc} ({incumbent_change:+d})")
        print(f"  Outsider PC: {outsider.pc} ({outsider_change:+d})")
        
        # Verify the logic
        expected_incumbent_change = mood
        expected_outsider_change = -mood
        
        print(f"Expected:")
        print(f"  Incumbent should {'gain' if mood >= 0 else 'lose'} {abs(mood)} PC")
        print(f"  Outsider should {'gain' if mood <= 0 else 'lose'} {abs(mood)} PC")
        
        # Check if results match expectations
        incumbent_correct = incumbent_change == expected_incumbent_change
        outsider_correct = outsider_change == expected_outsider_change
        
        if incumbent_correct and outsider_correct:
            print("✅ PASS: Public mood system working correctly!")
        else:
            print("❌ FAIL: Public mood system not working as expected!")
            if not incumbent_correct:
                print(f"   Incumbent: expected {expected_incumbent_change}, got {incumbent_change}")
            if not outsider_correct:
                print(f"   Outsider: expected {expected_outsider_change}, got {outsider_change}")
        
        # Reset PC for next test
        incumbent.pc = 20
        outsider.pc = 20

def test_mood_with_income():
    """Test public mood system with office income to show the combined effect."""
    
    print("\n\n💰 Testing Public Mood + Office Income")
    print("=" * 50)
    
    offices = load_offices()
    archetypes = load_archetypes()
    mandates = load_personal_mandates()
    
    # Create test players with State Senator (5 PC income)
    incumbent = Player(
        id=1,
        name="State Senator",
        archetype=archetypes[0],
        mandate=mandates[0],
        pc=20,
        current_office=offices["STATE_SENATOR"]  # 5 PC income
    )
    
    outsider = Player(
        id=2,
        name="Outsider",
        archetype=archetypes[1],
        mandate=mandates[1],
        pc=20,
        current_office=None
    )
    
    test_scenarios = [
        (-2, "Bad Mood"),
        (0, "Neutral Mood"),
        (2, "Good Mood")
    ]
    
    for mood, description in test_scenarios:
        print(f"\n📊 Testing: {description} (Mood: {mood})")
        print("-" * 40)
        
        state = GameState(
            players=[incumbent, outsider],
            offices=offices,
            legislation_options={},
            event_deck=Deck(),
            scrutiny_deck=Deck(),
            alliance_deck=Deck(),
            favor_supply=[],
            public_mood=mood
        )
        
        incumbent_initial_pc = incumbent.pc
        outsider_initial_pc = outsider.pc
        
        print(f"Before upkeep:")
        print(f"  State Senator PC: {incumbent_initial_pc}")
        print(f"  Outsider PC: {outsider_initial_pc}")
        
        state = resolve_upkeep(state)
        
        incumbent_change = incumbent.pc - incumbent_initial_pc
        outsider_change = outsider.pc - outsider_initial_pc
        
        print(f"After upkeep:")
        print(f"  State Senator PC: {incumbent.pc} ({incumbent_change:+d})")
        print(f"  Outsider PC: {outsider.pc} ({outsider_change:+d})")
        
        # Break down the effects
        mood_effect_incumbent = mood
        income_effect_incumbent = 5  # State Senator income
        total_expected_incumbent = mood_effect_incumbent + income_effect_incumbent
        
        mood_effect_outsider = -mood
        income_effect_outsider = 0  # No office income
        
        print(f"Breakdown:")
        print(f"  State Senator: {mood_effect_incumbent:+d} (mood) + {income_effect_incumbent:+d} (income) = {total_expected_incumbent:+d}")
        print(f"  Outsider: {mood_effect_outsider:+d} (mood) + {income_effect_outsider:+d} (income) = {mood_effect_outsider:+d}")
        
        # Check if results match expectations
        if incumbent_change == total_expected_incumbent and outsider_change == mood_effect_outsider:
            print("✅ PASS: Combined effects working correctly!")
        else:
            print("❌ FAIL: Combined effects not working as expected!")
        
        # Reset PC for next test
        incumbent.pc = 20
        outsider.pc = 20

def test_mood_log_messages():
    """Test that the log messages are correct."""
    
    print("\n\n📝 Testing Log Messages")
    print("=" * 50)
    
    offices = load_offices()
    archetypes = load_archetypes()
    mandates = load_personal_mandates()
    
    incumbent = Player(
        id=1,
        name="Test Incumbent",
        archetype=archetypes[0],
        mandate=mandates[0],
        pc=20,
        current_office=offices["PRESIDENT"]  # Use President to avoid income confusion
    )
    
    outsider = Player(
        id=2,
        name="Test Outsider",
        archetype=archetypes[1],
        mandate=mandates[1],
        pc=20,
        current_office=None
    )
    
    # Test with bad mood
    state = GameState(
        players=[incumbent, outsider],
        offices=offices,
        legislation_options={},
        event_deck=Deck(),
        scrutiny_deck=Deck(),
        alliance_deck=Deck(),
        favor_supply=[],
        public_mood=-2
    )
    
    print("Testing with bad mood (-2):")
    state = resolve_upkeep(state)
    
    # Print the log messages
    for message in state.turn_log:
        if "Public Mood" in message:
            print(f"  {message}")
    
    print("\nTesting with good mood (+2):")
    state.public_mood = 2
    state.turn_log = []  # Clear previous logs
    state = resolve_upkeep(state)
    
    for message in state.turn_log:
        if "Public Mood" in message:
            print(f"  {message}")

if __name__ == "__main__":
    test_public_mood_system()
    test_mood_with_income()
    test_mood_log_messages()
    print("\n�� Test complete!") 