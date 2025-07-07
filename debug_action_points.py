#!/usr/bin/env python3
"""
Debug Action Points Initialization
"""

import game_data
from engine.engine import GameEngine

def debug_action_points():
    print("🔍 Debugging Action Points Initialization")
    print("=" * 50)
    
    # Create engine
    engine = GameEngine(game_data.load_game_data())
    
    # Create new game
    state = engine.start_new_game(["Alice", "Bob"])
    
    print(f"Game created successfully")
    print(f"Players: {[p.name for p in state.players]}")
    print(f"Action points: {state.action_points}")
    print(f"Current player: {state.get_current_player().name}")
    print(f"Current player ID: {state.get_current_player().id}")
    
    # Check if action points are initialized
    for player in state.players:
        ap = state.action_points.get(player.id, "NOT SET")
        print(f"  {player.name} (ID {player.id}): {ap} AP")
    
    # Test an action
    print("\nTesting fundraise action...")
    from engine.actions import ActionFundraise
    
    action = ActionFundraise(player_id=0)
    new_state = engine.process_action(state, action)
    
    print(f"Action points after fundraise: {new_state.action_points}")
    for player in new_state.players:
        ap = new_state.action_points.get(player.id, "NOT SET")
        print(f"  {player.name} (ID {player.id}): {ap} AP")

if __name__ == "__main__":
    debug_action_points() 