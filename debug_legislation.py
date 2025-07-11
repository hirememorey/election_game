#!/usr/bin/env python3
"""
Debug script to check legislation IDs in the current game.
"""

import requests
import json

BASE_URL = 'http://localhost:5001/api/game'

def debug_legislation():
    """Debug the legislation IDs in the current game."""
    
    print("🔍 Debugging Legislation IDs")
    print("=" * 50)
    
    # Create a new game
    print("1. Creating new game...")
    resp = requests.post(BASE_URL, json={'player_names': ['Alice', 'Bob', 'Charlie']})
    if resp.status_code != 200:
        print(f"❌ Failed to create game: {resp.status_code}")
        return
    
    data = resp.json()
    game_id = data['game_id']
    state = data['state']
    
    print(f"✅ Game created: {game_id}")
    print(f"Current player: {state.get('current_player_index', 'Unknown')}")
    print(f"Phase: {state.get('current_phase', 'Unknown')}")
    print(f"Legislation session active: {state.get('legislation_session_active', False)}")
    
    # Check legislation options
    print("\n📋 Legislation Options:")
    legislation_options = state.get('legislation_options', {})
    for leg_id, leg_data in legislation_options.items():
        print(f"  {leg_id}: {leg_data.get('title', 'Unknown')}")
    
    # Alice sponsors Healthcare legislation
    print("\n2. Alice sponsors Healthcare legislation...")
    action_data = {
        'action_type': 'sponsor_legislation',
        'player_id': 0,
        'legislation_id': 'HEALTHCARE'
    }
    
    resp = requests.post(f"{BASE_URL}/{game_id}/action", json=action_data)
    if resp.status_code == 200:
        state = resp.json()['state']
        print("✅ Alice successfully sponsored Healthcare legislation")
        
        # Check pending legislation
        print("\n📋 Pending Legislation:")
        pending_legislation = state.get('pending_legislation')
        if pending_legislation:
            print(f"  ID={pending_legislation.get('legislation_id', 'Unknown')}, Sponsor={pending_legislation.get('sponsor_id', 'Unknown')}, Resolved={pending_legislation.get('resolved', False)}")
        else:
            print("  None")
    else:
        print(f"❌ Failed to sponsor legislation: {resp.status_code} - {resp.text}")
        return
    
    # Bob sponsors Military legislation
    print("\n3. Bob sponsors Military legislation...")
    action_data = {
        'action_type': 'sponsor_legislation',
        'player_id': 1,
        'legislation_id': 'MILITARY'
    }
    
    resp = requests.post(f"{BASE_URL}/{game_id}/action", json=action_data)
    if resp.status_code == 200:
        state = resp.json()['state']
        print("✅ Bob successfully sponsored Military legislation")
        
        # Check pending legislation
        print("\n📋 Pending Legislation:")
        pending_legislation = state.get('pending_legislation')
        if pending_legislation:
            print(f"  ID={pending_legislation.get('legislation_id', 'Unknown')}, Sponsor={pending_legislation.get('sponsor_id', 'Unknown')}, Resolved={pending_legislation.get('resolved', False)}")
        else:
            print("  None")
    else:
        print(f"❌ Failed to sponsor legislation: {resp.status_code} - {resp.text}")
        return
    
    # Trigger legislation session
    print("\n4. Triggering legislation session...")
    resp = requests.post(f"{BASE_URL}/{game_id}/resolve_legislation")
    if resp.status_code == 200:
        state = resp.json()['state']
        print("✅ Legislation session triggered")
        
        # Check term legislation
        print("\n📋 Term Legislation:")
        term_legislation = state.get('term_legislation', [])
        for i, leg in enumerate(term_legislation):
            print(f"  {i}: ID={leg.get('legislation_id', 'Unknown')}, Sponsor={leg.get('sponsor_id', 'Unknown')}, Resolved={leg.get('resolved', False)}")
        
        print("\n🎯 Analysis:")
        if term_legislation:
            for leg in term_legislation:
                leg_id = leg.get('legislation_id', 'Unknown')
                if leg_id in legislation_options:
                    title = legislation_options[leg_id].get('title', 'Unknown')
                    print(f"  ✅ {leg_id} -> {title}")
                else:
                    print(f"  ❌ {leg_id} -> NOT FOUND in legislation_options")
        else:
            print("  No term legislation found")
    else:
        print(f"❌ Failed to trigger legislation session: {resp.status_code} - {resp.text}")
        return
    
    # Check players
    print("\n👥 Players:")
    players = state.get('players', [])
    for i, player in enumerate(players):
        print(f"  {i}: {player.get('name', 'Unknown')} (ID: {player.get('id', 'Unknown')})")

if __name__ == "__main__":
    debug_legislation() 