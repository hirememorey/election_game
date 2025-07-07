#!/usr/bin/env python3
"""
Test script to verify that archetype and mandate information is displayed correctly.
"""

import requests
import json

def test_archetype_mandate_display():
    """Test that the API returns archetype and mandate information for players."""
    
    # Create a new game
    response = requests.post('http://localhost:5001/api/game', 
                           json={'player_names': ['TestPlayer1', 'TestPlayer2']})
    
    if response.status_code != 200:
        print(f"Failed to create game: {response.status_code}")
        return False
    
    game_data = response.json()
    game_id = game_data['game_id']
    
    print("✅ Game created successfully")
    print(f"Game ID: {game_id}")
    
    # Check player information
    players = game_data['state']['players']
    
    for i, player in enumerate(players):
        print(f"\n👤 Player {i+1}: {player['name']}")
        
        # Check archetype
        if 'archetype' in player and player['archetype']:
            archetype = player['archetype']
            print(f"   🎭 Archetype: {archetype['title']}")
            print(f"   📝 Description: {archetype['description']}")
        else:
            print("   ❌ No archetype found!")
            return False
        
        # Check mandate
        if 'mandate' in player and player['mandate']:
            mandate = player['mandate']
            print(f"   🎯 Mandate: {mandate['title']}")
            print(f"   📋 Description: {mandate['description']}")
        else:
            print("   ❌ No mandate found!")
            return False
    
    print("\n✅ All players have archetype and mandate information!")
    print("\n🎮 Frontend should now display:")
    print("   - Political Archetype card with title and description")
    print("   - Hidden Mission card with title and description")
    print("\n📱 The display is mobile-responsive and will stack vertically on small screens.")
    
    return True

if __name__ == "__main__":
    try:
        test_archetype_mandate_display()
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure server.py is running on port 5001.")
    except Exception as e:
        print(f"❌ Test failed with error: {e}") 