import random
from models.game_state import GameState
from models.components import Player, Candidacy
from models.cards import Deck, PoliticalArchetype, PersonalMandate
from engine import resolvers
from engine.actions import Action

class GameEngine:
    def __init__(self, game_data):
        self.game_data = game_data
        # Action point costs
        self.action_point_costs = {
            "ActionFundraise": 1,
            "ActionNetwork": 1,
            "ActionSponsorLegislation": 2,
            "ActionDeclareCandidacy": 2,
            "ActionUseFavor": 1,  # Now costs 1 AP
            "ActionSupportLegislation": 1,
            "ActionOpposeLegislation": 1,
            "ActionProposeTrade": 0,  # Free during trading phase
            "ActionAcceptTrade": 0,   # Free during trading phase
            "ActionDeclineTrade": 0,  # Free during trading phase
            "ActionCompleteTrading": 0,  # Free during trading phase
            "ActionCampaign": 2,  # New action
            "ActionPassTurn": 0,  # Free action to pass turn
        }
        # A dispatch table to map action classes to their resolver functions
        self.action_resolvers = {
            "ActionFundraise": resolvers.resolve_fundraise,
            "ActionNetwork": resolvers.resolve_network,
            "ActionSponsorLegislation": resolvers.resolve_sponsor_legislation,
            "ActionDeclareCandidacy": resolvers.resolve_declare_candidacy,
            "ActionUseFavor": resolvers.resolve_use_favor,
            "ActionSupportLegislation": resolvers.resolve_support_legislation,
            "ActionOpposeLegislation": resolvers.resolve_oppose_legislation,
            "ActionProposeTrade": resolvers.resolve_propose_trade,
            "ActionAcceptTrade": resolvers.resolve_accept_trade,
            "ActionDeclineTrade": resolvers.resolve_decline_trade,
            "ActionCompleteTrading": resolvers.resolve_complete_trading,
            "ActionCampaign": resolvers.resolve_campaign,
            "ActionPassTurn": resolvers.resolve_pass_turn,
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
            event_deck=Deck(list(self.game_data['events'])),
            scrutiny_deck=Deck(list(self.game_data['scrutiny'])),
            alliance_deck=Deck(list(self.game_data['alliances'])),
            favor_supply=list(self.game_data['favors'])
        )

        # Apply archetype-specific setup rules
        for p in state.players:
            if p.archetype.id == "INSIDER":
                p.pc = 15
                p.current_office = state.offices["STATE_SENATOR"]
                state.add_log(f"{p.name} starts as The Insider, holding the State Senator office with 15 PC.")
        
        # Initialize action points for all players
        for p in state.players:
            state.action_points[p.id] = 2
        
        return state

    def process_action(self, state: GameState, action: Action) -> GameState:
        """Routes an action to the correct resolver and advances the game state."""
        state.clear_turn_log()
        player = state.get_player_by_id(action.player_id)
        if not player or state.get_current_player().id != player.id:
            raise ValueError("It's not your turn or the player is invalid.")
        
        # Check action point cost
        action_cost = self.action_point_costs.get(action.__class__.__name__, 0)
        
        # Apply public gaffe effect (increased AP cost for public actions)
        if player.id in state.public_gaffe_players:
            if action.__class__.__name__ in ["ActionSponsorLegislation", "ActionDeclareCandidacy", "ActionCampaign"]:
                action_cost += 1
                state.add_log(f"{player.name} must pay +1 AP due to public gaffe effect.")
                # Remove the effect after it's applied
                state.public_gaffe_players.discard(player.id)
        
        if state.action_points[player.id] < action_cost:
            raise ValueError(f"Not enough action points. Need {action_cost}, have {state.action_points[player.id]}.")
        
        resolver = self.action_resolvers.get(action.__class__.__name__)
        if not resolver:
            raise ValueError(f"No resolver found for action: {action.__class__.__name__}")
        
        # Deduct action points
        state.action_points[player.id] -= action_cost
        
        # The resolver function will handle the logic and return the new state
        new_state = resolver(state, action)
        
        return self._advance_turn(new_state)

    def _advance_turn(self, state: GameState) -> GameState:
        """
        Advances to the next player's turn or next action within turn.
        """
        current_player = state.get_current_player()
        
        # Initialize action points if not set
        if current_player.id not in state.action_points:
            state.action_points[current_player.id] = 2
        
        # If player has action points remaining, stay on their turn
        if state.action_points[current_player.id] > 0:
            return state
        
        # Player has used all AP, advance to next player
        state.current_player_index += 1
        
        # Handle legislation session phase
        if state.legislation_session_active:
            if state.current_trade_phase:
                # Trading phase - advance to next player
                if state.current_player_index >= len(state.players):
                    # All players have had a chance to trade, move to voting phase
                    state.current_trade_phase = False
                    state.current_player_index = 0  # Reset for voting
                    state.add_log("\n--- VOTING PHASE ---")
                    state.add_log("Trading complete. Players may now vote on legislation.")
                    # Grant 1 AP to each player for voting
                    for player in state.players:
                        state.action_points[player.id] = 1
                    state.current_phase = "LEGISLATION_PHASE"
                    return state
                else:
                    # Continue to next player's trading turn
                    state.current_phase = "LEGISLATION_PHASE"
                    return state
            else:
                # Voting phase - advance to next player
                if state.current_player_index >= len(state.players):
                    # All players have voted, STOP and set awaiting_legislation_resolution
                    state.add_log("\n--- LEGISLATION SESSION: Ready to Resolve All Bills ---")
                    state.awaiting_legislation_resolution = True
                    state.current_player_index = 0  # Reset to prevent invalid index
                    # Do not resolve or advance further until manual trigger
                    return state
                else:
                    # Continue to next player's voting turn
                    state.current_phase = "LEGISLATION_PHASE"
                    return state
        
        # Handle normal action phase
        if state.current_player_index >= len(state.players):
            # All players have exhausted their AP, advance to next round
            state.current_player_index = 0
            return self.run_upkeep_phase(state)
        
        # Reset action points for new player (only if we haven't advanced to upkeep)
        new_player = state.get_current_player()
        state.action_points[new_player.id] = 2
        
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
        
        if state.round_marker >= 5:
            # End of the term, trigger the Legislation Session Phase
            # Reset round marker to 4 for clarity during legislation session
            state.round_marker = 4
            state.add_log("\n--- END OF TERM ---")
            state.add_log("Round 4 complete. Moving to legislation session.")
            return self.run_legislation_session(state)
        else:
            # Otherwise, automatically start the next round with the Event Phase
            state.add_log(f"\n--- ROUND {state.round_marker} ---")
            state.add_log("\n--- EVENT PHASE ---")
            return self.run_event_phase(state)

    def run_legislation_session(self, state: GameState) -> GameState:
        """Triggers the legislation session where all pending legislation is resolved."""
        state.current_phase = "LEGISLATION_PHASE"
        state.legislation_session_active = True
        state.add_log("\n--- LEGISLATION SESSION ---")
        state.add_log("All sponsored legislation from this term will now be voted on.")
        
        # Clear action points during legislation session - players vote, don't take regular actions
        for player in state.players:
            state.action_points[player.id] = 0
        
        # Move any current pending legislation to term legislation
        if state.pending_legislation and not state.pending_legislation.resolved:
            state.term_legislation.append(state.pending_legislation)
            state.pending_legislation = None
        
        # If no legislation was sponsored this term, skip to elections
        if not state.term_legislation:
            state.add_log("No legislation was sponsored this term. Moving to elections.")
            return self.run_election_phase(state)
        
        # Start with trading phase
        state.current_trade_phase = True
        state.current_player_index = 0  # Start with first player
        state.add_log("Trading Phase: Players may propose trades for votes on legislation.")
        state.add_log("Each player gets one turn to propose trades before voting begins.")
        
        return state

    def run_election_phase(self, state: GameState) -> GameState:
        """Triggers the election resolutions and resets for the new term."""
        state.current_phase = "ELECTION_PHASE"
        state.add_log("\n--- ELECTION PHASE ---")
        # Grant 2 AP to each player at the start of the election phase
        for player in state.players:
            state.action_points[player.id] = 2
        new_state = resolvers.resolve_elections(state)
        # Reset for the new term
        new_state.round_marker = 1
        new_state.current_player_index = 0  # Reset player index for new term
        new_state.secret_candidacies.clear()
        new_state.term_legislation.clear()  # Clear term legislation for new term
        new_state.pending_legislation = None  # Clear any pending legislation for new term
        # Reset any term-based abilities or effects
        for effect in list(new_state.active_effects):
            if effect in ["WAR_BREAKS_OUT", "VOTER_APATHY"]: # Add other term-long effects here
                new_state.active_effects.remove(effect)
        
        # Reset archetype-specific tracking for new term
        new_state.fundraiser_first_fundraise_used.clear()  # Reset Fundraiser first Fundraise tracking
        new_state.add_log("\nA new term begins!")
        # Automatically run the event phase for the new term
        new_state.add_log("\n--- EVENT PHASE ---")
        new_state = self.run_event_phase(new_state)
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

    def resolve_legislation_session(self, state: GameState) -> GameState:
        """Manually resolve all pending legislation at the end of the term."""
        if not state.awaiting_legislation_resolution:
            state.add_log("No legislation session to resolve.")
            return state
        state.add_log("\n--- LEGISLATION SESSION: Resolving All Bills ---")
        for legislation in state.term_legislation:
            if not legislation.resolved:
                state.pending_legislation = legislation
                state = resolvers.resolve_pending_legislation(state)
        # Clear term legislation and move to elections
        state.term_legislation.clear()
        state.legislation_session_active = False
        state.current_player_index = 0  # Reset for new term
        state.awaiting_legislation_resolution = False
        state.awaiting_election_resolution = True
        return state

    def resolve_legislation_session_with_secrets(self, state: GameState, secret_commitments: dict) -> GameState:
        """Manually resolve all pending legislation using the Secret Commitment System."""
        if not state.awaiting_legislation_resolution:
            state.add_log("No legislation session to resolve.")
            return state
        
        state.add_log("\n--- LEGISLATION SESSION: Secret Commitment Reveal ---")
        state.add_log("All secret commitments will now be revealed!")
        
        for legislation in state.term_legislation:
            if not legislation.resolved:
                legislation_id = legislation.legislation_id
                state.add_log(f"\n--- Revealing commitments for {legislation_id} ---")
                
                # Get secret commitments for this legislation
                if legislation_id in secret_commitments:
                    commitments = secret_commitments[legislation_id]
                    
                    # Reveal each commitment dramatically
                    for player_id, stance, amount in commitments:
                        player = state.get_player_by_id(player_id)
                        if player:
                            if stance == 'support':
                                state.add_log(f"🎭 REVEAL: {player.name} secretly supported with {amount} PC!")
                                # Apply PC deduction (if not already done)
                                if player.pc >= amount:
                                    player.pc -= amount
                                legislation.support_players[player_id] = amount
                            else:  # oppose
                                state.add_log(f"🎭 REVEAL: {player.name} secretly opposed with {amount} PC!")
                                # Apply PC deduction (if not already done)
                                if player.pc >= amount:
                                    player.pc -= amount
                                legislation.oppose_players[player_id] = amount
                else:
                    state.add_log(f"No secret commitments found for {legislation_id}")
                
                # Now resolve the legislation using the existing system
                state.pending_legislation = legislation
                state = resolvers.resolve_pending_legislation(state)
        
        # Clear term legislation and move to elections
        state.term_legislation.clear()
        state.legislation_session_active = False
        state.current_player_index = 0  # Reset for new term
        state.awaiting_legislation_resolution = False
        state.awaiting_election_resolution = True
        return state

    def resolve_elections_session(self, state: GameState) -> GameState:
        """Manually resolve all elections after legislation session."""
        if not state.awaiting_election_resolution:
            state.add_log("No election session to resolve.")
            return state
        state.current_phase = "ELECTION_PHASE"
        state.add_log("\n--- ELECTION PHASE ---")
        # Grant 2 AP to each player at the start of the election phase
        for player in state.players:
            state.action_points[player.id] = 2
        new_state = resolvers.resolve_elections(state)
        # Reset for the new term
        new_state.round_marker = 1
        new_state.current_player_index = 0  # Reset player index for new term
        new_state.secret_candidacies.clear()
        new_state.term_legislation.clear()  # Clear term legislation for new term
        new_state.pending_legislation = None  # Clear any pending legislation for new term
        # Reset any term-based abilities or effects
        for effect in list(new_state.active_effects):
            if effect in ["WAR_BREAKS_OUT", "VOTER_APATHY"]: # Add other term-long effects here
                new_state.active_effects.remove(effect)
        # Reset archetype-specific tracking for new term
        new_state.fundraiser_first_fundraise_used.clear()  # Reset Fundraiser first Fundraise tracking
        new_state.add_log("\nA new term begins!")
        # Automatically run the event phase for the new term
        new_state.add_log("\n--- EVENT PHASE ---")
        new_state = self.run_event_phase(new_state)
        new_state.awaiting_election_resolution = False
        return new_state