#!/usr/bin/env python3
"""
Test to verify Media Scrutiny negative favor correctly halves PC gained from Fundraise actions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionUseFavor, ActionFundraise
from models.game_state import GameState

def test_media_scrutiny_fix():
    """Test that Media Scrutiny correctly halves PC gained from Fundraise actions."""
    print("🧪 Testing Media Scrutiny Fix")
    
    # Initialize game
    game_data = load_game_data()
    engine = GameEngine(game_data)
    state = engine.start_new_game(["Alice", "Bob"])
    
    # Give Alice a Media Scrutiny favor
    media_scrutiny_favor = next(f for f in game_data['favors'] if f.id == 'MEDIA_SCRUTINY')
    state.players[0].favors.append(media_scrutiny_favor)
    
    # Set Alice as current player
    state.current_player_index = 0
    
    print(f"Alice's PC before Media Scrutiny: {state.players[0].pc}")
    
    # Use the Media Scrutiny favor
    action = ActionUseFavor(player_id=0, favor_id='MEDIA_SCRUTINY')
    state = engine.process_action(state, action)
    
    print(f"Alice's PC after using Media Scrutiny favor: {state.players[0].pc}")
    print(f"Media scrutiny players: {state.media_scrutiny_players}")
    
    # Now test Fundraise action - should gain 2 PC instead of 5 PC
    original_pc = state.players[0].pc
    action = ActionFundraise(player_id=0)
    state = engine.process_action(state, action)
    pc_gain = state.players[0].pc - original_pc
    
    print(f"Alice's PC after Fundraise: {state.players[0].pc}")
    print(f"PC gained from Fundraise: {pc_gain}")
    
    # Verify the effect worked correctly
    if pc_gain == 2:
        print("✅ Media Scrutiny Fix: PC gain correctly halved from 5 to 2")
    else:
        print(f"❌ Media Scrutiny Fix: Expected 2 PC gain, got {pc_gain}")
        return False
    
    # Test that the effect is cleared at the end of the round
    print("\n🧪 Testing Media Scrutiny Effect Clearing")
    
    # Advance to end of round (upkeep phase)
    print("Advancing to upkeep phase...")
    state = engine.run_upkeep_phase(state)
    
    print(f"Media scrutiny players after upkeep: {state.media_scrutiny_players}")
    
    # Test Fundraise again - should now gain normal 5 PC
    original_pc = state.players[0].pc
    action = ActionFundraise(player_id=0)
    state = engine.process_action(state, action)
    pc_gain = state.players[0].pc - original_pc
    
    print(f"Alice's PC after Fundraise (after upkeep): {state.players[0].pc}")
    print(f"PC gained from Fundraise (after upkeep): {pc_gain}")
    
    # Verify the effect was cleared
    if pc_gain == 5:
        print("✅ Media Scrutiny Effect Clearing: PC gain back to normal 5")
        return True
    else:
        print(f"❌ Media Scrutiny Effect Clearing: Expected 5 PC gain, got {pc_gain}")
        return False

if __name__ == "__main__":
    test_media_scrutiny_fix() 