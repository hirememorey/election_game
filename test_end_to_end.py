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

        # 5. Receive the final state after our turn and all AI turns are complete.
        # The server processes everything and sends the new state for the start of the next human turn.
        final_state = websocket.receive_json()

        # 6. Verify that it's our turn again and the game has advanced.
        assert final_state["current_player"] == "Human"
        
        # 7. Verify our PC has increased from the two Fundraise actions.
        final_pc = next((p["pc"] for p in final_state["players"] if p["id"] == human_player_id), None)
        assert final_pc > initial_pc

        # 8. Verify our action points have been reset for the new turn.
        assert final_state["action_points"][str(human_player_id)] == 2

        # 9. Verify that the AI turns actually ran by checking the log.
        assert len(final_state["log"]) > 0 