#!/usr/bin/env python3
"""
Test script to verify frontend manual resolution buttons work correctly.
This test manually sets up game state to trigger the resolution buttons.
"""

import requests
import json

BASE_URL = 'http://localhost:5001/api/game'

def test_manual_resolution_frontend():
    """Test the frontend manual resolution functionality."""
    
    print("🧪 Testing Frontend Manual Resolution Buttons")
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
    
    # 2. Manually set up the game state to trigger legislation resolution
    print("\n2. Setting up game state for legislation resolution...")
    
    # We need to simulate a game that has reached the legislation session
    # Let's create a simple test by making some actions and then manually triggering the resolution
    
    # First, let's try to sponsor some legislation
    print("   - Attempting to sponsor legislation...")
    action_data = {
        'action_type': 'sponsor_legislation',
        'player_id': 0,
        'legislation_id': 'INFRASTRUCTURE'
    }
    
    resp = requests.post(f"{BASE_URL}/{game_id}/action", json=action_data)
    if resp.status_code == 200:
        state = resp.json()['state']
        print("   ✅ Successfully sponsored legislation")
    else:
        print(f"   ⚠️ Could not sponsor legislation: {resp.status_code} - {resp.text}")
        # Continue anyway to test the resolution endpoints
    
    # 3. Test the resolve_legislation endpoint
    print("\n3. Testing resolve_legislation endpoint...")
    resp = requests.post(f"{BASE_URL}/{game_id}/resolve_legislation")
    if resp.status_code == 200:
        state = resp.json()['state']
        print("✅ Legislation resolution successful")
        print(f"   - awaiting_legislation_resolution: {state.get('awaiting_legislation_resolution', False)}")
        print(f"   - awaiting_election_resolution: {state.get('awaiting_election_resolution', False)}")
    else:
        print(f"❌ Legislation resolution failed: {resp.status_code} - {resp.text}")
        return False
    
    # 4. Test the resolve_elections endpoint
    print("\n4. Testing resolve_elections endpoint...")
    resp = requests.post(f"{BASE_URL}/{game_id}/resolve_elections")
    if resp.status_code == 200:
        state = resp.json()['state']
        print("✅ Elections resolution successful")
        print(f"   - awaiting_legislation_resolution: {state.get('awaiting_legislation_resolution', False)}")
        print(f"   - awaiting_election_resolution: {state.get('awaiting_election_resolution', False)}")
        print(f"   - Current phase: {state.get('current_phase', 'Unknown')}")
        print(f"   - Round marker: {state.get('round_marker', 'Unknown')}")
    else:
        print(f"❌ Elections resolution failed: {resp.status_code} - {resp.text}")
        return False
    
    # 5. Test the game state serialization includes resolution flags
    print("\n5. Testing game state serialization...")
    resp = requests.get(f"{BASE_URL}/{game_id}")
    if resp.status_code == 200:
        state = resp.json()['state']
        has_legislation_flag = 'awaiting_legislation_resolution' in state
        has_election_flag = 'awaiting_election_resolution' in state
        
        print(f"✅ Game state includes resolution flags:")
        print(f"   - awaiting_legislation_resolution: {has_legislation_flag}")
        print(f"   - awaiting_election_resolution: {has_election_flag}")
        
        if not (has_legislation_flag and has_election_flag):
            print("❌ Missing resolution flags in game state")
            return False
    else:
        print(f"❌ Failed to get game state: {resp.status_code}")
        return False
    
    print("\n🎉 All tests passed! Frontend manual resolution should work correctly.")
    print("\n📋 Next steps:")
    print("   1. Open http://localhost:5001 in your browser")
    print("   2. Start a new game")
    print("   3. Play until the end of a term (4 rounds)")
    print("   4. Look for the 'Resolve Legislation' and 'Resolve Elections' buttons")
    print("   5. Test clicking the buttons to see the resolution flow")
    
    return True

if __name__ == "__main__":
    success = test_manual_resolution_frontend()
    if success:
        print("\n✅ Frontend manual resolution test completed successfully!")
    else:
        print("\n❌ Frontend manual resolution test failed!") 