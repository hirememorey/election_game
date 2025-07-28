import unittest
from game_session import GameSession
from engine.ui_actions import UISponsorLegislation
from engine.actions import ActionSponsorLegislation

class TestGameSession(unittest.TestCase):
    def setUp(self):
        self.session = GameSession()
        self.session.start_game("Human", num_ai=1)
        self.human_player_id = self.session.human_player_id

    def test_sponsor_legislation_flow(self):
        # Set the turn to the human player for a clean test environment
        self.session.state.current_player_index = self.human_player_id
        
        # Snapshot starting PC
        starting_pc = self.session.state.get_current_player().pc

        # Step 1: Human player initiates sponsoring legislation
        ui_action_data = UISponsorLegislation(player_id=self.human_player_id).to_dict()
        self.session.process_action(ui_action_data)
        
        # Step 2: Human player chooses a specific bill to sponsor
        client_state = self.session.get_state_for_client()
        first_option = client_state['valid_actions'][0]
        choice_data = { "player_id": self.human_player_id, "choice": first_option['id'] }
        
        # Process the choice. We need to manually stop the AI from running.
        # To do this, we can call the internal _execute_action method directly.
        action = self.session.engine.action_from_dict({
            'action_type': 'ActionSponsorLegislation',
            'player_id': self.human_player_id,
            'legislation_id': first_option['id']
        })
        self.session.state = self.session.engine.process_action(self.session.state, action)
        
        # Verify the action was successful
        log_text = " ".join(self.session.state.turn_log)
        self.assertIn("sponsors the", log_text, "The log should contain the sponsorship message.")
        
        # Check that the player's PC was deducted correctly
        player = self.session.state.get_player_by_id(self.human_player_id)
        bill_id = first_option['id']
        bill_cost = self.session.state.legislation_options[bill_id].cost
        self.assertEqual(player.pc, starting_pc - bill_cost)

if __name__ == '__main__':
    unittest.main() 