#!/usr/bin/env python3
"""
Simulation Harness for Election Game

This module provides a headless simulation environment for running games
programmatically without the web server. It's designed to support agent-based
simulation for game balance analysis.
"""

import random
import time
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass

from engine.engine import GameEngine
from models.game_state import GameState
from models.components import Player
from engine.actions import (
    Action, ActionFundraise, ActionNetwork, ActionSponsorLegislation,
    ActionDeclareCandidacy, ActionUseFavor, ActionSupportLegislation,
    ActionOpposeLegislation, ActionPassTurn
)
from game_data import load_game_data


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
    
    def get_valid_actions(self, state: GameState, player_id: int) -> List[Action]:
        """
        Get all valid actions a player can take in the current game state.
        
        Args:
            state: Current game state
            player_id: ID of the player whose actions to check
            
        Returns:
            List of valid Action objects
        """
        valid_actions = []
        player = state.get_player_by_id(player_id)
        
        if not player:
            return valid_actions
            
        # Check if it's the player's turn
        if state.get_current_player().id != player_id:
            return valid_actions
            
        # Check if player has action points
        ap = state.action_points.get(player_id, 0)
        if ap <= 0:
            # Only Pass Turn is available
            valid_actions.append(ActionPassTurn(player_id=player_id))
            return valid_actions
            
        # Always available actions
        valid_actions.append(ActionFundraise(player_id=player_id))
        valid_actions.append(ActionNetwork(player_id=player_id))
        
        # Sponsor Legislation (if player has enough PC)
        if player.pc >= 5:  # Minimum PC requirement for sponsoring
            for leg_id in state.legislation_options:
                valid_actions.append(ActionSponsorLegislation(
                    player_id=player_id, 
                    legislation_id=leg_id
                ))
        
        # Declare Candidacy (only in round 4)
        if state.round_marker == 4:
            for office_id in state.offices:
                office = state.offices[office_id]
                if office.candidacy_cost <= player.pc:
                    # Can declare with 0 PC commitment
                    valid_actions.append(ActionDeclareCandidacy(
                        player_id=player_id,
                        office_id=office_id,
                        committed_pc=0
                    ))
                    # Can also declare with additional PC commitment
                    if player.pc > office.candidacy_cost:
                        valid_actions.append(ActionDeclareCandidacy(
                            player_id=player_id,
                            office_id=office_id,
                            committed_pc=min(10, player.pc - office.candidacy_cost)
                        ))
        
        # Use Favor (if player has favors)
        if player.favors:
            for favor in player.favors:
                valid_actions.append(ActionUseFavor(
                    player_id=player_id,
                    favor_id=favor.id
                ))
        
        # Support/Oppose Legislation (if there's pending legislation)
        if state.pending_legislation and not state.pending_legislation.resolved:
            if player.pc > 0:
                # Can support with any amount of PC
                for pc_amount in range(1, min(player.pc + 1, 21)):  # Cap at 20 PC
                    valid_actions.append(ActionSupportLegislation(
                        player_id=player_id,
                        legislation_id=state.pending_legislation.legislation_id,
                        support_amount=pc_amount
                    ))
                    valid_actions.append(ActionOpposeLegislation(
                        player_id=player_id,
                        legislation_id=state.pending_legislation.legislation_id,
                        oppose_amount=pc_amount
                    ))
        
        # Pass Turn (always available)
        valid_actions.append(ActionPassTurn(player_id=player_id))
        
        return valid_actions
    
    def run_simulation(self, 
                      player_agents: List[Callable[[GameState, int], Action]],
                      player_names: Optional[List[str]] = None,
                      max_rounds: int = 100,
                      verbose: bool = False) -> SimulationResult:
        """
        Run a complete game simulation with the specified agents.
        
        Args:
            player_agents: List of agent functions, one per player
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
            
            # Handle different phases
            if state.current_phase == "ACTION_PHASE":
                # Let the current player's agent choose an action
                current_player_id = state.get_current_player().id
                agent = player_agents[current_player_id]
                
                # Get valid actions
                valid_actions = self.get_valid_actions(state, current_player_id)
                
                if not valid_actions:
                    if verbose:
                        print(f"No valid actions for {state.get_current_player().name}")
                    # Force pass turn
                    action = ActionPassTurn(player_id=current_player_id)
                else:
                    # Let the agent choose an action
                    action = agent(state, current_player_id)
                    
                    # Validate the chosen action
                    if action not in valid_actions:
                        if verbose:
                            print(f"Agent chose invalid action: {action}")
                        # Fall back to pass turn
                        action = ActionPassTurn(player_id=current_player_id)
                    
                    # Additional validation: check if player has enough AP for the action
                    action_cost = 0
                    if isinstance(action, ActionSponsorLegislation):
                        action_cost = 2
                    elif isinstance(action, ActionDeclareCandidacy):
                        action_cost = 2
                    elif isinstance(action, (ActionFundraise, ActionNetwork, ActionUseFavor, 
                                           ActionSupportLegislation, ActionOpposeLegislation)):
                        action_cost = 1
                    elif isinstance(action, ActionPassTurn):
                        action_cost = 0
                    
                    if state.action_points.get(current_player_id, 0) < action_cost:
                        if verbose:
                            print(f"Agent chose action requiring {action_cost} AP but only has {state.action_points.get(current_player_id, 0)}")
                        # Fall back to pass turn
                        action = ActionPassTurn(player_id=current_player_id)
                
                if verbose:
                    print(f"{state.get_current_player().name} chose: {action.__class__.__name__}")
                
                # Process the action
                try:
                    state = self.engine.process_action(state, action)
                except Exception as e:
                    if verbose:
                        print(f"Error processing action: {e}")
                    # Force pass turn on error
                    state = self.engine.process_action(state, ActionPassTurn(player_id=current_player_id))
                    
            elif state.current_phase == "LEGISLATION_PHASE":
                # Handle legislation phase - auto-resolve
                if state.awaiting_legislation_resolution:
                    state = self.engine.resolve_legislation_session(state)
                else:
                    # If not awaiting resolution, advance to next player
                    state.current_player_index = (state.current_player_index + 1) % len(state.players)
                    if state.current_player_index == 0:
                        # All players have had a chance to act, resolve
                        state = self.engine.resolve_legislation_session(state)
                    
            elif state.awaiting_election_resolution:
                # Handle election phase - auto-resolve
                state = self.engine.resolve_elections_session(state)
                    
            elif state.current_phase == "UPKEEP_PHASE":
                # Handle upkeep phase - auto-advance
                state = self.engine.run_upkeep_phase(state)
                term_count += 1
                
            elif state.awaiting_results_acknowledgement:
                # Handle results acknowledgement phase - auto-acknowledge
                state.awaiting_results_acknowledgement = False
                # Start next term
                state = self.engine.start_next_term(state)
                term_count += 1
                
            else:
                # Unknown phase - try to advance
                if verbose:
                    print(f"Unknown phase: {state.current_phase}")
                break
        
        # Calculate final results
        simulation_time = time.time() - start_time
        
        winner_id = None
        winner_name = None
        final_scores = {}
        
        if self.engine.is_game_over(state):
            final_scores = self.engine.get_final_scores(state)
            # Find the winner (highest score)
            if final_scores:
                print(f"DEBUG: final_scores structure: {final_scores}")
                # Check if final_scores has the expected nested structure
                if 'scores' in final_scores and 'winner_id' in final_scores:
                    # Use the winner_id from the engine's calculation
                    winner_id = final_scores['winner_id']
                elif all(isinstance(score, dict) and 'total_influence' in score for score in final_scores.values()):
                    winner_id = max(final_scores.keys(), key=lambda k: final_scores[k]['total_influence'])
                else:
                    print(f"DEBUG: Unexpected final_scores structure, using first player as winner")
                    winner_id = list(final_scores.keys())[0] if final_scores else None
            
            winner = state.get_player_by_id(winner_id) if winner_id is not None else None
            winner_name = winner.name if winner else "Unknown"
        
        result = SimulationResult(
            winner_id=winner_id,
            winner_name=winner_name,
            game_length_rounds=round_count,
            game_length_terms=term_count,
            final_scores=final_scores,
            game_log=state.turn_log.copy(),
            simulation_time_seconds=simulation_time
        )
        
        if verbose:
            print(f"\n--- Simulation Complete ---")
            print(f"Winner: {winner_name}")
            print(f"Rounds: {round_count}, Terms: {term_count}")
            print(f"Final Scores: {final_scores}")
            print(f"Simulation Time: {simulation_time:.3f}s")
        
        return result


def create_random_agent() -> Callable[[GameState, int], Action]:
    """
    Create a simple random agent for testing.
    
    Returns:
        Agent function that chooses random valid actions
    """
    def random_agent(state: GameState, player_id: int) -> Action:
        valid_actions = SimulationHarness().get_valid_actions(state, player_id)
        if valid_actions:
            return random.choice(valid_actions)
        else:
            return ActionPassTurn(player_id=player_id)
    
    return random_agent


def test_simulation_harness():
    """Test the simulation harness with random agents."""
    print("Testing Simulation Harness...")
    
    harness = SimulationHarness()
    
    # Create 4 random agents
    agents = [create_random_agent() for _ in range(4)]
    player_names = ["Alice", "Bob", "Charlie", "Diana"]
    
    # Run a test simulation
    result = harness.run_simulation(
        player_agents=agents,
        player_names=player_names,
        verbose=True
    )
    
    print(f"\nTest completed successfully!")
    print(f"Winner: {result.winner_name}")
    print(f"Game length: {result.game_length_rounds} rounds, {result.game_length_terms} terms")
    print(f"Simulation time: {result.simulation_time_seconds:.3f} seconds")
    
    return result


if __name__ == "__main__":
    # Run a test simulation when executed directly
    test_simulation_harness() 