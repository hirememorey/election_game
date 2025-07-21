import pytest
from fastapi.testclient import TestClient
from server import app
import json

client = TestClient(app)

def test_full_game_loop_one_turn():
    """
    Tests the full end-to-end flow for a complete player turn:
    connect, receive state, take multiple actions, pass turn, receive new state.
    """
    with client.websocket_connect("/ws") as websocket:
        # 1. Receive initial state
        initial_data = websocket.receive_json()
        
        assert "players" in initial_data
        human_player_id = initial_data["players"][0]["id"]
        initial_pc = initial_data["players"][0]["pc"]
        assert initial_data["current_player"] == "Human"
        assert initial_data["action_points"][str(human_player_id)] == 2

        # 2. Take first action (Fundraise)
        fundraise_action = next((a for a in initial_data["valid_actions"] if a["action_type"] == "ActionFundraise"), None)
        assert fundraise_action is not None
        websocket.send_json(fundraise_action)
        
        # 3. Receive state after first action, verify it's still our turn
        after_action_1_data = websocket.receive_json()
        assert after_action_1_data["current_player"] == "Human"
        assert after_action_1_data["action_points"][str(human_player_id)] == 1
        
        # 4. Take second action (Fundraise again)
        fundraise_action_2 = next((a for a in after_action_1_data["valid_actions"] if a["action_type"] == "ActionFundraise"), None)
        assert fundraise_action_2 is not None
        websocket.send_json(fundraise_action_2)

        # 5. Receive state after second action, verify we have 0 AP
        after_action_2_data = websocket.receive_json()
        assert after_action_2_data["current_player"] == "Human"
        assert after_action_2_data["action_points"][str(human_player_id)] == 0
        
        # 6. Pass the turn
        pass_action = next((a for a in after_action_2_data["valid_actions"] if a["action_type"] == "ActionPassTurn"), None)
        assert pass_action is not None
        websocket.send_json(pass_action)
        
        # 7. Receive final state for the turn, verify it's now an AI's turn
        final_state = websocket.receive_json()
        assert final_state["current_player"] != "Human"
        
        # 8. Verify our PC has increased from the two Fundraise actions
        final_pc = next((p["pc"] for p in final_state["players"] if p["id"] == human_player_id), None)
        assert final_pc > initial_pc 