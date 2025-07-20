"""
Configuration Loader for Election Game

This module loads and manages game configuration from YAML files,
providing easy access to all game parameters for tuning and iteration.
"""

import yaml
import os
from typing import Dict, Any, Optional


class GameConfig:
    """
    Configuration manager for the Election Game.
    
    Loads configuration from YAML files and provides easy access
    to all game parameters for tuning and iteration.
    """
    
    def __init__(self, config_file: str = "game_config.yaml"):
        """
        Initialize the configuration manager.
        
        Args:
            config_file: Path to the YAML configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_file):
            print(f"Warning: Configuration file {self.config_file} not found. Using defaults.")
            return self._get_default_config()
        
        try:
            with open(self.config_file, 'r') as file:
                config = yaml.safe_load(file)
                if config is None:
                    return self._get_default_config()
                return config
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if file is not found."""
        return {
            'game': {
                'rounds_per_term': 4,
                'max_players': 4,
                'min_players': 2
            },
            'action_points': {
                'base_ap_per_turn': 2,
                'max_ap_per_turn': 4
            },
            'political_capital': {
                'base_fundraise_pc': 5,
                'base_network_pc': 2
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            key_path: Path to the configuration value (e.g., 'game.rounds_per_term')
            default: Default value if key is not found
            
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_int(self, key_path: str, default: int = 0) -> int:
        """Get an integer configuration value."""
        value = self.get(key_path, default)
        return int(value) if value is not None else default
    
    def get_float(self, key_path: str, default: float = 0.0) -> float:
        """Get a float configuration value."""
        value = self.get(key_path, default)
        return float(value) if value is not None else default
    
    def get_bool(self, key_path: str, default: bool = False) -> bool:
        """Get a boolean configuration value."""
        value = self.get(key_path, default)
        return bool(value) if value is not None else default
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self.config = self._load_config()
    
    def save(self, config_file: Optional[str] = None) -> None:
        """
        Save current configuration to file.
        
        Args:
            config_file: Optional path to save to (defaults to original file)
        """
        save_path = config_file or self.config_file
        try:
            with open(save_path, 'w') as file:
                yaml.dump(self.config, file, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"Error saving configuration: {e}")
    
    def update(self, key_path: str, value: Any) -> None:
        """
        Update a configuration value.
        
        Args:
            key_path: Path to the configuration value (e.g., 'game.rounds_per_term')
            value: New value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the value
        config[keys[-1]] = value
    
    def get_game_config(self) -> Dict[str, Any]:
        """Get all game-related configuration."""
        return self.config.get('game', {})
    
    def get_action_points_config(self) -> Dict[str, Any]:
        """Get all action points configuration."""
        return self.config.get('action_points', {})
    
    def get_political_capital_config(self) -> Dict[str, Any]:
        """Get all political capital configuration."""
        return self.config.get('political_capital', {})
    
    def get_legislation_config(self) -> Dict[str, Any]:
        """Get all legislation configuration."""
        return self.config.get('legislation', {})
    
    def get_elections_config(self) -> Dict[str, Any]:
        """Get all elections configuration."""
        return self.config.get('elections', {})
    
    def get_events_config(self) -> Dict[str, Any]:
        """Get all events configuration."""
        return self.config.get('events', {})
    
    def get_favors_config(self) -> Dict[str, Any]:
        """Get all favors configuration."""
        return self.config.get('favors', {})
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get all AI behavior configuration."""
        return self.config.get('ai', {})
    
    def get_balance_config(self) -> Dict[str, Any]:
        """Get all balance targets configuration."""
        return self.config.get('balance', {})
    
    def get_interface_config(self) -> Dict[str, Any]:
        """Get all interface configuration."""
        return self.config.get('interface', {})
    
    def get_development_config(self) -> Dict[str, Any]:
        """Get all development/testing configuration."""
        return self.config.get('development', {})
    
    def validate_config(self) -> bool:
        """
        Validate the configuration for required fields and reasonable values.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Check required sections
            required_sections = ['game', 'action_points', 'political_capital']
            for section in required_sections:
                if section not in self.config:
                    print(f"Error: Missing required configuration section: {section}")
                    return False
            
            # Validate game structure
            game_config = self.config['game']
            if game_config.get('rounds_per_term', 0) <= 0:
                print("Error: rounds_per_term must be positive")
                return False
            
            if game_config.get('max_players', 0) < game_config.get('min_players', 0):
                print("Error: max_players must be >= min_players")
                return False
            
            # Validate action points
            ap_config = self.config['action_points']
            if ap_config.get('base_ap_per_turn', 0) <= 0:
                print("Error: base_ap_per_turn must be positive")
                return False
            
            # Validate political capital
            pc_config = self.config['political_capital']
            if pc_config.get('base_fundraise_pc', 0) < 0:
                print("Error: base_fundraise_pc must be non-negative")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error validating configuration: {e}")
            return False
    
    def print_config_summary(self) -> None:
        """Print a summary of the current configuration."""
        print("=== Election Game Configuration Summary ===")
        
        sections = [
            ('Game Structure', 'game'),
            ('Action Points', 'action_points'),
            ('Political Capital', 'political_capital'),
            ('Legislation', 'legislation'),
            ('Elections', 'elections'),
            ('Events', 'events'),
            ('Favors', 'favors'),
            ('AI Behavior', 'ai'),
            ('Balance Targets', 'balance'),
            ('Interface', 'interface'),
            ('Development', 'development')
        ]
        
        for title, section in sections:
            if section in self.config:
                print(f"\n{title}:")
                for key, value in self.config[section].items():
                    print(f"  {key}: {value}")
        
        print("\n" + "="*40)


# Global configuration instance
_config_instance: Optional[GameConfig] = None


def get_config() -> GameConfig:
    """
    Get the global configuration instance.
    
    Returns:
        GameConfig instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = GameConfig()
    return _config_instance


def reload_config() -> None:
    """Reload the global configuration."""
    global _config_instance
    if _config_instance:
        _config_instance.reload()


def update_config(key_path: str, value: Any) -> None:
    """
    Update a configuration value globally.
    
    Args:
        key_path: Path to the configuration value
        value: New value to set
    """
    config = get_config()
    config.update(key_path, value)


def save_config() -> None:
    """Save the current configuration to file."""
    config = get_config()
    config.save()


def validate_config() -> bool:
    """
    Validate the current configuration.
    
    Returns:
        True if configuration is valid, False otherwise
    """
    config = get_config()
    return config.validate_config()


if __name__ == "__main__":
    # Test the configuration loader
    config = get_config()
    config.print_config_summary()
    
    if config.validate_config():
        print("\n✅ Configuration is valid!")
    else:
        print("\n❌ Configuration has errors!") 