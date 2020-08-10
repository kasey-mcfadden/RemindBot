import json

# Indeces of emails and phone numbers MUST correspond (example@gmail.com will be matched with 12345678999)
# CUSTOMIZE
# emails = ["example@gmail.com", "example2@yahoo.com", "example3@optonline.net"]
emails = []
# phones = ["12345678999", "19876543211", "18884809000"]

data = [{
	"email": "nexmo.remind.bot@gmail.com"
	}]

def attendees():
	i = 0
	for item in emails:
		user = {
			"displayName": phones[i],
			"email": item
		}
		data.append(user)
		i += 1
	return data
