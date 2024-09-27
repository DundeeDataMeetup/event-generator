import requests
import json
import calendar
from datetime import datetime

# Replace with your Tito API token and account name
API_TOKEN = 'your_tito_api_token'
ACCOUNT_NAME = 'your_account_name'

EVENT_TITLE_PREFIX = 'Dundee Data Meetup: '

# Function to get the last Tuesday of each month
def last_tuesdays(year):
    last_tuesday_dates = []
    for month in range(1, 13):
        # Find the last day of the month
        last_day = calendar.monthrange(year, month)[1]
        last_date = datetime(year, month, last_day)
        # Backtrack to the last Tuesday
        while last_date.weekday() != calendar.TUESDAY:
            last_date = last_date.replace(day=last_date.day - 1)
        last_tuesday_dates.append(last_date)
    return last_tuesday_dates

def create_event(date):
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
            "title": f'{EVENT_TITLE_PREFIX}: {tuesday.strftime('%B %Y')}',
            "slug": "my-new-event",
            "description": "This is a sample event created via the Tito API.",
            "start_date": tuesday.strftime('%Y-%m-%d') + 'T18:00:00.000Z',
            "end_date": tuesday.strftime('%Y-%m-%d') + 'T20:00:00.000Z',
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


# Get the last Tuesday of every month in 2025
last_tuesdays_2025 = last_tuesdays(2025)

for tuesday in last_tuesdays_2025:
    create_event(tuesday)