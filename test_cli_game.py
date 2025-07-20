#!/usr/bin/env python3
"""
Test script for the CLI game functionality.
"""

from cli_game import CLIGame
from human_vs_ai import HumanVsAIGame


def test_cli_game_creation():
    """Test that the CLI game can be created and initialized."""
    print("Testing CLI game creation...")
    
    try:
        # Test with different AI personas
        for persona in ["random", "heuristic", "economic"]:
            game = CLIGame(persona)
            print(f"✓ Successfully created CLI game with {persona} AI")
            
            # Test starting a new game
            game.game.start_new_game("TestPlayer")
            print(f"✓ Successfully started new game with {persona} AI")
            
            # Test that the game state is valid
            if game.game.state:
                print(f"✓ Game state is valid (round {game.game.state.round_marker})")
            else:
                print("✗ Game state is None")
                return False
        
        print("✓ All CLI game tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error testing CLI game: {e}")
        return False


def test_human_vs_ai_game():
    """Test the HumanVsAIGame class directly."""
    print("\nTesting HumanVsAIGame class...")
    
    try:
        game = HumanVsAIGame("heuristic")
        state = game.start_new_game("TestPlayer")
        
        print(f"✓ Game started successfully")
        print(f"  - Players: {[p.name for p in state.players]}")
        print(f"  - Current phase: {state.current_phase}")
        print(f"  - Round: {state.round_marker}")
        
        # Test getting valid actions
        actions = game.get_valid_actions()
        print(f"  - Valid actions: {len(actions)} available")
        
        # Test human turn detection
        is_human_turn = game.is_human_turn()
        print(f"  - Is human turn: {is_human_turn}")
        
        print("✓ HumanVsAIGame tests passed!")
        return True
        
    except Exception as e:
        print(f"✗ Error testing HumanVsAIGame: {e}")
        return False


def main():
    """Run all tests."""
    print("="*50)
    print("Testing CLI Game Implementation")
    print("="*50)
    
    success = True
    
    # Test CLI game creation
    if not test_cli_game_creation():
        success = False
    
    # Test HumanVsAIGame class
    if not test_human_vs_ai_game():
        success = False
    
    print("\n" + "="*50)
    if success:
        print("✓ All tests passed! CLI game is ready for use.")
        print("\nTo play a game, run:")
        print("  python3 cli_game.py [ai_persona]")
        print("\nAvailable AI personas: random, economic, legislative, balanced, heuristic")
    else:
        print("✗ Some tests failed. Please check the implementation.")
    print("="*50)


if __name__ == "__main__":
    main() 