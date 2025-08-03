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

        # The engine is now the single source of truth for valid actions,
        # including system actions and the state of pending UI actions.
        if self.is_human_turn():
            valid_actions = self.engine.get_valid_actions(self.state, self.human_player_id)
            state_dict['valid_actions'] = [action.to_dict() for action in valid_actions]
        else:
            # For AI turns, we can still get system actions if they exist
            system_actions = self.engine.get_valid_system_actions(self.state)
            state_dict['valid_actions'] = [action.to_dict() for action in system_actions]

        # The prompt and options for UI actions now come directly from the state
        if self.state.pending_ui_action:
             state_dict['prompt'] = self.state.pending_ui_action.get('prompt')
             state_dict['options'] = self.state.pending_ui_action.get('options')
             state_dict['expects_input'] = self.state.pending_ui_action.get('expects_input')

        return state_dict

    def process_action(self, action_data: Dict[str, Any]) -> List[str]:
        """
        Processes a single action from the client, then runs AI turns if necessary.
        This is the main entry point for all game interactions.
        """
        action_to_execute: Optional[Action] = None

        # The new architecture simplifies this method dramatically.
        # We just build the action and execute it. The engine handles all state changes.
        try:
            # The frontend might send a simple choice for a pending action.
            # We need to construct the correct action from it.
            if self.state and self.state.pending_ui_action and 'choice' in action_data:
                pending_action_info = self.state.pending_ui_action
                next_action_type = pending_action_info.get('next_action')
                if next_action_type:
                    action_class = ACTION_CLASSES.get(next_action_type)
                    if action_class:
                        # Construct the action based on what the pending state expects
                        if pending_action_info.get('expects_input') == 'amount':
                            action_to_execute = action_class(player_id=self.human_player_id, amount=action_data['choice'])
                        else:
                            action_to_execute = action_class(player_id=self.human_player_id, legislation_id=action_data['choice'])
            else:
                action_to_execute = self.engine.action_from_dict(action_data)

        except Exception as e:
            print(f"Error creating action from dict: {e}")
            # The engine will log this error to the game state if it's a valid action type.
            # If not, we can't do much.

        if action_to_execute:
            self._execute_action(action_to_execute)

        # The AI turn should run if it's not the human's turn after the action.
        if not self.is_human_turn():
            self.run_ai_turn()

        return list(self.state.turn_log) if self.state else []

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
            # This is now handled by the frontend implicitly by observing state changes.
            pass

    def _execute_action(self, action: Action):
        """Processes a single, concrete action through the engine."""
        if not self.state or self.is_game_over():
            return
        try:
            self.state = self.engine.process_action(self.state, action)
        except Exception as e:
            print(f"Error executing action '{action.to_dict().get('action_type')}': {e}")
            # The engine should handle logging this error to the game state
            # self.state.add_log(f"Error: {e}")

    def is_human_turn(self) -> bool:
        if not self.state: return False
        return self.state.get_current_player().id == self.human_player_id

    def is_game_over(self) -> bool:
        if not self.state: return True
        return self.engine.is_game_over(self.state) 