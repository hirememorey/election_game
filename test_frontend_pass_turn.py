#!/usr/bin/env python3
"""
Test script to verify the frontend pass turn API call is working correctly.
"""

import requests
import json

def test_frontend_pass_turn():
    """Test the frontend pass turn API call to see if it's working correctly."""
    
    print("=== Frontend Pass Turn Test ===\n")
    
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
    
    print(f"   Action data: {action_data}")
    
    response = requests.post(f'http://localhost:5001/api/game/{game_id}/action', 
                           json=action_data)
    
    if response.status_code != 200:
        print(f"   ❌ API call failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return False
    
    result = response.json()
    print(f"   ✅ API call successful")
    print(f"   Response: {result}")
    
    if result.get('state'):
        new_state = result['state']
        print(f"   New player: {new_state['players'][new_state['current_player_index']]['name']}")
        print(f"   New player index: {new_state['current_player_index']}")
        
        # Check if turn actually advanced
        if new_state['current_player_index'] != state['current_player_index']:
            print("   ✅ Turn advancement successful")
            return True
        else:
            print("   ❌ Turn advancement failed")
            return False
    else:
        print("   ❌ No state in response")
        return False

if __name__ == "__main__":
    try:
        success = test_frontend_pass_turn()
        
        if success:
            print("\n✅ Frontend pass turn API call is working correctly")
            print("The issue is likely in the frontend UI update after the API call")
        else:
            print("\n❌ Frontend pass turn API call is failing")
            
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc() 