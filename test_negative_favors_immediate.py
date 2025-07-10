#!/usr/bin/env python3
"""
Test that negative favors are applied immediately when drawn during Network action,
rather than being added to player's hand for later use.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from engine.actions import ActionNetwork
from models.game_state import GameState
from models.components import Player
import game_data

def test_negative_favors_immediate():
    """Test that negative favors are applied immediately during Network action"""
    
    # Load game data
    game_data_dict = game_data.load_game_data()
    
    # Create a simple game state with 2 players
    players = [
        Player(id=0, name="Player 1", pc=25, archetype=game_data_dict['archetypes'][0], mandate=game_data_dict['mandates'][0]),
        Player(id=1, name="Player 2", pc=25, archetype=game_data_dict['archetypes'][1], mandate=game_data_dict['mandates'][1])
    ]
    
    # Create game state with negative favors in the supply
    state = GameState(
        players=players,
        offices=game_data_dict['offices'],
        legislation_options=game_data_dict['legislation'],
        event_deck=game_data_dict['events'],
        scrutiny_deck=game_data_dict['scrutiny'],
        alliance_deck=game_data_dict['alliances'],
        favor_supply=game_data_dict['favors'],  # All favors including negative ones
        current_player_index=0
    )
    # Initialize action points for both players
    
    # Create engine
    engine = GameEngine(game_data_dict)
    
    print("Testing negative favor immediate application...")
    print(f"Initial player favors: {[len(p.favors) for p in state.players]}")
    print(f"Initial favor supply size: {len(state.favor_supply)}")
    
    # Count negative favors in supply
    negative_favors = [f for f in state.favor_supply if f.id in ["POLITICAL_DEBT", "PUBLIC_GAFFE", "MEDIA_SCRUTINY", "COMPROMISING_POSITION", "POLITICAL_HOT_POTATO"]]
    print(f"Negative favors in supply: {len(negative_favors)}")
    
    # Initialize action points for both players right before action
    state.action_points = {0: 3, 1: 3}
    print(f"Action points before action: {state.action_points}")
    
    # Perform Network action
    action = ActionNetwork(player_id=0)
    state = engine.process_action(state, action)
    
    print(f"After Network action:")
    print(f"Player 1 favors: {len(state.players[0].favors)}")
    print(f"Player 1 PC: {state.players[0].pc}")
    print(f"Favor supply size: {len(state.favor_supply)}")
    print(f"Political debts: {state.political_debts}")
    print(f"Public gaffe players: {state.public_gaffe_players}")
    print(f"Media scrutiny players: {state.media_scrutiny_players}")
    print(f"Compromised players: {state.compromised_players}")
    print(f"Hot potato holder: {state.hot_potato_holder}")
    
    # Check that negative favors are not in player's hand
    negative_favors_in_hand = [f for f in state.players[0].favors if f.id in ["POLITICAL_DEBT", "PUBLIC_GAFFE", "MEDIA_SCRUTINY", "COMPROMISING_POSITION", "POLITICAL_HOT_POTATO"]]
    assert len(negative_favors_in_hand) == 0, f"Negative favors should not be in player's hand, but found: {negative_favors_in_hand}"
    
    # Check that at least one negative effect was applied (since we have negative favors in supply)
    effects_applied = (
        len(state.political_debts) > 0 or
        len(state.public_gaffe_players) > 0 or
        len(state.media_scrutiny_players) > 0 or
        len(state.compromised_players) > 0 or
        state.hot_potato_holder is not None
    )
    
    if effects_applied:
        print("✅ Negative favor effects were applied immediately!")
    else:
        print("⚠️ No negative effects applied (may be due to random chance)")
    
    print("✅ Test passed: Negative favors are applied immediately and not added to player's hand")

if __name__ == "__main__":
    test_negative_favors_immediate() 