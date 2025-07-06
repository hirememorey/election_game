from engine.engine import GameEngine
from game_data import load_game_data
import cli

def main():
    """The main function to run the game."""
    # 1. SETUP
    print("="*30)
    print("Welcome to Election: The Game!")
    print("="*30)
    
    # Load all game data and initialize the engine
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Get player names
    num_players = int(input("Enter number of players (2-4): "))
    player_names = [input(f"Enter name for Player {i+1}: ") for i in range(num_players)]
    
    # Create the initial game state
    game_state = engine.start_new_game(player_names)

    # 2. MAIN GAME LOOP
    while not engine.is_game_over(game_state):
        # First, display the current state of the game
        cli.display_game_state(game_state)

        # Handle automated phases
        if game_state.current_phase == "EVENT_PHASE":
            input("\nPress Enter to begin the round and draw an Event card...")
            game_state = engine.run_event_phase(game_state)
            # Loop back to display the result of the event
            continue

        # If it's the action phase, get input from the current player
        elif game_state.current_phase == "ACTION_PHASE":
            try:
                # Prompt the user for a valid action
                action = cli.get_player_action(game_state)
                if action:
                    # Process the action through the engine
                    game_state = engine.process_action(game_state, action)
                else:
                    # If action is None (e.g., user backed out of a menu), just redisplay
                    continue
            except Exception as e:
                # Catch potential errors from invalid input or game logic
                print(f"\n--- An error occurred: {e} ---")
                print("--- Please try again. ---")

    # 3. GAME OVER
    # Display the final state and the winner
    cli.display_game_state(game_state)
    cli.display_game_over(game_state)


if __name__ == "__main__":
    main()