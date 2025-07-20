#!/usr/bin/env python3
"""
Simulation Harness for Election Game

This module provides a headless simulation environment for running games
programmatically without the web server. It's designed to support agent-based
simulation for game balance analysis.
"""

import random
import time
from typing import List, Dict, Any, Optional, Callable, Sequence
from dataclasses import dataclass
from abc import ABC, abstractmethod

from engine.engine import GameEngine
from models.game_state import GameState
from models.components import Player
from engine.actions import (
    Action, ActionFundraise, ActionNetwork, ActionSponsorLegislation,
    ActionDeclareCandidacy, ActionUseFavor, ActionSupportLegislation,
    ActionOpposeLegislation, ActionPassTurn, ActionResolveLegislation,
    ActionResolveElections, ActionAcknowledgeResults
)
from game_data import load_game_data


class Agent(ABC):
    """
    Abstract base class for all game agents.
    
    Agents are pure decision-makers that choose actions from a pre-validated list.
    They should not be responsible for figuring out what actions are possible.
    """
    
    @abstractmethod
    def choose_action(self, game_state: GameState, valid_actions: List[Action]) -> Action:
        """
        Choose an action from the list of valid actions.
        
        Args:
            game_state: Current game state
            valid_actions: List of valid actions to choose from
            
        Returns:
            Action: The chosen action
        """
        pass


class RandomAgent(Agent):
    """
    A simple agent that chooses actions randomly from available options.
    Provides baseline performance for comparison.
    """
    
    def choose_action(self, game_state: GameState, valid_actions: List[Action]) -> Action:
        """Choose a random action from the valid actions list."""
        return random.choice(valid_actions)


@dataclass
class SimulationResult:
    """Results from a single game simulation."""
    winner_id: Optional[int]
    winner_name: Optional[str]
    game_length_rounds: int
    game_length_terms: int
    final_scores: Dict[int, int]
    game_log: List[str]
    simulation_time_seconds: float


class SimulationHarness:
    """
    A headless simulation environment for running Election games programmatically.
    
    This class provides the infrastructure needed to run thousands of games
    quickly for balance analysis and agent testing.
    """
    
    def __init__(self):
        """Initialize the simulation harness with game data and engine."""
        self.game_data = load_game_data()
        self.engine = GameEngine(self.game_data)
        
    def create_game(self, player_names: List[str]) -> GameState:
        """
        Create a new game state with the specified players.
        
        Args:
            player_names: List of player names (2-4 players)
            
        Returns:
            GameState: The initial game state
            
        Raises:
            ValueError: If invalid number of players
        """
        if len(player_names) < 2 or len(player_names) > 4:
            raise ValueError("Game requires 2-4 players")
            
        # Create new game state
        game_state = self.engine.start_new_game(player_names)
        
        # Run the first event phase immediately
        game_state = self.engine.run_event_phase(game_state)
        
        return game_state
    
    def run_simulation(self, 
                      player_agents: Sequence[Agent],
                      player_names: Optional[List[str]] = None,
                      max_rounds: int = 100,
                      verbose: bool = False) -> SimulationResult:
        """
        Run a complete game simulation with the specified agents.
        
        Args:
            player_agents: List of agent objects, one per player
            player_names: Optional list of player names (defaults to Agent 0, Agent 1, etc.)
            max_rounds: Maximum number of rounds to prevent infinite loops
            verbose: Whether to print detailed game progress
            
        Returns:
            SimulationResult: Complete results of the simulation
        """
        start_time = time.time()
        
        # Set up player names if not provided
        if player_names is None:
            player_names = [f"Agent {i}" for i in range(len(player_agents))]
        
        # Create the game
        state = self.create_game(player_names)
        
        if verbose:
            print(f"Starting simulation with {len(player_agents)} players: {player_names}")
        
        round_count = 0
        term_count = 0
        
        # Main game loop
        while not self.engine.is_game_over(state) and round_count < max_rounds:
            round_count += 1
            
            if verbose:
                print(f"\n--- Round {round_count} ---")
                print(f"Current player: {state.get_current_player().name}")
                print(f"Phase: {state.current_phase}")
                print(f"Action Points: {state.action_points}")
            
            # Check for system actions first
            system_actions = self.engine.get_valid_system_actions(state)
            if system_actions:
                # Process the first system action
                action = system_actions[0]
                if verbose:
                    print(f"System action: {action.__class__.__name__}")
                
                # Handle system actions directly
                if isinstance(action, ActionResolveLegislation):
                    state = self.engine.resolve_legislation_session(state)
                elif isinstance(action, ActionResolveElections):
                    state = self.engine.resolve_elections_session(state)
                elif isinstance(action, ActionAcknowledgeResults):
                    state = self.engine.start_next_term(state)
                continue
            
            # Handle player actions
            if state.current_phase == "ACTION_PHASE":
                current_player_id = state.get_current_player().id
                agent = player_agents[current_player_id]
                
                # Get valid actions from the engine
                valid_actions = self.engine.get_valid_actions(state, current_player_id)
                
                if not valid_actions:
                    if verbose:
                        print(f"No valid actions for {state.get_current_player().name}")
                    # Force pass turn
                    action = ActionPassTurn(player_id=current_player_id)
                else:
                    # Let the agent choose an action
                    action = agent.choose_action(state, valid_actions)
                    
                    # Validate the chosen action is in the valid list
                    if action not in valid_actions:
                        if verbose:
                            print(f"Agent chose invalid action: {action}")
                        # Fall back to pass turn
                        action = ActionPassTurn(player_id=current_player_id)
                
                if verbose:
                    print(f"{state.get_current_player().name} chose: {action.__class__.__name__}")
                
                # Process the action through the engine
                state = self.engine.process_action(state, action)
            
            # Track term transitions
            if state.round_marker == 1 and round_count > 1:
                term_count += 1
                if verbose:
                    print(f"\n--- Term {term_count} Complete ---")
        
        # Calculate final results
        simulation_time = time.time() - start_time
        final_scores_data = self.engine.get_final_scores(state)
        
        # Determine winner
        winner_id = final_scores_data.get('winner_id')
        winner_name = final_scores_data.get('winner_name')
        final_scores = final_scores_data.get('scores', {})
        
        return SimulationResult(
            winner_id=winner_id,
            winner_name=winner_name,
            game_length_rounds=round_count,
            game_length_terms=term_count,
            final_scores=final_scores,
            game_log=state.turn_log,
            simulation_time_seconds=simulation_time
        )


def create_random_agent() -> Agent:
    """Create a random agent for testing."""
    return RandomAgent()


def test_simulation_harness():
    """Test the simulation harness with random agents."""
    print("Testing Simulation Harness...")
    
    # Create agents
    agents = [RandomAgent() for _ in range(4)]
    player_names = ['Alice', 'Bob', 'Charlie', 'Diana']
    
    # Create harness and run simulation
    harness = SimulationHarness()
    result = harness.run_simulation(agents, player_names, verbose=True)
    
    print(f"\n--- Simulation Complete ---")
    print(f"Winner: {result.winner_name}")
    print(f"Rounds: {result.game_length_rounds}, Terms: {result.game_length_terms}")
    print(f"Final Scores: {result.final_scores}")
    print(f"Simulation Time: {result.simulation_time_seconds:.3f}s")
    
    return result


if __name__ == "__main__":
    test_simulation_harness() 