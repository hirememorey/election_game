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


class GameSession:
    """
    Manages a single, headless game session.
    """
    
    def __init__(self, ai_personas: Optional[List[str]] = None):
        self.game_data = load_game_data()
        self.engine = GameEngine(self.game_data)
        
        if ai_personas is None:
            ai_personas = ["heuristic", "economic", "legislative"]
        
        self.ai_personas = [self._get_persona_class(persona)() for persona in ai_personas]
        self.state: Optional[GameState] = None
        self.human_player_id = 0
        
    def _get_persona_class(self, persona_name: str) -> type:
        persona_map = {
            "random": RandomPersona, "economic": EconomicPersona,
            "legislative": LegislativePersona, "balanced": BalancedPersona,
            "heuristic": HeuristicPersona,
        }
        return persona_map.get(persona_name, HeuristicPersona)

    def start_game(self, human_name: str = "Human") -> None:
        """
        Initializes a new game state.
        """
        player_names = [human_name] + [f"AI-{i+1}" for i in range(len(self.ai_personas))]
        self.state = self.engine.start_new_game(player_names)
        self.state = self.engine.run_event_phase(self.state)

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
        if self.is_human_turn():
            valid_actions = self.engine.get_valid_actions(self.state, self.human_player_id)
            # We need to serialize the actions as well
            state_dict['valid_actions'] = [action.to_dict() for action in valid_actions]
        else:
            state_dict['valid_actions'] = []
        
        return state_dict

    def process_action(self, action_data: Dict[str, Any]) -> List[str]:
        """
        Processes a single action from the player.
        Returns a log of all events that occurred.
        """
        if not self.state or self.is_game_over():
            return ["Error: Game is not active."]

        # Special case for a "continue" action from the client
        if action_data.get("action_type") == "continue":
            return []

        action = self.engine.action_from_dict(action_data)
        if not action:
            return ["Error: Invalid action data."]

        valid_actions = self.engine.get_valid_actions(self.state, self.state.get_current_player().id)
        if action not in valid_actions:
            # Construct a helpful error message
            error_msg = f"Error: Invalid action. Valid actions are: {[a.to_dict() for a in valid_actions]}"
            print(f"Invalid action attempted: {action.to_dict()}")
            print(f"Current Player: {self.state.get_current_player().id}")
            return [error_msg]


        self.state.clear_turn_log()
        self.state = self.engine.process_action(self.state, action)
        return list(self.state.turn_log)


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
        persona = self.ai_personas[current_player.id - 1]

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