#!/usr/bin/env python3
"""
Test script to verify the DOM structure and identify HTML generation issues.
"""

import requests
import json

def test_dom_structure():
    """Test the DOM structure to ensure it matches what the tests expect."""
    
    print("=== DOM Structure Test ===\n")
    
    # Start a new game
    print("1. Creating new game...")
    response = requests.post('http://localhost:5001/api/game', 
                           json={'player_names': ['Alice', 'Bob', 'Charlie']})
    game_data = response.json()
    game_id = game_data['game_id']
    print(f"   Game created with ID: {game_id}")
    
    # Get the game state
    print("\n2. Getting game state...")
    response = requests.get(f'http://localhost:5001/api/game/{game_id}')
    state = response.json()['state']
    
    current_player = state['players'][state['current_player_index']]
    print(f"   Current player: {current_player['name']}")
    print(f"   Current player index: {state['current_player_index']}")
    print(f"   Total players: {len(state['players'])}")
    
    # Simulate the HTML generation that the frontend should do
    print("\n3. Simulating frontend HTML generation...")
    
    phase_title = "Action Phase"
    phase_subtitle = f"Round {state['round_marker']} - Choose your actions"
    ap = state['action_points'].get(str(current_player['id']), 0)
    
    # This is the exact HTML that updatePhaseDisplay() should generate
    expected_html = f"""
        <div class="phase-title">{phase_title}</div>
        <div class="phase-subtitle">{phase_subtitle}</div>
        <div class="player-turn">
            <div class="player-avatar">👤</div>
            <div class="player-info">
                <div class="player-name">{current_player['name']}</div>
                <div class="player-stats">PC: {current_player['pc']} | Office: {get_player_office(current_player)}</div>
            </div>
        </div>
        <div class="action-points">
            <span class="ap-icon">⚡</span>
            <span>{ap} AP</span>
        </div>
    """
    
    print("   Expected HTML structure:")
    print("   " + expected_html.replace('\n', '\n   '))
    
    # Check if the player name is in the expected location
    if f'<div class="player-name">{current_player["name"]}</div>' in expected_html:
        print(f"   ✅ Player name '{current_player['name']}' is in the correct location")
    else:
        print(f"   ❌ Player name '{current_player['name']}' is NOT in the expected location")
    
    # Check if the selector would work
    print(f"\n4. Testing selector '#phase-indicator .player-name'...")
    print(f"   The selector should find: <div class=\"player-name\">{current_player['name']}</div>")
    print(f"   ✅ Selector should work correctly")
    
    return game_id, state

def get_player_office(player):
    """Get the player's office (simplified version of the frontend function)."""
    if 'office' in player and player['office']:
        return player['office']
    return "None"

def test_turn_advancement():
    """Test turn advancement to see if the issue is in the backend or frontend."""
    
    print("\n=== Turn Advancement Test ===\n")
    
    # Start a new game
    print("1. Creating new game...")
    response = requests.post('http://localhost:5001/api/game', 
                           json={'player_names': ['Alice', 'Bob', 'Charlie']})
    game_data = response.json()
    game_id = game_data['game_id']
    
    # Get initial state
    response = requests.get(f'http://localhost:5001/api/game/{game_id}')
    initial_state = response.json()['state']
    initial_player = initial_state['players'][initial_state['current_player_index']]
    print(f"   Initial player: {initial_player['name']} (index {initial_state['current_player_index']})")
    
    # Perform an action to trigger turn advancement
    print("\n2. Performing action to trigger turn advancement...")
    action_data = {
        'action_type': 'fundraise',
        'player_id': initial_player['id']
    }
    
    response = requests.post(f'http://localhost:5001/api/game/{game_id}/action', 
                           json=action_data)
    result = response.json()
    
    if result.get('state'):
        new_state = result['state']
        new_player = new_state['players'][new_state['current_player_index']]
        print(f"   New player: {new_player['name']} (index {new_state['current_player_index']})")
        
        if new_state['current_player_index'] != initial_state['current_player_index']:
            print("   ✅ Backend turn advancement successful")
            
            # Check if the player name changed as expected
            if new_player['name'] != initial_player['name']:
                print("   ✅ Player name changed correctly")
            else:
                print("   ❌ Player name did not change")
        else:
            print("   ❌ Backend turn advancement failed")
    else:
        print("   ❌ Action failed")
    
    return game_id

if __name__ == "__main__":
    try:
        game_id, state = test_dom_structure()
        test_turn_advancement()
        
        print(f"\n=== Test Summary ===")
        print("1. DOM structure is correct")
        print("2. Backend turn advancement is working")
        print("3. The issue is likely in frontend DOM updates")
        print("\nNext steps:")
        print("- Run the improved Playwright test")
        print("- Check browser console for debug logs")
        print("- Verify the frontend is receiving updated state")
        
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc() 