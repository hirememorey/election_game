import unittest
from game_session import GameSession
from engine.actions import ActionSponsorLegislation, ActionDeclareCandidacy, ActionResolveLegislation, ActionResolveElections, ActionAcknowledgeResults, ActionFundraise

class TestTermFlow(unittest.TestCase):
    def setUp(self):
        self.session = GameSession()
        self.session.start_game("Human", num_ai=1)
        self.human_player_id = self.session.human_player_id
        self.ai_player_id = 1

    def test_full_term_to_term_transition(self):
        """
        Tests the complete flow from an active term, through all resolution phases,
        and into the beginning of the next term using an explicit, state-aware method.
        """
        # --- SETUP: Go to the final turn of the term with a clean state ---
        self.session.state.term_counter = 0
        self.session.state.round_marker = 4
        self.session.state.current_player_index = self.human_player_id
        self.session.state.action_points[self.human_player_id] = 2
        self.session.state.action_points[self.ai_player_id] = 2
        self.session.state.get_player_by_id(self.human_player_id).pc = 20 # Ensure enough PC

        # --- ACTION: Process turns directly through the engine for determinism ---
        
        # 1. Human player sponsors a bill (uses 1 AP), then fundraises (uses 1 AP)
        sponsor_action = ActionSponsorLegislation(player_id=self.human_player_id, legislation_id="INFRASTRUCTURE")
        self.session.state = self.session.engine.process_action(self.session.state, sponsor_action)
        self.assertEqual(self.session.state.action_points[self.human_player_id], 1, "AP should be 1 after sponsoring.")
        self.assertEqual(len(self.session.state.term_legislation), 1)

        fundraise_action = ActionFundraise(player_id=self.human_player_id)
        self.session.state = self.session.engine.process_action(self.session.state, fundraise_action)
        self.assertEqual(self.session.state.action_points[self.human_player_id], 0, "AP should be 0 after fundraising.")

        # Manually advance to the AI's turn
        self.session.state = self.session.engine._check_and_advance_turn(self.session.state)
        self.assertEqual(self.session.state.get_current_player().id, self.ai_player_id)

        # 2. AI player fundraises twice
        fundraise_action_ai = ActionFundraise(player_id=self.ai_player_id)
        self.session.state = self.session.engine.process_action(self.session.state, fundraise_action_ai)
        self.session.state = self.session.engine.process_action(self.session.state, fundraise_action_ai)
        self.assertEqual(self.session.state.action_points[self.ai_player_id], 0)

        # 3. Trigger upkeep, which should now happen automatically
        self.session.state = self.session.engine._check_and_trigger_upkeep(self.session.state)
        
        # --- VERIFY LEGISLATION PHASE ---
        self.assertEqual(self.session.state.current_phase, "LEGISLATION_PHASE")
        self.assertTrue(self.session.state.awaiting_legislation_resolution)
        
        # Manually resolve the legislation session
        self.session.state = self.session.engine.resolve_legislation_session(self.session.state)

        # --- VERIFY ELECTION PHASE ---
        self.assertEqual(self.session.state.current_phase, "ELECTION_PHASE")
        self.assertTrue(self.session.state.awaiting_election_resolution)
        
        # Manually resolve the election session
        self.session.state = self.session.engine.resolve_elections_session(self.session.state, disable_dice_roll=True)

        # --- VERIFY ACKNOWLEDGEMENT PHASE ---
        self.assertTrue(self.session.state.awaiting_results_acknowledgement)
        
        # Manually acknowledge the results to start the new term
        self.session.state = self.session.engine.start_next_term(self.session.state)

        # --- VERIFY NEW TERM STATE ---
        self.assertEqual(self.session.state.term_counter, 1)
        self.assertEqual(self.session.state.round_marker, 1)
        self.assertEqual(self.session.state.current_phase, "ACTION_PHASE")
        self.assertTrue(self.session.is_human_turn())
        for p in self.session.state.players:
            self.assertEqual(self.session.state.action_points[p.id], 2)

if __name__ == '__main__':
    unittest.main() 