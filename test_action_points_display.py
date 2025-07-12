#!/usr/bin/env python3
"""
Test script to verify action points display correctly in the simplified UI
"""

import requests
import json

def test_action_points_display():
    """Test that action points display correctly"""
    
    base_url = "http://localhost:5001/api"
    
    print("🧪 Testing Action Points Display")
    print("=" * 40)
    
    # Create a new game
    print("\n1. Creating new game...")
    try:
        response = requests.post(f"{base_url}/game", json={
            "player_names": ["Alice", "Bob"]
        })
        
        if response.status_code == 200:
            game_data = response.json()
            game_id = game_data['game_id']
            game_state = game_data['state']
            print(f"✅ Game created: {game_id}")
        else:
            print(f"❌ Failed to create game: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error creating game: {e}")
        return
    
    # Check initial action points
    print("\n2. Checking initial action points...")
    current_player = game_state['players'][game_state['current_player_index']]
    player_id = current_player['id']
    action_points = game_state['action_points'].get(player_id, 0)
    
    print(f"   - Player: {current_player['name']}")
    print(f"   - Player ID: {player_id}")
    print(f"   - Action Points: {action_points}")
    
    if action_points > 0:
        print("✅ Action points are available")
    else:
        print("❌ No action points available")
    
    # Test performing an action
    print("\n3. Testing action performance...")
    try:
        response = requests.post(f"{base_url}/game/{game_id}/action", json={
            "action_type": "fundraise",
            "player_id": player_id
        })
        
        if response.status_code == 200:
            updated_state = response.json()['state']
            updated_ap = updated_state['action_points'].get(player_id, 0)
            print(f"✅ Action performed successfully")
            print(f"   - Remaining AP: {updated_ap}")
            
            if updated_ap < action_points:
                print("✅ Action points correctly deducted")
            else:
                print("❌ Action points not deducted")
        else:
            print(f"❌ Failed to perform action: {response.status_code}")
    except Exception as e:
        print(f"❌ Error performing action: {e}")
    
    # Test UI state
    print("\n4. Testing UI state...")
    try:
        response = requests.get("http://localhost:5001/")
        if response.status_code == 200:
            print("✅ UI loads successfully")
            
            # Check if the page contains action points display
            if "AP" in response.text:
                print("✅ Action points display found in UI")
            else:
                print("❌ Action points display not found in UI")
        else:
            print(f"❌ UI failed to load: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing UI: {e}")
    
    print("\n🎉 Action points display test completed!")
    print("\n📊 Expected Behavior:")
    print("   - Action points should display as 'X AP'")
    print("   - Available actions should show based on AP")
    print("   - AP should decrease when actions are performed")
    print("   - No 'undefined AP' should appear")

if __name__ == "__main__":
    test_action_points_display() 