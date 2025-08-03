#!/usr/bin/env python3
"""
Headless Game Session Manager

This module provides a GameSession class that manages the state and logic of a game,
acting as a self-contained, headless engine. It is designed to be controlled by an
external interface, such as a web server, without containing any I/O itself.
"""

from typing import List, Optional, Dict, Any, Type
from engine.engine import GameEngine
from models.game_state import GameState
from engine.actions import (
    Action, ActionSponsorLegislation, ActionSupportLegislation, 
    ActionOpposeLegislation, ActionDeclareCandidacy, ActionResolveLegislation,
    ActionResolveElections, ActionAcknowledgeResults
)
from game_data import load_game_data
from personas.base_persona import BasePersona
from personas.random_persona import RandomPersona
from personas.economic_persona import EconomicPersona
from personas.legislative_persona import LegislativePersona
from personas.balanced_persona import BalancedPersona
from personas.heuristic_persona import HeuristicPersona
from engine.actions import ActionPassTurn, ACTION_CLASSES
import json
from fastapi.responses import FileResponse


class GameSession:
    """
    Manages a single game session, including the game state, players, 
    and the interaction between the core game engine and a client.
    """
    def __init__(self):
        self.engine = GameEngine(load_game_data())
        self.state: Optional[GameState] = None
        self.human_player_id: int = 0
        self.ai_opponents: List[BasePersona] = []
        self.pending_ui_action: Optional[Dict[str, Any]] = None
        self.awaiting_ai_acknowledgement: bool = False

    def start_game(self, human_name: str = "Human", num_ai: int = 3):
        """
        Initializes a new game state.
        """
        player_names = [human_name] + [f"AI-{i+1}" for i in range(num_ai)]
        self.state = self.engine.start_new_game(player_names)
        self.human_player_id = self.state.players[0].id

        # Create AI opponents
        self.ai_opponents = [
            RandomPersona(),
            EconomicPersona(),
            LegislativePersona(),
            BalancedPersona(),
            HeuristicPersona()
        ]

        # Immediately run the first event phase to properly set up the game
        self.state = self.engine.run_event_phase(self.state)

    def get_state_for_client(self) -> Dict[str, Any]:
        """
        Returns a JSON-serializable representation of the current game state,
        including valid actions for the human player if it is their turn.
        """
        if not self.state:
            return {"error": "Game not started."}

        state_dict = self.state.to_dict()
        state_dict['log'] = list(self.state.turn_log)
        state_dict['is_game_over'] = self.is_game_over()

        # Check for high-priority system actions first.
        system_actions = self.engine.get_valid_system_actions(self.state)
        if system_actions:
            state_dict['valid_actions'] = [action.to_dict() for action in system_actions]
            state_dict['prompt'] = "Awaiting system resolution."
            if any(isinstance(a, ActionResolveLegislation) for a in system_actions):
                state_dict['prompt'] = "The legislative session has concluded. Resolve the outcomes."
            elif any(isinstance(a, ActionResolveElections) for a in system_actions):
                state_dict['prompt'] = "The election is over. Announce the results."
            elif any(isinstance(a, ActionAcknowledgeResults) for a in system_actions):
                state_dict['prompt'] = "Review the election results and start the next term."
        elif self.is_human_turn() and self.pending_ui_action:
            state_dict['valid_actions'] = self.pending_ui_action['options']
            state_dict['prompt'] = self.pending_ui_action['prompt']
            state_dict['expects_input'] = self.pending_ui_action.get('expects_input')
        elif self.is_human_turn():
            valid_actions = self.engine.get_valid_actions(self.state, self.human_player_id)
            state_dict['valid_actions'] = [action.to_dict() for action in valid_actions]
        else:
            state_dict['valid_actions'] = []

        state_dict['awaiting_ai_acknowledgement'] = self.awaiting_ai_acknowledgement
        
        return state_dict

    def process_action(self, action_data: Dict[str, Any]) -> List[str]:
        """
        Processes a single action from the client, then runs AI turns if necessary.
        This is the main entry point for all game interactions.
        """
        self.state.clear_turn_log()
        action_to_execute: Optional[Action] = None
        is_ui_setup_action = False

        if self.pending_ui_action:
            action_to_execute = self._resolve_pending_action(action_data)
        else:
            action_type = action_data.get("action_type")
            
            if action_type == "AcknowledgeAITurn":
                self.awaiting_ai_acknowledgement = False
            elif action_type in ["UISponsorLegislation", "UISupportLegislation", "UIOpposeLegislation", "UIDeclareCandidacy"]:
                self._handle_ui_action(action_data)
                is_ui_setup_action = True
            else:
                try:
                    action_to_execute = self.engine.action_from_dict(action_data)
                except Exception as e:
                    print(f"Error creating action from dict: {e}")
                    self.state.add_log(f"Error: {str(e)}")

        is_system_action = False
        if action_to_execute:
            # Check if the action is a system action BEFORE executing it.
            if isinstance(action_to_execute, (ActionResolveLegislation, ActionResolveElections, ActionAcknowledgeResults)):
                is_system_action = True
            self._execute_action(action_to_execute)

        if not is_ui_setup_action and not is_system_action:
            self.run_ai_turn()

        return list(self.state.turn_log)

    def run_ai_turn(self):
        """
        Checks if the game state requires an AI to take a turn, and if so,
        executes it.
        """
        if self.is_game_over() or self.is_human_turn():
            return

        if self.engine.get_valid_system_actions(self.state):
            return
        
        current_player = self.state.get_current_player()
        persona = self.ai_opponents[current_player.id - 1]
        
        if current_player.action_points <= 0:
            action = ActionPassTurn(player_id=current_player.id)
        else:
            valid_actions = self.engine.get_valid_actions(self.state, current_player.id)
            if not valid_actions:
                action = ActionPassTurn(player_id=current_player.id)
            else:
                action = persona.choose_action(self.state, valid_actions)
                if not action:
                    action = ActionPassTurn(player_id=current_player.id)

        self._execute_action(action)

        if not self.is_human_turn():
            self.awaiting_ai_acknowledgement = True

    def _execute_action(self, action: Action):
        """Processes a single, concrete action through the engine."""
        if not self.state or self.is_game_over():
            return
        try:
            self.state = self.engine.process_action(self.state, action)
        except Exception as e:
            print(f"Error executing action '{action.to_dict().get('action_type')}': {e}")
            self.state.add_log(f"Error: {e}")

    def _handle_ui_action(self, action_data: Dict[str, Any]):
        action_type = action_data.get("action_type")
        player_id = action_data.get("player_id")
        player = self.state.get_player_by_id(player_id)

        if action_type == "UISponsorLegislation":
            options = []
            sponsored_ids = {leg.legislation_id for leg in self.state.term_legislation}
            for leg_id, leg_details in self.state.legislation_options.items():
                if leg_id not in sponsored_ids and self.state.get_player_by_id(player_id).pc >= leg_details.cost:
                    options.append({
                        "id": leg_id,
                        "display_name": f"{leg_details.title} (Cost: {leg_details.cost} PC)"
                    })
            self.pending_ui_action = {
                "action_template": {"action_type": "ActionSponsorLegislation", "player_id": player_id},
                "prompt": "Which bill would you like to sponsor?",
                "options": options,
                "step": "choose_entity"
            }
        
        elif action_type == "UIDeclareCandidacy":
            options = []
            player = self.state.get_player_by_id(player_id)
            for office_id, office_details in self.state.offices.items():
                if player.pc >= office_details.candidacy_cost:
                    options.append({
                        "id": office_id,
                        "display_name": f"{office_details.title} (Cost: {office_details.candidacy_cost} PC)"
                    })
            self.pending_ui_action = {
                "action_template": {"action_type": "ActionDeclareCandidacy", "player_id": player_id},
                "prompt": "Which office would you like to run for?",
                "options": options,
                "step": "choose_entity"
            }

        elif action_type in ["UISupportLegislation", "UIOpposeLegislation"]:
            options = []
            for leg in self.state.term_legislation:
                if not leg.resolved:
                    leg_details = self.state.legislation_options[leg.legislation_id]
                    options.append({
                        "id": leg.legislation_id,
                        "display_name": f"{leg_details.title}"
                    })
            if not options:
                self.state.add_log("There is no active legislation to influence right now.")
                return

            is_support = action_type == "UISupportLegislation"
            final_action_type = "ActionSupportLegislation" if is_support else "ActionOpposeLegislation"
            prompt = "Which bill would you like to secretly support?" if is_support else "Which bill would you like to secretly oppose?"
            self.pending_ui_action = {
                "action_template": {"action_type": final_action_type, "player_id": player_id},
                "prompt": prompt,
                "options": options,
                "step": "choose_entity"
            }

    def _resolve_pending_action(self, action_data: Dict[str, Any]) -> Optional[Action]:
        """Resolves a multi-step action flow and returns a concrete Action to be executed."""
        choice = action_data.get('choice')
        pending_action = self.pending_ui_action
        action_template = pending_action['action_template']
        player_id = action_template['player_id']
        player = self.state.get_player_by_id(player_id)

        if pending_action.get("step") == "choose_entity":
            action_type = action_template['action_type']
            if action_type in ["ActionSupportLegislation", "ActionOpposeLegislation"]:
                pending_action["action_template"]["legislation_id"] = choice
                pending_action["step"] = "choose_amount"
                is_support = action_type == "ActionSupportLegislation"
                prompt = "support with" if is_support else "oppose with"
                pending_action["prompt"] = f"How much PC to {prompt}? (1 - {player.pc})"
                pending_action["options"] = []
                pending_action["expects_input"] = "amount"
                return None
            else:
                if action_type == 'ActionSponsorLegislation':
                    action_template['legislation_id'] = choice
                elif action_type == 'ActionDeclareCandidacy':
                    action_template['office_id'] = choice
                action_class = ACTION_CLASSES.get(action_type)
                if action_class:
                    action = action_class.from_dict(action_template)
                    self.pending_ui_action = None
                    return action
        
        elif pending_action.get("step") == "choose_amount":
            amount = choice
            if not isinstance(amount, int) or not (1 <= amount <= player.pc):
                pending_action["prompt"] = f"Invalid amount. How much PC? (1 - {player.pc})"
                return None
            
            action_type = action_template['action_type']
            if action_type == 'ActionSupportLegislation':
                action_template['support_amount'] = amount
            elif action_type == 'ActionOpposeLegislation':
                action_template['oppose_amount'] = amount
            
            action_class = ACTION_CLASSES.get(action_type)
            if action_class:
                action = action_class.from_dict(action_template)
                self.pending_ui_action = None
                return action
        
        self.state.add_log("Invalid state in pending action processing.")
        return None

    def is_human_turn(self) -> bool:
        if not self.state: return False
        return self.state.get_current_player().id == self.human_player_id

    def is_game_over(self) -> bool:
        if not self.state: return True
        return self.engine.is_game_over(self.state) 