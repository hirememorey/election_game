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
        # --- Go straight to the end of the term ---
        self.session.state.round_marker = 4
        
        # Manually sponsor a bill so the legislation phase isn't skipped
        sponsor_action = ActionSponsorLegislation(player_id=self.human_player_id, legislation_id="INFRASTRUCTURE_BILL")
        self.session.process_action(sponsor_action.to_dict())
        
        # Manually exhaust AP for both players to trigger the end of the term
        self.session.state.action_points[self.human_player_id] = 0
        self.session.state.action_points[self.ai_player_id] = 0
        
        # Have the human pass the turn to trigger the upkeep phase
        self.session.process_action({"action_type": "ActionPassTurn", "player_id": self.human_player_id})
        
        # --- VERIFY LEGISLATION PHASE ---
        self.assertEqual(self.session.state.current_phase, "LEGISLATION_PHASE")
        client_state = self.session.get_state_for_client()
        valid_actions = client_state['valid_actions']
        self.assertEqual(len(valid_actions), 1)
        self.assertEqual(valid_actions[0]['action_type'], 'ActionResolveLegislation')
        self.session.process_action(valid_actions[0])

        # --- VERIFY ELECTION PHASE ---
        self.assertEqual(self.session.state.current_phase, "ELECTION_PHASE")
        client_state = self.session.get_state_for_client()
        valid_actions = client_state['valid_actions']
        self.assertEqual(len(valid_actions), 1)
        self.assertEqual(valid_actions[0]['action_type'], 'ActionResolveElections')
        self.session.process_action(valid_actions[0])

        # --- VERIFY ACKNOWLEDGEMENT PHASE ---
        self.assertTrue(self.session.state.awaiting_results_acknowledgement)
        client_state = self.session.get_state_for_client()
        valid_actions = client_state['valid_actions']
        self.assertEqual(len(valid_actions), 1)
        self.assertEqual(valid_actions[0]['action_type'], 'ActionAcknowledgeResults')
        self.session.process_action(valid_actions[0])

        # --- VERIFY NEW TERM STATE ---
        self.assertEqual(self.session.state.term_counter, 1)
        self.assertEqual(self.session.state.round_marker, 1)
        self.assertEqual(self.session.state.current_phase, "ACTION_PHASE")
        self.assertTrue(self.session.is_human_turn())
        for p in self.session.state.players:
            self.assertEqual(self.session.state.action_points[p.id], 2)

if __name__ == '__main__':
    unittest.main() 