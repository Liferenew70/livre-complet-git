from flask import Flask, render_template_string, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(_name_)

# Fonction pour obtenir les matchs à venir dans les 48 prochaines heures
def get_upcoming_matches():
    now = datetime.now()
    end_time = now + timedelta(hours=48)
    url = "https://api.sofascore.com/api/v1/sport/ice-hockey/events/upcoming"
    response = requests.get(url)
    data = response.json()
    
    matchs = []

    for event in data.get('events', []):
        event_time = datetime.fromtimestamp(event['startTimestamp'])
        if now <= event_time <= end_time:
            match = {
                "id": event['id'],
                "home": event['homeTeam']['name'],
                "away": event['awayTeam']['name'],
                "start_time": event_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            matchs.append(match)

    return matchs

# Page HTML principale
with open('index.html', 'r', encoding='utf-8') as f:
    html_page = f.read()

@app.route('/')
def index():
    return render_template_string(html_page)

@app.route('/api/matchs')
def get_matchs():
    matchs = get_upcoming_matches()
    return jsonify(matchs)

@app.route('/api/predict/<int:match_id>')
def predict_score(match_id):
    try:
        url = f"https://api.sofascore.com/api/v1/event/{match_id}/statistics"
        response = requests.get(url)
        data = response.json()

        # Calcul des pourcentages de victoire
        home_wins_percentage = 50  # Valeur par défaut
        draw_percentage = 20  # Valeur par défaut pour un match nul
        away_wins_percentage = 30  # Valeur par défaut

        # Ajuster les pourcentages en fonction des stats de SofaScore
        if 'statistics' in data:
            home_wins_percentage += 10  # L'équipe à domicile gagne souvent
            away_wins_percentage -= 5  # L'équipe extérieure a moins de chances
            draw_percentage = 0  # Suppression de match nul

        prediction = {
            "home_win": home_wins_percentage,
            "draw": draw_percentage,
            "away_win": away_wins_percentage
        }

        return jsonify(prediction)

    except Exception as e:
        print(e)
        return jsonify({"home_win": 0, "draw": 0, "away_win": 0})

if _name_ == "_main_":
    app.run(host="0.0.0.0", port=5000, debug=True)