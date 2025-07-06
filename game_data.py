"""
This file contains all the static game data, loaded from the rulebook appendices.
It defines all the cards, offices, and other components that make up the game.
"""
from models.cards import (
    PoliticalArchetype, PersonalMandate, EventCard, 
    ScrutinyCard, AllianceCard
)
from models.components import Office, Legislation, PoliticalFavor

def load_game_data():
    """
    Initializes and returns a dictionary containing all the static data
    for a new game of Election.
    """
    return {
        "offices": load_offices(),
        "archetypes": load_archetypes(),
        "mandates": load_personal_mandates(),
        "events": load_event_deck(),
        "scrutiny": load_scrutiny_deck(),
        "alliances": load_alliance_deck(),
        "favors": load_political_favors(),
        "legislation": load_legislation(),
    }

# Appendix A: The Offices of Power
def load_offices():
    return {
        "STATE_SENATOR": Office(id="STATE_SENATOR", title="State Senator", tier=1, candidacy_cost=10, income=5, npc_challenger_bonus=0),
        "CONGRESS_SEAT": Office(id="CONGRESS_SEAT", title="Congress Seat", tier=1, candidacy_cost=15, income=7, npc_challenger_bonus=1),
        "GOVERNOR": Office(id="GOVERNOR", title="Governor", tier=2, candidacy_cost=25, income=12, npc_challenger_bonus=2),
        "US_SENATOR": Office(id="US_SENATOR", title="US Senator", tier=2, candidacy_cost=30, income=15, npc_challenger_bonus=3),
        "PRESIDENT": Office(id="PRESIDENT", title="President", tier=3, candidacy_cost=50, income=0, npc_challenger_bonus=4),
    }

# Appendix B: Political Archetypes
def load_archetypes():
    return [
        PoliticalArchetype(id="INSIDER", title="The Insider", description="Start with a State Senator office, but only 15 PC."),
        PoliticalArchetype(id="POPULIST", title="The Populist", description="When you gain PC from negative Public Mood as an Outsider, gain 1 additional PC."),
        PoliticalArchetype(id="FUNDRAISER", title="The Fundraiser", description="Your first Fundraise action each Term grants an additional 2 PC."),
        PoliticalArchetype(id="ORATOR", title="The Orator", description="Once per Term, you may re-roll one failed legislation die roll."),
    ]

# Appendix C: Personal Mandates
def load_personal_mandates():
    return [
        PersonalMandate(id="PRINCIPLED_LEADER", title="The Principled Leader", description="Win the Presidency without ever having held a Governor office."),
        PersonalMandate(id="ENVIRONMENTALIST", title="The Environmentalist", description="Ensure the Infrastructure Bill is successfully passed at least twice, and that you personally sponsored one of them."),
        PersonalMandate(id="WAR_HAWK", title="The War Hawk", description="Ensure the Military Funding bill is passed with a Critical Success."),
        PersonalMandate(id="KINGMAKER", title="The Kingmaker", description="Be allied with the player who wins the Presidency when the game ends."),
        PersonalMandate(id="MASTER_LEGISLATOR", title="The Master Legislator", description="Personally sponsor and pass at least 3 different types of legislation."),
        PersonalMandate(id="STATESMAN", title="The Statesman", description="At game end, hold a Governor or US Senator office."),
        PersonalMandate(id="SHADOW_DONOR", title="The Shadow Donor", description="Ensure a player you supported (via Co-Sponsorship) wins the Presidency."),
        PersonalMandate(id="UNPOPULAR_HERO", title="The Unpopular Hero", description="Pass the Healthcare Overhaul legislation."),
        PersonalMandate(id="MINIMALIST", title="The Minimalist", description="Win the Presidency having committed 20 PC or less to the final election."),
        PersonalMandate(id="DIPLOMAT", title="The Diplomat", description="Successfully use a Pledge token in a deal with every other player."),
        PersonalMandate(id="PEOPLES_CHAMPION", title="The People's Champion", description="Ensure the Public Mood is +2 or +3 when the final Presidential election occurs."),
        PersonalMandate(id="OPPORTUNIST", title="The Opportunist", description="Win the Presidency without ever having been an Incumbent before the final Election Phase."),
    ]

# Appendix D.1: Event Deck
def load_event_deck():
    return [
        EventCard(id="ECONOMIC_BOOM", title="Economic Boom", description="Move Public Mood +2 spaces. All players gain 5 PC.", effect_id="ECONOMIC_BOOM"),
        EventCard(id="RECESSION_HITS", title="Recession Hits", description="Move Public Mood -2 spaces. All players lose 5 PC.", effect_id="RECESSION_HITS"),
        EventCard(id="SCANDAL", title="Scandal!", description="The player with the most PC loses 15 PC and must immediately draw one card from the Scrutiny Deck.", effect_id="SCANDAL"),
        EventCard(id="FOREIGN_POLICY_CRISIS", title="Foreign Policy Crisis", description="A random player rolls a d6: 1-3: Lose 10 PC. 4-6: Gain 10 PC.", effect_id="FOREIGN_POLICY_CRISIS"),
        EventCard(id="SUPREME_COURT_VACANCY", title="Supreme Court Vacancy", description="Legacy Effect. The winner of the next Presidential election gains an additional 20 PC upon victory.", effect_id="SUPREME_COURT_VACANCY"),
        EventCard(id="LAST_BILL_HIT", title="Last Bill Was a Hit!", description="The last player to successfully sponsor legislation gains 10 PC. Move Public Mood +1.", effect_id="LAST_BILL_HIT"),
        EventCard(id="LAST_BILL_DUD", title="Last Bill Was a Dud!", description="The last player to successfully sponsor legislation loses 10 PC. Move Public Mood -1.", effect_id="LAST_BILL_DUD"),
        EventCard(id="BIPARTISAN_BREAKTHROUGH", title="Bipartisan Breakthrough", description="All players in Congress or Senate may immediately pay 5 PC to gain 10 PC.", effect_id="BIPARTISAN_BREAKTHROUGH"),
        EventCard(id="WAR_BREAKS_OUT", title="War Breaks Out", description="Public Mood is locked at its current position for the rest of the Term. Sponsoring any legislation is at -2 to the roll until the Term ends.", effect_id="WAR_BREAKS_OUT"),
        EventCard(id="TECH_LEAP", title="Technological Leap", description="Move Public Mood +1. The player with the least PC gains 10 PC.", effect_id="TECH_LEAP"),
        EventCard(id="NATURAL_DISASTER", title="Natural Disaster", description="Move Public Mood -1. A random Governor (or a random player if no Governors) must respond, losing 10 PC.", effect_id="NATURAL_DISASTER"),
        EventCard(id="MEDIA_DARLING", title="Media Darling", description="Choose one player. They gain 5 PC and are immune to the next 'Scandal!' event.", effect_id="MEDIA_DARLING"),
        EventCard(id="GAFFE", title="Gaffe on the Trail", description="Choose an opponent. They lose 8 PC.", effect_id="GAFFE"),
        EventCard(id="ENDORSEMENT", title="Surprise Endorsement", description="You (the player who drew this card) gain 10 PC.", effect_id="ENDORSEMENT"),
        EventCard(id="GRASSROOTS", title="Grassroots Movement", description="The player with the fewest held offices (0 is fewest) gains 10 PC.", effect_id="GRASSROOTS"),
        EventCard(id="VOTER_APATHY", title="Voter Apathy", description="Lingering Effect. For the next Election Phase, the PC committed by all players is only half as effective.", effect_id="VOTER_APATHY"),
        EventCard(id="MIDTERM_FURY", title="Midterm Fury", description="Timing. Draw only in Round 2 or 3 of a Term. Public Mood moves 2 spaces towards 'Very Angry'.", effect_id="MIDTERM_FURY"),
        EventCard(id="UNEXPECTED_SURPLUS", title="Unexpected Surplus", description="Move Public Mood +1. All office-holders collect double their income this Upkeep phase.", effect_id="UNEXPECTED_SURPLUS"),
        EventCard(id="STOCK_CRASH", title="Stock Market Crash", description="Move Public Mood -3 spaces. Any player who chose to 'Fundraise' this round loses 5 PC instead of gaining it.", effect_id="STOCK_CRASH"),
        EventCard(id="CELEB_POLITICIAN", title="Celebrity Politician", description="The player with the lowest PC gains 15 PC.", effect_id="CELEB_POLITICIAN"),
    ]

# Appendix D.2: Scrutiny Deck
def load_scrutiny_deck():
    return [
        ScrutinyCard(id="GAFFE_INVESTIGATION", title="Gaffe Investigation", description="A past mistake surfaces. Pay 10 PC.", effect_id="PAY_PC_10"),
        ScrutinyCard(id="FINANCE_AUDIT", title="Campaign Finance Audit", description="Your Fundraise action grants 0 PC next round.", effect_id="FINANCE_AUDIT"),
        ScrutinyCard(id="OLD_VOTE", title="Old Vote Haunts You", description="Your past policies are unpopular. Public Mood drops by 1.", effect_id="MOOD_MINUS_1"),
        ScrutinyCard(id="DONOR_SCANDAL", title="Minor Donor Scandal", description="You must return a questionable donation. Lose 8 PC.", effect_id="PAY_PC_8"),
        ScrutinyCard(id="NEGATIVE_PRESS", title="Negative Press Cycle", description="You are bombarded by bad press. Lose 5 PC and you cannot Network next round.", effect_id="NEGATIVE_PRESS"),
        ScrutinyCard(id="UNPOPULAR_STANCE", title="Unpopular Stance", description="Your position on a key issue backfires. Lose 7 PC.", effect_id="PAY_PC_7"),
        ScrutinyCard(id="GAFFE_INVESTIGATION_2", title="Gaffe Investigation", description="A past mistake surfaces. Pay 10 PC.", effect_id="PAY_PC_10"),
        ScrutinyCard(id="DONOR_SCANDAL_2", title="Minor Donor Scandal", description="You must return a questionable donation. Lose 8 PC.", effect_id="PAY_PC_8"),
        ScrutinyCard(id="OLD_VOTE_2", title="Old Vote Haunts You", description="Your past policies are unpopular. Public Mood drops by 1.", effect_id="MOOD_MINUS_1"),
        ScrutinyCard(id="INTERNAL_STRIFE", title="Internal Campaign Strife", description="Your team is in disarray. Lose 5 PC.", effect_id="PAY_PC_5"),
    ]

# Appendix D.3: Alliance Deck
def load_alliance_deck():
    return [
        AllianceCard(id="HEDGE_FUND_BRO", title="Steve McRoberts, The Hedge Fund Bro", description="When you take the Fundraise action, gain an additional 10 PC.", weakness_description="If an Event Card forces a random player to lose PC, you must be the target if you are an eligible choice."),
        AllianceCard(id="CAMPAIGN_MANAGER", title="Diane Westbrook, The Veteran Campaign Manager", description="Once per Election Phase, you may add a flat +1 to any single election roll (after rolling).", upkeep_cost=5),
        AllianceCard(id="SPIN_DOCTOR", title="Marcus Thorne, The Savvy Spin Doctor", description="The first time you would lose PC from the Public Mood track each round, ignore the loss.", weakness_description="You have a -1 penalty to your dice roll when sponsoring 'Protect The Children!'."),
        AllianceCard(id="GENERAL_JACKSON", title="General Hank 'Bulldog' Jackson", description="When you sponsor the Military Funding legislation, you automatically succeed (no roll needed).", weakness_description="Any time the Public Mood would improve due to an Event Card, it improves by 1 less space."),
        AllianceCard(id="UNION_BOSS", title="'Big' Sal Marconi, The Union Boss", description="Gain a +5 PC bonus when committing PC to an election for Governor or Congress.", weakness_description="Before the Election Phase begins, you must pay 10% of your current PC (rounded up) or discard this Ally."),
        AllianceCard(id="MASTER_POLLSTER", title="Katja Petrova, The Master Pollster", description="Once per Term (during Round 4), you may secretly look at the NPC Challenger's dice bonus for one office before anyone declares their candidacy.", weakness_description="Opponents only need to tie, not beat, your roll to win a contested election against you."),
        AllianceCard(id="GRASSROOTS_ACTIVIST", title="Celeste Imani, The Grassroots Activist", description="If your PC total is the lowest at the start of your turn, gain 5 PC.", weakness_description="You cannot use the Fundraise action."),
        AllianceCard(id="JUDGE_REED", title="Judge Evelyn Reed (Retired)", description="You are immune to the 'Gaffe on the Trail' and 'Scandal!' Event Cards.", weakness_description="You cannot sponsor 'Change the Tax Code' legislation."),
    ]

# Appendix E: Political Favor Tokens
def load_political_favors():
    return [
        PoliticalFavor(id="ELECTION_ROLL_BONUS", description="+1 to a single election roll (use before rolling)."),
        PoliticalFavor(id="FUNDRAISE_BONUS", description="+3 PC on your next Fundraise action."),
        PoliticalFavor(id="ALLY_UPKEEP_IGNORE", description="Ignore 2 PC of Ally Upkeep cost for one round."),
        PoliticalFavor(id="FORCE_REROLL", description="Force an opponent to re-roll one legislation die."),
        PoliticalFavor(id="PEEK_EVENT", description="Look at the top card of the Event Deck."),
    ]

# Appendix F: Legislation Reference
def load_legislation():
    return {
        "INFRASTRUCTURE": Legislation(id="INFRASTRUCTURE", title="Infrastructure Bill", cost=5, success_target=3, crit_target=5, success_reward=10, crit_reward=12, failure_penalty=0, mood_change=1),
        "CHILDREN": Legislation(id="CHILDREN", title="Protect The Children!", cost=5, success_target=2, crit_target=5, success_reward=8, crit_reward=10, failure_penalty=0, mood_change=1),
        "TAX_CODE": Legislation(id="TAX_CODE", title="Change the Tax Code", cost=10, success_target=4, crit_target=6, success_reward=20, crit_reward=25, failure_penalty=5),
        "MILITARY": Legislation(id="MILITARY", title="Military Funding", cost=8, success_target=4, crit_target=6, success_reward=12, crit_reward=15, failure_penalty=0),
        "HEALTHCARE": Legislation(id="HEALTHCARE", title="Healthcare Overhaul", cost=15, success_target=5, crit_target=6, success_reward=40, crit_reward=45, failure_penalty=10, mood_change=1),
    }