import unittest
from game_session import GameSession
from models.game_state import GameState
from engine.actions import ActionFundraise

class TestStateDrivenFlow(unittest.TestCase):
    def setUp(self):
        """Set up a new game session for each test."""
        self.session = GameSession()
        self.session.start_game("Human", num_ai=1)
        self.human_player_id = self.session.human_player_id

    def test_golden_path_single_player_single_action(self):
        """
        Tests the simplest possible flow: a single player taking a single valid action.
        This test will guide the initial refactoring of the engine to be stateless.
        """
        # 1. Get the initial state
        initial_state = self.session.state
        self.assertEqual(initial_state.get_current_player().id, self.human_player_id)
        starting_pc = initial_state.get_current_player().pc
        starting_ap = initial_state.get_current_player().action_points

        # 2. Define the action to be taken
        action_to_perform = ActionFundraise(player_id=self.human_player_id)

        # 3. Process the action through the engine
        # This is the target architecture we are building towards.
        # This will fail until we refactor the engine.
        new_state = self.session.engine.process_action(initial_state, action_to_perform)

        # 4. Verify the new state is correct
        self.assertIsInstance(new_state, GameState)
        self.assertNotEqual(initial_state, new_state, "The new state should be a different object.")

        # 5. Verify the player's resources were updated correctly
        player_in_new_state = new_state.get_player_by_id(self.human_player_id)
        # --- VERIFICATION ---
        # The player's PC should have increased by the fundraising amount
        self.assertEqual(player_in_new_state.pc, starting_pc + 5)
        
        # The player's action points should have been deducted
        self.assertEqual(new_state.action_points[self.human_player_id], starting_ap - 1)

        # The turn log in the new state should reflect the action
        self.assertIn("takes the Fundraise action", " ".join(new_state.turn_log))

        # 6. Verify the turn has not advanced
        self.assertEqual(new_state.get_current_player().id, self.human_player_id)

if __name__ == '__main__':
    unittest.main() 