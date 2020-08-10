from variables import watson_user, watson_pass, watson_workspace, redirect_uri
import json
import string
import datetime
from urllib import quote_plus
import pytz

from watson_developer_cloud import ConversationV1
from getMail import insert, watch, insert_recurring, to_object, getProfile, getTimeZone
from verify import verify, check
from database import db_util

conversation = ConversationV1(
    username=watson_user,
    password=watson_pass,
    version='2017-04-21')

def watson(text, msisdn, db, tz):
	response = conversation.message(workspace_id=watson_workspace, message_input={
	    'text': '%s' % text}, context={'timezone': tz})
	
	try:
		intent = response['intents'][0]['intent']
	except:
		intent = ""

	user_status = db.check_database(msisdn)

	if user_status == 'Registered':
		if intent == 'Hello':
			output = response['output']
			resp_text = output['text'][0]
			reply = resp_text

		elif intent == 'Calendar':
			reply = 'To access your calendar, use the following link: \n%s' % (redirect_uri.replace("/code", ""))

		elif intent == 'Remind':
			try: 
				data = json.loads(db.fetch_creds(msisdn))
			
			except:
				reply = 'Setting reminders requires you to link a google calendar. Try asking me to add your calendar.'
				print reply
				return reply
			credentials = to_object(data)
			getProfile(credentials)
			sys_time = sys_date = time_string = date_string = remind_string = frequency_string = frequency = None
			
			for item in response["entities"]:
				if item["entity"] == "sys-time":
					sys_time = str(item["value"])
					time_string_index = item["location"]
					time_string = text[time_string_index[0]-1:time_string_index[1]]

				if item["entity"] == "sys-date":
					sys_date = str(item["value"])
					date_string_index = item["location"]
					date_string = text[date_string_index[0]-1:date_string_index[1]]

				if item["entity"] == "remind_string":
					remind_index = item["location"]
					remind_string = text[remind_index[0]:remind_index[1]+1]

				if item["entity"] == "frequency":
					frequency = item["value"]
					frequency_index = item["location"]
					frequency_string = text[frequency_index[0]:frequency_index[1]]
			
			print ("sys_time: ", sys_time)
			print ("sys_date: ", sys_date)

			now = datetime.datetime.now()
			print ("Now: ", datetime.datetime.strftime(now,'%Y-%m-%d %H:%M:%S'))
			
			tzID = pytz.timezone(tz)
			offset = tzID.utcoffset(now)
			now = now + offset

			now_time = datetime.datetime.strftime(now,'%H:%M:%S')
			print ("Time w offset: ", now_time)

			if not sys_date and not sys_time:
				reply = "No date or time found. Please specify a date and time and try again."
				return reply
			
			elif sys_time and not sys_date:
				sys_date = datetime.datetime.strftime(now, '%Y-%m-%d')
			
			elif sys_date and not sys_time:
				reply = "No time found. Please specify a time and try again."
				return reply

			later = datetime.datetime.strptime("%s %s" % (sys_date, sys_time), '%Y-%m-%d %H:%M:%S')

			if (later - now).total_seconds() > 0:
				date_time = ("%sT%s" % (sys_date, sys_time))
				print ("date_time: ", date_time)
				title = text
				print "Title: " + title
				
				if time_string:
					title = title.replace(time_string, "")
				
				if remind_string:
					title = title.replace(remind_string, "")
				
				if date_string:
					title = title.replace(date_string, "")
				
				if frequency:
					title = title.replace(frequency_string, "")
					print "frequency: " + frequency
					eventId = insert_recurring(credentials, title, date_time, msisdn, frequency)
				
				else:
					eventId = insert(credentials, title, date_time, msisdn)
				
				watchId = watch()
				reply = ("Reminder created: %s" % title)
			
			else:
				reply =  "Cannot create a reminder for a past event."
		
		elif intent == "Unsubscribe":
			reply = db.delete_user(msisdn)
		
		elif intent == "Register":
			reply = "You are already registered."
		
		else:
			reply = "I'm not sure what you mean. Try asking me to set a reminder."
	
	elif intent == 'Register':
		request_id = verify(msisdn)
		if request_id == "Invalid":
			reply = "Something went wrong. Please try verification again."
		else:
			reply = "Getting you verified... \nYou will soon receive a text with a verification code. Send me that code once you get it."

	elif (len(text) == 4 and text.isdigit()):
		request_id = verify(msisdn)
		ver_result = check(text, request_id)
		if ver_result == "Success":
			reply = db.add_user(msisdn)
		else:
			reply = "Failed verification. Please try again."
	else:
		reply = user_status
	
	print reply
	return reply

