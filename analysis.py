#!/usr/bin/env python3
"""
Analysis Module for Election Game Simulation Framework

This module processes simulation results and generates actionable insights
for game balance analysis. It transforms raw simulation data into clear,
human-readable reports that help answer key questions about the game.
"""

import json
import csv
import os
import statistics
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from collections import defaultdict, Counter


@dataclass
class AnalysisMetrics:
    """Key metrics for game balance analysis."""
    total_games: int
    win_rates: Dict[str, float]  # persona_name -> win_rate
    win_rates_by_position: Dict[int, Dict[str, float]]  # position -> persona -> win_rate
    avg_game_length_rounds: float
    avg_game_length_terms: float
    action_frequency: Dict[str, Dict[str, int]]  # persona -> action_type -> count
    economic_analysis: Dict[str, Dict[str, float]]  # persona -> metric -> value
    game_length_distribution: Dict[int, int]  # rounds -> count


class SimulationAnalyzer:
    """
    Analyzes simulation results to provide actionable insights for game balance.
    
    This class transforms raw simulation data into clear metrics that help
    answer key questions: Is the game balanced? Are there dominant strategies?
    Does player order matter? What's the typical game length?
    """
    
    def __init__(self, results_directory: str = "simulation_results"):
        """
        Initialize the analyzer.
        
        Args:
            results_directory: Directory containing simulation results
        """
        self.results_directory = Path(results_directory)
        self.results = []
        self.metrics = None
    
    def load_results(self, timestamp: Optional[str] = None) -> None:
        """
        Load simulation results from files.
        
        Args:
            timestamp: Specific timestamp to load (if None, loads most recent)
        """
        if timestamp is None:
            # Find the most recent results file (including subdirectories)
            json_files = list(self.results_directory.glob("**/*detailed_results_*.json"))
            if not json_files:
                raise FileNotFoundError(f"No results found in {self.results_directory}")
            
            # Sort by modification time and get the most recent
            latest_file = max(json_files, key=lambda f: f.stat().st_mtime)
            timestamp = latest_file.stem.split('_')[-1]
        
        # Look for the file in the main directory first, then in subdirectories
        json_files = list(self.results_directory.glob(f"*detailed_results_{timestamp}.json"))
        if not json_files:
            # Search in subdirectories
            json_files = list(self.results_directory.glob(f"*/*detailed_results_{timestamp}.json"))
            if not json_files:
                raise FileNotFoundError(f"Results file not found with timestamp {timestamp}")
        
        json_path = json_files[0]  # Use the first matching file
        
        # Load detailed results
        with open(json_path, 'r') as f:
            self.results = json.load(f)
        
        print(f"Loaded {len(self.results)} simulation results from {json_path}")
    
    def calculate_metrics(self) -> AnalysisMetrics:
        """
        Calculate comprehensive metrics from the simulation results.
        
        Returns:
            AnalysisMetrics object containing all calculated metrics
        """
        if not self.results:
            raise ValueError("No results loaded. Call load_results() first.")
        
        total_games = len(self.results)
        
        # Calculate win rates
        win_rates = self._calculate_win_rates()
        
        # Calculate win rates by player position
        win_rates_by_position = self._calculate_win_rates_by_position()
        
        # Calculate game length statistics
        game_lengths_rounds = [r['game_length_rounds'] for r in self.results]
        game_lengths_terms = [r['game_length_terms'] for r in self.results]
        
        avg_game_length_rounds = statistics.mean(game_lengths_rounds)
        avg_game_length_terms = statistics.mean(game_lengths_terms)
        
        # Calculate action frequency analysis
        action_frequency = self._calculate_action_frequency()
        
        # Calculate economic analysis
        economic_analysis = self._calculate_economic_analysis()
        
        # Calculate game length distribution
        game_length_distribution = Counter(game_lengths_rounds)
        
        self.metrics = AnalysisMetrics(
            total_games=total_games,
            win_rates=win_rates,
            win_rates_by_position=win_rates_by_position,
            avg_game_length_rounds=avg_game_length_rounds,
            avg_game_length_terms=avg_game_length_terms,
            action_frequency=action_frequency,
            economic_analysis=economic_analysis,
            game_length_distribution=dict(game_length_distribution)
        )
        
        return self.metrics
    
    def _calculate_win_rates(self) -> Dict[str, float]:
        """Calculate win rates for each persona."""
        winner_counts = Counter()
        total_games = len(self.results)
        
        for result in self.results:
            winner_name = result.get('winner_name')
            if winner_name:
                winner_counts[winner_name] += 1
        
        win_rates = {}
        for winner_name, wins in winner_counts.items():
            win_rates[winner_name] = wins / total_games
        
        return win_rates
    
    def _calculate_win_rates_by_position(self) -> Dict[int, Dict[str, float]]:
        """Calculate win rates broken down by player position (first, second, etc.)."""
        position_wins = defaultdict(lambda: defaultdict(int))
        position_games = defaultdict(int)
        
        for result in self.results:
            # Extract player positions from game log or final state
            # This is a simplified version - in practice, we'd need to track
            # which player was in which position during the game
            winner_name = result.get('winner_name')
            if winner_name:
                # For now, assume winner was in position 0 (first player)
                # In a full implementation, we'd track this from the game state
                position_wins[0][winner_name] += 1
                position_games[0] += 1
        
        win_rates_by_position = {}
        for position in position_games:
            win_rates_by_position[position] = {}
            for winner_name, wins in position_wins[position].items():
                win_rates_by_position[position][winner_name] = wins / position_games[position]
        
        return win_rates_by_position
    
    def _calculate_action_frequency(self) -> Dict[str, Dict[str, int]]:
        """Calculate how often each persona takes different actions."""
        action_frequency = defaultdict(lambda: defaultdict(int))
        
        for result in self.results:
            game_log = result.get('game_log', [])
            
            # Parse game log to extract actions by player
            # This is a simplified version - in practice, we'd need to parse
            # the actual action log entries
            for log_entry in game_log:
                # Example log entry: "Player 1 chose: ActionFundraise"
                if "chose:" in log_entry:
                    parts = log_entry.split("chose:")
                    if len(parts) == 2:
                        player_name = parts[0].strip()
                        action_name = parts[1].strip()
                        
                        # Extract persona name from player name
                        persona_name = self._extract_persona_name(player_name)
                        action_frequency[persona_name][action_name] += 1
        
        return dict(action_frequency)
    
    def _calculate_economic_analysis(self) -> Dict[str, Dict[str, float]]:
        """Calculate economic metrics for each persona."""
        economic_metrics = defaultdict(lambda: defaultdict(list))
        
        for result in self.results:
            final_state = result.get('final_state', {})
            players = final_state.get('players', [])
            
            for player in players:
                persona_name = self._extract_persona_name(player.get('name', ''))
                pc = player.get('pc', 0)
                influence = player.get('influence', 0)
                
                economic_metrics[persona_name]['final_pc'].append(pc)
                economic_metrics[persona_name]['final_influence'].append(influence)
        
        # Calculate averages
        economic_analysis = {}
        for persona_name, metrics in economic_metrics.items():
            economic_analysis[persona_name] = {
                'avg_final_pc': statistics.mean(metrics['final_pc']),
                'avg_final_influence': statistics.mean(metrics['final_influence']),
                'max_final_pc': max(metrics['final_pc']),
                'min_final_pc': min(metrics['final_pc'])
            }
        
        return economic_analysis
    
    def _extract_persona_name(self, player_name: str) -> str:
        """Extract persona name from player name."""
        # Remove common suffixes like " Bot"
        if player_name.endswith(" Bot"):
            return player_name[:-4]
        return player_name
    
    def generate_report(self) -> str:
        """
        Generate a comprehensive human-readable report.
        
        Returns:
            Markdown-formatted report string
        """
        if self.metrics is None:
            self.calculate_metrics()
        
        # Ensure metrics are calculated
        metrics = self.metrics
        if metrics is None:
            return "# Error: Could not calculate metrics"
        
        report = []
        report.append("# Election Game Simulation Analysis Report")
        report.append("")
        
        # Summary statistics
        report.append("## Summary Statistics")
        report.append(f"- **Total Games:** {metrics.total_games}")
        report.append(f"- **Average Game Length:** {metrics.avg_game_length_rounds:.1f} rounds ({metrics.avg_game_length_terms:.1f} terms)")
        report.append("")
        
        # Win rate analysis
        report.append("## Win Rate Analysis")
        report.append("### Overall Win Rates")
        for persona, win_rate in sorted(metrics.win_rates.items(), key=lambda x: x[1], reverse=True):
            percentage = win_rate * 100
            report.append(f"- **{persona}:** {percentage:.1f}% ({win_rate * metrics.total_games:.0f} wins)")
        report.append("")
        
        # Balance assessment
        report.append("### Balance Assessment")
        win_rates = list(metrics.win_rates.values())
        if win_rates:
            max_win_rate = max(win_rates)
            min_win_rate = min(win_rates)
            win_rate_spread = max_win_rate - min_win_rate
            
            if win_rate_spread < 0.1:
                assessment = "✅ **BALANCED** - Win rates are well distributed"
            elif win_rate_spread < 0.2:
                assessment = "⚠️ **SLIGHTLY UNBALANCED** - Some strategies may be stronger"
            else:
                assessment = "❌ **UNBALANCED** - Significant strategy imbalance detected"
            
            report.append(f"- **Win Rate Spread:** {win_rate_spread:.1%}")
            report.append(f"- **Assessment:** {assessment}")
        report.append("")
        
        # Game length analysis
        report.append("## Game Length Analysis")
        report.append(f"- **Average Rounds:** {metrics.avg_game_length_rounds:.1f}")
        report.append(f"- **Average Terms:** {metrics.avg_game_length_terms:.1f}")
        report.append("")
        
        # Most common game lengths
        report.append("### Game Length Distribution")
        sorted_lengths = sorted(metrics.game_length_distribution.items())
        for rounds, count in sorted_lengths[:5]:  # Top 5 most common
            percentage = (count / metrics.total_games) * 100
            report.append(f"- **{rounds} rounds:** {count} games ({percentage:.1f}%)")
        report.append("")
        
        # Action frequency analysis
        report.append("## Action Frequency Analysis")
        for persona, actions in metrics.action_frequency.items():
            report.append(f"### {persona}")
            total_actions = sum(actions.values())
            if total_actions > 0:
                for action, count in sorted(actions.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total_actions) * 100
                    report.append(f"- **{action}:** {count} times ({percentage:.1f}%)")
            report.append("")
        
        # Economic analysis
        report.append("## Economic Analysis")
        for persona, metrics_econ in metrics.economic_analysis.items():
            report.append(f"### {persona}")
            report.append(f"- **Average Final PC:** {metrics_econ['avg_final_pc']:.1f}")
            report.append(f"- **Average Final Influence:** {metrics_econ['avg_final_influence']:.1f}")
            report.append(f"- **PC Range:** {metrics_econ['min_final_pc']:.0f} - {metrics_econ['max_final_pc']:.0f}")
            report.append("")
        
        return "\n".join(report)
    
    def save_report(self, output_path: str = "analysis_report.md") -> None:
        """
        Save the analysis report to a file.
        
        Args:
            output_path: Path to save the report
        """
        report = self.generate_report()
        
        with open(output_path, 'w') as f:
            f.write(report)
        
        print(f"Analysis report saved to: {output_path}")
    
    def print_summary(self) -> None:
        """Print a quick summary to the console."""
        if self.metrics is None:
            self.calculate_metrics()
        
        # Ensure metrics are calculated
        metrics = self.metrics
        if metrics is None:
            print("Error: Could not calculate metrics")
            return
        
        print("\n" + "="*50)
        print("SIMULATION ANALYSIS SUMMARY")
        print("="*50)
        
        print(f"Total Games: {metrics.total_games}")
        print(f"Average Game Length: {metrics.avg_game_length_rounds:.1f} rounds")
        print()
        
        print("Win Rates:")
        for persona, win_rate in sorted(metrics.win_rates.items(), key=lambda x: x[1], reverse=True):
            percentage = win_rate * 100
            print(f"  {persona}: {percentage:.1f}%")
        
        print()
        
        # Quick balance assessment
        win_rates = list(metrics.win_rates.values())
        if win_rates:
            max_win_rate = max(win_rates)
            min_win_rate = min(win_rates)
            spread = max_win_rate - min_win_rate
            
            if spread < 0.1:
                print("✅ Game appears BALANCED")
            elif spread < 0.2:
                print("⚠️ Game shows slight imbalance")
            else:
                print("❌ Game shows significant imbalance")
        
        print("="*50)


def main():
    """Main function to run analysis on simulation results."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze simulation results")
    parser.add_argument("--results-dir", default="simulation_results", 
                       help="Directory containing simulation results")
    parser.add_argument("--timestamp", help="Specific timestamp to analyze")
    parser.add_argument("--output", default="analysis_report.md",
                       help="Output file for the report")
    
    args = parser.parse_args()
    
    analyzer = SimulationAnalyzer(args.results_dir)
    
    try:
        analyzer.load_results(args.timestamp)
        analyzer.calculate_metrics()
        analyzer.print_summary()
        analyzer.save_report(args.output)
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Make sure to run simulations first using simulation_runner.py")
        return 1
    except Exception as e:
        print(f"Error during analysis: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 