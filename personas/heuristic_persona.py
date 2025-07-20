"""
Heuristic Persona for the Election Game simulation framework.

This persona implements basic strategic heuristics to represent foundational skill.
It serves as a proxy for a player who has played the game once and developed
basic strategic thinking.
"""

from typing import List, Optional
import random

from .base_persona import BasePersona
from models.game_state import GameState
from engine.actions import Action, ActionPassTurn, ActionFundraise, ActionDeclareCandidacy, ActionSupportLegislation, ActionOpposeLegislation


class HeuristicPersona(BasePersona):
    """
    A persona that follows basic strategic heuristics.
    
    This persona represents foundational skill - a player who understands
    the basic strategies but doesn't have advanced strategic thinking.
    It's strategically superior to the RandomPersona and provides a
    quantifiable measure of how much basic, logical play is rewarded.
    """
    
    def __init__(self, name: str = "Heuristic Bot", random_seed: Optional[int] = None):
        """
        Initialize the heuristic persona.
        
        Args:
            name: Human-readable name for this persona
            random_seed: Optional seed for reproducible behavior
        """
        super().__init__(name, random_seed)
    
    def choose_action(self, game_state: GameState, valid_actions: List[Action]) -> Action:
        """
        Choose an action based on basic strategic heuristics.
        
        This persona follows simple, hard-coded decision rules:
        1. If PC is low (< 10), prioritize fundraising
        2. If it's Round 4 and can afford it, declare candidacy for highest value office
        3. If supporting/opposing legislation, commit 30% of current PC
        4. Otherwise, choose randomly from valid actions
        
        Args:
            game_state: Current game state
            valid_actions: List of valid actions to choose from
            
        Returns:
            Action: The chosen action based on heuristics
        """
        if not valid_actions:
            # If no valid actions, pass turn
            current_player = game_state.get_current_player()
            return ActionPassTurn(player_id=current_player.id)
        
        current_player = game_state.get_current_player()
        current_round = game_state.round_marker
        
        # Heuristic 1: If PC is low, prioritize fundraising (unless stock market crash)
        if current_player.pc < 10:
            # Check for stock market crash - avoid Fundraise during crash
            stock_crash_active = "STOCK_CRASH" in game_state.active_effects
            if not stock_crash_active:
                fundraise_actions = [a for a in valid_actions if isinstance(a, ActionFundraise)]
                if fundraise_actions:
                    return fundraise_actions[0]
        
        # Heuristic 2: If it's Round 4 and can afford it, declare candidacy for highest value office
        if current_round == 4:
            candidacy_actions = [a for a in valid_actions if isinstance(a, ActionDeclareCandidacy)]
            if candidacy_actions:
                # Find the highest value office (President = 50, US Senator = 30, Governor = 25, etc.)
                best_candidacy = None
                best_value = 0
                
                for action in candidacy_actions:
                    office = game_state.offices.get(action.office_id)
                    if office and office.candidacy_cost <= current_player.pc:
                        if office.candidacy_cost > best_value:
                            best_value = office.candidacy_cost
                            best_candidacy = action
                
                if best_candidacy:
                    return best_candidacy
        
        # Heuristic 3: If supporting/opposing legislation, commit 30% of current PC
        support_actions = [a for a in valid_actions if isinstance(a, ActionSupportLegislation)]
        oppose_actions = [a for a in valid_actions if isinstance(a, ActionOpposeLegislation)]
        
        if support_actions or oppose_actions:
            # Choose randomly between support and oppose if both available
            if support_actions and oppose_actions:
                action_type = self.random.choice(['support', 'oppose'])
                if action_type == 'support':
                    action = support_actions[0]
                else:
                    action = oppose_actions[0]
            elif support_actions:
                action = support_actions[0]
            else:
                action = oppose_actions[0]
            
            # Set PC commitment to 30% of current PC
            pc_commitment = max(1, int(current_player.pc * 0.3))
            if isinstance(action, ActionSupportLegislation):
                action.support_amount = pc_commitment
            elif isinstance(action, ActionOpposeLegislation):
                action.oppose_amount = pc_commitment
            
            return action
        
        # Heuristic 4: Otherwise, choose randomly from valid actions (but never pass if profitable actions exist)
        profitable_actions = [a for a in valid_actions if not isinstance(a, ActionPassTurn)]
        if profitable_actions:
            return self.random.choice(profitable_actions)
        else:
            # Only pass if no profitable actions are available
            current_player = game_state.get_current_player()
            return ActionPassTurn(player_id=current_player.id)
    
    def get_action_priority(self, action: Action) -> int:
        """
        Get the priority score for an action.
        
        For the heuristic persona, actions are prioritized based on
        basic strategic value.
        
        Args:
            action: The action to score
            
        Returns:
            int: Priority score (higher = more preferred)
        """
        # Fundraise gets high priority when PC is low
        if isinstance(action, ActionFundraise):
            return 8
        
        # Declare candidacy gets high priority in round 4
        if isinstance(action, ActionDeclareCandidacy):
            return 7
        
        # Support/oppose legislation gets medium priority
        if isinstance(action, (ActionSupportLegislation, ActionOpposeLegislation)):
            return 5
        
        # Other actions get lower priority
        return 2 