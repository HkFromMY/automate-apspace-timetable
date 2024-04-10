import base64
import functions_framework

from googleapiclient.discovery import build 
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.cloud import storage
from google.cloud.storage import Blob
import pickle
import requests
import pandas as pd 
from datetime import date, timedelta
import os 

TIMETABLE_URI = os.environ.get("TIMETABLE_URI", "Specified environment variable is not set.")
CRED_BUCKET = os.environ.get("CRED_BUCKET", "Specified environment variable is not set.")
PROJECT_ID = os.environ.get("PROJECT_ID", "Specified environment variable is not set.")
STUDENT_INTAKE = os.environ.get("STUDENT_INTAKE", "Specified environment variable is not set.")
STUDENT_GROUP = os.environ.get("STUDENT_GROUP", "Specified environment variable is not set.")

def get_timetable():
    response = requests.get(
        TIMETABLE_URI, 
        headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }
    )

    timetable = response.json()
    timetable = pd.DataFrame(timetable)

    return timetable

# Triggered from a message on a Cloud Pub/Sub topic.
@functions_framework.cloud_event
def hello_pubsub(cloud_event):
    # Print out the data from Pub/Sub, to prove that it worked
    print(base64.b64decode(cloud_event.data["message"]["data"]))

    storage_client = storage.Client(project=PROJECT_ID)
    source_bucket = storage_client.get_bucket(CRED_BUCKET)
    pickle_file = source_bucket.blob('token.pickle')
    creds_str = pickle_file.download_as_string()

    print("Loading pickle file...")
    creds = pickle.loads(creds_str)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        pickle_out = pickle.dumps(creds)
        pickle_file.upload_from_string(pickle_out)

    service = build('calendar', 'v3', credentials=creds)

    # get timetable data
    timetable = get_timetable()

    # Call the Calendar API  
    # calculate week range
    today = date.today() + timedelta(days=7)
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)

    # convert to string
    start = start.strftime('%Y-%m-%d')
    end = end.strftime('%Y-%m-%d')

    timetable_next_week = timetable.loc[(timetable['INTAKE'] == STUDENT_INTAKE) & ((timetable['DATESTAMP_ISO'] >= start) & (timetable['DATESTAMP_ISO'] <= end)) & (timetable['GROUPING'] == STUDENT_GROUP)]
    if timetable_next_week.shape[0] >= 0:
        for index in timetable_next_week.index:
            event = {
                'summary': timetable_next_week['MODULE_NAME'][index],
                'location': timetable_next_week['ROOM'][index],
                'start': {
                    'dateTime': timetable_next_week['TIME_FROM_ISO'][index]
                },
                'end': {
                    'dateTime': timetable_next_week['TIME_TO_ISO'][index]
                }
            }

            events_result = service.events().insert(calendarId='primary', body=event).execute()
            print("Event created: %s" % (events_result.get('htmlLink')))


