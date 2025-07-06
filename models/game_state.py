from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
import copy

from models.components import Player, Office, Legislation, PoliticalFavor, Candidacy, Pledge
from models.cards import Deck

@dataclass
class GameState:
    """A single object holding the entire state of the game."""
    # Core game components
    players: List[Player]
    offices: Dict[str, Office]
    legislation_options: Dict[str, Legislation]
    
    # Decks and Supplies
    event_deck: Deck
    scrutiny_deck: Deck
    alliance_deck: Deck
    favor_supply: List[PoliticalFavor]
    pledge_supply: List[Pledge] = field(default_factory=list) # All pledges currently active

    # Game flow trackers
    round_marker: int = 1
    public_mood: int = 0  # Range from -3 (Very Angry) to +3 (Ecstatic)
    current_player_index: int = 0
    current_phase: str = "EVENT_PHASE"  # EVENT_PHASE, ACTION_PHASE, UPKEEP_PHASE, ELECTION_PHASE
    
    # State trackers for a single term/round
    turn_log: List[str] = field(default_factory=list)
    secret_candidacies: List[Candidacy] = field(default_factory=list)
    
    # Lingering effects from events, identified by event ID
    active_effects: Set[str] = field(default_factory=set)
    
    # History for checking mandates/events
    last_sponsor_result: Dict = field(default_factory=dict) # {'player_id': int, 'passed': bool}
    legislation_history: List[Dict] = field(default_factory=list) # [{'sponsor_id': int, 'leg_id': str, 'outcome': str}]

    def get_current_player(self) -> Player:
        """Returns the player whose turn it is."""
        return self.players[self.current_player_index]

    def get_player_by_id(self, player_id: int) -> Optional[Player]:
        """Finds a player by their unique ID."""
        for p in self.players:
            if p.id == player_id:
                return p
        return None

    def deep_copy(self) -> 'GameState':
        """Creates a perfect, independent copy of the game state."""
        return copy.deepcopy(self)

    def add_log(self, message: str):
        """Adds a message to the turn log to be displayed to players."""
        self.turn_log.append(message)

    def clear_turn_log(self):
        """Clears the log at the start of a new player's turn."""
        self.turn_log.clear()