from engine.engine import GameEngine
from game_data import load_game_data
import cli
from human_vs_ai import HumanVsMultipleAIGame

def main():
    """The main function to run the game."""
    # 1. SETUP
    print("="*30)
    print("Welcome to Election: The Game!")
    print("="*30)
    
    game = HumanVsMultipleAIGame()
    
    # Get player names
    human_name = input("Enter your name: ")
    game.start_new_game(human_name=human_name)


    # 2. MAIN GAME LOOP
    while not game.is_game_over():
        # First, display the current state of the game
        cli.display_game_state(game.state.to_dict())

        if game.is_human_turn():
            try:
                # Prompt the user for a valid action
                action = cli.get_player_action(game.state.to_dict())
                if action:
                    # Process the action through the engine
                    game.process_human_action(action)
                else:
                    # If action is None (e.g., user backed out of a menu), just redisplay
                    continue
            except Exception as e:
                # Catch potential errors from invalid input or game logic
                print(f"\n--- An error occurred: {e} ---")
                print("--- Please try again. ---")
        else:
            # AI's turn
            print(f"\n--- It's {game.get_current_player_name()}'s turn. ---")
            logs = game.process_ai_turn()
            for log in logs:
                print(f"[AI ACTION] {log}")
            input("\nPress Enter to continue...")


    # 3. GAME OVER
    # Display the final state and the winner
    cli.display_game_state(game.state.to_dict())
    cli.display_game_over(game.state.to_dict())


if __name__ == "__main__":
    main()