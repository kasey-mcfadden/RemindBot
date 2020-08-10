from variables import nexmo_api_key, nexmo_api_secret
import nexmo

def verify(msisdn):
	client = nexmo.Client(key=nexmo_api_key, secret=nexmo_api_secret)
	
	verify_resp = client.start_verification(number=msisdn, brand='Send RemindBot')
	try:
		request_id = verify_resp['request_id']
	except:
		request_id = "Invalid"
		print "No request_id"

	if verify_resp['status'] == '0':
		print 'Started verification request_id=' + request_id
		return request_id
	else:
		print 'Error:', verify_resp['error_text']
		return request_id

def check(text, request_id):
	client = nexmo.Client(key=nexmo_api_key, secret=nexmo_api_secret)

	response = client.check_verification(request_id, code=text)

	if response['status'] == '0':
		# print 'User verification complete!'
		return "Success"
	else:
		print 'Error:', response['error_text']
		cancel = client.cancel_verification(request_id)
		print (cancel)
		return "Fail"

