import pytest
from tournament_scheduler import (
    add_player, 
    generate_round_robin_pairs, 
    create_schedule, 
    record_result, 
    get_match_result, 
    get_player_matches, 
    get_player_statistics,
    calculate_standings,
    get_player_ranking,
    get_complete_ranking,
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

def test_point_system_basic():
    players = ["Anna", "Max", "Tom"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    record_result("Anna", "Max", "6:4, 6:3")  # Anna gewinnt
    record_result("Anna", "Tom", "6:2, 6:4")  # Anna gewinnt
    record_result("Max", "Tom", "6:4, 4:6, 6:3")  # Max gewinnt
    stats_anna = get_player_statistics("Anna")
    stats_max = get_player_statistics("Max")
    stats_tom = get_player_statistics("Tom")
    assert stats_anna["wins"] == 2 and stats_anna["losses"] == 0
    assert stats_max["wins"] == 1 and stats_max["losses"] == 1
    assert stats_tom["wins"] == 0 and stats_tom["losses"] == 2

def test_calculate_standings_basic():
    players = ["Anna", "Max", "Tom"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    record_result("Anna", "Max", "6:4, 6:3")  # Anna gewinnt
    record_result("Anna", "Tom", "6:2, 6:4")  # Anna gewinnt
    record_result("Max", "Tom", "6:4, 4:6, 6:3")  # Max gewinnt
    standings = calculate_standings(players)
    assert standings[0]["player"] == "Anna" and standings[0]["points"] == 2
    assert standings[1]["player"] == "Max" and standings[1]["points"] == 1
    assert standings[2]["player"] == "Tom" and standings[2]["points"] == 0

def test_get_player_ranking():
    players = ["Anna", "Max", "Tom"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    record_result("Anna", "Max", "6:4, 6:3")  # Anna gewinnt
    record_result("Anna", "Tom", "6:2, 6:4")  # Anna gewinnt
    record_result("Max", "Tom", "6:4, 4:6, 6:3")  # Max gewinnt
    assert get_player_ranking("Anna") == 1
    assert get_player_ranking("Max") == 2
    assert get_player_ranking("Tom") == 3

def test_get_complete_ranking():
    players = ["Anna", "Max", "Tom"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    record_result("Anna", "Max", "6:4, 6:3")  # Anna gewinnt
    record_result("Anna", "Tom", "6:2, 6:4")  # Anna gewinnt
    record_result("Max", "Tom", "6:4, 4:6, 6:3")  # Max gewinnt
    ranking = get_complete_ranking()
    assert len(ranking) == 3
    assert ranking[0]["player"] == "Anna" and ranking[0]["matches_won"] == 2
    assert ranking[1]["player"] == "Max" and ranking[1]["matches_won"] == 1
    assert ranking[2]["player"] == "Tom" and ranking[2]["matches_won"] == 0

def test_extended_player_statistics():
    players = ["Anna", "Max"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    record_result("Anna", "Max", "6:4, 6:7, 7:6")  # Anna gewinnt mit Tie-Break
    stats_anna = get_player_statistics("Anna")
    assert stats_anna["wins"] == 1
    assert stats_anna["sets_won"] == 2
    assert stats_anna["sets_lost"] == 1
    assert stats_anna["games_won"] == 19  # 6 + 6 + 7
    assert stats_anna["games_lost"] == 17  # 4 + 7 + 6
    assert stats_anna["tiebreaks_won"] == 1
    assert stats_anna["tiebreaks_lost"] == 1

def test_ranking_tie_direct_match():
    players = ["Anna", "Max", "Tom"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    record_result("Anna", "Max", "6:4, 6:3")  # Anna gewinnt
    record_result("Tom", "Anna", "6:4, 6:3")  # Tom gewinnt
    record_result("Max", "Tom", "6:4, 6:3")  # Max gewinnt
    # Alle haben 1 Sieg
    standings = calculate_standings(players)
    assert standings[0]["player"] == "Anna"  # Anna schlägt Max
    assert standings[1]["player"] == "Max"   # Max schlägt Tom
    assert standings[2]["player"] == "Tom"   # Tom schlägt Anna

def test_ranking_tie_set_ratio():
    players = ["Anna", "Max", "Tom", "Lisa"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    record_result("Lisa", "Max", "6:4, 6:3")      # Lisa: 2-0 Sätze
    record_result("Lisa", "Tom", "6:2, 6:4")      # Lisa: 2-0 Sätze
    record_result("Max", "Tom", "6:4, 4:6, 6:3")  # Max: 2-1 Sätze
    record_result("Anna", "Lisa", "6:4, 6:3")     # Lisa: 2-0 Sätze
    record_result("Anna", "Max", "6:4, 6:3")      # Lisa: 2-0 Sätze
    record_result("Tom", "Anna", "6:4, 6:3")      # Tom: 2-0 Sätze
    standings = calculate_standings(players)
    assert standings[0]["player"] == "Anna"  # 2 Siege, schlägt Anna
    assert standings[1]["player"] == "Lisa"  # 2 Siege, verlor gegen Lisa