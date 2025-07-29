from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Type

@dataclass
class Action:
    """Base class for all player actions."""
    player_id: int

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the action to a dictionary."""
        data = asdict(self)
        data['action_type'] = self.__class__.__name__
        return data

    @classmethod
    def from_dict(cls, data: dict):
        """Creates an Action object from a dictionary."""
        # This is a generic implementation. Subclasses with more complex
        # attributes will need to override this.
        action_type = data.pop("action_type", None) # action_type is not a constructor argument
        # For simple actions, the remaining data keys should match the constructor args
        return cls(**data)


# Dictionary to map action type names back to their classes
ACTION_CLASSES: Dict[str, Type[Action]] = {
    cls.action_type: cls for cls in Action.__subclasses__()
}

def _register_action(cls):
    ACTION_CLASSES[cls.__name__] = cls
    return cls

@dataclass
@_register_action
class ActionFundraise(Action):
    pass

@dataclass
@_register_action
class ActionNetwork(Action):
    pass


@dataclass
@_register_action
class ActionSponsorLegislation(Action):
    legislation_id: str

@dataclass
@_register_action
class ActionDeclareCandidacy(Action):
    office_id: str
    committed_pc: int

@dataclass
@_register_action
class ActionUseFavor(Action):
    favor_id: str
    target_player_id: int = -1  # For favors that affect other players, -1 means no target
    choice: str = ""  # For favors that require a choice (e.g., "discard_favors" or "reveal_archetype")

@dataclass
@_register_action
class ActionSupportLegislation(Action):
    legislation_id: str
    support_amount: int  # PC committed to support

@dataclass
@_register_action
class ActionOpposeLegislation(Action):
    legislation_id: str
    oppose_amount: int  # PC committed to oppose

@dataclass
@_register_action
class ActionProposeTrade(Action):
    """Propose a trade to another player during legislation voting."""
    target_player_id: int
    legislation_id: str
    offered_pc: int = 0
    offered_favor_ids: List[str] = field(default_factory=list)
    requested_vote: str = "support"  # "support", "oppose", or "abstain"

@dataclass
@_register_action
class ActionAcceptTrade(Action):
    """Accept a trade offer from another player."""
    trade_offer_id: int  # Index in the active_trade_offers list

@dataclass
@_register_action
class ActionDeclineTrade(Action):
    """Decline a trade offer from another player."""
    trade_offer_id: int  # Index in the active_trade_offers list

@dataclass
@_register_action
class ActionCompleteTrading(Action):
    """Complete the trading phase and move to voting."""
    pass

@dataclass
@_register_action
class ActionPassTurn(Action):
    """Pass turn without taking any action."""
    pass

@dataclass
@_register_action
class ActionResolveLegislation(Action):
    """System action to resolve pending legislation."""
    player_id: int = -1  # System action, no specific player

@dataclass
@_register_action
class ActionResolveElections(Action):
    """System action to resolve elections."""
    player_id: int = -1  # System action, no specific player

@dataclass
@_register_action
class ActionAcknowledgeResults(Action):
    """System action to acknowledge results and start new term."""
    player_id: int = -1  # System action, no specific player


class AcknowledgeAITurn(Action):
    """A special action used by the human player to acknowledge the AI's turn."""
    action_type: str = "AcknowledgeAITurn"
    player_id: int