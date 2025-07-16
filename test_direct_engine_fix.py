#!/usr/bin/env python3
"""
Direct engine test to verify legislation session fix.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionSponsorLegislation, ActionPassTurn

def test_direct_engine():
    print("🔍 Direct Engine Test")
    print("=" * 30)
    print()
    
    # Load game data and create engine
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Create a new game
    state = engine.start_new_game(['Alice', 'Bob'])
    print(f"✅ Game created")
    print(f"   Initial round marker: {state.round_marker}")
    print(f"   Initial phase: {state.current_phase}")
    print()
    
    # Run the initial event phase to get to ACTION_PHASE
    if state.current_phase == 'EVENT_PHASE':
        print("Running initial event phase...")
        state = engine.run_event_phase(state)
        print(f"   After event phase: {state.current_phase}")
        print()
    
    # Sponsor legislation
    action = ActionSponsorLegislation(player_id=0, legislation_id='INFRASTRUCTURE')
    state = engine.process_action(state, action)
    print(f"✅ Infrastructure bill sponsored!")
    print(f"   Pending legislation: {state.pending_legislation.legislation_id if state.pending_legislation else None}")
    print(f"   Term legislation: {len(state.term_legislation)} items")
    print()
    
    # Simulate rounds by passing turns
    for round_num in range(1, 5):
        print(f"Round {round_num}:")
        
        # Player 1 passes turn
        action = ActionPassTurn(player_id=1)
        state = engine.process_action(state, action)
        print(f"   After player 1 turn:")
        print(f"     Round marker: {state.round_marker}")
        print(f"     Phase: {state.current_phase}")
        print(f"     Term legislation: {len(state.term_legislation)} items")
        print(f"     Awaiting legislation: {state.awaiting_legislation_resolution}")
        
        # Player 0 passes turn
        action = ActionPassTurn(player_id=0)
        state = engine.process_action(state, action)
        print(f"   After player 0 turn:")
        print(f"     Round marker: {state.round_marker}")
        print(f"     Phase: {state.current_phase}")
        print(f"     Term legislation: {len(state.term_legislation)} items")
        print(f"     Awaiting legislation: {state.awaiting_legislation_resolution}")
        
        # Check if we're in legislation phase
        if state.current_phase == 'LEGISLATION_PHASE':
            print(f"   ✅ Legislation phase triggered!")
            return True
        
        print()
    
    # Final state
    print("Final state:")
    print(f"   Round marker: {state.round_marker}")
    print(f"   Phase: {state.current_phase}")
    print(f"   Awaiting legislation: {state.awaiting_legislation_resolution}")
    print(f"   Term legislation: {len(state.term_legislation)} items")
    
    if state.awaiting_legislation_resolution:
        print("✅ Legislation resolution was triggered")
        return True
    else:
        print("❌ Legislation resolution was never triggered")
        return False

if __name__ == "__main__":
    try:
        success = test_direct_engine()
        if success:
            print("\n✅ Direct engine test passed!")
        else:
            print("\n❌ Direct engine test failed!")
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc() 