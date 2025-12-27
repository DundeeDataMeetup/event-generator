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
ACCOUNT_NAME = 'JackGilmore'

EVENT_TITLE_PREFIX = 'Dundee Data Meetup'

# Headers for authentication and content type
HEADERS = {
    'Authorization': f'Token token={API_TOKEN}',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

# Function to get the last Tuesday of each month
def last_tuesdays(year):
    last_tuesday_dates = []
    for month in range(1, 2): # Should be 13!
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
            "live": False,  # False keeps the event in draft mode; True makes it live
            "start_time": "18:00",
            "end_time": "20:00",
            "timezone": "Edinburgh",
            "homepage_url": "https://ddm.scot",
        }
    }

    print("Event Data", event_data)

    # Make the API request to create the event
    response = requests.post(url, headers=HEADERS, data=json.dumps(event_data))

    # Check the response
    if response.status_code == 201:
        print("Event created successfully!")
        print("Response:", response.json())
    else:
        print(f"Failed to create event. Status code: {response.status_code}")
        print("Response:", response.text)

def create_questions(event_slug):
    url = f"https://api.tito.io/v3/{ACCOUNT_NAME}/{event_slug}/questions"

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

def add_tickets(event_slug, question_ids):
    print(f'Adding tickets to event {event_slug}')

    # Tickets are actually called Releases in Tito
    # The Tickets endpoint in Tito is used for registered tickets for attendees
    url = f'https://api.tito.io/v3/{ACCOUNT_NAME}/events/{event_slug}/releases'

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
        print("Event created successfully!")
        print("Response:", response.json())
    else:
        print(f"Failed to create event. Status code: {response.status_code}")
        print("Response:", response.text)


# Get the last Tuesday of every month in 2026
last_tuesdays_2026 = last_tuesdays(2026)

with open('event_description_template.md', 'r') as file:
    # Read the entire content of the file
    content = file.read()
    for tuesday in last_tuesdays_2026:
        print(f'Creating event for {tuesday}')
        create_event(tuesday, content)
