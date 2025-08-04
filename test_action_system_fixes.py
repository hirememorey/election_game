#!/usr/bin/env python3
"""
Test script to verify action system fixes work correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game_session import GameSession
from engine.actions import AcknowledgeAITurn, ActionResolveLegislation, ActionResolveElections, ActionAcknowledgeResults
from engine.engine import GameEngine
from game_data import load_game_data

def test_missing_resolvers():
    """Test that all action types have resolvers."""
    print("Testing missing resolvers...")
    
    engine = GameEngine(load_game_data())
    
    # Test that AcknowledgeAITurn has a resolver
    action = AcknowledgeAITurn(player_id=0)
    try:
        # This should not raise an error
        result = engine.process_action(engine.start_new_game(["Player1", "Player2"]), action)
        print("✅ AcknowledgeAITurn resolver works")
    except Exception as e:
        print(f"❌ AcknowledgeAITurn resolver failed: {e}")
        return False
    
    return True

def test_system_actions():
    """Test that system actions actually work."""
    print("Testing system actions...")
    
    engine = GameEngine(load_game_data())
    state = engine.start_new_game(["Player1", "Player2"])
    
    # Test ActionResolveLegislation
    try:
        action = ActionResolveLegislation(player_id=-1)
        result = engine.process_action(state, action)
        print("✅ ActionResolveLegislation works")
    except Exception as e:
        print(f"❌ ActionResolveLegislation failed: {e}")
        return False
    
    # Test ActionResolveElections
    try:
        action = ActionResolveElections(player_id=-1)
        result = engine.process_action(state, action)
        print("✅ ActionResolveElections works")
    except Exception as e:
        print(f"❌ ActionResolveElections failed: {e}")
        return False
    
    # Test ActionAcknowledgeResults
    try:
        action = ActionAcknowledgeResults(player_id=-1)
        result = engine.process_action(state, action)
        print("✅ ActionAcknowledgeResults works")
    except Exception as e:
        print(f"❌ ActionAcknowledgeResults failed: {e}")
        return False
    
    return True

def test_action_creation():
    """Test that action creation works with missing player_id."""
    print("Testing action creation...")
    
    session = GameSession()
    session.start_game()
    
    # Test action creation with missing player_id
    try:
        action_data = {"action_type": "ActionFundraise"}
        session.process_human_action(action_data)
        print("✅ Action creation with missing player_id works")
    except Exception as e:
        print(f"❌ Action creation with missing player_id failed: {e}")
        return False
    
    return True

def test_complete_game_flow():
    """Test complete game flow."""
    print("Testing complete game flow...")
    
    session = GameSession()
    session.start_game()
    
    # Test a few human actions
    try:
        # Test fundraise action
        action_data = {"action_type": "ActionFundraise"}
        session.process_human_action(action_data)
        
        # Test pass turn
        action_data = {"action_type": "ActionPassTurn"}
        session.process_human_action(action_data)
        
        print("✅ Complete game flow works")
        return True
    except Exception as e:
        print(f"❌ Complete game flow failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=== Testing Action System Fixes ===")
    
    tests = [
        test_missing_resolvers,
        test_system_actions,
        test_action_creation,
        test_complete_game_flow,
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
        print("🎉 All tests passed! Action system fixes are working.")
    else:
        print("❌ Some tests failed. Action system needs more work.")

if __name__ == "__main__":
    main() 