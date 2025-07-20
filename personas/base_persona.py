"""
Base Persona class for the Election Game simulation framework.

This module defines the abstract base class that all player personas must implement.
Personas are pure decision-makers that choose actions based on game state.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import random

from simulation_harness import Agent
from models.game_state import GameState
from engine.actions import Action, ActionPassTurn


class BasePersona(Agent, ABC):
    """
    Abstract base class for all player personas.
    
    Personas are pure decision-makers that choose actions from a pre-validated list.
    They should not be responsible for figuring out what actions are possible.
    Each persona implements a specific strategy or play style.
    """
    
    def __init__(self, name: str = "Base Persona", random_seed: Optional[int] = None):
        """
        Initialize the persona.
        
        Args:
            name: Human-readable name for this persona
            random_seed: Optional seed for reproducible behavior
        """
        self.name = name
        if random_seed is not None:
            self.random = random.Random(random_seed)
        else:
            self.random = random
    
    @abstractmethod
    def choose_action(self, game_state: GameState, valid_actions: List[Action]) -> Action:
        """
        Choose an action from the list of valid actions.
        
        This is the core decision-making method that each persona must implement.
        The persona should analyze the game state and choose the most appropriate
        action according to its strategy.
        
        IMPORTANT: The valid_actions list contains only actions that are legal
        for the current player in the current game state. The persona should
        not need to validate actions - it can focus purely on strategy.
        
        Args:
            game_state: Current game state (includes game_log for strategic agents)
            valid_actions: List of pre-validated actions to choose from
            
        Returns:
            Action: The chosen action (must be one from valid_actions)
        """
        pass
    
    def get_action_priority(self, action: Action) -> int:
        """
        Get the priority score for an action.
        
        This helper method can be used by personas to rank actions by preference.
        Higher scores indicate higher priority.
        
        Args:
            action: The action to score
            
        Returns:
            int: Priority score (higher = more preferred)
        """
        # Default implementation: all actions have equal priority
        return 0
    
    def choose_highest_priority_action(self, valid_actions: List[Action]) -> Optional[Action]:
        """
        Choose the action with the highest priority score.
        
        This helper method can be used by personas to select the best action
        based on priority scores.
        
        Args:
            valid_actions: List of valid actions to choose from
            
        Returns:
            Optional[Action]: The action with the highest priority score, or None if no actions available
        """
        if not valid_actions:
            return None
        
        # Score all actions
        scored_actions = [(action, self.get_action_priority(action)) for action in valid_actions]
        
        # Find the highest priority
        max_priority = max(score for _, score in scored_actions)
        
        # Get all actions with the highest priority
        best_actions = [action for action, score in scored_actions if score == max_priority]
        
        # Choose randomly among the best actions
        return self.random.choice(best_actions)
    
    def __str__(self) -> str:
        """Return a string representation of the persona."""
        return f"{self.__class__.__name__}({self.name})"
    
    def __repr__(self) -> str:
        """Return a detailed string representation of the persona."""
        return f"{self.__class__.__name__}(name='{self.name}')" 