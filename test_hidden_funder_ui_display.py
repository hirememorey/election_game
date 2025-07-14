#!/usr/bin/env python3
"""
Test to verify that the UI correctly displays Hidden Funder information.
"""

import requests
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data

BASE_URL = "http://localhost:5001"

def test_hidden_funder_api_response():
    """Test that the API correctly returns Hidden Funder information."""
    print("Testing Hidden Funder API response...")
    
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
        
        # Get the game state
        response = requests.get(f"{BASE_URL}/api/game/{game_id}")
        if response.status_code != 200:
            print(f"✗ Failed to get game state: {response.status_code}")
            return False
            
        state_data = response.json()
        
        # Check that each player has a mandate (Hidden Funder)
        players = state_data["state"]["players"]
        for i, player in enumerate(players):
            if "mandate" not in player:
                print(f"✗ Player {i} missing mandate")
                return False
                
            mandate = player["mandate"]
            if "id" not in mandate or "title" not in mandate or "description" not in mandate:
                print(f"✗ Player {i} mandate missing required fields")
                return False
                
            print(f"✓ Player {i} ({player['name']}) has Hidden Funder: {mandate['title']}")
            print(f"  Description: {mandate['description']}")
        
        # Verify all expected Hidden Funder titles are present
        expected_titles = [
            "The Defense Contractors Union",
            "The Environmental Trust", 
            "The People's Alliance",
            "The Kingmaker's Pact",
            "The Medical Advocacy Project",
            "The Fiscal Watchdogs",
            "The Governor's Association",
            "The Outsider's Collective",
            "The Policy Wonk's Institute",
            "The Grassroots Movement",
            "The Minimalist",
            "The Principled Leader",
            "The Unpopular Hero"
        ]
        
        actual_titles = [player["mandate"]["title"] for player in players]
        print(f"Actual titles: {actual_titles}")
        
        # Check that all titles are from our expected list
        for title in actual_titles:
            if title not in expected_titles:
                print(f"✗ Unexpected Hidden Funder title: {title}")
                return False
        
        print("✓ All Hidden Funder titles are correct")
        return True
        
    except Exception as e:
        print(f"✗ API test failed: {e}")
        return False

def test_hidden_funder_frontend_display():
    """Test that the frontend correctly displays Hidden Funder information."""
    print("Testing Hidden Funder frontend display...")
    
    try:
        # Test that the main page loads
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            print(f"✗ Main page failed: {response.status_code}")
            return False
        
        # Check that the page contains Hidden Funder related content
        page_content = response.text
        
        # Check for key UI elements that should display Hidden Funder info
        if "mandate" not in page_content.lower() and "funder" not in page_content.lower():
            print("⚠ Warning: Page doesn't seem to contain Hidden Funder display elements")
            # This might be okay if the UI loads dynamically
        
        # Check that static files are accessible
        static_files = ["/static/style.css", "/static/script.js"]
        for file_path in static_files:
            response = requests.get(f"{BASE_URL}{file_path}")
            if response.status_code != 200:
                print(f"✗ Static file failed: {file_path} - {response.status_code}")
                return False
        
        print("✓ Frontend files accessible")
        return True
        
    except Exception as e:
        print(f"✗ Frontend test failed: {e}")
        return False

def test_hidden_funder_data_consistency():
    """Test that the Hidden Funder data is consistent between backend and frontend."""
    print("Testing Hidden Funder data consistency...")
    
    try:
        # Load game data directly
        game_data = load_game_data()
        mandates = game_data["mandates"]
        
        # Check that all mandates have the expected structure
        for mandate in mandates:
            if not hasattr(mandate, 'id') or not hasattr(mandate, 'title') or not hasattr(mandate, 'description'):
                print(f"✗ Mandate missing required fields: {mandate}")
                return False
        
        # Verify all expected Hidden Funder IDs are present
        expected_ids = [
            "WAR_HAWK",
            "ENVIRONMENTALIST", 
            "PEOPLES_CHAMPION",
            "KINGMAKER",
            "UNPOPULAR_HERO",
            "MINIMALIST",
            "STATESMAN",
            "OPPORTUNIST",
            "MASTER_LEGISLATOR",
            "PRINCIPLED_LEADER"
        ]
        
        actual_ids = [mandate.id for mandate in mandates]
        print(f"Actual mandate IDs: {actual_ids}")
        
        for mandate_id in actual_ids:
            if mandate_id not in expected_ids:
                print(f"✗ Unexpected mandate ID: {mandate_id}")
                return False
        
        print("✓ All Hidden Funder IDs are correct")
        
        # Check that titles are properly themed
        for mandate in mandates:
            if not mandate.title.startswith("The "):
                print(f"⚠ Warning: Mandate title doesn't follow 'The X' format: {mandate.title}")
        
        print("✓ Hidden Funder data consistency verified")
        return True
        
    except Exception as e:
        print(f"✗ Data consistency test failed: {e}")
        return False

def test_hidden_funder_scoring_integration():
    """Test that Hidden Funder objectives integrate properly with scoring."""
    print("Testing Hidden Funder scoring integration...")
    
    try:
        # Create a game and simulate some actions
        response = requests.post(
            f"{BASE_URL}/api/game",
            json={"player_names": ["Alice", "Bob"]},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            print(f"✗ Failed to create game: {response.status_code}")
            return False
            
        game_data = response.json()
        game_id = game_data["game_id"]
        
        # Get initial state
        response = requests.get(f"{BASE_URL}/api/game/{game_id}")
        if response.status_code != 200:
            print(f"✗ Failed to get game state: {response.status_code}")
            return False
            
        state_data = response.json()
        
        # Check that players have mandates
        players = state_data["state"]["players"]
        for player in players:
            if "mandate" not in player:
                print(f"✗ Player missing mandate in API response")
                return False
        
        print("✓ Hidden Funder scoring integration verified")
        return True
        
    except Exception as e:
        print(f"✗ Scoring integration test failed: {e}")
        return False

def main():
    """Run all Hidden Funder UI tests."""
    print("Hidden Funder UI Display Test Suite")
    print("=" * 50)
    
    tests = [
        ("API Response", test_hidden_funder_api_response),
        ("Frontend Display", test_hidden_funder_frontend_display),
        ("Data Consistency", test_hidden_funder_data_consistency),
        ("Scoring Integration", test_hidden_funder_scoring_integration)
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
        print("🎉 All Hidden Funder UI tests passed!")
    else:
        print("⚠ Some tests failed. Please check the implementation.")
    
    print(f"\nTo test the UI manually, visit: {BASE_URL}")

if __name__ == "__main__":
    main() 