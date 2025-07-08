from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionFundraise, ActionNetwork, ActionSponsorLegislation, ActionDeclareCandidacy, ActionUseFavor, ActionSupportLegislation, ActionOpposeLegislation, ActionProposeTrade, ActionAcceptTrade, ActionDeclineTrade, ActionCompleteTrading, ActionCampaign, ActionPassTurn
import uuid
import os

app = Flask(__name__, static_folder='static')
CORS(app)  # Allow cross-origin requests for development

# Initialize the game engine
game_data = load_game_data()
engine = GameEngine(game_data)

# In-memory storage for active games (in production, use a database)
active_games = {}

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
                'resolved': leg.resolved,
                'trade_offers': [
                    {
                        'offerer_id': offer.offerer_id,
                        'target_id': offer.target_id,
                        'legislation_id': offer.legislation_id,
                        'offered_pc': offer.offered_pc,
                        'offered_favors': offer.offered_favors,
                        'requested_vote': offer.requested_vote,
                        'accepted': offer.accepted,
                        'declined': offer.declined
                    } for offer in leg.trade_offers
                ]
            } for leg in state.term_legislation
        ],
        'legislation_session_active': state.legislation_session_active,
        'current_trade_phase': state.current_trade_phase,
        'active_trade_offers': [
            {
                'offerer_id': offer.offerer_id,
                'target_id': offer.target_id,
                'legislation_id': offer.legislation_id,
                'offered_pc': offer.offered_pc,
                'offered_favors': offer.offered_favors,
                'requested_vote': offer.requested_vote,
                'accepted': offer.accepted,
                'declined': offer.declined
            } for offer in state.active_trade_offers
        ],
        'action_points': state.action_points,
        'campaign_influences': [
            {
                'player_id': influence.player_id,
                'office_id': influence.office_id,
                'influence_amount': influence.influence_amount
            } for influence in state.campaign_influences
        ],
        # Negative favor effects
        'political_debts': state.political_debts,
        'hot_potato_holder': state.hot_potato_holder,
        'public_gaffe_players': list(state.public_gaffe_players),
        'media_scrutiny_players': list(state.media_scrutiny_players),
        'compromised_players': list(state.compromised_players)
    }

@app.route('/api/game', methods=['POST'])
def create_game():
    """Create a new game."""
    data = request.get_json()
    player_names = data.get('player_names', [])
    
    if len(player_names) < 2 or len(player_names) > 4:
        return jsonify({'error': 'Game requires 2-4 players'}), 400
    
    # Create new game
    game_state = engine.start_new_game(player_names)
    game_id = str(uuid.uuid4())
    active_games[game_id] = game_state
    
    return jsonify({
        'game_id': game_id,
        'state': serialize_game_state(game_state)
    })

@app.route('/api/game/<game_id>', methods=['GET'])
def get_game_state(game_id):
    """Get the current state of a game."""
    if game_id not in active_games:
        return jsonify({'error': 'Game not found'}), 404
    
    state = active_games[game_id]
    
    # Check if all players have 0 AP and automatically advance (loop until not stuck)
    while (state.current_phase == 'ACTION_PHASE' and 
           not state.legislation_session_active and
           all(ap == 0 for ap in state.action_points.values())):
        dummy_action = ActionPassTurn(player_id=state.current_player_index)
        try:
            new_state = engine.process_action(state, dummy_action)
            active_games[game_id] = new_state
            state = new_state
        except Exception as e:
            break  # Stop if advancement fails
    
    return jsonify({
        'game_id': game_id,
        'state': serialize_game_state(state)
    })

@app.route('/api/game/<game_id>/action', methods=['POST'])
def process_action(game_id):
    """Process a player action."""
    if game_id not in active_games:
        return jsonify({'error': 'Game not found'}), 404
    
    state = active_games[game_id]
    data = request.get_json()
    
    action_type = data.get('action_type')
    player_id = data.get('player_id')
    
    # Create the appropriate action object
    action = None
    if action_type == 'fundraise':
        action = ActionFundraise(player_id=player_id)
    elif action_type == 'network':
        action = ActionNetwork(player_id=player_id)
    elif action_type == 'sponsor_legislation':
        legislation_id = data.get('legislation_id')
        action = ActionSponsorLegislation(player_id=player_id, legislation_id=legislation_id)

    elif action_type == 'declare_candidacy':
        office_id = data.get('office_id')
        committed_pc = data.get('committed_pc')
        action = ActionDeclareCandidacy(player_id=player_id, office_id=office_id, committed_pc=committed_pc)
    elif action_type == 'use_favor':
        favor_id = data.get('favor_id')
        target_player_id = data.get('target_player_id', -1)
        choice = data.get('choice', '')
        action = ActionUseFavor(player_id=player_id, favor_id=favor_id, target_player_id=target_player_id, choice=choice)
    elif action_type == 'support_legislation':
        legislation_id = data.get('legislation_id')
        support_amount = data.get('support_amount')
        action = ActionSupportLegislation(player_id=player_id, legislation_id=legislation_id, support_amount=support_amount)
    elif action_type == 'oppose_legislation':
        legislation_id = data.get('legislation_id')
        oppose_amount = data.get('oppose_amount')
        action = ActionOpposeLegislation(player_id=player_id, legislation_id=legislation_id, oppose_amount=oppose_amount)
    elif action_type == 'propose_trade':
        target_player_id = data.get('target_player_id')
        legislation_id = data.get('legislation_id')
        offered_pc = data.get('offered_pc', 0)
        offered_favor_ids = data.get('offered_favor_ids', [])
        requested_vote = data.get('requested_vote', 'support')
        action = ActionProposeTrade(
            player_id=player_id, 
            target_player_id=target_player_id, 
            legislation_id=legislation_id,
            offered_pc=offered_pc,
            offered_favor_ids=offered_favor_ids,
            requested_vote=requested_vote
        )
    elif action_type == 'accept_trade':
        trade_offer_id = data.get('trade_offer_id')
        action = ActionAcceptTrade(player_id=player_id, trade_offer_id=trade_offer_id)
    elif action_type == 'decline_trade':
        trade_offer_id = data.get('trade_offer_id')
        action = ActionDeclineTrade(player_id=player_id, trade_offer_id=trade_offer_id)
    elif action_type == 'complete_trading':
        action = ActionCompleteTrading(player_id=player_id)
    elif action_type == 'campaign':
        office_id = data.get('office_id')
        influence_amount = data.get('influence_amount')
        action = ActionCampaign(player_id=player_id, office_id=office_id, influence_amount=influence_amount)
    elif action_type == 'pass_turn':
        action = ActionPassTurn(player_id=player_id)
    else:
        return jsonify({'error': 'Invalid action type'}), 400
    
    try:
        # Process the action
        new_state = engine.process_action(state, action)
        active_games[game_id] = new_state
        
        return jsonify({
            'game_id': game_id,
            'state': serialize_game_state(new_state)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/game/<game_id>/event', methods=['POST'])
def run_event_phase(game_id):
    """Run the event phase (automated)."""
    if game_id not in active_games:
        return jsonify({'error': 'Game not found'}), 404
    
    state = active_games[game_id]
    
    try:
        new_state = engine.run_event_phase(state)
        active_games[game_id] = new_state
        
        return jsonify({
            'game_id': game_id,
            'state': serialize_game_state(new_state)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/game/<game_id>', methods=['DELETE'])
def delete_game(game_id):
    """Delete a game."""
    if game_id in active_games:
        del active_games[game_id]
    return jsonify({'message': 'Game deleted'})

@app.route('/api/test', methods=['GET'])
def test_api():
    """Test endpoint to verify API is working."""
    return jsonify({'message': 'API is working!', 'timestamp': '2025-07-07'})

@app.route('/')
def index():
    """Serve the main game page."""
    return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port) 