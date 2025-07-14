from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
import copy

from models.components import Player, Office, Legislation, PoliticalFavor, Candidacy, Pledge, CampaignInfluence
from models.cards import Deck

@dataclass
class TradeOffer:
    """Represents a trade offer made during legislation voting."""
    offerer_id: int  # Player making the offer
    target_id: int   # Player being offered to
    legislation_id: str  # Legislation the trade is about
    offered_pc: int = 0  # PC being offered
    offered_favors: List[str] = field(default_factory=list)  # Favor IDs being offered
    requested_vote: str = "support"  # "support", "oppose", or "abstain"
    accepted: bool = False
    declined: bool = False

@dataclass
class PendingLegislation:
    """Tracks legislation that has been sponsored and is waiting for support/opposition."""
    legislation_id: str
    sponsor_id: int
    support_players: Dict[int, int] = field(default_factory=dict)  # player_id -> pc_amount
    oppose_players: Dict[int, int] = field(default_factory=dict)   # player_id -> pc_amount
    resolved: bool = False

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
    
    # Action Points System
    action_points: Dict[int, int] = field(default_factory=dict)  # player_id -> remaining AP
    action_point_costs: Dict[str, int] = field(default_factory=dict)  # action_type -> AP cost
    
    # State trackers for a single term/round
    turn_log: List[str] = field(default_factory=list)
    secret_candidacies: List[Candidacy] = field(default_factory=list)
    campaign_influences: List[CampaignInfluence] = field(default_factory=list)  # Campaign influence for future elections
    
    # New: Track pending legislation and candidacy timing
    pending_legislation: Optional[PendingLegislation] = None
    
    # End-of-term legislation session
    term_legislation: List[PendingLegislation] = field(default_factory=list)  # All legislation sponsored this term
    
    # Lingering effects from events, identified by event ID
    active_effects: Set[str] = field(default_factory=set)
    
    # Negative favor effects tracking
    negative_favor_effects: Dict[int, List[Dict]] = field(default_factory=dict)  # player_id -> list of active negative effects
    political_debts: Dict[int, int] = field(default_factory=dict)  # debtor_id -> creditor_id
    hot_potato_holder: Optional[int] = None  # player_id currently holding the hot potato
    public_gaffe_players: Set[int] = field(default_factory=set)  # players with public gaffe effect
    media_scrutiny_players: Set[int] = field(default_factory=set)  # players with media scrutiny effect
    compromised_players: Set[int] = field(default_factory=set)  # players who revealed their archetype
    
    # Archetype-specific tracking
    fundraiser_first_fundraise_used: Set[int] = field(default_factory=set)  # players who have used their first Fundraise action this term
    
    # History for checking mandates/events
    last_sponsor_result: Dict = field(default_factory=dict) # {'player_id': int, 'passed': bool}
    legislation_history: List[Dict] = field(default_factory=list) # [{'sponsor_id': int, 'leg_id': str, 'outcome': str}]

    # --- NEW: Manual phase resolution flags ---
    awaiting_legislation_resolution: bool = False
    awaiting_election_resolution: bool = False

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