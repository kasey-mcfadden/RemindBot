from __future__ import print_function
import httplib2
import os
import json
import dumper
import pprint

from googleapiclient import discovery
from oauth2client import file, client, tools
from oauth2client.file import Storage
from httplib2 import Http
from googleapiclient import discovery

SCOPES = ['https://mail.google.com/', 'https://www.googleapis.com/auth/calendar']
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Web client 1'

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

def get_credentials():
    credential_path = ('default_credentials.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    # dumper.dump(credentials)
    token = credentials.token_response['access_token']
    # print ("Token:\n", token)
    return credentials


if __name__ == '__main__':
    get_credentials()