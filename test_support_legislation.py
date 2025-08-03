import unittest
from models.game_state import GameState, PendingLegislation
from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import (
    ActionSponsorLegislation,
    ActionInitiateSupportLegislation,
    ActionSubmitLegislationChoice,
    ActionSubmitAmount,
    ActionSupportLegislation
)

class TestSupportLegislationStateFlow(unittest.TestCase):
    def setUp(self):
        """Set up a new game engine and state for each test."""
        self.game_data = load_game_data()
        self.engine = GameEngine(self.game_data)
        self.state = self.engine.start_new_game(["Human", "AI"])
        self.human_player_id = 0

        # Setup initial game state for testing
        self.state.get_player_by_id(self.human_player_id).pc = 100
        self.state.action_points[self.human_player_id] = 2
        
        # Sponsor a bill to have something to support
        sponsor_action = ActionSponsorLegislation(player_id=self.human_player_id, legislation_id="INFRASTRUCTURE")
        self.state = self.engine.process_action(self.state, sponsor_action)
        self.state.get_player_by_id(self.human_player_id).pc = 100 # Reset PC for predictability
        self.state.action_points[self.human_player_id] = 2 # Reset AP

    def test_full_support_legislation_flow(self):
        """
        Tests the complete, multi-step, state-driven flow for supporting legislation.
        """
        # --- Step 1: Initiate the "Support Legislation" action ---
        initiate_action = ActionInitiateSupportLegislation(player_id=self.human_player_id)
        current_state = self.engine.process_action(self.state, initiate_action)
        
        # Verify the state is now awaiting a choice from the user
        self.assertIsNotNone(current_state.pending_ui_action)
        self.assertEqual(current_state.pending_ui_action['action_type'], 'ActionInitiateSupportLegislation')
        self.assertEqual(current_state.pending_ui_action['player_id'], self.human_player_id)
        self.assertIn("Which bill would you like to secretly support?", current_state.pending_ui_action['prompt'])
        self.assertEqual(len(current_state.pending_ui_action['options']), 1)
        self.assertEqual(current_state.pending_ui_action['options'][0]['id'], 'INFRASTRUCTURE')
        self.assertEqual(current_state.pending_ui_action['next_action'], 'ActionSubmitLegislationChoice')

        # --- Step 2: Submit the choice of which legislation to support ---
        bill_choice_action = ActionSubmitLegislationChoice(player_id=self.human_player_id, choice='INFRASTRUCTURE')
        current_state = self.engine.process_action(current_state, bill_choice_action)

        # Verify the state is now awaiting an amount from the user
        self.assertIsNotNone(current_state.pending_ui_action)
        self.assertEqual(current_state.pending_ui_action['action_type'], 'ActionSubmitLegislationChoice')
        self.assertEqual(current_state.pending_ui_action['player_id'], self.human_player_id)
        self.assertEqual(current_state.pending_ui_action['selected_legislation'], 'INFRASTRUCTURE')
        self.assertIn("How much Political Capital (PC) will you secretly commit to support the INFRASTRUCTURE? (1-100)", current_state.pending_ui_action['prompt'])
        self.assertEqual(current_state.pending_ui_action['next_action'], 'ActionSubmitAmount')

        # --- Step 3: Submit the amount of PC to commit ---
        starting_pc = self.state.get_player_by_id(self.human_player_id).pc
        amount_action = ActionSubmitAmount(player_id=self.human_player_id, amount=25)
        current_state = self.engine.process_action(current_state, amount_action)

        # Verify the UI interaction is complete and the action has been resolved
        self.assertIsNone(current_state.pending_ui_action)
        
        # Verify the final game state changes
        final_player = current_state.get_player_by_id(self.human_player_id)
        self.assertEqual(final_player.pc, starting_pc - 25)
        self.assertEqual(current_state.action_points[self.human_player_id], 1) # 1 AP should be deducted

        # Verify the secret commitment was recorded
        active_bill = current_state.get_legislation_by_id("INFRASTRUCTURE")
        self.assertIsNotNone(active_bill)
        self.assertEqual(active_bill.support_players[self.human_player_id], 25)
        
        log_text = " ".join(current_state.turn_log)
        self.assertIn(f"Human makes a commitment to the Infrastructure Bill.", log_text)

if __name__ == '__main__':
    unittest.main() 