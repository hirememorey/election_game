from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any

@dataclass
class Action:
    """Base class for all player actions."""
    player_id: int

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the action to a dictionary."""
        data = asdict(self)
        data['action_type'] = self.__class__.__name__
        return data

# Dictionary to map action type names back to their classes
ACTION_CLASSES = {}

def _register_action(cls):
    ACTION_CLASSES[cls.__name__] = cls
    return cls

@_register_action
@dataclass
class ActionFundraise(Action):
    pass

@_register_action
@dataclass
class ActionNetwork(Action):
    pass


@_register_action
@dataclass
class ActionSponsorLegislation(Action):
    legislation_id: str

@_register_action
@dataclass
class ActionDeclareCandidacy(Action):
    office_id: str
    committed_pc: int

@_register_action
@dataclass
class ActionUseFavor(Action):
    favor_id: str
    target_player_id: int = -1  # For favors that affect other players, -1 means no target
    choice: str = ""  # For favors that require a choice (e.g., "discard_favors" or "reveal_archetype")

@_register_action
@dataclass
class ActionSupportLegislation(Action):
    legislation_id: str
    support_amount: int  # PC committed to support

@_register_action
@dataclass
class ActionOpposeLegislation(Action):
    legislation_id: str
    oppose_amount: int  # PC committed to oppose

@_register_action
@dataclass
class ActionProposeTrade(Action):
    """Propose a trade to another player during legislation voting."""
    target_player_id: int
    legislation_id: str
    offered_pc: int = 0
    offered_favor_ids: List[str] = field(default_factory=list)
    requested_vote: str = "support"  # "support", "oppose", or "abstain"

@_register_action
@dataclass
class ActionAcceptTrade(Action):
    """Accept a trade offer from another player."""
    trade_offer_id: int  # Index in the active_trade_offers list

@_register_action
@dataclass
class ActionDeclineTrade(Action):
    """Decline a trade offer from another player."""
    trade_offer_id: int  # Index in the active_trade_offers list

@_register_action
@dataclass
class ActionCompleteTrading(Action):
    """Complete the trading phase and move to voting."""
    pass

@_register_action
@dataclass
class ActionPassTurn(Action):
    """Pass turn without taking any action."""
    pass

@_register_action
@dataclass
class ActionResolveLegislation(Action):
    """System action to resolve pending legislation."""
    player_id: int = -1  # System action, no specific player

@_register_action
@dataclass
class ActionResolveElections(Action):
    """System action to resolve elections."""
    player_id: int = -1  # System action, no specific player

@_register_action
@dataclass
class ActionAcknowledgeResults(Action):
    """System action to acknowledge results and start new term."""
    player_id: int = -1  # System action, no specific player