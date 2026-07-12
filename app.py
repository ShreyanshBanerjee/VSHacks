from flask import Flask, jsonify, render_template, request, redirect, url_for
import secrets
import sqlite3
import json
from pathlib import Path
from collections import Counter

from data import fetch_matches

BASE_DIR = Path(__file__).resolve().parent
MATCHES_FILE = BASE_DIR / "data" / "matches.json"
TEAMS_FILE = BASE_DIR / "data" / "teams.txt"
FOODS_FILE = BASE_DIR / "data" / "foods.json"

app = Flask(__name__)

def load_teams():
    with open(TEAMS_FILE, 'r') as f:
        return f.read().splitlines()
    
def load_foods():
    with open(FOODS_FILE, 'r') as f:
        return json.load(f)

fetch_matches.run()
def load_matches():
    with open(MATCHES_FILE, 'r') as f:
        return json.load(f)
    
def recommend_foods(team1, team2, budget, num_guests):
    foods_dict = load_foods()
    
    budget_per_person = budget / num_guests

    budget_per_team = budget_per_person / 2

    team1_recommended_foods = []
    team2_recommended_foods = []

    team1_key = team1 if team1 in foods_dict else "General"
    team2_key = team2 if team2 in foods_dict else "General"

    team1_foods = foods_dict.get(team1_key, [])
    team2_foods = foods_dict.get(team2_key, [])

    sorted_team1_foods = sorted(team1_foods, key=lambda food: food['cost_per_person'])
    sorted_team2_foods = sorted(team2_foods, key=lambda food: food['cost_per_person'])

    team1_used_budget = 0
    team2_used_budget = 0
    counter = 0
    while True:
        length = len(sorted_team1_foods)
        if sorted_team1_foods[counter % length]['cost_per_person'] + team1_used_budget <= budget_per_team:
            team1_recommended_foods.append(sorted_team1_foods[counter % length]["name"])
            team1_used_budget += sorted_team1_foods[counter % length]['cost_per_person']
            counter += 1
        else:
            break
    counter = 0
    while True:
        length = len(sorted_team2_foods)
        if sorted_team2_foods[counter % length]['cost_per_person'] + team2_used_budget <= budget_per_team:
            team2_recommended_foods.append(sorted_team2_foods[counter % length]["name"])
            team2_used_budget += sorted_team2_foods[counter % length]['cost_per_person']
            counter += 1
        else:
            break
    
    all_recommended_foods = team1_recommended_foods + team2_recommended_foods
    food_counts = Counter(all_recommended_foods)

    recommendations = [
        f"{count}x {food_name}" if count > 1 else food_name
        for food_name, count in food_counts.items()
    ]

    total_used_budget = team1_used_budget + team2_used_budget

    return recommendations, total_used_budget

def connect_to_database():
    connect = sqlite3.connect('database.db')
    connect.row_factory = sqlite3.Row
    connect.execute("PRAGMA foreign_keys = ON")
    return connect

def create_database():
    with connect_to_database() as connect:
        connect.execute(
            """
            CREATE TABLE IF NOT EXISTS parties (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE NOT NULL,
                host_name TEXT NOT NULL,
                location TEXT NOT NULL,
                budget REAL NOT NULL,
                max_guests INTEGER NOT NULL
            )
            """
        )

        connect.execute(
            """
            CREATE TABLE IF NOT EXISTS guests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                party_code TEXT NOT NULL,
                guest_name TEXT NOT NULL,
                favorite_team TEXT NOT NULL,
                available_matches TEXT NOT NULL,
                FOREIGN KEY (party_code) REFERENCES parties (code)
            )
            """
        )

def create_code():
    while True:
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        code = ''.join(secrets.choice(characters) for _ in range(6))
        with connect_to_database() as connect:
            existing_code = connect.execute(
                "SELECT * FROM parties WHERE code = ?", (code,)
            ).fetchone()
            if not existing_code:
                return code
            
def calculate_match_score(match, guests):
    score = 0
    available_guests = []
    supporters = []

    for guest in guests:
        current_matches = guest['available_matches'].split(',')

        if str(match["id"]) in current_matches:
            score += 2
            available_guests.append(guest['guest_name'])
            
        if guest['favorite_team'] == match['team1'] or guest['favorite_team'] == match['team2']:
            score += 1
            supporters.append(guest['guest_name'])
    
    return {
        "score": score,
        "available_guests": available_guests,
        "supporters": supporters
    }

create_database()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['GET', 'POST'])
def create_party():
    if request.method == 'POST':
        host_name = request.form['host_name'].strip()
        location = request.form['location'].strip()
        try:
            budget = float(request.form['budget'])
            max_guests = int(request.form['max_guests'])
        except ValueError:
            return "Invalid input for budget or max guests", 400
        
        if not host_name or not location or budget < 0 or max_guests < 1:
            return "Invalid input", 400
        
        code = create_code()


        with connect_to_database() as connect:
            connect.execute(
                "INSERT INTO parties (code, host_name, location, budget, max_guests) VALUES (?, ?, ?, ?, ?)",
                (code, host_name, location, budget, max_guests)
            )
            connect.commit()

        return redirect(url_for('join_party', code=code))

    return render_template('create_party.html')

@app.route("/party/<code>")
def party_dashboard(code):
    code = code.upper()

    with connect_to_database() as connect:
        party = connect.execute(
            "SELECT * FROM parties WHERE code = ?", (code,)
        ).fetchone()

        guests = connect.execute(
            "SELECT * FROM guests WHERE party_code = ?", (code,)
        ).fetchall()

    if party:
        if guests:
            matches = load_matches()
            best_score = 0
            best_match = None

            for match in matches:
                current_match = calculate_match_score(match, guests)
                if current_match["score"] > best_score:
                    best_match = {
                        **match,
                        **current_match
                    }
                    best_score = current_match["score"]
            print(best_match)
            return render_template('party_dashboard.html', party=party, guests=guests, best_match=best_match)
        else:
            return render_template('party_dashboard.html', party=party, guests=guests)
    else:
        return "Party not found", 404

@app.route("/join/<code>", methods=['GET', 'POST'])
def join_party(code):
    code = code.upper()
    matches = load_matches()
    teams = load_teams()

    with connect_to_database() as connect:
        party = connect.execute(
            "SELECT * FROM parties WHERE code = ?", (code,)
        ).fetchone()

        if not party:
            return "Party not found", 404

        guest_count = connect.execute(
            "SELECT COUNT(*) FROM guests WHERE party_code = ?", (code,)
        ).fetchone()[0]

    if request.method == 'POST':
        if guest_count >= party['max_guests']:
            return "Party is full", 403
        
        guest_name = request.form['guest_name'].strip()
        favorite_team = request.form['favorite_team'].strip()
        available_matches = request.form.getlist('available_matches')

        if not guest_name or not favorite_team or not available_matches:
            return "Invalid input", 400
        
        available_matches_comma = ','.join(available_matches)

        with connect_to_database() as connect:
            connect.execute(
                "INSERT INTO guests (party_code, guest_name, favorite_team, available_matches) VALUES (?, ?, ?, ?)",
                (code, guest_name, favorite_team, available_matches_comma)
            )
            connect.commit()

        return redirect(url_for('party_dashboard', code=code))
    

    return render_template(
        'join_party.html',
        party=party,
        teams=teams,
        matches=matches)

@app.route("/find-party", methods=['GET', 'POST'])
def find_party():
    if request.method == 'POST':
        code = request.form.get('party_code', '').strip().upper()
        if code:
            return redirect(url_for('join_party', code=code))
            
    return render_template('find_party.html')

@app.route("/generate/<code>/<team1>-<team2>")
def generate_plan(code, team1, team2):
    with connect_to_database() as connect:
        party = connect.execute(
            "SELECT * FROM parties WHERE code = ?",
            (code,)
        ).fetchone()

        if not party:
            return jsonify({"error": "Party not found"}), 404

    recommendations, total_used_budget = recommend_foods(
        team1,
        team2,
        party["budget"],
        party["max_guests"]
    )

    return jsonify({
        "team1": team1,
        "team2": team2,
        "foods": recommendations,
        "cost_per_person": total_used_budget,
        "budget_per_person": party["budget"],
        "remaining_budget": party["budget"] - total_used_budget * party["max_guests"]
    })

if __name__ == '__main__':
    app.run(debug=True)
