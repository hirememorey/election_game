#!/usr/bin/env python3

import requests
import json
import time

def test_pc_deduction():
    base_url = "http://localhost:5001/api"
    
    # Create a new game
    print("Creating new game...")
    response = requests.post(f"{base_url}/game", json={
        "player_names": ["Alice", "Bob", "Charlie"]
    })
    assert response.status_code == 200
    game_data = response.json()
    game_id = game_data["game_id"]
    print(f"Game created: {game_id}")
    
    # Get initial state
    response = requests.get(f"{base_url}/game/{game_id}")
    assert response.status_code == 200
    state = response.json()["state"]
    
    # Get initial PC for player 1
    initial_pc = state["players"][0]["pc"]
    print(f"Initial PC for player 1: {initial_pc}")
    
    # Sponsor legislation to get some PC
    print("Sponsoring legislation...")
    response = requests.post(f"{base_url}/game/{game_id}/action", json={
        "action_type": "sponsor_legislation",
        "player_id": 0,
        "legislation_id": "MILITARY"
    })
    assert response.status_code == 200
    state = response.json()["state"]
    
    pc_after_sponsor = state["players"][0]["pc"]
    print(f"PC after sponsoring: {pc_after_sponsor}")
    
    # Now commit PC to oppose legislation
    print("Committing PC to oppose legislation...")
    response = requests.post(f"{base_url}/game/{game_id}/action", json={
        "action_type": "oppose_legislation",
        "player_id": 0,
        "legislation_id": "INFRASTRUCTURE",
        "oppose_amount": pc_after_sponsor
    })
    assert response.status_code == 200
    state = response.json()["state"]
    
    pc_after_commit = state["players"][0]["pc"]
    print(f"PC after committing: {pc_after_commit}")
    
    # PC should be 0 after committing all PC
    if pc_after_commit == 0:
        print("✅ SUCCESS: PC was correctly deducted to 0")
    else:
        print(f"❌ FAILURE: PC should be 0, but is {pc_after_commit}")
        return False
    
    return True

def test_pc_deduction_partial():
    base_url = "http://localhost:5001/api"
    
    # Create a new game
    print("\nCreating new game for partial test...")
    response = requests.post(f"{base_url}/game", json={
        "player_names": ["Alice", "Bob", "Charlie"]
    })
    assert response.status_code == 200
    game_data = response.json()
    game_id = game_data["game_id"]
    
    # Get initial state
    response = requests.get(f"{base_url}/game/{game_id}")
    assert response.status_code == 200
    state = response.json()["state"]
    
    # Get initial PC for player 1
    initial_pc = state["players"][0]["pc"]
    print(f"Initial PC for player 1: {initial_pc}")
    
    # Sponsor legislation to get some PC
    print("Sponsoring legislation...")
    response = requests.post(f"{base_url}/game/{game_id}/action", json={
        "action_type": "sponsor_legislation",
        "player_id": 0,
        "legislation_id": "MILITARY"
    })
    assert response.status_code == 200
    state = response.json()["state"]
    
    pc_after_sponsor = state["players"][0]["pc"]
    print(f"PC after sponsoring: {pc_after_sponsor}")
    
    # Commit half of available PC to support legislation
    commit_amount = pc_after_sponsor // 2
    print(f"Committing {commit_amount} PC to support legislation...")
    response = requests.post(f"{base_url}/game/{game_id}/action", json={
        "action_type": "support_legislation",
        "player_id": 0,
        "legislation_id": "INFRASTRUCTURE",
        "support_amount": commit_amount
    })
    assert response.status_code == 200
    state = response.json()["state"]
    
    pc_after_commit = state["players"][0]["pc"]
    print(f"PC after committing: {pc_after_commit}")
    
    expected_pc = pc_after_sponsor - commit_amount
    if pc_after_commit == expected_pc:
        print(f"✅ SUCCESS: PC was correctly reduced from {pc_after_sponsor} to {pc_after_commit}")
    else:
        print(f"❌ FAILURE: PC should be {expected_pc}, but is {pc_after_commit}")
        return False
    
    return True

if __name__ == "__main__":
    print("Testing PC deduction functionality...")
    
    try:
        success1 = test_pc_deduction()
        success2 = test_pc_deduction_partial()
        
        if success1 and success2:
            print("\n🎉 All tests passed!")
        else:
            print("\n💥 Some tests failed!")
            
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc() 