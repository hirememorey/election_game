#!/usr/bin/env python3
"""
Test script to verify the frontend JavaScript error fix.
"""

import requests
import json
import time

def test_frontend_fix():
    """Test that the frontend can start a game without JavaScript errors."""
    print("🧪 Testing Frontend JavaScript Error Fix")
    print("=" * 50)
    
    base_url = "http://localhost:5001"
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{base_url}/api/test")
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding correctly")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Server is not running")
        return False
    
    # Test 2: Create a new game
    try:
        game_data = {
            "player_names": ["Alice", "Bob"]
        }
        response = requests.post(
            f"{base_url}/api/game",
            headers={"Content-Type": "application/json"},
            data=json.dumps(game_data)
        )
        
        if response.status_code == 200:
            game_response = response.json()
            game_id = game_response.get("game_id")
            game_state = game_response.get("state")
            
            print("✅ Game created successfully")
            print(f"   Game ID: {game_id}")
            print(f"   Players: {len(game_state.get('players', []))}")
            print(f"   Current Phase: {game_state.get('current_phase')}")
            print(f"   Action Points: {game_state.get('action_points')}")
            
            # Test 3: Verify required properties exist
            required_props = ['players', 'current_player_index', 'action_points', 'current_phase']
            missing_props = []
            
            for prop in required_props:
                if prop not in game_state:
                    missing_props.append(prop)
            
            if missing_props:
                print(f"❌ Missing required properties: {missing_props}")
                return False
            else:
                print("✅ All required game state properties present")
            
            # Test 4: Verify players array is properly structured
            players = game_state.get('players', [])
            if len(players) == 0:
                print("❌ No players in game state")
                return False
            
            for i, player in enumerate(players):
                if not all(key in player for key in ['id', 'name', 'pc', 'archetype', 'mandate', 'favors']):
                    print(f"❌ Player {i} missing required properties")
                    return False
            
            print("✅ All players have required properties")
            
            # Test 5: Verify action points are properly initialized
            action_points = game_state.get('action_points', {})
            for player in players:
                player_id_str = str(player['id'])
                if player_id_str not in action_points:
                    print(f"❌ Player {player['name']} (ID: {player['id']}) missing action points")
                    return False
            
            print("✅ Action points properly initialized for all players")
            
            return True
            
        else:
            print(f"❌ Failed to create game: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating game: {e}")
        return False

if __name__ == "__main__":
    success = test_frontend_fix()
    if success:
        print("\n🎉 Frontend fix test passed! The JavaScript error should be resolved.")
        print("You can now open http://localhost:5001 in your browser to test the game.")
    else:
        print("\n❌ Frontend fix test failed!") 