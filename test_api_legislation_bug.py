#!/usr/bin/env python3
"""
Test script to reproduce the legislation timing bug via API calls.
"""

import requests
import json
import time

def test_legislation_timing_bug():
    """Test the legislation timing bug via API calls."""
    
    base_url = "http://localhost:5001/api"
    
    print("🧪 Testing Legislation Timing Bug via API")
    print("=" * 50)
    
    # Create a new game
    print("Creating new game...")
    response = requests.post(f"{base_url}/game", json={
        "player_names": ["Alice", "Bob"]
    })
    
    if response.status_code != 200:
        print(f"Failed to create game: {response.status_code}")
        return
    
    game_data = response.json()
    game_id = game_data['game_id']
    print(f"Game created with ID: {game_id}")
    
    # Get initial game state
    response = requests.get(f"{base_url}/game/{game_id}")
    if response.status_code != 200:
        print(f"Failed to get game state: {response.status_code}")
        return
    
    game_state = response.json()['state']
    print(f"Initial phase: {game_state['current_phase']}")
    print(f"Round: {game_state['round_marker']}")
    
    # Alice sponsors legislation
    print("\n--- Alice sponsors Infrastructure Bill ---")
    response = requests.post(f"{base_url}/game/{game_id}/action", json={
        "action_type": "sponsor_legislation",
        "player_id": 0,
        "legislation_id": "INFRASTRUCTURE"
    })
    
    if response.status_code != 200:
        print(f"Failed to sponsor legislation: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    game_state = response.json()['state']
    print(f"Pending legislation: {game_state.get('pending_legislation') is not None}")
    
    # Simulate end of round (upkeep)
    print("\n--- Simulating end of round (upkeep) ---")
    response = requests.post(f"{base_url}/game/{game_id}/action", json={
        "action_type": "pass_turn",
        "player_id": 0
    })
    
    if response.status_code != 200:
        print(f"Failed to pass turn: {response.status_code}")
        return
    
    game_state = response.json()['state']
    print(f"Pending legislation after upkeep: {game_state.get('pending_legislation') is not None}")
    print(f"Term legislation count: {len(game_state.get('term_legislation', []))}")
    
    # Bob tries to oppose the legislation
    print("\n--- Bob opposes the Infrastructure Bill ---")
    response = requests.post(f"{base_url}/game/{game_id}/action", json={
        "action_type": "oppose_legislation",
        "player_id": 1,
        "legislation_id": "INFRASTRUCTURE",
        "oppose_amount": 5
    })
    
    if response.status_code != 200:
        print(f"Failed to oppose legislation: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    game_state = response.json()['state']
    print(f"Bob PC after opposing: {game_state['players'][1]['pc']}")
    
    # Check if the opposition was recorded
    term_legislation = game_state.get('term_legislation', [])
    if term_legislation:
        for leg in term_legislation:
            if leg['legislation_id'] == "INFRASTRUCTURE":
                print(f"Opposition players: {leg['oppose_players']}")
                print(f"Support players: {leg['support_players']}")
    
    print("\n✅ API legislation timing bug test completed!")
    print("=" * 50)

if __name__ == "__main__":
    test_legislation_timing_bug() 