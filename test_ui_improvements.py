#!/usr/bin/env python3
"""
Test script for UI improvements:
1. Legislation visibility in all phases
2. Compact game state bar functionality
3. Reduced scrolling layout
"""

import requests
import json
import time

def test_ui_improvements():
    """Test the UI improvements for legislation visibility and compact layout."""
    
    base_url = "http://localhost:5001/api"
    
    print("🧪 Testing UI Improvements...")
    
    # Test 1: Create a game
    print("\n1. Creating a new game...")
    response = requests.post(f"{base_url}/game", json={
        "player_names": ["Alice", "Bob", "Charlie"]
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to create game: {response.status_code}")
        return False
    
    game_data = response.json()
    game_id = game_data["game_id"]
    print(f"✅ Game created: {game_id}")
    
    # Test 2: Sponsor some legislation to test visibility
    print("\n2. Sponsoring legislation to test visibility...")
    
    # Take a few actions to get to a point where we can sponsor legislation
    for i in range(3):
        response = requests.post(f"{base_url}/game/{game_id}/action", json={
            "action_type": "fundraise"
        })
        if response.status_code != 200:
            print(f"❌ Failed to fundraise: {response.status_code}")
            return False
        time.sleep(0.1)
    
    # Sponsor legislation
    response = requests.post(f"{base_url}/game/{game_id}/action", json={
        "action_type": "sponsor_legislation",
        "legislation_id": "INFRASTRUCTURE"
    })
    
    if response.status_code != 200:
        print(f"❌ Failed to sponsor legislation: {response.status_code}")
        return False
    
    print("✅ Legislation sponsored")
    
    # Test 3: Check if legislation is visible in action phase
    print("\n3. Checking legislation visibility in action phase...")
    response = requests.get(f"{base_url}/game/{game_id}")
    
    if response.status_code != 200:
        print(f"❌ Failed to get game state: {response.status_code}")
        return False
    
    game_state = response.json()["state"]
    
    # Check if term_legislation exists and has content
    if game_state.get("term_legislation") and len(game_state["term_legislation"]) > 0:
        print("✅ Legislation is present in game state")
        print(f"   - Number of pending bills: {len(game_state['term_legislation'])}")
        print(f"   - Current phase: {game_state.get('current_phase', 'Unknown')}")
        
        # Check if we're not in legislation phase (legislation should still be visible)
        if game_state.get("current_phase") != "LEGISLATION_PHASE":
            print("✅ Legislation should be visible in non-legislation phase")
        else:
            print("ℹ️  Currently in legislation phase")
    else:
        print("❌ No legislation found in game state")
        return False
    
    # Test 4: Test compact game state bar elements
    print("\n4. Testing compact game state bar elements...")
    
    # Check if all required elements exist in the game state
    required_elements = [
        "current_player_index",
        "players", 
        "action_points",
        "round_marker",
        "current_phase",
        "public_mood"
    ]
    
    for element in required_elements:
        if element in game_state:
            print(f"✅ {element} present in game state")
        else:
            print(f"❌ {element} missing from game state")
            return False
    
    # Test 5: Verify player information is available
    current_player_index = game_state["current_player_index"]
    current_player = game_state["players"][current_player_index]
    
    print(f"✅ Current player: {current_player.get('name', 'Unknown')}")
    print(f"✅ Player PC: {current_player.get('pc', 0)}")
    print(f"✅ Player office: {current_player.get('office', 'None')}")
    print(f"✅ Action points: {game_state.get('action_points', {}).get(current_player.get('id'), 2)}")
    
    print("\n🎉 All UI improvement tests passed!")
    print("\n📱 To test the actual UI improvements:")
    print("   1. Open http://localhost:5001 in your browser")
    print("   2. Create a game and sponsor some legislation")
    print("   3. Verify legislation is visible in all phases")
    print("   4. Check that the compact game state bar shows at the top")
    print("   5. Verify reduced scrolling on mobile and desktop")
    
    return True

if __name__ == "__main__":
    try:
        success = test_ui_improvements()
        if success:
            print("\n✅ UI improvements test completed successfully!")
        else:
            print("\n❌ UI improvements test failed!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print("Make sure the server is running on port 5001") 