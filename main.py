# 📦 Requirements
# Install these Python packages (create a requirements.txt if needed):
# pip install flask requests geopy

#📦 Requirements
# Install these Python packages (create a requirements.txt if needed):
from flask import Flask, render_template, request, redirect, url_for
import requests
from math import radians, cos, sin, asin, sqrt

app = Flask(__name__)

# Helper to calculate great-circle distance in miles between two points
def haversine(lat1, lon1, lat2, lon2):
    # convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    miles = 3959 * c  # Earth radius in miles
    return miles

# Fetch station data from Indego API
def fetch_indego_stations():
    url = "https://www.rideindego.com/stations/json/"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        stations = data.get("features", [])
        result = []
        for station in stations:
            props = station["properties"]
            coords = station["geometry"]["coordinates"]  # [lon, lat]
            result.append({
                "name": props.get("name"),
                "bikesAvailable": props.get("bikesAvailable", 0),
                "docksAvailable": props.get("docksAvailable", 0),
                "lat": coords[1],
                "lon": coords[0],
            })
        return result
    except Exception as e:
        print(f"Error fetching Indego data: {e}")
        return []

@app.route("/", methods=["GET", "POST"])
def index():
    stations = []
    user_lat = user_lon = None

    if request.method == "POST":
        try:
            user_lat = float(request.form.get("latitude"))
            user_lon = float(request.form.get("longitude"))
            radius = float(request.form.get("radius", 1.0))
            min_bikes = int(request.form.get("min_bikes", 0))
            min_docks = int(request.form.get("min_docks", 0))
        except (TypeError, ValueError):
            return redirect(url_for("index"))

        all_stations = fetch_indego_stations()

        filtered = []
        for s in all_stations:
            dist = haversine(user_lat, user_lon, s["lat"], s["lon"])
            if (
                dist <= radius
                and s["bikesAvailable"] >= min_bikes
                and s["docksAvailable"] >= min_docks
            ):
                s["distance"] = round(dist, 2)
                filtered.append(s)

        # Sort by distance ascending
        filtered.sort(key=lambda x: x["distance"])

        stations = filtered

    return render_template(
        "index.html",
        stations=stations,
        user_lat=user_lat,
        user_lon=user_lon,
    )

if __name__ == "__main__":
    app.run(debug=True)
