"""
Balanced Persona for the Election Game simulation framework.

This persona takes a balanced approach to all actions, not strongly
favoring any particular strategy. It provides a middle-ground baseline
for comparison with more specialized strategies.
"""

from typing import List, Optional
import random

from .base_persona import BasePersona
from models.game_state import GameState
from engine.actions import (
    Action, ActionPassTurn, ActionFundraise, ActionNetwork,
    ActionSponsorLegislation, ActionSupportLegislation, ActionOpposeLegislation,
    ActionDeclareCandidacy, ActionUseFavor
)


class BalancedPersona(BasePersona):
    """
    A persona that takes a balanced approach to all actions.
    
    This persona doesn't strongly favor any particular strategy. It provides
    a middle-ground baseline for comparison with more specialized strategies.
    It will consider all actions roughly equally, with slight preferences
    based on game state.
    """
    
    def __init__(self, name: str = "Balanced Bot", random_seed: Optional[int] = None):
        """
        Initialize the balanced persona.
        
        Args:
            name: Human-readable name for this persona
            random_seed: Optional seed for reproducible behavior
        """
        super().__init__(name, random_seed)
    
    def choose_action(self, game_state: GameState, valid_actions: List[Action]) -> Action:
        """
        Choose an action with balanced priorities.
        
        This persona prioritizes actions in the following order:
        1. Fundraise/Network (high priority - economic foundation)
        2. Sponsor Legislation (high priority - core gameplay)
        3. Support/Oppose Legislation (medium priority - engagement)
        4. Declare Candidacy (medium priority - strategic)
        5. Use Favor (low priority - situational)
        6. Pass Turn (lowest priority)
        
        Args:
            game_state: Current game state
            valid_actions: List of valid actions to choose from
            
        Returns:
            Action: The chosen action
        """
        if not valid_actions:
            current_player = game_state.get_current_player()
            return ActionPassTurn(player_id=current_player.id)
        
        # Use priority-based selection
        chosen_action = self.choose_highest_priority_action(valid_actions)
        if chosen_action is None:
            current_player = game_state.get_current_player()
            return ActionPassTurn(player_id=current_player.id)
        return chosen_action
    
    def get_action_priority(self, action: Action) -> int:
        """
        Get the priority score for an action.
        
        Higher scores indicate higher priority. The balanced persona
        gives roughly equal weight to different action types.
        
        Args:
            action: The action to score
            
        Returns:
            int: Priority score (higher = more preferred)
        """
        # Priority levels (higher = more preferred)
        if isinstance(action, ActionFundraise):
            return 80   # High priority - economic foundation
        
        elif isinstance(action, ActionNetwork):
            return 75   # High priority - economic + favor
        
        elif isinstance(action, ActionSponsorLegislation):
            return 70   # High priority - core gameplay
        
        elif isinstance(action, (ActionSupportLegislation, ActionOpposeLegislation)):
            return 60   # Medium priority - engagement
        
        elif isinstance(action, ActionDeclareCandidacy):
            return 50   # Medium priority - strategic
        
        elif isinstance(action, ActionUseFavor):
            return 40   # Low priority - situational
        
        elif isinstance(action, ActionPassTurn):
            return 10   # Lowest priority - only when no other options
        
        else:
            return 30   # Default priority for unknown actions 