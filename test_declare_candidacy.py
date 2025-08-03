import unittest
from models.game_state import GameState
from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import (
    ActionInitiateDeclareCandidacy,
    ActionSubmitOfficeChoice,
    ActionDeclareCandidacy
)

class TestDeclareCandidacyStateFlow(unittest.TestCase):
    def setUp(self):
        """Set up a new game engine and state for each test."""
        self.game_data = load_game_data()
        self.engine = GameEngine(self.game_data)
        self.state = self.engine.start_new_game(["Human", "AI"])
        self.human_player_id = 0

        # Setup initial game state for testing
        self.state.get_player_by_id(self.human_player_id).pc = 100
        self.state.action_points[self.human_player_id] = 2
        self.state.round_marker = 4 # Candidacy is only allowed in round 4

    def test_full_declare_candidacy_flow(self):
        """
        Tests the complete, multi-step, state-driven flow for declaring candidacy.
        """
        # --- Step 1: Initiate the "Declare Candidacy" action ---
        initiate_action = ActionInitiateDeclareCandidacy(player_id=self.human_player_id)
        current_state = self.engine.process_action(self.state, initiate_action)

        # Verify the state is now awaiting a choice from the user
        self.assertIsNotNone(current_state.pending_ui_action)
        self.assertEqual(current_state.pending_ui_action['action_type'], 'ActionInitiateDeclareCandidacy')
        self.assertEqual(current_state.pending_ui_action['player_id'], self.human_player_id)
        self.assertIn("Which office would you like to run for?", current_state.pending_ui_action['prompt'])
        self.assertGreater(len(current_state.pending_ui_action['options']), 0)
        self.assertEqual(current_state.pending_ui_action['next_action'], 'ActionSubmitOfficeChoice')

        # --- Step 2: Submit the choice of which office to run for ---
        office_to_run_for_id = current_state.pending_ui_action['options'][0]['id']
        office_cost = current_state.pending_ui_action['options'][0]['cost']
        
        starting_pc = self.state.get_player_by_id(self.human_player_id).pc

        office_choice_action = ActionSubmitOfficeChoice(player_id=self.human_player_id, choice=office_to_run_for_id, committed_pc=0)
        current_state = self.engine.process_action(current_state, office_choice_action)

        # Verify the UI interaction is complete and the action has been resolved
        self.assertIsNone(current_state.pending_ui_action)

        # Verify the final game state changes
        final_player = current_state.get_player_by_id(self.human_player_id)
        self.assertEqual(final_player.pc, starting_pc - office_cost)
        self.assertEqual(current_state.action_points[self.human_player_id], 0) # 2 AP should be deducted

        # Verify the candidacy is now declared
        candidacy = next((c for c in current_state.secret_candidacies if c.player_id == self.human_player_id and c.office_id == office_to_run_for_id), None)
        self.assertIsNotNone(candidacy)

        log_text = " ".join(current_state.turn_log)
        office_title = self.game_data['offices'][office_to_run_for_id].title
        self.assertIn(f"pays {office_cost} PC to run for {office_title}", log_text)

if __name__ == '__main__':
    unittest.main() 