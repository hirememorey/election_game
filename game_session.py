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
        Returns a JSON-serializable representation of the current game state.
        This method will be expanded to serialize the full game state.
        """
        if not self.state:
            return {"error": "Game not started."}

        # This is a placeholder. We will need to implement a full to_dict method
        # on the GameState and its components. For now, this provides a basic structure.
        return {
            "round_marker": self.state.round_marker,
            "current_phase": self.state.current_phase,
            "public_mood": self.state.public_mood,
            "players": [p.name for p in self.state.players],
            "current_player": self.state.get_current_player().name,
            "log": self.state.turn_log
        }

    def _run_ai_turns(self) -> List[str]:
        """
        Runs all consecutive AI turns until it's the human's turn again.
        """
        if not self.state or self.is_human_turn():
            return []
            
        all_logs = []
        while not self.is_game_over() and not self.is_human_turn():
            current_player = self.state.get_current_player()
            ai_index = current_player.id - 1
            
            # AI takes its full turn (all APs)
            while not self.is_game_over() and self.state.get_current_player().id == current_player.id:
                if self.state.action_points.get(current_player.id, 0) <= 0:
                    # This logic should be handled by the engine's advance_turn,
                    # but as a safeguard, we advance turn if AP is 0.
                    self.state = self.engine.advance_turn(self.state)
                    break

                valid_actions = self.engine.get_valid_actions(self.state, current_player.id)
                if not valid_actions:
                    self.state = self.engine.advance_turn(self.state)
                    break
                
                chosen_action = self.ai_personas[ai_index].choose_action(self.state, valid_actions)
                
                self.state.clear_turn_log()
                self.state = self.engine.process_action(self.state, chosen_action)
                all_logs.extend(self.state.turn_log)

        # After all AI turns, the engine might have triggered events. Capture those logs.
        if self.state.turn_log:
            all_logs.extend(self.state.turn_log)
            self.state.clear_turn_log()
        
        return all_logs

    def is_human_turn(self) -> bool:
        if not self.state: return False
        return self.state.get_current_player().id == self.human_player_id

    def is_game_over(self) -> bool:
        if not self.state: return True
        return self.engine.is_game_over(self.state) 