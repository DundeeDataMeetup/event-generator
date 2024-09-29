import requests
import json
import os
import inquirer
import sys
from dotenv import load_dotenv

# Load values from .env file into environment variables
load_dotenv()

# Replace with your Tito API token and account name
# Set your Tito API token in a .env file as this is a secret
API_TOKEN = os.environ["API_TOKEN"]
ACCOUNT_NAME = "dundee-data-meetup"
API_BASE = f"https://api.tito.io/v3/{ACCOUNT_NAME}"

ACTION_QUESTION = [
    inquirer.List(
        "action",
        message="What action do you want to perform?",
        choices=[
            ("Create tickets", "create_tickets"),
            ("Create check-in list", "create_checkin"),
        ],
    )
]

EVENTS_CHOICE_QUESTION = [
    inquirer.Checkbox(
        "event_choice", message="Select events to perform action on", choices=[]
    )
]


def get_upcoming_events():
    # API endpoint to get upcoming events
    url = f"{API_BASE}/events"

    # Headers for authentication and content type
    headers = {
        "Authorization": f"Token token={API_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Make the API request to get the events
    response = requests.get(url, headers=headers)

    # Check the response
    if response.status_code == 200:
        print("Events retrieved successfully!")
        print("Response:", response.json())
        return response.json()["events"]
    else:
        print(f"Failed to retrieve events. Status code: {response.status_code}")
        print("Response:", response.text)
        return None


def create_tickets():
    upcoming_events = get_upcoming_events()

    upcoming_events_choices = map(lambda e: (e["title"], e["slug"]), upcoming_events)

    for e in upcoming_events_choices:
        EVENTS_CHOICE_QUESTION[0].add_choice(e)

    events_to_update = inquirer.prompt(EVENTS_CHOICE_QUESTION)

    print(events_to_update)


action_to_take = inquirer.prompt(ACTION_QUESTION)

match action_to_take["action"]:
    case "create_tickets":
        create_tickets()
    case _:
        sys.exit("Unknown action")
