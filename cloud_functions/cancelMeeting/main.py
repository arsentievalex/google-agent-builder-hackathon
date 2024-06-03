from flask import Flask, request, make_response, jsonify
from google.oauth2 import service_account
from googleapiclient.discovery import build
import logging
import json
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

@app.route('/cancelMeeting', methods=['POST'])
def cancel_meeting(request):

    request_json = request.get_json(silent=True)

    if not request_json or 'to_email' not in request_json or 'subject' not in request_json or 'content' not in request_json or 'event_id' not in request_json:
        return make_response(json.dumps({"error": "Missing event_id, 'to_email', 'subject', or 'content' in the request"}), 400,
                             {'Content-Type': 'application/json'})


    # Set up Google Calendar API credentials
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    SERVICE_ACCOUNT_FILE = ''

    # Initialize the Google Calendar service outside the route to avoid reinitializing on each request
    try:
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE, scopes=SCOPES)
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
    event_id = request_json['event_id']
    to_email = request_json['to_email']
    subject = request_json['subject']
    body = request_json['content']

    try:
        # delete event
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()

        # run send email function
        send_email(to_email, subject, body)

        response = {
            "message": "Event cancelled and email sent successfully",
        }

        # return make_response(jsonify(updated_event), 200)
        return make_response(json.dumps(response), 200, {'Content-Type': 'application/json'})

    except Exception as e:
        logging.error(f"Error moving the event: {e}")
        return make_response(jsonify({"error": str(e)}), 500)


def send_email(to_email, subject, body):

    from_email = ""
    password = ""

    # Create the email
    msg = MIMEMultipart()

    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Connect to Gmail's SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    # Login to your Gmail account
    server.login(from_email, password)

    # Send the email
    server.send_message(msg)

    server.quit()
