from .actions import Action

class UIAction(Action):
    """Base class for actions that are primarily for UI grouping and require a second step."""
    def __init__(self, player_id: int, text: str):
        super().__init__(player_id)
        self.text = text

    def to_dict(self):
        return {
            "action_type": self.__class__.__name__,
            "player_id": self.player_id,
            "text": self.text,
            "is_ui_action": True
        }

class UISponsorLegislation(UIAction):
    def __init__(self, player_id: int):
        super().__init__(player_id, "Sponsor Legislation")

class UISupportLegislation(UIAction):
    def __init__(self, player_id: int):
        super().__init__(player_id, "Support Legislation")

class UIOpposeLegislation(UIAction):
    def __init__(self, player_id: int):
        super().__init__(player_id, "Oppose Legislation") 