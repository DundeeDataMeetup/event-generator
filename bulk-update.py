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

# Global headers for authentication and content type
HEADERS = {
    "Authorization": f"Token token={API_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

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

    # Make the API request to get the events
    response = requests.get(url, headers=HEADERS)

    # Check the response
    if response.status_code == 200:
        print("Events retrieved successfully!")
        return response.json()["events"]
    else:
        print(f"Failed to retrieve events. Status code: {response.status_code}")
        print("Response:", response.text)
        return None


def create_questions(slug: str):
    url = f"{API_BASE}/{slug}/questions"

    questions = [
        {
            "question": {
                "title": "We're all about staying connected! Would you be okay with us using your email address to keep you informed about future events and gather your feedback?",
                "field_type": "Select",
                "required": True,
                "options": "\n".join([
                    "Yes",
                    "No"
                ]),
            }
        },
        {
            "question": {
                "title": "How can we tailor our food to best suit your dietary preferences and needs?",
                "field_type": "Select",
                "required": True,
                "options": "\n".join([
                    "I have no dietary requirements",
                    "I prefer vegetarian food",
                    "I prefer vegan food",
                    "I prefer gluten-free food"
                ]),
            }
        },
    ]

    question_ids = []

    for question in questions:
        response = requests.post(url, headers=HEADERS, data=json.dumps(question))

        if response.status_code == 201:
            print("Question created successfully!")
            # print("Response:", response.json())
            question_ids.append(response.json()["question"]["id"])
        else:
            print(f"Failed to create question. Status code: {response.status_code}")
            print("Response:", response.text)

    return question_ids


def create_tickets():
    upcoming_events = get_upcoming_events()

    upcoming_events_choices = map(lambda e: (e["title"], e["slug"]), upcoming_events)

    for e in upcoming_events_choices:
        EVENTS_CHOICE_QUESTION[0].add_choice(e)

    events_to_update = inquirer.prompt(EVENTS_CHOICE_QUESTION)

    events_to_update_slugs = events_to_update["event_choice"]

    for event_slug in events_to_update_slugs:
        print(f"Creating questions for event ticket release: {event_slug}")
        question_ids = create_questions(event_slug)

        print(f"Creating ticket release for event: {event_slug}")

        # API endpoint to create ticket releases
        url = f"{API_BASE}/{event_slug}/releases"

        print(url)

        # Body of the request
        body = {
            "release": {
                "title": "General admission",
                "default_quantity": 1,
                "price": 0,
                "quantity": 50,
                "state": 100,
                "require_email": True,
                "require_name": True,
                "request_company_name": False,
                "request_vat_number": False,
                "max_tickets_per_person": 10,
                "min_tickets_per_person": 1,
                "success_message": "Thank you for booking. We can't wait to see you at the Abertay cyberQuarter ([1-3 Bell St, Dundee DD1 1LH, UK](http://maps.google.com/maps?q=56.4629194%2C-2.9741615+%28Abertay+cyberQuarter%2C+1-3+Bell+St%2C+Dundee+DD1+1LH%2C+UK%29)) soon!",
                "question_ids": question_ids,
            }
        }

        # Make the API request to create ticket releases
        response = requests.post(url, headers=HEADERS, data=json.dumps(body))

        # Check the response
        if response.status_code == 201:
            print("Ticket release created successfully!")
            print("Response:", response.json())
        else:
            print(
                f"Failed to create ticket release. Status code: {response.status_code}"
            )
            print("Response:", response.text)


action_to_take = inquirer.prompt(ACTION_QUESTION)

match action_to_take["action"]:
    case "create_tickets":
        create_tickets()
    case _:
        sys.exit("Unknown action")
