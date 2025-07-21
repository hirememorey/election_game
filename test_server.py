import pytest
from fastapi.testclient import TestClient
from server import app
import json

client = TestClient(app)

def test_websocket_connection_and_initial_state():
    """
    Tests that a client can connect to the WebSocket and receives a valid initial game state.
    """
    with client.websocket_connect("/ws") as websocket:
        # Receive the first message, which should be the initial state
        data = websocket.receive_json()

        # Verify the structure of the initial state
        assert "round_marker" in data
        assert data["round_marker"] == 1
        
        assert "players" in data
        assert isinstance(data["players"], list)
        assert len(data["players"]) == 4  # Assuming 1 human, 3 AI
        
        assert "current_player" in data
        assert isinstance(data["current_player"], str)
        
        assert "log" in data
        assert isinstance(data["log"], list)
        
        # Check a specific player detail to ensure serialization is working
        # Note: This part of the test will need to be expanded once the to_dict methods
        # in the models are fully implemented.
        # For now, we are just checking the player names.
        assert data["players"][0]['name'] == "Human" 