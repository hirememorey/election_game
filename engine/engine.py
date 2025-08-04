import random
from models.game_state import GameState
from models.components import Player, Candidacy
from models.cards import Deck, PoliticalArchetype, PersonalMandate
from engine import resolvers
from engine.actions import Action
from engine.scoring import calculate_final_scores
from typing import List, Dict, Any
from copy import deepcopy
from engine.actions import (
    ActionFundraise, ActionNetwork, ActionSponsorLegislation, ActionDeclareCandidacy, 
    ActionUseFavor, ActionSupportLegislation, ActionOpposeLegislation, ActionPassTurn, 
    ActionResolveLegislation, ActionResolveElections, ActionAcknowledgeResults,
    ActionInitiateSupportLegislation, ActionSubmitLegislationChoice, ActionSubmitAmount,
    ActionInitiateSponsorLegislation, ActionInitiateOpposeLegislation,
    ActionInitiateDeclareCandidacy, ActionSubmitOfficeChoice,
    ACTION_CLASSES
)

class GameEngine:
    """The central rule enforcement and state-management authority for the game."""

    ACTION_CLASSES = ACTION_CLASSES
    
    def __init__(self, game_data: Dict[str, Any]):
        self.game_data = game_data
        self.action_point_costs = {
            "ActionFundraise": 1,
            "ActionNetwork": 1,
            "ActionSponsorLegislation": 2,
            "ActionDeclareCandidacy": 2,
            "ActionUseFavor": 1,
            "ActionSupportLegislation": 1,
            "ActionOpposeLegislation": 1,
            "ActionPassTurn": 0,
        }
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
            "ActionInitiateSupportLegislation": resolvers.resolve_initiate_support_legislation,
            "ActionInitiateOpposeLegislation": resolvers.resolve_initiate_oppose_legislation,
            "ActionInitiateSponsorLegislation": resolvers.resolve_initiate_sponsor_legislation,
            "ActionInitiateDeclareCandidacy": resolvers.resolve_initiate_declare_candidacy,
            "ActionSubmitLegislationChoice": resolvers.resolve_submit_legislation_choice,
            "ActionSubmitOfficeChoice": resolvers.resolve_submit_office_choice,
            "ActionSubmitAmount": resolvers.resolve_submit_amount,
            "AcknowledgeAITurn": resolvers.resolve_acknowledge_ai_turn,
        }

    def start_new_game(self, player_names: list[str]) -> GameState:
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

        for p in state.players:
            state.action_points[p.id] = 2

        for p in state.players:
            if p.archetype.id == "INSIDER":
                p.pc = 15
                p.current_office = state.offices["STATE_SENATOR"]
                state.add_log(f"{p.name} starts as The Insider, holding the State Senator office with 15 PC.")
        
        return state

    def process_action(self, state: GameState, action: Action) -> GameState:
        new_state = deepcopy(state)
        
        resolver = self.action_resolvers.get(type(action).__name__)
        
        if resolver:
            try:
                new_state = resolver(new_state, action)
            except Exception as e:
                error_msg = f"Error processing action '{type(action).__name__}': {e}"
                print(error_msg)
                new_state.add_log(error_msg)
                return new_state
        else:
            error_msg = f"No resolver found for action: {type(action).__name__}"
            print(error_msg)
            new_state.add_log(error_msg)
            return new_state

        if new_state.next_action_to_process:
            follow_up_action = new_state.next_action_to_process
            new_state.next_action_to_process = None
            new_state = self.process_action(new_state, follow_up_action)
            
        return new_state

    def get_valid_actions(self, state: GameState, player_id: int) -> List[Action]:
        valid_actions = []
        player = state.get_player_by_id(player_id)
        
        if not player:
            return valid_actions
            
        if state.get_current_player().id != player_id:
            return valid_actions
            
        ap = player.action_points
        if ap <= 0:
            pass
            
        def can_afford_action(action_class_name: str) -> bool:
            base_cost = self.action_point_costs.get(action_class_name, 0)
            if player.id in state.public_gaffe_players:
                if action_class_name in ["ActionSponsorLegislation", "ActionDeclareCandidacy"]:
                    base_cost += 1
            return ap >= base_cost
            
        is_ai = not player.name == "Human"

        if can_afford_action("ActionFundraise"):
            valid_actions.append(ActionFundraise(player_id=player_id))
        if can_afford_action("ActionNetwork"):
            valid_actions.append(ActionNetwork(player_id=player_id))
        
        if can_afford_action("ActionSponsorLegislation"):
            if is_ai:
                for leg_id, leg in state.legislation_options.items():
                    if player.pc >= leg.cost and leg_id not in [l.legislation_id for l in state.term_legislation]:
                        valid_actions.append(ActionSponsorLegislation(player_id=player_id, legislation_id=leg_id))
            else:
                can_sponsor_any = any(player.pc >= leg.cost and leg_id not in [l.legislation_id for l in state.term_legislation] for leg_id, leg in state.legislation_options.items())
                if can_sponsor_any:
                    valid_actions.append(ActionInitiateSponsorLegislation(player_id=player_id))

        if state.round_marker == 4 and can_afford_action("ActionDeclareCandidacy"):
            if is_ai:
                for office_id in state.offices:
                    office = state.offices[office_id]
                    if office.candidacy_cost <= player.pc:
                        valid_actions.append(ActionDeclareCandidacy(
                            player_id=player_id,
                            office_id=office_id,
                            committed_pc=0
                        ))
                        if player.pc > office.candidacy_cost:
                            valid_actions.append(ActionDeclareCandidacy(
                                player_id=player_id,
                                office_id=office_id,
                                committed_pc=min(10, player.pc - office.candidacy_cost)
                            ))
            else:
                can_run_for_any_office = any(player.pc >= office.candidacy_cost for office in state.offices.values())
                if can_run_for_any_office:
                    valid_actions.append(ActionInitiateDeclareCandidacy(player_id=player_id))

        if player.favors and can_afford_action("ActionUseFavor"):
            for favor in player.favors:
                valid_actions.append(ActionUseFavor(
                    player_id=player_id,
                    favor_id=favor.id
                ))
        
        active_legislation = [leg for leg in state.term_legislation if not leg.resolved]
        if active_legislation and player.pc > 0:
            if can_afford_action("ActionSupportLegislation"):
                if is_ai:
                    for leg in active_legislation:
                        for amount in [1, 5, 10]:
                            if player.pc >= amount:
                                valid_actions.append(ActionSupportLegislation(player_id=player_id, legislation_id=leg.legislation_id, support_amount=amount))
                else:
                    valid_actions.append(ActionInitiateSupportLegislation(player_id=player_id))
            if can_afford_action("ActionOpposeLegislation"):
                if is_ai:
                    for leg in active_legislation:
                        for amount in [1, 5, 10]:
                            if player.pc >= amount:
                                valid_actions.append(ActionOpposeLegislation(player_id=player_id, legislation_id=leg.legislation_id, oppose_amount=amount))
                else:
                    valid_actions.append(ActionInitiateOpposeLegislation(player_id=player_id))
        
        valid_actions.append(ActionPassTurn(player_id=player_id))
        
        return valid_actions

    def get_valid_system_actions(self, state: GameState) -> List[Action]:
        system_actions = []
        
        if state.awaiting_legislation_resolution:
            system_actions.append(ActionResolveLegislation())
            
        if state.awaiting_election_resolution:
            system_actions.append(ActionResolveElections())
            
        if state.awaiting_results_acknowledgement:
            system_actions.append(ActionAcknowledgeResults())
            
        return system_actions

    def is_game_over(self, state: GameState) -> bool:
        return state.term_counter >= 3

    def action_from_dict(self, data: dict) -> Action:
        action_type_name = data.pop('action_type', None)
        if not action_type_name:
            raise ValueError("Action data must include 'action_type'")

        action_class = ACTION_CLASSES.get(action_type_name)
        if not action_class:
            raise ValueError(f"Unknown action type: {action_type_name}")

        return action_class(**data)

    def get_final_scores(self, state: GameState) -> dict:
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
        if not state.awaiting_legislation_resolution:
            state.add_log("No legislation session to resolve.")
            return state
        state.add_log("\n--- LEGISLATION SESSION: Resolving All Bills ---")
        for legislation in state.term_legislation:
            if not legislation.resolved:
                state = resolvers._resolve_single_legislation(state, legislation)
        state.term_legislation.clear()
        state.current_player_index = 0
        state.awaiting_legislation_resolution = False
        state.awaiting_election_resolution = True
        
        return self.resolve_elections_session(state)

    def resolve_legislation_session_with_secrets(self, state: GameState, secret_commitments: dict) -> GameState:
        if not state.awaiting_legislation_resolution:
            state.add_log("No legislation session to resolve.")
            return state
        
        state.add_log("\n--- LEGISLATION SESSION: Secret Commitment Reveal ---")
        state.add_log("All secret commitments will now be revealed!")
        
        for legislation in state.term_legislation:
            if not legislation.resolved:
                legislation_id = legislation.legislation_id
                state.add_log(f"\n--- Revealing commitments for {legislation_id} ---")
                
                if legislation_id in secret_commitments:
                    commitments = secret_commitments[legislation_id]
                    
                    for player_id, stance, amount in commitments:
                        player = state.get_player_by_id(player_id)
                        if player:
                            if stance == 'support':
                                state.add_log(f"🎭 REVEAL: {player.name} secretly supported with {amount} PC!")
                                legislation.support_players[player_id] = amount
                            else:
                                state.add_log(f"🎭 REVEAL: {player.name} secretly opposed with {amount} PC!")
                                legislation.oppose_players[player_id] = amount
                else:
                    state.add_log(f"No secret commitments found for {legislation_id}")
                
                state = resolvers._resolve_single_legislation(state, legislation)
        
        state.term_legislation.clear()
        state.current_player_index = 0
        state.awaiting_legislation_resolution = False
        state.awaiting_election_resolution = True
        
        return self.resolve_elections_session(state)

    def resolve_elections_session(self, state: GameState, disable_dice_roll: bool = False) -> GameState:
        if not state.awaiting_election_resolution:
            return state

        print("[DEBUG] run_election_phase called")
        state.current_phase = "ELECTION_PHASE"
        state.add_log("\n--- ELECTION PHASE ---")
        
        state = resolvers.resolve_elections(state, disable_dice_roll=disable_dice_roll)
        
        state.awaiting_election_resolution = False
        state.awaiting_results_acknowledgement = True
        state.add_log("Elections resolved. Awaiting acknowledgement.")
        
        return state

    def start_next_term(self, state: GameState) -> GameState:
        state.term_counter += 1
        
        state.term_legislation.clear()
        state.secret_candidacies.clear()
        state.current_player_index = 0
        
        state.awaiting_legislation_resolution = False
        state.awaiting_election_resolution = False
        state.awaiting_results_acknowledgement = False
        
        for p in state.players:
            p.action_points = 2
            
        # Run event phase using resolvers
        state = resolvers.resolve_event_card(state)
        
        state.add_log("\n--- NEW TERM BEGINS ---")
        state.round_marker = 1
        return state