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
ACCOUNT_NAME = "Dundee-Data-Meetup"

EVENT_TITLE_PREFIX = "Dundee Data Meetup"

# Headers for authentication and content type
HEADERS = {
    "Authorization": f"Token token={API_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json",
}


# Function to get the last Tuesday of each month
def last_tuesdays(year):
    last_tuesday_dates = []
    for month in range(1, 13):  # Should be 13!
        # Find the last day of the month
        last_day = calendar.monthrange(year, month)[1]
        last_date = datetime(year, month, last_day)
        # Backtrack to the last Tuesday
        while last_date.weekday() != calendar.TUESDAY:
            last_date = last_date.replace(day=last_date.day - 1)
        last_tuesday_dates.append(last_date)
    return last_tuesday_dates


def create_event(selectedDate, content, additional_info):
    print(f"Try to create event for {selectedDate}")
    # API endpoint to create an event
    url = f"https://api.tito.io/v3/{ACCOUNT_NAME}/events"

    header = f"# Join us for the {selectedDate.strftime('%B %Y')} Dundee Data Meetup\n"

    slug = f"{selectedDate.strftime('%b-%Y').lower()}"

    # Event data
    event_data = {
        "event": {
            "title": f"{EVENT_TITLE_PREFIX}: {selectedDate.strftime('%B %Y')}",
            "slug": slug,
            "email_address": "dundeedatameetup@gmail.com",
            "location": "Dundee, UK",
            "description": header + content,
            "start_date": selectedDate.strftime("%Y-%m-%d"),
            "end_date": selectedDate.strftime("%Y-%m-%d"),
            "live": False,  # False keeps the event in draft mode; True makes it live
            "start_time": "18:00",
            "end_time": "20:00",
            "timezone": "Edinburgh",
            "homepage_url": "https://ddm.scot",
            "additional_info": additional_info,
        }
    }

    print("Event Data", event_data)

    # Make the API request to create the event
    response = requests.post(url, headers=HEADERS, data=json.dumps(event_data))

    # Check the response
    if response.status_code == 201:
        print("Event created successfully!")
        print("Response:", response.json())
        question_ids = create_questions(slug)
        if not question_ids:
            print("Failed to create questions; skipping ticket and check-in list creation.")
            return
        ticket_id = create_tickets(slug, question_ids, selectedDate)
        if not ticket_id:
            print("Failed to create tickets; skipping check-in list creation.")
            return
        create_checkin_list(slug, ticket_id)

    else:
        print(f"Failed to create event. Status code: {response.status_code}")
        print("Response:", response.text)


def create_questions(event_slug):
    print(f"Creating questions for event {event_slug}")

    question_create_url = (
        f"https://api.tito.io/v3/{ACCOUNT_NAME}/{event_slug}/questions"
    )

    # Questions to be created
    questions = [
        {
            "question": {
                "title": "We're all about staying connected! Would you be okay with us using your email address to keep you informed about future events and gather your feedback?",
                "field_type": "Select",
                "required": True,
                "options": "\n".join(["Yes", "No"]),
                "slug": "contact-consent",
            }
        },
        {
            "question": {
                "title": "To help us avoid food waste, do you intend to eat the supplied food? This really helps us with catering numbers.",
                "field_type": "Select",
                "required": True,
                "options": "\n".join(["Yes", "No"]),
                "slug": "catering-option",
            }
        },
        {
            "question": {
                "title": "How can we tailor our food to best suit your dietary preferences and needs?",
                "field_type": "Select",
                "required": True,
                "include_free_text_field": True,
                "options_free_text_field": "Other (e.g. allergies) - please specify",
                "options": "\n".join(
                    [
                        "I have no dietary requirements",
                        "I require vegetarian food",
                        "I require vegan food",
                        "I require gluten-free food",
                    ]
                ),
                "slug": "dietary-requirements",
            }
        },
    ]

    question_ids = {}

    # Create each question
    for question in questions:
        print(f'Creating question: {question["question"]["title"]}')

        question_create_response = requests.post(
            question_create_url, headers=HEADERS, data=json.dumps(question)
        )

        if question_create_response.status_code == 201:
            print("Question created successfully!")
            # print("Response:", response.json())
            question_ids[question["question"]["slug"]] = (
                question_create_response.json()["question"]["id"]
            )
        else:
            print(
                f"Failed to create question. Status code: {question_create_response.status_code}"
            )
            print("Response:", question_create_response.text)

    # Link trigger for dietary requirements question
    question_trigger_create_url = (
        f"https://api.tito.io/v3/{ACCOUNT_NAME}/{event_slug}/questions/triggers"
    )

    question_trigger_body = {
        "question_trigger": {
            "question_id": question_ids["catering-option"],
            "operator": "equal_to",
            "responses": ["Yes", ""],
            "triggerable_question_ids": [question_ids["dietary-requirements"]],
        }
    }

    question_trigger_create_response = requests.post(
        question_trigger_create_url,
        headers=HEADERS,
        data=json.dumps(question_trigger_body),
    )

    if question_trigger_create_response.status_code == 201:
        print("Trigger created successfully!")

    else:
        print(
            f"Failed to create trigger. Status code: {question_trigger_create_response.status_code}"
        )
        print("Response:", question_trigger_create_response.text)

    return question_ids


def create_tickets(event_slug, question_ids, selected_date):
    print(f"Adding tickets to event {event_slug}")

    # Tickets are actually called Releases in Tito
    # The Tickets endpoint in Tito is used for registered tickets for attendees
    url = f"https://api.tito.io/v3/{ACCOUNT_NAME}/{event_slug}/releases"

    question_ids_values = list(question_ids.values())

    body = {
        "release": {
            "title": "General admission",
            "default_quantity": 1,
            "price": 0,
            "quantity": 50,
            "state": 100, # 100 = active
            "end_at": selected_date.strftime("%Y-%m-%dT20:00:00.000+00:00"),
            "require_email": True,
            "require_name": True,
            "request_company_name": False,
            "request_vat_number": False,
            "max_tickets_per_person": 10,
            "min_tickets_per_person": 1,
            "success_message": "Thank you for booking. We can't wait to see you at the Abertay cyberQuarter ([1-3 Bell St, Dundee DD1 1LH, UK](http://maps.google.com/maps?q=56.4629194%2C-2.9741615+%28Abertay+cyberQuarter%2C+1-3+Bell+St%2C+Dundee+DD1+1LH%2C+UK%29)) soon!",
            "question_ids": question_ids_values,
        }
    }

    # Make the API request to create ticket releases
    response = requests.post(url, headers=HEADERS, data=json.dumps(body))

    # Attempt to parse the JSON response once
    try:
        data = response.json()
    except ValueError:
        data = None

    # Check the response
    if response.status_code == 201 and isinstance(data, dict):
        print("Tickets created successfully!")
        print("Response:", data)

        release = data.get("release") if isinstance(data.get("release"), dict) else None
        ticket_id = release.get("id") if release is not None else None

        if ticket_id is not None:
            return ticket_id

        print("Ticket creation response did not contain a valid release id.")
        return None

    # Non-201 status or invalid/missing JSON structure
    print(f"Failed to create tickets. Status code: {response.status_code}")
    # If JSON parsing succeeded, log it; otherwise fall back to raw text
    if data is not None:
        print("Response:", data)
    else:
        print("Response:", response.text)

    return None


def create_checkin_list(event_slug, ticket_id):
    if not ticket_id:
        print(
            f"Cannot create check-in list for event {event_slug}: "
            "no valid ticket_id was provided."
        )
        return
    print(f"Creating check-in list for event {event_slug}")

    checkins_create_url = (
        f"https://api.tito.io/v3/{ACCOUNT_NAME}/{event_slug}/checkin_lists"
    )

    checkins_create_body = {
        "checkin_list": {
            "title": "Check-ins",
            "release_ids": [ticket_id],
        }
    }

    response = requests.post(
        checkins_create_url, headers=HEADERS, data=json.dumps(checkins_create_body)
    )

    if response.status_code == 201:
        print("Check-in list created successfully!")
        print("Response:", response.json())
    else:
        print(f"Failed to create check-in list. Status code: {response.status_code}")
        print("Response:", response.text)


# Get the last Tuesday of every month in 2026
last_tuesdays_2026 = last_tuesdays(2026)

with open("event_description_template.md", "r") as file:
    content = file.read()

with open("additional_info_template.md", "r") as file:
    additional_info = file.read()

for tuesday in last_tuesdays_2026:
    print(f"Creating event for {tuesday}")
    create_event(tuesday, content, additional_info)
