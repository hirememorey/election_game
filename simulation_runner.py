#!/usr/bin/env python3
"""
Enhanced Simulation Runner for Election Game

This module provides a configuration-driven simulation runner that can
run thousands of games with different persona combinations for game
balance analysis.
"""

import yaml
import json
import csv
import os
import time
import random
from typing import List, Dict, Any, Optional, Sequence
from dataclasses import asdict
from pathlib import Path


class GameStateEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle GameState objects."""
    
    def default(self, obj):
        if hasattr(obj, '__dict__'):
            # Convert objects to dict, handling sets and other non-serializable types
            result = {}
            for key, value in obj.__dict__.items():
                result[key] = self._serialize_value(value)
            return result
        return super().default(obj)
    
    def _serialize_value(self, value):
        """Recursively serialize a value, handling sets and complex objects."""
        if isinstance(value, set):
            return list(value)
        elif hasattr(value, '__dict__'):
            return self.default(value)
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        else:
            return value

from simulation_harness import SimulationHarness, SimulationResult, SilentLogger
from personas import (
    RandomPersona, EconomicPersona, LegislativePersona, BalancedPersona
)


class SimulationRunner:
    """
    Configuration-driven simulation runner for large-scale game analysis.
    
    This class can run thousands of simulations with different persona
    combinations and collect detailed metrics for analysis.
    """
    
    def __init__(self, config_path: str = "simulation_config.yaml"):
        """
        Initialize the simulation runner.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.harness = SimulationHarness()
        
        # Set random seed for reproducible results
        if 'random_seed' in self.config.get('simulation', {}):
            random.seed(self.config['simulation']['random_seed'])
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Configuration file {self.config_path} not found. Using defaults.")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if file not found."""
        return {
            'simulation': {
                'num_games': 100,
                'max_rounds_per_game': 100,
                'parallel_workers': 0,
                'random_seed': 42
            },
            'players': [
                {'name': 'Random Bot', 'persona': 'random'},
                {'name': 'Economic Bot', 'persona': 'economic'},
                {'name': 'Legislative Bot', 'persona': 'legislative'},
                {'name': 'Balanced Bot', 'persona': 'balanced'}
            ],
            'data_collection': {
                'log_level': 'silent',
                'save_game_logs': True,
                'save_final_states': False,
                'output_directory': 'simulation_results'
            }
        }
    
    def _create_persona(self, persona_type: str, name: str) -> Any:
        """
        Create a persona instance based on type.
        
        Args:
            persona_type: Type of persona to create
            name: Name for the persona
            
        Returns:
            Persona instance
        """
        persona_map = {
            'random': RandomPersona,
            'economic': EconomicPersona,
            'legislative': LegislativePersona,
            'balanced': BalancedPersona
        }
        
        if persona_type not in persona_map:
            print(f"Unknown persona type: {persona_type}. Using RandomPersona.")
            persona_type = 'random'
        
        return persona_map[persona_type](name=name)
    
    def _create_player_agents(self) -> List[Any]:
        """Create agent instances for all players."""
        agents = []
        for player_config in self.config['players']:
            persona = self._create_persona(
                player_config['persona'], 
                player_config['name']
            )
            agents.append(persona)
        return agents
    
    def _setup_output_directory(self) -> str:
        """Create output directory and return path."""
        output_dir = self.config['data_collection']['output_directory']
        Path(output_dir).mkdir(exist_ok=True)
        return output_dir
    
    def _save_simulation_results(self, results: List[SimulationResult], output_dir: str):
        """Save simulation results to files."""
        timestamp = int(time.time())
        
        # Save summary CSV
        csv_path = os.path.join(output_dir, f"simulation_results_{timestamp}.csv")
        with open(csv_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'game_id', 'winner_id', 'winner_name', 'game_length_rounds',
                'game_length_terms', 'simulation_time_seconds'
            ])
            
            for i, result in enumerate(results):
                writer.writerow([
                    i, result.winner_id, result.winner_name,
                    result.game_length_rounds, result.game_length_terms,
                    result.simulation_time_seconds
                ])
        
        # Save detailed JSON results
        json_path = os.path.join(output_dir, f"detailed_results_{timestamp}.json")
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2, cls=GameStateEncoder)
        
        print(f"Results saved to {output_dir}")
        print(f"  Summary: {csv_path}")
        print(f"  Details: {json_path}")
    
    def run_simulation_batch(self) -> List[SimulationResult]:
        """
        Run a batch of simulations according to configuration.
        
        Returns:
            List of simulation results
        """
        print("Starting simulation batch...")
        print(f"Configuration: {self.config_path}")
        
        # Get simulation parameters
        num_games = self.config['simulation']['num_games']
        max_rounds = self.config['simulation']['max_rounds_per_game']
        
        # Create agents
        agents = self._create_player_agents()
        player_names = [config['name'] for config in self.config['players']]
        
        print(f"Running {num_games} games with {len(agents)} players:")
        for i, (agent, name) in enumerate(zip(agents, player_names)):
            print(f"  Player {i}: {name} ({agent.__class__.__name__})")
        
        # Setup output directory
        output_dir = self._setup_output_directory()
        
        # Run simulations
        results = []
        start_time = time.time()
        
        for game_id in range(num_games):
            if game_id % 100 == 0 and game_id > 0:
                elapsed = time.time() - start_time
                rate = game_id / elapsed
                print(f"Completed {game_id}/{num_games} games ({rate:.1f} games/sec)")
            
            try:
                result = self.harness.run_simulation(
                    agents, player_names, max_rounds, SilentLogger()
                )
                results.append(result)
            except Exception as e:
                print(f"Error in game {game_id}: {e}")
                # Continue with next game
        
        total_time = time.time() - start_time
        print(f"\nSimulation batch completed in {total_time:.1f} seconds")
        print(f"Average time per game: {total_time/num_games:.3f} seconds")
        
        # Save results
        self._save_simulation_results(results, output_dir)
        
        return results
    
    def generate_summary_report(self, results: List[SimulationResult]) -> str:
        """
        Generate a summary report of simulation results.
        
        Args:
            results: List of simulation results
            
        Returns:
            Markdown report string
        """
        if not results:
            return "No results to report."
        
        # Calculate statistics
        total_games = len(results)
        winners = [r.winner_name for r in results if r.winner_name]
        winner_counts = {}
        for winner in winners:
            winner_counts[winner] = winner_counts.get(winner, 0) + 1
        
        avg_rounds = sum(r.game_length_rounds for r in results) / total_games
        avg_terms = sum(r.game_length_terms for r in results) / total_games
        avg_time = sum(r.simulation_time_seconds for r in results) / total_games
        
        # Generate report
        report = f"""# Simulation Results Report

## Summary
- **Total Games**: {total_games}
- **Average Rounds per Game**: {avg_rounds:.1f}
- **Average Terms per Game**: {avg_terms:.1f}
- **Average Simulation Time**: {avg_time:.3f} seconds

## Winner Distribution
"""
        
        for winner, count in sorted(winner_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_games) * 100
            report += f"- **{winner}**: {count} wins ({percentage:.1f}%)\n"
        
        report += f"""
## Configuration
- **Configuration File**: {self.config_path}
- **Players**: {len(self.config['players'])}
- **Max Rounds per Game**: {self.config['simulation']['max_rounds_per_game']}

## Player Strategies
"""
        
        for i, player_config in enumerate(self.config['players']):
            report += f"- **Player {i+1}**: {player_config['name']} ({player_config['persona']} strategy)\n"
        
        return report


def main():
    """Main entry point for the simulation runner."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run Election Game simulations')
    parser.add_argument('--config', default='simulation_config.yaml',
                       help='Configuration file path')
    parser.add_argument('--report', action='store_true',
                       help='Generate summary report')
    
    args = parser.parse_args()
    
    # Run simulations
    runner = SimulationRunner(args.config)
    results = runner.run_simulation_batch()
    
    # Generate report if requested
    if args.report:
        report = runner.generate_summary_report(results)
        print("\n" + "="*50)
        print("SUMMARY REPORT")
        print("="*50)
        print(report)


if __name__ == "__main__":
    main() 