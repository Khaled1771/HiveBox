# test_integration.py

import requests

def test_temperature_endpoint_integration():
    """
    This test assumes the Flask app is running locally at port 5000.
    Make sure `python main.py` or your container is running before testing.
    """
    url = "http://localhost:5000/temperature"
    response = requests.get(url)
    assert response.status_code in [200, 404]  # Either successful or no data

    data = response.json()
    if response.status_code == 200:
        assert "average_temperature" in data
        assert "status" in data  # Optional: if added later
    else:
        assert "error" in data
