from variables import nexmo_api_key, nexmo_api_secret
import nexmo
    
def sendSMS(send_to, send_from, content): 
    client = nexmo.Client(key=nexmo_api_key, secret=nexmo_api_secret)

    if isinstance (content, unicode):
        sms_type = 'unicode'
    else:
        sms_type = 'text'

    result = client.send_message({
        'text': content,
        'from': send_from, 
        'to': send_to,
        'type': sms_type
        })
    
    # get returned http code from JSON data
    response = result['messages'][0]
    
    # return success message if code = 0 (success), otherwise indicate error
    if response['status'] == '0':
        return "Message sent to %s: '%s'" % (send_to, content)
    else:
        return 'Error:', response['error-text']
