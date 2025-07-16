#!/usr/bin/env python3
"""
Test that uses the server but calls the engine directly to isolate the issue.
"""

import requests
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionPassTurn

def test_server_direct_engine():
    print("🔍 Server Direct Engine Test")
    print("=" * 30)
    print()
    
    # 1. Create a new game via server
    print("1. Creating new game via server...")
    response = requests.post('http://localhost:5001/api/game', 
                           json={'player_names': ['Alice', 'Bob']})
    if response.status_code != 200:
        print(f"❌ Failed to create game: {response.text}")
        return False
    
    game_data = response.json()
    game_id = game_data['game_id']
    print(f"✅ Game created with ID: {game_id}")
    print()
    
    # 2. Sponsor a bill via server
    print("2. Sponsoring a bill via server...")
    response = requests.post(f'http://localhost:5001/api/game/{game_id}/action',
                           json={
                               'action_type': 'sponsor_legislation',
                               'player_id': 0,
                               'legislation_id': 'INFRASTRUCTURE'
                           })
    if response.status_code != 200:
        print(f"❌ Failed to sponsor legislation: {response.text}")
        return False
    
    state_data = response.json()['state']
    print(f"✅ Infrastructure bill sponsored!")
    print(f"   Round marker: {state_data['round_marker']}")
    print(f"   Phase: {state_data['current_phase']}")
    print(f"   Term legislation: {len(state_data['term_legislation'])} items")
    print()
    
    # 3. Now use the engine directly to simulate the rest
    print("3. Using engine directly to simulate rounds...")
    
    # Load game data and create engine
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Recreate the state from the server data
    # This is a simplified recreation - in practice you'd need to properly deserialize
    # For now, let's just test the engine logic directly
    
    # Simulate rounds by passing turns
    for round_num in range(1, 5):
        print(f"Round {round_num}:")
        
        # Player 1 passes turn
        action = ActionPassTurn(player_id=1)
        # We can't use the engine directly here because we don't have the state object
        # Let's use the server API instead
        
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
        print(f"     Term legislation: {len(state_data['term_legislation'])} items")
        print(f"     Awaiting legislation: {state_data['awaiting_legislation_resolution']}")
        
        # Check if we're in legislation phase
        if state_data['current_phase'] == 'LEGISLATION_PHASE':
            print(f"     ✅ Legislation phase triggered!")
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
        print(f"     Term legislation: {len(state_data['term_legislation'])} items")
        print(f"     Awaiting legislation: {state_data['awaiting_legislation_resolution']}")
        
        # Check if we're in legislation phase
        if state_data['current_phase'] == 'LEGISLATION_PHASE':
            print(f"     ✅ Legislation phase triggered!")
            return True
        
        print()
    
    # 4. Final state
    print("4. Final state:")
    print(f"   Round marker: {state_data['round_marker']}")
    print(f"   Phase: {state_data['current_phase']}")
    print(f"   Awaiting legislation: {state_data['awaiting_legislation_resolution']}")
    print(f"   Term legislation: {len(state_data['term_legislation'])} items")
    
    if state_data['awaiting_legislation_resolution']:
        print("✅ Legislation resolution was triggered")
        return True
    else:
        print("❌ Legislation resolution was never triggered")
        return False

if __name__ == "__main__":
    try:
        success = test_server_direct_engine()
        if success:
            print("\n✅ Server direct engine test passed!")
        else:
            print("\n❌ Server direct engine test failed!")
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc() 