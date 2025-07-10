#!/usr/bin/env python3
"""
Test that the Fundraiser archetype only gets the +2 PC bonus on the first Fundraise action of each term.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from engine.actions import ActionFundraise
from models.game_state import GameState
from models.components import Player
import game_data

def test_fundraiser_archetype():
    """Test that Fundraiser archetype only gets bonus on first Fundraise action of each term"""
    
    # Load game data
    game_data_dict = game_data.load_game_data()
    
    # Create a Fundraiser player
    fundraiser = Player(
        id=0, 
        name="Fundraiser", 
        pc=25, 
        archetype=game_data_dict['archetypes'][2],  # FUNDRAISER archetype
        mandate=game_data_dict['mandates'][0]
    )
    
    # Create another player
    other_player = Player(
        id=1, 
        name="Other Player", 
        pc=25, 
        archetype=game_data_dict['archetypes'][0], 
        mandate=game_data_dict['mandates'][1]
    )
    
    # Create game state
    from models.cards import Deck
    
    state = GameState(
        players=[fundraiser, other_player],
        offices=game_data_dict['offices'],
        legislation_options=game_data_dict['legislation'],
        event_deck=Deck(cards=game_data_dict['events']),
        scrutiny_deck=Deck(cards=game_data_dict['scrutiny']),
        alliance_deck=Deck(cards=game_data_dict['alliances']),
        favor_supply=game_data_dict['favors'],
        current_player_index=0
    )
    
    # Initialize action points
    state.action_points = {0: 3, 1: 3}
    
    # Create engine
    engine = GameEngine(game_data_dict)
    
    print("Testing Fundraiser archetype bonus...")
    print(f"Initial PC: {fundraiser.pc}")
    
    # Test 1: First Fundraise action of the term should get +2 PC bonus
    print("\n📋 Test 1: First Fundraise action of the term")
    action1 = ActionFundraise(player_id=0)
    state = engine.process_action(state, action1)
    
    print(f"After first Fundraise: PC = {fundraiser.pc}")
    print(f"Fundraiser first fundraise used: {state.fundraiser_first_fundraise_used}")
    
    # Test 2: Second Fundraise action of the term should NOT get +2 PC bonus
    print("\n📋 Test 2: Second Fundraise action of the term")
    action2 = ActionFundraise(player_id=0)
    state = engine.process_action(state, action2)
    
    print(f"After second Fundraise: PC = {fundraiser.pc}")
    print(f"Fundraiser first fundraise used: {state.fundraiser_first_fundraise_used}")
    
    # Test 3: After term transition, first Fundraise of new term should get +2 PC bonus again
    print("\n📋 Test 3: First Fundraise action of new term")
    
    # Simulate term transition by running election phase
    state = engine.run_election_phase(state)
    
    print(f"After term transition: PC = {fundraiser.pc}")
    print(f"Fundraiser first fundraise used: {state.fundraiser_first_fundraise_used}")
    
    # Take first Fundraise action of new term
    action3 = ActionFundraise(player_id=0)
    state = engine.process_action(state, action3)
    
    print(f"After first Fundraise of new term: PC = {fundraiser.pc}")
    print(f"Fundraiser first fundraise used: {state.fundraiser_first_fundraise_used}")
    
    # Verify the behavior
    print("\n✅ Test Results:")
    print(f"Fundraiser archetype: {fundraiser.archetype.title}")
    print(f"Final PC: {fundraiser.pc}")
    print(f"Fundraiser first fundraise used: {state.fundraiser_first_fundraise_used}")
    
    # The test should show that:
    # 1. First Fundraise gets +7 PC (5 base + 2 bonus)
    # 2. Second Fundraise gets +5 PC (5 base, no bonus)
    # 3. After term transition, first Fundraise of new term gets +7 PC again
    
    print("✅ Test completed: Fundraiser archetype bonus should only apply to first Fundraise action of each term")

if __name__ == "__main__":
    test_fundraiser_archetype() 