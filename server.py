"""
Core Game Logic Module
This module contains the core game logic and state management functions
that were previously part of the Flask server.
"""

import json
from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionFundraise, ActionNetwork, ActionSponsorLegislation, ActionDeclareCandidacy, ActionUseFavor, ActionSupportLegislation, ActionOpposeLegislation, ActionProposeTrade, ActionAcceptTrade, ActionDeclineTrade, ActionCompleteTrading, ActionPassTurn
import uuid

# Initialize the game engine
game_data = load_game_data()
engine = GameEngine(game_data)

# In-memory storage for active games (in production, use a database)
active_games = {}

# NEW: Secret commitment storage for the Secret Commitment System
# Structure: {game_id: {legislation_id: [(player_id, stance, amount), ...]}}
SECRET_COMMITMENTS = {}

def serialize_game_state(state):
    """Convert GameState to JSON-serializable format."""
    return {
        'players': [
            {
                'id': p.id,
                'name': p.name,
                'archetype': {
                    'id': p.archetype.id,
                    'title': p.archetype.title,
                    'description': p.archetype.description
                },
                'mandate': {
                    'id': p.mandate.id,
                    'title': p.mandate.title,
                    'description': p.mandate.description
                },
                'pc': p.pc,
                'current_office': {
                    'id': p.current_office.id,
                    'title': p.current_office.title,
                    'tier': p.current_office.tier,
                    'income': p.current_office.income
                } if p.current_office else None,
                'allies': [
                    {
                        'id': ally.id,
                        'title': ally.title,
                        'description': ally.description,
                        'upkeep_cost': ally.upkeep_cost,
                        'weakness_description': ally.weakness_description
                    } for ally in p.allies
                ],
                'favors': [
                    {
                        'id': favor.id,
                        'description': favor.description
                    } for favor in p.favors
                ]
            } for p in state.players
        ],
        'offices': {
            office_id: {
                'id': office.id,
                'title': office.title,
                'tier': office.tier,
                'candidacy_cost': office.candidacy_cost,
                'income': office.income,
                'npc_challenger_bonus': office.npc_challenger_bonus
            } for office_id, office in state.offices.items()
        },
        'legislation_options': {
            leg_id: {
                'id': leg.id,
                'title': leg.title,
                'cost': leg.cost,
                'success_target': leg.success_target,
                'crit_target': leg.crit_target,
                'success_reward': leg.success_reward,
                'crit_reward': leg.crit_reward,
                'failure_penalty': leg.failure_penalty,
                'mood_change': leg.mood_change
            } for leg_id, leg in state.legislation_options.items()
        },
        'round_marker': state.round_marker,
        'public_mood': state.public_mood,
        'current_player_index': state.current_player_index,
        'current_phase': state.current_phase,
        'turn_log': state.turn_log,
        'secret_candidacies': [
            {
                'player_id': c.player_id,
                'office_id': c.office_id,
                'committed_pc': c.committed_pc
            } for c in state.secret_candidacies
        ],
        'active_effects': list(state.active_effects),
        'last_sponsor_result': state.last_sponsor_result,
        'legislation_history': state.legislation_history,
        'pending_legislation': {
            'legislation_id': state.pending_legislation.legislation_id,
            'sponsor_id': state.pending_legislation.sponsor_id,
            'support_players': state.pending_legislation.support_players,
            'oppose_players': state.pending_legislation.oppose_players,
            'resolved': state.pending_legislation.resolved
        } if state.pending_legislation else None,
        'term_legislation': [
            {
                'legislation_id': leg.legislation_id,
                'sponsor_id': leg.sponsor_id,
                'support_players': leg.support_players,
                'oppose_players': leg.oppose_players,
                'resolved': leg.resolved
            } for leg in state.term_legislation
        ],
        'action_points': state.action_points,
        # Negative favor effects
        'political_debts': state.political_debts,
        'hot_potato_holder': state.hot_potato_holder,
        'public_gaffe_players': list(state.public_gaffe_players),
        'media_scrutiny_players': list(state.media_scrutiny_players),
        'compromised_players': list(state.compromised_players),
        # --- NEW: Manual phase resolution flags ---
        'awaiting_legislation_resolution': state.awaiting_legislation_resolution,
        'awaiting_election_resolution': state.awaiting_election_resolution,
        'awaiting_results_acknowledgement': state.awaiting_results_acknowledgement,
        'last_election_results': state.last_election_results
    }

def create_game(player_names):
    """Create a new game."""
    if len(player_names) < 2 or len(player_names) > 4:
        raise ValueError('Game requires 2-4 players')
    
    # Create new game
    game_state = engine.start_new_game(player_names)
    # Run the first event phase immediately
    game_state = engine.run_event_phase(game_state)
    game_id = str(uuid.uuid4())
    active_games[game_id] = game_state
    
    return game_id, serialize_game_state(game_state)

def get_game_state(game_id):
    """Get the current state of a game."""
    if game_id not in active_games:
        raise ValueError('Game not found')
    
    state = active_games[game_id]
    return serialize_game_state(state)

def process_action(game_id, action_data):
    """Process a player action."""
    if game_id not in active_games:
        raise ValueError('Game not found')
    
    state = active_games[game_id]
    action_type = action_data.get('action_type')
    player_id = action_data.get('player_id')
    
    # Create the appropriate action object
    action = None
    if action_type == 'fundraise':
        action = ActionFundraise(player_id=player_id)
    elif action_type == 'network':
        action = ActionNetwork(player_id=player_id)
    elif action_type == 'sponsor_legislation':
        legislation_id = action_data.get('legislation_id')
        action = ActionSponsorLegislation(player_id=player_id, legislation_id=legislation_id)
    elif action_type == 'declare_candidacy':
        office_id = action_data.get('office_id')
        committed_pc = action_data.get('committed_pc')
        action = ActionDeclareCandidacy(player_id=player_id, office_id=office_id, committed_pc=committed_pc)
    elif action_type == 'use_favor':
        favor_id = action_data.get('favor_id')
        target_player_id = action_data.get('target_player_id', -1)
        choice = action_data.get('choice', '')
        action = ActionUseFavor(player_id=player_id, favor_id=favor_id, target_player_id=target_player_id, choice=choice)
    elif action_type == 'support_legislation':
        legislation_id = action_data.get('legislation_id')
        support_amount = action_data.get('support_amount')
        
        # NEW: Store secret commitment instead of updating public state
        if game_id not in SECRET_COMMITMENTS:
            SECRET_COMMITMENTS[game_id] = {}
        if legislation_id not in SECRET_COMMITMENTS[game_id]:
            SECRET_COMMITMENTS[game_id][legislation_id] = []
        
        # Prevent multiple support/oppose commitments by the same player for the same bill
        already_committed = any(
            entry[0] == player_id and entry[1] == 'support'
            for entry in SECRET_COMMITMENTS[game_id][legislation_id]
        )
        if already_committed:
            raise ValueError('You have already committed support for this bill.')
        
        # Check if player has enough PC
        player = state.get_player_by_id(player_id)
        if not player:
            raise ValueError('Player not found')
        
        if player.pc < support_amount:
            raise ValueError(f'Not enough PC. You have {player.pc}, need {support_amount}')
        
        # Deduct PC immediately
        player.pc -= support_amount
        
        # Store the secret commitment
        SECRET_COMMITMENTS[game_id][legislation_id].append((player_id, 'support', support_amount))
        
        # Create action for engine processing (will consume AP)
        action = ActionSupportLegislation(player_id=player_id, legislation_id=legislation_id, support_amount=support_amount)
        
    elif action_type == 'oppose_legislation':
        legislation_id = action_data.get('legislation_id')
        oppose_amount = action_data.get('oppose_amount')
        
        # NEW: Store secret commitment instead of updating public state
        if game_id not in SECRET_COMMITMENTS:
            SECRET_COMMITMENTS[game_id] = {}
        if legislation_id not in SECRET_COMMITMENTS[game_id]:
            SECRET_COMMITMENTS[game_id][legislation_id] = []
        
        # Prevent multiple support/oppose commitments by the same player for the same bill
        already_committed = any(
            entry[0] == player_id and entry[1] == 'oppose'
            for entry in SECRET_COMMITMENTS[game_id][legislation_id]
        )
        if already_committed:
            raise ValueError('You have already committed opposition for this bill.')
        
        # Check if player has enough PC
        player = state.get_player_by_id(player_id)
        if not player:
            raise ValueError('Player not found')
        
        if player.pc < oppose_amount:
            raise ValueError(f'Not enough PC. You have {player.pc}, need {oppose_amount}')
        
        # Deduct PC immediately
        player.pc -= oppose_amount
        
        # Store the secret commitment
        SECRET_COMMITMENTS[game_id][legislation_id].append((player_id, 'oppose', oppose_amount))
        
        # Create action for engine processing (will consume AP)
        action = ActionOpposeLegislation(player_id=player_id, legislation_id=legislation_id, oppose_amount=oppose_amount)
    elif action_type == 'propose_trade':
        target_player_id = action_data.get('target_player_id')
        legislation_id = action_data.get('legislation_id')
        offered_pc = action_data.get('offered_pc', 0)
        offered_favor_ids = action_data.get('offered_favor_ids', [])
        requested_vote = action_data.get('requested_vote', 'support')
        action = ActionProposeTrade(
            player_id=player_id, 
            target_player_id=target_player_id, 
            legislation_id=legislation_id,
            offered_pc=offered_pc,
            offered_favor_ids=offered_favor_ids,
            requested_vote=requested_vote
        )
    elif action_type == 'accept_trade':
        trade_offer_id = action_data.get('trade_offer_id')
        action = ActionAcceptTrade(player_id=player_id, trade_offer_id=trade_offer_id)
    elif action_type == 'decline_trade':
        trade_offer_id = action_data.get('trade_offer_id')
        action = ActionDeclineTrade(player_id=player_id, trade_offer_id=trade_offer_id)
    elif action_type == 'complete_trading':
        action = ActionCompleteTrading(player_id=player_id)
    elif action_type == 'pass_turn':
        action = ActionPassTurn(player_id=player_id)
    else:
        raise ValueError('Invalid action type')
    
    # Process all actions through the engine to ensure AP validation
    new_state = engine.process_action(state, action)
    active_games[game_id] = new_state
    
    return serialize_game_state(new_state)

def run_event_phase(game_id):
    """Run the event phase (automated)."""
    if game_id not in active_games:
        raise ValueError('Game not found')
    
    state = active_games[game_id]
    new_state = engine.run_event_phase(state)
    active_games[game_id] = new_state
    
    return serialize_game_state(new_state)

def resolve_legislation(game_id):
    """Manually resolve all pending legislation at the end of the term."""
    if game_id not in active_games:
        raise ValueError('Game not found')
    
    state = active_games[game_id]
    
    # NEW: Use secret commitments for legislation resolution
    if game_id in SECRET_COMMITMENTS:
        # Pass the secret commitments to the engine for resolution
        new_state = engine.resolve_legislation_session_with_secrets(state, SECRET_COMMITMENTS[game_id])
        # Clear the secret commitments after resolution
        del SECRET_COMMITMENTS[game_id]
    else:
        # Fallback to old system if no secret commitments
        new_state = engine.resolve_legislation_session(state)
    
    active_games[game_id] = new_state
    return serialize_game_state(new_state)

def resolve_elections(game_id):
    """Manually resolve all elections after legislation session."""
    if game_id not in active_games:
        raise ValueError('Game not found')
    
    state = active_games[game_id]
    # Ensure dice rolls are enabled for CLI version (disable_dice_roll=False)
    new_state = engine.resolve_elections_session(state, disable_dice_roll=False)
    active_games[game_id] = new_state
    
    return serialize_game_state(new_state)

def acknowledge_results(game_id):
    """Acknowledge the results of an election or legislation to proceed."""
    if game_id not in active_games:
        raise ValueError('Game not found')
    
    state = active_games[game_id]
    
    if not state.awaiting_results_acknowledgement:
        raise ValueError('No results to acknowledge.')
        
    state.awaiting_results_acknowledgement = False
    
    # After acknowledgement, start the next term
    new_state = engine.start_next_term(state)
    
    active_games[game_id] = new_state
    return serialize_game_state(new_state)

def delete_game(game_id):
    """Delete a game."""
    if game_id in active_games:
        del active_games[game_id]
    return True 