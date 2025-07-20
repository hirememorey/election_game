"""
Legislative Persona for the Election Game simulation framework.

This persona prioritizes legislative actions (sponsoring, supporting, opposing
legislation) over economic activities. It focuses on influencing the game
through legislation rather than building PC reserves.
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


class LegislativePersona(BasePersona):
    """
    A persona that prioritizes legislative actions.
    
    This persona focuses on sponsoring and supporting/opposing legislation.
    It will fundraise and network only when necessary to support its
    legislative agenda.
    """
    
    def __init__(self, name: str = "Legislative Bot", random_seed: Optional[int] = None):
        """
        Initialize the legislative persona.
        
        Args:
            name: Human-readable name for this persona
            random_seed: Optional seed for reproducible behavior
        """
        super().__init__(name, random_seed)
    
    def choose_action(self, game_state: GameState, valid_actions: List[Action]) -> Action:
        """
        Choose an action prioritizing legislative activities.
        
        This persona prioritizes actions in the following order:
        1. Sponsor Legislation (highest priority - core strategy)
        2. Support/Oppose Legislation (high priority - influence bills)
        3. Fundraise (medium priority - needed for legislation)
        4. Network (medium priority - PC + favor for legislation)
        5. Declare Candidacy (if in final round)
        6. Use Favor (if available)
        7. Pass Turn (lowest priority)
        
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
        
        Higher scores indicate higher priority. The legislative persona
        prioritizes actions that influence legislation.
        
        Args:
            action: The action to score
            
        Returns:
            int: Priority score (higher = more preferred)
        """
        # Priority levels (higher = more preferred)
        if isinstance(action, ActionSponsorLegislation):
            return 100  # Highest priority - core legislative strategy
        
        elif isinstance(action, (ActionSupportLegislation, ActionOpposeLegislation)):
            return 90   # High priority - influence existing legislation
        
        elif isinstance(action, ActionFundraise):
            return 70   # Medium priority - needed for legislation costs
        
        elif isinstance(action, ActionNetwork):
            return 60   # Medium priority - PC + favor for legislation
        
        elif isinstance(action, ActionDeclareCandidacy):
            return 50   # Medium-low priority - strategic timing
        
        elif isinstance(action, ActionUseFavor):
            return 40   # Low priority - situational
        
        elif isinstance(action, ActionPassTurn):
            return 10   # Lowest priority - only when no other options
        
        else:
            return 30   # Default priority for unknown actions 