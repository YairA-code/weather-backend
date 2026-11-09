# "מה ללבוש היום?" - Python backend (Flask)
# מקור המידע: https://open-meteo.com  (REST API חינמי שמחזיר JSON, בלי מפתח)

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False  # כדי שעברית תוצג כמו שצריך ב-JSON
app.json.compact = False       # JSON מסודר עם שורות ורווחים, קל לקרוא בדפדפן
app.json.sort_keys = False     # לשמור על סדר השדות כמו שכתבנו
PORT = 5001

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"


def get_city(name):
    """שלב 1: הופכים שם עיר לקואורדינטות"""
    data = requests.get(GEO_URL, params={"name": name, "count": 1}, timeout=10).json()
    if "results" not in data:
        raise ValueError(f"City '{name}' not found")
    c = data["results"][0]
    return {"name": c["name"], "country": c["country"], "lat": c["latitude"], "lon": c["longitude"]}


def get_weather(name):
    """שלב 2: מביאים את מזג האוויר העכשווי לפי הקואורדינטות"""
    city = get_city(name)
    params = {
        "latitude": city["lat"],
        "longitude": city["lon"],
        "current": "temperature_2m,wind_speed_10m,precipitation",
    }
    data = requests.get(WEATHER_URL, params=params, timeout=10).json()
    return {
        "city": city["name"],
        "country": city["country"],
        "temperature": data["current"]["temperature_2m"],
        "wind": data["current"]["wind_speed_10m"],
        "rain": data["current"]["precipitation"],
    }


def recommend_outfit(w):
    """שלב 3: הלוגיקה שלנו - ממליצים מה ללבוש"""
    t = w["temperature"]
    if t >= 28:
        items = ["גופייה ומכנס קצר", "כובע", "בקבוק מים"]
    elif t >= 20:
        items = ["חולצה קצרה", "ג'ינס"]
    elif t >= 12:
        items = ["סווטשירט", "מכנס ארוך"]
    else:
        items = ["מעיל חם", "צעיף", "כפפות"]
    if w["rain"] > 0:
        items.append("מטרייה")
    if w["wind"] > 30:
        items.append("מעיל רוח")
    return items


# Endpoint 1: מזג אוויר + המלצת לבוש   ->  GET /outfit/Tel Aviv
@app.route("/outfit/<city>")
def outfit(city):
    try:
        weather = get_weather(city)
        return jsonify({**weather, "wear": recommend_outfit(weather)})
    except (ValueError, requests.RequestException) as e:
        return jsonify({"error": str(e)}), 404


# Endpoint 2: לאיזו עיר כדאי לטוס? (הכי קרובה ל-24 מעלות)
#   ->  GET /trip?cities=London,Eilat,Paris
@app.route("/trip")
def trip():
    cities = request.args.get("cities")
    if not cities:
        return jsonify({"error": "send ?cities=a,b,c"}), 400
    try:
        all_w = [get_weather(n.strip()) for n in cities.split(",")]
    except (ValueError, requests.RequestException) as e:
        return jsonify({"error": str(e)}), 404

    all_w.sort(key=lambda w: abs(w["temperature"] - 24))
    return jsonify({
        "bestCity": all_w[0]["city"],
        "ranking": [f"{w['city']}: {w['temperature']}°C" for w in all_w],
    })


if __name__ == "__main__":
    print(f"Python server running on http://localhost:{PORT}")
    app.run(port=PORT)
