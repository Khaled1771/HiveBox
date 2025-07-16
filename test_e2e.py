import os
import requests
import time
from minio import Minio

def test_end_to_end_temperature_store():
    # Setup
    ip = os.getenv("HIVEBOX_IP", "localhost")
    base_url = f"http://{ip}:5000"
    # minio_endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9010").replace("http://", "").replace("https://", "") # For Kubernetes
    minio_host = os.getenv("MINIO_HOST", "localhost")
    minio_port = os.getenv("MINIO_PORT", "9000")
    minio_endpoint = f"{minio_host}:{minio_port}"
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

    # Wait for the background thread to complete
    time.sleep(10)

    # Check MinIO for new file
    objects = minio_client.list_objects(bucket, recursive=True)
    found = False
    for obj in objects:
        if obj.object_name.endswith(".json"):
            print(f"Found file: {obj.object_name}")
            found = True
            data = minio_client.get_object(bucket, obj.object_name)
            content = data.read().decode("utf-8")
            assert '"data":' in content  # Ensure it’s JSON with data
            break

    assert found, "No .json file was uploaded to MinIO"
