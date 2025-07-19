from flask import Flask, jsonify, Response
import requests
import os
from datetime import datetime, timedelta, timezone
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter
import redis
import json
import threading
import time
from minio import Minio
from minio.error import S3Error
from io import BytesIO

app = Flask(__name__)

__version__ = "0.0.1"

# Connect to Redis/Valkey container
REDIS_HOST = os.getenv("REDIS_HOST", "valkey-service.default.svc.cluster.local")      # For Kubernetes Deployment
# REDIS_HOST = os.getenv("REDIS_HOST", "172.20.0.2")
redis_client = redis.Redis(host=REDIS_HOST, port=6379)

# Connect to MinIO Storage
MINIO_HOST = os.getenv("MINIO_ENDPOINT", "minio-release-minio-service.default.svc.cluster.local:9000")    # For Kubernetes Deployment
# MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "172.17.0.2")
# MINIO_PORT = int(os.getenv("MINIO_PORT", "9000"))
# MINIO_HOST = f"{MINIO_ENDPOINT}:{MINIO_PORT}"
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "hivebox-data")

minio_client = Minio(
    MINIO_HOST,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# Create the bucket if it does not exist
if not minio_client.bucket_exists(MINIO_BUCKET):
    minio_client.make_bucket(MINIO_BUCKET)

# Store file to MinIO

def save_to_minio(filename: str, data: str):
    buffer = BytesIO(data.encode('utf-8'))
    minio_client.put_object(
        MINIO_BUCKET,
        filename,
        buffer,
        length=len(data.encode('utf-8')),
        content_type="application/json"
    )
    print(f"Uploaded {filename} to MinIO bucket '{MINIO_BUCKET}'")

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

@app.route("/temperature")
def temperature():
    REQUEST_COUNTER.inc()

    cache_key = "temperature_data"
    cached_data = redis_client.get(cache_key)
    if cached_data:
        return Response(cached_data, content_type="application/json")

    now = datetime.now(timezone.utc)
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
                        measured_time = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=timezone.utc)
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

        redis_client.setex(cache_key, timedelta(minutes=5), jsonify(result).get_data(as_text=True))
        return jsonify(result)
    else:
        return jsonify({"error": "No recent temperature data available."}), 404

@app.route("/metrics")
def metrics():
    REQUEST_COUNTER.inc()
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route("/store")
def store_now():
    threading.Thread(target=store_temperature_data).start()
    return jsonify({"status": "Data storage triggered"})

def store_temperature_data():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    data = {
        "timestamp": now,
        "data": []
    }

    for box_id in sensebox_ids:
        url = f"https://api.opensensemap.org/boxes/{box_id}"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            box_data = response.json()
            for sensor in box_data.get("sensors", []):
                if "temp" in sensor["title"].lower():
                    last = sensor.get("lastMeasurement", {})
                    value = last.get("value")
                    timestamp = last.get("createdAt")
                    data["data"].append({
                        "box_id": box_id,
                        "value": value,
                        "timestamp": timestamp
                    })
        except Exception as e:
            print(f"[STORE] Error fetching box {box_id}: {e}")

    filename = f"{now}.json"
    try:
        save_to_minio(filename, json.dumps(data))
    except Exception as e:
        print(f"[STORE] Failed to upload to MinIO: {e}")

def start_periodic_storage():
    def loop():
        while True:
            store_temperature_data()
            time.sleep(300)
    threading.Thread(target=loop, daemon=True).start()

start_periodic_storage()

@app.route("/readyz")
def readyz():
    reachable = 0
    for box_id in sensebox_ids:
        try:
            url = f"https://api.opensensemap.org/boxes/{box_id}"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            reachable += 1
        except:
            pass

    cache_key = "temperature_data"
    cached_data = redis_client.get(cache_key)
    cache_valid = False
    if cached_data:
        try:
            result = json.loads(cached_data)
            timestamp_str = result.get("timestamp")
            if timestamp_str:
                timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                age = datetime.now(timezone.utc) - timestamp
                if age < timedelta(minutes=5):
                    cache_valid = True
        except:
            pass

    required_reachable = (len(sensebox_ids) // 2) + 1
    if reachable >= required_reachable or cache_valid:
        return jsonify({"status": "ok"})
    else:
        return jsonify({"status": "not ready"}), 503

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')