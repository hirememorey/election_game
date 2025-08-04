#!/usr/bin/env python3
"""
Test script to verify legislation resolution works end-to-end.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_session import GameSession
from engine.actions import ActionResolveLegislation
from engine.engine import GameEngine
from game_data import load_game_data

def test_legislation_resolution():
    """Test that legislation resolution actually works."""
    print("Testing legislation resolution...")
    
    # Create a game session
    session = GameSession()
    session.start_game()
    
    # Add some legislation to resolve
    from models.game_state import PendingLegislation
    
    # Create test legislation
    test_legislation = PendingLegislation(
        legislation_id="CHILDREN",
        sponsor_id=1,
        support_players={},
        oppose_players={},
        resolved=False
    )
    
    session.state.term_legislation.append(test_legislation)
    session.state.awaiting_legislation_resolution = True
    
    print(f"Before resolution: {len(session.state.term_legislation)} bills")
    
    try:
        # Test the resolve legislation action
        action = ActionResolveLegislation(player_id=-1)
        session._execute_action(action)
        
        print(f"After resolution: {len(session.state.term_legislation)} bills")
        print(f"Awaiting election resolution: {session.state.awaiting_election_resolution}")
        print(f"Awaiting results acknowledgement: {session.state.awaiting_results_acknowledgement}")
        
        # After legislation resolution, elections should be processed immediately
        # So awaiting_election_resolution should be False, but awaiting_results_acknowledgement should be True
        if len(session.state.term_legislation) == 0 and session.state.awaiting_results_acknowledgement:
            print("✅ Legislation resolution works!")
            return True
        else:
            print("❌ Legislation resolution failed")
            return False
            
    except Exception as e:
        print(f"❌ Legislation resolution crashed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_complete_legislation_flow():
    """Test the complete legislation flow."""
    print("Testing complete legislation flow...")
    
    # Create a game session
    session = GameSession()
    session.start_game()
    
    # Simulate a complete term with legislation
    try:
        # Add some legislation
        from models.game_state import PendingLegislation
        test_legislation = PendingLegislation(
            legislation_id="CHILDREN",
            sponsor_id=1,
            support_players={},
            oppose_players={},
            resolved=False
        )
        session.state.term_legislation.append(test_legislation)
        session.state.awaiting_legislation_resolution = True
        
        # Test resolve legislation
        action = ActionResolveLegislation(player_id=-1)
        session._execute_action(action)
        
        # Test resolve elections
        from engine.actions import ActionResolveElections
        action = ActionResolveElections(player_id=-1)
        session._execute_action(action)
        
        print("✅ Complete legislation flow works!")
        return True
        
    except Exception as e:
        print(f"❌ Complete legislation flow failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("=== Testing Legislation Resolution ===")
    
    tests = [
        test_legislation_resolution,
        test_complete_legislation_flow,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test {test.__name__} failed")
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print(f"\n=== Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("🎉 All tests passed! Legislation resolution should work.")
    else:
        print("❌ Some tests failed. Legislation resolution needs more work.")

if __name__ == "__main__":
    main() 