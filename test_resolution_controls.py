#!/usr/bin/env python3
"""
Test script to verify that resolution controls appear after 4 rounds
and that legislation and election results are properly shown.
"""

import requests
import json
import time

def test_resolution_controls():
    """Test that resolution controls appear after 4 rounds."""
    
    # Start server URL
    base_url = "http://localhost:5001/api"
    
    print("🧪 Testing Resolution Controls")
    print("=" * 50)
    
    # Step 1: Create a new game
    print("\n1. Creating new game...")
    response = requests.post(f"{base_url}/game", json={
        "player_names": ["Alice", "Bob", "Charlie"]
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to create game: {response.status_code}")
        return False
    
    game_data = response.json()
    game_id = game_data["game_id"]
    print(f"✅ Game created with ID: {game_id}")
    
    # Step 2: Advance through 4 rounds to trigger legislation session
    print("\n2. Advancing through 4 rounds...")
    
    for round_num in range(1, 5):
        print(f"   Round {round_num}:")
        
        # Each player takes actions to advance the round
        for player_id in range(3):
            # Fundraise action to advance turn
            response = requests.post(f"{base_url}/game/{game_id}/action", json={
                "action_type": "fundraise",
                "player_id": player_id
            })
            
            if response.status_code != 200:
                print(f"   ❌ Failed to perform action for player {player_id}: {response.status_code}")
                return False
            
            print(f"     Player {player_id} performed fundraise action")
            
            # Get updated game state
            response = requests.get(f"{base_url}/game/{game_id}")
            if response.status_code != 200:
                print(f"   ❌ Failed to get game state: {response.status_code}")
                return False
            
            game_state = response.json()["state"]
            print(f"     Round marker: {game_state['round_marker']}")
            print(f"     Current phase: {game_state['current_phase']}")
            
            # Check if we've reached the legislation phase
            if game_state.get('awaiting_legislation_resolution'):
                print(f"   ✅ Legislation resolution flag set!")
                break
    
    # Step 3: Check if legislation resolution is needed
    print("\n3. Checking legislation resolution status...")
    response = requests.get(f"{base_url}/game/{game_id}")
    if response.status_code != 200:
        print(f"❌ Failed to get final game state: {response.status_code}")
        return False
    
    game_state = response.json()["state"]
    
    print(f"   Round marker: {game_state['round_marker']}")
    print(f"   Current phase: {game_state['current_phase']}")
    print(f"   Awaiting legislation resolution: {game_state.get('awaiting_legislation_resolution', False)}")
    print(f"   Awaiting election resolution: {game_state.get('awaiting_election_resolution', False)}")
    
    if game_state.get('awaiting_legislation_resolution'):
        print("   ✅ Legislation resolution is needed!")
        
        # Step 4: Test legislation resolution
        print("\n4. Testing legislation resolution...")
        response = requests.post(f"{base_url}/game/{game_id}/resolve_legislation")
        
        if response.status_code != 200:
            print(f"   ❌ Failed to resolve legislation: {response.status_code}")
            return False
        
        print("   ✅ Legislation resolved successfully!")
        
        # Check if election resolution is now needed
        response = requests.get(f"{base_url}/game/{game_id}")
        game_state = response.json()["state"]
        
        print(f"   Awaiting election resolution: {game_state.get('awaiting_election_resolution', False)}")
        
        if game_state.get('awaiting_election_resolution'):
            print("   ✅ Election resolution is needed!")
            
            # Step 5: Test election resolution
            print("\n5. Testing election resolution...")
            response = requests.post(f"{base_url}/game/{game_id}/resolve_elections")
            
            if response.status_code != 200:
                print(f"   ❌ Failed to resolve elections: {response.status_code}")
                return False
            
            print("   ✅ Elections resolved successfully!")
            
            # Check if new term started
            response = requests.get(f"{base_url}/game/{game_id}")
            game_state = response.json()["state"]
            
            print(f"   New round marker: {game_state['round_marker']}")
            print(f"   New current phase: {game_state['current_phase']}")
            
            if game_state['round_marker'] == 1:
                print("   ✅ New term started successfully!")
            else:
                print(f"   ❌ Round marker should be 1, but is {game_state['round_marker']}")
                return False
        else:
            print("   ❌ Election resolution flag not set after legislation resolution")
            return False
    else:
        print("   ❌ Legislation resolution flag not set after 4 rounds")
        return False
    
    print("\n🎉 All tests passed! Resolution controls are working properly.")
    return True

if __name__ == "__main__":
    try:
        success = test_resolution_controls()
        if success:
            print("\n✅ Resolution controls test completed successfully!")
        else:
            print("\n❌ Resolution controls test failed!")
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc() 