from flask import Flask, jsonify
import requests
import os
from datetime import datetime, timedelta
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter
from flask import Response
import redis

app = Flask(__name__)

__version__ = "0.0.1"

# Connect to Redis/Valkey contaier
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=REDIS_HOST, port=6379)

# 1. Load senseBox IDs from environment variable
sensebox_ids = os.getenv("SENSEBOX_IDS", "").split(",")
if not any(sensebox_ids):
    sensebox_ids = [
        "5eba5fbad46fb8001b799786",
        "5c21ff8f919bf8001adf2488",
        "5ade1acf223bd80019a1011c"
    ]

# Prometheus metric
REQUEST_COUNTER = Counter('hivebox_requests_total', 'Total requests received')

@app.route("/version")
def version():
    REQUEST_COUNTER.inc()
    return jsonify({"version": __version__})

# Update /temperature endpoint to use valkey caching
@app.route("/temperature")
def temperature():
    REQUEST_COUNTER.inc()

    cache_key = "temperature_data"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return Response(cached_data, content_type="application/json")

    now = datetime.utcnow()
    cutoff = now - timedelta(hours=1)
    temps = []

    for box_id in sensebox_ids:
        url = f"https://api.opensensemap.org/boxes/{box_id}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            box_data = response.json()

            for sensor in box_data.get("sensors", []):
                if "temp" in sensor["title"].lower():
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
        if avg_temp < 10:
            status = "Too Cold"
        elif 11 <= avg_temp <= 36:
            status = "Good"
        else:
            status = "Too Hot"

        result = {
            "average_temperature": round(avg_temp, 2),
            "unit": "°C",
            "status": status,
            "sources": len(temps)
        }

        # Cache the result for 5 minutes
        redis_client.setex(cache_key, timedelta(minutes=5), jsonify(result).get_data(as_text=True))
        return jsonify(result)
    else:
        return jsonify({"error": "No recent temperature data available."}), 404



# 3. Prometheus metrics endpoint
@app.route("/metrics")
def metrics():
    REQUEST_COUNTER.inc()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
