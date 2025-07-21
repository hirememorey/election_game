from dataclasses import dataclass, field
from typing import Optional, List, Callable
import random

# --- Base Classes ---

@dataclass
class Card:
    """Base class for all cards in the game."""
    id: str
    title: str
    description: str

    def to_dict(self):
        return {"id": self.id, "title": self.title, "description": self.description}

@dataclass
class PoliticalArchetype(Card):
    """A special role defining a player's unique abilities."""
    # Specific logic will be handled by the game engine based on the card's ID.
    pass

@dataclass
class PersonalMandate(Card):
    """A secret objective for a player."""
    # The condition for fulfilling the mandate.
    # This will be checked at the end of the game.
    pass

@dataclass
class EventCard(Card):
    """A card drawn each round with immediate effects on the game."""
    # The effect can be a simple lambda or a complex function defined in the engine.
    # We'll use an effect_id to link to a handler in the engine.
    effect_id: str

    def to_dict(self):
        data = super().to_dict()
        data['effect_id'] = self.effect_id
        return data

@dataclass
class ScrutinyCard(EventCard):
    """A negative event card, usually drawn as a result of a scandal."""
    pass

@dataclass
class AllianceCard(Card):
    """A powerful ally who provides a bonus but also has a weakness or cost."""
    upkeep_cost: int = 0
    weakness_description: str = ""
    # Effect and weakness logic will be handled by the engine based on the card's ID.

    def to_dict(self):
        data = super().to_dict()
        data['upkeep_cost'] = self.upkeep_cost
        data['weakness_description'] = self.weakness_description
        return data

# --- Utility Classes ---

@dataclass
class Deck:
    """A class to represent and manage a deck of cards."""
    cards: List[Card] = field(default_factory=list)

    def __post_init__(self):
        # Keep an immutable copy of the original cards to allow for reshuffling
        self._original_cards = list(self.cards)
        self.shuffle()

    def shuffle(self):
        """Shuffles the deck."""
        random.shuffle(self.cards)

    def draw(self) -> Optional[Card]:
        """Draws a card from the top of the deck."""
        if self.is_empty():
            print("Deck is empty. Reshuffling from discard...")
            self.reshuffle_from_discard()
        
        return self.cards.pop(0) if self.cards else None

    def reshuffle_from_discard(self):
        """Resets the deck with its original cards and shuffles it."""
        self.cards = list(self._original_cards)
        self.shuffle()
        print("Deck has been reshuffled.")

    def is_empty(self) -> bool:
        """Checks if the deck is empty."""
        return len(self.cards) == 0

    def __len__(self) -> int:
        return len(self.cards)