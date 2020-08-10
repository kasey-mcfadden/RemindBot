import pymysql
import base64

class db_util:
	connection = None
	cursor = None

	def __init__(self, host, user, password, db, logger):
		self.connection = pymysql.connect(host = host, 
			user = user, 
			password = password, 
			db = db, 
			charset='utf8mb4', 
			connect_timeout = 5)
		self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)
		self.logger = logger


	def add_user(self, msisdn):
		sql = 'insert into phone_numbers (id) values (%s)'
		result = self.cursor.execute(sql, msisdn)
		self.connection.commit()

		if result == 1:
			reply = "User verified! Added to database."
		else:
			reply = "Your info could not be added. Please try again."

		return reply


	def fetch_creds(self, msisdn):
		sql = 'select credentials from phone_numbers where id = %s'
		result = self.cursor.execute(sql, msisdn)
		outcome = self.cursor.fetchall()

		try:
			encoded_creds = outcome[0]['credentials']
			credentials = base64.b64decode(encoded_creds)
		except TypeError, e:
			print e
			credentials = ''
		except Exception, e:
			print e
			credentials = ''

		print ("Creds: ", credentials)
		return credentials


	def delete_user(self, msisdn):
		sql = 'delete from phone_numbers where id=%s'
		result = self.cursor.execute(sql, msisdn)
		self.connection.commit()

		if result == 1:
			reply = "You are being unsubscribed. To complete the unsubscription process, please remove Google account access for \'Remind Bot\' by visiting: \nmyaccount.google.com/permissions."
		else:
			reply = "You could not be unsubscribed. Please try again."

		return reply


	def add_creds(self, msisdn, credentials):
		if self.fetch_creds(msisdn):
			return "Credentials already stored"

		encoded = base64.b64encode(credentials)
		print ("Encoded: ", encoded)
		sql = "insert into phone_numbers (id, credentials) values (%s, %s) on duplicate key update credentials=%s"
		result = 1
		
		try:
			self.cursor.execute(sql, (msisdn, encoded, encoded))
			self.connection.commit()
		except Exception, e:
			print e
			result = 0

		if result:
			reply = 'Credentials added!'
		else:
			reply = 'Fail'
		print reply
		return reply


	def check_database(self, msisdn):
		sql = 'select id from phone_numbers where id=%s'
		result = self.cursor.execute(sql, msisdn)
		self.connection.commit()
		outcome = self.cursor.fetchall()

		if result == 0:
			reply = "It appears you\'re not a registered user. Ask me to register if you would like to use this service."
		else:
			reply = "Registered"

		return reply

