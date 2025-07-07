#!/usr/bin/env python3
"""
Test script to verify that Form Alliance action has been removed.
"""

from engine.engine import GameEngine
from game_data import load_game_data

def test_form_alliance_removal():
    """Test that Form Alliance action is no longer available."""
    
    print("Testing Form Alliance removal...")
    
    # Load game data and create engine
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Check that Form Alliance is not in action resolvers
    if "ActionFormAlliance" in engine.action_resolvers:
        print("❌ ERROR: ActionFormAlliance still in action resolvers")
        return False
    else:
        print("✅ ActionFormAlliance removed from action resolvers")
    
    # Test that we can't import ActionFormAlliance
    try:
        from engine.actions import ActionFormAlliance
        print("❌ ERROR: ActionFormAlliance can still be imported")
        return False
    except ImportError:
        print("✅ ActionFormAlliance cannot be imported")
    
    # Check that other actions are still available
    available_actions = list(engine.action_resolvers.keys())
    expected_actions = [
        "ActionFundraise", "ActionNetwork", "ActionSponsorLegislation",
        "ActionDeclareCandidacy", "ActionUseFavor", "ActionSupportLegislation", 
        "ActionOpposeLegislation"
    ]
    
    for action in expected_actions:
        if action in available_actions:
            print(f"✅ {action} still available")
        else:
            print(f"❌ ERROR: {action} missing from action resolvers")
            return False
    
    print("\n🎉 All tests passed! Form Alliance action has been successfully removed.")
    print(f"Available actions: {', '.join(available_actions)}")
    return True

if __name__ == "__main__":
    test_form_alliance_removal() 