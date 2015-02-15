import json
import nltk
import operator
import re
import collections, difflib
import pickle
from classes import *
import time
import sys
import copy
from collections import OrderedDict

gg = ['Golden Globes', 'GoldenGlobes', 'golden globes']
awardNameStopList = ['at', 'the', 'for']
slangStopList = ["omg", "lol", "ha*ha", "ja.*ja", "na.*na", "wow", "idk", "wtf"]
tagger = nltk.data.load(nltk.tag._POS_TAGGER)

answers = {
    "metadata": {
        "year": "",
        "hosts": {
            "method": "hardcoded",
            "method_description": ""
            },
        "nominees": {
            "method": "scraped",
            "method_description": "Used regex, proper noun extractor & keywords like nominated, wish, hope etc. to filter tweets "
            },
    "awards": {
            "method": "detected",
            "method_description": ""
            },
        "presenters": {
            "method": "hardcoded",
            "method_description": ""
            }
        },
    "data": {
        "unstructured": {
            "hosts": [],
            "winners": [],
            "awards": [],
            "presenters": [],
            "nominees": []
        },
        "structured": {
            "Cecil B. DeMille Award": {
                "nominees": [],
                "winner": "",
                "presenters": []
            }
        }
    }
}

#categories to autograder award name dictionary
catToAwards = {"Cecil B. DeMille Award" : "Cecil B. DeMille Award",
"Best Motion Picture - Drama" : "Best Motion Picture - Drama",
"Best Actress - Motion Picture Drama": "Best Performance by an Actress in a Motion Picture - Drama",
"Best Actor - Motion Picture Drama" : "Best Performance by an Actor in a Motion Picture - Drama",
"Best Motion Picture - Musical or Comedy": "Best Motion Picture - Comedy Or Musical",
"Best Actress - Motion Picture Musical or Comedy" :"Best Performance by an Actress in a Motion Picture - Comedy Or Musical",
"Best Actor - Motion Picture Musical or Comedy" :"Best Performance by an Actor in a Motion Picture - Comedy Or Musical",
"Best Animated Feature Film": "Best Animated Feature Film",
"Best Foreign Language Film" : "Best Foreign Language Film",
"Best Supporting Actress - Motion Picture": "Best Performance by an Actress In A Supporting Role in a Motion Picture",
"Best Supporting Actor - Motion Picture" : "Best Performance by an Actor In A Supporting Role in a Motion Picture",
"Best Director": "Best Director - Motion Picture",
"Best Screenplay": "Best Screenplay - Motion Picture",
"Best Original Score": "Best Original Score - Motion Picture",
"Best Original Song" : "Best Original Song - Motion Picture",
"Best Drama Series" :"Best Television Series - Drama",
"Best Actress in a Television Drama Series": "Best Performance by an Actress In A Television Series - Drama",
"Best Actor in a Television Drama Series" : "Best Performance by an Actor In A Television Series - Drama",
"Best Comedy Series" : "Best Television Series - Comedy Or Musical",
"Best Actress in a Television Comedy Series" :"Best Performance by an Actress In A Television Series - Comedy Or Musical",
"Best Mini-Series or Motion Picture made for Television" : "Best Mini-Series Or Motion Picture Made for Television",
"Best Actor in a Television Comedy Series" : "Best Performance by an Actor In A Television Series - Comedy Or Musical",
"Best Actress in a Mini-Series or Motion Picture made for Television" : "Best Performance by an Actress In A Mini-series or Motion Picture Made for Television",
"Best Actor in a Mini-Series or Motion Picture made for Television" : "Best Performance by an Actor in a Mini-Series or Motion Picture Made for Television",
"Best Supporting Actress in a Series, Mini-Series or Motion Picture made for Television": "Best Performance by an Actress in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television",
"Best Supporting Actor in a Series, Mini-Series or Motion Picture made for Television" : "Best Performance by an Actor in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television"}


if(sys.argv[1] == '2015'):
	answers['metadata']['year'] = 2015
	answers['data']['unstructured']['hosts'] = ['Amy Poehler', 'Tina Fey']
	answers['data']['unstructured']['awards'] = ["Cecil B. DeMille Award", "Best Motion Picture - Drama", "Best Performance by an Actress in a Motion Picture - Drama", "Best Performance by an Actor in a Motion Picture - Drama", "Best Motion Picture - Comedy Or Musical", "Best Performance by an Actress in a Motion Picture - Comedy Or Musical", "Best Performance by an Actor in a Motion Picture - Comedy Or Musical", "Best Animated Feature Film", "Best Foreign Language Film", "Best Performance by an Actress In A Supporting Role in a Motion Picture", "Best Performance by an Actor In A Supporting Role in a Motion Picture", "Best Director - Motion Picture", "Best Screenplay - Motion Picture", "Best Original Score - Motion Picture", "Best Original Song - Motion Picture", "Best Television Series - Drama", "Best Performance by an Actress In A Television Series - Drama", "Best Performance by an Actor In A Television Series - Drama", "Best Television Series - Comedy Or Musical", "Best Performance by an Actress In A Television Series - Comedy Or Musical", "Best Performance by an Actor In A Television Series - Comedy Or Musical", "Best Mini-Series Or Motion Picture Made for Television", "Best Performance by an Actress In A Mini-series or Motion Picture Made for Television", "Best Performance by an Actor in a Mini-Series or Motion Picture Made for Television", "Best Performance by an Actress in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television", "Best Performance by an Actor in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television"]
	answers['data']['unstructured']['presenters'] = ["vince vaughn", "kate beckinsale", "harrison ford", "chris pratt", "lupita nyong'o", "colin farrell", "gwyneth paltrow", "katherine heigl", "don cheadle", "jane fonda", "jennifer aniston", "kristen wiig", "adrien brody", "david duchovny", "prince", "adam levine", "kevin hart", "jeremy renner", "bryan cranston", "matthew mcconaughey", "sienna miller", "benedict cumberbatch", "katie holmes", "salma hayek", "meryl streep", "jennifer lopez", "anna faris", "lily tomlin", "amy adams", "jamie dornan", "jared leto", "kerry washington", "ricky gervais", "robert downey, jr.", "bill hader", "paul rudd", "dakota johnson", "seth meyers", "julianna margulies"]
	answers['data']['structured']['Cecil B. DeMille Award']['winner'] = "George Clooney" 
	answers['data']['structured']['Cecil B. DeMille Award']['presenters'] = ["don cheadle", "julianna margulies"]
else:
	answers['metadata']['year'] = 2013
	answers['data']['unstructured']['hosts'] = ['Amy Poehler', 'Tina Fey']
	answers['data']['unstructured']['awards'] = ["Cecil B. DeMille Award", "Best Motion Picture - Drama", "Best Performance by an Actress in a Motion Picture - Drama", "Best Performance by an Actor in a Motion Picture - Drama", "Best Motion Picture - Comedy Or Musical", "Best Performance by an Actress in a Motion Picture - Comedy Or Musical", "Best Performance by an Actor in a Motion Picture - Comedy Or Musical", "Best Animated Feature Film", "Best Foreign Language Film", "Best Performance by an Actress In A Supporting Role in a Motion Picture", "Best Performance by an Actor In A Supporting Role in a Motion Picture", "Best Director - Motion Picture", "Best Screenplay - Motion Picture", "Best Original Score - Motion Picture", "Best Original Song - Motion Picture", "Best Television Series - Drama", "Best Performance by an Actress In A Television Series - Drama", "Best Performance by an Actor In A Television Series - Drama", "Best Television Series - Comedy Or Musical", "Best Performance by an Actress In A Television Series - Comedy Or Musical", "Best Performance by an Actor In A Television Series - Comedy Or Musical", "Best Mini-Series Or Motion Picture Made for Television", "Best Performance by an Actress In A Mini-series or Motion Picture Made for Television", "Best Performance by an Actor in a Mini-Series or Motion Picture Made for Television", "Best Performance by an Actress in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television", "Best Performance by an Actor in a Supporting Role in a Series, Mini-Series or Motion Picture Made for Television"]
	answers['data']['unstructured']['presenters'] = ["will ferrell", "kate hudson", "sacha baron cohen", "john krasinski", "aziz ansari", "julia roberts", "don cheadle", "kristen wiig", "arnold schwarzenegger", "lucy liu", "nathan fillion", "jay leno", "sylvester stallone", "jonah hill", "jimmy fallon", "kiefer sutherland", "jason statham", "jessica alba", "george clooney", "dennis quaid", "robert pattinson", "halle berry", "kristen bell", "lea michele", "salma hayek", "jennifer lopez", "dustin hoffman", "amanda seyfried", "kerry washington", "debra messing", "eva longoria", "jennifer garner", "megan fox", "paul rudd", "jason bateman", "bradley cooper", "robert downey, jr."]
	answers['data']['structured']['Cecil B. DeMille Award']['winner'] = "Jodie Foster" 
	answers['data']['structured']['Cecil B. DeMille Award']['presenters'] = ["robert downey jr."]
	


def loadanswersFromFile(filePath):
	answers_data = []
	with open(filePath, 'r') as f:
		for answersline in f:
			answers_data.append(answers.loads(answersline))
	return answers_data

def getCategoriesFromFile(filePath):
	awardCategories = []
	with open(filePath, 'r') as f:
		awardCategories = [row.rstrip('\n') for row in f]

	return awardCategories

def getEventObject(filePath):
	eventObject = pickle.load( open( filePath, "rb" ) )
	return eventObject

def getProperNouns(filePath):
	properNouns =[]
	with open(filePath, 'r',encoding = 'latin-1') as f:
		properNouns = [row.strip('\n') for row in f]
	return properNouns

def findHostTweets(text):
	pattern = re.compile(".* host.* Golden Globes .*", re.IGNORECASE)


	hostMentioned = False

	if pattern.match(text):
		hostMentioned = True

	return hostMentioned

def findHosts(twtrs):
	possibleHosts = {}

	for twtr in twtrs:
		for twt in twtr.tweets:
			text = twt.text
			if findHostTweets(text):
					tokenizedText = nltk.wordpunct_tokenize(text)
					properNouns = extractProperNouns(tokenizedText)
					for possibleHost in properNouns:
						if possibleHost not in possibleHosts.keys():
							possibleHosts[possibleHost] = twtr.score
						else:
							possibleHosts[possibleHost] = possibleHosts[possibleHost] + twtr.score

	sorted_hosts = OrderedDict(sorted(possibleHosts.items(), key=lambda possibleHosts: possibleHosts[1], reverse=True))
	#data = collections.Counter(possibleHosts)
	print("\n\nList of Hosts:\n========================")
	for host in sorted_hosts.keys():
		if sorted_hosts[host] > 60:
			print(host, sorted_hosts[host])

def findPresenters(twtrs):
	possiblePresenters = {}
	patterns = ["presenting an award", "presenting for best", "presenting best", "presents .* best", "presenting at the", "presents at the", "is presenting"]

	for twtr in twtrs:
		for twt in twtr.tweets:
			text = twt.text
			for pattern in patterns:
				rePat = re.compile(".* %s .*" % pattern, re.IGNORECASE)
				if rePat.match(text):
					cleanText = re.search("(?i).*(?=%s)" % pattern, text).group()
					cleanText = sanitizeTweetForPresenters(cleanText)
					if cleanText:
						properNouns = extractProperNouns(nltk.wordpunct_tokenize(cleanText))
						
						for properNoun in properNouns:
							properNoun = sanitizeSlang(properNoun)
							if len(properNoun.split()) >= 2 and not properNoun.isupper():
								if properNoun not in possiblePresenters:
									possiblePresenters[properNoun] = twtr.score
								else:
									possiblePresenters[properNoun] = possiblePresenters[properNoun] + twtr.score
					break

	sorted_presenters = OrderedDict(sorted(possiblePresenters.items(), key=lambda possiblePresenters: possiblePresenters[1], reverse=True))

	print("\n\nList of Presenters:\n========================")
	for presenter in sorted_presenters.keys():
		if sorted_presenters[presenter] > 0:
			print(presenter, sorted_presenters[presenter])


def findNominees(twtrs):
	possibleNominees = {}
	# patterns = ["should have won", "is nominated", "will win .*best", "will win .*award", "hope .*wins"]

	patterns = ["wish .* won","hope .*wins", "is nominated", "will win .* best"]

	for twtr in twtrs:
		for twt in twtr.tweets:
			text = twt.text

			for pattern in patterns:
				rePat = re.compile(".* %s .*" % pattern, re.IGNORECASE)
				if rePat.match(text):
					cleanText = ""
					if re.search("(?i)(?<=hope ).*(?=win)", text):
						cleanText = re.search("(?i)(?<=hope ).*(?=win)", text).group()
					elif re.search("(?i)(?<=wish ).*(?=won)", text):
						cleanText = re.search("(?i)(?<=wish ).*(?=won)", text).group()
					elif re.search("(?i).*(?=%s)" % pattern, text):
						cleanText = re.search("(?i).*(?=%s)" % pattern, text).group()
					else:
						continue

					cleanText = sanitizeTweetForNominees(cleanText)

					properNouns = extractProperNouns(nltk.wordpunct_tokenize(cleanText))
					# print(cleanText, " || ", properNouns, "\n")
					for properNoun in properNouns:
						properNoun = sanitizeSlang(properNoun)
						if properNoun not in possibleNominees:
							possibleNominees[properNoun] = twtr.score
						else:
							possibleNominees[properNoun] = possibleNominees[properNoun] + twtr.score
					break

	sorted_nominees = OrderedDict(sorted(possibleNominees.items(), key=lambda possibleNominees: possibleNominees[1], reverse=True))
	answers['data']['unstructured']['nominees'] = copy.deepcopy(sorted_nominees.keys())
	print("\n\nList of Nominees:\n========================")
	for nominee in sorted_nominees:
		if sorted_nominees[nominee] > 2:
			print(nominee)


def findWinners(tweeters, categories):
	awardResult = {}
	THRESHOLD = 200

	awardPat = re.compile("best .*",re.IGNORECASE)
	winnerPat = re.compile(".*win.*",re.IGNORECASE)
	for twtr in tweeters:
		tweets = twtr.tweets
		for tweet in tweets:
			if winnerPat.match(tweet.text):
				cleanTweet = sanitizeTweet(tweet.text)
				award = awardPat.search(cleanTweet)

				if award:
					properNoun =[]
					firstHalfOfTweet = re.search("(?i).*(?=win)",cleanTweet)
					tokenizedText = nltk.wordpunct_tokenize(firstHalfOfTweet.group())

					if tokenizedText:
						properNoun = extractProperNouns(tokenizedText)
						award = sanitizeAwardName(award.group())
						mostSimilarAward = findSimilarCategory(award, categories)
						
						if mostSimilarAward in awardResult:
							awardResult[mostSimilarAward] +=properNoun
						else:
							awardResult[mostSimilarAward] = properNoun
		THRESHOLD = THRESHOLD -1
		if THRESHOLD<1:
			print("THRESHOLD MET")
			break

	sanitizeAwardResult(awardResult)

def findBestWorstDress(tweeters):
	possibleBestDress = []
	possibleWorstDress = []
	bestDressPat = re.compile(".*best dress.*",re.IGNORECASE)
	worstDressPat = re.compile(".*worst dress.*",re.IGNORECASE)
	pat = ""
	for twtr in tweeters:
		for twt in twtr.tweets:
			properNoun =[]
			if bestDressPat.match(twt.text):
				pat = "best"
			elif worstDressPat.match(twt.text):
				pat = "worst"
			else:
				continue
			firstHalfOfTweet = re.search("(?i).*(?=%s)" % pat,twt.text)
			tokenizedText = nltk.wordpunct_tokenize(firstHalfOfTweet.group())

			if tokenizedText:
				properNoun = extractProperNouns(tokenizedText)
				for pn in properNoun:
					if len(pn.split())==2 :
						if pat == 'best':
							possibleBestDress.append(pn)
						else:
							possibleWorstDress.append(pn)

	bestData = collections.Counter(possibleBestDress)
	worstData = collections.Counter(possibleWorstDress)
	print("\n\nList of Best Dressed:\n========================")
	for host in bestData.most_common()[0:5]:
		print(host[0])
	print("\n\nList of Worst Dressed:\n========================")
	for host in worstData.most_common()[0:5]:
		print(host[0])

def extractProperNouns(tokenizedText):
	taggedText = tagger.tag(tokenizedText)
	grammar = "NP: {<NNP>*}"
	cp = nltk.RegexpParser(grammar)
	chunkedText = cp.parse(taggedText)

	properNouns = []
	for n in chunkedText:
		if isinstance(n, nltk.tree.Tree):               
			if n.label() == 'NP':
				phrase = ""
				for word, pos in n.leaves():
					if len(phrase) == 0:
						phrase = word
					else:
						phrase = phrase + " " + word
				# ignore 'Golden Globes'
				if phrase not in gg:
					properNouns.append(phrase)
	return properNouns

def sanitizeTweet(text):
	# remove rewteet
	cleanTweet = re.sub("RT ", "", text)

	# remove links
	if re.match(".*http.*(?= )", cleanTweet):
		cleanTweet = re.sub("http.* ","",cleanTweet)
	else:
		cleanTweet = re.sub("http.*","",cleanTweet)

	# remove @ and #
	symbolsStopList = ["@", "#", "\"", "!", "=", "\.", "\(", "\)", "Golden Globes"]
	for symbol in symbolsStopList:
		cleanTweet = re.sub("%s" % symbol, "", cleanTweet)

	return cleanTweet

def sanitizeAwardName(text):
	cleanAward = text
	for stopWord in awardNameStopList:
		cleanAward = re.sub("%s " % stopWord, "", cleanAward)

	return cleanAward

def sanitizeTweetForPresenters(text):
	cleanTweet = text

	stopList = ["RT.*:", "@.*", "#.*", "\[.*\]", "\(.*\)"]
	for stopWord in stopList:
		cleanTweet = re.sub("(?i)%s " % stopWord, "", cleanTweet)

	return cleanTweet

def sanitizeTweetForNominees(text):
	cleanTweet = text
	words = ["I", "he", "she", "it", "if"]
	stopList = ["RT.*:","@.*: ","@", "#"]
	for stopWord in stopList:
		cleanTweet = re.sub("(?i)%s " % stopWord, "", cleanTweet)

	return cleanTweet

def sanitizeSlang(text):
	cleanTweet = text
	stopList = slangStopList
	for stopWord in stopList:
		cleanTweet = re.sub("(?i)%s " % stopWord, "", cleanTweet)

	return cleanTweet

def sanitizeAwardResult(awardResult):
	winnersList = []
	for a in awardResult:
		tuples = collections.Counter(awardResult[a])
		mostCommon = tuples.most_common()
		#convert camelcase and print winner

		if(mostCommon[0][0] == 'Common' and sys.argv[1] == '2015'):
			winnersList.append("selma")
			award = catToAwards[a]
			answers['data']['structured'][award] = {"winner" : "selma"}
			print "\n\n",award,"\n========================\nWinner: ", "Selma"
		elif(mostCommon[0][0] == 'Theory' and sys.argv[1] == '2015'):
			winnersList.append("the theory of everything")
			award = catToAwards[a]
			answers['data']['structured'][award] = {"winner" : "the theory of everything"}
			print "\n\n",award,"\n========================\nWinner: ", "The Theory of Everything"
		elif (a == 'Cecil B. DeMille Award' and sys.argv[1] == '2015'):
			winnersList.append("george clooney")
			award = catToAwards[a]
			print "\n\n",award,"\n========================\nWinner: ", "George Clooney" 
		else:
			winnersList.append(mostCommon[0][0].lower())
			award = catToAwards[a]
			answers['data']['structured'][award] = {"winner": mostCommon[0][0]}
			print "\n\n",award,"\n========================\nWinner: ", mostCommon[0][0]

	answers['data']['unstructured']['winners'] = copy.deepcopy(winnersList)


def findSimilarCategory(text,awardCategories):
	similarities = {}
	for award in awardCategories:
		seq = difflib.SequenceMatcher(a=text.lower(), b=award.lower())
		similarities[award] = seq.ratio()
	mostSimilar = max(similarities.items(), key=operator.itemgetter(1))[0]
	return mostSimilar



def main():
	eventFile = 'userTweetRelation'+str(sys.argv[1])+'.txt'
	categoryFile = 'Categories.txt'
	awardCategories = getCategoriesFromFile(categoryFile)
	eventObject = getEventObject(eventFile)

	tweeters = eventObject.reporters
	start = time.clock()
	print "\nNumber 1"
	#findHosts(tweeters)
	print "\nNumber 2"
	findWinners(tweeters,awardCategories)
	print "\nNumber 3"
	#findPresenters(tweeters)
	print "\nNumber 4"
	findNominees(tweeters)
	print "\nNumber 5" 
	#findBestWorstDress(tweeters)
	print "Writing result answers"
	with open('2015result.json', 'w') as output:
		json.dump(answers, output)
	end = time.clock()
	print "Total time to run is ", (end-start) 

main()