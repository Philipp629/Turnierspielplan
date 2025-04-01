import itertools
from collections import defaultdict
import re

class Result:
    def __init__(self, success, message):
        self.success = success
        self.message = message

match_results = {}
current_schedule = []
match_days = {}

def generate_round_robin_pairs(players):
    return list(itertools.combinations(players, 2))

def organize_match_days(pairs, players):
    global match_days
    match_days.clear()
    remaining_pairs = list(pairs)
    day_number = 1
    n = len(players)
    max_matches_per_day = n // 2

    while remaining_pairs:
        current_day = {"matches": [], "completed": False}
        players_used = set()

        for pair in remaining_pairs[:]:
            p1, p2 = pair
            if (len(current_day["matches"]) < max_matches_per_day and
                p1 not in players_used and p2 not in players_used):
                current_day["matches"].append(pair)
                players_used.add(p1)
                players_used.add(p2)
                remaining_pairs.remove(pair)

        if current_day["matches"]:
            match_days[day_number] = current_day
            day_number += 1
        else:
            raise ValueError("Konnte nicht alle Paarungen verteilen!")

    global current_schedule
    current_schedule = [day["matches"] for day in match_days.values()]
    return current_schedule

def create_schedule(pairs, players):
    return organize_match_days(pairs, players)

def print_schedule(schedule):
    print("\n=== Spielplan ===")
    for day_num, day_matches in match_days.items():
        print(f"\nTag {day_num}{' (Abgeschlossen)' if day_matches['completed'] else ''}:")
        for i, (player1, player2) in enumerate(day_matches["matches"], 1):
            result = get_match_result(player1, player2)
            print(f"  Court {i}: {player1} vs {player2}{' - ' + result if result else ''}")

def check_fairness(schedule, players):
    matches_per_round = defaultdict(list)
    for player in players:
        for round_num, round_games in enumerate(schedule):
            for player1, player2 in round_games:
                if player in (player1, player2):
                    matches_per_round[player].append(round_num)
    
    print("\n=== Fairness-Check ===")
    for player, rounds in matches_per_round.items():
        print(f"{player} spielt in Runden: {rounds}")
        if len(rounds) > 1:
            gaps = [rounds[i+1] - rounds[i] for i in range(len(rounds)-1)]
            print(f"Pausenzeiten zwischen Spielen (in Runden): {gaps}")
            avg_gap = sum(gaps) / len(gaps)
            print(f"Durchschnittliche Pausenzeit: {avg_gap:.2f}")

def add_player(players, max_players):
    if len(players) >= max_players:
        return Result(False, f"Maximale Anzahl von {max_players} Spielern erreicht!")

    while True:
        player_name = input("Geben Sie den Namen des Spielers ein: ").strip()
        
        if not re.match(r'^[A-Za-zÄÖÜäöüß]{2,}$', player_name):
            print("Ungültiger Name! Bitte nur Buchstaben und mindestens 2 Zeichen verwenden.")
            continue

        if player_name in players:
            print("Dieser Spieler existiert bereits!")
            continue
        
        players.append(player_name)
        return Result(True, f"Spieler {player_name} hinzugefügt.")

def validate_tennis_score(score):
    sets = [s.strip() for s in score.split(",")]
    
    for i, s in enumerate(sets):
        if not re.match(r'^\d+:\d+$', s):
            raise ValueError("Ungültiges Ergebnisformat! Verwenden Sie z. B. '6:4'.")
        
        p1_score, p2_score = map(int, s.split(":"))
        
        if p1_score == p2_score:
            raise ValueError(f"Ungültiger Satz {s}: Ein Satz kann nicht unentschieden enden.")

        if p1_score >= 6 or p2_score >= 6:
            if (p1_score == 6 and p2_score <= 4) or (p2_score == 6 and p1_score <= 4):
                continue
            elif ((p1_score == 7 and p2_score in (5, 6)) or 
                  (p2_score == 7 and p1_score in (5, 6))):
                continue
            else:
                raise ValueError(f"Ungültiger Satz {s}: Ein Satz endet bei 6 mit 2 Vorsprung oder bei 7 mit 5 oder 6.")
        else:
            raise ValueError(f"Ungültiger Satz {s}: Ein Satz muss bis mindestens 6 gehen.")
    
    player1_wins = sum(1 for s in sets if int(s.split(":")[0]) > int(s.split(":")[1]))
    player2_wins = len(sets) - player1_wins
    if player1_wins == player2_wins:
        raise ValueError("Kein eindeutiger Gewinner bestimmbar.")
    
    return True

def record_result(player1, player2, score):
    key = (player1, player2)
    if key in match_results or (player2, player1) in match_results:
        raise ValueError("Ergebnis für dieses Spiel wurde bereits eingetragen")

    valid_pairs = {pair for round in current_schedule for pair in round}
    if key not in valid_pairs and (player2, player1) not in valid_pairs:
        raise ValueError("Spiel ist nicht im Spielplan enthalten")

    validate_tennis_score(score)
    match_results[key] = score

def get_match_result(player1, player2):
    key = (player1, player2)
    reverse_key = (player2, player1)
    if key in match_results:
        return match_results[key]
    elif reverse_key in match_results:
        return match_results[reverse_key]
    return None

def get_player_matches(player):
    matches = []
    for (p1, p2), result in match_results.items():
        if p1 == player:
            matches.append({"opponent": p2, "result": result})
        elif p2 == player:
            matches.append({"opponent": p1, "result": result})
    return matches

def get_player_statistics(player):
    stats = {"wins": 0, "losses": 0, "sets_won": 0, "sets_lost": 0, "games_won": 0, "games_lost": 0, "tiebreaks_won": 0, "tiebreaks_lost": 0}
    for (p1, p2), result in match_results.items():
        if p1 == player or p2 == player:
            sets = [s.strip() for s in result.split(",")]
            player_wins = 0
            opponent_wins = 0
            for s in sets:
                p1_score, p2_score = map(int, s.split(":"))
                if p1 == player:
                    stats["games_won"] += p1_score
                    stats["games_lost"] += p2_score
                    if p1_score > p2_score:
                        stats["sets_won"] += 1
                        player_wins += 1
                        if p1_score == 7 and p2_score == 6:
                            stats["tiebreaks_won"] += 1
                    else:
                        stats["sets_lost"] += 1
                        opponent_wins += 1
                        if p2_score == 7 and p1_score == 6:
                            stats["tiebreaks_lost"] += 1
                elif p2 == player:
                    stats["games_won"] += p2_score
                    stats["games_lost"] += p1_score
                    if p2_score > p2_score:
                        stats["sets_won"] += 1
                        player_wins += 1
                        if p2_score == 7 and p1_score == 6:
                            stats["tiebreaks_won"] += 1
                    else:
                        stats["sets_lost"] += 1
                        opponent_wins += 1
                        if p1_score == 7 and p2_score == 6:
                            stats["tiebreaks_lost"] += 1
            if player_wins > opponent_wins:
                stats["wins"] += 1
            else:
                stats["losses"] += 1
    return stats

def input_match_result(schedule):
    for round_num, round_games in enumerate(schedule):
        for player1, player2 in round_games:
            if not get_match_result(player1, player2):
                print(f"\nErgebnis für {player1} vs {player2} eingeben (z. B. '6:4' pro Satz):")
                sets = []
                
                while True:
                    set_score = input(f"Satz {len(sets) + 1} (oder 'fertig' zum Beenden): ").strip()
                    
                    if set_score.lower() == "fertig":
                        if len(sets) < 2:
                            print("Mindestens 2 gewonnene Sätze erforderlich!")
                            continue
                        break
                    
                    try:
                        validate_tennis_score(set_score)
                        sets.append(set_score)
                        p1_wins = sum(1 for s in sets if int(s.split(":")[0]) > int(s.split(":")[1]))
                        p2_wins = len(sets) - p1_wins
                        if p1_wins == 2 or p2_wins == 2:
                            break
                    except ValueError as e:
                        print(f"Fehler: {e}")
                        continue
                
                score = ", ".join(sets)
                return player1, player2, score
    
    print("Alle Ergebnisse sind bereits eingetragen!")
    return None

def calculate_standings(players):
    standings = []
    player_order = {p: i for i, p in enumerate(players)}
    for player in players:
        stats = get_player_statistics(player)
        standings.append({
            "player": player,
            "points": stats["wins"],
            "matches_won": stats["wins"],
            "matches_lost": stats["losses"],
            "sets_won": stats["sets_won"],
            "sets_lost": stats["sets_lost"],
            "games_won": stats["games_won"],
            "games_lost": stats["games_lost"]
        })

    standings.sort(key=lambda x: (x["points"], x["sets_won"], x["games_won"]), reverse=True)

    def get_direct_winner(p1, p2):
        result = get_match_result(p1, p2)
        if result:
            p1_sets = sum(1 for s in result.split(",") if int(s.split(":")[0]) > int(s.split(":")[1]))
            p2_sets = len(result.split(",")) - p1_sets
            return p1 if p1_sets > p2_sets else p2
        return None

    i = 0
    while i < len(standings):
        start = i
        while i < len(standings) - 1 and standings[i]["points"] == standings[i + 1]["points"]:
            i += 1
        i += 1
        if i - start > 1:
            group = standings[start:i]
            for j in range(len(group) - 1):
                for k in range(len(group) - 1 - j):
                    p1 = group[k]["player"]
                    p2 = group[k + 1]["player"]
                    winner = get_direct_winner(p1, p2)
                    if winner == p2:
                        group[k], group[k + 1] = group[k + 1], group[k]
            standings[start:i] = group
            
            if all(get_direct_winner(group[j]["player"], group[j + 1]["player"]) is None for j in range(len(group) - 1)):
                def sort_key(entry):
                    set_ratio = entry["sets_won"] / max(1, (entry["sets_won"] + entry["sets_lost"]))
                    game_ratio = entry["games_won"] / max(1, (entry["games_won"] + entry["games_lost"]))
                    return (entry["points"], set_ratio, game_ratio, -player_order[entry["player"]])
                standings[start:i] = sorted(standings[start:i], key=sort_key, reverse=True)

    return standings

def get_player_ranking(player):
    standings = calculate_standings(list(set([p for round in current_schedule for p1, p2 in round for p in (p1, p2)])))
    for i, entry in enumerate(standings, 1):
        if entry["player"] == player:
            return i
    return 1 if not standings else len(standings)

def get_complete_ranking():
    players = list(set([p for round in current_schedule for p1, p2 in round for p in (p1, p2)]))
    return calculate_standings(players)

def create_match_matrix(players):
    matrix = [["" for _ in range(len(players) + 1)] for _ in range(len(players) + 1)]
    for i, player in enumerate(players):
        matrix[i + 1][0] = player
        matrix[0][i + 1] = player
    
    for (p1, p2), result in match_results.items():
        p1_index = players.index(p1) + 1
        p2_index = players.index(p2) + 1
        cleaned_result = "".join(result.split())
        matrix[p1_index][p2_index] = cleaned_result
        
        if cleaned_result:
            sets = cleaned_result.split(",")
            reversed_result = ",".join(f"{s.split(':')[1].strip()}:{s.split(':')[0].strip()}" for s in sets)
            matrix[p2_index][p1_index] = reversed_result
        else:
            matrix[p2_index][p1_index] = ""
    
    return matrix

def make_match_matrix_pretty(matrix):
    # Bestimme die maximale Breite für jede Spalte
    col_widths = [max(len(str(row[i])) for row in matrix) for i in range(len(matrix[0]))]
    # Mindestbreite für bessere Lesbarkeit
    col_widths = [max(w, 8) for w in col_widths]  # Mindestens 8 Zeichen pro Spalte
    
    # Erstelle die Trennlinie
    separator = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"
    
    # Formatiere die Zeilen
    formatted_rows = []
    for i, row in enumerate(matrix):
        formatted_row = "| " + " | ".join(
            str(cell).center(col_widths[j]) for j, cell in enumerate(row)
        ) + " |"
        formatted_rows.append(formatted_row)
        # Füge eine Trennlinie nach der Kopfzeile hinzu
        if i == 0:
            formatted_rows.append(separator)
    
    # Kombiniere alles mit der oberen und unteren Rahmenlinie
    return "\n".join([separator] + formatted_rows + [separator])

def get_tournament_progress():
    total_matches = sum(len(round_games) for round_games in current_schedule)
    played_matches = len(match_results)
    progress_percent = (played_matches / total_matches * 100) if total_matches > 0 else 0
    
    open_matches = []
    for round_games in current_schedule:
        for p1, p2 in round_games:
            if not get_match_result(p1, p2):
                open_matches.append(f"{p1} vs {p2}")
    
    standings = calculate_standings(list(set(p for round in current_schedule for p1, p2 in round for p in (p1, p2))))
    leader = standings[0] if standings else {"player": "Keiner", "matches_won": 0, "matches_lost": 0}
    
    output = [
        f"Turnier-Fortschritt: {progress_percent:.0f}% ({played_matches}/{total_matches} Matches gespielt)",
        "",
        "Ausstehende Matches:" if open_matches else "Keine ausstehenden Matches",
        *[f"{i+1}. {match}" for i, match in enumerate(open_matches)],
        "",
        f"Aktueller Tabellenführer: {leader['player']} ({leader['matches_won']} Siege, {leader['matches_lost']} Niederlagen)"
    ]
    return "\n".join(line for line in output if line)

def create_player_performance(player):
    matches = get_player_matches(player)
    history = []
    set_balances = []
    rankings = []
    
    if not matches:
        history.append("Keine Matches")
        rankings.append(f"Start:  #1")
    else:
        for i, match in enumerate(matches):
            result = match["result"]
            sets = result.split(", ")
            p1_wins = sum(1 for s in sets if int(s.split(":")[0]) > int(s.split(":")[1]))
            p2_wins = len(sets) - p1_wins
            my_wins = p1_wins if match["opponent"] != player else p2_wins
            opp_wins = p2_wins if match["opponent"] != player else p1_wins
            history.append("W" if my_wins > opp_wins else "L")
            set_display = "██ █" if my_wins == 2 and opp_wins == 1 else "██" if my_wins == 2 else "█" if my_wins == 1 else ""
            set_balances.append(f"Match {i+1}: {set_display}  ({my_wins}-{opp_wins})")
            rankings.append(f"{'Start' if i == 0 else f'Nach {i}'} : #{get_player_ranking(player)} {'↑' if i == 0 else '-' if i > 0 else ''}")
    
    output = [
        f"Spieler: {player}",
        f"Match-Verlauf: {' '.join(history)}",
        "",
        "Satz-Bilanz:",
        *set_balances,
        "",
        "Ranglistenentwicklung:",
        *rankings
    ]
    return "\n".join(output)

def get_matches_by_day(day_number):
    return match_days.get(day_number, {"matches": []})["matches"]

def get_player_schedule(player):
    output = [f"Spielplan für {player}:\n"]
    completed_matches = []
    pending_matches = []

    for day_num, day in match_days.items():
        for p1, p2 in day["matches"]:
            if p1 == player or p2 == player:
                opponent = p2 if p1 == player else p1
                result = get_match_result(p1, p2)
                line = f"Tag {day_num}: {player} vs. {opponent} (Court {day['matches'].index((p1, p2)) + 1})"
                if result:
                    p1_wins = sum(1 for s in result.split(",") if int(s.split(":")[0]) > int(s.split(":")[1]))
                    p2_wins = len(result.split(",")) - p1_wins
                    my_wins = p1_wins if p1 == player else p2_wins
                    outcome = "Gewonnen" if my_wins > p2_wins else "Verloren"
                    completed_matches.append(f"- {line}: {outcome} ({result})")
                else:
                    pending_matches.append(f"- {line}")

    output.append("Abgeschlossene Matches:")
    output.extend(completed_matches if completed_matches else ["- Keine"])
    output.append("\nAusstehende Matches:")
    output.extend(pending_matches if pending_matches else ["- Keine"])
    return "\n".join(output)

def mark_day_completed(day_number):
    if day_number in match_days:
        match_days[day_number]["completed"] = True

def get_next_scheduled_day():
    for day_num in sorted(match_days.keys()):
        if not match_days[day_num]["completed"]:
            return day_num
    return None

def reschedule_match(player1, player2, new_day):
    old_day = None
    match = (player1, player2)
    reverse_match = (player2, player1)

    for day_num, day in match_days.items():
        if match in day["matches"] or reverse_match in day["matches"]:
            old_day = day_num
            break

    if not old_day:
        raise ValueError("Match nicht gefunden!")

    if get_match_result(player1, player2):
        raise ValueError("Bereits gespieltes Match kann nicht verschoben werden!")

    new_day_players = {p for m in get_matches_by_day(new_day) for p in m}
    if player1 in new_day_players or player2 in new_day_players:
        raise ValueError("Ein Spieler hat bereits ein Match am neuen Tag!")

    actual_match = match if match in match_days[old_day]["matches"] else reverse_match
    match_days[old_day]["matches"].remove(actual_match)
    if not match_days[old_day]["matches"]:
        del match_days[old_day]
    if new_day not in match_days:
        match_days[new_day] = {"matches": [], "completed": False}
    match_days[new_day]["matches"].append(actual_match)

    global current_schedule
    current_schedule = [day["matches"] for day in match_days.values()]

def main():
    players = []
    max_players = 10

    print("Bitte geben Sie den ersten Spieler ein.")
    while len(players) < 3:
        print(f"\nAktuelle Spieler: {players if players else 'Keine Spieler'}")
        result = add_player(players, max_players)
        if not result.success:
            print(result.message)
            continue
        if len(players) < 3:
            print(f"Bitte geben Sie den {len(players) + 1}. Spieler ein.")

    while True:
        print("\nAktuelle Spieler:", players)
        print("Optionen:")
        print("1. Spieler hinzufügen")
        print("2. Paarungen erstellen und Spielplan anzeigen")

        choice = input("Wählen Sie eine Option (1 oder 2): ").strip()

        if choice == "1":
            result = add_player(players, max_players)
            if not result.success:
                print(result.message)
            else:
                print(result.message)

        elif choice == "2":
            pairs = generate_round_robin_pairs(players)
            schedule = create_schedule(pairs, players)
            print_schedule(schedule)
            check_fairness(schedule, players)
            break

        else:
            print("Ungültige Eingabe! Bitte wählen Sie 1 oder 2.")

    while True:
        print("\nAktuelle Spieler:", players)
        print("Optionen:")
        open_matches = [(p1, p2) for round in schedule for p1, p2 in round if not get_match_result(p1, p2)]
        if open_matches:
            print("1. Ergebnis eintragen")
        print("2. Spielergebnis abrufen")
        print("3. Spielerstatistik anzeigen")
        print("4. Spielplan anzeigen")
        print("5. Rangliste anzeigen")
        print("6. Spielplan-Matrix anzeigen")
        print("7. Turnier-Fortschritt anzeigen")
        print("8. Spieler-Performance anzeigen")
        print("9. Spieltage anzeigen und verwalten")
        print("10. Beenden")

        choice = input("Wählen Sie eine Option: ").strip()

        if choice == "1" and open_matches:
            result = input_match_result(schedule)
            if result:
                player1, player2, score = result
                try:
                    record_result(player1, player2, score)
                    print(f"Ergebnis {score} für {player1} vs {player2} eingetragen.")
                except ValueError as e:
                    print(f"Fehler: {e}")

        elif choice == "2":
            if not players:
                print("Keine Spieler vorhanden!")
            else:
                print("\nWählen Sie den ersten Spieler:")
                for i, player in enumerate(players, 1):
                    print(f"{i}. {player}")
                try:
                    selection1 = int(input("Spieler Nummer eingeben: ").strip())
                    if 1 <= selection1 <= len(players):
                        player1 = players[selection1 - 1]
                        print("\nWählen Sie den zweiten Spieler:")
                        for i, player in enumerate(players, 1):
                            print(f"{i}. {player}")
                        selection2 = int(input("Spieler Nummer eingeben: ").strip())
                        if 1 <= selection2 <= len(players):
                            player2 = players[selection2 - 1]
                            result = get_match_result(player1, player2)
                            if result:
                                print(f"Ergebnis für {player1} vs {player2}: {result}")
                            else:
                                print(f"Kein Ergebnis für {player1} vs {player2} gefunden.")
                        else:
                            print(f"Ungültige Auswahl! Bitte wählen Sie eine Nummer zwischen 1 und {len(players)}.")
                    else:
                        print(f"Ungültige Auswahl! Bitte wählen Sie eine Nummer zwischen 1 und {len(players)}.")
                except ValueError:
                    print("Ungültige Eingabe! Bitte geben Sie eine Zahl ein.")

        elif choice == "3":
            if not players:
                print("Keine Spieler vorhanden!")
            else:
                print("\nWählen Sie einen Spieler für die Statistik:")
                for i, player in enumerate(players, 1):
                    print(f"{i}. {player}")
                try:
                    selection = int(input("Spieler Nummer eingeben: ").strip())
                    if 1 <= selection <= len(players):
                        player = players[selection - 1]
                        stats = get_player_statistics(player)
                        print(f"\nStatistik für {player}:")
                        print(f"Siege: {stats['wins']}")
                        print(f"Niederlagen: {stats['losses']}")
                        print(f"Gewonnene Sätze: {stats['sets_won']}")
                        print(f"Verlorene Sätze: {stats['sets_lost']}")
                        print(f"Gewonnene Spiele: {stats['games_won']}")
                        print(f"Verlorene Spiele: {stats['games_lost']}")
                        print(f"Gewonnene Tie-Breaks: {stats['tiebreaks_won']}")
                        print(f"Verlorene Tie-Breaks: {stats['tiebreaks_lost']}")
                    else:
                        print(f"Ungültige Auswahl! Bitte wählen Sie eine Nummer zwischen 1 und {len(players)}.")
                except ValueError:
                    print("Ungültige Eingabe! Bitte geben Sie eine Zahl ein.")

        elif choice == "4":
            print_schedule(schedule)

        elif choice == "5":
            ranking = get_complete_ranking()
            print("\n=== Rangliste ===")
            print(f"{'Pos':<4} | {'Spieler':<8} | {'Matches (W-L)':<14} | {'Sätze (W-L)':<12} | {'Spiele (W-L)':<13} | {'Punkte':<6}")
            print(f"{'-'*4}|{'-'*8}|{'-'*14}|{'-'*12}|{'-'*13}|{'-'*6}")
            for i, entry in enumerate(ranking, 1):
                print(f"{i:<4} | {entry['player']:<8} | {entry['matches_won']}-{entry['matches_lost']:<12} | "
                      f"{entry['sets_won']}-{entry['sets_lost']:<9} | {entry['games_won']}-{entry['games_lost']:<10} | "
                      f"{entry['points']:<6}")

        elif choice == "6":
            print(make_match_matrix_pretty(create_match_matrix(players)))

        elif choice == "7":
            print(get_tournament_progress())

        elif choice == "8":
            if not players:
                print("Keine Spieler vorhanden!")
            else:
                print("\nWählen Sie einen Spieler für die Performance-Anzeige:")
                for i, player in enumerate(players, 1):
                    print(f"{i}. {player}")
                try:
                    selection = int(input("Spieler Nummer eingeben: ").strip())
                    if 1 <= selection <= len(players):
                        selected_player = players[selection - 1]
                        print(create_player_performance(selected_player))
                    else:
                        print(f"Ungültige Auswahl! Bitte wählen Sie eine Nummer zwischen 1 und {len(players)}.")
                except ValueError:
                    print("Ungültige Eingabe! Bitte geben Sie eine Zahl ein.")

        elif choice == "10":
            print("Programm wird beendet.")
            break

        elif choice == "9":
            print("\nSpieltage:")
            for day_num, day in match_days.items():
                status = "Abgeschlossen" if day["completed"] else "Ausstehend"
                print(f"Tag {day_num} ({status}):")
                for i, (p1, p2) in enumerate(day["matches"], 1):
                    result = get_match_result(p1, p2)
                    print(f"  Court {i}: {p1} vs {p2}{' - ' + result if result else ''}")
            print("\nOptionen:")
            print("1. Spieltag als abgeschlossen markieren")
            print("2. Match verschieben")
            print("3. Spielerplan anzeigen")
            sub_choice = input("Wählen Sie eine Option (1-3): ").strip()
            
            if sub_choice == "1":
                try:
                    day = int(input("Spieltag-Nummer eingeben: "))
                    mark_day_completed(day)
                    print(f"Spieltag {day} als abgeschlossen markiert.")
                except ValueError:
                    print("Ungültige Eingabe! Bitte geben Sie eine Zahl ein.")
            
            elif sub_choice == "2":
                p1 = input("Erster Spieler: ").strip()
                p2 = input("Zweiter Spieler: ").strip()
                try:
                    new_day = int(input("Neuer Spieltag: "))
                    reschedule_match(p1, p2, new_day)
                    print(f"Match {p1} vs {p2} auf Tag {new_day} verschoben.")
                except ValueError as e:
                    print(f"Fehler: {e}")
            
            elif sub_choice == "3":
                player = input("Spielername eingeben: ").strip()
                if player in players:
                    print(get_player_schedule(player))
                else:
                    print("Spieler nicht gefunden!")

        else:
            print("Ungültige Eingabe! Bitte wählen Sie eine Option von 1 bis 10.")

if __name__ == "__main__":
    main()