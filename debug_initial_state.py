#!/usr/bin/env python3
"""
Debug script to check the initial game state
"""

from game_session import GameSession
import json

def debug_initial_state():
    print("=== DEBUGGING INITIAL GAME STATE ===")
    
    # Create a game session just like the server does
    session = GameSession()
    session.start_game()
    
    print(f"Human player ID: {session.human_player_id}")
    print(f"Current player index: {session.state.current_player_index}")
    print(f"Current player: {session.state.get_current_player().name} (ID: {session.state.get_current_player().id})")
    print(f"Is human turn? {session.is_human_turn()}")
    print(f"Game over? {session.is_game_over()}")
    
    print("\nPlayer details:")
    for i, player in enumerate(session.state.players):
        ap = session.state.action_points.get(player.id, 0)
        print(f"  Player {i}: {player.name} (ID: {player.id}, AP: {ap})")
        # Check mandate data
        if player.mandate:
            print(f"    Mandate: {player.mandate.title} - {player.mandate.description}")
        else:
            print(f"    Mandate: None")
    
    print(f"\nCurrent phase: {session.state.current_phase}")
    
    # Check what actions are available
    if session.is_human_turn():
        valid_actions = session.engine.get_valid_actions(session.state, session.human_player_id)
        print(f"\nValid actions for human: {len(valid_actions)}")
        for action in valid_actions:
            print(f"  - {action.to_dict()}")
    else:
        print("\nNot human turn - no actions available")
    
    # Check the state that would be sent to the client
    client_state = session.get_state_for_client()
    print(f"\nClient state keys: {list(client_state.keys())}")
    if 'valid_actions' in client_state:
        print(f"Valid actions in client state: {len(client_state['valid_actions'])}")
        for action in client_state['valid_actions']:
            print(f"  - {action}")
    else:
        print("No valid_actions in client state")
    
    # Check the players array that gets sent to the client
    print(f"\nPlayers in client state:")
    for i, player in enumerate(client_state['players']):
        print(f"  Player {i}: name='{player['name']}', id={player['id']}")
        # Check if mandate data is included
        if 'mandate' in player and player['mandate']:
            print(f"    Mandate: {player['mandate']['title']} - {player['mandate']['description']}")
        else:
            print(f"    Mandate: Not included or None")
    
    print(f"\nCurrent player index in client state: {client_state['current_player_index']}")
    
    # Simulate the frontend logic
    human_player = None
    for player in client_state['players']:
        if player['name'] == "Human":
            human_player = player
            break
    
    if human_player:
        print(f"\nFrontend would find human player: {human_player['name']} (ID: {human_player['id']})")
        print(f"Current player index: {client_state['current_player_index']}")
        print(f"Human player ID: {human_player['id']}")
        print(f"Match? {client_state['current_player_index'] == human_player['id']}")
        
        # Check human player's mandate
        if 'mandate' in human_player and human_player['mandate']:
            print(f"Human player mandate: {human_player['mandate']['title']}")
            print(f"Mandate description: {human_player['mandate']['description']}")
        else:
            print(f"Human player mandate: Not found in client state")
    else:
        print(f"\nFrontend would NOT find human player!")

if __name__ == "__main__":
    debug_initial_state() 