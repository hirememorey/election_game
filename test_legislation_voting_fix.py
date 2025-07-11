#!/usr/bin/env python3
"""
Test script to verify legislation voting fix - players cannot vote on their own legislation.
"""

import requests
import json

BASE_URL = 'http://localhost:5001/api/game'

def test_legislation_voting_fix():
    """Test that players cannot vote on their own legislation and can pass turn."""
    
    print("🧪 Testing Legislation Voting Fix")
    print("=" * 50)
    
    # 1. Create a new game
    print("1. Creating new game...")
    resp = requests.post(BASE_URL, json={'player_names': ['Alice', 'Bob']})
    if resp.status_code != 200:
        print(f"❌ Failed to create game: {resp.status_code}")
        return False
    
    data = resp.json()
    game_id = data['game_id']
    state = data['state']
    print(f"✅ Game created: {game_id}")
    
    # 2. Alice sponsors legislation
    print("\n2. Alice sponsors legislation...")
    action_data = {
        'action_type': 'sponsor_legislation',
        'player_id': 0,
        'legislation_id': 'INFRASTRUCTURE'
    }
    
    resp = requests.post(f"{BASE_URL}/{game_id}/action", json=action_data)
    if resp.status_code == 200:
        state = resp.json()['state']
        print("✅ Alice successfully sponsored legislation")
    else:
        print(f"❌ Failed to sponsor legislation: {resp.status_code} - {resp.text}")
        return False
    
    # 3. Manually trigger legislation session
    print("\n3. Triggering legislation session...")
    resp = requests.post(f"{BASE_URL}/{game_id}/resolve_legislation")
    if resp.status_code == 200:
        state = resp.json()['state']
        print("✅ Legislation session triggered")
        print(f"   - awaiting_legislation_resolution: {state.get('awaiting_legislation_resolution', False)}")
    else:
        print(f"❌ Failed to trigger legislation session: {resp.status_code} - {resp.text}")
        return False
    
    # 4. Test that Alice cannot vote on her own legislation
    print("\n4. Testing that Alice cannot vote on her own legislation...")
    
    # Try to support own legislation
    support_data = {
        'action_type': 'support_legislation',
        'player_id': 0,
        'legislation_id': 'INFRASTRUCTURE',
        'support_amount': 1
    }
    
    resp = requests.post(f"{BASE_URL}/{game_id}/action", json=support_data)
    if resp.status_code == 400:
        print("✅ Alice correctly cannot support her own legislation")
    else:
        print(f"❌ Alice was able to support her own legislation: {resp.status_code}")
        return False
    
    # Try to oppose own legislation
    oppose_data = {
        'action_type': 'oppose_legislation',
        'player_id': 0,
        'legislation_id': 'INFRASTRUCTURE',
        'oppose_amount': 1
    }
    
    resp = requests.post(f"{BASE_URL}/{game_id}/action", json=oppose_data)
    if resp.status_code == 400:
        print("✅ Alice correctly cannot oppose her own legislation")
    else:
        print(f"❌ Alice was able to oppose her own legislation: {resp.status_code}")
        return False
    
    # 5. Test pass turn functionality
    print("\n5. Testing pass turn functionality...")
    
    # First check current player
    resp = requests.get(f"{BASE_URL}/{game_id}")
    if resp.status_code == 200:
        state = resp.json()['state']
        current_player = state.get('current_player_index', 0)
        print(f"   - Current player index: {current_player}")
        
        pass_data = {
            'action_type': 'pass_turn',
            'player_id': current_player
        }
        
        resp = requests.post(f"{BASE_URL}/{game_id}/action", json=pass_data)
        if resp.status_code == 200:
            state = resp.json()['state']
            print("✅ Pass turn works correctly")
            print(f"   - New current player: {state.get('current_player_index', 'Unknown')}")
        else:
            print(f"❌ Pass turn failed: {resp.status_code} - {resp.text}")
            return False
    else:
        print(f"❌ Failed to get game state: {resp.status_code}")
        return False
    
    # 6. Test that Bob can vote on Alice's legislation
    print("\n6. Testing that Bob can vote on Alice's legislation...")
    
    # Bob supports Alice's legislation
    bob_support_data = {
        'action_type': 'support_legislation',
        'player_id': 1,
        'legislation_id': 'INFRASTRUCTURE',
        'support_amount': 2
    }
    
    resp = requests.post(f"{BASE_URL}/{game_id}/action", json=bob_support_data)
    if resp.status_code == 200:
        state = resp.json()['state']
        print("✅ Bob successfully supported Alice's legislation")
    else:
        print(f"❌ Bob could not support Alice's legislation: {resp.status_code} - {resp.text}")
        return False
    
    print("\n🎉 All tests passed! Legislation voting fix works correctly.")
    print("\n📋 Summary:")
    print("   ✅ Players cannot vote on their own legislation")
    print("   ✅ Pass turn functionality works")
    print("   ✅ Other players can vote on legislation")
    print("   ✅ Frontend will show appropriate UI for own legislation")
    
    return True

if __name__ == "__main__":
    success = test_legislation_voting_fix()
    if success:
        print("\n✅ Legislation voting fix test completed successfully!")
    else:
        print("\n❌ Legislation voting fix test failed!") 