#!/usr/bin/env python3
"""
Simple test to check legislation session behavior.
"""

import requests
import json

BASE_URL = "http://localhost:5001/api"

def main():
    # Create a new game
    print("Creating new game...")
    game_data = {
        'player_names': ['Alice', 'Bob']
    }
    resp = requests.post(f"{BASE_URL}/game", json=game_data)
    if resp.status_code != 200:
        print(f"Failed to create game: {resp.status_code}")
        return
    
    game_data = resp.json()
    game_id = game_data['game_id']
    state = game_data['state']
    
    print(f"Game ID: {game_id}")
    print(f"Initial phase: {state['current_phase']}")
    
    # Get player IDs and office/legislation IDs
    player_ids = [p['id'] for p in state['players']]
    office_ids = list(state['offices'].keys())
    legislation_ids = list(state['legislation_options'].keys())
    
    # Perform some actions to get to legislation session
    actions = [
        {'action_type': 'sponsor_legislation', 'player_id': player_ids[0], 'legislation_id': legislation_ids[0]},
        {'action_type': 'sponsor_legislation', 'player_id': player_ids[1], 'legislation_id': legislation_ids[1]},
        {'action_type': 'sponsor_legislation', 'player_id': player_ids[0], 'legislation_id': legislation_ids[2]},
        {'action_type': 'sponsor_legislation', 'player_id': player_ids[1], 'legislation_id': legislation_ids[0]},
        {'action_type': 'sponsor_legislation', 'player_id': player_ids[0], 'legislation_id': legislation_ids[1]},
        {'action_type': 'sponsor_legislation', 'player_id': player_ids[1], 'legislation_id': legislation_ids[2]},
        {'action_type': 'declare_candidacy', 'player_id': player_ids[0], 'office_id': office_ids[0], 'committed_pc': 5},
        {'action_type': 'declare_candidacy', 'player_id': player_ids[1], 'office_id': office_ids[1], 'committed_pc': 5},
    ]
    
    for i, action in enumerate(actions):
        print(f"\n--- Action {i+1}: {action['action_type']} ---")
        resp = requests.post(f"{BASE_URL}/game/{game_id}/action", json=action)
        if resp.status_code != 200:
            print(f"Action failed: {resp.status_code} - {resp.text}")
            return
        
        result = resp.json()
        state = result['state']
        print(f"Phase: {state['current_phase']}")
        
        # Print recent log entries
        if 'turn_log' in state and state['turn_log']:
            print("Recent log:")
            for entry in state['turn_log'][-3:]:  # Last 3 entries
                print(f"  {entry}")
    
    # Check if we're in legislation phase
    if state['current_phase'] == 'LEGISLATION_PHASE':
        print("\n--- LEGISLATION PHASE DETECTED ---")
        print("Current state:")
        print(f"  Phase: {state['current_phase']}")
        print(f"  Term legislation count: {len(state.get('term_legislation', []))}")
        
        # Try to resolve legislation
        print("\n--- Resolving Legislation ---")
        resp = requests.post(f"{BASE_URL}/game/{game_id}/resolve_legislation")
        if resp.status_code == 200:
            result = resp.json()
            state = result['state']
            print(f"Legislation resolved. New phase: {state['current_phase']}")
            
            # Print recent log entries
            if 'turn_log' in state and state['turn_log']:
                print("Recent log after resolution:")
                for entry in state['turn_log'][-5:]:  # Last 5 entries
                    print(f"  {entry}")
        else:
            print(f"Failed to resolve legislation: {resp.status_code} - {resp.text}")
    
    print("\nTest complete.")

if __name__ == "__main__":
    main() 