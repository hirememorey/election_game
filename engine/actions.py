from dataclasses import dataclass, field
from typing import List

@dataclass
class Action:
    """Base class for all player actions."""
    player_id: int

@dataclass
class ActionFundraise(Action):
    pass

@dataclass
class ActionNetwork(Action):
    pass



@dataclass
class ActionSponsorLegislation(Action):
    legislation_id: str

@dataclass
class ActionDeclareCandidacy(Action):
    office_id: str
    committed_pc: int

@dataclass
class ActionUseFavor(Action):
    favor_id: str
    target_player_id: int = -1  # For favors that affect other players, -1 means no target
    choice: str = ""  # For favors that require a choice (e.g., "discard_favors" or "reveal_archetype")

@dataclass
class ActionSupportLegislation(Action):
    legislation_id: str
    support_amount: int  # PC committed to support

@dataclass
class ActionOpposeLegislation(Action):
    legislation_id: str
    oppose_amount: int  # PC committed to oppose

@dataclass
class ActionProposeTrade(Action):
    """Propose a trade to another player during legislation voting."""
    target_player_id: int
    legislation_id: str
    offered_pc: int = 0
    offered_favor_ids: List[str] = field(default_factory=list)
    requested_vote: str = "support"  # "support", "oppose", or "abstain"

@dataclass
class ActionAcceptTrade(Action):
    """Accept a trade offer from another player."""
    trade_offer_id: int  # Index in the active_trade_offers list

@dataclass
class ActionDeclineTrade(Action):
    """Decline a trade offer from another player."""
    trade_offer_id: int  # Index in the active_trade_offers list

@dataclass
class ActionCompleteTrading(Action):
    """Complete the trading phase and move to voting."""
    pass

@dataclass
class ActionPassTurn(Action):
    """Pass turn without taking any action."""
    pass

@dataclass
class ActionResolveLegislation(Action):
    """System action to resolve pending legislation."""
    player_id: int = -1  # System action, no specific player

@dataclass
class ActionResolveElections(Action):
    """System action to resolve elections."""
    player_id: int = -1  # System action, no specific player

@dataclass
class ActionAcknowledgeResults(Action):
    """System action to acknowledge results and start new term."""
    player_id: int = -1  # System action, no specific player