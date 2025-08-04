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
from engine import resolvers
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
        self.state = self._run_event_phase(self.state)

    def _run_event_phase(self, state: GameState) -> GameState:
        """Draws an event card and resolves it using the resolver module."""
        state.clear_turn_log()
        
        new_state = resolvers.resolve_event_card(state)
        
        new_state.current_phase = "ACTION_PHASE"
        new_state.current_player_index = 0
        
        return new_state

    def _advance_game_flow(self, state: GameState) -> GameState:
        """
        The single, authoritative function for advancing the game state after an action.
        This function checks for and executes turn, round, and term advancements.
        It is the sole owner of game flow logic.
        """
        # 1. Check if the current player's turn is over
        current_player = state.get_current_player()
        if state.action_points.get(current_player.id, 0) <= 0:
            state.add_log(f"{current_player.name}'s turn ends.")
            state.current_player_index = (state.current_player_index + 1) % len(state.players)
            state.add_log(f"It is now {state.get_current_player().name}'s turn.")

        # 2. Check if the entire round is over
        all_players_out_of_ap = all(state.action_points.get(p.id, 0) <= 0 for p in state.players)
        if all_players_out_of_ap:
            state = self._run_upkeep_phase(state)

        return state

    def _run_upkeep_phase(self, state: GameState) -> GameState:
        """Runs the entire Upkeep Phase automatically."""
        state.add_log("\n--- ROUND COMPLETE ---")
        state.add_log("All players have used their action points. Moving to upkeep phase.")
        state.current_phase = "UPKEEP_PHASE"
        state.add_log("\n--- UPKEEP PHASE ---")
        state = resolvers.resolve_upkeep(state)
        state.round_marker += 1
        
        if state.round_marker >= 5:
            state = self._run_legislation_session(state)
        else:
            state.add_log(f"\n--- ROUND {state.round_marker} ---")
            state.add_log("\n--- EVENT PHASE ---")
            state = self._run_event_phase(state)
        
        return state

    def _run_legislation_session(self, state: GameState) -> GameState:
        """Triggers the legislation session where all pending legislation is resolved."""
        state.round_marker = 4 
        state.add_log("\n--- END OF TERM ---")
        state.add_log("Round 4 complete. Moving to legislation session.")
        state.current_phase = "LEGISLATION_PHASE"
        state.add_log("\n--- LEGISLATION SESSION ---")
        
        if not state.term_legislation:
            state.add_log("No legislation was sponsored this term. Moving to elections.")
            return self._run_election_phase(state)
        
        state.awaiting_legislation_resolution = True
        state.add_log("Click 'Resolve Legislation' to reveal all secret commitments and determine outcomes.")
        return state

    def _run_election_phase(self, state: GameState) -> GameState:
        """Triggers the election resolutions."""
        state.current_phase = "ELECTION_PHASE"
        state.add_log("\n--- ELECTION PHASE ---")
        state.awaiting_election_resolution = True
        state.add_log("Click 'Resolve Elections' to determine office winners and start the new term.")
        return state

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
            # Also include system actions for human players when appropriate
            system_actions = self.engine.get_valid_system_actions(self.state)
            all_actions = valid_actions + system_actions
            state_dict['valid_actions'] = [action.to_dict() for action in all_actions]
        else:
            # For AI turns, we can still get system actions if they exist
            system_actions = self.engine.get_valid_system_actions(self.state)
            state_dict['valid_actions'] = [action.to_dict() for action in system_actions]

        # The prompt and options for UI actions now come directly from the state
        if self.state.pending_ui_action:
             state_dict['prompt'] = self.state.pending_ui_action.get('prompt')
             state_dict['options'] = self.state.pending_ui_action.get('options')
             state_dict['expects_input'] = self.state.pending_ui_action.get('expects_input')
             print(f"DEBUG: pending_ui_action = {self.state.pending_ui_action}")
             print(f"DEBUG: expects_input = {self.state.pending_ui_action.get('expects_input')}")

        return state_dict

    def process_human_action(self, action_data: Dict[str, Any]) -> List[str]:
        """
        Processes a single action from the human client, updates the state,
        and advances the game flow by one step. Does not loop.
        """
        action_to_execute: Optional[Action] = None

        try:
            if self.state and self.state.pending_ui_action and 'choice' in action_data:
                pending_action_info = self.state.pending_ui_action
                next_action_type = pending_action_info.get('next_action')
                print(f"Processing choice: {action_data['choice']} for action type: {next_action_type}")
                
                if next_action_type:
                    action_class = ACTION_CLASSES.get(next_action_type)
                    if action_class:
                        if pending_action_info.get('expects_input') == 'amount':
                            print(f"Creating amount action: {next_action_type} with amount {action_data['choice']}")
                            action_to_execute = action_class(player_id=self.human_player_id, amount=action_data['choice'])
                        else:
                            # For choice-based actions (like legislation selection), use the choice parameter
                            print(f"Creating choice action: {next_action_type} with choice {action_data['choice']}")
                            
                            # Special handling for ActionSubmitOfficeChoice which needs committed_pc
                            if next_action_type == 'ActionSubmitOfficeChoice':
                                # For candidacy declaration, committed_pc should be 0 (no additional commitment)
                                # The office cost is handled separately in the resolver
                                office_id = action_data['choice']
                                
                                print(f"Creating ActionSubmitOfficeChoice with office_id={office_id}, committed_pc=0")
                                action_to_execute = action_class(
                                    player_id=self.human_player_id, 
                                    choice=action_data['choice'],
                                    committed_pc=0
                                )
                            else:
                                action_to_execute = action_class(player_id=self.human_player_id, choice=action_data['choice'])
                    else:
                        print(f"Action class not found for: {next_action_type}")
            else:
                # Ensure player_id is included for actions that need it
                if 'player_id' not in action_data:
                    action_data['player_id'] = self.human_player_id
                action_to_execute = self.engine.action_from_dict(action_data)

        except Exception as e:
            print(f"Error creating action from dict: {e}")
            import traceback
            traceback.print_exc()

        if action_to_execute:
            self._execute_action(action_to_execute)

        if self.state:
            self.state = self._advance_game_flow(self.state)

        return list(self.state.turn_log) if self.state else []

    def process_ai_turn(self) -> List[str]:
        """
        Selects and executes a single action for the current AI player,
        advances the game flow, and returns the log. Does not loop.
        """
        if self.is_game_over() or self.is_human_turn():
            return []

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
        
        if self.state:
            self.state = self._advance_game_flow(self.state)
            
        return list(self.state.turn_log) if self.state else []

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