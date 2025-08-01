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
from engine.actions import Action, ActionSponsorLegislation, ActionSupportLegislation, ActionOpposeLegislation, ActionDeclareCandidacy
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

        # on the GameState and its components. For now, this provides a basic structure.
        state_dict = self.state.to_dict()
        state_dict['log'] = list(self.state.turn_log)
        state_dict['is_game_over'] = self.is_game_over()


        # If it's the human's turn, add the available actions to the state payload
        if self.is_human_turn() and self.pending_ui_action:
            state_dict['valid_actions'] = self.pending_ui_action['options']
            state_dict['prompt'] = self.pending_ui_action['prompt']
            state_dict['expects_input'] = self.pending_ui_action.get('expects_input')
        elif self.is_human_turn():
            valid_actions = self.engine.get_valid_actions(self.state, self.human_player_id)
            # We need to serialize the actions as well
            state_dict['valid_actions'] = [action.to_dict() for action in valid_actions]
        else:
            state_dict['valid_actions'] = []

        state_dict['awaiting_ai_acknowledgement'] = self.awaiting_ai_acknowledgement
        
        return state_dict

    def process_action(self, action_data: Dict[str, Any]) -> List[str]:
        """
        Processes an action from the client, advances the game state,
        and runs AI turns until it's the human's turn again.
        Returns a log of events that occurred.
        """
        if self.pending_ui_action:
            return self._process_pending_action(action_data)

        action_type = action_data.get("action_type")
        
        if action_type == 'continue':
            # This is for events or other pauses
            return self._run_ai_turns()

        if action_type == "AcknowledgeAITurn":
            self.awaiting_ai_acknowledgement = False
            # Now that the AI turn is acknowledged, run the next one if it's still not the human's turn
            return self._run_ai_turns()

        # Handle UI actions that require a second step
        if action_type in ["UISponsorLegislation", "UISupportLegislation", "UIOpposeLegislation", "UIDeclareCandidacy"]:
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
        player = self.state.get_player_by_id(player_id)

        if action_type == "UISponsorLegislation":
            # Get available legislation to sponsor with richer data
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
                return ["There is no active legislation to influence right now."]

            is_support = action_type == "UISupportLegislation"
            final_action_type = "ActionSupportLegislation" if is_support else "ActionOpposeLegislation"
            prompt = "Which bill would you like to secretly support?" if is_support else "Which bill would you like to secretly oppose?"

            self.pending_ui_action = {
                "action_template": {"action_type": final_action_type, "player_id": player_id},
                "prompt": prompt,
                "options": options,
                "step": "choose_entity"
            }

        return []

    def _process_pending_action(self, action_data: Dict[str, Any]) -> List[str]:
        """Handles the multi-step action flow."""
        choice = action_data.get('choice')
        pending_action = self.pending_ui_action
        action_template = pending_action['action_template']
        player_id = action_template['player_id']
        player = self.state.get_player_by_id(player_id)

        # Step 1: Player chooses the entity (legislation, office, etc.)
        if pending_action.get("step") == "choose_entity":
            action_type = action_template['action_type']

            # For Support/Oppose, we need to ask for an amount next
            if action_type in ["ActionSupportLegislation", "ActionOpposeLegislation"]:
                pending_action["action_template"]["legislation_id"] = choice
                pending_action["step"] = "choose_amount"
                is_support = action_type == "ActionSupportLegislation"
                prompt = "support with" if is_support else "oppose with"
                pending_action["prompt"] = f"How much PC to {prompt}? (1 - {player.pc})"
                pending_action["options"] = []
                pending_action["expects_input"] = "amount"
                return [] # Wait for the amount
            
            # For other actions, this is the final step
            if action_type == 'ActionSponsorLegislation':
                action_template['legislation_id'] = choice
            elif action_type == 'ActionDeclareCandidacy':
                action_template['office_id'] = choice

            action_class = self.engine.ACTION_CLASSES[action_type]
            action = action_class.from_dict(action_template)
            self.pending_ui_action = None
            return self._execute_action_and_run_ais(action)

        # Step 2: Player chooses the amount (for Support/Oppose)
        elif pending_action.get("step") == "choose_amount":
            amount = choice
            if not isinstance(amount, int) or not (1 <= amount <= player.pc):
                # Resend the prompt on invalid input
                pending_action["prompt"] = f"Invalid amount. How much PC? (1 - {player.pc})"
                return []
            
            action_type = action_template['action_type']
            if action_type == 'ActionSupportLegislation':
                action_template['support_amount'] = amount
            elif action_type == 'ActionOpposeLegislation':
                action_template['oppose_amount'] = amount

            action_class = self.engine.ACTION_CLASSES[action_type]
            action = action_class.from_dict(action_template)
            self.pending_ui_action = None
            return self._execute_action_and_run_ais(action)

        return ["Invalid state in pending action processing."]

    def _execute_action_and_run_ais(self, action: Action) -> List[str]:
        """
        Processes a single action and then runs AI turns.
        """
        if not self.state or self.is_game_over():
            return ["Error: Game is not active."]

        self.state.clear_turn_log()
        self.state = self.engine.process_action(self.state, action)

        # After the human action, run the first AI turn if it's now an AI's turn
        if not self.is_human_turn():
            return self._run_ai_turns()


        # Capture any final logs from the processed actions or upkeep
        turn_logs = list(self.state.turn_log)
        self.state.clear_turn_log()
            
        return turn_logs

    def _run_ai_turns(self) -> List[str]:
        """
        Runs AI turns one by one, pausing for acknowledgement after each.
        """
        if self.is_game_over() or self.is_human_turn():
            return []

        # Run a single AI action
        action_logs = self.run_one_ai_action()
        
        # After the AI action, if it's not the human's turn, we need to wait for acknowledgement
        if not self.is_human_turn():
            self.awaiting_ai_acknowledgement = True
        
        return action_logs


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
            if not valid_actions: # Check if list is empty
                action = ActionPassTurn(player_id=current_player.id)
            else:
                action = persona.choose_action(self.state, valid_actions)
                if not action:
                    action = ActionPassTurn(player_id=current_player.id)

        self.state.clear_turn_log()
        self.state = self.engine.process_action(self.state, action)
        return list(self.state.turn_log)

    def is_human_turn(self) -> bool:
        if not self.state: return False
        return self.state.get_current_player().id == self.human_player_id

    def is_game_over(self) -> bool:
        if not self.state: return True
        return self.engine.is_game_over(self.state) 