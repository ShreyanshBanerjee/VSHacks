from flask import Flask, jsonify, render_template, request, redirect, url_for
import secrets
import sqlite3
import json
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent
MATCHES_FILE = BASE_DIR / "data" / "matches.json"
TEAMS_FILE = BASE_DIR / "data" / "teams.txt"
FOODS_FILE = BASE_DIR / "data" / "foods.json"

def load_foods():
    with open(FOODS_FILE, 'r') as f:
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

    return [
        f"{count}x {food_name}" if count > 1 else food_name
        for food_name, count in food_counts.items()
    ]

print(recommend_foods("Argentina", "jello", 100, 4))