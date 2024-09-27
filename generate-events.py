import requests
import json

# Replace with your Tito API token and account name
API_TOKEN = 'your_tito_api_token'
ACCOUNT_NAME = 'your_account_name'

# API endpoint to create an event
url = f'https://api.tito.io/v3/{ACCOUNT_NAME}/events'

# Headers for authentication and content type
headers = {
    'Authorization': f'Token token={API_TOKEN}',
    'Content-Type': 'application/json'
}

# Event data
event_data = {
    "event": {
        "title": "My New Event",
        "slug": "my-new-event",
        "description": "This is a sample event created via the Tito API.",
        "start_date": "2025-10-01",
        "end_date": "2025-10-02",
        "live": False  # False keeps the event in draft mode; True makes it live
    }
}

# Make the API request to create the event
response = requests.post(url, headers=headers, data=json.dumps(event_data))

# Check the response
if response.status_code == 201:
    print("Event created successfully!")
    print("Response:", response.json())
else:
    print(f"Failed to create event. Status code: {response.status_code}")
    print("Response:", response.text)