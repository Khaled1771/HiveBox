import os
import requests
import time
from minio import Minio

def test_end_to_end_temperature_store():
    """
    This test assumes the Flask app is running and the IP is passed via environment variable.
    Example:
        HIVEBOX_IP=172.17.0.3 pytest test_integration.py
    
    Test on Kubernetes testing namespace
    """
    # Setup
    base_url = os.getenv("HIVEBOX_URL", "http://hivebox-service.testing.svc.cluster.local:5000")
    minio_endpoint = os.getenv("MINIO_ENDPOINT", "minio-release-minio-service.default.svc.cluster.local:9000")
    minio_client = Minio(
        minio_endpoint,
        access_key=os.getenv("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "minioadmin"),
        secure=False
    )
    bucket = os.getenv("MINIO_BUCKET", "hivebox-data")

    # Trigger the store endpoint
    store_response = requests.get(f"{base_url}/store")
    assert store_response.status_code == 200
    assert store_response.json()["status"] == "Data storage triggered"

    # Wait and poll MinIO for new file
    timeout = 30
    interval = 5
    found = False

    for _ in range(timeout // interval):
        objects = minio_client.list_objects(bucket, recursive=True)
        for obj in objects:
            if obj.object_name.endswith(".json"):
                print(f"Found file: {obj.object_name}")
                data = minio_client.get_object(bucket, obj.object_name)
                content = data.read().decode("utf-8")
                assert '"data":' in content
                found = True
                break
        if found:
            break
        time.sleep(interval)

    assert found, "No .json file was uploaded to MinIO"




# ip = os.getenv("HIVEBOX_IP", "localhost")
    # minio_endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9010").replace("http://", "").replace("https://", "") # For Kubernetes
    # minio_host = os.getenv("MINIO_HOST", "localhost")
    # minio_port = os.getenv("MINIO_PORT", "9010")