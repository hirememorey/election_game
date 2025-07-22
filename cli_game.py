#!/usr/bin/env python3
"""
Enhanced CLI Game Interface for Human vs AI Gameplay

This module provides a text-based interface for human players to play against AI opponents.
It focuses on clarity, enjoyment, and ease of use for rapid gameplay testing.
"""

import os
import sys
import time
from typing import List, Optional
from engine.actions import (
    Action, ActionFundraise, ActionNetwork, ActionSponsorLegislation,
    ActionDeclareCandidacy, ActionUseFavor, ActionSupportLegislation,
    ActionOpposeLegislation, ActionPassTurn
)
from models.game_state import GameState
from models.components import Player
from human_vs_ai import HumanVsAIGame, HumanVsMultipleAIGame


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    MAGENTA = '\033[95m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


class CLIGameView:
    """
    Enhanced text-based interface for displaying game state and accepting user input.
    
    This class handles all the user-facing aspects of the CLI game,
    including state display and command parsing with improved UX.
    """
    
    def __init__(self):
        self.game = None
        self.clear_screen = os.name == 'nt'  # Windows compatibility
    
    def set_game(self, game):
        """Set the game object for the view to access."""
        self.game = game
    
    def clear_terminal(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_game_state(self, state: GameState) -> None:
        """
        Display the current game state in a clear, readable format with enhanced styling.
        
        Args:
            state: The current game state
        """
        self.clear_terminal()
        
        # Header with game progress
        print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}🗳️  ELECTION: THE GAME{Colors.END}")
        print(f"{Colors.BOLD}{'='*70}{Colors.END}")
        
        # Game progress bar
        progress = state.round_marker / 4.0
        bar_length = 40
        filled_length = int(bar_length * progress)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        print(f"\n{Colors.CYAN}Game Progress: [{bar}] {state.round_marker}/4 Rounds{Colors.END}")
        print(f"{Colors.CYAN}Current Phase: {state.current_phase.replace('_', ' ').title()}{Colors.END}")
        print(f"{Colors.CYAN}Public Mood: {state.public_mood}{Colors.END}")
        
        # Display turn log if any
        if state.turn_log:
            print(f"\n{Colors.YELLOW}📰 Recent Events:{Colors.END}")
            for message in state.turn_log[-3:]:  # Show last 3 messages
                if message.strip():
                    print(f"  {Colors.YELLOW}•{Colors.END} {message}")
            print(f"{Colors.YELLOW}{'─'*50}{Colors.END}")
        
        # Display players with enhanced formatting
        print(f"\n{Colors.BOLD}👥 PLAYERS:{Colors.END}")
        for p in state.players:
            office_title = p.current_office.title if p.current_office else "Outsider"
            is_current = f"{Colors.GREEN}▶▶▶{Colors.END}" if p.id == state.get_current_player().id and state.current_phase == "ACTION_PHASE" else "   "
            
            # Player header
            print(f"\n  {is_current} {Colors.BOLD}{p.name}{Colors.END} ({p.archetype.title})")
            
            # Player stats
            ap = state.action_points.get(p.id, 0)
            print(f"    {Colors.CYAN}💰 PC: {p.pc}{Colors.END} | {Colors.BLUE}🏛️  Office: {office_title}{Colors.END} | {Colors.GREEN}⚡ AP: {ap}{Colors.END}")
            
            # Allies and favors
            if p.allies:
                print(f"    {Colors.YELLOW}🤝 Ally: {p.allies[0].title}{Colors.END}")
            if p.favors:
                print(f"    {Colors.YELLOW}🎁 Favors: {len(p.favors)} available{Colors.END}")
        
        # Current player turn info
        if state.current_phase == "ACTION_PHASE":
            current_player = state.get_current_player()
            print(f"\n{Colors.BOLD}{Colors.GREEN}🎯 {current_player.name}'s Turn{Colors.END}")
            print(f"{Colors.GREEN}Action Points Available: {state.action_points.get(current_player.id, 0)}{Colors.END}")
        
        print(f"\n{Colors.BOLD}{'='*70}{Colors.END}")
    
    def display_available_actions(self, actions: List[Action], state: GameState) -> None:
        """
        Display available actions for the current player with enhanced descriptions.
        
        Args:
            actions: List of valid actions
            state: The current game state
        """
        if not actions:
            print(f"{Colors.RED}No actions available.{Colors.END}")
            return
        
        print(f"\n{Colors.BOLD}🎮 Available Actions:{Colors.END}")
        
        # Consolidate legislation actions into a single menu item
        action_map = {}
        has_legislation_action = False
        
        # Basic actions
        i = 1
        for action in actions:
            if not isinstance(action, (ActionSponsorLegislation, ActionSupportLegislation, ActionOpposeLegislation)):
                action_map[i] = action
                action_desc = self._get_enhanced_action_description(action)
                print(f"  {Colors.CYAN}[{i}]{Colors.END} {action_desc}")
                i += 1
        
        # Legislation actions
        if any(isinstance(a, (ActionSponsorLegislation, ActionSupportLegislation, ActionOpposeLegislation)) for a in actions):
            has_legislation_action = True
            action_map['l'] = 'legislation'
            print(f"  {Colors.CYAN}[L]{Colors.END} {Colors.YELLOW}📜 Legislation Actions{Colors.END} - Sponsor, support, or oppose a bill")
        
        # Add pass turn if available
        pass_action = next((a for a in actions if isinstance(a, ActionPassTurn)), None)
        if pass_action:
            action_map['p'] = pass_action
            print(f"  {Colors.CYAN}[P]{Colors.END} {self._get_enhanced_action_description(pass_action)}")
        
        # Add special commands
        print(f"\n{Colors.BOLD}🔧 Special Commands:{Colors.END}")
        print(f"  {Colors.YELLOW}[info]{Colors.END} View detailed game information")
        print(f"  {Colors.YELLOW}[help]{Colors.END} Show action descriptions")
        print(f"  {Colors.YELLOW}[quit]{Colors.END} Exit the game")
        
        return action_map

    def _get_enhanced_action_description(self, action: Action) -> str:
        """Get a detailed, human-readable description of an action."""
        if isinstance(action, ActionFundraise):
            return f"{Colors.GREEN}💰 Fundraise{Colors.END} - Gain Political Capital through fundraising efforts"
        elif isinstance(action, ActionNetwork):
            return f"{Colors.BLUE}🤝 Network{Colors.END} - Build connections to gain PC and potential favors"
        elif isinstance(action, ActionSponsorLegislation):
            bill = self.game.state.legislation_options.get(action.legislation_id)
            return f"{Colors.YELLOW}📜 Sponsor Legislation{Colors.END} - Propose {bill.title} (Cost: {bill.cost} PC)"
        elif isinstance(action, ActionDeclareCandidacy):
            office = self.game.state.offices.get(action.office_id)
            return f"{Colors.CYAN}🏛️  Declare Candidacy{Colors.END} - Run for {office.title}"
        elif isinstance(action, ActionUseFavor):
            return f"{Colors.MAGENTA}🎁 Use Favor{Colors.END} - Call in a political favor"
        elif isinstance(action, ActionSupportLegislation):
            return f"{Colors.GREEN}✅ Support Legislation{Colors.END} - Commit PC to support a bill"
        elif isinstance(action, ActionOpposeLegislation):
            return f"{Colors.RED}❌ Oppose Legislation{Colors.END} - Commit PC to oppose a bill"
        elif isinstance(action, ActionPassTurn):
            return f"{Colors.YELLOW}⏭️  Pass Turn{Colors.END} - Skip your turn"
        else:
            return f"{Colors.WHITE}{action.__class__.__name__}{Colors.END}"
    
    def prompt_for_action(self, actions: List[Action], state: GameState) -> Optional[Action]:
        """
        Prompt the user to select an action with enhanced input handling.
        
        Args:
            actions: List of valid actions
            state: The current game state
            
        Returns:
            Selected action or None if user wants to quit
        """
        action_map = self.display_available_actions(actions, state)
        
        while True:
            try:
                choice = input(f"\n{Colors.BOLD}Enter your choice: {Colors.END}").strip().lower()
                
                # Handle special commands
                if choice == 'quit':
                    return None
                elif choice == 'info':
                    self._display_game_info()
                    self.display_available_actions(actions, state)
                    continue
                elif choice == 'help':
                    self._display_action_help()
                    self.display_available_actions(actions, state)
                    continue
                
                # Handle legislation sub-menu
                if choice == 'l' and 'l' in action_map:
                    return self._prompt_for_legislation_action(actions)
                
                # Handle numeric and character choices
                try:
                    key = int(choice) if choice.isdigit() else choice
                    if key in action_map:
                        return action_map[key]
                    else:
                        print(f"{Colors.RED}Invalid choice. Please enter a valid option.{Colors.END}")
                except (ValueError, KeyError):
                    print(f"{Colors.RED}Please enter a valid option from the list.{Colors.END}")
                    
            except KeyboardInterrupt:
                print(f"\n{Colors.YELLOW}Game interrupted. Exiting...{Colors.END}")
                return None
    
    def _prompt_for_legislation_action(self, all_actions: List[Action]) -> Optional[Action]:
        """Handle the legislation sub-menu."""
        state = self.game.state
        
        # Scenario A: A bill is pending
        if state.pending_legislation and not state.pending_legislation.resolved:
            bill = state.legislation_options[state.pending_legislation.legislation_id]
            print(f"\n--- {Colors.YELLOW}The '{bill.title}' is currently pending.{Colors.END} ---")
            print("What is your stance?")
            
            support_action = next((a for a in all_actions if isinstance(a, ActionSupportLegislation)), None)
            oppose_action = next((a for a in all_actions if isinstance(a, ActionOpposeLegislation)), None)
            
            options = {}
            if support_action:
                options['1'] = ("✅ Support the Legislation", support_action)
            if oppose_action:
                options['2'] = ("❌ Oppose the Legislation", oppose_action)
            options['3'] = ("⏪ Back to Main Menu", None)
            
            for key, (desc, _) in options.items():
                print(f"  [{key}] {desc}")
            
            while True:
                choice = input(f"\nEnter your choice: ").strip().lower()
                if choice in options:
                    desc, action = options[choice]
                    if action:
                        # Prompt for PC amount
                        while True:
                            try:
                                amount_str = input(f"How much PC to commit? (You have {state.get_current_player().pc}) ").strip()
                                amount = int(amount_str)
                                if amount > 0 and amount <= state.get_current_player().pc:
                                    if isinstance(action, ActionSupportLegislation):
                                        action.support_amount = amount
                                    else:
                                        action.oppose_amount = amount
                                    return action
                                else:
                                    print(f"{Colors.RED}Invalid amount. Please enter a number between 1 and {state.get_current_player().pc}.{Colors.END}")
                            except ValueError:
                                print(f"{Colors.RED}Please enter a valid number.{Colors.END}")
                    else:
                        return "back" # Sentinel value to re-prompt
                else:
                    print(f"{Colors.RED}Invalid choice.{Colors.END}")

        # Scenario B: No bill is pending
        else:
            print(f"\n--- {Colors.YELLOW}Sponsor a New Bill{Colors.END} ---")
            sponsor_actions = [a for a in all_actions if isinstance(a, ActionSponsorLegislation)]
            
            options = {}
            for i, action in enumerate(sponsor_actions, 1):
                bill = state.legislation_options[action.legislation_id]
                options[str(i)] = (f"Sponsor {bill.title} (Cost: {bill.cost} PC)", action)
            
            options[str(len(sponsor_actions) + 1)] = ("⏪ Back to Main Menu", None)

            for key, (desc, _) in options.items():
                print(f"  [{key}] {desc}")
            
            while True:
                choice = input(f"\nEnter your choice: ").strip().lower()
                if choice in options:
                    desc, action = options[choice]
                    if action:
                        return action
                    else:
                        return "back" # Sentinel value to re-prompt
                else:
                    print(f"{Colors.RED}Invalid choice.{Colors.END}")

    def _display_game_info(self):
        """Display detailed game information."""
        if not self.game or not self.game.state:
            return
        
        state = self.game.state
        print(f"\n{Colors.BOLD}{Colors.HEADER}📊 GAME INFORMATION{Colors.END}")
        print(f"{Colors.BOLD}{'='*50}{Colors.END}")
        
        # Game state info
        print(f"{Colors.CYAN}Round: {state.round_marker}/4{Colors.END}")
        print(f"{Colors.CYAN}Phase: {state.current_phase}{Colors.END}")
        print(f"{Colors.CYAN}Public Mood: {state.public_mood}{Colors.END}")
        
        # Current player's mandate (if it's a human turn)
        if state.current_phase == "ACTION_PHASE" and self.game.is_human_turn():
            current_player = state.get_current_player()
            print(f"\n{Colors.BOLD}🎯 Your Personal Mandate:{Colors.END}")
            print(f"  {Colors.YELLOW}{current_player.mandate.title}{Colors.END}")
            print(f"  {Colors.WHITE}{current_player.mandate.description}{Colors.END}")
        
        # Available offices
        if state.offices:
            print(f"\n{Colors.BOLD}🏛️  Available Offices:{Colors.END}")
            for office_id, office in state.offices.items():
                print(f"  {office.title} (Tier {office.tier}) - Cost: {office.candidacy_cost} PC")
        
        # Available legislation
        if state.legislation_options:
            print(f"\n{Colors.BOLD}📜 Available Legislation:{Colors.END}")
            for leg_id, legislation in state.legislation_options.items():
                print(f"  {legislation.title} - Cost: {legislation.cost} PC")
        
        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
    
    def _display_action_help(self):
        """Display detailed help for all actions."""
        print(f"\n{Colors.BOLD}{Colors.HEADER}❓ ACTION HELP{Colors.END}")
        print(f"{Colors.BOLD}{'='*50}{Colors.END}")
        
        help_text = """
💰 Fundraise: Gain Political Capital through fundraising efforts
🤝 Network: Build connections to gain PC and potential favors  
📜 Sponsor Legislation: Propose new legislation (costs PC)
🏛️  Declare Candidacy: Run for office (costs PC)
🎁 Use Favor: Call in a political favor for special effects
✅ Support Legislation: Commit PC to support a bill
❌ Oppose Legislation: Commit PC to oppose a bill
⏭️  Pass Turn: Skip your turn

💡 Tips:
- PC (Political Capital) is your primary resource
- Action Points (AP) limit how many actions you can take
- Favors provide special abilities and effects
- Legislation can significantly impact the game
- Timing is crucial - choose when to act carefully
        """
        print(help_text)
        input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.END}")
    
    def display_ai_action(self, player_name: str, action: Action):
        """Display AI action with enhanced formatting."""
        action_desc = self._get_enhanced_action_description(action)
        print(f"\n{Colors.BLUE}🤖 {player_name} chose: {action_desc}{Colors.END}")
    
    def display_election_results(self, results: dict):
        """Display election results with enhanced formatting."""
        print(f"\n{Colors.BOLD}{Colors.HEADER}🗳️  ELECTION RESULTS{Colors.END}")
        print(f"{Colors.BOLD}{'='*50}{Colors.END}")
        
        for office_id, result in results.items():
            winner = result.get('winner', 'No winner')
            print(f"{Colors.GREEN}🏆 {office_id}: {winner}{Colors.END}")
    
    def display_game_over(self, final_scores: dict):
        """Display game over screen with enhanced formatting."""
        print(f"\n{Colors.BOLD}{Colors.HEADER}🎉 GAME OVER{Colors.END}")
        print(f"{Colors.BOLD}{'='*50}{Colors.END}")
        
        # Sort players by score
        sorted_scores = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
        
        print(f"\n{Colors.BOLD}🏆 Final Standings:{Colors.END}")
        for i, (player_name, score) in enumerate(sorted_scores, 1):
            if i == 1:
                print(f"  {Colors.YELLOW}🥇 {player_name}: {score} points{Colors.END}")
            elif i == 2:
                print(f"  {Colors.CYAN}🥈 {player_name}: {score} points{Colors.END}")
            elif i == 3:
                print(f"  {Colors.RED}🥉 {player_name}: {score} points{Colors.END}")
            else:
                print(f"  {Colors.WHITE}{i}. {player_name}: {score} points{Colors.END}")
        
        winner = sorted_scores[0][0] if sorted_scores else "No winner"
        print(f"\n{Colors.BOLD}{Colors.GREEN}🎊 Congratulations to {winner}! 🎊{Colors.END}")
    
    def prompt_for_next_turn(self, player_name: str):
        """Prompt for next turn with enhanced UX."""
        print(f"\n{Colors.YELLOW}Press Enter to continue to {player_name}'s turn...{Colors.END}")
        try:
            input()
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Game interrupted. Exiting...{Colors.END}")
            sys.exit(0)


class CLIGame:
    """
    Enhanced CLI game interface that orchestrates human vs AI gameplay.
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
        Start a new game and run the main game loop with enhanced UX.
        
        Args:
            human_name: Name for the human player
        """
        self.view.clear_terminal()
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}🗳️  Welcome to Election: The Game! 🗳️{Colors.END}")
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.CYAN}You will be playing against {self.game.ai_count} AI opponents{Colors.END}")
        print(f"{Colors.CYAN}AI Persona: {self.game.ai_persona.__class__.__name__}{Colors.END}")
        print(f"{Colors.YELLOW}💡 Type 'help' during your turn for action descriptions{Colors.END}")
        print(f"{Colors.YELLOW}💡 Type 'info' to view detailed game information{Colors.END}")
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")
        
        # Start the game
        self.game.start_new_game(human_name)
        
        # Main game loop
        while not self.game.is_game_over():
            # Clear turn log at the start of each player's turn to prevent duplicates
            self.game.clear_turn_log()
            
            # Display current state
            if self.game.state:
                self.view.display_game_state(self.game.state)
            
            # Check if it's human turn
            if self.game.is_human_turn():
                # Human turn
                action_to_process = None
                while not action_to_process:
                    actions = self.game.get_valid_actions()
                    action = self.view.prompt_for_action(actions, self.game.state)
                    
                    if action is None: # User chose to quit
                        action_to_process = "quit"
                        break
                    
                    if action != "back":
                        action_to_process = action
                    else:
                        # User backed out of sub-menu, redisplay top-level actions
                        self.view.display_game_state(self.game.state)
                
                if action_to_process == "quit":
                    print(f"{Colors.YELLOW}Game ended by user.{Colors.END}")
                    break
                
                # Process human action
                self.game.process_human_action(action_to_process)
                
            else:
                # AI turn - run their entire turn automatically
                if not self.game.is_game_over():
                    current_ai_player_name = self.game.get_current_player_name()
                    print(f"\n{Colors.BLUE}🤖 {current_ai_player_name} is thinking...{Colors.END}")
                    time.sleep(1)
                    
                    # Get the complete log of the AI's turn from the engine
                    all_ai_actions_log = self.game.process_ai_turn()

                    # After the AI's turn is fully over, display all their actions.
                    if all_ai_actions_log:
                        print(f"\n{Colors.BLUE}🤖 {current_ai_player_name}'s actions:{Colors.END}")
                        for message in all_ai_actions_log:
                            if message.strip():
                                if "secretly commits" in message and current_ai_player_name != "Human":
                                    print(f"  {Colors.BLUE}•{Colors.END} {current_ai_player_name} made a secret commitment.")
                                else:
                                    print(f"  {Colors.BLUE}•{Colors.END} {message}")

                    # Prompt to continue to the next player's turn
                    if not self.game.is_game_over():
                        next_player_name = self.game.get_current_player_name()
                        self.view.prompt_for_next_turn(next_player_name)
        
        # Game over
        if self.game.is_game_over():
            final_scores = self.game.get_final_scores()
            self.view.display_game_over(final_scores)


class CLIMultiAIGame:
    """
    Enhanced CLI game interface for playing against multiple AI opponents with different personas.
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
        Start a new game and run the main game loop with enhanced UX.
        
        Args:
            human_name: Name for the human player
        """
        self.view.clear_terminal()
        print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}🗳️  Welcome to Election: The Game! 🗳️{Colors.END}")
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.CYAN}You will be playing against {len(self.game.ai_personas)} AI opponents{Colors.END}")
        print(f"{Colors.CYAN}AI Personas: {', '.join([p.__class__.__name__ for p in self.game.ai_personas])}{Colors.END}")
        print(f"{Colors.YELLOW}💡 Type 'help' during your turn for action descriptions{Colors.END}")
        print(f"{Colors.YELLOW}💡 Type 'info' to view detailed game information{Colors.END}")
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")
        
        # Start the game
        self.game.start_new_game(human_name)
        
        # Main game loop
        while not self.game.is_game_over():
            # Clear turn log at the start of each player's turn to prevent duplicates
            self.game.clear_turn_log()

            # Display current state
            if self.game.state:
                self.view.display_game_state(self.game.state)
            
            # Check if it's human turn
            if self.game.is_human_turn():
                # Human turn
                actions = self.game.get_valid_actions()
                self.view.display_available_actions(actions, self.game.state)
                
                action = self.view.prompt_for_action(actions, self.game.state)
                if action is None:
                    print(f"{Colors.YELLOW}Game ended by user.{Colors.END}")
                    break
                
                # Process human action
                self.game.process_human_action(action)
                
            else:
                # AI turn - run their entire turn automatically
                if not self.game.is_game_over():
                    current_ai_player_name = self.game.get_current_player_name()
                    print(f"\n{Colors.BLUE}🤖 {current_ai_player_name} is thinking...{Colors.END}")
                    time.sleep(1)

                    # Get the complete log of the AI's turn from the engine
                    all_ai_actions_log = self.game.process_ai_turn()
                    
                    # After the AI's turn is fully over, display all their actions.
                    if all_ai_actions_log:
                        print(f"\n{Colors.BLUE}🤖 {current_ai_player_name}'s actions:{Colors.END}")
                        for message in all_ai_actions_log:
                            if message.strip():
                                if "secretly commits" in message and current_ai_player_name != "Human":
                                    print(f"  {Colors.BLUE}•{Colors.END} {current_ai_player_name} made a secret commitment.")
                                else:
                                    print(f"  {Colors.BLUE}•{Colors.END} {message}")

                    # Prompt for next turn
                    if not self.game.is_game_over():
                        next_player_name = self.game.get_current_player_name()
                        self.view.prompt_for_next_turn(next_player_name)
        
        # Game over
        if self.game.is_game_over():
            final_scores = self.game.get_final_scores()
            self.view.display_game_over(final_scores)


def main():
    """Main entry point for the CLI game."""
    import sys
    
    if len(sys.argv) < 2 or sys.argv[1] in ['--help', '-h', 'help']:
        print(f"{Colors.BOLD}Usage: python3 cli_game.py [mode] [ai_persona]{Colors.END}")
        print(f"\n{Colors.BOLD}Modes:{Colors.END}")
        print(f"  {Colors.CYAN}single{Colors.END}    - Play against 1 AI (default)")
        print(f"  {Colors.CYAN}multi{Colors.END}     - Play against 3 AI with different personas")
        print(f"\n{Colors.BOLD}AI Personas (for single mode):{Colors.END}")
        print(f"  {Colors.YELLOW}random, economic, legislative, balanced, heuristic{Colors.END}")
        print(f"\n{Colors.BOLD}Examples:{Colors.END}")
        print(f"  {Colors.GREEN}python3 cli_game.py single heuristic{Colors.END}")
        print(f"  {Colors.GREEN}python3 cli_game.py multi{Colors.END}")
        return
    
    mode = sys.argv[1].lower()
    
    if mode == "multi":
        # Multi-AI game
        game = CLIMultiAIGame()
        game.start_game()
    elif mode == "single":
        # Single AI game
        ai_persona = sys.argv[2] if len(sys.argv) > 2 else "heuristic"
        game = CLIGame(ai_persona, 1)
        game.start_game()
    else:
        print(f"{Colors.RED}Invalid mode. Use 'single' or 'multi'.{Colors.END}")


if __name__ == "__main__":
    main() 