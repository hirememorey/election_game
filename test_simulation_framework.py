#!/usr/bin/env python3
"""
Comprehensive Test Suite for Simulation Framework

This test suite validates the simulation framework using first principles
and red-teams all assumptions and conclusions.
"""

import unittest
import random
import time
from typing import List, Dict, Any

from simulation_harness import SimulationHarness, Agent, RandomAgent, SimulationResult
from simulation_runner import SimulationRunner
from personas import RandomPersona, EconomicPersona, LegislativePersona, BalancedPersona
from engine.engine import GameEngine
from models.game_state import GameState
from models.components import Player
from engine.actions import (
    Action, ActionFundraise, ActionNetwork, ActionSponsorLegislation,
    ActionDeclareCandidacy, ActionUseFavor, ActionSupportLegislation,
    ActionOpposeLegislation, ActionPassTurn, ActionResolveLegislation
)
from game_data import load_game_data


class TestAgent(Agent):
    """Test agent that always chooses the first available action."""
    
    def choose_action(self, game_state: GameState, valid_actions: List[Action]) -> Action:
        """Always choose the first action in the list."""
        return valid_actions[0] if valid_actions else ActionPassTurn(player_id=game_state.get_current_player().id)


class TestAgentPassOnly(Agent):
    """Test agent that only passes turn."""
    
    def choose_action(self, game_state: GameState, valid_actions: List[Action]) -> Action:
        """Always pass turn."""
        return ActionPassTurn(player_id=game_state.get_current_player().id)


class TestAgentFundraiseOnly(Agent):
    """Test agent that only fundraises when possible."""
    
    def choose_action(self, game_state: GameState, valid_actions: List[Action]) -> Action:
        """Choose fundraise if available, otherwise pass."""
        for action in valid_actions:
            if isinstance(action, ActionFundraise):
                return action
        return ActionPassTurn(player_id=game_state.get_current_player().id)


class SimulationFrameworkTest(unittest.TestCase):
    """Comprehensive test suite for the simulation framework."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.game_data = load_game_data()
        self.engine = GameEngine(self.game_data)
        self.harness = SimulationHarness()
        
    def test_agent_interface_first_principles(self):
        """Test that agents are pure decision-makers with no side effects."""
        # First principle: Agents should be pure functions
        agent = TestAgent()
        state1 = self.harness.create_game(['Alice', 'Bob'])
        state2 = self.harness.create_game(['Alice', 'Bob'])
        
        # Same state should produce same action
        actions1 = self.engine.get_valid_actions(state1, 0)
        actions2 = self.engine.get_valid_actions(state2, 0)
        
        action1 = agent.choose_action(state1, actions1)
        action2 = agent.choose_action(state2, actions2)
        
        # Red-team: Are agents truly pure?
        self.assertEqual(type(action1), type(action2))
        
    def test_engine_single_source_of_truth(self):
        """Test that engine is the single source of truth for valid actions."""
        # First principle: Only the engine should determine valid actions
        state = self.harness.create_game(['Alice', 'Bob', 'Charlie'])
        
        # Test that get_valid_actions respects action point costs
        player = state.get_player_by_id(0)
        if player:
            original_pc = player.pc
            player.pc = 0  # Player has no PC
            
            valid_actions = self.engine.get_valid_actions(state, 0)
            
            # Red-team: Should not be able to sponsor legislation with 0 PC
            sponsor_actions = [a for a in valid_actions if isinstance(a, ActionSponsorLegislation)]
            self.assertEqual(len(sponsor_actions), 0)
            
            # Test action point validation
            state.action_points[0] = 0
            valid_actions = self.engine.get_valid_actions(state, 0)
            
            # Red-team: Should only have pass turn available
            self.assertEqual(len(valid_actions), 1)
            self.assertIsInstance(valid_actions[0], ActionPassTurn)
        
    def test_action_point_cost_validation(self):
        """Test that action point costs are properly validated."""
        # First principle: Action costs must be enforced consistently
        state = self.harness.create_game(['Alice', 'Bob'])
        
        # Test base costs
        state.action_points[0] = 1
        valid_actions = self.engine.get_valid_actions(state, 0)
        
        # Red-team: 1 AP should allow fundraise/network but not sponsor legislation
        fundraise_actions = [a for a in valid_actions if isinstance(a, ActionFundraise)]
        network_actions = [a for a in valid_actions if isinstance(a, ActionNetwork)]
        sponsor_actions = [a for a in valid_actions if isinstance(a, ActionSponsorLegislation)]
        
        self.assertGreater(len(fundraise_actions), 0)
        self.assertGreater(len(network_actions), 0)
        self.assertEqual(len(sponsor_actions), 0)
        
        # Test public gaffe effect
        state.public_gaffe_players.add(0)
        state.action_points[0] = 2
        valid_actions = self.engine.get_valid_actions(state, 0)
        
        # Red-team: Public gaffe should increase sponsor legislation cost to 3 AP
        sponsor_actions = [a for a in valid_actions if isinstance(a, ActionSponsorLegislation)]
        self.assertEqual(len(sponsor_actions), 0)  # 2 AP not enough for 3 AP cost
        
    def test_system_action_handling(self):
        """Test that system actions are handled correctly."""
        # First principle: System actions should be processed automatically
        state = self.harness.create_game(['Alice', 'Bob'])
        
        # Simulate end of term
        state.awaiting_legislation_resolution = True
        system_actions = self.engine.get_valid_system_actions(state)
        
        # Red-team: Should have system action available
        self.assertGreater(len(system_actions), 0)
        self.assertIsInstance(system_actions[0], ActionResolveLegislation)
        
    def test_simulation_completeness(self):
        """Test that simulations complete properly."""
        # First principle: Simulations must complete and produce valid results
        agents = [TestAgentPassOnly() for _ in range(3)]
        result = self.harness.run_simulation(agents, ['Alice', 'Bob', 'Charlie'])
        
        # Red-team: Should have valid result structure
        self.assertIsInstance(result, SimulationResult)
        self.assertIsInstance(result.winner_id, (int, type(None)))
        self.assertIsInstance(result.winner_name, (str, type(None)))
        self.assertIsInstance(result.game_length_rounds, int)
        self.assertIsInstance(result.game_length_terms, int)
        self.assertIsInstance(result.final_scores, dict)
        self.assertIsInstance(result.simulation_time_seconds, float)
        
        # Red-team: Should complete in reasonable time
        self.assertLess(result.simulation_time_seconds, 10.0)
        
    def test_game_state_integrity(self):
        """Test that game state remains consistent throughout simulation."""
        # First principle: Game state must remain internally consistent
        state = self.harness.create_game(['Alice', 'Bob'])
        
        # Test initial state
        self.assertEqual(len(state.players), 2)
        self.assertGreater(len(state.legislation_options), 0)
        self.assertGreater(len(state.offices), 0)
        
        # Test action point initialization
        for player in state.players:
            self.assertEqual(state.action_points[player.id], 2)
            
    def test_action_validation_robustness(self):
        """Test that action validation is robust against edge cases."""
        # First principle: System must handle all edge cases gracefully
        
        # Test with invalid player ID
        state = self.harness.create_game(['Alice', 'Bob'])
        valid_actions = self.engine.get_valid_actions(state, 999)  # Invalid player ID
        self.assertEqual(len(valid_actions), 0)
        
        # Test with wrong player's turn
        state.current_player_index = 1
        valid_actions = self.engine.get_valid_actions(state, 0)  # Player 0's turn but player 1 is current
        self.assertEqual(len(valid_actions), 0)
        
    def test_agent_decision_consistency(self):
        """Test that agents make consistent decisions given same inputs."""
        # First principle: Deterministic agents should produce same results
        agent = TestAgentFundraiseOnly()
        state = self.harness.create_game(['Alice', 'Bob'])
        
        # Set up same conditions
        state.action_points[0] = 1
        player = state.get_player_by_id(0)
        if player:
            player.pc = 25
            
            valid_actions = self.engine.get_valid_actions(state, 0)
            action1 = agent.choose_action(state, valid_actions)
            action2 = agent.choose_action(state, valid_actions)
            
            # Red-team: Same inputs should produce same outputs
            self.assertEqual(type(action1), type(action2))
            
    def test_simulation_determinism(self):
        """Test that simulations are deterministic with deterministic agents."""
        # First principle: Deterministic inputs should produce deterministic outputs
        agents = [TestAgentPassOnly() for _ in range(2)]
        
        # Run same simulation twice
        result1 = self.harness.run_simulation(agents, ['Alice', 'Bob'])
        result2 = self.harness.run_simulation(agents, ['Alice', 'Bob'])
        
        # Red-team: Should produce same results
        self.assertEqual(result1.game_length_rounds, result2.game_length_rounds)
        self.assertEqual(result1.game_length_terms, result2.game_length_terms)
        
    def test_performance_scalability(self):
        """Test that framework scales to multiple agents."""
        # First principle: System should handle any number of agents
        for num_players in [2, 3, 4]:
            agents = [TestAgentPassOnly() for _ in range(num_players)]
            start_time = time.time()
            
            result = self.harness.run_simulation(agents)
            
            # Red-team: Should complete in reasonable time regardless of player count
            self.assertLess(time.time() - start_time, 5.0)
            self.assertEqual(len(result.final_scores), num_players)
            
    def test_error_handling(self):
        """Test that framework handles errors gracefully."""
        # First principle: System must be robust against failures
        
        # Test with invalid agent
        class InvalidAgent(Agent):
            def choose_action(self, game_state: GameState, valid_actions: List[Action]) -> Action:
                raise Exception("Agent error")
        
        agents = [InvalidAgent(), TestAgentPassOnly()]
        
        # Red-team: Should handle agent errors gracefully
        with self.assertRaises(Exception):
            self.harness.run_simulation(agents, ['Alice', 'Bob'])
            
    def test_action_point_arithmetic(self):
        """Test that action point arithmetic is correct."""
        # First principle: Action point costs must be mathematically correct
        state = self.harness.create_game(['Alice', 'Bob'])
        
        # Test that action points are properly deducted
        initial_ap = state.action_points[0]
        action = ActionFundraise(player_id=0)
        
        # Process action
        new_state = self.engine.process_action(state, action)
        
        # Red-team: Action point should be deducted correctly
        expected_ap = initial_ap - self.engine.action_point_costs["ActionFundraise"]
        self.assertEqual(new_state.action_points[0], expected_ap)
        
    def test_legislation_sponsoring_logic(self):
        """Test that legislation sponsoring follows correct rules."""
        # First principle: Legislation sponsoring must follow game rules
        state = self.harness.create_game(['Alice', 'Bob'])
        
        # Test PC requirement
        player = state.get_player_by_id(0)
        if player:
            original_pc = player.pc
            
            # Set PC below minimum
            player.pc = 4  # Below minimum of 5
            
            valid_actions = self.engine.get_valid_actions(state, 0)
            sponsor_actions = [a for a in valid_actions if isinstance(a, ActionSponsorLegislation)]
            
            # Red-team: Should not be able to sponsor with insufficient PC
            self.assertEqual(len(sponsor_actions), 0)
            
            # Test with sufficient PC
            player.pc = 10
            valid_actions = self.engine.get_valid_actions(state, 0)
            sponsor_actions = [a for a in valid_actions if isinstance(a, ActionSponsorLegislation)]
            
            # Red-team: Should be able to sponsor with sufficient PC
            self.assertGreater(len(sponsor_actions), 0)
            
    def test_candidacy_declaration_timing(self):
        """Test that candidacy declaration follows timing rules."""
        # First principle: Candidacy declaration must follow timing rules
        state = self.harness.create_game(['Alice', 'Bob'])
        
        # Test that candidacy is only available in round 4
        for round_num in [1, 2, 3]:
            state.round_marker = round_num
            valid_actions = self.engine.get_valid_actions(state, 0)
            candidacy_actions = [a for a in valid_actions if isinstance(a, ActionDeclareCandidacy)]
            
            # Red-team: Should not be available before round 4
            self.assertEqual(len(candidacy_actions), 0)
            
        # Test round 4 - but only if player has sufficient PC for candidacy
        state.round_marker = 4
        player = state.get_player_by_id(0)
        if player:
            # Set player PC to ensure they can afford candidacy
            player.pc = 25  # Should be enough for any office
            
            valid_actions = self.engine.get_valid_actions(state, 0)
            candidacy_actions = [a for a in valid_actions if isinstance(a, ActionDeclareCandidacy)]
            
            # Red-team: Should be available in round 4 if player has sufficient PC
            self.assertGreater(len(candidacy_actions), 0)
        
    def test_final_scores_structure(self):
        """Test that final scores have correct structure."""
        # First principle: Final scores must have consistent structure
        agents = [TestAgentPassOnly() for _ in range(2)]
        result = self.harness.run_simulation(agents, ['Alice', 'Bob'])
        
        # Red-team: Final scores should have expected structure
        self.assertIsInstance(result.final_scores, dict)
        for player_id, score in result.final_scores.items():
            self.assertIsInstance(player_id, int)
            self.assertIsInstance(score, int)
            
    def test_simulation_termination(self):
        """Test that simulations terminate properly."""
        # First principle: Simulations must terminate
        agents = [TestAgentPassOnly() for _ in range(2)]
        
        # Test with reasonable max_rounds
        result = self.harness.run_simulation(agents, ['Alice', 'Bob'], max_rounds=50)
        
        # Red-team: Should complete within max_rounds
        self.assertLessEqual(result.game_length_rounds, 50)
        
        # Test with very low max_rounds
        result = self.harness.run_simulation(agents, ['Alice', 'Bob'], max_rounds=5)
        self.assertLessEqual(result.game_length_rounds, 5)
        
    def test_new_personas(self):
        """Test that the new persona system works correctly."""
        # Test that all personas can be created and used
        personas = [
            RandomPersona("Test Random"),
            EconomicPersona("Test Economic"),
            LegislativePersona("Test Legislative"),
            BalancedPersona("Test Balanced")
        ]
        
        # Test that each persona can make decisions
        state = self.harness.create_game(['Alice', 'Bob'])
        valid_actions = self.engine.get_valid_actions(state, 0)
        
        for persona in personas:
            action = persona.choose_action(state, valid_actions)
            self.assertIsInstance(action, Action)
            
    def test_simulation_runner(self):
        """Test that the simulation runner works correctly."""
        # Test that the simulation runner can be initialized
        runner = SimulationRunner()
        
        # Test that it can create agents
        agents = runner._create_player_agents()
        self.assertEqual(len(agents), 4)  # Default config has 4 players
        
        # Test that all agents are personas
        for agent in agents:
            self.assertIsInstance(agent, (RandomPersona, EconomicPersona, LegislativePersona, BalancedPersona))


def run_comprehensive_tests():
    """Run all comprehensive tests."""
    print("Running Comprehensive Simulation Framework Tests...")
    print("=" * 60)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(SimulationFrameworkTest)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"\n{test}:")
            print(traceback)
            
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"\n{test}:")
            print(traceback)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1) 