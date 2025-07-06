"""
This file contains the core logic resolvers for the game engine.
It is responsible for implementing the specific rules of actions, events,
and game phases.
"""
import random
from copy import deepcopy
from models.game_state import GameState
from models.cards import AllianceCard, EventCard, ScrutinyCard
from models.components import Player, Office
from engine.actions import (
    Action, ActionFundraise, ActionNetwork, ActionFormAlliance,
    ActionSponsorLegislation, ActionDeclareCandidacy
)

#--- Action Resolvers ---

def resolve_fundraise(state: GameState, action: ActionFundraise) -> GameState:
    player = state.get_player_by_id(action.player_id)
    if not player: return state

    # Check for stock crash effect
    if "STOCK_CRASH" in state.active_effects:
        player.pc -= 5
        state.add_log(f"{player.name} takes the Fundraise action but loses 5 PC due to the stock market crash.")
        return state

    pc_gain = 5
    if player.archetype.id == "FUNDRAISER":
        pc_gain += 2
        state.add_log(f"Archetype bonus: +2 PC for The Fundraiser.")
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
        player.favors.append(favor)
        state.add_log(f"{player.name} Networks, gaining 2 PC and a Political Favor: '{favor.description}'")
    else:
        state.add_log(f"{player.name} Networks, gaining 2 PC, but the favor supply is empty.")
    return state

def resolve_form_alliance(state: GameState, action: ActionFormAlliance) -> GameState:
    player = state.get_player_by_id(action.player_id)
    if not player: return state
    cost = 10
    if player.pc < cost:
        state.add_log(f"{player.name} does not have enough PC to form an alliance.")
        return state
    player.pc -= cost
    if state.alliance_deck.is_empty():
        state.add_log("The Alliance Deck is empty!")
        return state
    if player.allies:
        old_ally = player.allies.pop()
        state.add_log(f"{player.name} discards their former ally, {old_ally.title}.")
    new_ally_card = state.alliance_deck.draw()
    if new_ally_card and isinstance(new_ally_card, AllianceCard):
        player.allies.append(new_ally_card)
        state.add_log(f"{player.name} pays {cost} PC to form an alliance with {new_ally_card.title}.")
        state.add_log(f"  Effect: {new_ally_card.description}")
        if new_ally_card.weakness_description:
            state.add_log(f"  Weakness: {new_ally_card.weakness_description}")
    else:
        state.add_log("Failed to draw a valid ally card.")
    return state

def resolve_sponsor_legislation(state: GameState, action: ActionSponsorLegislation) -> GameState:
    player = state.get_player_by_id(action.player_id)
    if not player: return state
    bill = state.legislation_options[action.legislation_id]
    if player.pc < bill.cost:
        state.add_log(f"Not enough PC to sponsor {bill.title}.")
        return state
    player.pc -= bill.cost
    state.add_log(f"{player.name} pays {bill.cost} PC to sponsor the {bill.title}.")
    support_bonus = 0
    roll = random.randint(1, 6)
    
    # Apply war penalty if active
    war_penalty = -2 if "WAR_BREAKS_OUT" in state.active_effects else 0
    modified_roll = roll + support_bonus + war_penalty
    if war_penalty < 0:
        state.add_log(f"{player.name} rolls a {roll} (Modified: {modified_roll} due to war penalty).")
    else:
        state.add_log(f"{player.name} rolls a {roll} (Modified: {modified_roll}).")
    
    outcome = "Failure"
    if modified_roll >= bill.crit_target:
        outcome = "Critical Success"
        player.pc += bill.crit_reward
        state.public_mood = min(3, state.public_mood + bill.mood_change)
        state.add_log(f"Critical Success! {player.name} gains {bill.crit_reward} PC.")
    elif modified_roll >= bill.success_target:
        outcome = "Success"
        player.pc += bill.success_reward
        state.public_mood = min(3, state.public_mood + bill.mood_change)
        state.add_log(f"Success! {player.name} gains {bill.success_reward} PC.")
    else:
        player.pc -= bill.failure_penalty
        state.add_log(f"Failure! The bill fails. {player.name} loses an additional {bill.failure_penalty} PC.")
    passed = outcome in ["Success", "Critical Success"]
    state.last_sponsor_result = {'player_id': player.id, 'passed': passed}
    state.legislation_history.append({'sponsor_id': player.id, 'leg_id': bill.id, 'outcome': outcome})
    return state

def resolve_declare_candidacy(state: GameState, action: ActionDeclareCandidacy) -> GameState:
    from models.components import Candidacy
    player = state.get_player_by_id(action.player_id)
    if not player: return state
    office = state.offices[action.office_id]
    cost = office.candidacy_cost
    if player.pc < cost + action.committed_pc:
        state.add_log("Not enough PC to pay candidacy and commitment.")
        return state
    player.pc -= (cost + action.committed_pc)
    candidacy = Candidacy(player_id=player.id, office_id=action.office_id, committed_pc=action.committed_pc)
    state.secret_candidacies.append(candidacy)
    state.add_log(f"{player.name} pays {cost} PC to run for {office.title} and secretly commits additional funds.")
    return state

#--- Phase Resolvers ---

def resolve_upkeep(state: GameState) -> GameState:
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

    return state

def resolve_elections(state: GameState) -> GameState:
    offices_by_tier = sorted(state.offices.values(), key=lambda o: o.tier)
    
    # Check for voter apathy effect
    apathy_penalty = 0.5 if "VOTER_APATHY" in state.active_effects else 1.0
    if apathy_penalty < 1.0:
        state.add_log("Voter Apathy: Committed PC is only half as effective in this election.")
    
    for office in offices_by_tier:
        candidates = [c for c in state.secret_candidacies if c.office_id == office.id]
        if not candidates: continue
        state.add_log(f"\n--- Resolving Election for {office.title} ---")
        if len(candidates) == 1:
            player_cand = candidates[0]
            player = state.get_player_by_id(player_cand.player_id)
            if not player: continue
            player_roll = random.randint(1, 6)
            player_bonus = int((player_cand.committed_pc // 2) * apathy_penalty)
            player_score = player_roll + player_bonus
            state.add_log(f"{player.name} reveals {player_cand.committed_pc} committed PC.")
            state.add_log(f"{player.name}'s Score: {player_roll} (d6) + {player_bonus} (PC bonus) = {player_score}")
            npc_roll = random.randint(1, 6)
            npc_score = npc_roll + office.npc_challenger_bonus
            state.add_log(f"NPC Challenger's Score: {npc_roll} (d6) + {office.npc_challenger_bonus} (NPC bonus) = {npc_score}")
            if player_score >= npc_score:
                _award_office(state, player, office)
            else:
                state.add_log(f"{player.name} loses the election.")
        else:
            scores = []
            for cand in candidates:
                player = state.get_player_by_id(cand.player_id)
                if not player: continue
                roll = random.randint(1, 6)
                bonus = int((cand.committed_pc // 2) * apathy_penalty)
                score = roll + bonus
                scores.append({'player': player, 'score': score, 'committed_pc': cand.committed_pc})
                state.add_log(f"{player.name} reveals {cand.committed_pc} committed PC.")
                state.add_log(f"  {player.name}'s Score: {roll} (d6) + {bonus} (PC bonus) = {score}")
            highest_score = max(s['score'] for s in scores)
            winners = [s for s in scores if s['score'] == highest_score]
            if len(winners) == 1:
                winner = winners[0]['player']
            else:
                state.add_log("Tie in score! Checking committed PC...")
                max_pc = max(w['committed_pc'] for w in winners)
                pc_winners = [w for w in winners if w['committed_pc'] == max_pc]
                if len(pc_winners) == 1:
                    winner = pc_winners[0]['player']
                else:
                    state.add_log("Still tied! Re-rolling d6 until a winner emerges...")
                    winner = random.choice(pc_winners)['player']
            _award_office(state, winner, office)
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
    state.public_mood = min(3, state.public_mood + 2)
    for p in state.players:
        p.pc += 5
    state.add_log("Public Mood improves. All players gain 5 PC.")
    return state

def _event_recession_hits(state: GameState) -> GameState:
    state.public_mood = max(-3, state.public_mood - 2)
    for p in state.players:
        p.pc -= 5
    state.add_log("Public Mood worsens. All players lose 5 PC.")
    return state

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
    state.public_mood = min(3, state.public_mood + 1)
    state.active_effects.add("UNEXPECTED_SURPLUS")
    state.add_log("Public Mood improves. Incumbents will receive double income this round.")
    return state

def _event_last_bill_dud(state: GameState) -> GameState:
    state.public_mood = max(-3, state.public_mood - 1)
    state.add_log("Public Mood worsens.")
    
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
    state.public_mood = min(3, state.public_mood + 1)
    state.add_log("Public Mood improves.")
    
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
    state.public_mood = min(3, state.public_mood + 1)
    state.add_log("Public Mood improves due to technological advancement.")
    
    if not state.players: return state
    
    # Find player with least PC
    poorest_player = min(state.players, key=lambda p: p.pc)
    poorest_player.pc += 10
    state.add_log(f"{poorest_player.name}, with the least PC, gains 10 PC from the technological leap.")
    
    return state

def _event_natural_disaster(state: GameState) -> GameState:
    state.public_mood = max(-3, state.public_mood - 1)
    state.add_log("Public Mood worsens due to the natural disaster.")
    
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
    
    # Move Public Mood 2 spaces towards "Very Angry" (-2)
    state.public_mood = max(-3, state.public_mood - 2)
    state.add_log("Midterm Fury! Public Mood moves 2 spaces towards 'Very Angry'.")
    
    return state

def _event_stock_crash(state: GameState) -> GameState:
    state.public_mood = max(-3, state.public_mood - 3)
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