import random
from models.game_state import GameState
from models.components import Player, Candidacy
from models.cards import Deck, PoliticalArchetype, PersonalMandate
from engine import resolvers
from engine.actions import Action
from engine.scoring import calculate_final_scores
from typing import List
from engine.actions import ActionFundraise, ActionNetwork, ActionSponsorLegislation, ActionDeclareCandidacy, ActionUseFavor, ActionSupportLegislation, ActionOpposeLegislation, ActionPassTurn, ActionResolveLegislation, ActionResolveElections, ActionAcknowledgeResults

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
            "ActionPassTurn": resolvers.resolve_pass_turn,
            "ActionResolveLegislation": resolvers.resolve_resolve_legislation,
            "ActionResolveElections": resolvers.resolve_resolve_elections,
            "ActionAcknowledgeResults": resolvers.resolve_acknowledge_results,
            # Trading actions removed
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

        # Harden the backend: reject actions during non-action phases.
        if (state.awaiting_results_acknowledgement or
            state.awaiting_legislation_resolution or
            state.awaiting_election_resolution):
            raise ValueError("Invalid action: The game is awaiting resolution or acknowledgement.")

        player = state.get_player_by_id(action.player_id)
        if not player or state.get_current_player().id != player.id:
            raise ValueError("It's not your turn or the player is invalid.")
        
        # Check action point cost
        action_cost = self.action_point_costs.get(action.__class__.__name__, 0)
        
        # Apply public gaffe effect (increased AP cost for public actions)
        if player.id in state.public_gaffe_players:
            if action.__class__.__name__ in ["ActionSponsorLegislation", "ActionDeclareCandidacy"]:
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
        
        # Always advance turn after ActionPassTurn
        if action.__class__.__name__ == "ActionPassTurn":
            new_state = self._advance_turn(new_state)
        
        # Always advance turn after any action
        new_state = self._advance_turn(new_state)
        
        # CRITICAL FIX: Only auto-advance if we're in ACTION_PHASE and not in resolution phases
        # This prevents legislation session from being immediately resolved
        while (new_state.current_phase == "ACTION_PHASE" and 
               all(ap <= 0 for ap in new_state.action_points.values()) and
               not new_state.awaiting_legislation_resolution and
               not new_state.awaiting_election_resolution):
            new_state = self._advance_turn(new_state)
        
        # CRITICAL FIX: If at end of round 4 and all players have 0 or less AP, force upkeep phase
        if (new_state.current_phase == "ACTION_PHASE" and
            new_state.round_marker == 4 and
            all(ap <= 0 for ap in new_state.action_points.values()) and
            not new_state.awaiting_legislation_resolution and
            not new_state.awaiting_election_resolution):
            print("[DEBUG] Forcing upkeep phase at end of round 4 due to all APs exhausted.")
            new_state = self.run_upkeep_phase(new_state)
        
        return new_state

    def _advance_turn(self, state: GameState) -> GameState:
        """Advances the turn to the next player or phase."""
        print(f"[DEBUG] _advance_turn: current_phase={state.current_phase}, current_player_index={state.current_player_index}, APs={[state.action_points[p.id] for p in state.players]}")
        # If we're in the action phase, only advance if current player's AP is 0 or less
        if state.current_phase == "ACTION_PHASE":
            current_player = state.players[state.current_player_index]
            if state.action_points[current_player.id] <= 0:
                state.current_player_index = (state.current_player_index + 1) % len(state.players)
                print(f"[DEBUG] _advance_turn: advanced to player {state.current_player_index}")
                # If we've gone through all players, check if we should end the round
                if state.current_player_index == 0:
                    # End of round - run upkeep phase
                    print(f"[DEBUG] _advance_turn: End of round detected, calling run_upkeep_phase")
                    state = self.run_upkeep_phase(state)
                else:
                    # Grant action points to the next player
                    next_player = state.players[state.current_player_index]
                    state.action_points[next_player.id] = 2
                    state.add_log(f"\n{next_player.name}'s turn.")
            # Additional check: if current player has no valid actions, auto-advance
            elif state.action_points[current_player.id] > 0:
                # Check if player has any valid actions they can take
                has_valid_actions = self._player_has_valid_actions(state, current_player)
                if not has_valid_actions:
                    state.add_log(f"{current_player.name} has no valid actions available. Auto-advancing turn.")
                    state.action_points[current_player.id] = 0  # Force turn advancement
                    return self._advance_turn(state)  # Recursively advance
            # CRITICAL FIX: If all players have 0 or less AP and round_marker is 4, force upkeep phase
            if (
                all(ap <= 0 for ap in state.action_points.values()) and
                state.round_marker == 4
            ):
                print("[DEBUG] _advance_turn: Forcing upkeep phase at end of round 4 due to all APs exhausted.")
                state = self.run_upkeep_phase(state)
        # If we're in the legislation phase, do nothing - wait for manual resolution
        elif state.current_phase == "LEGISLATION_PHASE":
            # Advance to the next player
            state.current_player_index = (state.current_player_index + 1) % len(state.players)
            state.add_log(f"Turn advances to {state.get_current_player().name}.")

            # Check if all players have passed (or acted)
            # This is a placeholder for a more robust check.
            # A better implementation would be to track if each player has voted.
            if state.current_player_index == 0:
                # This simplistic check assumes a full circle means the phase might be over.
                # In a real scenario, we'd check `state.awaiting_legislation_resolution`.
                pass
        # If we're in the election phase, do nothing - wait for manual resolution
        elif state.current_phase == "ELECTION_PHASE":
            # Do not automatically advance - wait for manual resolution
            pass
        print(f"[DEBUG] _advance_turn: end state current_player_index={state.current_player_index}, APs={[state.action_points[p.id] for p in state.players]}")
        return state

    def _player_has_valid_actions(self, state: GameState, player: Player) -> bool:
        """Check if a player has any valid actions they can take."""
        ap = state.action_points.get(player.id, 0)
        
        # Always allow pass turn (0 AP cost)
        if ap >= 0:
            return True
            
        # Check for 1 AP actions (fundraise, network, use favor, support/oppose legislation)
        if ap >= 1:
            return True
            
        # Check for 2 AP actions (sponsor legislation, campaign, declare candidacy)
        if ap >= 2:
            return True
            
        return False

    def run_upkeep_phase(self, state: GameState) -> GameState:
        """Runs the entire Upkeep Phase automatically."""
        print(f"[DEBUG] run_upkeep_phase called with round_marker={state.round_marker}")
        state.current_phase = "UPKEEP_PHASE"
        state.add_log("\n--- UPKEEP PHASE ---")

        state = resolvers.resolve_upkeep(state)

        # After upkeep, advance the round marker
        state.round_marker += 1
        print(f"[DEBUG] run_upkeep_phase: round_marker incremented to {state.round_marker}")
        
        if state.round_marker >= 5:
            # End of the term, trigger the Legislation Session Phase
            # Reset round marker to 4 for clarity during legislation session
            state.round_marker = 4
            print(f"[DEBUG] run_upkeep_phase: End of term detected, calling run_legislation_session")
            state.add_log("\n--- END OF TERM ---")
            state.add_log("Round 4 complete. Moving to legislation session.")
            return self.run_legislation_session(state)
        else:
            # Otherwise, automatically start the next round with the Event Phase
            print(f"[DEBUG] run_upkeep_phase: Starting round {state.round_marker}, calling run_event_phase")
            state.add_log(f"\n--- ROUND {state.round_marker} ---")
            state.add_log("\n--- EVENT PHASE ---")
            return self.run_event_phase(state)

    def run_legislation_session(self, state: GameState) -> GameState:
        """Triggers the legislation session where all pending legislation is resolved."""
        print(f"[DEBUG] run_legislation_session called with {len(state.term_legislation)} term legislation items")
        print(f"[DEBUG] run_legislation_session: term_legislation contents: {[leg.legislation_id for leg in state.term_legislation]}")
        state.current_phase = "LEGISLATION_PHASE"
        state.add_log("DEBUG: This is the new code! If you see this, the correct code is running.")
        state.add_log("\n--- LEGISLATION SESSION ---")
        state.add_log("All sponsored legislation from this term will now be voted on.")
        
        # Clear action points during legislation session - players vote, don't take regular actions
        for player in state.players:
            state.action_points[player.id] = 0
        
        # Move any current pending legislation to term legislation
        if state.pending_legislation and not state.pending_legislation.resolved:
            print(f"[DEBUG] Moving pending legislation to term legislation: {state.pending_legislation.legislation_id}")
            state.term_legislation.append(state.pending_legislation)
            state.pending_legislation = None
        
        print(f"[DEBUG] After moving pending legislation, term_legislation has {len(state.term_legislation)} items")
        
        # If no legislation was sponsored this term, skip to elections
        if not state.term_legislation:
            print("[DEBUG] No term legislation found, skipping to elections")
            state.add_log("No legislation was sponsored this term. Moving to elections.")
            return self.run_election_phase(state)
        
        print(f"[DEBUG] Setting awaiting_legislation_resolution flag for {len(state.term_legislation)} items")
        # Set the flag to indicate legislation resolution is needed
        state.awaiting_legislation_resolution = True
        state.add_log("\n--- LEGISLATION SESSION: Ready for Resolution ---")
        state.add_log("Click 'Resolve Legislation' to reveal all secret commitments and determine outcomes.")
        
        print(f"[DEBUG] run_legislation_session returning with phase={state.current_phase}, awaiting={state.awaiting_legislation_resolution}")
        return state

    def run_election_phase(self, state: GameState) -> GameState:
        """Triggers the election resolutions and resets for the new term."""
        print(f"[DEBUG] run_election_phase called")
        state.current_phase = "ELECTION_PHASE"
        state.add_log("\n--- ELECTION PHASE ---")
        state.add_log("Elections are ready to be resolved.")
        
        # Set the flag to indicate election resolution is needed
        state.awaiting_election_resolution = True
        state.add_log("Click 'Resolve Elections' to determine office winners and start the new term.")
        
        return state

    def run_event_phase(self, state: GameState) -> GameState:
        """Draws an event card and resolves it using the resolver module."""
        state.clear_turn_log()
        
        new_state = resolvers.resolve_event_card(state)
        
        new_state.current_phase = "ACTION_PHASE"
        new_state.current_player_index = 0  # Ensure first player can take actions
        
        # Grant action points to all players at the start of action phase
        for player in new_state.players:
            new_state.action_points[player.id] = 2
        
        return new_state

    def get_valid_actions(self, state: GameState, player_id: int) -> List[Action]:
        """
        Get all valid actions a player can take in the current game state.
        This is the single source of truth for valid actions.
        
        Args:
            state: Current game state
            player_id: ID of the player whose actions to check
            
        Returns:
            List of valid Action objects
        """
        valid_actions = []
        player = state.get_player_by_id(player_id)
        
        if not player:
            return valid_actions
            
        # Check if it's the player's turn
        if state.get_current_player().id != player_id:
            return valid_actions
            
        # Check if player has action points
        ap = state.action_points.get(player_id, 0)
        if ap <= 0:
            # Only Pass Turn is available
            valid_actions.append(ActionPassTurn(player_id=player_id))
            return valid_actions
            
        # Helper function to check if player can afford an action
        def can_afford_action(action_class_name: str) -> bool:
            base_cost = self.action_point_costs.get(action_class_name, 0)
            # Apply public gaffe effect
            if player.id in state.public_gaffe_players:
                if action_class_name in ["ActionSponsorLegislation", "ActionDeclareCandidacy"]:
                    base_cost += 1
            return ap >= base_cost
            
        # Always available actions (1 AP each)
        if can_afford_action("ActionFundraise"):
            valid_actions.append(ActionFundraise(player_id=player_id))
        if can_afford_action("ActionNetwork"):
            valid_actions.append(ActionNetwork(player_id=player_id))
        
        # Sponsor Legislation (2 AP, if player has enough PC and AP)
        if player.pc >= 5 and can_afford_action("ActionSponsorLegislation"):
            for leg_id in state.legislation_options:
                valid_actions.append(ActionSponsorLegislation(
                    player_id=player_id, 
                    legislation_id=leg_id
                ))
        
        # Declare Candidacy (2 AP, only in round 4)
        if state.round_marker == 4 and can_afford_action("ActionDeclareCandidacy"):
            for office_id in state.offices:
                office = state.offices[office_id]
                if office.candidacy_cost <= player.pc:
                    # Can declare with 0 PC commitment
                    valid_actions.append(ActionDeclareCandidacy(
                        player_id=player_id,
                        office_id=office_id,
                        committed_pc=0
                    ))
                    # Can also declare with additional PC commitment
                    if player.pc > office.candidacy_cost:
                        valid_actions.append(ActionDeclareCandidacy(
                            player_id=player_id,
                            office_id=office_id,
                            committed_pc=min(10, player.pc - office.candidacy_cost)
                        ))
        
        # Use Favor (1 AP, if player has favors)
        if player.favors and can_afford_action("ActionUseFavor"):
            for favor in player.favors:
                valid_actions.append(ActionUseFavor(
                    player_id=player_id,
                    favor_id=favor.id
                ))
        
        # Support/Oppose Legislation (1 AP each, if there's pending legislation)
        if state.pending_legislation and not state.pending_legislation.resolved:
            if can_afford_action("ActionSupportLegislation") and player.pc > 0:
                # Can support with any amount of PC
                for pc_amount in range(1, min(player.pc + 1, 21)):  # Cap at 20 PC
                    valid_actions.append(ActionSupportLegislation(
                        player_id=player_id,
                        legislation_id=state.pending_legislation.legislation_id,
                        support_amount=pc_amount
                    ))
            if can_afford_action("ActionOpposeLegislation") and player.pc > 0:
                # Can oppose with any amount of PC
                for pc_amount in range(1, min(player.pc + 1, 21)):  # Cap at 20 PC
                    valid_actions.append(ActionOpposeLegislation(
                        player_id=player_id,
                        legislation_id=state.pending_legislation.legislation_id,
                        oppose_amount=pc_amount
                    ))
        
        # Pass Turn (always available)
        valid_actions.append(ActionPassTurn(player_id=player_id))
        
        return valid_actions

    def get_valid_system_actions(self, state: GameState) -> List[Action]:
        """
        Get system-level actions that need to be performed (e.g., resolution actions).
        This handles non-player actions like legislation and election resolution.
        
        Args:
            state: Current game state
            
        Returns:
            List of valid system Action objects
        """
        system_actions = []
        
        # Check for legislation resolution
        if state.awaiting_legislation_resolution:
            system_actions.append(ActionResolveLegislation())
            
        # Check for election resolution
        if state.awaiting_election_resolution:
            system_actions.append(ActionResolveElections())
            
        # Check for results acknowledgement
        if state.awaiting_results_acknowledgement:
            system_actions.append(ActionAcknowledgeResults())
            
        return system_actions

    def is_game_over(self, state: GameState) -> bool:
        """Checks if the game has ended (after 3 terms)."""
        # The game ends after the election phase of the 3rd term.
        # We track terms completed in state.term_counter
        return state.term_counter >= 3

    def get_final_scores(self, state: GameState) -> dict:
        """Calculates and returns the final scores and the winner."""
        final_scores = calculate_final_scores(state)
        
        winner_id = -1
        max_score = -1
        for player_id, score_data in final_scores.items():
            if score_data['total_influence'] > max_score:
                max_score = score_data['total_influence']
                winner_id = player_id
        
        winner_player = state.get_player_by_id(winner_id)
        winner_name = winner_player.name if winner_player else "None"

        return {
            "scores": final_scores,
            "winner_id": winner_id,
            "winner_name": winner_name
        }

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
        state.current_player_index = 0  # Reset for new term
        state.awaiting_legislation_resolution = False
        state.awaiting_election_resolution = True
        
        # Transition to election phase
        return self.run_election_phase(state)

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
                                # PC was already deducted when commitment was made
                                legislation.support_players[player_id] = amount
                            else:  # oppose
                                state.add_log(f"🎭 REVEAL: {player.name} secretly opposed with {amount} PC!")
                                # PC was already deducted when commitment was made
                                legislation.oppose_players[player_id] = amount
                else:
                    state.add_log(f"No secret commitments found for {legislation_id}")
                
                # Now resolve the legislation using the existing system
                state.pending_legislation = legislation
                state = resolvers.resolve_pending_legislation(state)
        
        # Clear term legislation and move to elections
        state.term_legislation.clear()
        state.current_player_index = 0  # Reset for new term
        state.awaiting_legislation_resolution = False
        state.awaiting_election_resolution = True
        
        # Transition to election phase
        return self.run_election_phase(state)

    def resolve_elections_session(self, state: GameState, disable_dice_roll: bool = False) -> GameState:
        """Resolves elections and transitions to the next term."""
        if not state.awaiting_election_resolution:
            return state

        print("[DEBUG] run_election_phase called")
        state.current_phase = "ELECTION_PHASE"
        state.add_log("\n--- ELECTION PHASE ---")
        
        state = resolvers.resolve_elections(state, disable_dice_roll=disable_dice_roll)
        
        # Instead of advancing to the next term, set a flag
        state.awaiting_election_resolution = False
        state.awaiting_results_acknowledgement = True
        state.add_log("Elections resolved. Awaiting acknowledgement.")
        
        return state

    def start_next_term(self, state: GameState) -> GameState:
        """Clears the board and starts the next term."""
        # Increment term counter
        state.term_counter += 1
        
        # Reset term-specific state
        state.term_legislation.clear()
        state.secret_candidacies.clear()
        state.current_player_index = 0
        
        # Clear resolution flags
        state.awaiting_legislation_resolution = False
        state.awaiting_election_resolution = False
        state.awaiting_results_acknowledgement = False
        
        # Reset action points for all players
        for p in state.players:
            state.action_points[p.id] = 2
            
        # Start with a new event phase
        state = self.run_event_phase(state)
        
        state.add_log("\n--- NEW TERM BEGINS ---")
        return state