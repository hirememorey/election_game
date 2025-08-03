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

    def to_dict(self):
        return {
            "id": self.id, "title": self.title, "tier": self.tier,
            "candidacy_cost": self.candidacy_cost, "income": self.income,
            "npc_challenger_bonus": self.npc_challenger_bonus
        }

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

    def to_dict(self):
        return {
            "id": self.id, "title": self.title, "cost": self.cost,
            "success_target": self.success_target, "crit_target": self.crit_target,
            "success_reward": self.success_reward, "crit_reward": self.crit_reward,
            "failure_penalty": self.failure_penalty, "mood_change": self.mood_change
        }

@dataclass
class PoliticalFavor:
    """A one-time use token for a small advantage."""
    id: str
    description: str

    def to_dict(self):
        return {"id": self.id, "description": self.description}

@dataclass
class Pledge:
    """A token representing a binding promise between players."""
    # The player who owes the action
    promiser_id: int
    # The player to whom the action is owed
    owed_to_id: int
    # A description of the promised action, for logging
    promise_description: str

    def to_dict(self):
        return {
            "promiser_id": self.promiser_id, "owed_to_id": self.owed_to_id,
            "promise_description": self.promise_description
        }

@dataclass
class Candidacy:
    """Stores a player's secret declaration for an office."""
    player_id: int
    office_id: str
    committed_pc: int

    def to_dict(self):
        return {
            "player_id": self.player_id, "office_id": self.office_id,
            "committed_pc": self.committed_pc
        }

@dataclass
class Player:
    """Represents a player's state in the game."""
    id: int
    name: str
    archetype: PoliticalArchetype
    mandate: PersonalMandate
    pc: int  # Political Capital
    action_points: int = 2
    current_office: Optional[Office] = None
    allies: List[AllianceCard] = field(default_factory=list)
    favors: List[PoliticalFavor] = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id, "name": self.name,
            "archetype": self.archetype.to_dict(),
            "mandate": self.mandate.to_dict(),
            "pc": self.pc,
            "action_points": self.action_points,
            "current_office": self.current_office.to_dict() if self.current_office else None,
            "allies": [ally.to_dict() for ally in self.allies],
            "favors": [favor.to_dict() for favor in self.favors],
            "is_incumbent": self.is_incumbent
        }

    @property
    def is_incumbent(self) -> bool:
        """A player is an incumbent if they hold any office."""
        return self.current_office is not None