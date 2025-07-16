#!/usr/bin/env python3
"""
Simple test to verify the server is working and test the legislation session fix.
"""

import requests
import json
import time

def test_simple_server():
    print("🔍 Simple Server Test")
    print("=" * 30)
    print()
    
    # Test if server is running
    try:
        response = requests.get('http://localhost:5001/api/test')
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding correctly")
            return False
    except Exception as e:
        print(f"❌ Server is not running: {e}")
        return False
    
    # Create a game
    try:
        response = requests.post('http://localhost:5001/api/game', 
                               json={'player_names': ['Alice', 'Bob']})
        if response.status_code != 200:
            print(f"❌ Failed to create game: {response.text}")
            return False
        
        game_data = response.json()
        game_id = game_data['game_id']
        print(f"✅ Game created with ID: {game_id}")
        
        # Sponsor a bill
        response = requests.post(f'http://localhost:5001/api/game/{game_id}/action',
                               json={
                                   'action_type': 'sponsor_legislation',
                                   'player_id': 0,
                                   'legislation_id': 'INFRASTRUCTURE'
                               })
        if response.status_code != 200:
            print(f"❌ Failed to sponsor legislation: {response.text}")
            return False
        
        print("✅ Infrastructure bill sponsored!")
        
        # Pass turns to trigger legislation session
        for round_num in range(1, 5):
            print(f"\nRound {round_num}:")
            
            # Player 1 passes turn
            response = requests.post(f'http://localhost:5001/api/game/{game_id}/action',
                                   json={
                                       'action_type': 'pass_turn',
                                       'player_id': 1
                                   })
            if response.status_code != 200:
                print(f"❌ Failed to pass turn: {response.text}")
                return False
            
            state_data = response.json()['state']
            print(f"   After player 1 turn:")
            print(f"     Round marker: {state_data['round_marker']}")
            print(f"     Phase: {state_data['current_phase']}")
            print(f"     Awaiting legislation: {state_data['awaiting_legislation_resolution']}")
            
            if state_data['current_phase'] == 'LEGISLATION_PHASE':
                print("     ✅ Legislation phase triggered!")
                return True
            
            # Player 0 passes turn
            response = requests.post(f'http://localhost:5001/api/game/{game_id}/action',
                                   json={
                                       'action_type': 'pass_turn',
                                       'player_id': 0
                                   })
            if response.status_code != 200:
                print(f"❌ Failed to pass turn: {response.text}")
                return False
            
            state_data = response.json()['state']
            print(f"   After player 0 turn:")
            print(f"     Round marker: {state_data['round_marker']}")
            print(f"     Phase: {state_data['current_phase']}")
            print(f"     Awaiting legislation: {state_data['awaiting_legislation_resolution']}")
            
            if state_data['current_phase'] == 'LEGISLATION_PHASE':
                print("     ✅ Legislation phase triggered!")
                return True
        
        print(f"\nFinal state:")
        print(f"   Round marker: {state_data['round_marker']}")
        print(f"   Phase: {state_data['current_phase']}")
        print(f"   Awaiting legislation: {state_data['awaiting_legislation_resolution']}")
        
        if state_data['awaiting_legislation_resolution']:
            print("✅ Legislation resolution was triggered")
            return True
        else:
            print("❌ Legislation resolution was never triggered")
            return False
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_server()
    if success:
        print("\n✅ Simple server test passed!")
    else:
        print("\n❌ Simple server test failed!") 