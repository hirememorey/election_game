#!/usr/bin/env python3
"""
Human vs AI Game Orchestrator

This module provides a lightweight game orchestrator that allows a human player
to play against AI opponents. It uses the existing game engine directly without
the complexity of the web server or simulation harness.
"""

from typing import List, Optional
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


class HumanVsAIGame:
    """
    Orchestrates a game between a human player and AI opponents.
    
    This class provides a simple interface for human vs AI gameplay,
    focusing on the core game mechanics without web complexity.
    """
    
    def __init__(self, ai_persona: str = "heuristic", ai_count: int = 2):
        """
        Initialize the human vs AI game.
        
        Args:
            ai_persona: The AI persona to use ("random", "economic", "legislative", "balanced", "heuristic")
            ai_count: Number of AI opponents (default: 2 for 3-player game)
        """
        self.game_data = load_game_data()
        self.engine = GameEngine(self.game_data)
        self.ai_persona = self._get_persona_class(ai_persona)()
        self.ai_count = ai_count
        self.state = None
        self.human_player_id = 0  # Human is always player 0
        
    def _get_persona_class(self, persona_name: str) -> type:
        """Get the persona class by name."""
        persona_map = {
            "random": RandomPersona,
            "economic": EconomicPersona,
            "legislative": LegislativePersona,
            "balanced": BalancedPersona,
            "heuristic": HeuristicPersona,
        }
        
        if persona_name not in persona_map:
            raise ValueError(f"Unknown persona: {persona_name}. Available: {list(persona_map.keys())}")
        
        return persona_map[persona_name]
    
    def start_new_game(self, human_name: str = "Human") -> GameState:
        """
        Start a new game with the human player and AI opponents.
        
        Args:
            human_name: Name for the human player
            
        Returns:
            GameState: The initial game state
        """
        # Create player names: Human + AI opponents
        player_names = [human_name] + [f"AI-{i+1}" for i in range(self.ai_count)]
        
        # Create new game state
        self.state = self.engine.start_new_game(player_names)
        
        # Run the first event phase immediately
        self.state = self.engine.run_event_phase(self.state)
        
        return self.state
    
    def get_current_player_name(self) -> str:
        """Get the name of the current player."""
        if not self.state:
            return "No game in progress"
        return self.state.get_current_player().name
    
    def is_human_turn(self) -> bool:
        """Check if it's the human player's turn."""
        if not self.state:
            return False
        return self.state.get_current_player().id == self.human_player_id
    
    def get_valid_actions(self) -> List[Action]:
        """Get valid actions for the current player."""
        if not self.state:
            return []
        
        current_player = self.state.get_current_player()
        return self.engine.get_valid_actions(self.state, current_player.id)
    
    def process_human_action(self, action: Action) -> GameState:
        """
        Process an action from the human player.
        
        Args:
            action: The action to process
            
        Returns:
            GameState: The updated game state
        """
        if not self.state:
            raise ValueError("No game in progress")
        
        if not self.is_human_turn():
            raise ValueError("It's not the human player's turn")
        
        self.state = self.engine.process_action(self.state, action)
        return self.state
    
    def process_ai_turn(self) -> GameState:
        """
        Process the AI player's turn.
        
        Returns:
            GameState: The updated game state
        """
        if not self.state:
            raise ValueError("No game in progress")
        
        if self.is_human_turn():
            raise ValueError("It's the human player's turn")
        
        # Get valid actions for the AI
        current_player = self.state.get_current_player()
        valid_actions = self.engine.get_valid_actions(self.state, current_player.id)
        
        # Let the AI choose an action
        chosen_action = self.ai_persona.choose_action(self.state, valid_actions)
        
        # Process the action
        self.state = self.engine.process_action(self.state, chosen_action)
        
        return self.state
    
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        if not self.state:
            return True
        return self.engine.is_game_over(self.state)
    
    def get_final_scores(self) -> dict:
        """Get the final scores if the game is over."""
        if not self.state or not self.is_game_over():
            return {}
        return self.engine.get_final_scores(self.state)
    
    def run_until_human_turn(self) -> GameState:
        """
        Run the game until it's the human player's turn.
        
        This processes all AI turns and any automated phases
        until the human player needs to make a decision.
        
        Returns:
            GameState: The current game state
        """
        if not self.state:
            raise ValueError("No game in progress")
            
        while not self.is_game_over() and not self.is_human_turn():
            # Process AI turn
            self.process_ai_turn()
            
            # Handle any automated phases (elections, legislation resolution, etc.)
            self._handle_automated_phases()
        
        return self.state
    
    def _handle_automated_phases(self):
        """Handle phases that don't require player input."""
        if not self.state:
            return
        
        # Handle legislation resolution if needed
        if self.state.awaiting_legislation_resolution:
            # For now, we'll skip legislation resolution in CLI mode
            # This can be enhanced later
            pass
        
        # Handle election resolution if needed
        if self.state.awaiting_election_resolution:
            # For now, we'll skip election resolution in CLI mode
            # This can be enhanced later
            pass
        
        # Handle results acknowledgement if needed
        if self.state.awaiting_results_acknowledgement:
            # For now, we'll skip results acknowledgement in CLI mode
            # This can be enhanced later
            pass


class HumanVsMultipleAIGame:
    """
    Enhanced orchestrator for games with multiple AI players with different personas.
    
    This class allows you to play against multiple AI opponents, each with their own persona.
    """
    
    def __init__(self, ai_personas: Optional[List[str]] = None):
        """
        Initialize the human vs multiple AI game.
        
        Args:
            ai_personas: List of AI personas to use. Default: ["heuristic", "economic", "legislative"]
        """
        self.game_data = load_game_data()
        self.engine = GameEngine(self.game_data)
        
        # Default to 3 AI opponents with different personas
        if ai_personas is None:
            ai_personas = ["heuristic", "economic", "legislative"]
        
        self.ai_personas = [self._get_persona_class(persona)() for persona in ai_personas]
        self.state = None
        self.human_player_id = 0  # Human is always player 0
        
    def _get_persona_class(self, persona_name: str) -> type:
        """Get the persona class by name."""
        persona_map = {
            "random": RandomPersona,
            "economic": EconomicPersona,
            "legislative": LegislativePersona,
            "balanced": BalancedPersona,
            "heuristic": HeuristicPersona,
        }
        
        if persona_name not in persona_map:
            raise ValueError(f"Unknown persona: {persona_name}. Available: {list(persona_map.keys())}")
        
        return persona_map[persona_name]
    
    def start_new_game(self, human_name: str = "Human") -> GameState:
        """
        Start a new game with the human player and multiple AI opponents.
        
        Args:
            human_name: Name for the human player
            
        Returns:
            GameState: The initial game state
        """
        # Create player names: Human + AI opponents
        player_names = [human_name] + [f"AI-{i+1}" for i in range(len(self.ai_personas))]
        
        # Create new game state
        self.state = self.engine.start_new_game(player_names)
        
        # Run the first event phase immediately
        self.state = self.engine.run_event_phase(self.state)
        
        return self.state
    
    def get_current_player_name(self) -> str:
        """Get the name of the current player."""
        if not self.state:
            return "No game in progress"
        return self.state.get_current_player().name
    
    def is_human_turn(self) -> bool:
        """Check if it's the human player's turn."""
        if not self.state:
            return False
        return self.state.get_current_player().id == self.human_player_id
    
    def get_valid_actions(self) -> List[Action]:
        """Get valid actions for the current player."""
        if not self.state:
            return []
        
        current_player = self.state.get_current_player()
        return self.engine.get_valid_actions(self.state, current_player.id)
    
    def process_human_action(self, action: Action) -> GameState:
        """
        Process an action from the human player.
        
        Args:
            action: The action to process
            
        Returns:
            GameState: The updated game state
        """
        if not self.state:
            raise ValueError("No game in progress")
        
        if not self.is_human_turn():
            raise ValueError("It's not the human player's turn")
        
        self.state = self.engine.process_action(self.state, action)
        return self.state
    
    def process_ai_turn(self) -> GameState:
        """
        Process the AI player's turn.
        
        Returns:
            GameState: The updated game state
        """
        if not self.state:
            raise ValueError("No game in progress")
        
        if self.is_human_turn():
            raise ValueError("It's the human player's turn")
        
        # Get the current AI player
        current_player = self.state.get_current_player()
        ai_index = current_player.id - 1  # AI players start at index 1
        
        # Get valid actions for the AI
        valid_actions = self.engine.get_valid_actions(self.state, current_player.id)
        
        # Let the AI choose an action
        chosen_action = self.ai_personas[ai_index].choose_action(self.state, valid_actions)
        
        # Process the action
        self.state = self.engine.process_action(self.state, chosen_action)
        
        return self.state
    
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        if not self.state:
            return True
        return self.engine.is_game_over(self.state)
    
    def get_final_scores(self) -> dict:
        """Get the final scores if the game is over."""
        if not self.state or not self.is_game_over():
            return {}
        return self.engine.get_final_scores(self.state)
    
    def run_until_human_turn(self) -> GameState:
        """
        Run the game until it's the human player's turn.
        
        This processes all AI turns and any automated phases
        until the human player needs to make a decision.
        
        Returns:
            GameState: The current game state
        """
        if not self.state:
            raise ValueError("No game in progress")
            
        while not self.is_game_over() and not self.is_human_turn():
            # Process AI turn
            self.process_ai_turn()
            
            # Handle any automated phases (elections, legislation resolution, etc.)
            self._handle_automated_phases()
        
        return self.state
    
    def _handle_automated_phases(self):
        """Handle phases that don't require player input."""
        if not self.state:
            return
        
        # Handle legislation resolution if needed
        if self.state.awaiting_legislation_resolution:
            # For now, we'll skip legislation resolution in CLI mode
            # This can be enhanced later
            pass
        
        # Handle election resolution if needed
        if self.state.awaiting_election_resolution:
            # For now, we'll skip election resolution in CLI mode
            # This can be enhanced later
            pass
        
        # Handle results acknowledgement if needed
        if self.state.awaiting_results_acknowledgement:
            # For now, we'll skip results acknowledgement in CLI mode
            # This can be enhanced later
            pass 