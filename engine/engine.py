import random
from models.game_state import GameState
from models.components import Player, Candidacy
from models.cards import Deck, PoliticalArchetype, PersonalMandate
from engine import resolvers
from engine.actions import Action

class GameEngine:
    def __init__(self, game_data):
        self.game_data = game_data
        # A dispatch table to map action classes to their resolver functions
        self.action_resolvers = {
            "ActionFundraise": resolvers.resolve_fundraise,
            "ActionNetwork": resolvers.resolve_network,
            "ActionSponsorLegislation": resolvers.resolve_sponsor_legislation,
            "ActionFormAlliance": resolvers.resolve_form_alliance,
            "ActionDeclareCandidacy": resolvers.resolve_declare_candidacy,
        }

    def start_new_game(self, player_names: list[str]) -> GameState:
        """Creates the initial GameState for a new game, including archetype setup."""
        archetypes = list(self.game_data['archetypes'])
        mandates = list(self.game_data['mandates'])
        random.shuffle(archetypes)
        random.shuffle(mandates)

        players = []
        for i, name in enumerate(player_names):
            player = Player(
                id=i, 
                name=name, 
                archetype=archetypes.pop(), 
                mandate=mandates.pop(),
                pc=25 
            )
            players.append(player)
        
        state = GameState(
            players=players,
            offices=self.game_data['offices'],
            legislation_options=self.game_data['legislation'],
            event_deck=Deck(self.game_data['events']),
            scrutiny_deck=Deck(self.game_data['scrutiny']),
            alliance_deck=Deck(self.game_data['alliances']),
            favor_supply=list(self.game_data['favors'])
        )

        # Apply archetype-specific setup rules
        for p in state.players:
            if p.archetype.id == "INSIDER":
                p.pc = 15
                p.current_office = state.offices["STATE_SENATOR"]
                state.add_log(f"{p.name} starts as The Insider, holding the State Senator office with 15 PC.")
        
        return state

    def process_action(self, state: GameState, action: Action) -> GameState:
        """Routes an action to the correct resolver and advances the game state."""
        state.clear_turn_log()
        player = state.get_player_by_id(action.player_id)
        if not player or state.get_current_player().id != player.id:
            raise ValueError("It's not your turn or the player is invalid.")
        
        resolver = self.action_resolvers.get(action.__class__.__name__)
        if not resolver:
            raise ValueError(f"No resolver found for action: {action.__class__.__name__}")
        
        # The resolver function will handle the logic and return the new state
        new_state = resolver(state, action)
        
        return self._advance_turn(new_state)

    def _advance_turn(self, state: GameState) -> GameState:
        """
        Advances to the next player's turn. If all players have acted,
        triggers the Upkeep Phase.
        """
        state.current_player_index += 1
        if state.current_player_index >= len(state.players):
            state.current_player_index = 0
            return self.run_upkeep_phase(state)
        
        # If the turn advances normally, set to next player's action phase
        state.current_phase = "ACTION_PHASE"
        return state

    def run_upkeep_phase(self, state: GameState) -> GameState:
        """Runs the entire Upkeep Phase automatically."""
        state.current_phase = "UPKEEP_PHASE"
        state.add_log("\n--- UPKEEP PHASE ---")

        state = resolvers.resolve_upkeep(state)

        # After upkeep, advance the round marker
        state.round_marker += 1
        
        if state.round_marker > 4:
            # End of the term, trigger the Election Phase
            return self.run_election_phase(state)
        else:
            # Otherwise, start the next round with the Event Phase
            state.current_phase = "EVENT_PHASE"
            return state

    def run_election_phase(self, state: GameState) -> GameState:
        """Triggers the election resolutions and resets for the next term."""
        state.current_phase = "ELECTION_PHASE"
        state.add_log("\n--- ELECTION PHASE ---")
        
        new_state = resolvers.resolve_elections(state)

        # Reset for the new term
        new_state.round_marker = 1
        new_state.secret_candidacies.clear()
        # Reset any term-based abilities or effects
        for effect in list(new_state.active_effects):
            if effect in ["WAR_BREAKS_OUT", "VOTER_APATHY"]: # Add other term-long effects here
                new_state.active_effects.remove(effect)

        new_state.add_log("\nA new term begins!")
        new_state.current_phase = "EVENT_PHASE" # Ready for the next term's event
        return new_state

    def run_event_phase(self, state: GameState) -> GameState:
        """Draws an event card and resolves it using the resolver module."""
        state.clear_turn_log()
        
        new_state = resolvers.resolve_event_card(state)
        
        new_state.current_phase = "ACTION_PHASE"
        return new_state

    def is_game_over(self, state: GameState) -> bool:
        """Checks for a win condition (a player holding the Presidency)."""
        for p in state.players:
            if p.current_office and p.current_office.id == "PRESIDENT":
                state.add_log(f"\n{p.name.upper()} HAS BEEN ELECTED PRESIDENT!")
                return True
        return False