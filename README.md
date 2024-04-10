### Pre-requisites:
1. Make sure Google Calendar API is enabled. Then, create an OAuth2.0 Client IDs (this will be used to generate credentials.json) and set up the OAuth consent screen properly.
2. After the set up, remember to login as the user you want to receive notification. (the workflow should be like "Login with Google")

### Notes:
1. Follow this documentation: https://cloud.google.com/scheduler/docs/tut-gcf-pub-sub to invoke cloud function periodically. Basically, it just set up a pub/sub that sends message to the cloud function according to the cron expression you've configured. When the cloud function receives the message, it will be invoked. On Cloud Function's end, set up a Pub/Sub trigger so that the function will be invoked when the message is received.
2. Use local machine to authorize Google Calendar actions using your Google Account first, then export the credentials in pickle format after setting the scope and authorization. The code block below displays the authorize screen if the not cannot find the refresh and access token. Reference: https://medium.com/@ayushbhatnagarmit/supercharge-your-scheduling-automating-google-calendar-with-python-87f752010375 

```python
creds = None
# The file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.pickle', 'wb') as token:
        pickle.dump(creds, token)
```
3. Upload the pickle file generated to the GCS. 
4. Connect the GCS with the Cloud Functions using the Python GCS Client Library
5. Force run your Cloud Scheduler job to test if the Cloud Function is working as expected.

### System Architecture on GCP
![System architecture of automation apspace timetable](https://github.com/HkFromMY/automate-apspace-timetable/assets/48499555/b9ffe211-0875-4ec1-94de-05766148c078)


