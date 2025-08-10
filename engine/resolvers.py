"""
This file contains the core logic resolvers for the game engine.
It is responsible for implementing the specific rules of actions, events,
and game phases.
"""
import random
from copy import deepcopy
from models.game_state import GameState, PendingLegislation, TradeOffer
from models.cards import AllianceCard, EventCard, ScrutinyCard
from models.components import Player, Office, Legislation, PoliticalFavor, Candidacy, Pledge
from engine.actions import (
    Action, ActionFundraise, ActionNetwork,
    ActionSponsorLegislation, ActionDeclareCandidacy, ActionUseFavor,
    ActionSupportLegislation, ActionOpposeLegislation,
    ActionInitiateSupportLegislation, ActionSubmitLegislationChoice, ActionSubmitAmount,
    ActionProposeTrade, ActionAcceptTrade, ActionDeclineTrade, ActionCompleteTrading, ActionPassTurn,
    ActionInitiateUseFavor, ActionSubmitTarget
)
import json

#--- Action Resolvers ---

def resolve_initiate_support_legislation(state: GameState, action: ActionInitiateSupportLegislation) -> GameState:
    """Sets up the game state to ask the player which legislation to support."""
    player = state.get_player_by_id(action.player_id)
    if not player:
        return state

    options = []
    active_legislation = [leg for leg in state.term_legislation if not leg.resolved]
    for leg in active_legislation:
        leg_details = state.legislation_options[leg.legislation_id]
        options.append({
            "id": leg.legislation_id,
            "display_name": f"{leg_details.title}"
        })

    if not options:
        state.add_log("There is no active legislation to support right now.")
        return state

    state.pending_ui_action = {
        "original_action_type": "ActionInitiateSupportLegislation", # Add this line
        "action_type": "ActionInitiateSupportLegislation",
        "player_id": action.player_id,
        "prompt": "Which bill would you like to secretly support?",
        "options": options,
        "next_action": "ActionSubmitLegislationChoice",
    }
    return state

def resolve_initiate_oppose_legislation(state: GameState, action: Action) -> GameState:
    """Sets up the game state to ask the player which legislation to oppose."""
    player = state.get_player_by_id(action.player_id)
    if not player:
        return state

    options = []
    active_legislation = [leg for leg in state.term_legislation if not leg.resolved]
    for leg in active_legislation:
        leg_details = state.legislation_options[leg.legislation_id]
        options.append({
            "id": leg.legislation_id,
            "display_name": f"{leg_details.title}"
        })

    if not options:
        state.add_log("There is no active legislation to oppose right now.")
        return state

    state.pending_ui_action = {
        "original_action_type": "ActionInitiateOpposeLegislation", # Add this line
        "action_type": "ActionInitiateOpposeLegislation",
        "player_id": action.player_id,
        "prompt": "Which bill would you like to secretly oppose?",
        "options": options,
        "next_action": "ActionSubmitLegislationChoice",
    }
    return state

def resolve_initiate_sponsor_legislation(state: GameState, action: Action) -> GameState:
    """Sets up the game state to ask the player which legislation to sponsor."""
    player = state.get_player_by_id(action.player_id)
    if not player:
        return state

    options = []
    for leg_id, leg_details in state.legislation_options.items():
        is_already_sponsored = any(l.legislation_id == leg_id for l in state.term_legislation)
        if player.pc >= leg_details.cost and not is_already_sponsored:
            options.append({
                "id": leg_id,
                "display_name": f"{leg_details.title} (Cost: {leg_details.cost} PC)",
                "cost": leg_details.cost
            })

    if not options:
        state.add_log("There are no bills you can afford to sponsor right now.")
        return state

    state.pending_ui_action = {
        "original_action_type": "ActionInitiateSponsorLegislation",
        "action_type": "ActionInitiateSponsorLegislation",
        "player_id": action.player_id,
        "prompt": "Which bill would you like to sponsor?",
        "options": options,
        "next_action": "ActionSubmitLegislationChoice",
    }
    return state


def resolve_submit_legislation_choice(state: GameState, action: ActionSubmitLegislationChoice) -> GameState:
    """Updates the pending action state with the chosen legislation and asks for an amount."""
    player = state.get_player_by_id(action.player_id)
    if not player or not state.pending_ui_action:
        return state

    # Determine the context (support or oppose) from the original pending action
    original_action_type = state.pending_ui_action.get("action_type")
    
    if original_action_type == "ActionInitiateSupportLegislation":
        prompt = f"How much Political Capital (PC) will you secretly commit to support the {action.choice}? (1-{player.pc})"
    elif original_action_type == "ActionInitiateOpposeLegislation":
        prompt = f"How much Political Capital (PC) will you secretly commit to oppose the {action.choice}? (1-{player.pc})"
    elif original_action_type == "ActionInitiateSponsorLegislation":
        # No amount needed for sponsoring, create the concrete action immediately
        
        # Find the cost from the original options
        chosen_option = next((opt for opt in state.pending_ui_action['options'] if opt['id'] == action.choice), None)
        if not chosen_option:
            state.add_log("Invalid legislation choice.")
            state.pending_ui_action = None
            return state

        concrete_action = ActionSponsorLegislation(
            player_id=action.player_id,
            legislation_id=action.choice
        )
        state.pending_ui_action = None
        state.next_action_to_process = concrete_action
        return state
    else:
        # Fallback or error
        prompt = f"How much PC will you commit? (1-{player.pc})"

    # Update the pending action to ask for an amount
    state.pending_ui_action.update({
        "action_type": "ActionSubmitLegislationChoice", # Mark that we've processed this step
        "selected_legislation": action.choice,
        "prompt": prompt,
        "options": [], # No more choices, expecting free-form input
        "next_action": "ActionSubmitAmount",
        "expects_input": "amount", # This tells the frontend to show an amount input
        "min_amount": 1,
        "max_amount": player.pc,
        # Preserve the original action type for the final step
        "original_action_type": original_action_type 
    })
    return state

def resolve_submit_amount(state: GameState, action: ActionSubmitAmount) -> GameState:
    """Finalizes the UI action, creates a concrete action, and clears the pending state."""
    player = state.get_player_by_id(action.player_id)
    if not player or not state.pending_ui_action:
        return state
        
    pending_action_data = state.pending_ui_action
    amount = action.amount
    
    # Validate the amount
    if not isinstance(amount, int) or not (pending_action_data.get('min_amount', 1) <= amount <= pending_action_data.get('max_amount', player.pc)):
        state.pending_ui_action['prompt'] = f"Invalid amount. How much PC? ({pending_action_data.get('min_amount', 1)}-{pending_action_data.get('max_amount', player.pc)})"
        return state

    # Create the concrete action based on the original context.
    legislation_id = pending_action_data.get("selected_legislation")
    office_id = pending_action_data.get("selected_office")
    original_action_type = pending_action_data.get("original_action_type")

    concrete_action = None
    if original_action_type == "ActionInitiateSupportLegislation":
        concrete_action = ActionSupportLegislation(
            player_id=action.player_id,
            legislation_id=legislation_id,
            support_amount=amount
        )
    elif original_action_type == "ActionInitiateOpposeLegislation":
        concrete_action = ActionOpposeLegislation(
            player_id=action.player_id,
            legislation_id=legislation_id,
            oppose_amount=amount
        )
    elif original_action_type == "ActionInitiateDeclareCandidacy":
        # For declare candidacy, the amount is additional commitment beyond base cost
        base_cost = pending_action_data.get("base_cost", 0)
        total_committed = base_cost + amount
        concrete_action = ActionDeclareCandidacy(
            player_id=action.player_id,
            office_id=office_id,
            committed_pc=total_committed
        )

    # Clear the pending UI action and set the next concrete action to be processed.
    state.pending_ui_action = None
    state.next_action_to_process = concrete_action
        
    return state

def resolve_initiate_declare_candidacy(state: GameState, action: Action) -> GameState:
    """Sets up the game state to ask the player which office to run for."""
    player = state.get_player_by_id(action.player_id)
    if not player:
        return state

    options = []
    for office_id, office_details in state.offices.items():
        if player.pc >= office_details.candidacy_cost:
            options.append({
                "id": office_id,
                "display_name": f"{office_details.title} (Cost: {office_details.candidacy_cost} PC)",
                "cost": office_details.candidacy_cost
            })

    if not options:
        state.add_log("You cannot afford to run for any office right now.")
        return state

    state.pending_ui_action = {
        "original_action_type": "ActionInitiateDeclareCandidacy",
        "action_type": "ActionInitiateDeclareCandidacy",
        "player_id": action.player_id,
        "prompt": "Which office would you like to run for?",
        "options": options,
        "next_action": "ActionSubmitOfficeChoice",
    }
    return state

def resolve_submit_office_choice(state: GameState, action: 'ActionSubmitOfficeChoice') -> GameState:
    """Updates the pending action state with the chosen office and asks for additional commitment amount."""
    player = state.get_player_by_id(action.player_id)
    if not player or not state.pending_ui_action:
        return state

    office_id = action.choice
    office = state.offices.get(office_id)
    if not office:
        state.add_log("Invalid office choice.")
        state.pending_ui_action = None
        return state

    # Calculate how much additional PC the player can commit beyond the base cost
    base_cost = office.candidacy_cost
    max_additional = player.pc - base_cost  # How much extra they can commit
    
    if max_additional < 0:
        state.add_log("You cannot afford the base cost to run for this office.")
        state.pending_ui_action = None
        return state

    # Update the pending action to ask for additional commitment amount
    state.pending_ui_action.update({
        "action_type": "ActionSubmitOfficeChoice",  # Mark that we've processed this step
        "selected_office": office_id,
        "prompt": f"How much additional Political Capital (PC) will you commit to your campaign for {office.title}? (0-{max_additional})",
        "options": [],  # No more choices, expecting free-form input
        "next_action": "ActionSubmitAmount",
        "expects_input": "amount",  # This tells the frontend to show an amount input
        "min_amount": 0,
        "max_amount": max_additional,
        "base_cost": base_cost,
        # Preserve the original action type for the final step
        "original_action_type": "ActionInitiateDeclareCandidacy"
    })
    return state


def apply_public_mood_effect(state: GameState, mood_change: int, pc_bonus: int = 5):
    """
    Apply public mood change with incumbent/outsider logic.
    
    Args:
        state: Current game state
        mood_change: How much to change public mood (+ or -)
        pc_bonus: Base PC amount for the effect (default 5)
    """
    # Prevent public mood changes if war is active
    if "WAR_BREAKS_OUT" in state.active_effects:
        state.add_log("Public Mood is locked due to War. No change occurs.")
        mood_change = 0
    
    # Apply mood change
    if mood_change > 0:
        state.public_mood = min(3, state.public_mood + mood_change)
    else:
        state.public_mood = max(-3, state.public_mood + mood_change)
    
    # Apply PC effects based on incumbent status
    for player in state.players:
        if player.is_incumbent:
            # Incumbents benefit from positive mood, suffer from negative
            if mood_change > 0:
                player.pc += pc_bonus
                state.add_log(f"{player.name} (incumbent) gains {pc_bonus} PC from improved public mood.")
            else:
                player.pc -= pc_bonus
                state.add_log(f"{player.name} (incumbent) loses {pc_bonus} PC from worsened public mood.")
        else:
            # Outsiders suffer from positive mood, benefit from negative
            if mood_change > 0:
                player.pc -= pc_bonus
                state.add_log(f"{player.name} (outsider) loses {pc_bonus} PC from improved public mood.")
            else:
                player.pc += pc_bonus
                state.add_log(f"{player.name} (outsider) gains {pc_bonus} PC from worsened public mood.")
    
    return state

def resolve_fundraise(state: GameState, action: ActionFundraise) -> GameState:
    """The player gains 5 PC."""
    player = state.get_player_by_id(action.player_id)
    if not player:
        return state

    # Deduct AP cost
    state.action_points[player.id] -= 1

    pc_gain = 5

    # Apply the Fundraiser archetype bonus only once
    if player.archetype.id == "FUNDRAISER" and not player.fundraiser_bonus_used:
        pc_gain += 2
        player.fundraiser_bonus_used = True
        state.add_log(f"Archetype bonus: +2 PC for The Fundraiser (one-time).")

    player.pc += pc_gain
    state.add_log(f"{player.name} takes the Fundraise action and gains {pc_gain} PC.")
    return state

def resolve_network(state: GameState, action: ActionNetwork) -> GameState:
    player = state.get_player_by_id(action.player_id)
    if not player: return state
    
    # Deduct AP cost
    state.action_points[player.id] -= 1

    player.pc += 2
    if state.favor_supply:
        favor = state.favor_supply.pop(random.randrange(len(state.favor_supply)))
        
        # Check if this is a negative favor that should be applied immediately
        negative_favor_ids = ["POLITICAL_DEBT", "PUBLIC_GAFFE", "MEDIA_SCRUTINY", "COMPROMISING_POSITION", "POLITICAL_HOT_POTATO"]
        
        if favor.id in negative_favor_ids:
            # Apply negative favor effect immediately
            if favor.id == "POLITICAL_DEBT":
                # For political debt, randomly choose another player as creditor
                other_players = [p for p in state.players if p.id != player.id]
                if other_players:
                    creditor = random.choice(other_players)
                    state.political_debts[player.id] = creditor.id
                    state.add_log(f"{player.name} networks, gaining 2 PC but incurs a political debt to {creditor.name}.")
                else:
                    state.add_log(f"{player.name} networks, gaining 2 PC but incurs a political debt (no other players available).")
            
            elif favor.id == "PUBLIC_GAFFE":
                state.public_gaffe_players.add(player.id)
                state.add_log(f"{player.name} networks, gaining 2 PC but makes a public gaffe. Their next public action will cost +1 AP.")
            
            elif favor.id == "MEDIA_SCRUTINY":
                state.media_scrutiny_players.add(player.id)
                state.add_log(f"{player.name} networks, gaining 2 PC but comes under media scrutiny. All PC gained from Fundraise actions this round will be halved.")
            
            elif favor.id == "COMPROMISING_POSITION":
                # Automatically reveal archetype since player wouldn't choose this
                state.compromised_players.add(player.id)
                state.add_log(f"{player.name} networks, gaining 2 PC but is caught in a compromising position. Their archetype is revealed to all players.")
            
            elif favor.id == "POLITICAL_HOT_POTATO":
                # Pass to a random other player
                other_players = [p for p in state.players if p.id != player.id]
                if other_players:
                    target = random.choice(other_players)
                    state.hot_potato_holder = target.id
                    state.add_log(f"{player.name} networks, gaining 2 PC but receives a politically toxic dossier, which they pass to {target.name}.")
                else:
                    state.add_log(f"{player.name} networks, gaining 2 PC but receives a politically toxic dossier (no other players available).")
        else:
            # Positive favor - add to player's hand for later use
            player.favors.append(favor)
            state.add_log(f"{player.name} networks, gaining 2 PC and a Political Favor: '{favor.description}'")
    else:
        state.add_log(f"{player.name} networks, gaining 2 PC, but the favor supply is empty.")
    return state

def resolve_initiate_use_favor(state: GameState, action: ActionInitiateUseFavor) -> GameState:
    """Sets up a prompt for targeted favors, letting the human choose a target player."""
    player = state.get_player_by_id(action.player_id)
    if not player:
        return state

    # Determine if the favor requires a target
    targeted_favor_ids = {"POLITICAL_PRESSURE", "POLITICAL_DEBT", "POLITICAL_HOT_POTATO"}
    if action.favor_id not in targeted_favor_ids:
        # If not targeted, immediately schedule concrete use favor
        state.pending_ui_action = None
        state.next_action_to_process = ActionUseFavor(
            player_id=action.player_id,
            favor_id=action.favor_id
        )
        return state

    # Build list of valid targets (exclude self)
    options = []
    for p in state.players:
        if p.id != player.id:
            options.append({
                "id": p.id,
                "display_name": p.name
            })

    if not options:
        state.add_log("There are no valid targets for this favor right now.")
        return state

    # If only one option, auto-advance by scheduling submit target
    if len(options) == 1:
        only_id = options[0]["id"]
        state.pending_ui_action = None
        state.next_action_to_process = ActionSubmitTarget(
            player_id=action.player_id,
            choice=only_id
        )
        # Stash the favor details temporarily on state to complete later step
        # Use the existing pending_ui_action pattern to carry context
        state.pending_ui_action = {
            "original_action_type": "ActionInitiateUseFavor",
            "action_type": "ActionInitiateUseFavor",
            "player_id": action.player_id,
            "favor_id": action.favor_id,
        }
        return state

    # Prompt selection
    state.pending_ui_action = {
        "original_action_type": "ActionInitiateUseFavor",
        "action_type": "ActionInitiateUseFavor",
        "player_id": action.player_id,
        "favor_id": action.favor_id,
        "prompt": "Choose a player to target.",
        "options": options,
        "next_action": "ActionSubmitTarget",
    }
    return state

def resolve_submit_target(state: GameState, action: ActionSubmitTarget) -> GameState:
    """Consumes the target selection and schedules a concrete ActionUseFavor."""
    player = state.get_player_by_id(action.player_id)
    if not player or not state.pending_ui_action:
        return state

    if state.pending_ui_action.get("original_action_type") != "ActionInitiateUseFavor":
        return state

    favor_id = state.pending_ui_action.get("favor_id")
    target_id = action.choice

    # Validate target
    target = state.get_player_by_id(target_id)
    if not target or target.id == player.id:
        state.add_log("Invalid target selection.")
        # Keep prompt active for re-selection
        return state

    # Clear prompt and schedule concrete action
    state.pending_ui_action = None
    state.next_action_to_process = ActionUseFavor(
        player_id=action.player_id,
        favor_id=favor_id,
        target_player_id=target_id
    )
    return state

def resolve_use_favor(state: GameState, action: ActionUseFavor) -> GameState:
    player = state.get_player_by_id(action.player_id)
    if not player: return state

    # Find the favor in player's hand first; don't deduct AP/remove favor until inputs validated
    favor = None
    favor_index = -1
    for i, f in enumerate(player.favors):
        if f.id == action.favor_id:
            favor = f
            favor_index = i
            break
    
    if not favor:
        state.add_log(f"{player.name} doesn't have that favor.")
        return state

    # For targeted favors, ensure a valid target is specified before consuming AP/favor
    if favor.id in {"POLITICAL_PRESSURE", "POLITICAL_DEBT", "POLITICAL_HOT_POTATO"}:
        target = state.get_player_by_id(action.target_player_id)
        if not target or target == player:
            state.add_log(f"{player.name} tries to use '{favor.description}' but no valid target was specified.")
            return state

    # Deduct AP and remove favor now that all inputs are valid
    state.action_points[player.id] -= 1
    player.favors.pop(favor_index)
    
    # Apply favor effect based on favor type
    if favor.id == "EXTRA_FUNDRAISING":
        pc_gain = 8
        player.pc += pc_gain
        state.add_log(f"{player.name} uses '{favor.description}' and gains {pc_gain} PC.")
    
    elif favor.id == "LEGISLATIVE_INFLUENCE":
        active_legislation = [leg for leg in state.term_legislation if not leg.resolved]
        if active_legislation:
            # Add support to the first active legislation
            target_legislation = active_legislation[0]
            current_support = target_legislation.support_players.get(player.id, 0)
            target_legislation.support_players[player.id] = current_support + 5
            bill = state.legislation_options[target_legislation.legislation_id]
            state.add_log(f"{player.name} uses '{favor.description}' to add 5 PC support to {bill.title}.")
        else:
            state.add_log(f"{player.name} uses '{favor.description}' but there's no active legislation.")
    
    elif favor.id == "MEDIA_SPIN":
        # Improve public mood with incumbent/outsider logic
        apply_public_mood_effect(state, mood_change=1, pc_bonus=3)
        state.add_log(f"{player.name} uses '{favor.description}' to improve public mood.")
    
    elif favor.id == "POLITICAL_PRESSURE":
        if action.target_player_id >= 0:
            target = state.get_player_by_id(action.target_player_id)
            if target and target != player:
                target.pc -= 3
                state.add_log(f"{player.name} uses '{favor.description}' to pressure {target.name}, who loses 3 PC.")
            else:
                state.add_log(f"{player.name} uses '{favor.description}' but the target is invalid.")
        else:
            state.add_log(f"{player.name} uses '{favor.description}' but no target was specified.")
    
    elif favor.id == "PEEK_EVENT":
        # Peek at the top card of the Event Deck
        if state.event_deck.cards:
            top_card = state.event_deck.cards[-1]
            state.add_log(f"Peeked at the top Event Card: '{top_card.title}' - {top_card.description}")
        else:
            state.add_log(f"{player.name} uses '{favor.description}' but the Event Deck is empty.")
        player.pc += 5  # Optionally, still give 5 PC as a bonus
        state.add_log(f"{player.name} gains 5 PC.")
    
    # Negative favor effects
    elif favor.id == "POLITICAL_DEBT":
        if action.target_player_id >= 0:
            creditor = state.get_player_by_id(action.target_player_id)
            if creditor and creditor != player:
                state.political_debts[player.id] = creditor.id
                state.add_log(f"{player.name} owes a political debt to {creditor.name}. {creditor.name} can force {player.name} to abstain or vote with them on future legislation.")
            else:
                state.add_log(f"{player.name} uses '{favor.description}' but the target is invalid.")
        else:
            state.add_log(f"{player.name} uses '{favor.description}' but no target was specified.")
    
    elif favor.id == "PUBLIC_GAFFE":
        state.public_gaffe_players.add(player.id)
        state.add_log(f"{player.name} has made a public gaffe. Their next public action (Sponsor Legislation, Declare Candidacy, or Campaign) will cost +1 AP.")
    
    elif favor.id == "MEDIA_SCRUTINY":
        state.media_scrutiny_players.add(player.id)
        state.add_log(f"{player.name} is under media scrutiny. All PC gained from Fundraise actions this round will be halved.")
    
    elif favor.id == "COMPROMISING_POSITION":
        if action.choice == "discard_favors":
            # Discard two favors
            if len(player.favors) >= 2:
                discarded = player.favors[:2]
                player.favors = player.favors[2:]
                state.add_log(f"{player.name} discards two Political Favors to avoid revealing their archetype.")
            else:
                state.add_log(f"{player.name} doesn't have enough favors to discard. Their archetype is revealed to all players.")
                state.compromised_players.add(player.id)
        elif action.choice == "reveal_archetype":
            state.compromised_players.add(player.id)
            state.add_log(f"{player.name} reveals their archetype to all players.")
        else:
            state.add_log(f"{player.name} uses '{favor.description}' but no choice was specified.")
    
    elif favor.id == "POLITICAL_HOT_POTATO":
        if action.target_player_id >= 0:
            target = state.get_player_by_id(action.target_player_id)
            if target and target != player:
                state.hot_potato_holder = target.id
                state.add_log(f"{player.name} passes the politically toxic dossier to {target.name}. Whoever holds it when the next Upkeep Phase begins will lose 5 Influence.")
            else:
                state.add_log(f"{player.name} uses '{favor.description}' but the target is invalid.")
        else:
            state.add_log(f"{player.name} uses '{favor.description}' but no target was specified.")
    
    else:
        # Generic favor effect
        player.pc += 5
        state.add_log(f"{player.name} uses '{favor.description}' and gains 5 PC.")
    
    return state

def resolve_sponsor_legislation(state: GameState, action: ActionSponsorLegislation) -> GameState:
    player = state.get_player_by_id(action.player_id)
    if not player: return state

    bill = state.legislation_options[action.legislation_id]
    if player.pc < bill.cost:
        state.add_log(f"Not enough PC to sponsor {bill.title}.")
        return state
    
    player.pc -= bill.cost
    state.action_points[player.id] -= 2 # Deduct the AP cost for the action
    state.add_log(f"{player.name} sponsors the {bill.title} for {bill.cost} PC.")
    state.add_log(f"This legislation will be voted on during the end-of-term legislation session.")
    
    # Create pending legislation for other players to respond to during the term
    # MODIFIED: Add to term_legislation list directly
    state.term_legislation.append(PendingLegislation(
        legislation_id=action.legislation_id,
        sponsor_id=player.id
    ))
    
    return state

def resolve_support_legislation(state: GameState, action: ActionSupportLegislation) -> GameState:
    player = state.get_player_by_id(action.player_id)
    if not player: return state
    
    print(f"[DEBUG] resolve_support_legislation: Player {player.name} (ID: {player.id}) has {player.pc} PC, trying to commit {action.support_amount} PC")
    
    # NEW: Secret Commitment System - only validate, don't update public state
    # The actual commitment is stored secretly on the server
    
    # Find the legislation to support in pending_legislation or term_legislation
    target_legislation = None
    for legislation in state.term_legislation:
        if legislation.legislation_id == action.legislation_id and not legislation.resolved:
            target_legislation = legislation
            break
    
    if not target_legislation:
        # Provide more detailed error message
        available_legislation = [f"term: {leg.legislation_id}" for leg in state.term_legislation if not leg.resolved]
        
        error_msg = f"There's no active legislation to support with ID: {action.legislation_id}"
        if available_legislation:
            error_msg += f". Available: {', '.join(available_legislation)}"
        state.add_log(error_msg)
        return state
    
    # Allow sponsors to support their own legislation with additional PC commitment
    is_sponsor = player.id == target_legislation.sponsor_id
    
    if player.pc < action.support_amount:
        state.add_log(f"{player.name} doesn't have enough PC to provide that much support.")
        return state
    
    # FIXED: Deduct PC immediately when commitment is made
    old_pc = player.pc
    player.pc -= action.support_amount
    print(f"[DEBUG] resolve_support_legislation: Deducted {action.support_amount} PC from {player.name}. Old PC: {old_pc}, New PC: {player.pc}")
    
    # Provide confirmation feedback - only to the acting player, not publicly
    # Secret commitments should not be revealed to other players
    # Only log for human players (AI secret commitments should be hidden)
    bill = state.legislation_options[action.legislation_id]
    
    # Deduct AP cost
    state.action_points[player.id] -= 1
    
    if player.name == "Human":
        if is_sponsor:
            state.add_log(f"You secretly commit {action.support_amount} PC to support your own legislation.")
        else:
            state.add_log(f"You secretly commit {action.support_amount} PC to support the {bill.title}.")
    
    # Public log for all players (including AI)
    state.add_log(f"{player.name} makes a commitment to the {bill.title}.")
    
    # Actually record the commitment
    current_support = target_legislation.support_players.get(player.id, 0)
    target_legislation.support_players[player.id] = current_support + action.support_amount

    return state

def resolve_oppose_legislation(state: GameState, action: ActionOpposeLegislation) -> GameState:
    player = state.get_player_by_id(action.player_id)
    if not player: return state
    
    # Find the legislation to oppose
    target_legislation = None
    for leg in state.term_legislation:
        if leg.legislation_id == action.legislation_id:
            target_legislation = leg
            break
    
    if not target_legislation:
        state.add_log(f"There's no active legislation to oppose with ID: {action.legislation_id}")
        return state
    
    if player.pc < action.oppose_amount:
        state.add_log(f"{player.name} doesn't have enough PC to provide that much opposition.")
        return state
    
    # Deduct PC immediately
    player.pc -= action.oppose_amount
    
    # Record the secret opposition
    target_legislation.oppose_players[player.id] = target_legislation.oppose_players.get(player.id, 0) + action.oppose_amount
    
    # Deduct AP cost and add a log entry
    state.action_points[player.id] -= 1
    bill_title = state.legislation_options[action.legislation_id].title
    state.add_log(f"{player.name} secretly committed {action.oppose_amount} PC to oppose the {bill_title}")

    return state

def resolve_declare_candidacy(state: GameState, action: ActionDeclareCandidacy) -> GameState:
    from models.components import Candidacy
    player = state.get_player_by_id(action.player_id)
    if not player: return state
    
    # Check if candidacy has already been declared this round
    # (Removed: allow multiple candidacies per round)
    # if state.candidacy_declared_this_round:
    #     state.add_log(f"A candidacy has already been declared this round. {player.name} must wait until next round.")
    #     return state
    
    office = state.offices[action.office_id]
    cost = office.candidacy_cost
    # The committed_pc is already part of the cost, so we only need to pay the remaining amount
    remaining_cost = cost - action.committed_pc
    if player.pc < remaining_cost:
        state.add_log(f"You cannot afford the cost to run for this office with the committed PC.")
        return state
    
    # Deduct AP cost
    state.action_points[player.id] -= 2

    player.pc -= remaining_cost
    candidacy = Candidacy(player_id=player.id, office_id=action.office_id, committed_pc=action.committed_pc)
    state.secret_candidacies.append(candidacy)
    # state.candidacy_declared_this_round = True # This line is removed
    
    state.add_log(f"{player.name} pays {cost} PC to run for {office.title} and secretly commits additional funds.")
    return state

#--- Phase Resolvers ---

def resolve_upkeep(state: GameState) -> GameState:
    # Reset candidacy flag for new round
    # state.candidacy_declared_this_round = False # This line is removed
    
    # Reset action points for all players for the new round
    for p in state.players:
        state.action_points[p.id] = 2
    
    mood = state.public_mood
    income_multiplier = 2 if "UNEXPECTED_SURPLUS" in state.active_effects else 1
    if income_multiplier > 1:
        state.add_log("EVENT: Unexpected Surplus provides double income for incumbents this turn.")

    for p in state.players:
        if p.is_incumbent:
            p.pc += mood
            state.add_log(f"Incumbent {p.name} {'gains' if mood >= 0 else 'loses'} {abs(mood)} PC from Public Mood.")
        else:
            p.pc -= mood
            state.add_log(f"Outsider {p.name} {'gains' if mood <= 0 else 'loses'} {abs(mood)} PC from Public Mood.")
        for ally in p.allies:
            if ally.upkeep_cost > 0:
                if p.pc >= ally.upkeep_cost:
                    p.pc -= ally.upkeep_cost
                    state.add_log(f"{p.name} pays {ally.upkeep_cost} PC for their ally, {ally.title}.")
                else:
                    p.allies.remove(ally)
                    state.add_log(f"{p.name} cannot afford upkeep for {ally.title} and must discard them.")
        if p.is_incumbent and p.current_office:
            income = p.current_office.income * income_multiplier
            p.pc += income
            state.add_log(f"{p.name} collects {income} PC income from the {p.current_office.title} office.")

    # Clear one-time effects after they've been applied
    if "UNEXPECTED_SURPLUS" in state.active_effects:
        state.active_effects.remove("UNEXPECTED_SURPLUS")
    if "STOCK_CRASH" in state.active_effects:
        state.active_effects.remove("STOCK_CRASH")
    
    # Clear negative favor effects that expire at end of round
    if state.media_scrutiny_players:
        state.add_log("Media scrutiny effects have cleared for the new round.")
    state.media_scrutiny_players.clear()  # Media scrutiny expires at end of round
    
    # Handle hot potato effect
    if state.hot_potato_holder is not None:
        hot_potato_player = state.get_player_by_id(state.hot_potato_holder)
        if hot_potato_player:
            # Since campaign actions are removed, hot potato effect is simplified
            # Player loses 5 PC instead of campaign influence
            hot_potato_player.pc -= 5
            state.add_log(f"{hot_potato_player.name} loses 5 PC for holding the politically toxic dossier.")
            
            # Clear the hot potato
            state.hot_potato_holder = None

    return state

def _resolve_single_legislation(state: GameState, bill_to_resolve: PendingLegislation) -> GameState:
    """Resolves a single piece of legislation."""
    bill = state.legislation_options[bill_to_resolve.legislation_id]
    sponsor = state.get_player_by_id(bill_to_resolve.sponsor_id)
    
    if not sponsor:
        state.add_log(f"Error: Sponsor not found for {bill.title}.")
        bill_to_resolve.resolved = True # Mark as resolved to avoid retrying
        return state
    
    state.add_log(f"\n--- Resolving {bill.title} (Enhanced PC Gambling System) ---")
    
    # Calculate total influence committed
    total_support = sum(bill_to_resolve.support_players.values())
    total_opposition = sum(bill_to_resolve.oppose_players.values())
    net_influence = total_support - total_opposition
    
    # Show committed amounts
    if bill_to_resolve.support_players:
        support_details = []
        for player_id, amount in bill_to_resolve.support_players.items():
            player = state.get_player_by_id(player_id)
            if player:
                support_details.append(f"{player.name} ({amount} PC)")
        state.add_log(f"Support: {', '.join(support_details)}")
    
    if bill_to_resolve.oppose_players:
        oppose_details = []
        for player_id, amount in bill_to_resolve.oppose_players.items():
            player = state.get_player_by_id(player_id)
            if player:
                oppose_details.append(f"{player.name} ({amount} PC)")
        state.add_log(f"Opposition: {', '.join(oppose_details)}")
    
    state.add_log(f"Net influence: {net_influence} PC")
    
    # Apply war penalty if active (reduces net influence)
    war_penalty = 0
    if "WAR_BREAKS_OUT" in state.active_effects:
        war_penalty = -2
        net_influence += war_penalty
        state.add_log(f"War penalty: -2 PC (net influence reduced to {net_influence} PC)")
    
    # Determine outcome based on influence vs targets
    outcome = "Failure"
    sponsor_bonus_multiplier = 1.5  # Sponsor gets 50% bonus on success
    sponsor_penalty_multiplier = 1.5  # Sponsor gets 50% penalty on failure
    
    if net_influence >= bill.crit_target:
        outcome = "Critical Success"
        # Sponsor gets enhanced reward with bonus multiplier
        base_reward = bill.crit_reward
        sponsor_reward = int(base_reward * sponsor_bonus_multiplier)
        sponsor.pc += sponsor_reward
        if bill.mood_change > 0:
            apply_public_mood_effect(state, mood_change=bill.mood_change, pc_bonus=2)
        state.add_log(f"Critical Success! {sponsor.name} gains {sponsor_reward} PC (base {base_reward} + {sponsor_bonus_multiplier}x bonus).")
    elif net_influence >= bill.success_target:
        outcome = "Success"
        # Sponsor gets enhanced reward with bonus multiplier
        base_reward = bill.success_reward
        sponsor_reward = int(base_reward * sponsor_bonus_multiplier)
        sponsor.pc += sponsor_reward
        if bill.mood_change > 0:
            apply_public_mood_effect(state, mood_change=bill.mood_change, pc_bonus=2)
        state.add_log(f"Success! {sponsor.name} gains {sponsor_reward} PC (base {base_reward} + {sponsor_bonus_multiplier}x bonus).")
    else:
        # Sponsor gets enhanced penalty
        base_penalty = bill.failure_penalty
        sponsor_penalty = int(base_penalty * sponsor_penalty_multiplier)
        sponsor.pc -= sponsor_penalty
        state.add_log(f"Failure! The bill fails. {sponsor.name} loses {sponsor_penalty} PC (base {base_penalty} + {sponsor_penalty_multiplier}x penalty).")
    
    # Enhanced reward system for supporters/opponents based on commitment size
    passed = outcome in ["Success", "Critical Success"]
    
    # Reward supporters if legislation passed (gambling-style rewards)
    if passed and bill_to_resolve.support_players:
        state.add_log("--- Supporters Rewards ---")
        for player_id, amount in bill_to_resolve.support_players.items():
            player = state.get_player_by_id(player_id)
            if player:
                # Bigger commitments get bigger rewards (gambling mechanic)
                if amount >= 10:
                    reward_multiplier = 2.0  # 2x reward for big commitments (10+ PC)
                    reward = int(amount * reward_multiplier)
                    state.add_log(f"{player.name} committed {amount} PC - BIG BET! Gets {reward} PC (2x multiplier).")
                elif amount >= 5:
                    reward_multiplier = 1.5  # 1.5x reward for medium commitments (5-9 PC)
                    reward = int(amount * reward_multiplier)
                    state.add_log(f"{player.name} committed {amount} PC - Medium bet! Gets {reward} PC (1.5x multiplier).")
                else:
                    reward_multiplier = 1.0  # 1x reward for small commitments (1-4 PC)
                    reward = int(amount * reward_multiplier)
                    state.add_log(f"{player.name} committed {amount} PC - Small bet. Gets {reward} PC (1x multiplier).")
                
                player.pc += reward
    
    # Reward opponents if legislation failed (gambling-style rewards)
    if not passed and bill_to_resolve.oppose_players:
        state.add_log("--- Opponents Rewards ---")
        for player_id, amount in bill_to_resolve.oppose_players.items():
            player = state.get_player_by_id(player_id)
            if player:
                # Bigger commitments get bigger rewards (gambling mechanic)
                if amount >= 10:
                    reward_multiplier = 2.0  # 2x reward for big commitments (10+ PC)
                    reward = int(amount * reward_multiplier)
                    state.add_log(f"{player.name} committed {amount} PC - BIG BET! Gets {reward} PC (2x multiplier).")
                elif amount >= 5:
                    reward_multiplier = 1.5  # 1.5x reward for medium commitments (5-9 PC)
                    reward = int(amount * reward_multiplier)
                    state.add_log(f"{player.name} committed {amount} PC - Medium bet! Gets {reward} PC (1.5x multiplier).")
                else:
                    reward_multiplier = 1.0  # 1x reward for small commitments (1-4 PC)
                    reward = int(amount * reward_multiplier)
                    state.add_log(f"{player.name} committed {amount} PC - Small bet. Gets {reward} PC (1x multiplier).")
                
                player.pc += reward
    
    # Record result
    state.last_sponsor_result = {'player_id': sponsor.id, 'passed': passed}
    state.legislation_history.append({
        'sponsor_id': sponsor.id, 
        'leg_id': bill.id, 
        'outcome': outcome,
        'support_players': dict(bill_to_resolve.support_players),
        'oppose_players': dict(bill_to_resolve.oppose_players),
        'net_influence': net_influence
    })
    
    # Mark as resolved
    bill_to_resolve.resolved = True
    
    return state

def resolve_elections(state: GameState, disable_dice_roll: bool = False) -> GameState:
    state.add_log("\n--- ELECTION RESULTS ---")
    
    # Process elections for each office
    for office in state.offices.values():
        candidates = [c for c in state.secret_candidacies if c.office_id == office.id]
        
        if not candidates:
            continue  # No candidates for this office

        scores = {}
        dice_rolls = {}
        
        for cand in candidates:
            player = state.get_player_by_id(cand.player_id)
            if player:
                # Base score is committed PC
                base_score = cand.committed_pc
                
                if disable_dice_roll:
                    # Deterministic mode: no dice roll
                    final_score = base_score
                    dice_roll = 0
                else:
                    # Dice roll mode: add random element
                    dice_roll = random.randint(1, 6)
                    final_score = base_score + dice_roll
                
                scores[player.name] = final_score
                dice_rolls[player.name] = dice_roll
                
                if disable_dice_roll:
                    state.add_log(f"{player.name}: {base_score} PC (no dice roll)")
                else:
                    state.add_log(f"{player.name}: {base_score} PC + {dice_roll} (dice) = {final_score}")

        # Add NPC challenger if there are candidates
        if candidates:
            npc_base = office.npc_challenger_bonus
            if disable_dice_roll:
                npc_score = npc_base
                npc_dice = 0
            else:
                npc_dice = random.randint(1, 6)
                npc_score = npc_base + npc_dice
            
            scores["NPC Challenger"] = npc_score
            dice_rolls["NPC Challenger"] = npc_dice
            
            if disable_dice_roll:
                state.add_log(f"NPC Challenger: {npc_base} (no dice roll)")
            else:
                state.add_log(f"NPC Challenger: {npc_base} + {npc_dice} (dice) = {npc_score}")
        
        # Determine winner
        if scores:
            winner_name = max(scores, key=lambda k: scores[k])
            winner_score = scores[winner_name]
        else:
            winner_name = "NPC Challenger" # Should not happen if candidates exist
            winner_score = 0

        winner = None
        if winner_name != "NPC Challenger":
            winner = next((p for p in state.players if p.name == winner_name), None)

        if winner:
            _award_office(state, winner, office)
            state.add_log(f"{winner.name} wins the election for {office.title}!")
        else:
            state.add_log(f"The NPC Challenger wins the election for {office.title}.")

        # Always log the result for the frontend
        result_data = {
            "type": "election",
            "office_name": office.title,
            "scores": scores,
            "dice_rolls": dice_rolls,
            "winner_name": winner_name,
            "winner_score": winner_score
        }
        state.last_election_results = result_data

    # Clear candidacies after elections are resolved
    state.secret_candidacies.clear()
    
    return state

def _award_office(state: GameState, winner: Player, new_office: Office):
    if not winner: return
    state.add_log(f"{winner.name} wins the election for {new_office.title}!")
    if winner.current_office:
        state.add_log(f"{winner.name} vacates the {winner.current_office.title} office.")
    winner.current_office = new_office
    
    # Check for Supreme Court Vacancy effect on Presidential election
    if new_office.id == "PRESIDENT" and "SUPREME_COURT_VACANCY" in state.active_effects:
        winner.pc += 20
        state.add_log(f"{winner.name} gains an additional 20 PC from the Supreme Court vacancy legacy effect!")
        state.active_effects.remove("SUPREME_COURT_VACANCY")

def _event_economic_boom(state: GameState) -> GameState:
    """Move Public Mood +2 spaces. All players gain 5 PC."""
    state = apply_public_mood_effect(state, 2)
    for player in state.players:
        player.pc += 5
    state.add_log("The economy is booming! Public mood improves and all players gain 5 PC.")
    return state

def _event_recession_hits(state: GameState) -> GameState:
    """Move Public Mood -2 spaces. All players lose 5 PC."""
    state = apply_public_mood_effect(state, -2)
    for player in state.players:
        player.pc -= 5
    state.add_log("A recession hits! Public mood worsens and all players lose 5 PC.")
    return state

def _event_scandal(state: GameState) -> GameState:
    """The player with the most PC loses 15 PC and must immediately draw one card from the Scrutiny Deck."""
    richest_player = max(state.players, key=lambda p: p.pc)
    richest_player.pc -= 15
    # This part would need a way to draw and resolve a scrutiny card.
    # For now, we'll just log it.
    state.add_log(f"Scandal! {richest_player.name} is caught in a scandal, losing 15 PC.")
    return state

def _event_unexpected_surplus(state: GameState) -> GameState:
    """Move Public Mood +1. All office-holders collect double their income this Upkeep phase."""
    state = apply_public_mood_effect(state, 1)
    state.active_effects.add("UNEXPECTED_SURPLUS")
    state.add_log("An unexpected surplus improves public mood. Office holders will receive double income this term.")
    return state

def _event_last_bill_dud(state: GameState) -> GameState:
    """The last player to successfully sponsor legislation loses 10 PC. Move Public Mood -1."""
    if state.last_sponsor_result and state.last_sponsor_result['passed']:
        sponsor = state.get_player_by_id(state.last_sponsor_result['player_id'])
        if sponsor:
            sponsor.pc -= 10
            state.add_log(f"The last bill was a dud! {sponsor.name} loses 10 PC.")
    state = apply_public_mood_effect(state, -1)
    return state
    
def _event_foreign_policy_crisis(state: GameState) -> GameState:
    """A random player rolls a d6: 1-3: Lose 10 PC. 4-6: Gain 10 PC."""
    player = random.choice(state.players)
    if random.randint(1, 6) <= 3:
        player.pc -= 10
        state.add_log(f"A foreign policy crisis erupts! {player.name} handles it poorly, losing 10 PC.")
    else:
        player.pc += 10
        state.add_log(f"A foreign policy crisis is resolved successfully! {player.name} gains 10 PC.")
    return state

def _event_supreme_court_vacancy(state: GameState) -> GameState:
    """Legacy Effect. The winner of the next Presidential election gains an additional 20 PC upon victory."""
    state.active_effects.add("SUPREME_COURT_VACANCY")
    state.add_log("A Supreme Court vacancy has occurred. The next President will have a lasting legacy.")
    return state

def _event_last_bill_hit(state: GameState) -> GameState:
    """The last player to successfully sponsor legislation gains 10 PC. Move Public Mood +1."""
    if state.last_sponsor_result and state.last_sponsor_result['passed']:
        sponsor = state.get_player_by_id(state.last_sponsor_result['player_id'])
        if sponsor:
            sponsor.pc += 10
            state.add_log(f"The last bill was a hit! {sponsor.name} gains 10 PC.")
    state = apply_public_mood_effect(state, 1)
    return state

def _event_bipartisan_breakthrough(state: GameState) -> GameState:
    """All players in Congress or Senate may immediately pay 5 PC to gain 10 PC."""
    state.add_log("A bipartisan breakthrough! Some office holders can make a deal.")
    # This would require a sub-prompt, which is not supported in the current event system.
    # For now, we'll just log it.
    return state

def _event_war_breaks_out(state: GameState) -> GameState:
    """Public Mood is locked at its current position for the rest of the Term. All legislation requires 2 additional PC to pass until the Term ends."""
    state.active_effects.add("WAR_BREAKS_OUT")
    state.add_log("War has broken out! Public mood is frozen, and legislation is harder to pass.")
    return state

def _event_tech_leap(state: GameState) -> GameState:
    """Move Public Mood +1. The player with the least PC gains 10 PC."""
    state = apply_public_mood_effect(state, 1)
    poorest_player = min(state.players, key=lambda p: p.pc)
    poorest_player.pc += 10
    state.add_log(f"A technological leap improves public mood and helps {poorest_player.name} with a 10 PC grant.")
    return state

def _event_natural_disaster(state: GameState) -> GameState:
    """Move Public Mood -1. A random Governor (or a random player if no Governors) must respond, losing 10 PC."""
    state = apply_public_mood_effect(state, -1)
    governors = [p for p in state.players if p.current_office and p.current_office.id == "GOVERNOR"]
    if governors:
        victim = random.choice(governors)
    else:
        victim = random.choice(state.players)
    victim.pc -= 10
    state.add_log(f"A natural disaster strikes! {victim.name} must respond, losing 10 PC.")
    return state
    
def _event_media_darling(state: GameState) -> GameState:
    """Choose one player. They gain 5 PC and are immune to the next 'Scandal!' event."""
    # This requires a choice, not supported yet. For now, affects a random player.
    darling = random.choice(state.players)
    darling.pc += 5
    state.active_effects.add(f"MEDIA_DARLING_{darling.id}")
    state.add_log(f"{darling.name} has become a media darling, gaining 5 PC and scandal immunity.")
    return state

def _event_gaffe(state: GameState) -> GameState:
    """Choose an opponent. They lose 8 PC."""
    # This requires a choice, not supported yet. For now, affects a random opponent.
    player = state.get_current_player()
    opponents = [p for p in state.players if p.id != player.id]
    if opponents:
        victim = random.choice(opponents)
        victim.pc -= 8
        state.add_log(f"{victim.name} makes a gaffe on the campaign trail, losing 8 PC.")
    return state

def _event_endorsement(state: GameState) -> GameState:
    """You (the player who drew this card) gain 10 PC."""
    player = state.get_current_player()
    player.pc += 10
    state.add_log(f"{player.name} receives a surprise endorsement, gaining 10 PC.")
    return state

def _event_grassroots(state: GameState) -> GameState:
    """The player with the fewest held offices (0 is fewest) gains 10 PC."""
    min_offices = min(len(p.allies) + (1 if p.current_office else 0) for p in state.players)
    beneficiaries = [p for p in state.players if len(p.allies) + (1 if p.current_office else 0) == min_offices]
    if beneficiaries:
        # If there's a tie, they all benefit
        for player in beneficiaries:
            player.pc += 10
            state.add_log(f"A grassroots movement supports {player.name}, who gains 10 PC.")
    return state

def _event_voter_apathy(state: GameState) -> GameState:
    """Public Mood moves 1 space towards 'Neutral'."""
    if state.public_mood > 0:
        state = apply_public_mood_effect(state, -1)
    elif state.public_mood < 0:
        state = apply_public_mood_effect(state, 1)
    state.add_log("Voter apathy is high. Public mood returns towards neutral.")
    return state

def _event_midterm_fury(state: GameState) -> GameState:
    """Timing. Draw only in Round 2 or 3 of a Term. Public Mood moves 2 spaces towards 'Very Angry'."""
    if state.round_marker in [2, 3]:
        state = apply_public_mood_effect(state, -2)
        state.add_log("Midterm fury erupts! Public mood plummets.")
    else:
        state.add_log("Midterm fury fizzles out due to timing.")
    return state

def _event_stock_crash(state: GameState) -> GameState:
    """Move Public Mood -3 spaces. Any player who chose to 'Fundraise' this round loses 5 PC instead of gaining it."""
    state = apply_public_mood_effect(state, -3)
    state.active_effects.add("STOCK_CRASH")
    state.add_log("The stock market crashes! Public mood plummets, and fundraising is impacted.")
    return state

def _event_celeb_politician(state: GameState) -> GameState:
    """The player with the lowest PC gains 15 PC."""
    poorest_player = min(state.players, key=lambda p: p.pc)
    poorest_player.pc += 15
    state.add_log(f"A celebrity politician enters the race, boosting the underdog {poorest_player.name} with 15 PC.")
    return state

def resolve_event_card(state: GameState) -> GameState:
    event = state.event_deck.draw()
    if not event:
        state.add_log("Event deck is empty! Reshuffled.")
        event = state.event_deck.draw()
        if not event: return state
    state.add_log(f"\nEVENT: {event.title}")
    state.add_log(f"\"{event.description}\"")
    event_resolvers = {
        "ECONOMIC_BOOM": _event_economic_boom,
        "RECESSION_HITS": _event_recession_hits,
        "SCANDAL": _event_scandal,
        "UNEXPECTED_SURPLUS": _event_unexpected_surplus,
        "LAST_BILL_DUD": _event_last_bill_dud,
        "FOREIGN_POLICY_CRISIS": _event_foreign_policy_crisis,
        "SUPREME_COURT_VACANCY": _event_supreme_court_vacancy,
        "LAST_BILL_HIT": _event_last_bill_hit,
        "BIPARTISAN_BREAKTHROUGH": _event_bipartisan_breakthrough,
        "WAR_BREAKS_OUT": _event_war_breaks_out,
        "TECH_LEAP": _event_tech_leap,
        "NATURAL_DISASTER": _event_natural_disaster,
        "MEDIA_DARLING": _event_media_darling,
        "GAFFE": _event_gaffe,
        "ENDORSEMENT": _event_endorsement,
        "GRASSROOTS": _event_grassroots,
        "VOTER_APATHY": _event_voter_apathy,
        "MIDTERM_FURY": _event_midterm_fury,
        "STOCK_CRASH": _event_stock_crash,
        "CELEB_POLITICIAN": _event_celeb_politician,
    }
    if isinstance(event, EventCard):
        resolver = event_resolvers.get(event.effect_id)
        if resolver:
            return resolver(state)
        else:
            state.add_log(f"Warning: No resolver found for event ID '{event.effect_id}'. No effect.")
    else:
        state.add_log(f"Warning: Event card '{event.title}' is not a valid EventCard. No effect.")
    return state

def resolve_pass_turn(state: GameState, action: ActionPassTurn) -> GameState:
    """Resolve a pass turn action."""
    player = state.get_player_by_id(action.player_id)
    if not player: return state
    
    # Passing the turn now costs all remaining AP for the turn
    state.action_points[player.id] = 0
    state.add_log(f"{player.name} passes their turn, ending their action phase.")
    return state

def resolve_resolve_legislation(state: GameState, action) -> GameState:
    """System action to resolve pending legislation."""
    # Actually call the engine's resolve_legislation_session method
    from engine.engine import GameEngine
    engine = GameEngine({})  # We'll need to pass game_data properly later
    return engine.resolve_legislation_session(state)

def resolve_resolve_elections(state: GameState, action) -> GameState:
    """System action to resolve elections."""
    # Actually call the engine's resolve_elections_session method
    from engine.engine import GameEngine
    engine = GameEngine({})  # We'll need to pass game_data properly later
    return engine.resolve_elections_session(state)

def resolve_acknowledge_results(state: GameState, action) -> GameState:
    """System action to acknowledge results and start new term."""
    # Actually call the engine's start_next_term method
    from engine.engine import GameEngine
    engine = GameEngine({})  # We'll need to pass game_data properly later
    state.awaiting_results_acknowledgement = False
    state.add_log("Results acknowledged. Starting next term.")
    return engine.start_next_term(state)


def resolve_acknowledge_ai_turn(state: GameState, action: 'AcknowledgeAITurn') -> GameState:
    """
    Resolves the acknowledgement of an AI's turn. 
    This action does nothing but allow the game loop to proceed after an AI action.
    """
    # No state change is needed, just return the state.
    # The engine will handle advancing to the next player.
    return state


def _calculate_election_influence(state: GameState, player: 'Player', office: 'Office', disable_dice_roll: bool = False) -> int:
    """Helper function to calculate total influence for a single candidate in an election."""
    base_influence = 0