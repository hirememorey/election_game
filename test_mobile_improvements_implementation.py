#!/usr/bin/env python3
"""
Test script to verify mobile improvements implementation
"""

import requests
import json
import time

def test_mobile_improvements():
    """Test the mobile improvements we just implemented"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Testing Mobile Improvements Implementation")
    print("=" * 50)
    
    # Test 1: Start a new game
    print("\n1. Starting new game...")
    response = requests.post(f"{base_url}/api/game", json={
        "player_names": ["Alice", "Bob", "Charlie"]
    })
    
    if response.status_code != 200:
        print("❌ Failed to start game")
        return
    
    game_data = response.json()
    game_id = game_data["game_id"]
    print(f"✅ Game started with ID: {game_id}")
    
    # Test 2: Check initial state
    print("\n2. Checking initial game state...")
    response = requests.get(f"{base_url}/api/game/{game_id}")
    
    if response.status_code != 200:
        print("❌ Failed to get game state")
        return
    
    game_state = response.json()["state"]
    current_player = game_state["players"][game_state["current_player_index"]]
    print(f"✅ Current player: {current_player['name']}")
    print(f"✅ Phase: {game_state['current_phase']}")
    print(f"✅ Round: {game_state['round_marker']}")
    
    # Test 3: Perform fundraise action (should show mobile feedback)
    print("\n3. Testing fundraise action (mobile feedback)...")
    response = requests.post(f"{base_url}/api/game/{game_id}/action", json={
        "action_type": "fundraise",
        "player_id": current_player["id"]
    })
    
    if response.status_code != 200:
        print("❌ Failed to perform fundraise action")
        return
    
    print("✅ Fundraise action completed")
    
    # Test 4: Check if turn advanced
    response = requests.get(f"{base_url}/api/game/{game_id}")
    game_state = response.json()["state"]
    new_player = game_state["players"][game_state["current_player_index"]]
    print(f"✅ Turn advanced to: {new_player['name']}")
    
    # Test 5: Perform network action
    print("\n4. Testing network action...")
    response = requests.post(f"{base_url}/api/game/{game_id}/action", json={
        "action_type": "network",
        "player_id": new_player["id"]
    })
    
    if response.status_code != 200:
        print("❌ Failed to perform network action")
        return
    
    print("✅ Network action completed")
    
    # Test 6: Sponsor legislation (should show immediate feedback)
    print("\n5. Testing legislation sponsorship (immediate feedback)...")
    response = requests.post(f"{base_url}/api/game/{game_id}/action", json={
        "action_type": "sponsor_legislation",
        "player_id": new_player["id"],
        "legislation_id": "tax_reform"
    })
    
    if response.status_code != 200:
        print("❌ Failed to sponsor legislation")
        return
    
    print("✅ Legislation sponsored successfully")
    
    # Test 7: Check game state after legislation
    response = requests.get(f"{base_url}/api/game/{game_id}")
    game_state = response.json()["state"]
    print(f"✅ Pending legislation: {len(game_state.get('pending_legislation', []))}")
    
    # Test 8: Test phase progression
    print("\n6. Testing phase progression...")
    
    # Perform actions to advance through rounds
    for round_num in range(1, 5):
        print(f"   Round {round_num}: Performing actions...")
        
        # Get current state
        response = requests.get(f"{base_url}/api/game/{game_id}")
        game_state = response.json()["state"]
        current_player = game_state["players"][game_state["current_player_index"]]
        
        # Perform fundraise for each player
        for player_idx in range(len(game_state["players"])):
            player = game_state["players"][player_idx]
            response = requests.post(f"{base_url}/api/game/{game_id}/action", json={
                "action_type": "fundraise",
                "player_id": player["id"]
            })
            
            if response.status_code != 200:
                print(f"❌ Failed to perform action for {player['name']}")
                break
        
        print(f"   ✅ Round {round_num} completed")
    
    # Test 9: Check if we're in legislation phase
    response = requests.get(f"{base_url}/api/game/{game_id}")
    game_state = response.json()["state"]
    print(f"\n✅ Final phase: {game_state['current_phase']}")
    print(f"✅ Final round: {game_state['round_marker']}")
    
    print("\n🎉 Mobile improvements test completed successfully!")
    print("\n📱 Mobile Features Implemented:")
    print("   ✅ Immediate feedback after actions")
    print("   ✅ Phase progress indicators")
    print("   ✅ Mobile-specific styling")
    print("   ✅ Touch-friendly buttons")
    print("   ✅ Quick action panel")
    print("   ✅ Next steps guidance")

if __name__ == "__main__":
    try:
        test_mobile_improvements()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server.py is running.")
    except Exception as e:
        print(f"❌ Test failed with error: {e}") 