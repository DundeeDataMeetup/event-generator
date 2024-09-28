import requests
import json
import calendar
import os
from datetime import datetime
from dotenv import load_dotenv

# Load values from .env file into environment variables
load_dotenv()

# Replace with your Tito API token and account name
# Set your Tito API token in a .env file as this is a secret
API_TOKEN = os.environ["API_TOKEN"]
ACCOUNT_NAME = 'dundee-data-meetup'

EVENT_TITLE_PREFIX = 'Dundee Data Meetup'

# Function to get the last Tuesday of each month
def last_tuesdays(year):
    last_tuesday_dates = []
    for month in range(2, 13): # Should be 13!
        # Find the last day of the month
        last_day = calendar.monthrange(year, month)[1]
        last_date = datetime(year, month, last_day)
        # Backtrack to the last Tuesday
        while last_date.weekday() != calendar.TUESDAY:
            last_date = last_date.replace(day=last_date.day - 1)
        last_tuesday_dates.append(last_date)
    return last_tuesday_dates

def create_event(selectedDate, content):
    print(f'Try to create event for {selectedDate}')
    # API endpoint to create an event
    url = f'https://api.tito.io/v3/{ACCOUNT_NAME}/events'

    # Headers for authentication and content type
    headers = {
        'Authorization': f'Token token={API_TOKEN}',
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    header = f'# Join us for the {selectedDate.strftime('%B %Y')} Dundee Data Meetup\n'

    # Event data
    event_data = {
        "event": {
            "title": f'{EVENT_TITLE_PREFIX}: {selectedDate.strftime('%B %Y')}',
            "slug": f'{selectedDate.strftime('%b-%Y').lower()}',
            "email_address": "dundeedatameetup@gmail.com",
            "location": "Dundee, UK",
            "description": header + content,
            "start_date": selectedDate.strftime('%Y-%m-%d'),
            "end_date": selectedDate.strftime('%Y-%m-%d'),
            "live": False  # False keeps the event in draft mode; True makes it live
        }
    }

    print("Event Data", event_data)

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

with open('event_description_template.md', 'r') as file:
    # Read the entire content of the file
    content = file.read()
    for tuesday in last_tuesdays_2025:
        create_event(tuesday, content)