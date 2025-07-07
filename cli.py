from typing import Optional
from models.game_state import GameState
from models.components import Player
from engine.actions import (
    Action, ActionFundraise, ActionNetwork,
    ActionSponsorLegislation, ActionDeclareCandidacy
)

def display_game_state(state: GameState):
    """Prints a comprehensive, human-readable summary of the game state."""
    print("\n" + "="*60)
    print(f"ROUND: {state.round_marker}/4  |  PUBLIC MOOD: {state.public_mood} ({mood_to_string(state.public_mood)})  |  PHASE: {state.current_phase}")
    print("="*60)

    if state.turn_log:
        for message in state.turn_log:
            print(f"[LOG] {message}")
        print("-"*60)

    print("PLAYERS:")
    for p in state.players:
        office_title = p.current_office.title if p.current_office else "Outsider"
        is_current = ">>>" if p.id == state.get_current_player().id and state.current_phase == "ACTION_PHASE" else ""
        print(f"  {is_current}{p.name} ({p.archetype.title})")
        print(f"    PC: {p.pc} | Office: {office_title}")
        if p.allies:
            print(f"    Ally: {p.allies[0].title} ({p.allies[0].description})")
        if p.favors:
            print(f"    Favors: {len(p.favors)}")
    print("="*60)

def get_player_action(state: GameState) -> Optional[Action]:
    """Prompts the current player for their move and returns a structured Action object."""
    player = state.get_current_player()

    while True:
        print(f"\nIt's your turn, {player.name}. What is your action?")
        print("  [1] Fundraise")
        print("  [2] Network")
        print("  [3] Sponsor Legislation")
        if state.round_marker == 4:
            print("  [4] Declare Candidacy for an Office")
        print("---")
        print("  [info] View Game Info (Offices, Mandate, etc.)")
        print("  [rules] See action descriptions")


        choice = input("> ").lower()

        if choice == '1':
            return ActionFundraise(player_id=player.id)
        elif choice == '2':
            return ActionNetwork(player_id=player.id)
        elif choice == '3':
            return _prompt_for_legislation(state, player)
        elif choice == '4' and state.round_marker == 4:
            return _prompt_for_candidacy(state, player)
        elif choice == 'info':
            _display_info_menu(state, player)
            continue
        elif choice == 'rules':
            _display_rules()
            continue
        else:
            print("Invalid input. Please try again.")

def _prompt_for_legislation(state: GameState, player: Player) -> Optional[Action]:
    """Handles the multi-step process of sponsoring a bill. Co-sponsorship is NOT yet implemented."""
    print("Which bill would you like to sponsor?")
    options = list(state.legislation_options.items())
    for i, (leg_id, leg) in enumerate(options):
        print(f"  [{i+1}] {leg.title} (Cost: {leg.cost} PC)")
    print(f"  [{len(options)+1}] Cancel")
    
    while True:
        try:
            choice = int(input("> ")) - 1
            if 0 <= choice < len(options):
                leg_id, leg = options[choice]
                if player.pc >= leg.cost:
                    # TODO: Implement co-sponsorship prompt here
                    print(f"You chose to sponsor the {leg.title}.")
                    return ActionSponsorLegislation(player_id=player.id, legislation_id=leg_id)
                else:
                    print("You do not have enough PC to sponsor this bill.")
                    return None
            elif choice == len(options):
                return None
            else:
                print("Invalid number.")
        except ValueError:
            print("Please enter a number.")
    return None # Fallback

def _prompt_for_candidacy(state: GameState, player: Player) -> Optional[Action]:
    """Helper to handle declaring candidacy."""
    print("Which office will you run for?")
    options = list(state.offices.values())
    for i, office in enumerate(options):
        print(f"  [{i+1}] {office.title} (Cost: {office.candidacy_cost} PC)")
    print(f"  [{len(options)+1}] Cancel")

    while True:
        try:
            office_choice = int(input("> ")) - 1
            if not (0 <= office_choice < len(options)):
                if office_choice == len(options): return None
                print("Invalid number.")
                continue
            
            chosen_office = options[office_choice]
            if player.pc < chosen_office.candidacy_cost:
                print("You don't have enough PC for the candidacy cost.")
                continue

            max_commit = player.pc - chosen_office.candidacy_cost
            print(f"You have {max_commit} PC remaining after the fee.")
            commit_pc = int(input(f"How much PC will you secretly commit to the {chosen_office.title} race? (0-{max_commit}) > "))

            if 0 <= commit_pc <= max_commit:
                return ActionDeclareCandidacy(player_id=player.id, office_id=chosen_office.id, committed_pc=commit_pc)
            else:
                print(f"Invalid commitment. Must be between 0 and {max_commit}.")
        except ValueError:
            print("Please enter a valid number.")
    return None # Fallback

def _display_info_menu(state: GameState, player: Player):
    """Shows a menu for viewing game information."""
    while True:
        print("\n--- INFO MENU ---")
        print("  [1] View My Personal Mandate")
        print("  [2] View All Offices of Power")
        print("  [3] View Legislation Options")
        print("  [4] Return to action menu")
        choice = input("> ")
        if choice == '1':
            print(f"Your Secret Mandate: {player.mandate.title} - {player.mandate.description}")
        elif choice == '2':
            for office in state.offices.values():
                print(f"  - {office.title} (Tier {office.tier}): Income {office.income} PC, NPC Bonus +{office.npc_challenger_bonus}")
        elif choice == '3':
             for leg in state.legislation_options.values():
                print(f"  - {leg.title}: Cost {leg.cost}, Reward {leg.success_reward}/{leg.crit_reward} PC")
        elif choice == '4':
            break
        else:
            print("Invalid choice.")

def _display_rules():
    """Prints descriptions for the primary actions."""
    print("\n--- ACTION RULES ---")
    print("Fundraise: Gain 5 PC (plus any bonuses).")
    print("Network: Gain 2 PC and one random Political Favor token.")
    print("Sponsor Legislation: Pay PC cost to propose a bill. Roll a d6 to determine outcome. Other players may co-sponsor.")
    print("Declare Candidacy: In Round 4 only, pay a fee to run for an office and secretly commit funds to the race.")

def display_game_over(state: GameState):
    """Displays the final game over message."""
    print("\n" + "#"*50)
    print("#" + "GAME OVER".center(48) + "#")
    print("#"*50)
    
    winner = None
    for p in state.players:
        if p.current_office and p.current_office.id == "PRESIDENT":
            winner = p
            break
            
    if winner:
        print(f"\nCongratulations, {winner.name}! You have won the Presidency!")
    else:
        print("\nNo winner was declared this game.")

def mood_to_string(mood: int) -> str:
    return {
        -3: "Very Angry", -2: "Angry", -1: "Unhappy", 0: "Neutral",
        1: "Happy", 2: "Pleased", 3: "Ecstatic"
    }.get(mood, "Unknown")