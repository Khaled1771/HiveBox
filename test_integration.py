import os
import requests

def test_temperature_endpoint_integration():
    """
    This test assumes the Flask app is running and the IP is passed via environment variable.
    Example:
        HIVEBOX_IP=172.17.0.3 pytest test_integration.py
    
    Test on Kubernetes testing namespace
    """
    ip = os.environ.get("HIVEBOX_IP", "hivebox-service.default.svc.cluster.local")
    url = f"http://hivebox-service.default.svc.cluster.local:5000/temperature"       # Kubernetes Service insted of ingress

    response = requests.get(url)
    assert response.status_code in [200, 404]

    data = response.json()
    if response.status_code == 200:
        assert "average_temperature" in data
    else:
        assert "error" in data
