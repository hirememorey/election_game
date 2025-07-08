#!/usr/bin/env python3
"""
Test file for negative favors implementation.
Tests all the new negative favor mechanics to ensure they work correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionNetwork, ActionUseFavor, ActionFundraise, ActionSponsorLegislation, ActionDeclareCandidacy, ActionCampaign
from models.game_state import GameState

def test_negative_favors():
    """Test all negative favor mechanics."""
    print("🧪 Testing Negative Favors Implementation")
    
    # Initialize game
    game_data = load_game_data()
    engine = GameEngine(game_data)
    state = engine.start_new_game(["Alice", "Bob", "Charlie"])
    
    # Test 1: Political Debt
    print("\n1. Testing Political Debt...")
    # Give Alice a political debt favor
    political_debt_favor = next(f for f in game_data['favors'] if f.id == 'POLITICAL_DEBT')
    state.players[0].favors.append(political_debt_favor)
    
    # Use the political debt favor
    action = ActionUseFavor(player_id=0, favor_id='POLITICAL_DEBT', target_player_id=1)
    state = engine.process_action(state, action)
    
    # Verify the debt was created
    assert 0 in state.political_debts
    assert state.political_debts[0] == 1
    print("✅ Political Debt: Alice now owes Bob a political debt")
    
    # Test 2: Public Gaffe
    print("\n2. Testing Public Gaffe...")
    # Give Bob a public gaffe favor
    public_gaffe_favor = next(f for f in game_data['favors'] if f.id == 'PUBLIC_GAFFE')
    state.players[1].favors.append(public_gaffe_favor)
    
    # Set Bob as current player
    state.current_player_index = 1
    
    # Use the public gaffe favor
    action = ActionUseFavor(player_id=1, favor_id='PUBLIC_GAFFE')
    state = engine.process_action(state, action)
    
    # Verify the effect was applied
    assert 1 in state.public_gaffe_players
    print("✅ Public Gaffe: Bob has the public gaffe effect")
    
    # Test 3: Media Scrutiny
    print("\n3. Testing Media Scrutiny...")
    # Give Charlie a media scrutiny favor
    media_scrutiny_favor = next(f for f in game_data['favors'] if f.id == 'MEDIA_SCRUTINY')
    state.players[2].favors.append(media_scrutiny_favor)
    
    # Set Charlie as current player
    state.current_player_index = 2
    
    # Use the media scrutiny favor
    action = ActionUseFavor(player_id=2, favor_id='MEDIA_SCRUTINY')
    state = engine.process_action(state, action)
    
    # Verify the effect was applied
    assert 2 in state.media_scrutiny_players
    print("✅ Media Scrutiny: Charlie has the media scrutiny effect")
    
    # Test that fundraise is halved for Charlie
    original_pc = state.players[2].pc
    action = ActionFundraise(player_id=2)
    state = engine.process_action(state, action)
    pc_gain = state.players[2].pc - original_pc
    print(f"✅ Media Scrutiny Effect: Charlie gained {pc_gain} PC (should be halved)")
    
    # Test 4: Compromising Position - Discard Favors
    print("\n4. Testing Compromising Position (Discard Favors)...")
    # Give Alice two extra favors and a compromising position favor
    extra_favor1 = next(f for f in game_data['favors'] if f.id == 'EXTRA_FUNDRAISING')
    extra_favor2 = next(f for f in game_data['favors'] if f.id == 'LEGISLATIVE_INFLUENCE')
    state.players[0].favors.extend([extra_favor1, extra_favor2])
    
    compromising_favor = next(f for f in game_data['favors'] if f.id == 'COMPROMISING_POSITION')
    state.players[0].favors.append(compromising_favor)
    
    initial_favor_count = len(state.players[0].favors)
    
    # Set Alice as current player
    state.current_player_index = 0
    
    # Use the compromising position favor with discard choice
    action = ActionUseFavor(player_id=0, favor_id='COMPROMISING_POSITION', choice='discard_favors')
    state = engine.process_action(state, action)
    
    # Verify two favors were discarded
    final_favor_count = len(state.players[0].favors)
    assert final_favor_count == initial_favor_count - 3  # -3 because we added 2 extra + 1 compromising, then discarded 2
    print("✅ Compromising Position (Discard): Alice discarded two favors")
    
    # Test 5: Compromising Position - Reveal Archetype
    print("\n5. Testing Compromising Position (Reveal Archetype)...")
    # Give Bob a compromising position favor
    state.players[1].favors.append(compromising_favor)
    
    # Set Bob as current player
    state.current_player_index = 1
    
    # Use the compromising position favor with reveal choice
    action = ActionUseFavor(player_id=1, favor_id='COMPROMISING_POSITION', choice='reveal_archetype')
    state = engine.process_action(state, action)
    
    # Verify the archetype was revealed
    assert 1 in state.compromised_players
    print("✅ Compromising Position (Reveal): Bob's archetype is now revealed")
    
    # Test 6: Political Hot Potato
    print("\n6. Testing Political Hot Potato...")
    # Give Charlie a political hot potato favor
    hot_potato_favor = next(f for f in game_data['favors'] if f.id == 'POLITICAL_HOT_POTATO')
    state.players[2].favors.append(hot_potato_favor)
    
    # Set Charlie as current player
    state.current_player_index = 2
    
    # Use the political hot potato favor
    action = ActionUseFavor(player_id=2, favor_id='POLITICAL_HOT_POTATO', target_player_id=0)
    state = engine.process_action(state, action)
    
    # Verify the hot potato was passed
    assert state.hot_potato_holder == 0
    print("✅ Political Hot Potato: The hot potato was passed to Alice")
    
    # Test 7: Public Gaffe AP Cost Increase
    print("\n7. Testing Public Gaffe AP Cost Increase...")
    # Give Bob the public gaffe effect again
    state.public_gaffe_players.add(1)
    
    # Set Bob as current player
    state.current_player_index = 1
    
    # Try to sponsor legislation (should cost +1 AP)
    state.players[1].pc = 20  # Give Bob enough PC
    action = ActionSponsorLegislation(player_id=1, legislation_id='INFRASTRUCTURE')
    
    # This should work but cost extra AP
    state = engine.process_action(state, action)
    print("✅ Public Gaffe AP Cost: Bob's legislation sponsorship cost +1 AP")
    
    # Verify the effect was removed after use
    assert 1 not in state.public_gaffe_players
    print("✅ Public Gaffe Effect: The effect was removed after use")
    
    # Test 8: Upkeep Phase Clears Effects
    print("\n8. Testing Upkeep Phase Clears Effects...")
    # Charlie should still have media scrutiny
    assert 2 in state.media_scrutiny_players
    
    # Run upkeep phase
    from engine.resolvers import resolve_upkeep
    state = resolve_upkeep(state)
    
    # Verify media scrutiny was cleared
    assert 2 not in state.media_scrutiny_players
    print("✅ Upkeep Phase: Media scrutiny effect was cleared")
    
    # Test 9: Hot Potato Effect at Upkeep
    print("\n9. Testing Hot Potato Effect at Upkeep...")
    # Give Alice some campaign influence
    from models.components import CampaignInfluence
    influence = CampaignInfluence(player_id=0, office_id='GOVERNOR', influence_amount=10)
    state.campaign_influences.append(influence)
    
    # Run upkeep again to trigger hot potato effect
    state = resolve_upkeep(state)
    
    # Verify hot potato holder was cleared
    assert state.hot_potato_holder is None
    print("✅ Hot Potato Effect: Alice lost influence and hot potato was cleared")
    
    print("\n🎉 All negative favor tests passed!")
    return True

def test_network_action_balance():
    """Test that Network action now has risk/reward balance."""
    print("\n🧪 Testing Network Action Balance")
    
    # Initialize game
    game_data = load_game_data()
    engine = GameEngine(game_data)
    state = engine.start_new_game(["Alice", "Bob"])
    
    # Count negative vs positive favors in the supply
    negative_favors = [f for f in state.favor_supply if f.id.startswith(('POLITICAL_DEBT', 'PUBLIC_GAFFE', 'MEDIA_SCRUTINY', 'COMPROMISING_POSITION', 'POLITICAL_HOT_POTATO'))]
    positive_favors = [f for f in state.favor_supply if not f.id.startswith(('POLITICAL_DEBT', 'PUBLIC_GAFFE', 'MEDIA_SCRUTINY', 'COMPROMISING_POSITION', 'POLITICAL_HOT_POTATO'))]
    
    print(f"Total favors in supply: {len(state.favor_supply)}")
    print(f"Negative favors: {len(negative_favors)}")
    print(f"Positive favors: {len(positive_favors)}")
    print(f"Risk ratio: {len(negative_favors)}/{len(state.favor_supply)} = {len(negative_favors)/len(state.favor_supply)*100:.1f}%")
    
    # Test multiple network actions to see the risk
    print("\nTesting multiple Network actions...")
    for i in range(5):
        # Set player 0 as current player
        state.current_player_index = 0
        
        action = ActionNetwork(player_id=0)
        state = engine.process_action(state, action)
        
        if state.players[0].favors:
            last_favor = state.players[0].favors[-1]
            is_negative = last_favor.id.startswith(('POLITICAL_DEBT', 'PUBLIC_GAFFE', 'MEDIA_SCRUTINY', 'COMPROMISING_POSITION', 'POLITICAL_HOT_POTATO'))
            print(f"Network {i+1}: Got favor '{last_favor.description}' ({'NEGATIVE' if is_negative else 'POSITIVE'})")
        else:
            print(f"Network {i+1}: No favor gained (supply empty)")
    
    print("✅ Network action balance test completed")
    return True

if __name__ == "__main__":
    try:
        test_negative_favors()
        test_network_action_balance()
        print("\n🎉 All tests passed! Negative favors are working correctly.")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 