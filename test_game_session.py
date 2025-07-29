import unittest
from game_session import GameSession
from engine.ui_actions import UISponsorLegislation
from engine.actions import ActionSponsorLegislation
from engine.ui_actions import UIDeclareCandidacy
from engine.actions import ActionDeclareCandidacy

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

    def test_declare_candidacy_flow(self):
        # Set the game to round 4
        self.session.state.round_marker = 4
        self.session.state.current_player_index = self.human_player_id
        starting_pc = self.session.state.get_current_player().pc

        # Step 1: Human initiates declaring candidacy
        ui_action_data = UIDeclareCandidacy(player_id=self.human_player_id).to_dict()
        self.session.process_action(ui_action_data)

        # Step 2: Human chooses an office
        client_state = self.session.get_state_for_client()
        first_option = client_state['valid_actions'][0]
        choice_data = {"player_id": self.human_player_id, "choice": first_option['id']}

        action = self.session.engine.action_from_dict({
            'action_type': 'ActionDeclareCandidacy',
            'player_id': self.human_player_id,
            'office_id': first_option['id'],
            'committed_pc': 0
        })
        self.session.state = self.session.engine.process_action(self.session.state, action)

        # Verify the action was successful
        player = self.session.state.get_player_by_id(self.human_player_id)
        office_id = first_option['id']
        office_cost = self.session.state.offices[office_id].candidacy_cost
        office_title = self.session.state.offices[office_id].title

        log_text = " ".join(self.session.state.turn_log)
        expected_log = f"pays {office_cost} PC to run for {office_title}"
        self.assertIn(expected_log, log_text)
        self.assertEqual(player.pc, starting_pc - office_cost)

if __name__ == '__main__':
    unittest.main() 