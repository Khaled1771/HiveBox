from flask import Flask, jsonify
import requests
from datetime import datetime, timedelta

app = Flask(__name__)

# App version
__version__ = "0.0.1"

# List of senseBox IDs (use your actual ones)
sensebox_ids = [
    "5eba5fbad46fb8001b799786",
    "5c21ff8f919bf8001adf2488",
    "5ade1acf223bd80019a1011c"
]

@app.route("/version")
def version():
    return jsonify({"version": __version__})


@app.route("/temperature")
def temperature():
    now = datetime.utcnow()
    cutoff = now - timedelta(hours=1)

    temps = []

    for box_id in sensebox_ids:
        url = f"https://api.opensensemap.org/boxes/{box_id}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            box_data = response.json()

            for sensor in box_data.get("sensors", []):
                if "temp" in sensor["title"].lower():  # Flexible match: "Temperature"
                    last = sensor.get("lastMeasurement", {})
                    timestamp = last.get("createdAt")
                    value = last.get("value")

                    if timestamp:
                        measured_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ")
                        if measured_time > cutoff:
                            temps.append(float(value))
        except Exception as e:
            print(f"Error fetching data from box {box_id}: {e}")

    if temps:
        avg_temp = sum(temps) / len(temps)
        return jsonify({"average_temperature": round(avg_temp, 2), "unit": "°C", "sources": len(temps)})
    else:
        return jsonify({"error": "No recent temperature data available."}), 404


if __name__ == "__main__":
    app.run(debug=True)
