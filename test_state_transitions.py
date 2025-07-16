#!/usr/bin/env python3
"""
Test to show exact state transitions and understand the legislation session issue.
"""

import requests
import json

def test_state_transitions():
    print("🔍 State Transitions Test")
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
    
    # 2. Sponsor a bill
    print("2. Sponsoring a bill...")
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
    print(f"✅ Infrastructure bill sponsored!")
    print(f"   Round marker: {state['round_marker']}")
    print(f"   Phase: {state['current_phase']}")
    print(f"   Term legislation: {len(state['term_legislation'])} items")
    print()
    
    # 3. Advance through rounds with detailed state tracking
    print("3. Advancing through rounds...")
    
    for round_num in range(1, 5):
        print(f"Round {round_num}:")
        
        # Player 1's turn
        print(f"   Player 1 turn:")
        response = requests.post(f'http://localhost:5001/api/game/{game_id}/action',
                               json={
                                   'action_type': 'pass_turn',
                                   'player_id': 1
                               })
        if response.status_code != 200:
            print(f"❌ Failed to pass turn: {response.text}")
            return False
        
        state = response.json()['state']
        print(f"     Round marker: {state['round_marker']}")
        print(f"     Phase: {state['current_phase']}")
        print(f"     Term legislation: {len(state['term_legislation'])} items")
        print(f"     Awaiting legislation: {state['awaiting_legislation_resolution']}")
        
        # Check if we're in legislation phase
        if state['current_phase'] == 'LEGISLATION_PHASE':
            print(f"     ✅ Legislation phase triggered!")
            return True
        
        # Player 0's turn
        print(f"   Player 0 turn:")
        response = requests.post(f'http://localhost:5001/api/game/{game_id}/action',
                               json={
                                   'action_type': 'pass_turn',
                                   'player_id': 0
                               })
        if response.status_code != 200:
            print(f"❌ Failed to pass turn: {response.text}")
            return False
        
        state = response.json()['state']
        print(f"     Round marker: {state['round_marker']}")
        print(f"     Phase: {state['current_phase']}")
        print(f"     Term legislation: {len(state['term_legislation'])} items")
        print(f"     Awaiting legislation: {state['awaiting_legislation_resolution']}")
        
        # Check if we're in legislation phase
        if state['current_phase'] == 'LEGISLATION_PHASE':
            print(f"     ✅ Legislation phase triggered!")
            return True
        
        print()
    
    # 4. Final state
    print("4. Final state:")
    print(f"   Round marker: {state['round_marker']}")
    print(f"   Phase: {state['current_phase']}")
    print(f"   Awaiting legislation: {state['awaiting_legislation_resolution']}")
    print(f"   Term legislation: {len(state['term_legislation'])} items")
    
    if state['awaiting_legislation_resolution']:
        print("✅ Legislation resolution was triggered")
        return True
    else:
        print("❌ Legislation resolution was never triggered")
        return False

if __name__ == "__main__":
    try:
        success = test_state_transitions()
        if success:
            print("\n✅ State transitions test passed!")
        else:
            print("\n❌ State transitions test failed!")
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc() 