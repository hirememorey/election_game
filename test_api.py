#!/usr/bin/env python3
"""
Simple test script to verify the Election game API endpoints are working correctly.
Run this after starting the server with: PORT=5001 python3 server.py
"""

import requests
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionUseFavor
from models.components import PoliticalFavor

BASE_URL = "http://localhost:5001"

def test_static_files():
    """Test that static files are being served correctly."""
    print("Testing static files...")
    
    files_to_test = [
        "/static/style.css",
        "/static/script.js",
        "/static/index.html"
    ]
    
    for file_path in files_to_test:
        try:
            response = requests.get(f"{BASE_URL}{file_path}")
            if response.status_code == 200:
                print(f"✓ {file_path} - OK")
            else:
                print(f"✗ {file_path} - Failed (Status: {response.status_code})")
        except Exception as e:
            print(f"✗ {file_path} - Error: {e}")

def test_api_endpoints():
    """Test the API endpoints."""
    print("\nTesting API endpoints...")
    
    # Test creating a game
    print("Creating a new game...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/game",
            json={"player_names": ["Alice", "Bob", "Charlie"]},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            game_data = response.json()
            game_id = game_data["game_id"]
            print(f"✓ Game created successfully (ID: {game_id})")
            
            # Test getting game state
            print("Getting game state...")
            response = requests.get(f"{BASE_URL}/api/game/{game_id}")
            if response.status_code == 200:
                print("✓ Game state retrieved successfully")
                
                # Test performing an action
                print("Testing action (fundraise)...")
                response = requests.post(
                    f"{BASE_URL}/api/game/{game_id}/action",
                    json={
                        "action_type": "fundraise",
                        "player_id": 0
                    },
                    headers={"Content-Type": "application/json"}
                )
                if response.status_code == 200:
                    print("✓ Action performed successfully")
                else:
                    print(f"✗ Action failed (Status: {response.status_code})")
                    print(f"Response: {response.text}")
            else:
                print(f"✗ Failed to get game state (Status: {response.status_code})")
        else:
            print(f"✗ Failed to create game (Status: {response.status_code})")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"✗ API test failed: {e}")

def test_main_page():
    """Test that the main page loads correctly."""
    print("\nTesting main page...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            if "Election: The Game" in response.text:
                print("✓ Main page loads correctly")
            else:
                print("✗ Main page content seems incorrect")
        else:
            print(f"✗ Main page failed (Status: {response.status_code})")
    except Exception as e:
        print(f"✗ Main page test failed: {e}")

def test_peek_event_favor():
    print("🧪 Testing PEEK_EVENT favor...")
    game_data = load_game_data()
    engine = GameEngine(game_data)
    state = engine.start_new_game(["Benjamin", "Tara"])
    # Give Benjamin the PEEK_EVENT favor
    favor = PoliticalFavor(id="PEEK_EVENT", description="Look at the top card of the Event Deck.")
    state.players[0].favors.append(favor)
    # Use the favor
    action = ActionUseFavor(player_id=0, favor_id="PEEK_EVENT")
    state = engine.process_action(state, action)
    # Print the last log entries
    print("Game Log:")
    for entry in state.turn_log:
        print(entry)
    # Check that the log contains the peeked event card
    assert any("Peeked at the top Event Card" in entry for entry in state.turn_log), "PEEK_EVENT did not log the top event card!"
    print("✅ PEEK_EVENT favor test passed!")

def main():
    print("Election Game API Test")
    print("=" * 50)
    
    # Test static files
    test_static_files()
    
    # Test main page
    test_main_page()
    
    # Test API endpoints
    test_api_endpoints()
    
    # Test PEEK_EVENT favor
    test_peek_event_favor()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nTo play the game:")
    print(f"1. Open your browser to: {BASE_URL}")
    print("2. Enter player names and click 'Start Game'")
    print("3. Use the action buttons to play the game")

if __name__ == "__main__":
    main() 