from dataclasses import dataclass
from engine.actions import Action

@dataclass
class UIAction(Action):
    """
    Base class for actions that only exist to trigger a UI sub-menu.
    These actions do not have a resolver in the engine because they are handled
    by the GameSession before reaching the engine.
    """
    is_ui_action: bool = True

@dataclass
class UISponsorLegislation(UIAction):
    pass

@dataclass
class UISupportLegislation(UIAction):
    pass

@dataclass
class UIOpposeLegislation(UIAction):
    pass 