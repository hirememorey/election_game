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


class MetricsLogger(ABC):
    """
    Abstract base class for logging simulation metrics.
    
    This separates the concerns of running the simulation from recording data about it.
    Different loggers can be used for different purposes: verbose console output,
    silent operation for speed, database logging for analysis, etc.
    """
    
    @abstractmethod
    def log_start(self, state: GameState) -> None:
        """Log the start of a simulation."""
        pass
    
    @abstractmethod
    def log_action(self, action: Action, new_state: GameState) -> None:
        """Log an action taken and the resulting state."""
        pass
    
    @abstractmethod
    def log_round_end(self, state: GameState, round_number: int) -> None:
        """Log the end of a round."""
        pass
    
    @abstractmethod
    def log_term_end(self, state: GameState, term_number: int) -> None:
        """Log the end of a term."""
        pass
    
    @abstractmethod
    def finalize(self, final_state: GameState, simulation_time: float) -> 'SimulationResult':
        """Finalize the logging and return the simulation results."""
        pass


class VerboseLogger(MetricsLogger):
    """
    A logger that prints detailed information to the console.
    Useful for debugging and understanding game flow.
    """
    
    def __init__(self):
        self.round_count = 0
        self.term_count = 0
        self.game_log = []
    
    def log_start(self, state: GameState) -> None:
        player_names = [p.name for p in state.players]
        print(f"Starting simulation with {len(state.players)} players: {player_names}")
    
    def log_action(self, action: Action, new_state: GameState) -> None:
        current_player = new_state.get_current_player()
        print(f"{current_player.name} chose: {action.__class__.__name__}")
    
    def log_round_end(self, state: GameState, round_number: int) -> None:
        self.round_count = round_number
        print(f"\n--- Round {round_number} ---")
        print(f"Current player: {state.get_current_player().name}")
        print(f"Phase: {state.current_phase}")
        print(f"Action Points: {state.action_points}")
    
    def log_term_end(self, state: GameState, term_number: int) -> None:
        self.term_count = term_number
        print(f"\n--- Term {term_number} Complete ---")
    
    def finalize(self, final_state: GameState, simulation_time: float) -> 'SimulationResult':
        final_scores_data = GameEngine(load_game_data()).get_final_scores(final_state)
        
        winner_id = final_scores_data.get('winner_id')
        winner_name = final_scores_data.get('winner_name')
        final_scores = final_scores_data.get('scores', {})
        
        print(f"\n--- Simulation Complete ---")
        print(f"Winner: {winner_name}")
        print(f"Rounds: {self.round_count}, Terms: {self.term_count}")
        print(f"Final Scores: {final_scores}")
        print(f"Simulation Time: {simulation_time:.3f}s")
        
        return SimulationResult(
            winner_id=winner_id,
            winner_name=winner_name,
            game_length_rounds=self.round_count,
            game_length_terms=self.term_count,
            final_scores=final_scores,
            game_log=final_state.turn_log,
            simulation_time_seconds=simulation_time,
            final_state=final_state
        )


class SilentLogger(MetricsLogger):
    """
    A logger that records data silently for maximum speed.
    Useful for running thousands of simulations for analysis.
    """
    
    def __init__(self):
        self.round_count = 0
        self.term_count = 0
        self.game_log = []
    
    def log_start(self, state: GameState) -> None:
        pass
    
    def log_action(self, action: Action, new_state: GameState) -> None:
        pass
    
    def log_round_end(self, state: GameState, round_number: int) -> None:
        self.round_count = round_number
    
    def log_term_end(self, state: GameState, term_number: int) -> None:
        self.term_count = term_number
    
    def finalize(self, final_state: GameState, simulation_time: float) -> 'SimulationResult':
        final_scores_data = GameEngine(load_game_data()).get_final_scores(final_state)
        
        winner_id = final_scores_data.get('winner_id')
        winner_name = final_scores_data.get('winner_name')
        final_scores = final_scores_data.get('scores', {})
        
        return SimulationResult(
            winner_id=winner_id,
            winner_name=winner_name,
            game_length_rounds=self.round_count,
            game_length_terms=self.term_count,
            final_scores=final_scores,
            game_log=final_state.turn_log,
            simulation_time_seconds=simulation_time,
            final_state=final_state
        )


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
            game_state: Current game state (includes game_log for strategic agents)
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


class ScriptedAgent(Agent):
    """
    An agent that follows a predetermined sequence of actions.
    Useful for testing specific game scenarios and rule validation.
    """
    
    def __init__(self, actions_to_perform: List[Action]):
        """
        Initialize with a list of actions to perform in order.
        
        Args:
            actions_to_perform: List of actions to perform sequentially
        """
        self.actions = actions_to_perform.copy()
        self.action_index = 0
    
    def choose_action(self, game_state: GameState, valid_actions: List[Action]) -> Action:
        """
        Return the next action from the script.
        
        Raises:
            ValueError: If the scripted action is not in the valid actions list
        """
        if self.action_index >= len(self.actions):
            # If we've used all our scripted actions, fall back to pass turn
            return ActionPassTurn(player_id=game_state.get_current_player().id)
        
        scripted_action = self.actions[self.action_index]
        
        # Validate that the scripted action is actually valid
        if scripted_action not in valid_actions:
            raise ValueError(
                f"Scripted action {scripted_action} is not valid. "
                f"Valid actions: {[a.__class__.__name__ for a in valid_actions]}"
            )
        
        self.action_index += 1
        return scripted_action


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
    final_state: Optional[GameState] = None  # Add final state for analysis


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
                      logger: Optional[MetricsLogger] = None) -> SimulationResult:
        """
        Run a complete game simulation with the specified agents.
        
        Args:
            player_agents: List of agent objects, one per player
            player_names: Optional list of player names (defaults to Agent 0, Agent 1, etc.)
            max_rounds: Maximum number of rounds to prevent infinite loops
            logger: Optional metrics logger (defaults to SilentLogger for speed)
            
        Returns:
            SimulationResult: Complete results of the simulation
        """
        start_time = time.time()
        
        # Set up player names if not provided
        if player_names is None:
            player_names = [f"Agent {i}" for i in range(len(player_agents))]
        
        # Set up logger if not provided
        if logger is None:
            logger = SilentLogger()
        
        # Create the game
        state = self.create_game(player_names)
        logger.log_start(state)
        
        round_count = 0
        term_count = 0
        
        # Main game loop
        while not self.engine.is_game_over(state) and round_count < max_rounds:
            round_count += 1
            logger.log_round_end(state, round_count)
            
            # Check for system actions first
            system_actions = self.engine.get_valid_system_actions(state)
            if system_actions:
                # Process the first system action
                action = system_actions[0]
                
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
                    # Force pass turn
                    action = ActionPassTurn(player_id=current_player_id)
                else:
                    # Let the agent choose an action
                    action = agent.choose_action(state, valid_actions)
                    
                    # Validate the chosen action is in the valid list
                    if action not in valid_actions:
                        # Fall back to pass turn
                        action = ActionPassTurn(player_id=current_player_id)
                
                # Process the action through the engine
                state = self.engine.process_action(state, action)
                logger.log_action(action, state)
            
            # Track term transitions
            if state.round_marker == 1 and round_count > 1:
                term_count += 1
                logger.log_term_end(state, term_count)
        
        # Calculate final results using the logger
        simulation_time = time.time() - start_time
        return logger.finalize(state, simulation_time)


def create_random_agent() -> Agent:
    """Create a random agent for testing."""
    return RandomAgent()


def create_scripted_agent(actions: List[Action]) -> Agent:
    """Create a scripted agent for testing specific scenarios."""
    return ScriptedAgent(actions)


def test_simulation_harness():
    """Test the simulation harness with random agents."""
    print("Testing Simulation Harness...")
    
    # Create agents
    agents = [RandomAgent() for _ in range(4)]
    player_names = ['Alice', 'Bob', 'Charlie', 'Diana']
    
    # Create harness and run simulation with verbose logging
    harness = SimulationHarness()
    result = harness.run_simulation(agents, player_names, logger=VerboseLogger())
    
    return result


if __name__ == "__main__":
    test_simulation_harness() 