#!/usr/bin/env python3
"""
Detailed debug script for action points issue
"""

import requests
import json

def debug_action_points_detailed():
    """Debug action points initialization and display"""
    
    base_url = "http://localhost:5001/api"
    
    print("🔍 Detailed Action Points Debug")
    print("=" * 50)
    
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
    
    # Detailed analysis of game state
    print("\n2. Analyzing game state...")
    print(f"   - Current phase: {game_state['current_phase']}")
    print(f"   - Current player index: {game_state['current_player_index']}")
    print(f"   - Round marker: {game_state['round_marker']}")
    
    # Check action points
    action_points = game_state.get('action_points', {})
    print(f"   - Action points dict: {action_points}")
    
    # Check players
    players = game_state['players']
    print(f"   - Number of players: {len(players)}")
    
    for i, player in enumerate(players):
        player_id = player['id']
        ap = action_points.get(player_id, 'NOT SET')
        print(f"   - Player {i}: {player['name']} (ID: {player_id}) - AP: {ap}")
    
    # Check current player
    current_player = players[game_state['current_player_index']]
    current_player_id = current_player['id']
    current_ap = action_points.get(current_player_id, 'NOT SET')
    
    print(f"\n3. Current player analysis:")
    print(f"   - Current player: {current_player['name']}")
    print(f"   - Current player ID: {current_player_id}")
    print(f"   - Current player AP: {current_ap}")
    
    # Test API call to get game state
    print("\n4. Testing API call to get game state...")
    try:
        response = requests.get(f"{base_url}/game/{game_id}")
        if response.status_code == 200:
            api_state = response.json()['state']
            api_action_points = api_state.get('action_points', {})
            print(f"   - API action points: {api_action_points}")
            
            # Check if action points are different
            if api_action_points != action_points:
                print("   ⚠️  Action points differ between creation and API call!")
            else:
                print("   ✅ Action points consistent")
        else:
            print(f"   ❌ Failed to get game state: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error getting game state: {e}")
    
    # Test performing an action
    print("\n5. Testing action performance...")
    try:
        response = requests.post(f"{base_url}/game/{game_id}/action", json={
            "action_type": "fundraise",
            "player_id": current_player_id
        })
        
        if response.status_code == 200:
            updated_state = response.json()['state']
            updated_ap = updated_state['action_points'].get(current_player_id, 'NOT SET')
            print(f"   ✅ Action performed successfully")
            print(f"   - AP before action: {current_ap}")
            print(f"   - AP after action: {updated_ap}")
            
            if current_ap != 'NOT SET' and updated_ap != 'NOT SET':
                if updated_ap < current_ap:
                    print("   ✅ Action points correctly deducted")
                else:
                    print("   ❌ Action points not deducted")
            else:
                print("   ⚠️  Cannot compare AP values")
        else:
            print(f"   ❌ Failed to perform action: {response.status_code}")
            error_data = response.json()
            print(f"   - Error: {error_data}")
    except Exception as e:
        print(f"   ❌ Error performing action: {e}")
    
    print("\n🎯 Summary:")
    print("   - Action points should be initialized to 2 for each player")
    print("   - Current player should have 2 AP available")
    print("   - Performing a 1 AP action should leave 1 AP remaining")
    print("   - UI should show '2 AP' not 'undefined AP'")

if __name__ == "__main__":
    debug_action_points_detailed() 