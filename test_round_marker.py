#!/usr/bin/env python3
"""
Test to track round marker progression and see when legislation session is triggered.
"""

import requests
import json

def test_round_marker():
    """Test round marker progression."""
    
    base_url = "http://localhost:5001/api"
    
    print("🧪 Round Marker Test")
    print("=" * 30)
    
    # Step 1: Create a new game
    print("\n1. Creating new game...")
    response = requests.post(f"{base_url}/game", json={
        "player_names": ["Alice", "Bob"]
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to create game: {response.status_code}")
        return False
    
    game_data = response.json()
    game_id = game_data["game_id"]
    print(f"✅ Game created with ID: {game_id}")
    
    # Step 2: Track round progression
    print("\n2. Tracking round progression...")
    
    for round_num in range(1, 6):  # Test 5 rounds
        print(f"\n   Round {round_num}:")
        
        # Get current state
        response = requests.get(f"{base_url}/game/{game_id}")
        if response.status_code != 200:
            print(f"   ❌ Failed to get game state: {response.status_code}")
            return False
        
        game_state = response.json()["state"]
        print(f"     Round marker: {game_state['round_marker']}")
        print(f"     Current phase: {game_state['current_phase']}")
        print(f"     Current player: {game_state['current_player_index']}")
        
        # Make each player pass their turn
        for player_id in range(2):
            current_player = game_state["current_player_index"]
            
            response = requests.post(f"{base_url}/game/{game_id}/action", json={
                "action_type": "pass_turn",
                "player_id": current_player
            })
            
            if response.status_code != 200:
                print(f"   ❌ Failed to pass turn for player {current_player}: {response.status_code}")
                return False
            
            print(f"     Player {current_player} passed turn")
            
            # Get updated state
            response = requests.get(f"{base_url}/game/{game_id}")
            if response.status_code != 200:
                print(f"   ❌ Failed to get updated game state: {response.status_code}")
                return False
            
            game_state = response.json()["state"]
            print(f"     New round marker: {game_state['round_marker']}")
            print(f"     New phase: {game_state['current_phase']}")
            print(f"     Awaiting legislation: {game_state.get('awaiting_legislation_resolution', False)}")
            
            # Check if we've reached legislation phase
            if game_state.get('awaiting_legislation_resolution'):
                print(f"     ✅ LEGISLATION RESOLUTION NEEDED!")
                return True
    
    print("\n❌ Legislation resolution was never triggered")
    return False

if __name__ == "__main__":
    try:
        success = test_round_marker()
        if success:
            print("\n✅ Round marker test completed successfully!")
        else:
            print("\n❌ Round marker test failed!")
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc() 