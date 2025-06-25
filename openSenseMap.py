import requests

# List of senseBox IDs
sensebox_ids = [
    "5eba5fbad46fb8001b799786",
    "5c21ff8f919bf8001adf2488",
    "5ade1acf223bd80019a1011c"
]

# openSenseMap API base URL
BASE_URL = "https://api.opensensemap.org/boxes/"

# Function to get latest measurements from a senseBox
def get_latest_measurements(box_id):
    try:
        response = requests.get(f"{BASE_URL}{box_id}")
        response.raise_for_status()
        data = response.json()

        print(f"\nSenseBox: {data.get('name', box_id)}")
        print("Location:", data.get('loc', ['N/A'])[0])

        for sensor in data.get("sensors", []):
            title = sensor.get("title")
            last_value = sensor.get("lastMeasurement", {}).get("value", "N/A")
            unit = sensor.get("unit", "")
            print(f"  {title}: {last_value} {unit}")
    except Exception as e:
        print(f"Error fetching data for senseBox {box_id}: {e}")

# Loop over each box ID
for box_id in sensebox_ids:
    get_latest_measurements(box_id)
