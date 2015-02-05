class Ceremony():
	def __init__(self, name):
		self.name = name
		self.hosts = []
		self.awards = []
		self.location = None
		self.dateTime = None


class Awards():
	def __init__(self, name):
		self.name = name
		self.presenters = []
		self.nominees = []
		self.winner = "none"

