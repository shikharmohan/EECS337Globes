class tweeter:
    def __init__(self):
        self.score = 1
        self.tweets = []
        self.userName = ''
        self.userId = 0

class tweet:
    def __init__(self):
        self.text = ''
        self.score = 1
        self.tweetId = 0

class relation:
    #relating tweeters to tweets
    def __init__(self):
        self.name = ''
        self.id = 0
        self.tweeters = []     
        self.tags = {}          
        self.tagwords = {}      
        self.words_dict = {}   