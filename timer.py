import time

class Timer():
	def __init__(self):
		self.startTime = time.time()


	def span(self):
		span = time.time() - self.startTime
		hour = span // 3600
		minute = (span - hour * 3600) // 60
		second = (span - hour * 3600 - minute * 60)
		print(f'總花費時間{int(hour)}小時{int(minute)}分鐘{int(second)}秒')


	def reset(self):
		self.startTime = time.time()