import os
import logging

db_host = os.environ.get('db_host')
db_user = os.environ.get('db_user')
db_pass = os.environ.get('db_pass')
db_name = os.environ.get('db_name')

if not (db_host and db_user and db_pass and db_name):
    raise Exception("Missing DB Info")

# Cheat: If you need to validate domain name for Google
try:
    google_file = os.environ.get('google_file_name')
except:
    pass

# logger
logger = logging.getLogger()
log_level = os.environ.get('log_level')
if not log_level:
    log_level = logging.ERROR
logger.setLevel(log_level)


nexmo_number = os.environ.get('nexmo_number')
if not nexmo_number:
    raise Exception("Nexmo number needed to send SMS! Dying...")

redirect_uri = os.environ.get('redirect_uri')
if not redirect_uri:
    raise Exception("No redirect uri specified!")

watson_user = os.environ.get('watson_user')
if not watson_user:
    raise Exception("Missing watson_user!")

watson_pass = os.environ.get('watson_pass')
if not watson_pass:
    raise Exception("Missing watson_pass!")

watson_workspace = os.environ.get('watson_workspace')
if not watson_workspace:
    raise Exception("Missing watson_workspace!")

nexmo_api_key = os.environ.get('nexmo_api_key')
if not nexmo_api_key:
    raise Exception("Missing nexmo_api_key!")

nexmo_api_secret = os.environ.get('nexmo_api_secret')
if not nexmo_api_secret:
    raise Exception("Missing nexmo_api_secret!")

master_email = os.environ.get('master_email')
if not master_email:
    raise Exception("Missing master_email!")

# watson_user = 'bd41227a-d690-419f-8369-2f1950f154c9'
# watson_pass = 'AMR3Mn0FPMVf'
# watson_workspace = '67395cfa-89a1-45fa-b693-6e8df414e6e1'

# nexmo_api_key = "1cb038c8"
# nexmo_api_secret = "30479663876d1f1e"

# db_host = 'mramsunder.cvkyzrhntomg.us-east-1.rds.amazonaws.com'
# db_user = 'kasey'
# db_pass = 'kasey_mcfadden'
# db_name = 'calendar_app'
# nexmo_number = '12034089799'
# redirect_uri = "https://vlwdak19r1.execute-api.us-east-1.amazonaws.com/dev/auth/code"



