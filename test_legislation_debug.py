#!/usr/bin/env python3
"""
Debug test to track legislation state and see why it's not being moved to term_legislation.
"""

import requests
import json
import time

def test_legislation_debug():
    print("🔍 Legislation Debug Test")
    print("=" * 30)
    print()
    
    # 1. Create a new game
    print("1. Creating new game...")
    response = requests.post('http://localhost:5001/api/game', 
                           json={'player_names': ['Alice', 'Bob']})
    if response.status_code != 200:
        print(f"❌ Failed to create game: {response.text}")
        return False
    
    game_data = response.json()
    game_id = game_data['game_id']
    print(f"✅ Game created with ID: {game_id}")
    print()
    
    # 2. Sponsor a bill and track state
    print("2. Sponsoring a bill and tracking state...")
    state = game_data['state']
    print(f"   Initial state:")
    print(f"     Current player: {state['current_player_index']}")
    print(f"     Pending legislation: {state['pending_legislation']}")
    print(f"     Term legislation: {state['term_legislation']}")
    
    # Sponsor infrastructure bill
    response = requests.post(f'http://localhost:5001/api/game/{game_id}/action',
                           json={
                               'action_type': 'sponsor_legislation',
                               'player_id': 0,
                               'legislation_id': 'INFRASTRUCTURE'
                           })
    if response.status_code != 200:
        print(f"❌ Failed to sponsor legislation: {response.text}")
        return False
    
    state = response.json()['state']
    print(f"   ✅ Infrastructure bill sponsored!")
    print(f"   After sponsoring:")
    print(f"     Pending legislation: {state['pending_legislation']}")
    print(f"     Term legislation: {state['term_legislation']}")
    print()
    
    # 3. Advance through rounds and track legislation state
    print("3. Advancing through rounds and tracking legislation state...")
    
    for round_num in range(1, 5):
        print(f"   Round {round_num}:")
        
        # Player 1's turn
        print(f"     Before player 1 turn:")
        print(f"       Pending legislation: {state['pending_legislation']}")
        print(f"       Term legislation: {state['term_legislation']}")
        print(f"       Round marker: {state['round_marker']}")
        print(f"       Current phase: {state['current_phase']}")
        
        # Player 1 takes a pass turn
        response = requests.post(f'http://localhost:5001/api/game/{game_id}/action',
                               json={
                                   'action_type': 'pass_turn',
                                   'player_id': 1
                               })
        if response.status_code != 200:
            print(f"❌ Failed to pass turn: {response.text}")
            return False
        
        state = response.json()['state']
        print(f"     After player 1 turn:")
        print(f"       Pending legislation: {state['pending_legislation']}")
        print(f"       Term legislation: {state['term_legislation']}")
        print(f"       Round marker: {state['round_marker']}")
        print(f"       Current phase: {state['current_phase']}")
        print(f"       Awaiting legislation: {state['awaiting_legislation_resolution']}")
        
        # Player 0's turn
        print(f"     Before player 0 turn:")
        print(f"       Pending legislation: {state['pending_legislation']}")
        print(f"       Term legislation: {state['term_legislation']}")
        print(f"       Round marker: {state['round_marker']}")
        print(f"       Current phase: {state['current_phase']}")
        
        # Player 0 takes a pass turn
        response = requests.post(f'http://localhost:5001/api/game/{game_id}/action',
                               json={
                                   'action_type': 'pass_turn',
                                   'player_id': 0
                               })
        if response.status_code != 200:
            print(f"❌ Failed to pass turn: {response.text}")
            return False
        
        state = response.json()['state']
        print(f"     After player 0 turn:")
        print(f"       Pending legislation: {state['pending_legislation']}")
        print(f"       Term legislation: {state['term_legislation']}")
        print(f"       Round marker: {state['round_marker']}")
        print(f"       Current phase: {state['current_phase']}")
        print(f"       Awaiting legislation: {state['awaiting_legislation_resolution']}")
        
        # Check if we're in legislation phase
        if state['current_phase'] == 'LEGISLATION_PHASE':
            print(f"     ✅ Legislation phase triggered!")
            return True
        
        print()
    
    # 4. Check final state
    print("4. Final state analysis:")
    print(f"   Round marker: {state['round_marker']}")
    print(f"   Current phase: {state['current_phase']}")
    print(f"   Awaiting legislation: {state['awaiting_legislation_resolution']}")
    print(f"   Term legislation: {state['term_legislation']}")
    print(f"   Turn log: {state['turn_log'][-200:] if state['turn_log'] else 'None'}")
    
    if state['awaiting_legislation_resolution']:
        print("✅ Legislation resolution was triggered")
        return True
    else:
        print("❌ Legislation resolution was never triggered")
        return False

if __name__ == "__main__":
    try:
        success = test_legislation_debug()
        if success:
            print("\n✅ Legislation debug test passed!")
        else:
            print("\n❌ Legislation debug test failed!")
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc() 