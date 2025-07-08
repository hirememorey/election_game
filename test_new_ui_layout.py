import unittest
import json
from server import app, active_games
from engine.engine import GameEngine
from game_data import load_game_data

class TestNewUILayout(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        # No need to set app.testing = True, test_client() does this.
        # Manually clear the games dictionary before each test
        active_games.clear()

    def test_full_game_flow_with_new_ui(self):
        # 1. Start a new game
        player_names = ["Alice", "Bob"]
        response = self.app.post('/api/game', 
                                 data=json.dumps({'player_names': player_names}),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)
        game_data = json.loads(response.data)
        game_id = game_data['game_id'] # Correct key from server response
        state = game_data['state']

        self.assertIn('players', state)
        self.assertEqual(len(state['players']), 2)
        self.assertEqual(state['players'][0]['name'], 'Alice')

        # 2. Have a player perform an action (fundraise)
        current_player_id = state['players'][state['current_player_index']]['id']
        action_data = {
            'action_type': 'fundraise',
            'player_id': current_player_id
        }
        response = self.app.post(f'/api/game/{game_id}/action',
                                 data=json.dumps(action_data),
                                 content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        new_game_data = json.loads(response.data)
        new_state = new_game_data['state']

        # 3. Check if the game state updated correctly
        self.assertNotEqual(state['action_points'], new_state['action_points'])
        
        original_pc = state['players'][0]['pc']
        updated_pc = new_state['players'][0]['pc']
        self.assertTrue(updated_pc > original_pc)

        expected_log_message = f"{player_names[0]} takes the Fundraise action and gains 5 PC."
        self.assertIn(expected_log_message, new_state['turn_log'])

if __name__ == '__main__':
    unittest.main() 