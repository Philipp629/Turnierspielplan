import itertools
from collections import defaultdict
import re

class Result:
    def __init__(self, success, message):
        self.success = success
        self.message = message

match_results = {}
current_schedule = []

def generate_round_robin_pairs(players):
    return list(itertools.combinations(players, 2))

def create_schedule(pairs, players):
    global current_schedule
    schedule = []
    remaining_pairs = list(pairs)
    player_last_round = {player: -1 for player in players}
    
    while remaining_pairs:
        best_pair = None
        max_min_gap = -1
        
        for pair in remaining_pairs:
            p1, p2 = pair
            last_p1 = player_last_round[p1]
            last_p2 = player_last_round[p2]
            current_round = len(schedule)
            
            gap_p1 = current_round - last_p1 if last_p1 >= 0 else float('inf')
            gap_p2 = current_round - last_p2 if last_p2 >= 0 else float('inf')
            min_gap = min(gap_p1, gap_p2)
            
            if min_gap > max_min_gap:
                max_min_gap = min_gap
                best_pair = pair
        
        if best_pair is None:
            best_pair = remaining_pairs[0]
        
        p1, p2 = best_pair
        schedule.append([(p1, p2)])
        player_last_round[p1] = len(schedule) - 1
        player_last_round[p2] = len(schedule) - 1
        remaining_pairs.remove(best_pair)
    
    current_schedule = schedule
    return schedule

def print_schedule(schedule):
    print("\n=== Spielplan ===")
    for round_num, round_games in enumerate(schedule, 1):
        print(f"\nRunde {round_num}:")
        for i, (player1, player2) in enumerate(round_games, 1):
            result = get_match_result(player1, player2)
            print(f"{i}. {player1} vs {player2}{' - ' + result if result else ''}")

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
        
        # Überprüfung: Mindestens 2 Zeichen und nur Buchstaben
        if not re.match(r'^[A-Za-zÄÖÜäöüß]{2,}$', player_name):
            print("Ungültiger Name! Bitte nur Buchstaben und mindestens 2 Zeichen verwenden.")
            continue

        if player_name in players:
            print("Dieser Spieler existiert bereits!")
            continue
        
        players.append(player_name)
        return Result(True, f"Spieler {player_name} hinzugefügt.")


def validate_tennis_score(score):
    """Validiert ein Tennis-Satzergebnis nach Standardregeln."""
    sets = [s.strip() for s in score.split(",")]
    
    for i, s in enumerate(sets):
        if not re.match(r'^\d+:\d+$', s):
            raise ValueError("Ungültiges Ergebnisformat! Verwenden Sie z. B. '6:4'.")
        
        p1_score, p2_score = map(int, s.split(":"))
        
        if p1_score == p2_score:
            raise ValueError(f"Ungültiger Satz {s}: Ein Satz kann nicht unentschieden enden.")

        # Prüfe reguläre Sätze (bis 6 mit 2 Vorsprung)
        if p1_score >= 6 or p2_score >= 6:
            if (p1_score == 6 and p2_score <= 4) or (p2_score == 6 and p1_score <= 4):
                continue  # Gültiger regulärer Satz
            elif (p1_score == 7 and p2_score == 6) or (p2_score == 7 and p1_score == 6):
                continue  # Gültiger Tiebreak-Satz
            else:
                raise ValueError(f"Ungültiger Satz {s}: Ein Satz endet bei 6 mit 2 Vorsprung oder 7:6.")
        else:
            raise ValueError(f"Ungültiger Satz {s}: Ein Satz muss bis mindestens 6 gehen.")
    
    # Prüfe, ob ein eindeutiger Sieger existiert
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
    stats = {"wins": 0, "losses": 0, "sets_won": 0, "sets_lost": 0}
    for (p1, p2), result in match_results.items():
        if p1 == player or p2 == player:
            sets = [s.strip() for s in result.split(",")]
            player_wins = 0
            opponent_wins = 0
            for s in sets:
                p1_score, p2_score = map(int, s.split(":"))
                if p1 == player:
                    if p1_score > p2_score:
                        stats["sets_won"] += 1
                        player_wins += 1
                    else:
                        stats["sets_lost"] += 1
                        opponent_wins += 1
                elif p2 == player:
                    if p2_score > p1_score:
                        stats["sets_won"] += 1
                        player_wins += 1
                    else:
                        stats["sets_lost"] += 1
                        opponent_wins += 1
            if player_wins > opponent_wins:
                stats["wins"] += 1
            else:
                stats["losses"] += 1
    return stats

def input_match_result(schedule):
    """Trägt automatisch das nächste ausstehende Ergebnis ein."""
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

                    if not re.match(r'^\d+:\d+$', set_score):
                        print("Ungültiges Format! Verwenden Sie z. B. '6:4'.")
                        continue

                    sets.append(set_score)
                    
                    # Prüfen, ob ein Spieler bereits 2 Sätze gewonnen hat
                    p1_wins = sum(1 for s in sets if int(s.split(":")[0]) > int(s.split(":")[1]))
                    p2_wins = len(sets) - p1_wins

                    if p1_wins == 2 or p2_wins == 2:
                        break  # Spieler hat gewonnen, weitere Eingabe nicht nötig
                
                score = ", ".join(sets)
                return player1, player2, score  # Erstes ausstehendes Spiel gefunden -> Ergebnis wird eingetragen

    print("Alle Ergebnisse sind bereits eingetragen!")
    return None



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
        print("5. Beenden")
        
        choice = input("Wählen Sie eine Option (1-5): ").strip()

        if choice == "1" and open_matches:
            result = input_match_result(schedule)
            if result:
                player1, player2, score = result
                try:
                    record_result(player1, player2, score)
                    print(f"Ergebnis {score} für {player1} vs {player2} eingetragen.")
                except ValueError as e:
                    print(f"Fehler: {e}")

        elif choice == "1" and not open_matches:
            print("Alle Ergebnisse sind bereits eingetragen!")

        elif choice == "2":
            player1 = input("Erster Spieler: ").strip()
            player2 = input("Zweiter Spieler: ").strip()
            result = get_match_result(player1, player2)
            if result:
                print(f"Ergebnis für {player1} vs {player2}: {result}")
            else:
                print(f"Kein Ergebnis für {player1} vs {player2} gefunden.")

        elif choice == "3":
            player = input("Spielername: ").strip()
            stats = get_player_statistics(player)
            print(f"\nStatistik für {player}:")
            print(f"Siege: {stats['wins']}")
            print(f"Niederlagen: {stats['losses']}")
            print(f"Gewonnene Sätze: {stats['sets_won']}")
            print(f"Verlorene Sätze: {stats['sets_lost']}")

        elif choice == "4":
            print_schedule(schedule)

        elif choice == "5":
            print("Programm wird beendet.")
            break

        else:
            print("Ungültige Eingabe! Bitte wählen Sie eine Option von 1 bis 5.")


if __name__ == "__main__":
    main()