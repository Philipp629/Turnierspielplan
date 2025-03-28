import pytest
from tournament_scheduler import (
    add_player, 
    generate_round_robin_pairs, 
    create_schedule, 
    record_result, 
    get_match_result, 
    get_player_matches, 
    get_player_statistics,
    match_results,
    current_schedule
)
from collections import defaultdict

@pytest.fixture(autouse=True)
def reset_globals():
    match_results.clear()
    global current_schedule
    current_schedule = []

def test_maximum_10_players():
    max_players = 10
    players = ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10"]
    assert add_player(players, max_players).success == False

def test_errormessage_maximum_10_players():
    max_players = 10
    players = ["P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8", "P9", "P10"]
    assert add_player(players, max_players).message == f"Maximale Anzahl von {max_players} Spielern erreicht!"

def test_3_players_3_pairs():
    players = ["Philipp", "Ben", "Daniel"]
    pairs = generate_round_robin_pairs(players)
    assert len(pairs) == 3
    schedule = create_schedule(pairs, players)
    assert len(schedule) == 3

def test_4_players_6_pairs():
    players = ["Philipp", "Ben", "Daniel", "Tisch"]
    pairs = generate_round_robin_pairs(players)
    assert len(pairs) == 6
    schedule = create_schedule(pairs, players)
    assert len(schedule) == 6

def test_each_player_plays_each_once():
    players = ["Philipp", "Ben", "Daniel", "Tisch"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    scheduled_pairs = set(frozenset(pair) for round in schedule for pair in round)
    expected_pairs = set(frozenset(pair) for pair in pairs)
    assert scheduled_pairs == expected_pairs

def test_no_parallel_games():
    players = ["Philipp", "Ben", "Daniel", "Tisch"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    for round_num, round_games in enumerate(schedule):
        assert len(round_games) == 1, f"Runde {round_num} hat {len(round_games)} Spiele, erwartet genau 1"

def test_balanced_pauses():
    players = ["Philipp", "Ben", "Daniel", "Tisch"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    
    matches_per_round = defaultdict(list)
    for round_num, round_games in enumerate(schedule):
        for p1, p2 in round_games:
            matches_per_round[p1].append(round_num)
            matches_per_round[p2].append(round_num)
    
    for player, rounds in matches_per_round.items():
        if len(rounds) > 1:
            gaps = [rounds[i+1] - rounds[i] for i in range(len(rounds)-1)]
            avg_gap = sum(gaps) / len(gaps)
            assert all(abs(gap - avg_gap) <= 1 for gap in gaps), f"{player} hat unausgeglichene Pausen: {gaps}"

def test_shortest_possible_duration():
    players_3 = ["Philipp", "Ben", "Daniel"]
    pairs_3 = generate_round_robin_pairs(players_3)
    schedule_3 = create_schedule(pairs_3, players_3)
    expected_rounds_3 = (len(players_3) * (len(players_3) - 1)) // 2
    assert len(schedule_3) == expected_rounds_3, f"Erwartete {expected_rounds_3} Runden, bekam {len(schedule_3)}"

    players_4 = ["Philipp", "Ben", "Daniel", "Tisch"]
    pairs_4 = generate_round_robin_pairs(players_4)
    schedule_4 = create_schedule(pairs_4, players_4)
    expected_rounds_4 = (len(players_4) * (len(players_4) - 1)) // 2
    assert len(schedule_4) == expected_rounds_4, f"Erwartete {expected_rounds_4} Runden, bekam {len(schedule_4)}"

def test_record_result_basic():
    players = ["Philipp", "Ben", "Daniel"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    record_result("Philipp", "Ben", "6:4, 6:3")
    assert get_match_result("Philipp", "Ben") == "6:4, 6:3"

def test_no_duplicate_results():
    players = ["Philipp", "Ben", "Daniel"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    record_result("Philipp", "Ben", "6:4, 6:3")
    with pytest.raises(ValueError, match="Ergebnis für dieses Spiel wurde bereits eingetragen"):
        record_result("Philipp", "Ben", "7:6, 6:4")

def test_valid_score_format():
    players = ["Philipp", "Ben", "Daniel"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    record_result("Philipp", "Ben", "6:4, 6:3")
    with pytest.raises(ValueError, match="Ungültiges Ergebnisformat"):
        record_result("Philipp", "Daniel", "6-4, 6-3")
    with pytest.raises(ValueError, match="Ungültiges Ergebnisformat"):
        record_result("Ben", "Daniel", "abc")

def test_match_in_schedule():
    players = ["Philipp", "Ben", "Daniel"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    with pytest.raises(ValueError, match="Spiel ist nicht im Spielplan enthalten"):
        record_result("Philipp", "Max", "6:4, 6:3")

def test_clear_winner():
    players = ["Philipp", "Ben", "Daniel"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    record_result("Philipp", "Ben", "6:4, 4:6, 6:4")
    with pytest.raises(ValueError, match="Kein eindeutiger Gewinner bestimmbar"):
        record_result("Philipp", "Daniel", "6:4, 4:6")

def test_get_match_result():
    players = ["Philipp", "Ben", "Daniel"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    record_result("Philipp", "Ben", "6:4, 6:3")
    assert get_match_result("Philipp", "Ben") == "6:4, 6:3"
    assert get_match_result("Philipp", "Daniel") is None

def test_get_player_matches():
    players = ["Philipp", "Ben", "Daniel"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    record_result("Philipp", "Ben", "6:4, 6:3")
    record_result("Philipp", "Daniel", "7:6, 4:6, 6:4")
    matches = get_player_matches("Philipp")
    assert len(matches) == 2
    assert {"opponent": "Ben", "result": "6:4, 6:3"} in matches
    assert {"opponent": "Daniel", "result": "7:6, 4:6, 6:4"} in matches

def test_get_player_statistics():
    players = ["Philipp", "Ben", "Daniel"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    record_result("Philipp", "Ben", "6:4, 6:3")  # Philipp gewinnt
    record_result("Philipp", "Daniel", "7:6, 4:6, 6:4")  # Philipp gewinnt
    record_result("Ben", "Daniel", "6:4, 4:6, 6:3")  # Ben gewinnt
    stats = get_player_statistics("Philipp")
    assert stats["wins"] == 2
    assert stats["losses"] == 0
    assert stats["sets_won"] == 4
    assert stats["sets_lost"] == 1