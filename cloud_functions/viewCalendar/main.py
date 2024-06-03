from flask import Flask, request, make_response, jsonify
import os
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


app = Flask(__name__)

@app.route('/viewCalendar', methods=['GET'])
def view_meetings(request):

    # Set up Google Calendar API credentials
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    SERVICE_ACCOUNT_FILE = ''

    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('calendar', 'v3', credentials=credentials)
    except Exception as e:
        raise

    # Replace with your calendar ID
    CALENDAR_ID = ''

    try:
        now = datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
 
        events_result = service.events().list(calendarId=CALENDAR_ID, timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        return make_response(json.dumps(events), 200, {'Content-Type': 'application/json'})

    except HttpError as err:
    
        return make_response(jsonify({"error": f"HttpError: {err}"}), 500)
    except Exception as e:

        return make_response(jsonify({"error": str(e)}), 500)
