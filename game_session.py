#!/usr/bin/env python3
"""
Headless Game Session Manager

This module provides a GameSession class that manages the state and logic of a game,
acting as a self-contained, headless engine. It is designed to be controlled by an
external interface, such as a web server, without containing any I/O itself.
"""

from typing import List, Optional, Dict, Any
from engine.engine import GameEngine
from models.game_state import GameState
from engine.actions import Action
from game_data import load_game_data
from personas.base_persona import BasePersona
from personas.random_persona import RandomPersona
from personas.economic_persona import EconomicPersona
from personas.legislative_persona import LegislativePersona
from personas.balanced_persona import BalancedPersona
from personas.heuristic_persona import HeuristicPersona
from engine.actions import ActionPassTurn
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

    def get_state_for_client(self) -> Dict[str, Any]:
        """
        Returns a JSON-serializable representation of the current game state,
        including valid actions for the human player if it is their turn.
        """
        if not self.state:
            return {"error": "Game not started."}

        # on the GameState and its components. For now, this provides a basic structure.
        state_dict = self.state.to_dict()
        state_dict['log'] = list(self.state.turn_log)
        state_dict['is_game_over'] = self.is_game_over()


        # If it's the human's turn, add the available actions to the state payload
        if self.is_human_turn() and self.pending_ui_action:
            state_dict['valid_actions'] = self.pending_ui_action['options']
            state_dict['prompt'] = self.pending_ui_action['prompt']
        elif self.is_human_turn():
            valid_actions = self.engine.get_valid_actions(self.state, self.human_player_id)
            # We need to serialize the actions as well
            state_dict['valid_actions'] = [action.to_dict() for action in valid_actions]
        else:
            state_dict['valid_actions'] = []
        
        return state_dict

    def process_action(self, action_data: Dict[str, Any]) -> List[str]:
        """
        Processes an action from the client, advances the game state,
        and runs AI turns until it's the human's turn again.
        Returns a log of events that occurred.
        """
        if self.pending_ui_action:
            # The user is responding to a sub-prompt (e.g., choosing a bill)
            action_type = self.pending_ui_action['action_type']
            
            # Find the chosen option
            choice = action_data.get('choice')
            chosen_action_dict = None
            for option in self.pending_ui_action['options']:
                if option['action_type'] == action_type and option.get('legislation_id') == choice:
                     chosen_action_dict = option
                     break
                # TODO: Add other potential identifiers here like office_id, favor_id etc.

            if not chosen_action_dict:
                 # Invalid choice, just return the prompt again
                return ["Invalid choice. Please try again."]

            # Reconstruct the action object from the dictionary
            action_class = self.engine.ACTION_CLASSES[chosen_action_dict['action_type']]
            action = action_class.from_dict(chosen_action_dict)
            
            self.pending_ui_action = None # Clear pending action
            return self._execute_action_and_run_ais(action)


        action_type = action_data.get("action_type")
        
        if action_type == 'continue':
            # This is for events or other pauses
            return self._run_ai_turns()

        # Handle UI actions that require a second step
        if action_type in ["UISponsorLegislation", "UISupportLegislation", "UIOpposeLegislation"]:
            return self._handle_ui_action(action_data)

        # For all other actions, they should have a direct mapping in the engine
        try:
            action_class = self.engine.ACTION_CLASSES.get(action_type)
            if not action_class:
                raise ValueError(f"Unknown action type: {action_type}")
            
            action = action_class.from_dict(action_data)
            return self._execute_action_and_run_ais(action)
        except Exception as e:
            print(f"Error processing action: {e}")
            return [f"Error: {str(e)}"]

    def _handle_ui_action(self, action_data: Dict[str, Any]) -> List[str]:
        action_type = action_data.get("action_type")
        player_id = action_data.get("player_id")

        if action_type == "UISponsorLegislation":
            # Get available legislation to sponsor
            options = [
                ActionSponsorLegislation(player_id=player_id, legislation_id=leg_id).to_dict()
                for leg_id in self.state.legislation_options
            ]
            self.pending_ui_action = {
                "action_type": "ActionSponsorLegislation",
                "prompt": "Which bill would you like to sponsor?",
                "options": options
            }
        
        elif action_type == "UISupportLegislation":
            # Get active legislation to support
            options = [
                ActionSupportLegislation(player_id=player_id, legislation_id=leg.legislation_id, support_amount=5).to_dict() # Temp amount
                for leg in self.state.term_legislation if not leg.resolved
            ]
            self.pending_ui_action = {
                "action_type": "ActionSupportLegislation",
                "prompt": "Which bill would you like to support?",
                "options": options
            }

        elif action_type == "UIOpposeLegislation":
            # Get active legislation to oppose
            options = [
                ActionOpposeLegislation(player_id=player_id, legislation_id=leg.legislation_id, oppose_amount=5).to_dict() # Temp amount
                for leg in self.state.term_legislation if not leg.resolved
            ]
            self.pending_ui_action = {
                "action_type": "ActionOpposeLegislation",
                "prompt": "Which bill would you like to oppose?",
                "options": options
            }
        
        # We don't run any game logic here, just return an empty log. 
        # The new state with the prompt will be sent back to the client.
        return []


    def _execute_action_and_run_ais(self, action: Action) -> List[str]:
        """
        Processes a single action and then runs AI turns.
        """
        if not self.state or self.is_game_over():
            return ["Error: Game is not active."]

        self.state.clear_turn_log()
        self.state = self.engine.process_action(self.state, action)

        # Run AI turns until it's the human's turn again
        turn_logs = []
        while (not self.is_game_over() and
               self.state.get_current_player().id == self.human_player_id and
               self.state.action_points.get(self.human_player_id, 0) > 0):
            
            action_logs = self.run_one_ai_action()
            turn_logs.extend(action_logs)

        # After the loop, the turn might have auto-passed. Capture any final logs.
        if self.state.turn_log:
            turn_logs.extend(self.state.turn_log)
            self.state.clear_turn_log()
            
        return turn_logs

    def run_ai_turn(self) -> List[str]:
        """
        Runs a single turn for the current AI player.
        A turn consists of multiple actions until AP is depleted.
        """
        if not self.state or self.is_human_turn() or self.is_game_over():
            return []

        turn_logs = []
        current_player_id = self.state.get_current_player().id

        # Loop as long as it's the current AI's turn and they have AP
        while (not self.is_game_over() and
               self.state.get_current_player().id == current_player_id and
               self.state.action_points.get(current_player_id, 0) > 0):
            
            action_logs = self.run_one_ai_action()
            turn_logs.extend(action_logs)

        # After the loop, the turn might have auto-passed. Capture any final logs.
        if self.state.turn_log:
            turn_logs.extend(self.state.turn_log)
            self.state.clear_turn_log()
            
        return turn_logs

    def run_one_ai_action(self) -> List[str]:
        """
        Runs a single action for the current AI player.
        Returns the logs for that action.
        """
        if not self.state or self.is_human_turn() or self.is_game_over():
            return []

        current_player = self.state.get_current_player()
        persona = self.ai_opponents[current_player.id - 1] # Changed from ai_personas to ai_opponents

        if self.state.action_points.get(current_player.id, 0) <= 0:
            action = ActionPassTurn(player_id=current_player.id)
        else:
            valid_actions = self.engine.get_valid_actions(self.state, current_player.id)
            action = persona.choose_action(self.state, valid_actions)
            if not action:
                action = ActionPassTurn(player_id=current_player.id)

        self.state.clear_turn_log()
        self.state = self.engine.process_action(self.state, action)
        return list(self.state.turn_log)

    def run_full_ai_turn(self) -> List[str]:
        """
        DEPRECATED: This method is no longer suitable for the interactive web version.
        Use run_ai_turn instead.
        """
        print("Warning: run_full_ai_turn is deprecated.")
        return self.run_ai_turn()

    def is_human_turn(self) -> bool:
        if not self.state: return False
        return self.state.get_current_player().id == self.human_player_id

    def is_game_over(self) -> bool:
        if not self.state: return True
        return self.engine.is_game_over(self.state) 