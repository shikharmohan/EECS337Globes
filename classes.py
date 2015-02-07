class user:
    def __init__(self):
        self.score = 1
        self.tweetList = []
        self.userName = ''
        self.userId = 0

class tweet:
    def __init__(self):
        self.text = ''
        self.score = 1
        self.tweetId = 0

class event:
    def __init__(self):
        self.name = ''
        self.id = 0
        self.tweeters = []     
        self.hashtags = {}          
        self.keywords = {}      
        self.dict_words = {}    
