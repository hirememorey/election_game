import unittest
from models.game_state import GameState
from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import (
    ActionInitiateSponsorLegislation,
    ActionSubmitLegislationChoice,
    ActionSponsorLegislation
)

class TestSponsorLegislationStateFlow(unittest.TestCase):
    def setUp(self):
        """Set up a new game engine and state for each test."""
        self.game_data = load_game_data()
        self.engine = GameEngine(self.game_data)
        self.state = self.engine.start_new_game(["Human", "AI"])
        self.human_player_id = 0

        # Setup initial game state for testing
        self.state.get_player_by_id(self.human_player_id).pc = 100
        self.state.action_points[self.human_player_id] = 2

    def test_full_sponsor_legislation_flow(self):
        """
        Tests the complete, multi-step, state-driven flow for sponsoring legislation.
        """
        # --- Step 1: Initiate the "Sponsor Legislation" action ---
        initiate_action = ActionInitiateSponsorLegislation(player_id=self.human_player_id)
        current_state = self.engine.process_action(self.state, initiate_action)

        # Verify the state is now awaiting a choice from the user
        self.assertIsNotNone(current_state.pending_ui_action)
        self.assertEqual(current_state.pending_ui_action['action_type'], 'ActionInitiateSponsorLegislation')
        self.assertEqual(current_state.pending_ui_action['player_id'], self.human_player_id)
        self.assertIn("Which bill would you like to sponsor?", current_state.pending_ui_action['prompt'])
        self.assertGreater(len(current_state.pending_ui_action['options']), 0)
        self.assertEqual(current_state.pending_ui_action['next_action'], 'ActionSubmitLegislationChoice')

        # --- Step 2: Submit the choice of which legislation to sponsor ---
        # Get the first available bill to sponsor
        bill_to_sponsor_id = current_state.pending_ui_action['options'][0]['id']
        bill_cost = current_state.pending_ui_action['options'][0]['cost']
        
        starting_pc = self.state.get_player_by_id(self.human_player_id).pc

        bill_choice_action = ActionSubmitLegislationChoice(player_id=self.human_player_id, choice=bill_to_sponsor_id)
        current_state = self.engine.process_action(current_state, bill_choice_action)

        # Verify the UI interaction is complete and the action has been resolved
        self.assertIsNone(current_state.pending_ui_action)

        # Verify the final game state changes
        final_player = current_state.get_player_by_id(self.human_player_id)
        self.assertEqual(final_player.pc, starting_pc - bill_cost)
        self.assertEqual(current_state.action_points[self.human_player_id], 0) # 2 AP should be deducted

        # Verify the bill is now sponsored
        active_bill = current_state.get_legislation_by_id(bill_to_sponsor_id)
        self.assertIsNotNone(active_bill)
        self.assertEqual(active_bill.sponsor_id, self.human_player_id)

        log_text = " ".join(current_state.turn_log)
        bill_title = self.game_data['legislation'][bill_to_sponsor_id].title
        self.assertIn(f"Human sponsors the {bill_title}", log_text)

if __name__ == '__main__':
    unittest.main() 