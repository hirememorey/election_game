#!/usr/bin/env python3
"""
Simple test to verify the full game flow works with the new scoring system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionFundraise, ActionSponsorLegislation, ActionSupportLegislation
from engine.scoring import calculate_final_scores

def test_full_game_flow():
    """Test a complete game flow with scoring."""
    print("Testing complete game flow with scoring...")
    
    # Initialize game
    game_data = load_game_data()
    engine = GameEngine(game_data)
    state = engine.start_new_game(["Alice", "Bob", "Charlie"])
    
    print(f"Game started. Current player: {state.get_current_player().name}")
    print(f"Alice PC: {state.players[0].pc}, AP: {state.action_points[0]}")
    print(f"Bob PC: {state.players[1].pc}, AP: {state.action_points[1]}")
    print(f"Charlie PC: {state.players[2].pc}, AP: {state.action_points[2]}")
    
    # Simulate a few rounds of actions
    actions = [
        ActionFundraise(player_id=0),  # Alice fundraises
        ActionFundraise(player_id=0),  # Alice fundraises again
        ActionSponsorLegislation(player_id=1, legislation_id="INFRASTRUCTURE"),  # Bob sponsors
        ActionSupportLegislation(player_id=2, legislation_id="INFRASTRUCTURE", support_amount=5),  # Charlie supports
        ActionFundraise(player_id=1),  # Bob fundraises
        ActionFundraise(player_id=2),  # Charlie fundraises
    ]
    
    for i, action in enumerate(actions):
        try:
            state = engine.process_action(state, action)
            player = state.get_player_by_id(action.player_id)
            player_name = player.name if player else f"Player {action.player_id}"
            print(f"Action {i+1}: {action.__class__.__name__} by {player_name}")
            print(f"Current player: {state.get_current_player().name}")
            print(f"Alice PC: {state.players[0].pc}, AP: {state.action_points[0]}")
            print(f"Bob PC: {state.players[1].pc}, AP: {state.action_points[1]}")
            print(f"Charlie PC: {state.players[2].pc}, AP: {state.action_points[2]}")
            print(f"Round: {state.round_marker}, Phase: {state.current_phase}")
            print("---")
        except Exception as e:
            print(f"Action {i+1} failed: {e}")
            break
    
    # Simulate end of term and legislation resolution
    print("Simulating legislation resolution...")
    state.legislation_history = [
        {
            'sponsor_id': 1,  # Bob sponsored
            'legislation_id': 'INFRASTRUCTURE',
            'outcome': 'Success',
            'support_players': {2: 5},  # Charlie supported
            'oppose_players': {}
        }
    ]
    
    # Give Alice the presidency for testing
    state.players[0].current_office = game_data["offices"]["PRESIDENT"]
    state.players[0].pc = 50
    
    # Give Bob a lower office
    state.players[1].current_office = game_data["offices"]["US_SENATOR"]
    state.players[1].pc = 30
    
    # Charlie has no office but lots of PC
    state.players[2].pc = 100
    
    # Test final scoring
    print("Testing final scoring...")
    scores = calculate_final_scores(state)
    
    print("Final Scores:")
    for player_id, score_data in scores.items():
        player = state.get_player_by_id(player_id)
        if player:
            print(f"{player.name}: {score_data['total_influence']} Influence")
            for detail in score_data['details']:
                print(f"  - {detail}")
    
    # Verify the scoring works
    assert scores[0]['total_influence'] > 0, "Alice should have Influence from presidency"
    assert scores[1]['total_influence'] > 0, "Bob should have Influence from office + PC"
    assert scores[2]['total_influence'] > 0, "Charlie should have Influence from PC conversion"
    
    print("✓ Full game flow test passed!")
    return True

if __name__ == "__main__":
    test_full_game_flow() 