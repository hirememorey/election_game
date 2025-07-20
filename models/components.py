from dataclasses import dataclass, field
from typing import Optional, List, Dict
from models.cards import PersonalMandate, PoliticalArchetype, AllianceCard

@dataclass
class Office:
    """Represents a political office a player can hold."""
    id: str
    title: str
    tier: int
    candidacy_cost: int
    income: int
    npc_challenger_bonus: int

@dataclass
class Legislation:
    """Represents a bill that can be sponsored."""
    id: str
    title: str
    cost: int
    # Target for net influence (support - opposition)
    success_target: int  # Minimum net influence needed for success
    crit_target: int     # Minimum net influence needed for critical success
    # Rewards are PC gain for the sponsor
    success_reward: int
    crit_reward: int
    # Penalty is PC loss for the sponsor on failure
    failure_penalty: int
    # Public mood change on success
    mood_change: int = 0

@dataclass
class PoliticalFavor:
    """A one-time use token for a small advantage."""
    id: str
    description: str

@dataclass
class Pledge:
    """A token representing a binding promise between players."""
    # The player who owes the action
    promiser_id: int
    # The player to whom the action is owed
    owed_to_id: int
    # A description of the promised action, for logging
    promise_description: str

@dataclass
class Candidacy:
    """Stores a player's secret declaration for an office."""
    player_id: int
    office_id: str
    committed_pc: int

@dataclass
class Player:
    """Represents a player's state in the game."""
    id: int
    name: str
    archetype: PoliticalArchetype
    mandate: PersonalMandate
    pc: int  # Political Capital
    current_office: Optional[Office] = None
    allies: List[AllianceCard] = field(default_factory=list)
    favors: List[PoliticalFavor] = field(default_factory=list)

    @property
    def is_incumbent(self) -> bool:
        """A player is an incumbent if they hold any office."""
        return self.current_office is not None