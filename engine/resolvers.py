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
    ActionProposeTrade, ActionAcceptTrade, ActionDeclineTrade, ActionCompleteTrading, ActionPassTurn
)
import json

#--- Action Resolvers ---

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
    player = state.get_player_by_id(action.player_id)
    if not player: return state

    # Check for stock crash effect
    if "STOCK_CRASH" in state.active_effects:
        player.pc -= 5
        state.add_log(f"{player.name} takes the Fundraise action but loses 5 PC due to the stock market crash.")
        return state

    base_pc_gain = 5
    # Check for media scrutiny effect (halve only the base 5 PC)
    if player.id in state.media_scrutiny_players:
        halved_base = base_pc_gain // 2
        state.add_log(f"{player.name} is under media scrutiny. Base PC gain is halved to {halved_base}.")
        pc_gain = halved_base
    else:
        pc_gain = base_pc_gain

    # Add bonuses after halving
    if player.archetype.id == "FUNDRAISER":
        # Check if this is the first Fundraise action of the term
        if player.id not in state.fundraiser_first_fundraise_used:
            pc_gain += 2
            state.fundraiser_first_fundraise_used.add(player.id)
            state.add_log(f"Archetype bonus: +2 PC for The Fundraiser (first Fundraise action this term).")
        else:
            state.add_log(f"The Fundraiser has already used their first Fundraise action this term.")
    if any(ally.id == "HEDGE_FUND_BRO" for ally in player.allies):
        pc_gain += 10
        state.add_log(f"Ally bonus: +10 PC from Steve McRoberts.")

    player.pc += pc_gain
    state.add_log(f"{player.name} takes the Fundraise action and gains {pc_gain} PC.")
    return state

def resolve_network(state: GameState, action: ActionNetwork) -> GameState:
    player = state.get_player_by_id(action.player_id)
    if not player: return state
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

def resolve_use_favor(state: GameState, action: ActionUseFavor) -> GameState:
    player = state.get_player_by_id(action.player_id)
    if not player: return state
    
    # Find the favor in player's hand
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
    
    # Remove the favor from player's hand
    player.favors.pop(favor_index)
    
    # Apply favor effect based on favor type
    if favor.id == "EXTRA_FUNDRAISING":
        pc_gain = 8
        player.pc += pc_gain
        state.add_log(f"{player.name} uses '{favor.description}' and gains {pc_gain} PC.")
    
    elif favor.id == "LEGISLATIVE_INFLUENCE":
        if state.pending_legislation:
            # Add support to pending legislation
            current_support = state.pending_legislation.support_players.get(player.id, 0)
            state.pending_legislation.support_players[player.id] = current_support + 5
            state.add_log(f"{player.name} uses '{favor.description}' to add 5 PC support to pending legislation.")
        else:
            state.add_log(f"{player.name} uses '{favor.description}' but there's no pending legislation.")
    
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
    state.add_log(f"{player.name} sponsored the {bill.title}.")
    state.add_log(f"This legislation will be voted on during the end-of-term legislation session.")
    
    # Create pending legislation for other players to respond to during the term
    # If there's already pending legislation, move it to term_legislation first
    if state.pending_legislation and not state.pending_legislation.resolved:
        state.term_legislation.append(state.pending_legislation)
        state.pending_legislation = None
    
    # Create new pending legislation
    state.pending_legislation = PendingLegislation(
        legislation_id=action.legislation_id,
        sponsor_id=player.id
    )
    
    return state

def resolve_support_legislation(state: GameState, action: ActionSupportLegislation) -> GameState:
    player = state.get_player_by_id(action.player_id)
    if not player: return state
    
    print(f"[DEBUG] resolve_support_legislation: Player {player.name} (ID: {player.id}) has {player.pc} PC, trying to commit {action.support_amount} PC")
    
    # NEW: Secret Commitment System - only validate, don't update public state
    # The actual commitment is stored secretly on the server
    
    # Find the legislation to support in pending_legislation or term_legislation
    target_legislation = None
    
    # Check pending legislation first
    if state.pending_legislation and state.pending_legislation.legislation_id == action.legislation_id:
        target_legislation = state.pending_legislation
    
    # If not found in pending, check term legislation
    if not target_legislation:
        for legislation in state.term_legislation:
            if legislation.legislation_id == action.legislation_id and not legislation.resolved:
                target_legislation = legislation
                break
    
    if not target_legislation:
        # Provide more detailed error message
        available_legislation = []
        if state.pending_legislation:
            available_legislation.append(f"pending: {state.pending_legislation.legislation_id}")
        for leg in state.term_legislation:
            if not leg.resolved:
                available_legislation.append(f"term: {leg.legislation_id}")
        
        error_msg = f"There's no legislation to support. Looking for: {action.legislation_id}"
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
    
    # Provide confirmation feedback
    if is_sponsor:
        state.add_log(f"{player.name} secretly commits {action.support_amount} PC to support their own legislation.")
        state.add_log(f"Secret commitment has been registered.")
    else:
        state.add_log(f"{player.name} secretly commits {action.support_amount} PC to support the legislation.")
        state.add_log(f"Secret commitment has been registered.")
    
    return state

def resolve_oppose_legislation(state: GameState, action: ActionOpposeLegislation) -> GameState:
    player = state.get_player_by_id(action.player_id)
    if not player: return state
    
    print(f"[DEBUG] resolve_oppose_legislation: Player {player.name} (ID: {player.id}) has {player.pc} PC, trying to commit {action.oppose_amount} PC")
    
    # NEW: Secret Commitment System - only validate, don't update public state
    # The actual commitment is stored secretly on the server
    
    # Find the legislation to oppose in pending_legislation or term_legislation
    target_legislation = None
    
    # Check pending legislation first
    if state.pending_legislation and state.pending_legislation.legislation_id == action.legislation_id:
        target_legislation = state.pending_legislation
    
    # If not found in pending, check term legislation
    if not target_legislation:
        for legislation in state.term_legislation:
            if legislation.legislation_id == action.legislation_id and not legislation.resolved:
                target_legislation = legislation
                break
    
    if not target_legislation:
        # Provide more detailed error message
        available_legislation = []
        if state.pending_legislation:
            available_legislation.append(f"pending: {state.pending_legislation.legislation_id}")
        for leg in state.term_legislation:
            if not leg.resolved:
                available_legislation.append(f"term: {leg.legislation_id}")
        error_msg = f"There's no legislation to oppose. Looking for: {action.legislation_id}"
        if available_legislation:
            error_msg += f". Available: {', '.join(available_legislation)}"
        state.add_log(error_msg)
        return state
    
    # Allow sponsors to oppose their own legislation (for strategic reasons)
    is_sponsor = player.id == target_legislation.sponsor_id
    
    if player.pc < action.oppose_amount:
        state.add_log(f"{player.name} doesn't have enough PC to provide that much opposition.")
        return state
    
    # FIXED: Deduct PC immediately when commitment is made
    old_pc = player.pc
    player.pc -= action.oppose_amount
    print(f"[DEBUG] resolve_oppose_legislation: Deducted {action.oppose_amount} PC from {player.name}. Old PC: {old_pc}, New PC: {player.pc}")
    
    # Provide confirmation feedback
    if is_sponsor:
        state.add_log(f"{player.name} secretly commits {action.oppose_amount} PC to oppose their own legislation.")
        state.add_log(f"Secret commitment has been registered.")
    else:
        state.add_log(f"{player.name} secretly commits {action.oppose_amount} PC to oppose the legislation.")
        state.add_log(f"Secret commitment has been registered.")
    
    return state

def resolve_declare_candidacy(state: GameState, action: ActionDeclareCandidacy) -> GameState:
    player = state.get_player_by_id(action.player_id)
    if not player: return state

    # Check if player has enough PC for candidacy cost
    office = state.offices.get(action.office_id)
    if not office:
        state.add_log(f"Office with ID {action.office_id} not found.")
        return state
        
    candidacy_cost = office.candidacy_cost
    if player.pc < candidacy_cost:
        state.add_log(f"{player.name} does not have enough PC to run for {office.title} (needs {candidacy_cost}).")
        return state
        
    # Deduct candidacy cost
    player.pc -= candidacy_cost

    # Add candidacy to secret list
    candidacy = Candidacy(player_id=player.id, office_id=action.office_id, committed_pc=action.committed_pc)
    state.secret_candidacies.append(candidacy)
    
    state.add_log(f"{player.name} secretly declares candidacy for {office.title} and pays {candidacy_cost} PC.")
    return state

def resolve_upkeep(state: GameState) -> GameState:
    # Move any pending legislation to term legislation (will be resolved at end of term)
    if state.pending_legislation:
        state.term_legislation.append(state.pending_legislation)
        state.pending_legislation = None
    
    # Pay upkeep for allies
    for player in state.players:
        upkeep_cost = sum(ally.upkeep_cost for ally in player.allies)
        if upkeep_cost > 0:
            player.pc -= upkeep_cost
            state.add_log(f"{player.name} pays {upkeep_cost} PC for ally upkeep.")

    # Reset fundraiser archetype bonus
    state.fundraiser_first_fundraise_used.clear()

    return state

def resolve_pending_legislation(state: GameState) -> GameState:
    """Resolves pending legislation using enhanced PC commitment gambling system."""
    if not state.pending_legislation or state.pending_legislation.resolved:
        return state
    
    pending = state.pending_legislation
    bill = state.legislation_options[pending.legislation_id]
    sponsor = state.get_player_by_id(pending.sponsor_id)
    
    if not sponsor:
        state.add_log("Error: Sponsor not found for pending legislation.")
        return state
    
    state.add_log(f"\n--- Resolving {bill.title} (Enhanced PC Gambling System) ---")
    
    # Calculate total influence committed
    total_support = sum(pending.support_players.values())
    total_opposition = sum(pending.oppose_players.values())
    net_influence = total_support - total_opposition
    
    # Show committed amounts
    if pending.support_players:
        support_details = []
        for player_id, amount in pending.support_players.items():
            player = state.get_player_by_id(player_id)
            if player:
                support_details.append(f"{player.name} ({amount} PC)")
        state.add_log(f"Support: {', '.join(support_details)}")
    
    if pending.oppose_players:
        oppose_details = []
        for player_id, amount in pending.oppose_players.items():
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
    if passed and pending.support_players:
        state.add_log("--- Supporters Rewards ---")
        for player_id, amount in pending.support_players.items():
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
    if not passed and pending.oppose_players:
        state.add_log("--- Opponents Rewards ---")
        for player_id, amount in pending.oppose_players.items():
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
        'support_players': dict(pending.support_players),
        'oppose_players': dict(pending.oppose_players),
        'net_influence': net_influence
    })
    
    # Mark as resolved
    pending.resolved = True
    state.pending_legislation = None
    
    return state

def resolve_elections(state: GameState) -> GameState:
    state.add_log("\n--- ELECTION RESULTS ---")
    
    # Process elections for each office
    for office in state.offices.values():
        candidates = [c for c in state.secret_candidacies if c.office_id == office.id]
        
        if not candidates:
            continue  # No candidates for this office

        scores = {}
        for cand in candidates:
            player = state.get_player_by_id(cand.player_id)
            if player:
                # Base score is committed PC
                score = cand.committed_pc
                scores[player.name] = score

        # Add NPC challenger if there are candidates
        if candidates:
            scores["NPC Challenger"] = office.npc_challenger_bonus
        
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
            "winner_name": winner_name,
            "winner_score": winner_score
        }
        state.last_election_results = result_data

    # Clear candidacies after elections are resolved
    state.secret_candidacies.clear()

    # Transition to the next term
    state = start_next_term(state)
    
    return state

def start_next_term(state: GameState) -> GameState:
    """Clears the board for the next term, but does not start any new phases."""
    state.round_marker = 1
    state.current_phase = "ACTION_PHASE"
    state.secret_candidacies.clear()
    state.term_legislation.clear()
    state.pending_legislation = None
    for p in state.players:
        state.action_points[p.id] = 2
    # Reset any term-based abilities or effects
    for effect in list(state.active_effects):
        if effect in ["WAR_BREAKS_OUT", "VOTER_APATHY"]:
            state.active_effects.remove(effect)
    state.fundraiser_first_fundraise_used.clear()
    state.add_log("\n--- NEW TERM BEGINS ---")
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

def _event_economic_boom(state: GameState) -> GameState:
    return apply_public_mood_effect(state, mood_change=2, pc_bonus=5)

def _event_recession_hits(state: GameState) -> GameState:
    return apply_public_mood_effect(state, mood_change=-2, pc_bonus=5)

def _event_scandal(state: GameState) -> GameState:
    if not state.players: return state
    
    # Check for media darling immunity
    if "MEDIA_DARLING_IMMUNITY" in state.active_effects:
        state.add_log("A player is immune to scandal due to being a Media Darling!")
        state.active_effects.remove("MEDIA_DARLING_IMMUNITY")
        return state
    
    richest_player = max(state.players, key=lambda p: p.pc)
    richest_player.pc -= 15
    state.add_log(f"{richest_player.name} is caught in a scandal! They lose 15 PC.")
    scrutiny_card = state.scrutiny_deck.draw()
    if scrutiny_card and isinstance(scrutiny_card, ScrutinyCard):
        state.add_log(f"They must also face scrutiny: {scrutiny_card.title} - {scrutiny_card.description}")
        if scrutiny_card.effect_id == "PAY_PC_10":
            richest_player.pc -= 10
    else:
        state.add_log("The Scrutiny Deck is empty or card has no effect.")
    return state

def _event_unexpected_surplus(state: GameState) -> GameState:
    apply_public_mood_effect(state, mood_change=1, pc_bonus=3)
    state.active_effects.add("UNEXPECTED_SURPLUS")
    state.add_log("Incumbents will receive double income this round.")
    return state

def _event_last_bill_dud(state: GameState) -> GameState:
    apply_public_mood_effect(state, mood_change=-1, pc_bonus=3)
    
    last_sponsor_info = state.last_sponsor_result
    if last_sponsor_info and last_sponsor_info.get('passed'):
        player_id = last_sponsor_info.get('player_id')
        if player_id is not None:
            player = state.get_player_by_id(player_id)
            if player:
                player.pc -= 10
                state.add_log(f"{player.name}, who sponsored the last successful bill, loses 10 PC.")
            else:
                state.add_log("Could not find the player who sponsored the last bill.")
        else:
            state.add_log("Sponsor player ID not found in records.")
    else:
        state.add_log("No legislation was successfully sponsored recently, so this event has no target.")
    
    return state

def _event_foreign_policy_crisis(state: GameState) -> GameState:
    if not state.players: return state
    
    # Randomly select a player
    selected_player = random.choice(state.players)
    state.add_log(f"{selected_player.name} is affected by the Foreign Policy Crisis.")
    
    # Roll a d6
    roll = random.randint(1, 6)
    state.add_log(f"{selected_player.name} rolls a {roll}.")
    
    # Apply effect based on roll
    if roll <= 3:
        selected_player.pc -= 10
        state.add_log(f"{selected_player.name} loses 10 PC from the crisis.")
    else:
        selected_player.pc += 10
        state.add_log(f"{selected_player.name} gains 10 PC from handling the crisis well.")
    
    return state

def _event_supreme_court_vacancy(state: GameState) -> GameState:
    state.active_effects.add("SUPREME_COURT_VACANCY")
    state.add_log("A Supreme Court vacancy has opened! The next President will gain an additional 20 PC upon victory.")
    return state

def _event_last_bill_hit(state: GameState) -> GameState:
    apply_public_mood_effect(state, mood_change=1, pc_bonus=3)
    
    last_sponsor_info = state.last_sponsor_result
    if last_sponsor_info and last_sponsor_info.get('passed'):
        player_id = last_sponsor_info.get('player_id')
        if player_id is not None:
            player = state.get_player_by_id(player_id)
            if player:
                player.pc += 10
                state.add_log(f"{player.name}, who sponsored the last successful bill, gains 10 PC.")
            else:
                state.add_log("Could not find the player who sponsored the last bill.")
        else:
            state.add_log("Sponsor player ID not found in records.")
    else:
        state.add_log("No legislation was successfully sponsored recently, so this event has no target.")
    
    return state

def _event_bipartisan_breakthrough(state: GameState) -> GameState:
    congress_offices = {"CONGRESS_SEAT", "US_SENATOR"}
    eligible_players = [p for p in state.players if p.current_office and p.current_office.id in congress_offices]
    
    if not eligible_players:
        state.add_log("No players are in Congress or Senate positions.")
        return state
    
    state.add_log("Bipartisan Breakthrough! Congress and Senate members may pay 5 PC to gain 10 PC.")
    
    for player in eligible_players:
        if player.current_office and player.pc >= 5:
            player.pc -= 5
            player.pc += 10
            state.add_log(f"{player.name} (in {player.current_office.title}) pays 5 PC and gains 10 PC.")
        elif player.current_office:
            state.add_log(f"{player.name} (in {player.current_office.title}) cannot afford the 5 PC cost.")
    
    return state

def _event_war_breaks_out(state: GameState) -> GameState:
    state.active_effects.add("WAR_BREAKS_OUT")
    state.add_log("War has broken out! Public Mood is locked and legislation faces a -2 penalty for the rest of the term.")
    return state

def _event_tech_leap(state: GameState) -> GameState:
    apply_public_mood_effect(state, mood_change=1, pc_bonus=3)
    
    if not state.players: return state
    
    # Find player with least PC
    poorest_player = min(state.players, key=lambda p: p.pc)
    poorest_player.pc += 10
    state.add_log(f"{poorest_player.name}, with the least PC, gains 10 PC from the technological leap.")
    
    return state

def _event_natural_disaster(state: GameState) -> GameState:
    apply_public_mood_effect(state, mood_change=-1, pc_bonus=3)
    
    if not state.players: return state
    
    # Find Governors first
    governors = [p for p in state.players if p.current_office and p.current_office.id == "GOVERNOR"]
    
    if governors:
        # Select random Governor
        affected_player = random.choice(governors)
        state.add_log(f"{affected_player.name} (Governor) must respond to the natural disaster.")
    else:
        # Select random player if no Governors
        affected_player = random.choice(state.players)
        state.add_log(f"{affected_player.name} must respond to the natural disaster.")
    
    affected_player.pc -= 10
    state.add_log(f"{affected_player.name} loses 10 PC responding to the crisis.")
    
    return state

def _event_media_darling(state: GameState) -> GameState:
    if not state.players: return state
    
    # For now, randomly select a player (in a full implementation, this would be player choice)
    # TODO: Implement player choice mechanism
    selected_player = random.choice(state.players)
    selected_player.pc += 5
    state.active_effects.add("MEDIA_DARLING_IMMUNITY")
    state.add_log(f"{selected_player.name} becomes a Media Darling! They gain 5 PC and are immune to the next Scandal event.")
    
    return state

def _event_gaffe(state: GameState) -> GameState:
    if not state.players: return state
    
    # For now, randomly select an opponent (in a full implementation, this would be player choice)
    # TODO: Implement player choice mechanism
    selected_player = random.choice(state.players)
    selected_player.pc -= 8
    state.add_log(f"{selected_player.name} makes a gaffe on the trail and loses 8 PC.")
    
    return state

def _event_endorsement(state: GameState) -> GameState:
    current_player = state.get_current_player()
    current_player.pc += 10
    state.add_log(f"{current_player.name} receives a surprise endorsement and gains 10 PC!")
    
    return state

def _event_grassroots(state: GameState) -> GameState:
    if not state.players: return state
    
    # Count offices for each player (0 if no office)
    office_counts = []
    for player in state.players:
        count = 1 if player.current_office else 0
        office_counts.append((player, count))
    
    # Find player with fewest offices
    player_with_fewest = min(office_counts, key=lambda x: x[1])[0]
    player_with_fewest.pc += 10
    state.add_log(f"{player_with_fewest.name}, with the fewest offices, gains 10 PC from the grassroots movement.")
    
    return state

def _event_voter_apathy(state: GameState) -> GameState:
    state.active_effects.add("VOTER_APATHY")
    state.add_log("Voter Apathy sets in! Committed PC will be only half as effective in the next election.")
    return state

def _event_midterm_fury(state: GameState) -> GameState:
    # Check timing restriction
    if state.round_marker not in [2, 3]:
        state.add_log("Midterm Fury can only occur in Round 2 or 3 of a Term. This event has no effect.")
        return state
    
    # Move Public Mood 2 spaces towards "Very Angry" (-2) with incumbent/outsider logic
    apply_public_mood_effect(state, mood_change=-2, pc_bonus=3)
    state.add_log("Midterm Fury! Public Mood moves 2 spaces towards 'Very Angry'.")
    
    return state

def _event_stock_crash(state: GameState) -> GameState:
    apply_public_mood_effect(state, mood_change=-3, pc_bonus=3)
    state.active_effects.add("STOCK_CRASH")
    state.add_log("Stock Market Crash! Public Mood worsens by 3 spaces. Fundraising this round will cost 5 PC instead of gaining it.")
    return state

def _event_celeb_politician(state: GameState) -> GameState:
    if not state.players: return state
    
    # Find player with lowest PC
    poorest_player = min(state.players, key=lambda p: p.pc)
    poorest_player.pc += 15
    state.add_log(f"{poorest_player.name}, with the lowest PC, gains 15 PC from becoming a celebrity politician.")
    
    return state

def resolve_pass_turn(state: GameState, action: ActionPassTurn) -> GameState:
    """Simply advance to the next player's turn without any other effects."""
    player = state.get_player_by_id(action.player_id)
    if not player:
        return state
    
    state.add_log(f"{player.name} passes their turn.")
    # Force turn advancement by setting action points to -1
    state.action_points[player.id] = -1
    return state