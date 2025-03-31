import pytest
from unittest.mock import patch
from tournament_scheduler import *

def setup_reset_globals():
    global match_results, current_schedule
    match_results.clear()
    current_schedule.clear()

def test_generate_pairs():
    players = ["Anna", "Max", "Tom"]
    pairs = generate_round_robin_pairs(players)
    assert len(pairs) == 3
    assert ("Anna", "Max") in pairs
    assert ("Anna", "Tom") in pairs
    assert ("Max", "Tom") in pairs

def test_create_schedule():
    players = ["Anna", "Max", "Tom"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    assert len(schedule) == 3
    assert all(len(round_games) == 1 for round_games in schedule)
    all_matches = [match for round_games in schedule for match in round_games]
    assert len(set(all_matches)) == 3

def test_add_player_success():
    players = []
    with patch('builtins.input', return_value="Anna"):
        result = add_player(players, 4)
        assert result.success
        assert "Anna" in players

def test_add_player_max_reached():
    players = ["Anna", "Max"]
    with patch('builtins.input', return_value="Tom"):
        result = add_player(players, 2)
        assert not result.success
        assert "Tom" not in players

def test_add_player_invalid_name():
    players = []
    with patch('builtins.input', side_effect=["A1", "Anna"]):
        result = add_player(players, 4)
        assert result.success
        assert "Anna" in players
        assert "A1" not in players

def test_record_result():
    setup_reset_globals()
    players = ["Anna", "Max"]
    pairs = generate_round_robin_pairs(players)
    create_schedule(pairs, players)
    record_result("Anna", "Max", "6:4, 6:3")
    assert get_match_result("Anna", "Max") == "6:4, 6:3"

def test_matrix_empty_tournament():
    setup_reset_globals()
    players = ["Anna", "Max", "Tom", "Lisa"]
    pairs = generate_round_robin_pairs(players)
    create_schedule(pairs, players)
    matrix = create_match_matrix(players)
    assert "Anna   |   X   |  vs   |  vs   |  vs   " in matrix  # Angepasst: zusätzliches Leerzeichen nach "Anna"

def test_matrix_with_results():
    setup_reset_globals()
    players = ["Anna", "Max", "Tom", "Lisa"]
    pairs = generate_round_robin_pairs(players)
    create_schedule(pairs, players)
    record_result("Anna", "Max", "6:3, 6:4")
    record_result("Anna", "Lisa", "6:2, 6:1")
    matrix = create_match_matrix(players)
    assert "Anna   |   X   |  6:3  |  vs   |  6:2  " in matrix  # Angepasst: zusätzliches Leerzeichen nach "Anna"

def test_player_statistics():
    setup_reset_globals()
    players = ["Anna", "Max"]
    pairs = generate_round_robin_pairs(players)
    create_schedule(pairs, players)
    record_result("Anna", "Max", "6:3, 6:4")
    stats = get_player_statistics("Anna")
    assert stats["wins"] == 1
    assert stats["sets_won"] == 2
    assert stats["games_won"] == 12

def test_calculate_standings():
    setup_reset_globals()
    players = ["Anna", "Max", "Tom"]
    pairs = generate_round_robin_pairs(players)
    create_schedule(pairs, players)
    record_result("Anna", "Max", "6:3, 6:4")
    record_result("Anna", "Tom", "6:2, 6:1")
    standings = calculate_standings(players)
    assert standings[0]["player"] == "Anna"
    assert standings[0]["points"] == 2

def test_tournament_progress():
    setup_reset_globals()
    players = ["Anna", "Max"]
    pairs = generate_round_robin_pairs(players)
    create_schedule(pairs, players)
    record_result("Anna", "Max", "6:3, 6:4")
    progress = get_tournament_progress()
    assert "Turnier-Fortschritt: 100%" in progress

def test_player_ranking():
    setup_reset_globals()
    players = ["Anna", "Max"]
    pairs = generate_round_robin_pairs(players)
    create_schedule(pairs, players)
    record_result("Anna", "Max", "6:3, 6:4")
    assert get_player_ranking("Anna") == 1

def test_performance_no_matches():
    setup_reset_globals()
    players = ["Anna", "Max"]
    pairs = generate_round_robin_pairs(players)
    create_schedule(pairs, players)
    perf = create_player_performance("Anna")
    assert "Keine Matches" in perf

def test_performance_with_matches():
    setup_reset_globals()
    players = ["Anna", "Max", "Tom", "Lisa"]
    pairs = generate_round_robin_pairs(players)
    create_schedule(pairs, players)
    record_result("Anna", "Max", "6:3, 6:4")
    record_result("Anna", "Lisa", "6:2, 6:1")
    perf = create_player_performance("Anna")
    assert "Match-Verlauf: W W" in perf
    assert "Match 1: ██  (2-0)" in perf

def test_performance_mixed_results():
    setup_reset_globals()
    players = ["Anna", "Max", "Tom", "Lisa"]
    pairs = generate_round_robin_pairs(players)
    create_schedule(pairs, players)
    record_result("Max", "Anna", "3:6, 6:4, 6:2")
    record_result("Max", "Tom", "6:3, 7:6")
    perf = create_player_performance("Max")
    assert "Match-Verlauf: W W" in perf
    assert "Match 1: ██ █  (2-1)" in perf  # Angepasst: zusätzliches Leerzeichen vor "(2-1)"
    assert "Match 2: ██  (2-0)" in perf