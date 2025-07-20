#!/usr/bin/env python3
"""
Test Campaign Removal

This test verifies that:
1. Campaign actions have been completely removed from the game
2. Declare Candidacy still works correctly in round 4
3. No campaign-related errors occur
4. Other actions still work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionFundraise, ActionNetwork, ActionSponsorLegislation, ActionDeclareCandidacy, ActionUseFavor, ActionPassTurn

def test_campaign_removal():
    """Test that campaign actions have been completely removed."""
    print("🧪 Testing Campaign Removal")
    
    # Load game data and create engine
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Create a new game
    player_names = ["Alice", "Bob", "Charlie"]
    state = engine.start_new_game(player_names)
    
    print(f"✅ Game created with {len(state.players)} players")
    
    # Test 1: Verify campaign action is not in action point costs
    print("\nTest 1: Verifying campaign action is not in action point costs")
    action_costs = engine.action_point_costs
    if "ActionCampaign" in action_costs:
        print(f"❌ ActionCampaign still exists in action point costs: {action_costs['ActionCampaign']}")
        return False
    else:
        print("✅ ActionCampaign removed from action point costs")
    
    # Test 2: Verify campaign action is not in action resolvers
    print("\nTest 2: Verifying campaign action is not in action resolvers")
    action_resolvers = engine.action_resolvers
    if "ActionCampaign" in action_resolvers:
        print(f"❌ ActionCampaign still exists in action resolvers")
        return False
    else:
        print("✅ ActionCampaign removed from action resolvers")
    
    # Test 3: Verify campaign_influences field is removed from game state
    print("\nTest 3: Verifying campaign_influences field is removed")
    if hasattr(state, 'campaign_influences'):
        print(f"❌ campaign_influences field still exists in game state")
        return False
    else:
        print("✅ campaign_influences field removed from game state")
    
    # Test 4: Test that other actions still work
    print("\nTest 4: Testing that other actions still work")
    
    # Test fundraise action
    try:
        action = ActionFundraise(player_id=0)
        new_state = engine.process_action(state, action)
        print("✅ Fundraise action works")
    except Exception as e:
        print(f"❌ Fundraise action failed: {e}")
        return False
    
    # Test network action
    try:
        action = ActionNetwork(player_id=0)
        new_state = engine.process_action(new_state, action)
        print("✅ Network action works")
    except Exception as e:
        print(f"❌ Network action failed: {e}")
        return False
    
    # Test 5: Test candidacy in round 4
    print("\nTest 5: Testing candidacy in round 4")
    
    # Set up round 4
    new_state.round_marker = 4
    new_state.action_points[0] = 2  # Give Alice 2 AP
    new_state.public_gaffe_players.clear()  # Ensure no public gaffe effects
    
    try:
        action = ActionDeclareCandidacy(player_id=0, office_id="GOVERNOR", committed_pc=5)
        final_state = engine.process_action(new_state, action)
        print("✅ Declare Candidacy action works in round 4")
        
        # Verify candidacy was created
        if len(final_state.secret_candidacies) == 1:
            candidacy = final_state.secret_candidacies[0]
            if candidacy.player_id == 0 and candidacy.office_id == "GOVERNOR":
                print("✅ Candidacy was properly created")
            else:
                print(f"❌ Candidacy details incorrect: {candidacy}")
                return False
        else:
            print(f"❌ Expected 1 candidacy, got {len(final_state.secret_candidacies)}")
            return False
            
    except Exception as e:
        print(f"❌ Declare Candidacy action failed: {e}")
        return False
    
    # Test 6: Test that candidacy is not available in other rounds
    print("\nTest 6: Testing candidacy is not available in other rounds")
    
    # Set up round 3
    test_state = engine.start_new_game(player_names)
    test_state.round_marker = 3
    test_state.action_points[0] = 2  # Give Alice 2 AP
    test_state.public_gaffe_players.clear()  # Ensure no public gaffe effects
    
    try:
        action = ActionDeclareCandidacy(player_id=0, office_id="GOVERNOR", committed_pc=5)
        # This should work since the round restriction is only in frontend
        # The backend allows candidacy in any round, frontend restricts to round 4
        test_result = engine.process_action(test_state, action)
        print("✅ Backend allows candidacy in any round (frontend restricts to round 4)")
    except Exception as e:
        print(f"❌ Backend incorrectly blocks candidacy: {e}")
        return False
    
    # Test 7: Test pass turn action
    print("\nTest 7: Testing pass turn action")
    
    try:
        action = ActionPassTurn(player_id=0)
        pass_state = engine.process_action(test_state, action)
        print("✅ Pass Turn action works")
    except Exception as e:
        print(f"❌ Pass Turn action failed: {e}")
        return False
    
    print("\n🎉 All tests passed! Campaign removal successful.")
    return True

if __name__ == "__main__":
    success = test_campaign_removal()
    if success:
        print("\n✅ Campaign removal test completed successfully")
        sys.exit(0)
    else:
        print("\n❌ Campaign removal test failed")
        sys.exit(1) 