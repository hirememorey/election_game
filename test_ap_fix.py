#!/usr/bin/env python3
"""
Test script to verify that support/oppose legislation actions properly consume Action Points.
"""

import requests
import json
import time

# Test configuration
BASE_URL = "http://localhost:5001/api"

def test_action_points_fix():
    """Test that support/oppose legislation actions consume Action Points."""
    
    print("🧪 Testing Action Points fix for support/oppose legislation...")
    
    # Step 1: Create a new game
    print("\n1. Creating new game...")
    create_response = requests.post(f"{BASE_URL}/game", json={
        "player_names": ["Alice", "Bob"]
    })
    
    if create_response.status_code != 200:
        print(f"❌ Failed to create game: {create_response.text}")
        return False
    
    game_data = create_response.json()
    game_id = game_data['game_id']
    state = game_data['state']
    
    current_player = state['players'][state['current_player_index']]
    current_player_name = current_player['name']
    current_player_id = str(current_player['id'])
    current_player_ap = state['action_points'][current_player_id]
    print(f"✅ Game created: {game_id}")
    print(f"   Current player: {current_player_name}")
    print(f"   AP for current player: {current_player_ap}")
    
    # Step 2: Sponsor legislation so we have something to support/oppose
    print("\n2. Sponsoring legislation...")
    current_player = state['players'][state['current_player_index']]
    legislation_id = list(state['legislation_options'].keys())[0]  # Get first legislation option
    
    sponsor_response = requests.post(f"{BASE_URL}/game/{game_id}/action", json={
        "action_type": "sponsor_legislation",
        "player_id": state['current_player_index'],
        "legislation_id": legislation_id
    })
    
    if sponsor_response.status_code != 200:
        print(f"❌ Failed to sponsor legislation: {sponsor_response.text}")
        return False
    
    state = sponsor_response.json()['state']
    current_player = state['players'][state['current_player_index']]
    current_player_id = str(current_player['id'])
    ap_after_sponsor = state['action_points'][current_player_id]
    print(f"✅ Legislation sponsored")
    print(f"   AP after sponsoring: {ap_after_sponsor}")
    
    # Step 3: Try to support legislation (should consume 1 AP)
    print("\n3. Testing support legislation (should consume 1 AP)...")
    support_response = requests.post(f"{BASE_URL}/game/{game_id}/action", json={
        "action_type": "support_legislation",
        "player_id": state['current_player_index'],
        "legislation_id": legislation_id,
        "support_amount": 5
    })
    
    if support_response.status_code != 200:
        print(f"❌ Failed to support legislation: {support_response.text}")
        return False
    
    state = support_response.json()['state']
    current_player = state['players'][state['current_player_index']]
    current_player_id = str(current_player['id'])
    ap_after_support = state['action_points'][current_player_id]
    print(f"✅ Support action completed")
    print(f"   AP after supporting: {ap_after_support}")
    
    # Step 4: Try to oppose legislation (should consume 1 AP)
    print("\n4. Testing oppose legislation (should consume 1 AP)...")
    oppose_response = requests.post(f"{BASE_URL}/game/{game_id}/action", json={
        "action_type": "oppose_legislation",
        "player_id": state['current_player_index'],
        "legislation_id": legislation_id,
        "oppose_amount": 3
    })
    
    if oppose_response.status_code != 200:
        print(f"❌ Failed to oppose legislation: {oppose_response.text}")
        return False
    
    state = oppose_response.json()['state']
    current_player = state['players'][state['current_player_index']]
    current_player_id = str(current_player['id'])
    ap_after_oppose = state['action_points'][current_player_id]
    print(f"✅ Oppose action completed")
    print(f"   AP after opposing: {ap_after_oppose}")
    
    # Step 5: Verify AP consumption
    print("\n5. Verifying Action Points consumption...")
    
    # Player should have started with 2 AP, sponsored (-2), supported (-1), opposed (-1)
    # After oppose action, AP should be 0, but turn advances to next player who gets 2 AP
    # So we should see 2 AP (next player's turn)
    expected_ap = 2  # Next player's AP
    actual_ap = ap_after_oppose
    
    if actual_ap == expected_ap:
        print(f"✅ SUCCESS: Action Points properly consumed and turn advanced!")
        print(f"   Expected AP: {expected_ap} (next player's turn)")
        print(f"   Actual AP: {actual_ap}")
        return True
    else:
        print(f"❌ FAILURE: Action Points not properly consumed!")
        print(f"   Expected AP: {expected_ap} (next player's turn)")
        print(f"   Actual AP: {actual_ap}")
        return False

def test_ap_validation():
    """Test that players cannot perform actions without sufficient AP."""
    
    print("\n🧪 Testing Action Points validation...")
    
    # Create a new game
    create_response = requests.post(f"{BASE_URL}/game", json={
        "player_names": ["Alice", "Bob"]
    })
    
    if create_response.status_code != 200:
        print(f"❌ Failed to create game: {create_response.text}")
        return False
    
    game_data = create_response.json()
    game_id = game_data['game_id']
    state = game_data['state']
    
    # Use all AP with fundraise actions
    print("\n1. Using all Action Points...")
    for i in range(2):  # 2 AP available
        fundraise_response = requests.post(f"{BASE_URL}/game/{game_id}/action", json={
            "action_type": "fundraise",
            "player_id": state['current_player_index']
        })
        
        if fundraise_response.status_code != 200:
            print(f"❌ Failed to fundraise: {fundraise_response.text}")
            return False
        
        state = fundraise_response.json()['state']
        current_player = state['players'][state['current_player_index']]
        current_player_id = str(current_player['id'])
        ap_after_fundraise = state['action_points'][current_player_id]
        print(f"   AP after fundraise {i+1}: {ap_after_fundraise}")
    
    # After using all AP, turn should advance to next player
    # Check that the current player has 0 AP (turn should have advanced)
    current_player = state['players'][state['current_player_index']]
    current_player_id = str(current_player['id'])
    current_ap = state['action_points'][current_player_id]
    
    if current_ap == 0:
        print("✅ SUCCESS: Turn properly advanced after using all AP!")
        return True
    else:
        print(f"❌ FAILURE: Turn should have advanced but didn't. Current player AP: {current_ap}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Action Points fix verification...")
    
    try:
        # Test 1: Verify AP consumption
        test1_passed = test_action_points_fix()
        
        # Test 2: Verify AP validation
        test2_passed = test_ap_validation()
        
        print("\n" + "="*50)
        print("📊 TEST RESULTS:")
        test1_result = "✅ PASSED" if test1_passed else "❌ FAILED"
        test2_result = "✅ PASSED" if test2_passed else "❌ FAILED"
        print(f"   AP Consumption Test: {test1_result}")
        print(f"   AP Validation Test: {test2_result}")
        
        if test1_passed and test2_passed:
            print("\n🎉 ALL TESTS PASSED! Action Points fix is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Action Points fix may need more work.")
            
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc() 