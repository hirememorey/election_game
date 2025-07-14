#!/usr/bin/env python3
"""
Comprehensive test for the new scoring system and Hidden Funder mechanics.
Tests the full game flow including end-game scoring and Hidden Funder objectives.
"""

import requests
import json
import sys
import os
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from models.game_state import GameState
from engine.scoring import calculate_final_scores

BASE_URL = "http://localhost:5001"

def test_scoring_system():
    """Test the new scoring system with PC conversion and Hidden Funder bonuses."""
    print("Testing scoring system...")
    
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Create a test game state
    state = engine.start_new_game(["Alice", "Bob", "Charlie"])
    
    # Simulate some game progress
    # Give Alice the presidency and some PC
    state.players[0].current_office = game_data["offices"]["PRESIDENT"]  # President
    state.players[0].pc = 50
    
    # Give Bob a lower office and some PC
    state.players[1].current_office = game_data["offices"]["US_SENATOR"]  # Senator
    state.players[1].pc = 30
    
    # Give Charlie no office but lots of PC
    state.players[2].pc = 100
    
    # Simulate some legislation history for Hidden Funder objectives
    state.legislation_history = [
        {
            'sponsor_id': 0,  # Alice sponsored
            'outcome': 'Critical Success',
            'support_players': {1: 5},  # Bob supported
            'oppose_players': {}
        }
    ]
    
    # Test the scoring function
    scores = calculate_final_scores(state)
    
    print("Final Scores:")
    for player_id, score_data in scores.items():
        player = state.get_player_by_id(player_id)
        if player:
            print(f"{player.name}: {score_data['total_influence']} Influence")
            for detail in score_data['details']:
                print(f"  - {detail}")
    
    # Verify the scoring logic
    assert scores[0]['total_influence'] > 0, "Alice should have Influence from presidency"
    assert scores[1]['total_influence'] > 0, "Bob should have Influence from office + PC"
    assert scores[2]['total_influence'] > 0, "Charlie should have Influence from PC conversion"
    
    print("✓ Scoring system test passed!")
    return True

def test_hidden_funder_objectives():
    """Test that Hidden Funder objectives are properly evaluated."""
    print("Testing Hidden Funder objectives...")
    
    game_data = load_game_data()
    engine = GameEngine(game_data)
    state = engine.start_new_game(["Alice", "Bob", "Charlie"])
    
    # Test the Defense Contractors Union objective (WAR_HAWK)
    # This requires Military Funding to pass with Critical Success
    state.legislation_history = [
        {
            'sponsor_id': 0,
            'legislation_id': 'MILITARY',
            'outcome': 'Critical Success',
            'support_players': {},
            'oppose_players': {}
        }
    ]
    
    # Give Alice the WAR_HAWK mandate
    state.players[0].mandate = next(m for m in game_data["mandates"] if m.id == "WAR_HAWK")
    
    scores = calculate_final_scores(state)
    
    # Check if Alice got the bonus
    alice_score = scores[0]['total_influence']
    alice_details = scores[0]['details']
    
    # Should have the Hidden Funder bonus
    assert any("Hidden Funder" in detail for detail in alice_details), "Alice should get Hidden Funder bonus"
    
    print("✓ Hidden Funder objectives test passed!")
    return True

def test_full_game_flow():
    """Test the complete game flow including end-game scoring."""
    print("Testing full game flow...")
    
    try:
        # Create a new game
        response = requests.post(
            f"{BASE_URL}/api/game",
            json={"player_names": ["Alice", "Bob", "Charlie"]},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"✗ Failed to create game: {response.status_code}")
            return False
            
        game_data = response.json()
        game_id = game_data["game_id"]
        print(f"✓ Game created: {game_id}")
        
        # Simulate a full game by taking actions until we reach end-game
        actions_taken = 0
        max_actions = 50  # Prevent infinite loops
        
        while actions_taken < max_actions:
            # Get current game state
            response = requests.get(f"{BASE_URL}/api/game/{game_id}")
            if response.status_code != 200:
                print(f"✗ Failed to get game state: {response.status_code}")
                return False
                
            state_data = response.json()
            
            # Check if game is over
            if state_data.get("game_over", False):
                print("✓ Game ended successfully")
                
                # Check for final scores
                if "final_scores" in state_data:
                    print("Final Scores:")
                    for player_id, score_data in state_data["final_scores"].items():
                        print(f"Player {player_id}: {score_data['total_influence']} Influence")
                    print("✓ End-game scoring working!")
                else:
                    print("⚠ No final scores found in game state")
                
                return True
            
            # Take an action for the current player
            current_player = state_data.get("current_player", 0)
            
            # Try different actions
            actions_to_try = [
                {"action_type": "fundraise", "player_id": current_player},
                {"action_type": "network", "player_id": current_player},
                {"action_type": "sponsor_legislation", "player_id": current_player, "legislation_id": "INFRASTRUCTURE"},
                {"action_type": "support_legislation", "player_id": current_player, "legislation_id": "INFRASTRUCTURE", "pc_committed": 3},
                {"action_type": "pass_turn", "player_id": current_player}
            ]
            
            action_taken = False
            for action in actions_to_try:
                try:
                    response = requests.post(
                        f"{BASE_URL}/api/game/{game_id}/action",
                        json=action,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if response.status_code == 200:
                        print(f"✓ Action taken: {action['action_type']}")
                        action_taken = True
                        break
                    elif response.status_code == 400:
                        # Action not valid, try next one
                        continue
                    else:
                        print(f"⚠ Unexpected response: {response.status_code}")
                        break
                        
                except Exception as e:
                    print(f"✗ Action failed: {e}")
                    break
            
            if not action_taken:
                print("⚠ No valid actions found, game might be stuck")
                return False
            
            actions_taken += 1
            time.sleep(0.1)  # Small delay to prevent overwhelming the server
        
        print(f"⚠ Game did not end after {max_actions} actions")
        return False
        
    except Exception as e:
        print(f"✗ Full game flow test failed: {e}")
        return False

def test_ui_end_to_end():
    """Test the UI can handle the full game flow."""
    print("Testing UI end-to-end...")
    
    try:
        # Test that the main page loads
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print(f"✗ Main page failed: {response.status_code}")
            return False
        
        # Test that static files are available
        static_files = ["/static/style.css", "/static/script.js"]
        for file_path in static_files:
            response = requests.get(f"{BASE_URL}{file_path}")
            if response.status_code != 200:
                print(f"✗ Static file failed: {file_path} - {response.status_code}")
                return False
        
        print("✓ UI files accessible")
        return True
        
    except Exception as e:
        print(f"✗ UI test failed: {e}")
        return False

def test_api_endpoints():
    """Test all critical API endpoints."""
    print("Testing API endpoints...")
    
    try:
        # Test game creation
        response = requests.post(
            f"{BASE_URL}/api/game",
            json={"player_names": ["Alice", "Bob"]},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"✗ Game creation failed: {response.status_code}")
            return False
        
        game_data = response.json()
        game_id = game_data["game_id"]
        
        # Test getting game state
        response = requests.get(f"{BASE_URL}/api/game/{game_id}")
        if response.status_code != 200:
            print(f"✗ Game state retrieval failed: {response.status_code}")
            return False
        
        # Test taking an action
        response = requests.post(
            f"{BASE_URL}/api/game/{game_id}/action",
            json={"action_type": "fundraise", "player_id": 0},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"✗ Action failed: {response.status_code}")
            return False
        
        print("✓ API endpoints working")
        return True
        
    except Exception as e:
        print(f"✗ API test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Election Game Comprehensive Test Suite")
    print("=" * 50)
    
    tests = [
        ("Scoring System", test_scoring_system),
        ("Hidden Funder Objectives", test_hidden_funder_objectives),
        ("API Endpoints", test_api_endpoints),
        ("UI End-to-End", test_ui_end_to_end),
        ("Full Game Flow", test_full_game_flow)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        try:
            if test_func():
                print(f"✓ {test_name} PASSED")
                passed += 1
            else:
                print(f"✗ {test_name} FAILED")
        except Exception as e:
            print(f"✗ {test_name} ERROR: {e}")
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The game is ready to play.")
    else:
        print("⚠ Some tests failed. Please check the implementation.")
    
    print(f"\nTo play the game, visit: {BASE_URL}")

if __name__ == "__main__":
    main() 