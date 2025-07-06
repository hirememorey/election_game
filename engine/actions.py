from dataclasses import dataclass

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
class ActionFormAlliance(Action):
    pass

@dataclass
class ActionSponsorLegislation(Action):
    legislation_id: str

@dataclass
class ActionDeclareCandidacy(Action):
    office_id: str
    committed_pc: int