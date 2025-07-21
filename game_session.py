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


        # If it's the human's turn, add the available actions to the state payload
        if self.is_human_turn():
            valid_actions = self.engine.get_valid_actions(self.state, self.human_player_id)
            # We need to serialize the actions as well
            state_dict['valid_actions'] = [action.to_dict() for action in valid_actions]
        
        return state_dict

    def process_human_action(self, action_data: Dict[str, Any]) -> List[str]:
        """
        Processes a single action from the human player and runs subsequent AI turns.
        Returns a log of all events that occurred.
        """
        if not self.state or not self.is_human_turn():
            return ["Error: It is not your turn."]

        # Reconstruct the action object from the dictionary
        action = self.engine.action_from_dict(action_data)
        if not action:
            return ["Error: Invalid action data."]
            
        # Validate that the action is actually valid
        valid_actions = self.engine.get_valid_actions(self.state, self.human_player_id)
        if action not in valid_actions:
             return ["Error: That action is not valid right now."]

        # Process the human action and collect logs
        self.state.clear_turn_log()
        self.state = self.engine.process_action(self.state, action)
        human_logs = list(self.state.turn_log)
        self.state.clear_turn_log()

        # After the human action, run all subsequent AI turns
        ai_logs = self._run_ai_turns()
        
        # The game state has been advanced by the AI turns, so the "new" state is the current state
        final_logs = human_logs + ai_logs
        
        # The state has already been advanced by the engine, so we just return the logs
        return final_logs

    def _run_ai_turns(self) -> List[str]:
        """
        Runs all consecutive AI turns until it's the human's turn again.
        """
        if not self.state or self.is_human_turn():
            return []
            
        all_ai_logs = []
        while not self.is_human_turn() and not self.is_game_over():
            current_player = self.state.get_current_player()
            persona = self.ai_personas[current_player.id - 1] 

            # AI takes its full turn until it runs out of AP
            while self.state.action_points[current_player.id] > 0 and not self.is_game_over():
                self.state.clear_turn_log()
                action = persona.choose_action(self.state, self.engine)
                
                if not action: # If persona returns None, it passes
                    action = ActionPassTurn(player_id=current_player.id)

                self.state = self.engine.process_action(self.state, action)
                all_ai_logs.extend(self.state.turn_log)

                # Break if the turn has somehow advanced to a different player
                if self.state.get_current_player().id != current_player.id:
                    break
        
        return all_ai_logs

    def is_human_turn(self) -> bool:
        if not self.state: return False
        return self.state.get_current_player().id == self.human_player_id

    def is_game_over(self) -> bool:
        if not self.state: return True
        return self.engine.is_game_over(self.state) 