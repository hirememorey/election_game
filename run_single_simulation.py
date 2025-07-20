#!/usr/bin/env python3
"""
Single Simulation Runner

This script runs a single simulation using the simulation harness and provides
detailed analysis of the winner and their victory conditions.
"""

from simulation_harness import SimulationHarness, RandomAgent, VerboseLogger
from engine.engine import GameEngine
from game_data import load_game_data


def analyze_winner(result, game_state):
    """
    Analyze the winner and provide detailed reasoning for their victory.
    
    Args:
        result: SimulationResult object
        game_state: Final GameState object
    
    Returns:
        str: Detailed analysis of the winner
    """
    if not result.winner_name:
        return "No winner determined - game may have ended in a tie or error."
    
    winner = None
    for player in game_state.players:
        if player.name == result.winner_name:
            winner = player
            break
    
    if not winner:
        return f"Error: Could not find winner {result.winner_name} in final game state."
    
    # Get final scores
    engine = GameEngine(load_game_data())
    final_scores = engine.get_final_scores(game_state)
    scores = final_scores.get('scores', {})
    
    # Extract total influence scores
    winner_score_data = scores.get(winner.id, {})
    winner_total_influence = winner_score_data.get('total_influence', 0) if isinstance(winner_score_data, dict) else winner_score_data
    
    analysis = f"""
🏆 WINNER ANALYSIS: {winner.name}

📊 FINAL SCORE: {winner_total_influence} influence points

🎭 PLAYER IDENTITY:
• Archetype: {winner.archetype.title if winner.archetype else 'Unknown'}
• Mandate: {winner.mandate.title if winner.mandate else 'Unknown'}

💰 RESOURCES:
• Political Capital: {winner.pc} PC
• Current Office: {winner.current_office.title if winner.current_office else 'None'}

🏛️ INFLUENCE BREAKDOWN:
"""
    
    # Add influence breakdown details
    if isinstance(winner_score_data, dict) and 'details' in winner_score_data:
        for detail in winner_score_data['details']:
            analysis += f"• {detail}\n"
    
    # Analyze victory factors
    analysis += "\n🎯 VICTORY FACTORS:\n"
    
    # Office holding
    if winner.current_office:
        analysis += f"• Held the {winner.current_office.title} office\n"
    else:
        analysis += "• Did not hold any office\n"
    
    # PC conversion
    if winner.pc > 0:
        pc_conversion = winner.pc // 10  # 10:1 conversion ratio
        analysis += f"• Converted {winner.pc} PC to {pc_conversion} influence points\n"
    else:
        analysis += "• Had no PC to convert\n"
    
    # Compare to other players
    analysis += "\n📈 COMPARISON TO OTHER PLAYERS:\n"
    for player in game_state.players:
        if player.id != winner.id:
            player_score_data = scores.get(player.id, {})
            player_total_influence = player_score_data.get('total_influence', 0) if isinstance(player_score_data, dict) else player_score_data
            difference = winner_total_influence - player_total_influence
            analysis += f"• {player.name}: {player_total_influence} points (winner by {difference} points)\n"
    
    # Game statistics
    analysis += f"\n📊 GAME STATISTICS:\n"
    analysis += f"• Game Length: {result.game_length_rounds} rounds, {result.game_length_terms} terms\n"
    analysis += f"• Simulation Time: {result.simulation_time_seconds:.3f} seconds\n"
    
    return analysis


def run_single_simulation():
    """
    Run a single simulation and provide detailed analysis.
    """
    print("🎮 ELECTION GAME - SINGLE SIMULATION")
    print("=" * 50)
    
    # Create simulation harness
    harness = SimulationHarness()
    
    # Create agents (all random for this example)
    agents = [RandomAgent() for _ in range(4)]
    player_names = ['Alice', 'Bob', 'Charlie', 'Diana']
    
    # Run simulation with verbose logging
    print("\n🚀 Starting simulation...")
    result = harness.run_simulation(
        agents, 
        player_names, 
        logger=VerboseLogger()
    )
    
    # Analyze the winner using the final state from the result
    print("\n" + "=" * 50)
    if result.final_state:
        analysis = analyze_winner(result, result.final_state)
        print(analysis)
    else:
        print("Error: No final state available for analysis.")
    
    return result


if __name__ == "__main__":
    result = run_single_simulation() 