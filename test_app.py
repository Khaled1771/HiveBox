from main import app

def test_version_endpoint():
    client = app.test_client()
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.get_json()

def test_temperature_endpoint_real():
    client = app.test_client()
    response = client.get("/temperature")
    data = response.get_json()

    if response.status_code == 200:
        assert "average_temperature" in data
        assert isinstance(data["average_temperature"], (int, float))
        assert data["unit"] == "°C"
        assert data["sources"] > 0
    elif response.status_code == 404:
        assert "error" in data
        assert data["error"] == "No recent temperature data available."
    else:
        # Unexpected status
        assert False, f"Unexpected response: {response.status_code} - {data}"
