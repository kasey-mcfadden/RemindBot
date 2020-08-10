from variables import db_host, db_user, db_pass, db_name, logger, nexmo_number, redirect_uri, google_file
import json
import base64
import datetime

from SMS import sendSMS
from watson import watson
from base64 import b64decode
from database import db_util
from getMail import ListHistory, watch, insert, GetMessage, delMessage, delEvent, get_user_credentials, getTimeZone


db = db_util(db_host, db_user, db_pass, db_name, logger)
if not db:
    raise Exception("Database initialization failed!")

# Default lambda response
data = {
    "statusCode": 200,
    "headers": {"Content-Type": "text/html"}, 
    "body": None
}

def auth_code(code, state, redirect_uri):
    credentials = get_user_credentials(code, redirect_uri)
    msisdn = state
    if credentials:
        reply = db.add_creds(msisdn, credentials)
        if reply == 'Credentials added!':
            data["body"] = open('success.html', 'r').read()
        else:
            data["body"] = open('failure.html', 'r').read()
        sendSMS(msisdn, nexmo_number, reply)

    else:
        data["body"] = "No credentials found."
    return data["body"]

# Lambda entry point
def lambda_handler(event, context):    
    resource = event['requestContext']['resourcePath']
    
    if (resource == google_file):
            f = open('google_validation_file.html', 'r')
            data["body"] = f.read()
            return data

    elif (resource == '/auth/code'):
        try:
            code = event['queryStringParameters']['code']
            state = event['queryStringParameters']['state']
        except:
            data["body"] = open('failure.html', 'r').read()
            return data
        data["body"] = auth_code(code, state, redirect_uri)
        return data
    
    elif (resource == '/auth'):
        f = open('register.html', 'r')
        data["body"] = f.read()
        return data


    elif (resource == '/interact'):
        text = event['queryStringParameters']['text']
        msisdn = event['queryStringParameters']['msisdn']
        v_num = event['queryStringParameters']['to']

        print ('\nMessage: "%s" from %s\n' % (text, msisdn))

        send_to = msisdn    # user number
        send_from = v_num   # virtual number provided by Nexmo
        try:
            credentials = db.fetch_creds(msisdn)
            tz = getTimeZone(credentials)
        except:
            tz = 'America/New_York'

        reply = watson(text, msisdn, db, tz)
        sent = sendSMS(send_to, send_from, reply)
        data["body"] = json.dumps({"Status": "%s" % sent})

        return data


    elif (resource == '/notifications'):
        info = json.loads(event['body'])
        json_data = json.loads(b64decode(info['message']['data']))
        historyId = json_data['historyId']
        print "historyId: " + str(historyId)

        try:
            list = ListHistory(historyId-100)
            logger.debug(list)

            if (list):
                for item in list:
                    message = item["messages"][0]["id"]
                    print ("Message ID: ", message)
                    try:
                        email = GetMessage(message)
                        for item2 in email["payload"]["headers"]:
                            if item2["name"] == "From":
                                sender = item2["value"]
                            if item2["name"] == "Subject":
                                subject = item2["value"]
                        
                        if ("calendar" in sender):
                            subject = subject.replace('Notification: ','')
                            subject, trash = subject.split(" @")
                            reply = ("Reminder: " + subject)

                            snippet = email["snippet"]
                            trash, event = snippet.split("details ")
                            event, trash = event.split("When")
                            
                            trash, number = snippet.split("Where ")
                            number, trash = number.split(" (map)")
                            
                            send_from = '12034089799'
                            sent = sendSMS(number, send_from, reply)
                            print (sent)

                        delMessage(message)
                        
                        # Optionally delete events after they expire
                        # delEvent(eventId)
                    except:
                        print "Failed to get message for message id: " + message  
                        
        except:
            print "Error: No history ID"
        
        data['body'] = json.dumps({"Status": "Success"})
        return data
