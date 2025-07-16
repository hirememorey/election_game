#!/usr/bin/env python3
"""
Test script to debug what the frontend is receiving from the API call.
"""

import requests
import json

def test_frontend_debug():
    """Test to see what the frontend is receiving from the API call."""
    
    print("=== Frontend Debug Test ===\n")
    
    # Start a new game
    print("1. Creating new game...")
    response = requests.post('http://localhost:5001/api/game', 
                           json={'player_names': ['Alice', 'Bob', 'Charlie']})
    game_data = response.json()
    game_id = game_data['game_id']
    print(f"   Game created with ID: {game_id}")
    
    # Get initial state
    print("\n2. Getting initial game state...")
    response = requests.get(f'http://localhost:5001/api/game/{game_id}')
    state = response.json()['state']
    print(f"   Initial player: {state['players'][state['current_player_index']]['name']}")
    print(f"   Initial player index: {state['current_player_index']}")
    
    # Simulate the frontend pass turn API call
    print("\n3. Simulating frontend pass turn API call...")
    current_player = state['players'][state['current_player_index']]
    action_data = {
        'action_type': 'pass_turn',
        'player_id': current_player['id']
    }
    
    response = requests.post(f'http://localhost:5001/api/game/{game_id}/action', 
                           json=action_data)
    
    if response.status_code != 200:
        print(f"   ❌ API call failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return
    
    result = response.json()
    print(f"   ✅ API call successful")
    
    if result.get('state'):
        new_state = result['state']
        print(f"   New player: {new_state['players'][new_state['current_player_index']]['name']}")
        print(f"   New player index: {new_state['current_player_index']}")
        print(f"   Action points: {new_state['action_points']}")
        print(f"   Turn log: {new_state['turn_log']}")
        
        # Check if turn actually advanced
        if new_state['current_player_index'] != state['current_player_index']:
            print("   ✅ Turn advancement successful")
        else:
            print("   ❌ Turn advancement failed")
    else:
        print("   ❌ No state in response")
    
    # Get the state again to see if it's consistent
    print("\n4. Getting state again to verify...")
    response = requests.get(f'http://localhost:5001/api/game/{game_id}')
    final_state = response.json()['state']
    print(f"   Final player: {final_state['players'][final_state['current_player_index']]['name']}")
    print(f"   Final player index: {final_state['current_player_index']}")
    print(f"   Final action points: {final_state['action_points']}")

if __name__ == "__main__":
    try:
        test_frontend_debug()
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc() 