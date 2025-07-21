import pytest
from game_session import GameSession

def test_game_session_initialization():
    """Tests that a GameSession can be created and a game can be started."""
    try:
        session = GameSession()
        assert session.state is None, "Game state should be None before starting."
        
        session.start_game()
        assert session.state is not None, "Game state should be initialized after starting."
        assert session.state.round_marker == 1, "Game should start in round 1."
        assert len(session.state.players) == 4, "Game should start with 4 players (1 human, 3 AI)."

    except Exception as e:
        pytest.fail(f"GameSession initialization failed with an exception: {e}")

def test_get_state_for_client():
    """Tests that the game state can be serialized to a dictionary for the client."""
    session = GameSession()
    session.start_game()
    
    client_state = session.get_state_for_client()
    
    assert isinstance(client_state, dict)
    # Check for some key fields to ensure serialization is working
    assert "round_marker" in client_state
    assert "players" in client_state
    assert "current_player" in client_state
    assert "log" in client_state
    
    assert len(client_state["players"]) == 4
    assert client_state["players"][0] == "Human"

    # Since the to_dict methods are not fully implemented, we can't test everything yet.
    # This confirms the basic structure is present. 