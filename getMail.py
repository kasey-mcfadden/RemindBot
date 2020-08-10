from __future__ import print_function
from variables import logger, master_email
import httplib2
import json
import logging

from attendees import attendees
from googleapiclient import discovery
from oauth2client import file, client, tools
from oauth2client.file import Storage
from httplib2 import Http

SCOPES = ['https://mail.google.com/', 'https://www.googleapis.com/auth/calendar']
APPLICATION_NAME = 'Remind Bot ID'

def get_default_credentials():
    json_data=open('default_credentials.json').read()
    data = json.loads(json_data)

    credentials = to_object(data)
    
    access_token = credentials.token_response['access_token']
    refresh_token = credentials.token_response['refresh_token']
    print ("Default access token: %s" % access_token)
    print ("Default refresh token: %s" % refresh_token)
    return credentials


def get_user_credentials(code, redirect_uri):
    flow = client.flow_from_clientsecrets(
        'client_secrets.json',
        scope=SCOPES,
        redirect_uri=redirect_uri)
    flow.params['access_type'] = 'offline'         # offline access
    flow.params['include_granted_scopes'] = True   # incremental auth
    
    try:
        old_data = flow.step2_exchange(code)
        data = old_data.__dict__
        json_data = old_data.to_json()
    except:
        string = "none"
        return string

    credentials = to_object(data)
    
    access_token = credentials.token_response['access_token']
    refresh_token = credentials.token_response['refresh_token']
    print ("Access Token: %s" % access_token)
    print ("Refresh Token: %s" % refresh_token)
    print ("Credentials: ", credentials)

    return json_data


def to_object(data):
    credentials = client.OAuth2Credentials(
        data['access_token'],
        data['client_id'],
        data['client_secret'],
        data['refresh_token'],
        data['token_expiry'],
        data['token_uri'],
        data['user_agent'],
        revoke_uri=data.get('revoke_uri', None),
        id_token=data.get('id_token', None),
        id_token_jwt=data.get('id_token_jwt', None),
        token_response=data.get('token_response', None),
        scopes=SCOPES,
        token_info_uri=data.get('token_info_uri', None))
    return credentials


def getProfile(credentials):
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    getProfile = service.users().getProfile(userId='me').execute()

    email = getProfile['emailAddress']
    print ("User: ", email)
    return (email)


def getTimeZone(credentials):
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http, cache_discovery=False)

    tz_info = service.settings().get(setting="timezone").execute()

    tz = tz_info['value']
    return tz


def insert(credentials, title, time, msisdn):
    tz = getTimeZone(credentials)
    user_id = getProfile(credentials)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http, cache_discovery=False)
    attend = attendees()
    
    EVENT = {
        'summary': '%s' % title,
        "start": {
            "dateTime": "%s" % time,
            "timeZone": tz
            },
        "end": {
            "dateTime": "%s" % time,
            "timeZone": tz
            },
        "location": msisdn,
        "attendees": attend,
        "reminders": {
        "overrides": [
          {
            "method": "email",
            "minutes": 0
          }
        ],
        "useDefault": "false"
      }
    }
    resp = service.events().insert(calendarId=user_id, body=EVENT).execute()
    title = str(resp['summary'])
    eventId = str(resp['id'])
    print ("Event created: ", title, " at ", time, "(", tz, ")")
    return eventId
    

def insert_recurring(credentials, title, time, msisdn, frequency):
    tz = getTimeZone(credentials)
    user_id = getProfile(credentials)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http, cache_discovery=False)

    EVENT = {
        'summary': '%s' % title,
        "location": msisdn,
        "start": {
            "dateTime": "%s" % time,
            "timeZone": tz
            },
        "end": {
            "dateTime": "%s" % time,
            "timeZone": tz
            },
        "recurrence": [
        "RRULE:FREQ=%s;COUNT=10" % frequency
        ],
        "reminders": {
        "overrides": [
          {
            "method": "email",
            "minutes": 0
          }
        ],
        "useDefault": "false"
      }
    }

    resp = service.events().insert(calendarId=user_id, body=EVENT).execute()
    title = str(resp['summary'])
    eventId = str(resp['id'])
    print ("Event created: ", title, " at ", time, ",", frequency, "(", tz, ")")
    return eventId


def delEvent(credentials, eventId):
    user_id = getProfile(credentials)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    delete = service.events().delete(calendarId=user_id, eventId=eventId).execute()

    return delete


def watch():
    user_id = master_email
    credentials = get_default_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http, cache_discovery=False)

    try:
        stop = service.users().stop(userId=user_id).execute()
    except:
        print ("No watch functions to stop.")

    request = {
        'labelIds': ['INBOX', 'CATEGORY_PERSONAL'],
        'topicName': 'projects/remind-bot-175816/topics/remind-topic'
    }

    watch_results = service.users().watch(userId=user_id, body=request).execute()
    id = str(watch_results["historyId"])
    return id
    # expiration of watch function is 7 days


def GetMessage(msg_id):
    user_id = master_email
    credentials = get_default_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    message = service.users().messages().get(format='full', userId=user_id, id=msg_id).execute()
    return message


def delMessage(msg_id):
    user_id = master_email
    credentials = get_default_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    delete = service.users().messages().delete(userId=user_id, id=msg_id).execute()

    return delete


def ListHistory(start_history_id):
    user_id = master_email
    credentials = get_default_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    history = (service.users().history().list(userId=user_id, labelId="Label_1", startHistoryId=start_history_id, historyTypes='messageAdded').execute())
    changes = history['history'] if 'history' in history else []
    while 'nextPageToken' in history:
        page_token = history['nextPageToken']
        history = (service.users().history().list(userId=user_id, labelId="Label_1", startHistoryId=start_history_id, historyTypes='messageAdded', pageToken=page_token).execute())
        changes.extend(history['history'])

    return changes
