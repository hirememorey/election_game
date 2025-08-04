#!/usr/bin/env python3
"""
WebSocket Debug Test Script
"""

import asyncio
import websockets
import json
import sys

async def test_websocket():
    print("🔍 Testing WebSocket connection...")
    
    try:
        # Connect to the WebSocket
        uri = "ws://localhost:5001/ws"
        print(f"Connecting to {uri}...")
        
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")
            
            # Wait for initial state
            print("📨 Waiting for initial state...")
            message = await websocket.recv()
            print(f"📨 Received message ({len(message)} bytes)")
            
            try:
                state = json.loads(message)
                print("✅ Successfully parsed JSON")
                
                # Analyze the state
                print("\n📊 State Analysis:")
                print(f"  Players: {len(state.get('players', []))}")
                print(f"  Current Player Index: {state.get('current_player_index')}")
                print(f"  Valid Actions: {len(state.get('valid_actions', []))}")
                
                # Check for human player
                players = state.get('players', [])
                human_player = None
                for player in players:
                    if player.get('name') == 'Human':
                        human_player = player
                        break
                
                if human_player:
                    print(f"  Human Player Found: Yes (ID: {human_player.get('id')})")
                    print(f"  Is Human Turn: {state.get('current_player_index') == human_player.get('id')}")
                else:
                    print("  Human Player Found: No")
                
                # Check valid actions
                valid_actions = state.get('valid_actions', [])
                if valid_actions:
                    print(f"  Action Types: {[a.get('action_type') for a in valid_actions]}")
                else:
                    print("  No valid actions")
                
                # Test sending an action
                if valid_actions:
                    test_action = valid_actions[0]
                    print(f"\n🧪 Testing action: {test_action.get('action_type')}")
                    
                    await websocket.send(json.dumps(test_action))
                    print("📤 Sent test action")
                    
                    # Wait for response
                    response = await websocket.recv()
                    print(f"📨 Received response ({len(response)} bytes)")
                    
                    try:
                        response_state = json.loads(response)
                        print("✅ Successfully parsed response JSON")
                        print(f"  New Valid Actions: {len(response_state.get('valid_actions', []))}")
                    except json.JSONDecodeError as e:
                        print(f"❌ Failed to parse response JSON: {e}")
                        print(f"Raw response: {response}")
                
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse initial JSON: {e}")
                print(f"Raw message: {message}")
                
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_websocket())
    sys.exit(0 if success else 1) 