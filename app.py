from flask import Flask, render_template, request, jsonify
import requests
import pandas as pd
import os

app = Flask(__name__)

GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY_HERE"

# Load Excel once
df = pd.read_excel("locations (2).xlsx", engine="openpyxl")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/calculate", methods=["POST"])
def calculate():

    data = request.json
    dc_codes = data.get("locations")

    if len(dc_codes) < 2:
        return jsonify({"error": "Minimum 2 DC codes required"}), 400

    coordinates = []

    for code in dc_codes:
        row = df[df["im_location"] == code]

        if row.empty:
            return jsonify({"error": f"DC Code {code} not found"}), 400

        lat = row.iloc[0]["latitude"]
        lng = row.iloc[0]["longitude"]

        coordinates.append({"lat": lat, "lng": lng})

    origin = f"{coordinates[0]['lat']},{coordinates[0]['lng']}"
    destination = f"{coordinates[-1]['lat']},{coordinates[-1]['lng']}"

    waypoints = "|".join(
        f"{loc['lat']},{loc['lng']}"
        for loc in coordinates[1:-1]
    )

    url = "https://maps.googleapis.com/maps/api/directions/json"

    params = {
        "origin": origin,
        "destination": destination,
        "key": GOOGLE_API_KEY
    }

    if waypoints:
        params["waypoints"] = waypoints

    response = requests.get(url, params=params)
    result = response.json()

    if result["status"] != "OK":
        return jsonify({"error": result["status"]}), 400

    total_distance = 0
    total_duration = 0

    for leg in result["routes"][0]["legs"]:
        total_distance += leg["distance"]["value"]
        total_duration += leg["duration"]["value"]

    return jsonify({
        "distance_km": round(total_distance / 1000, 2),
        "duration_hr": round(total_duration / 3600, 2),
        "coordinates": coordinates
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
