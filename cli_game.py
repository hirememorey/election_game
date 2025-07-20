#!/usr/bin/env python3
"""
CLI Game Interface for Human vs AI Gameplay

This module provides a text-based interface for human players to play against AI opponents.
It focuses on clarity and ease of use for rapid gameplay testing.
"""

from typing import List, Optional
from engine.actions import (
    Action, ActionFundraise, ActionNetwork, ActionSponsorLegislation,
    ActionDeclareCandidacy, ActionUseFavor, ActionSupportLegislation,
    ActionOpposeLegislation, ActionPassTurn
)
from models.game_state import GameState
from models.components import Player
from human_vs_ai import HumanVsAIGame, HumanVsMultipleAIGame


class CLIGameView:
    """
    Text-based interface for displaying game state and accepting user input.
    
    This class handles all the user-facing aspects of the CLI game,
    including state display and command parsing.
    """
    
    def __init__(self):
        self.game = None
    
    def set_game(self, game):
        """Set the game object for the view to access."""
        self.game = game
    
    def display_game_state(self, state: GameState) -> None:
        """
        Display the current game state in a clear, readable format.
        
        Args:
            state: The current game state
        """
        print("\n" + "="*60)
        print(f"ROUND: {state.round_marker}/4  |  PHASE: {state.current_phase}")
        print("="*60)
        
        # Display turn log if any
        if state.turn_log:
            print("\n--- Recent Events ---")
            for message in state.turn_log[-3:]:  # Show last 3 messages
                print(f"  {message}")
            print("-"*40)
        
        # Display players
        print("\nPLAYERS:")
        for p in state.players:
            office_title = p.current_office.title if p.current_office else "Outsider"
            is_current = ">>>" if p.id == state.get_current_player().id and state.current_phase == "ACTION_PHASE" else "   "
            print(f"  {is_current}{p.name} ({p.archetype.title})")
            print(f"    PC: {p.pc} | Office: {office_title} | AP: {state.action_points.get(p.id, 0)}")
            if p.allies:
                print(f"    Ally: {p.allies[0].title}")
            if p.favors:
                print(f"    Favors: {len(p.favors)}")
        
        # Display current phase info
        if state.current_phase == "ACTION_PHASE":
            current_player = state.get_current_player()
            print(f"\n--- {current_player.name}'s Turn ---")
            print(f"Action Points: {state.action_points.get(current_player.id, 0)}")
        
        print("="*60)
    
    def display_available_actions(self, actions: List[Action]) -> None:
        """
        Display available actions for the current player.
        
        Args:
            actions: List of valid actions
        """
        if not actions:
            print("No actions available.")
            return
        
        print("\nAvailable Actions:")
        for i, action in enumerate(actions, 1):
            action_desc = self._get_action_description(action)
            print(f"  [{i}] {action_desc}")
        
        # Add special commands
        print("\nSpecial Commands:")
        print("  [info] View game information")
        print("  [help] Show action descriptions")
        print("  [quit] Exit the game")
    
    def _get_action_description(self, action: Action) -> str:
        """Get a human-readable description of an action."""
        if isinstance(action, ActionFundraise):
            return "Fundraise (Gain PC)"
        elif isinstance(action, ActionNetwork):
            return "Network (Gain PC + Favor)"
        elif isinstance(action, ActionSponsorLegislation):
            return f"Sponsor Legislation ({action.legislation_id})"
        elif isinstance(action, ActionDeclareCandidacy):
            return f"Declare Candidacy for {action.office_id}"
        elif isinstance(action, ActionUseFavor):
            return "Use Political Favor"
        elif isinstance(action, ActionSupportLegislation):
            return f"Support Legislation ({action.legislation_id})"
        elif isinstance(action, ActionOpposeLegislation):
            return f"Oppose Legislation ({action.legislation_id})"
        elif isinstance(action, ActionPassTurn):
            return "Pass Turn"
        else:
            return f"{action.__class__.__name__}"
    
    def prompt_for_action(self, actions: List[Action]) -> Optional[Action]:
        """
        Prompt the user to choose an action.
        
        Args:
            actions: List of valid actions
            
        Returns:
            The chosen action, or None if user wants to quit
        """
        if not actions:
            print("No actions available.")
            return None
        
        while True:
            try:
                choice = input("\nChoose action (number or command): ").strip().lower()
                
                # Handle special commands
                if choice == "quit":
                    return None
                elif choice == "info":
                    self._display_game_info()
                    continue
                elif choice == "help":
                    self._display_action_help()
                    continue
                
                # Handle numeric choice
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(actions):
                        return actions[choice_num - 1]
                    else:
                        print(f"Invalid number. Please choose 1-{len(actions)}")
                except ValueError:
                    print("Invalid input. Please enter a number or command.")
                    
            except KeyboardInterrupt:
                print("\nExiting...")
                return None
    
    def _display_game_info(self):
        """Display general game information."""
        while True:
            print("\n--- Game Information ---")
            print("  [1] View My Personal Mandate")
            print("  [2] View All Offices of Power")
            print("  [3] View Legislation Options")
            print("  [4] General Game Rules")
            print("  [5] Return to action menu")
            
            choice = input("Choose option: ").strip()
            
            if choice == '1':
                # Get the human player's mandate
                if self.game and self.game.state:
                    human_player = None
                    for player in self.game.state.players:
                        if player.name == "Human":  # Assuming human player is named "Human"
                            human_player = player
                            break
                    
                    if human_player and hasattr(human_player, 'mandate') and human_player.mandate:
                        print(f"\nYour Secret Mandate: {human_player.mandate.title}")
                        print(f"Description: {human_player.mandate.description}")
                    else:
                        print("\nMandate information not available.")
                else:
                    print("\nGame state not available.")
                    
            elif choice == '2':
                if self.game and self.game.state:
                    print("\n--- Offices of Power ---")
                    try:
                        for office in self.game.state.offices.values():
                            print(f"  - {office.title} (Tier {office.tier}): Income {office.income} PC, NPC Bonus +{office.npc_challenger_bonus}")
                    except (AttributeError, TypeError):
                        print("Office information not available.")
                else:
                    print("\nOffice information not available.")
                    
            elif choice == '3':
                if self.game and self.game.state:
                    print("\n--- Legislation Options ---")
                    try:
                        for leg in self.game.state.legislation_options.values():
                            print(f"  - {leg.title}: Cost {leg.cost}, Success Target {leg.success_target}+ PC, Critical Success {leg.critical_success_target}+ PC")
                    except (AttributeError, TypeError):
                        print("Legislation information not available.")
                else:
                    print("\nLegislation information not available.")
                    
            elif choice == '4':
                print("\n--- General Game Rules ---")
                print("This is a political strategy game where you compete for offices.")
                print("Actions cost Action Points (AP). You get 2 AP per turn.")
                print("The game has 4 rounds per term, with elections at the end.")
                print("Your goal is to win the Presidency!")
                print("Each player has a secret mandate that provides bonus influence if achieved.")
                
            elif choice == '5':
                break
            else:
                print("Invalid choice. Please enter 1-5.")
    
    def _display_action_help(self):
        """Display help for available actions."""
        print("\n--- Action Descriptions ---")
        print("Fundraise: Gain 5 PC (plus any bonuses)")
        print("Network: Gain 2 PC and one random Political Favor")
        print("Sponsor Legislation: Pay PC cost to propose a bill")
        print("Declare Candidacy: Run for an office (Round 4 only)")
        print("Use Favor: Use a political favor for special effects")
        print("Support/Oppose Legislation: Commit PC to legislation votes")
        print("Pass Turn: Skip your turn")
    
    def display_ai_action(self, player_name: str, action: Action):
        """Display what action an AI player took."""
        action_desc = self._get_action_description(action)
        print(f"\n{player_name} chose: {action_desc}")
    
    def display_election_results(self, results: dict):
        """Display election results."""
        print("\n--- Election Results ---")
        for office_id, office_results in results.items():
            print(f"\n{office_id}:")
            for candidate, score in office_results.items():
                print(f"  {candidate}: {score}")
    
    def display_game_over(self, final_scores: dict):
        """Display game over and final scores."""
        print("\n" + "#"*50)
        print("#" + "GAME OVER".center(48) + "#")
        print("#"*50)
        
        print("\nFinal Scores:")
        for player_id, score_data in final_scores.items():
            print(f"  Player {player_id}: {score_data.get('total_influence', 0)} Influence")
        
        # Find winner
        winner_id = final_scores.get('winner_id')
        winner_name = final_scores.get('winner_name')
        if winner_name:
            print(f"\nWinner: {winner_name}!")
        else:
            print("\nNo clear winner.")
    
    def prompt_for_next_turn(self, player_name: str):
        """Prompt the user to continue to the next turn."""
        print(f"\n{player_name}'s turn complete.")
        input("Press Enter to continue to the next player...")


class CLIGame:
    """
    Main CLI game interface that orchestrates human vs AI gameplay.
    """
    
    def __init__(self, ai_persona: str = "heuristic", ai_count: int = 2):
        """
        Initialize the CLI game.
        
        Args:
            ai_persona: The AI persona to use
            ai_count: Number of AI opponents
        """
        self.game = HumanVsAIGame(ai_persona, ai_count)
        self.view = CLIGameView()
        self.view.set_game(self.game)
    
    def start_game(self, human_name: str = "Human") -> None:
        """
        Start a new game and run the main game loop.
        
        Args:
            human_name: Name for the human player
        """
        print("="*50)
        print("Welcome to Election: The Game!")
        print("="*50)
        print(f"You will be playing against {self.game.ai_count} AI opponents")
        print(f"AI Persona: {self.game.ai_persona.__class__.__name__}")
        print("="*50)
        
        # Start the game
        self.game.start_new_game(human_name)
        
        # Main game loop
        while not self.game.is_game_over():
            # Display current state
            if self.game.state:
                self.view.display_game_state(self.game.state)
            
            # Check if it's human turn
            if self.game.is_human_turn():
                # Human turn
                actions = self.game.get_valid_actions()
                self.view.display_available_actions(actions)
                
                action = self.view.prompt_for_action(actions)
                if action is None:
                    print("Game ended by user.")
                    break
                
                # Process human action
                self.game.process_human_action(action)
                
            else:
                # AI turn
                current_player = self.game.get_current_player_name()
                print(f"\n{current_player} is thinking...")
                
                # Process AI turn
                self.game.process_ai_turn()
                
                # Display what the AI did
                if self.game.state and self.game.state.turn_log:
                    # Show all recent messages from the turn log
                    print(f"\n{current_player}'s actions:")
                    for message in self.game.state.turn_log:
                        if message.strip():  # Only show non-empty messages
                            print(f"  {message}")
                
                # Prompt for next turn
                self.view.prompt_for_next_turn(current_player)
        
        # Game over
        if self.game.is_game_over():
            final_scores = self.game.get_final_scores()
            self.view.display_game_over(final_scores)


class CLIMultiAIGame:
    """
    CLI game interface for playing against multiple AI opponents with different personas.
    """
    
    def __init__(self, ai_personas: Optional[List[str]] = None):
        """
        Initialize the multi-AI CLI game.
        
        Args:
            ai_personas: List of AI personas to use
        """
        self.game = HumanVsMultipleAIGame(ai_personas)
        self.view = CLIGameView()
        self.view.set_game(self.game)
    
    def start_game(self, human_name: str = "Human") -> None:
        """
        Start a new game and run the main game loop.
        
        Args:
            human_name: Name for the human player
        """
        print("="*50)
        print("Welcome to Election: The Game!")
        print("="*50)
        print(f"You will be playing against {len(self.game.ai_personas)} AI opponents:")
        for i, persona in enumerate(self.game.ai_personas):
            print(f"  AI-{i+1}: {persona.__class__.__name__}")
        print("="*50)
        
        # Start the game
        self.game.start_new_game(human_name)
        
        # Main game loop
        while not self.game.is_game_over():
            # Display current state
            if self.game.state:
                self.view.display_game_state(self.game.state)
            
            # Check if it's human turn
            if self.game.is_human_turn():
                # Human turn
                actions = self.game.get_valid_actions()
                self.view.display_available_actions(actions)
                
                action = self.view.prompt_for_action(actions)
                if action is None:
                    print("Game ended by user.")
                    break
                
                # Process human action
                self.game.process_human_action(action)
                
            else:
                # AI turn
                current_player = self.game.get_current_player_name()
                if self.game.state:
                    ai_index = self.game.state.get_current_player().id - 1
                    ai_persona = self.game.ai_personas[ai_index]
                    print(f"\n{current_player} ({ai_persona.__class__.__name__}) is thinking...")
                else:
                    print(f"\n{current_player} is thinking...")
                
                # Process AI turn
                self.game.process_ai_turn()
                
                # Display what the AI did
                if self.game.state and self.game.state.turn_log:
                    # Show only the messages from this AI's turn
                    print(f"\n{current_player}'s actions:")
                    # Since the turn log is cleared before each action, we need to show all current messages
                    # as they should all be from this AI's turn
                    for message in self.game.state.turn_log:
                        if message.strip():  # Only show non-empty messages
                            print(f"  {message}")
                
                # Prompt for next turn
                self.view.prompt_for_next_turn(current_player)
        
        # Game over
        if self.game.is_game_over():
            final_scores = self.game.get_final_scores()
            self.view.display_game_over(final_scores)


def main():
    """Main entry point for the CLI game."""
    import sys
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help" or sys.argv[1] == "-h":
            print("Usage: python3 cli_game.py [mode] [ai_persona]")
            print("\nModes:")
            print("  single    - Play against 1 AI (default)")
            print("  multi     - Play against 3 AI with different personas")
            print("\nAI Personas (for single mode):")
            print("  random, economic, legislative, balanced, heuristic")
            print("\nExamples:")
            print("  python3 cli_game.py single heuristic")
            print("  python3 cli_game.py multi")
            return
        
        mode = sys.argv[1]
        
        if mode == "multi":
            # Multi-AI game with different personas
            game = CLIMultiAIGame()
            game.start_game()
        elif mode == "single":
            # Single AI game
            ai_persona = sys.argv[2] if len(sys.argv) > 2 else "heuristic"
            game = CLIGame(ai_persona, ai_count=1)
            game.start_game()
        else:
            # Backward compatibility: treat as single AI with specified persona
            ai_persona = mode
            game = CLIGame(ai_persona, ai_count=1)
            game.start_game()
    else:
        # Default: single AI game
        game = CLIGame("heuristic", ai_count=1)
        game.start_game()


if __name__ == "__main__":
    main() 