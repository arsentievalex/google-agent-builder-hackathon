from flask import Flask, request, make_response, jsonify
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import logging
import json
from datetime import datetime, timedelta
import os

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

@app.route('/createMeeting', methods=['POST'])
def create_meeting(request):

    request_json = request.get_json(silent=True)

    if not request_json or 'to_email' not in request_json or 'summary' not in request_json or 'description' not in request_json:
        return make_response(json.dumps({"error": "Missing 'to_email', 'summary', or 'description' in the request"}), 400,
                             {'Content-Type': 'application/json'})


    # Set up Google Calendar API credentials
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    SERVICE_ACCOUNT_FILE = ''

    # Initialize the Google Calendar service outside the route to avoid reinitializing on each request
    try:
        # credentials = service_account.Credentials.from_service_account_file(
        #     SERVICE_ACCOUNT_FILE, scopes=SCOPES)

        with open('token.json', 'r') as token_file:
            credentials_info = json.load(token_file)
            credentials = Credentials.from_authorized_user_info(credentials_info)

        service = build('calendar', 'v3', credentials=credentials)
        logging.info("Google Calendar API service initialized successfully.")
    except Exception as e:
        logging.error(f"Error setting up Google Calendar API: {e}")
        service = None

    # Replace with your calendar ID
    CALENDAR_ID = ''

    if service is None:
        logging.error("Google Calendar API service is not initialized.")
        return make_response(jsonify({"error": "Google Calendar API service is not initialized."}), 500)

    # get variables from request
    summary = request_json['summary']
    to_email = request_json['to_email']
    description = request_json['description']

    try:
        event = {
        'summary': summary,
        'description': description,
        'start': {
            'dateTime': "2024-06-03T17:00:00+02:00",
            'timeZone': "Europe/Warsaw",
        },
        'end': {
            'dateTime': "2024-06-03T17:30:00+02:00",
            'timeZone': "Europe/Warsaw",
        },
        'attendees': [{'email': to_email}]
        }

        event = service.events().insert(calendarId=CALENDAR_ID, body=event).execute()


        response = {
            "message": "Event created successfully",
        }

        # return make_response(jsonify(updated_event), 200)
        return make_response(json.dumps(response), 200, {'Content-Type': 'application/json'})

    except Exception as e:
        logging.error(f"Error creating the event: {e}")
        return make_response(jsonify({"error": str(e)}), 500)
