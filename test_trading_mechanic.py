#!/usr/bin/env python3
"""
Test script for the trading mechanic during legislation sessions.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from engine.engine import GameEngine
from game_data import load_game_data
from engine.actions import ActionProposeTrade, ActionAcceptTrade, ActionDeclineTrade, ActionCompleteTrading
from engine.actions import ActionSponsorLegislation, ActionSupportLegislation, ActionOpposeLegislation

def test_trading_mechanic():
    """Test the complete trading mechanic flow."""
    print("🧪 Testing Trading Mechanic")
    print("=" * 50)
    
    # Load game data and create engine
    game_data = load_game_data()
    engine = GameEngine(game_data)
    
    # Start a new game with 3 players
    state = engine.start_new_game(["Alice", "Bob", "Charlie"])
    
    # Give players some resources for testing
    state.players[0].pc = 20  # Alice
    state.players[1].pc = 15  # Bob  
    state.players[2].pc = 25  # Charlie
    
    # Add some favors to players
    from models.components import PoliticalFavor
    favor1 = PoliticalFavor(id="FAVOR_1", description="Test Favor 1")
    favor2 = PoliticalFavor(id="FAVOR_2", description="Test Favor 2")
    state.players[0].favors.append(favor1)
    state.players[1].favors.append(favor2)
    
    print(f"Initial state:")
    print(f"Alice: {state.players[0].pc} PC, {len(state.players[0].favors)} favors")
    print(f"Bob: {state.players[1].pc} PC, {len(state.players[1].favors)} favors")
    print(f"Charlie: {state.players[2].pc} PC, {len(state.players[2].favors)} favors")
    print()
    
    # Simulate reaching the legislation session
    state.round_marker = 4
    state.current_phase = "LEGISLATION_PHASE"
    state.legislation_session_active = True
    state.current_trade_phase = True
    state.current_player_index = 0
    
    # Have Alice sponsor some legislation
    print("📜 Alice sponsors legislation...")
    legislation_action = ActionSponsorLegislation(player_id=0, legislation_id="INFRASTRUCTURE")
    state = engine.process_action(state, legislation_action)
    
    # Move to legislation session
    state = engine.run_legislation_session(state)
    
    print(f"Legislation session started: {state.current_trade_phase}")
    print(f"Current player: {state.get_current_player().name}")
    print()
    
    # Test 1: Alice proposes a trade to Bob
    print("🤝 Test 1: Alice proposes trade to Bob")
    trade_action = ActionProposeTrade(
        player_id=0,
        target_player_id=1,
        legislation_id="INFRASTRUCTURE",
        offered_pc=5,
        offered_favor_ids=["FAVOR_1"],
        requested_vote="support"
    )
    state = engine.process_action(state, action=trade_action)
    
    print(f"Trade offers: {len(state.active_trade_offers)}")
    print(f"Alice PC: {state.players[0].pc}")
    print(f"Alice favors: {len(state.players[0].favors)}")
    print()
    
    # Test 2: Bob accepts the trade
    print("✅ Test 2: Bob accepts the trade")
    state.current_player_index = 1  # Bob's turn
    accept_action = ActionAcceptTrade(player_id=1, trade_offer_id=0)
    state = engine.process_action(state, action=accept_action)
    
    print(f"Trade accepted: {state.active_trade_offers[0].accepted}")
    print(f"Alice PC: {state.players[0].pc}")
    print(f"Bob PC: {state.players[1].pc}")
    print(f"Alice favors: {len(state.players[0].favors)}")
    print(f"Bob favors: {len(state.players[1].favors)}")
    print()
    
    # Test 3: Charlie proposes a trade to Alice
    print("🤝 Test 3: Charlie proposes trade to Alice")
    state.current_player_index = 2  # Charlie's turn
    trade_action2 = ActionProposeTrade(
        player_id=2,
        target_player_id=0,
        legislation_id="INFRASTRUCTURE",
        offered_pc=10,
        offered_favor_ids=[],
        requested_vote="oppose"
    )
    state = engine.process_action(state, action=trade_action2)
    
    print(f"Trade offers: {len(state.active_trade_offers)}")
    print(f"Charlie PC: {state.players[2].pc}")
    print()
    
    # Test 4: Alice declines the trade
    print("❌ Test 4: Alice declines the trade")
    state.current_player_index = 0  # Alice's turn
    decline_action = ActionDeclineTrade(player_id=0, trade_offer_id=1)
    state = engine.process_action(state, action=decline_action)
    
    print(f"Trade declined: {state.active_trade_offers[1].declined}")
    print(f"Charlie PC: {state.players[2].pc} (should be unchanged)")
    print()
    
    # Test 5: Complete trading phase (Charlie's turn)
    print("🏁 Test 5: Complete trading phase")
    state.current_player_index = 2  # Charlie's turn
    complete_action = ActionCompleteTrading(player_id=2)
    state = engine.process_action(state, action=complete_action)
    
    print(f"Trading phase: {state.current_trade_phase}")
    print(f"Current player: {state.get_current_player().name}")
    print()
    
    # Test 6: Verify voting results from trades
    print("🗳️ Test 6: Verify voting results")
    for legislation in state.term_legislation:
        print(f"Legislation: {legislation.legislation_id}")
        print(f"Support: {legislation.support_players}")
        print(f"Oppose: {legislation.oppose_players}")
        print()
    
    # Test 7: Test invalid actions
    print("🚫 Test 7: Invalid actions")
    
    # Try to trade during voting phase
    state.current_trade_phase = False
    current_player = state.get_current_player()
    invalid_trade = ActionProposeTrade(
        player_id=current_player.id,
        target_player_id=2,
        legislation_id="INFRASTRUCTURE",
        offered_pc=5,
        offered_favor_ids=[],
        requested_vote="support"
    )
    old_state = state.deep_copy()
    state = engine.process_action(state, action=invalid_trade)
    
    if state == old_state:
        print("✅ Correctly prevented trading during voting phase")
    else:
        print("❌ Should have prevented trading during voting phase")
    
    # Try to trade with yourself
    state.current_trade_phase = True
    current_player = state.get_current_player()
    self_trade = ActionProposeTrade(
        player_id=current_player.id,
        target_player_id=current_player.id,
        legislation_id="INFRASTRUCTURE",
        offered_pc=5,
        offered_favor_ids=[],
        requested_vote="support"
    )
    old_state = state.deep_copy()
    state = engine.process_action(state, action=self_trade)
    
    if state == old_state:
        print("✅ Correctly prevented self-trading")
    else:
        print("❌ Should have prevented self-trading")
    
    print()
    print("🎉 Trading mechanic tests completed!")

if __name__ == "__main__":
    test_trading_mechanic() 