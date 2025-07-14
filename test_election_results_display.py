#!/usr/bin/env python3
"""
Test the election results display functionality.
"""

import requests
import time
import json

BASE_URL = "http://localhost:5001/api"

def print_log(log_entries):
    """Print log entries in a readable format."""
    print("\n--- Game Log ---")
    for entry in log_entries:
        print(entry)
    print("--- End Log ---\n")

def main():
    # 1. Create a new game
    print("Creating new game...")
    game_data = {
        'player_names': ['Alice', 'Bob']
    }
    resp = requests.post(f"{BASE_URL}/game", json=game_data)
    if resp.status_code != 200:
        print(f"Failed to create game: {resp.status_code} - {resp.text}")
        return
    
    game_data = resp.json()
    game_id = game_data['game_id']
    state = game_data['state']
    
    print(f"Game ID: {game_id}")
    print(f"Initial phase: {state['current_phase']}")
    print_log(state['turn_log'])
    
    player_ids = [p['id'] for p in state['players']]
    office_ids = list(state['offices'].keys())
    legislation_ids = list(state['legislation_options'].keys())
    
    # Helper to get the current player id
    def get_current_player_id(state):
        idx = state['current_player_index']
        return state['players'][idx]['id']
    
    # Helper to get a valid action for the current player
    def get_valid_action(state):
        # Always try fundraise, then network, then sponsor_legislation, then declare_candidacy
        player_id = get_current_player_id(state)
        # Try to sponsor legislation if possible
        if state['current_phase'] == 'ACTION_PHASE':
            # If round_marker == 4, try to declare candidacy
            if state['round_marker'] == 4:
                # Find an office not already held
                for office_id in office_ids:
                    already_held = any((p.get('current_office') and p['current_office'].get('id') == office_id) for p in state['players'])
                    if not already_held:
                        return {'action_type': 'declare_candidacy', 'player_id': player_id, 'office_id': office_id, 'committed_pc': 3}
            # Otherwise, try to sponsor legislation
            for leg_id in legislation_ids:
                # Only sponsor if not already in term_legislation
                if not any(l['legislation_id'] == leg_id for l in state.get('term_legislation', [])):
                    return {'action_type': 'sponsor_legislation', 'player_id': player_id, 'legislation_id': leg_id}
            # Otherwise, try fundraise
            return {'action_type': 'fundraise', 'player_id': player_id}
        return None
    
    # Main loop: alternate actions until legislation session
    max_actions = 30
    actions_taken = 0
    while not state.get('awaiting_legislation_resolution', False) and actions_taken < max_actions:
        action = get_valid_action(state)
        if not action:
            print("No valid action found for current player.")
            break
        print(f"\n--- Action {actions_taken+1}: {action['action_type']} (Player {action['player_id']}) ---")
        resp = requests.post(f"{BASE_URL}/game/{game_id}/action", json=action)
        if resp.status_code != 200:
            print(f"Failed to perform action: {resp.status_code} - {resp.text}")
            break
        state = resp.json()['state']
        print(f"Action completed. Current phase: {state['current_phase']}, Round: {state['round_marker']}")
        print_log(state['turn_log'])
        actions_taken += 1
        if state.get('awaiting_legislation_resolution', False):
            print(f"\n✅ REACHED LEGISLATION RESOLUTION POINT!")
            break
    if not state.get('awaiting_legislation_resolution', False):
        print("❌ Failed to reach legislation resolution point")
        return
    # 4. Resolve legislation
    print("\n🔧 Resolving legislation session...")
    resp = requests.post(f"{BASE_URL}/{game_id}/resolve_legislation")
    if resp.status_code != 200:
        print(f"Error resolving legislation: {resp.status_code} - {resp.text}")
        return
    state = resp.json()['state']
    print(f"Legislation resolved. awaiting_election_resolution: {state['awaiting_election_resolution']}")
    print_log(state['turn_log'])
    # 5. Resolve elections
    print("\n🗳️ Resolving elections...")
    resp = requests.post(f"{BASE_URL}/{game_id}/resolve_elections")
    if resp.status_code != 200:
        print(f"Error resolving elections: {resp.status_code} - {resp.text}")
        return
    state = resp.json()['state']
    print(f"Elections resolved. New term started.")
    print_log(state['turn_log'])
    # 6. Test the election results display by checking the game state
    print("\n📊 Testing election results display...")
    resp = requests.get(f"{BASE_URL}/{game_id}")
    if resp.status_code == 200:
        state = resp.json()['state']
        print("✅ Game state retrieved successfully")
        print(f"Current phase: {state['current_phase']}")
        print(f"Turn log entries: {len(state['turn_log'])}")
        election_entries = [entry for entry in state['turn_log'] if 'Election' in entry or 'Score:' in entry]
        if election_entries:
            print("\n📋 Found election-related log entries:")
            for entry in election_entries:
                print(f"  - {entry}")
        else:
            print("\n❌ No election-related log entries found")
    else:
        print(f"❌ Failed to get game state: {resp.status_code}")
    print("\n✅ Election results display test complete!")
    print("\n📋 Next steps:")
    print("   1. Open http://localhost:5001 in your browser")
    print("   2. Start a new game and play until elections")
    print("   3. Look for the enhanced election results display")

if __name__ == "__main__":
    main() 