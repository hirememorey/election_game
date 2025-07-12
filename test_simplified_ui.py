#!/usr/bin/env python3
"""
Test script for the simplified phase-based UI
"""

import requests
import json
import time

def test_simplified_ui():
    """Test the simplified UI functionality"""
    
    base_url = "http://localhost:5001/api"
    
    print("🧪 Testing Simplified Phase-Based UI")
    print("=" * 50)
    
    # Test 1: Create a new game
    print("\n1. Creating new game...")
    try:
        response = requests.post(f"{base_url}/game", json={
            "player_names": ["Alice", "Bob", "Charlie"]
        })
        
        if response.status_code == 200:
            game_data = response.json()
            game_id = game_data['game_id']
            print(f"✅ Game created successfully: {game_id}")
        else:
            print(f"❌ Failed to create game: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error creating game: {e}")
        return
    
    # Test 2: Get initial game state
    print("\n2. Getting initial game state...")
    try:
        response = requests.get(f"{base_url}/game/{game_id}")
        
        if response.status_code == 200:
            game_state = response.json()['state']
            print(f"✅ Game state retrieved")
            print(f"   - Current phase: {game_state['current_phase']}")
            print(f"   - Current round: {game_state['round_marker']}")
            print(f"   - Current player: {game_state['players'][game_state['current_player_index']]['name']}")
        else:
            print(f"❌ Failed to get game state: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Error getting game state: {e}")
        return
    
    # Test 3: Perform a simple action
    print("\n3. Testing action performance...")
    try:
        current_player = game_state['players'][game_state['current_player_index']]
        response = requests.post(f"{base_url}/game/{game_id}/action", json={
            "action_type": "fundraise",
            "player_id": current_player['id']
        })
        
        if response.status_code == 200:
            updated_state = response.json()['state']
            print(f"✅ Action performed successfully")
            print(f"   - Player PC: {updated_state['players'][game_state['current_player_index']]['pc']}")
        else:
            print(f"❌ Failed to perform action: {response.status_code}")
    except Exception as e:
        print(f"❌ Error performing action: {e}")
    
    # Test 4: Test UI elements
    print("\n4. Testing UI elements...")
    try:
        # Test main page
        response = requests.get("http://localhost:5001/")
        if response.status_code == 200:
            print("✅ Main page loads successfully")
        else:
            print(f"❌ Main page failed to load: {response.status_code}")
        
        # Test static files
        response = requests.get("http://localhost:5001/static/style.css")
        if response.status_code == 200:
            print("✅ CSS loads successfully")
        else:
            print(f"❌ CSS failed to load: {response.status_code}")
        
        response = requests.get("http://localhost:5001/static/script.js")
        if response.status_code == 200:
            print("✅ JavaScript loads successfully")
        else:
            print(f"❌ JavaScript failed to load: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing UI elements: {e}")
    
    print("\n🎉 Simplified UI test completed!")
    print("\n📱 Key Features Implemented:")
    print("   - Phase-based contextual UI")
    print("   - Swipe gesture navigation")
    print("   - Progressive disclosure")
    print("   - Mobile-first design")
    print("   - Simplified action buttons")
    print("   - Quick access panel")
    
    print(f"\n🌐 Open http://localhost:5001 in your browser to see the new UI!")

if __name__ == "__main__":
    test_simplified_ui() 