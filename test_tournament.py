import pytest
from unittest.mock import mock_open, patch
import json
import csv
from tournament_scheduler import *

@pytest.fixture
def reset_globals():
    match_results.clear()
    match_days.clear()
    current_schedule.clear()
    players.clear()
    yield

def test_save_tournament(reset_globals):
    # Setup: Turnierdaten vorbereiten
    players.extend(["Anna", "Max"])
    match_results[("Anna", "Max")] = "6:3, 6:4"
    match_days[1] = {"matches": [("Anna", "Max")], "completed": True}
    current_schedule.append([("Anna", "Max")])
    
    # Mock für Dateioperation
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = save_tournament("test_turnier.json")
        
        # Überprüfen, ob Datei geschrieben wurde
        mock_file.assert_called_once_with("test_turnier.json", "w", encoding="utf-8")
        handle = mock_file()
        written_data = "".join(call.args[0] for call in handle.write.call_args_list)
        data = json.loads(written_data)
        
        # Überprüfen der gespeicherten Daten
        assert data["tournament_name"] == "Tennis Tournament"
        assert data["players"] == ["Anna", "Max"]
        assert data["matches"][0]["player1"] == "Anna"
        assert data["matches"][0]["player2"] == "Max"
        assert data["matches"][0]["result"] == "6:3, 6:4"
        assert data["days"][0]["number"] == 1
        assert data["days"][0]["status"] == "completed"
        assert result.success
        assert result.message == "Turnier in test_turnier.json gespeichert"

def test_load_tournament(reset_globals):
    mock_data = json.dumps({
        "players": ["Anna", "Max"],
        "matches": [{"id": 1, "player1": "Anna", "player2": "Max", "day": 1, "court": 1, "status": "completed", "result": "6:3, 6:4", "winner": "Anna"}],
        "days": [{"number": 1, "status": "completed", "date": "2025-04-02"}],
        "current_standings": [{"player": "Anna", "matches_won": 1, "matches_lost": 0, "points": 1}]
    })
    mock_file = mock_open(read_data=mock_data)
    with patch("builtins.open", mock_file):
        result = load_tournament("test_turnier.json")
        assert result.success
        assert "Anna" in players
        assert match_results[("Anna", "Max")] == "6:3, 6:4"
        assert match_days[1]["completed"]

def test_export_results_csv(reset_globals):
    # Setup
    players.extend(["Anna", "Max"])
    pairs = generate_round_robin_pairs(players)
    create_schedule(pairs, players)
    record_result("Anna", "Max", "6:3,6:4")
    
    # Mock für Dateioperation
    mock_file = mock_open()
    with patch("builtins.open", mock_file):
        result = export_results_csv("test_results.csv")
        
        # Überprüfe Erfolg
        assert result.success, f"Export fehlgeschlagen: {result.message}"
        
        # Überprüfe Aufruf von open
        mock_file.assert_called_once_with("test_results.csv", "w", encoding="utf-8", newline="")
        
        # Überprüfe geschriebene Daten
        handle = mock_file()
        written_calls = handle.write.call_args_list
        written_data = "".join(call.args[0] for call in written_calls)
        expected_data = 'p1,p2,result\r\nAnna,Max,"6:3,6:4"\r\n'  # Anführungszeichen hinzugefügt
        assert written_data == expected_data, f"Erwartet: {repr(expected_data)}, erhalten: {repr(written_data)}"


def setup_reset_globals():
    global match_results, current_schedule, match_days
    match_results.clear()
    current_schedule.clear()
    match_days.clear()

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
    a = [["" for _ in range(5)] for _ in range(5)]
    a[0][1] = "Anna"
    a[0][2] = "Max"
    a[0][3] = "Tom"
    a[0][4] = "Lisa"
    a[1][0] = "Anna"
    a[2][0] = "Max"
    a[3][0] = "Tom"
    a[4][0] = "Lisa"
    assert a == matrix

def test_matrix_with_results():
    setup_reset_globals()
    players = ["Anna", "Max", "Tom", "Lisa"]
    pairs = generate_round_robin_pairs(players)
    create_schedule(pairs, players)
    record_result("Anna", "Max", "6:3, 6:4")
    record_result("Tom", "Lisa", "6:2, 6:1")
    matrix = create_match_matrix(players)
    a = [["" for _ in range(5)] for _ in range(5)] 
    a[0][1] = "Anna"
    a[0][2] = "Max"
    a[0][3] = "Tom"
    a[0][4] = "Lisa"
    a[1][0] = "Anna"
    a[2][0] = "Max"
    a[3][0] = "Tom"
    a[4][0] = "Lisa"
    a[1][2] = "6:3,6:4"
    a[3][4] = "6:2,6:1"
    a[2][1] = "3:6,4:6"
    a[4][3] = "2:6,1:6"
    assert a == matrix

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
    assert "Match 1: ██ █  (2-1)" in perf
    assert "Match 2: ██  (2-0)" in perf

def test_organize_match_days_basic():
    setup_reset_globals()
    players = ["Anna", "Max", "Tom", "Lisa"]
    pairs = generate_round_robin_pairs(players)
    organize_match_days(pairs, players)
    days = match_days
    assert len(days) >= 3
    total_matches = sum(len(day["matches"]) for day in days.values())
    assert total_matches == 6
    for day in days.values():
        assert len(day["matches"]) <= 2
        players_in_day = set()
        for p1, p2 in day["matches"]:
            assert p1 not in players_in_day
            assert p2 not in players_in_day
            players_in_day.add(p1)
            players_in_day.add(p2)

def test_get_matches_by_day():
    setup_reset_globals()
    players = ["Anna", "Max", "Tom", "Lisa"]
    pairs = generate_round_robin_pairs(players)
    organize_match_days(pairs, players)
    day1_matches = get_matches_by_day(1)
    assert len(day1_matches) <= 2
    assert all(isinstance(match, tuple) and len(match) == 2 for match in day1_matches)

def test_get_player_schedule():
    setup_reset_globals()
    players = ["Anna", "Max", "Tom", "Lisa"]
    pairs = generate_round_robin_pairs(players)
    organize_match_days(pairs, players)
    schedule = get_player_schedule("Anna")
    assert "Anna vs." in schedule
    assert len([line for line in schedule.split("\n") if "Anna vs." in line]) == 3

def test_mark_day_completed():
    setup_reset_globals()
    players = ["Anna", "Max", "Tom", "Lisa"]
    pairs = generate_round_robin_pairs(players)
    organize_match_days(pairs, players)
    mark_day_completed(1)
    days = match_days
    assert days[1]["completed"] == True

def test_get_next_scheduled_day():
    setup_reset_globals()
    players = ["Anna", "Max", "Tom", "Lisa"]
    pairs = generate_round_robin_pairs(players)
    organize_match_days(pairs, players)
    assert get_next_scheduled_day() == 1
    mark_day_completed(1)
    assert get_next_scheduled_day() == 2

def test_reschedule_match():
    setup_reset_globals()
    players = ["Anna", "Max", "Tom", "Lisa"]
    pairs = generate_round_robin_pairs(players)
    organize_match_days(pairs, players)
    days = match_days
    original_day1_matches = days[1]["matches"]
    reschedule_match("Anna", "Max", 4)  # Verwende Tag 4 statt Tag 2
    days = match_days
    assert ("Anna", "Max") not in days[1]["matches"]
    assert ("Anna", "Max") in days[4]["matches"]

def test_odd_number_of_players():
    setup_reset_globals()
    players = ["Anna", "Max", "Tom"]
    pairs = generate_round_robin_pairs(players)
    organize_match_days(pairs, players)
    days = match_days
    total_matches = sum(len(day["matches"]) for day in days.values())
    assert total_matches == 3
    for day in days.values():
        assert len(day["matches"]) <= 1

def test_all_days_completed():
    setup_reset_globals()
    players = ["Anna", "Max"]
    pairs = generate_round_robin_pairs(players)
    organize_match_days(pairs, players)
    mark_day_completed(1)
    assert get_next_scheduled_day() is None

def test_record_result_with_7_5():
    setup_reset_globals()
    players = ["Anna", "Max"]
    pairs = generate_round_robin_pairs(players)
    create_schedule(pairs, players)
    record_result("Anna", "Max", "7:5, 6:4")
    assert get_match_result("Anna", "Max") == "7:5, 6:4"

def test_balanced_breaks():
    setup_reset_globals()
    players = ["Anna", "Max", "Tom", "Lisa"]
    pairs = generate_round_robin_pairs(players)
    schedule = create_schedule(pairs, players)
    matches_per_round = defaultdict(list)
    for round_num, round_games in enumerate(schedule):
        for p1, p2 in round_games:
            matches_per_round[p1].append(round_num)
            matches_per_round[p2].append(round_num)
    for player in players:
        rounds = matches_per_round[player]
        gaps = [rounds[i+1] - rounds[i] for i in range(len(rounds)-1)]
        assert len(gaps) == 2  # 3 Spiele → 2 Pausen
        assert all(gap <= 2 for gap in gaps)  # Keine übermäßig langen Pausen

def test_player_statistics_counts_wins_and_losses_correctly():
    players = ["Anna", "Max"]
    pairs = generate_round_robin_pairs(players)
    create_schedule(pairs, players)
    record_result("Anna", "Max", "4:6, 4:6")
    anna_stats = get_player_statistics("Anna")
    max_stats = get_player_statistics("Max")
    assert anna_stats["wins"] == 0
    assert anna_stats["losses"] == 1
    assert max_stats["wins"] == 1
    assert max_stats["losses"] == 0