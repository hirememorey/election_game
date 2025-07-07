#!/usr/bin/env python3
"""
Test Frontend Action Points Implementation
Tests the API endpoints to ensure the Action Points system works correctly
"""

import requests
import json
import time

BASE_URL = "http://localhost:5001/api"

def test_action_points_frontend():
    print("🧪 Testing Frontend Action Points Implementation")
    print("=" * 50)
    
    try:
        # Test 1: Create a new game
        print("\nTest 1: Creating new game...")
        response = requests.post(f"{BASE_URL}/game", json={
            "player_names": ["Alice", "Bob"]
        })
        
        if response.status_code != 200:
            print(f"❌ Failed to create game: {response.status_code}")
            return False
            
        game_data = response.json()
        game_id = game_data["game_id"]
        state = game_data["state"]
        
        print(f"✅ Game created with ID: {game_id}")
        print(f"   Current player: {state['current_player_index']}")
        print(f"   Action points: {state.get('action_points', {})}")
        
        # Test 2: Check initial Action Points
        print("\nTest 2: Checking initial Action Points...")
        current_player_id = state["players"][state["current_player_index"]]["id"]
        initial_ap = state.get("action_points", {}).get(current_player_id, 3)
        
        if initial_ap != 3:
            print(f"❌ Expected 3 AP, got {initial_ap}")
            return False
            
        print(f"✅ Initial AP: {initial_ap}")
        
        # Test 3: Perform a 1 AP action (fundraise)
        print("\nTest 3: Testing 1 AP action (fundraise)...")
        print(f"   Current player ID: {current_player_id}")
        print(f"   Current player index: {state['current_player_index']}")
        print(f"   Action points before: {state.get('action_points', {})}")
        
        response = requests.post(f"{BASE_URL}/game/{game_id}/action", json={
            "action_type": "fundraise",
            "player_id": state["current_player_index"]
        })
        
        if response.status_code != 200:
            print(f"❌ Failed to perform fundraise action: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
        state = response.json()["state"]
        current_player_id = state["players"][state["current_player_index"]]["id"]
        ap_after_fundraise = state.get("action_points", {}).get(current_player_id, 3)
        
        print(f"   Action points after: {state.get('action_points', {})}")
        print(f"   Current player ID after: {current_player_id}")
        print(f"   AP after fundraise: {ap_after_fundraise}")
        
        if ap_after_fundraise != 2:
            print(f"❌ Expected 2 AP after fundraise, got {ap_after_fundraise}")
            return False
            
        print(f"✅ AP after fundraise: {ap_after_fundraise}")
        
        # Test 4: Perform a 2 AP action (sponsor legislation)
        print("\nTest 4: Testing 2 AP action (sponsor legislation)...")
        response = requests.post(f"{BASE_URL}/game/{game_id}/action", json={
            "action_type": "sponsor_legislation",
            "player_id": state["current_player_index"],
            "legislation_id": "TAX_CUT"
        })
        
        if response.status_code != 200:
            print(f"❌ Failed to perform sponsor legislation action: {response.status_code}")
            return False
            
        state = response.json()["state"]
        current_player_id = state["players"][state["current_player_index"]]["id"]
        ap_after_sponsor = state.get("action_points", {}).get(current_player_id, 3)
        
        if ap_after_sponsor != 0:
            print(f"❌ Expected 0 AP after sponsor legislation, got {ap_after_sponsor}")
            return False
            
        print(f"✅ AP after sponsor legislation: {ap_after_sponsor}")
        
        # Test 5: Check turn advancement
        print("\nTest 5: Checking turn advancement...")
        new_player_index = state["current_player_index"]
        if new_player_index != 1:  # Should be Bob's turn now
            print(f"❌ Expected player index 1, got {new_player_index}")
            return False
            
        new_player_id = state["players"][new_player_index]["id"]
        new_player_ap = state.get("action_points", {}).get(new_player_id, 3)
        
        if new_player_ap != 3:
            print(f"❌ Expected 3 AP for new player, got {new_player_ap}")
            return False
            
        print(f"✅ Turn advanced to player {new_player_index} with {new_player_ap} AP")
        
        # Test 6: Test campaign action
        print("\nTest 6: Testing campaign action...")
        response = requests.post(f"{BASE_URL}/game/{game_id}/action", json={
            "action_type": "campaign",
            "player_id": state["current_player_index"],
            "office_id": "GOVERNOR",
            "influence_amount": 5
        })
        
        if response.status_code != 200:
            print(f"❌ Failed to perform campaign action: {response.status_code}")
            return False
            
        state = response.json()["state"]
        current_player_id = state["players"][state["current_player_index"]]["id"]
        ap_after_campaign = state.get("action_points", {}).get(current_player_id, 3)
        campaign_influences = state.get("campaign_influences", [])
        
        if ap_after_campaign != 1:
            print(f"❌ Expected 1 AP after campaign, got {ap_after_campaign}")
            return False
            
        if len(campaign_influences) != 1:
            print(f"❌ Expected 1 campaign influence, got {len(campaign_influences)}")
            return False
            
        print(f"✅ AP after campaign: {ap_after_campaign}")
        print(f"✅ Campaign influences: {len(campaign_influences)}")
        
        # Test 7: Test AP validation (try to perform action with insufficient AP)
        print("\nTest 7: Testing AP validation...")
        response = requests.post(f"{BASE_URL}/game/{game_id}/action", json={
            "action_type": "sponsor_legislation",
            "player_id": state["current_player_index"],
            "legislation_id": "TAX_CUT"
        })
        
        if response.status_code == 200:
            print("❌ Should have failed due to insufficient AP")
            return False
            
        print("✅ Correctly prevented action with insufficient AP")
        
        print("\n🎉 Frontend Action Points tests completed successfully!")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the server is running on port 5001.")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_action_points_frontend()
    exit(0 if success else 1) 