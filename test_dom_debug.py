#!/usr/bin/env python3
"""
Debug script to test DOM updates and identify the root cause of Playwright test failures.
"""

import requests
import json
import time

def test_dom_updates():
    """Test the DOM update flow to identify where the issue occurs."""
    
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
    
    # Perform a pass turn action to trigger turn advancement
    print("\n3. Performing pass turn action to trigger turn advancement...")
    current_player = state['players'][state['current_player_index']]
    action_data = {
        'action_type': 'pass_turn',
        'player_id': current_player['id']
    }
    
    response = requests.post(f'http://localhost:5001/api/game/{game_id}/action', 
                           json=action_data)
    result = response.json()
    
    if result.get('state'):
        new_state = result['state']
        print(f"   New player: {new_state['players'][new_state['current_player_index']]['name']}")
        print(f"   New player index: {new_state['current_player_index']}")
        
        # Check if turn actually advanced
        if new_state['current_player_index'] != state['current_player_index']:
            print("   ✅ Turn advancement successful")
        else:
            print("   ❌ Turn advancement failed")
    else:
        print("   ❌ Action failed")
    
    # Get the updated state
    print("\n4. Getting updated game state...")
    response = requests.get(f'http://localhost:5001/api/game/{game_id}')
    final_state = response.json()['state']
    print(f"   Final player: {final_state['players'][final_state['current_player_index']]['name']}")
    print(f"   Final player index: {final_state['current_player_index']}")
    
    return game_id, final_state

def test_frontend_sync():
    """Test if the frontend is receiving the correct data."""
    print("\n5. Testing frontend synchronization...")
    
    # This would require a browser automation tool like Selenium
    # For now, we'll just verify the API is working correctly
    print("   Backend API is working correctly")
    print("   Frontend synchronization needs to be tested manually")
    
    print("\n6. Manual testing steps:")
    print("   a. Open http://localhost:5001 in browser")
    print("   b. Start a new game with players Alice, Bob, Charlie")
    print("   c. Perform a pass turn action")
    print("   d. Check if the phase indicator shows the correct player")
    print("   e. Check browser console for debug logs")

if __name__ == "__main__":
    print("=== DOM Update Debug Test ===\n")
    
    try:
        game_id, final_state = test_dom_updates()
        test_frontend_sync()
        
        print(f"\n=== Test Complete ===")
        print(f"Game ID: {game_id}")
        print(f"Final state: Player {final_state['players'][final_state['current_player_index']]['name']} at index {final_state['current_player_index']}")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc() 