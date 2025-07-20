"""
Economic Persona for the Election Game simulation framework.

This persona prioritizes actions that generate Political Capital (PC),
particularly fundraising and networking. It focuses on building economic
strength before engaging in other activities.
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


class EconomicPersona(BasePersona):
    """
    A persona that prioritizes economic actions (fundraising, networking).
    
    This persona focuses on building Political Capital (PC) through
    fundraising and networking. It will only sponsor legislation or
    engage in other activities when it has sufficient PC reserves.
    """
    
    def __init__(self, name: str = "Economic Bot", random_seed: Optional[int] = None):
        """
        Initialize the economic persona.
        
        Args:
            name: Human-readable name for this persona
            random_seed: Optional seed for reproducible behavior
        """
        super().__init__(name, random_seed)
    
    def choose_action(self, game_state: GameState, valid_actions: List[Action]) -> Action:
        """
        Choose an action prioritizing economic activities.
        
        This persona prioritizes actions in the following order:
        1. Fundraise (highest priority - generates PC)
        2. Network (high priority - generates PC + favor)
        3. Sponsor Legislation (if sufficient PC)
        4. Support/Oppose Legislation (if PC available)
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
        
        Higher scores indicate higher priority. The economic persona
        prioritizes actions that generate PC.
        
        Args:
            action: The action to score
            
        Returns:
            int: Priority score (higher = more preferred)
        """
        # Priority levels (higher = more preferred)
        if isinstance(action, ActionFundraise):
            return 100  # Highest priority - direct PC generation
        
        elif isinstance(action, ActionNetwork):
            return 90   # High priority - PC + favor generation
        
        elif isinstance(action, ActionSponsorLegislation):
            # Only sponsor if we have sufficient PC
            return 70   # Medium-high priority
        
        elif isinstance(action, (ActionSupportLegislation, ActionOpposeLegislation)):
            return 60   # Medium priority - requires PC commitment
        
        elif isinstance(action, ActionDeclareCandidacy):
            return 50   # Medium-low priority - strategic timing
        
        elif isinstance(action, ActionUseFavor):
            return 40   # Low priority - situational
        
        elif isinstance(action, ActionPassTurn):
            return 10   # Lowest priority - only when no other options
        
        else:
            return 30   # Default priority for unknown actions 