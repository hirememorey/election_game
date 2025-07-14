from models.game_state import GameState

def calculate_final_scores(state: GameState) -> dict[int, dict]:
    """
    Calculates the final scores for all players based on offices and mandates.
    """
    scores = {p.id: {'total_influence': 0, 'details': []} for p in state.players}

    # 1. Influence from Offices
    office_influence = {
        "PRESIDENT": 25,
        "US_SENATOR": 15,
        "GOVERNOR": 10,
        "STATE_SENATOR": 5,
        "CONGRESS_SEAT": 5, # Assuming Congress Seat is similar to State Senator
    }
    for p in state.players:
        if p.current_office:
            influence = office_influence.get(p.current_office.id, 0)
            if influence > 0:
                scores[p.id]['total_influence'] += influence
                scores[p.id]['details'].append(f"+{influence} Influence from holding office: {p.current_office.title}")

    # 2. Convert remaining PC to Influence
    pc_conversion_rate = 10  # 10 PC = 1 Influence
    for p in state.players:
        influence_from_pc = p.pc // pc_conversion_rate
        if influence_from_pc > 0:
            scores[p.id]['total_influence'] += influence_from_pc
            scores[p.id]['details'].append(f"+{influence_from_pc} Influence from {p.pc} PC remaining (1/{pc_conversion_rate} conversion)")

    # 3. Influence from Hidden Funder Mandates
    mandate_bonus = 15
    presidency_winner_id = -1

    for p in state.players:
        mandate_id = p.mandate.id
        completed = False
        
        # Check all mandate conditions
        if mandate_id == "WAR_HAWK":
            # Defense Contractors Union: Military Funding must pass with Critical Success
            for leg in state.legislation_history:
                if leg.get('legislation_id') == 'MILITARY' and leg.get('outcome') == 'Critical Success':
                    completed = True
                    break
        
        elif mandate_id == "ENVIRONMENTALIST":
            # Environmental Trust: Infrastructure must pass twice, player must sponsor one
            infrastructure_successes = 0
            player_sponsored = False
            for leg in state.legislation_history:
                if leg.get('legislation_id') == 'INFRASTRUCTURE' and leg.get('outcome') in ['Success', 'Critical Success']:
                    infrastructure_successes += 1
                    if leg.get('sponsor_id') == p.id:
                        player_sponsored = True
            if infrastructure_successes >= 2 and player_sponsored:
                completed = True
        
        elif mandate_id == "PEOPLES_CHAMPION":
            # People's Alliance: Public mood +2 or +3 at final election
            if state.public_mood >= 2:
                completed = True
        
        elif mandate_id == "KINGMAKER" and presidency_winner_id != -1:
            # Kingmaker's Pact: Support 2+ successful bills from presidency winner
            successful_supported_bills = 0
            for leg in state.legislation_history:
                if leg['sponsor_id'] == presidency_winner_id and leg['outcome'] in ["Success", "Critical Success"]:
                    if p.id in leg.get('support_players', {}):
                        successful_supported_bills += 1
            if successful_supported_bills >= 2:
                completed = True
        
        elif mandate_id == "UNPOPULAR_HERO":
            # Medical Advocacy Project: Pass Healthcare Overhaul
            for leg in state.legislation_history:
                if leg.get('legislation_id') == 'HEALTHCARE' and leg.get('outcome') in ['Success', 'Critical Success']:
                    completed = True
                    break
        
        elif mandate_id == "MINIMALIST":
            # Fiscal Watchdogs: Win presidency with 20 PC or less committed
            if p.current_office and p.current_office.id == "PRESIDENT":
                # This would need to track PC committed to final election
                # For now, assume it's completed if they're president
                completed = True
        
        elif mandate_id == "STATESMAN":
            # Governor's Association: Hold Governor or US Senator at game end
            if p.current_office and p.current_office.id in ["GOVERNOR", "US_SENATOR"]:
                completed = True
        
        elif mandate_id == "OPPORTUNIST":
            # Outsider's Collective: Win presidency without being incumbent before final election
            if p.current_office and p.current_office.id == "PRESIDENT":
                # This would need to track incumbent status history
                # For now, assume it's completed if they're president
                completed = True
        
        elif mandate_id == "MASTER_LEGISLATOR":
            # Policy Wonk's Institute: Sponsor and pass 3+ different types of legislation
            sponsored_successful_types = set()
            for leg in state.legislation_history:
                if leg.get('sponsor_id') == p.id and leg.get('outcome') in ['Success', 'Critical Success']:
                    sponsored_successful_types.add(leg.get('legislation_id', ''))
            if len(sponsored_successful_types) >= 3:
                completed = True
        
        elif mandate_id == "PRINCIPLED_LEADER":
            # Grassroots Movement: Win presidency without ever holding Governor office
            if p.current_office and p.current_office.id == "PRESIDENT":
                # This would need to track office history
                # For now, assume it's completed if they're president
                completed = True

        if completed:
            scores[p.id]['total_influence'] += mandate_bonus
            scores[p.id]['details'].append(f"+{mandate_bonus} Influence from Hidden Funder: {p.mandate.title}")

    return scores 