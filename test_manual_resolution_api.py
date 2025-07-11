import requests
import time

BASE_URL = 'http://localhost:5001/api/game'

# Utility to pretty print logs
def print_log(log):
    print("\n--- Game Log ---")
    for entry in log:
        print(entry)
    print("--- End Log ---\n")

def main():
    # 1. Create a new game
    print("Creating new game...")
    resp = requests.post(BASE_URL, json={'player_names': ['Alice', 'Bob']})
    data = resp.json()
    game_id = data['game_id']
    state = data['state']
    print(f"Game ID: {game_id}")
    print(f"Initial phase: {state['current_phase']}")
    print_log(state['turn_log'])

    # 2. Simulate gameplay to reach end of term
    print("\nSimulating gameplay to reach end of term...")
    round_count = 0
    max_rounds = 50  # Safety limit
    
    while not state.get('awaiting_legislation_resolution', False) and round_count < max_rounds:
        round_count += 1
        print(f"\n--- Round {round_count} ---")
        
        # Get current player
        current_player = state['players'][state['current_player_index']]
        player_id = current_player['id']
        player_name = current_player['name']
        
        print(f"Current player: {player_name} (ID: {player_id})")
        print(f"Phase: {state['current_phase']}, Round: {state['round_marker']}")
        print(f"AP: {state['action_points'].get(player_id, 0)}")
        
        # Choose action based on phase and available AP
        action_type = None
        action_data = {'player_id': player_id}
        
        if state['current_phase'] == 'ACTION_PHASE':
            ap = state['action_points'].get(player_id, 0)
            if ap >= 2:
                # Sponsor legislation to create something to resolve
                action_type = 'sponsor_legislation'
                action_data['legislation_id'] = 'INFRASTRUCTURE'
            elif ap >= 1:
                # Fundraise to get more PC
                action_type = 'fundraise'
            else:
                # No AP left, skip this player (turn will advance automatically)
                print(f"No AP left for {player_name}, skipping...")
                # Just get the current state to see if it advanced
                resp = requests.get(f"{BASE_URL}/{game_id}")
                state = resp.json()['state']
                continue
        elif state['current_phase'] == 'LEGISLATION_PHASE':
            # During legislation session, just get current state
            print("In legislation phase, checking state...")
            resp = requests.get(f"{BASE_URL}/{game_id}")
            state = resp.json()['state']
            continue
        else:
            # For other phases, just get current state
            print(f"In {state['current_phase']} phase, checking state...")
            resp = requests.get(f"{BASE_URL}/{game_id}")
            state = resp.json()['state']
            continue
        
        print(f"Taking action: {action_type}")
        
        # Make the API call
        resp = requests.post(f"{BASE_URL}/{game_id}/action", json=action_data)
        if resp.status_code != 200:
            print(f"Error: {resp.status_code} - {resp.text}")
            # Try to get current state to see what happened
            resp = requests.get(f"{BASE_URL}/{game_id}")
            state = resp.json()['state']
            continue
            
        state = resp.json()['state']
        
        # Check if we've reached the legislation resolution point
        if state.get('awaiting_legislation_resolution', False):
            print(f"\n✅ REACHED LEGISLATION RESOLUTION POINT!")
            print_log(state['turn_log'])
            break
            
        time.sleep(0.1)  # Small delay to avoid overwhelming the server
    
    if round_count >= max_rounds:
        print("❌ Test failed: Reached maximum rounds without reaching legislation resolution")
        print(f"Final state - awaiting_legislation_resolution: {state.get('awaiting_legislation_resolution', False)}")
        print(f"Final state - awaiting_election_resolution: {state.get('awaiting_election_resolution', False)}")
        return

    # 3. Call resolve_legislation
    print("\n🔧 Resolving legislation session via API...")
    resp = requests.post(f"{BASE_URL}/{game_id}/resolve_legislation")
    if resp.status_code != 200:
        print(f"Error resolving legislation: {resp.status_code} - {resp.text}")
        return
        
    state = resp.json()['state']
    print(f"awaiting_legislation_resolution: {state['awaiting_legislation_resolution']}")
    print(f"awaiting_election_resolution: {state['awaiting_election_resolution']}")
    print_log(state['turn_log'])

    # 4. Call resolve_elections
    print("\n🗳️ Resolving elections session via API...")
    resp = requests.post(f"{BASE_URL}/{game_id}/resolve_elections")
    if resp.status_code != 200:
        print(f"Error resolving elections: {resp.status_code} - {resp.text}")
        return
        
    state = resp.json()['state']
    print(f"awaiting_legislation_resolution: {state['awaiting_legislation_resolution']}")
    print(f"awaiting_election_resolution: {state['awaiting_election_resolution']}")
    print_log(state['turn_log'])

    print("\n✅ Test complete! Manual resolution flow works correctly!")

if __name__ == "__main__":
    main() 