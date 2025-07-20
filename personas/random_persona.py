"""
Random Persona for the Election Game simulation framework.

This persona makes completely random decisions from available actions.
It serves as a baseline for comparison with more sophisticated strategies.
"""

from typing import List, Optional
import random

from .base_persona import BasePersona
from models.game_state import GameState
from engine.actions import Action, ActionPassTurn


class RandomPersona(BasePersona):
    """
    A persona that makes random decisions from available actions.
    
    This persona serves as a baseline for comparison with more sophisticated
    strategies. It provides a measure of expected performance when players
    make no strategic decisions.
    """
    
    def __init__(self, name: str = "Random Bot", random_seed: Optional[int] = None):
        """
        Initialize the random persona.
        
        Args:
            name: Human-readable name for this persona
            random_seed: Optional seed for reproducible behavior
        """
        super().__init__(name, random_seed)
    
    def choose_action(self, game_state: GameState, valid_actions: List[Action]) -> Action:
        """
        Choose a random action from the valid actions list.
        
        This is the simplest possible decision-making strategy. It provides
        a baseline for comparison with more sophisticated strategies.
        
        Args:
            game_state: Current game state (unused in random strategy)
            valid_actions: List of valid actions to choose from
            
        Returns:
            Action: A randomly chosen action
        """
        if not valid_actions:
            # If no valid actions, pass turn
            current_player = game_state.get_current_player()
            return ActionPassTurn(player_id=current_player.id)
        
        # Choose randomly from all valid actions
        return self.random.choice(valid_actions)
    
    def get_action_priority(self, action: Action) -> int:
        """
        Get the priority score for an action.
        
        For the random persona, all actions have equal priority (0).
        
        Args:
            action: The action to score
            
        Returns:
            int: Priority score (always 0 for random persona)
        """
        return 0 