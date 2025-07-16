#!/usr/bin/env python3
"""
Simple test to verify that resolution controls appear after 4 rounds when legislation is sponsored.
"""

import requests
import json
import time

def test_simple_resolution():
    """Test that resolution controls appear after 4 rounds when legislation is sponsored."""
    
    base_url = "http://localhost:5001/api"
    
    print("🧪 Simple Resolution Controls Test (with legislation)")
    print("=" * 50)
    
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
    
    # Step 2: Sponsor a bill in round 1
    print("\n2. Sponsoring a bill in round 1...")
    
    # Get current state
    response = requests.get(f"{base_url}/game/{game_id}")
    if response.status_code != 200:
        print(f"❌ Failed to get game state: {response.status_code}")
        return False
    
    game_state = response.json()["state"]
    current_player = game_state["current_player_index"]
    
    print(f"   Current player: {current_player}")
    
    # Sponsor a bill (INFRASTRUCTURE costs 5 PC)
    response = requests.post(f"{base_url}/game/{game_id}/action", json={
        "action_type": "sponsor_legislation",
        "player_id": current_player,
        "legislation_id": "INFRASTRUCTURE"
    })
    
    if response.status_code != 200:
        print(f"   ❌ Failed to sponsor legislation: {response.status_code}")
        return False
    
    print("   ✅ Infrastructure bill sponsored!")
    
    # Get updated state
    response = requests.get(f"{base_url}/game/{game_id}")
    game_state = response.json()["state"]
    print(f"   Pending legislation: {game_state.get('pending_legislation') is not None}")
    
    # Step 3: Advance through rounds by making each player pass their turn
    print("\n3. Advancing through rounds...")
    
    for round_num in range(1, 5):
        print(f"   Round {round_num}:")
        
        # Each player passes their turn to advance the round
        for player_id in range(2):
            # Get current game state
            response = requests.get(f"{base_url}/game/{game_id}")
            if response.status_code != 200:
                print(f"   ❌ Failed to get game state: {response.status_code}")
                return False
            
            game_state = response.json()["state"]
            current_player = game_state["current_player_index"]
            
            print(f"     Current player: {current_player}")
            
            # Make the current player pass their turn
            response = requests.post(f"{base_url}/game/{game_id}/action", json={
                "action_type": "pass_turn",
                "player_id": current_player
            })
            
            if response.status_code != 200:
                print(f"   ❌ Failed to pass turn for player {current_player}: {response.status_code}")
                return False
            
            print(f"     Player {current_player} passed turn")
            
            # Get updated game state
            response = requests.get(f"{base_url}/game/{game_id}")
            if response.status_code != 200:
                print(f"   ❌ Failed to get updated game state: {response.status_code}")
                return False
            
            game_state = response.json()["state"]
            print(f"     Round marker: {game_state['round_marker']}")
            print(f"     Current phase: {game_state['current_phase']}")
            print(f"     Awaiting legislation: {game_state.get('awaiting_legislation_resolution', False)}")
            
            # Check if we've reached the legislation phase
            if game_state.get('awaiting_legislation_resolution'):
                print(f"     ✅ LEGISLATION RESOLUTION NEEDED!")
                break
    
    # Step 4: Check final state
    print("\n4. Checking final game state...")
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
        print("   ✅ SUCCESS: Legislation resolution is needed!")
        
        # Step 5: Test legislation resolution
        print("\n5. Testing legislation resolution...")
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
            print("   ✅ SUCCESS: Election resolution is needed!")
            return True
        else:
            print("   ❌ Election resolution flag not set after legislation resolution")
            return False
    else:
        print("   ❌ FAILED: Legislation resolution flag not set")
        return False

if __name__ == "__main__":
    try:
        success = test_simple_resolution()
        if success:
            print("\n✅ Resolution controls test completed successfully!")
        else:
            print("\n❌ Resolution controls test failed!")
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc() 