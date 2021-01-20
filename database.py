import MySQLdb

class DBManager():
	def __init__(self, config):
		try:
			self.db = MySQLdb.connect(
			host=config['DATABASE']['CONNECT_HOST'],
			user=config['DATABASE']['CONNECT_USER'],
			passwd=config['DATABASE']['CONNECT_PASSWD'],
			db=config['DATABASE']['CONNECT_DB'])
			self.cursor = self.db.cursor()
		except Exception as e:
			print(e)


	def query(self, id):
		cmd = f"SELECT timestamp FROM account WHERE instagram_id='{id}'"
		exist = self.cursor.execute(cmd)
		if exist == 1:
			return self.cursor.fetchone()[0]
		else:
			return 0


	def update(self, id, timestamp):
		cmd = f"REPLACE INTO account(instagram_id, timestamp) VALUES('{id}', '{timestamp}')"
		self.cursor.execute(cmd)
		self.db.commit()


	def delete(self, id):
		cmd = f"DELETE FROM account WHERE instagram_id='{id}'"
		self.cursor.execute(cmd)
		self.db.commit()


	def clear(self):
		self.db.close()