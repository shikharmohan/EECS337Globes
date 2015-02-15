print('Loading python libraries')
import json
import pickle
import nltk
import operator
import itertools
import re
import pdb
import sys
from classes import *
from collections import OrderedDict

if(sys.argv[1] =='gg15mini'):
    year = 2015
else:
    year = 2013

def keywordCheck(string):
    """Check to see if the word is not a symbol or short word"""
    if ((string != 'RT') 
    and (string != '#') 
    and (string != '@') 
    and (string != 'the') 
    and (string != 'is') 
    and (string != 'I') 
    and (string != 't')
    and (string != '"')
    and (string != 's')
    and (string != 'and')
    and (string != 'in')
    and (string != 'at')
    and (string != 'http')
    and (string != 'it')
    and (string != 'me')
    and (string != 'this')
    and (string != 'my')
    and (string != 'The')
    and (string != 'for')
    and (string != 'like')
    and (string != 'not')
    and (string != 'she')
    and (string != 'an')
    and (string != 'he')):
        return True
    else:
        return False

def createRelation(name, top_tweeter_list, word_list, keyword_list, hashtag_list):
    """Creates a relation between tweets, keywords, relations"""

    Relation = relation()
    Relation.name = name
    Relation.reporters = top_tweeter_list
    Relation.words_dict = word_list
    Relation.tags = hashtag_list
    Relation.tagwords = keyword_list

    return Relation

def processTweets(json_object, keyword_list, tweeter_list, word_list, user_list, mentionedUser_list):
    """Parses the tweet from the json_object and updates categories"""

    #Create the tweet object
    twt = tweet()
    twt.text = json_object['text']
    twt.tweetId = json_object['id']

    #Create the tweeter object
    twter = tweeter()
    twter.tweets.append(twt)
    twter.userName = json_object['user']['screen_name']
    twter.userId = json_object['user']['id']

    #Create tokens from text
    text = nltk.wordpunct_tokenize(twt.text)
    
    #Bools
    hashtag = False
    mention = False
    retweet = False
    properNoun = False
    recent = False

    #Look through each word to categorize it
    for word in text:
       
        if hashtag and (word not in keyword_list):
            keyword_list[word] = 1
            hashtag = False
        if hashtag and (word in keyword_list):
            votes = keyword_list[word]
            keyword_list[word] = votes + 1
            hashtag = False
            
            

        #Find the original tweet and increase its score. Also find the user and increase his score.
        if retweet and mention:

                mention = False
                retweet = False

        #If the user mentioned is not in the user list, create a mentionedUser of the user
                if (word not in user_list) and (word not in mentionedUser_list):

                    mentionUser_twter = tweeter()
                    mentionUser_twter.userName = word
                    mentionUser_twter.score = 1
                    mentionUser_twter.userId = -1

                    mentionUser_twt = tweet()
                    mentionUser_twt.text = twt.text
                    mentionUser_twt.score = 1
                    mentionUser_twt.tweetId = -1

                    mentionUser_twter.tweets.append(mentionUser_twt)

                    mentionedUser_list[word] = mentionUser_twter
                    
                    recent = True

                #Check to see if the retweet belongs to a mentionedUser
                if (word in mentionedUser_list) and not recent:
                    exists = False

                    mentionedUser = mentionedUser_list[word]

                    mentionUser_twt = tweet()
                    mentionUser_twt.text = twt.text

                    for mt in mentionedUser.tweets:
                        if mentionUser_twt.text == mt.text:
                            exists = True
                            mt.score = mt.score + 1
                            
                    if exists != True:
                        mentionedUser.tweets.append(mentionUser_twt)

                    mentionedUser.score = mentionedUser.score + 1

        #         #Otherwise, increase the original tweeter's and tweet's score
                if (not recent) and (word in user_list):
                    id = user_list[word]
                    mentioned = tweeter_list[id]
                    found = False

                    for t in mentioned.tweets:
                        if t.text in twt.text:
                            found = True
                            t.score = t.score + 1

                    if not found:
                        newTweet = tweet()
                        newTweet.text = twt.text
                        mentioned.tweets.append(newTweet)

                    mentioned.score = mentioned.score + 1

        #Interpret the twitter commands and adjust the bools
        if '#' in word:
            hashtag = True
        if '@' in word:
            mention = True
        if 'RT' in word:
            retweet = True

        #Add word to the master word list, or increase its score.
        if word not in word_list:
            word_list[word] = 1
        else:
            freq = word_list[word]
            word_list[word] = freq + 1

    #Add tweeter to the master tweeter list
    if twter.userId not in tweeter_list:
        tweeter_list[twter.userId] = twter
        user_list[twter.userName] = twter.userId
    else:
        tweeter_list[twter.userId].tweets.append(twt)
            
def main():
    #File data variables
    file_data = []
    json_data = []
    
    #Dictionaries
    hashtags = {}
    keywords = {}
    words = {} 
    tweeters = {}
    mentionUser_tweeters = {}
    userIdTable = {}

    #Lists
    properNouns = []
    properPhrases = []
    top_tweeters = []

    #JSON file location
    json_file = sys.argv[1]

    #Open the JSON File and load contents into a list
    with open(json_file, 'r') as f:   
        text = f.readline()
        json_data = json.loads(text)

    print('Loading libraries COMPLETED.  Pre-processing tweets...')



    #Parse the text from the tweets
    progress = 0
    for item in json_data:
        progress = progress + 1
        if progress % 10000 == 0:
            print str(progress) + ' tweets processed'
        try:
            processTweets(item, hashtags, tweeters, words, userIdTable, mentionUser_tweeters)
        except:
            print(item['id'])
            print('An error occurred parsing this line')
            print(item['created_at'])

    #Start Program
    print('Loading ', json_file, '...')

    

    #Pick out keywords from the word list using the hashtags
    print('Finding keywords')
    for word in words:
        if word in hashtags:
            if word not in keywords:
                keywords[word] = words[word]

    #Remove common twitter commands from keyword list
    print('Filtering Keywords')
    filtered_keywords = {}
    for keyword in keywords:
        if keywordCheck(keyword):
            filtered_keywords[keyword] = keywords[keyword]
    
    #Sort the dictionaries to display the most popular items
    print('Sorting hashtags')
    sorted_hashtags = OrderedDict(sorted(hashtags.items(), key=lambda hashtags: hashtags[1], reverse=True))
    print('Sorting users')
    sorted_users = OrderedDict(sorted(tweeters.items(), key=lambda tweeters: tweeters[1].score, reverse=True))
    print('Sorting mentionedUsers')
    sorted_mentionedUsers = OrderedDict(sorted(mentionUser_tweeters.items(), key=lambda mentionUser_tweeters: mentionUser_tweeters[1].score, reverse=True))
    print('Sorting keywords')
    sorted_keywords = OrderedDict(sorted(filtered_keywords.items(), key=lambda filtered_keywords: filtered_keywords[1], reverse=True))

    #Write the most popular hashtags to file
    print('Writing popular hashtags to hashtags.txt')

    with open('popular_hashtags'+str(year)+'.txt', 'w') as output:
        for word in sorted_hashtags:
            try:
                output.write(word)
                output.write('\r')
            except:
                output.write('Error writing hashtag to file \r')

    #Print the most popular users
    print('Writing users to users.txt')

    with open('popular_users'+str(year)+'.txt', 'w') as output:
        for user in sorted_users:
            try:
                output.write(sorted_users[user].userName)
                output.write(' ')
                output.write(str(sorted_users[user].score))
                output.write('\r')
            except:
                output.write('Error writing user to file\r')

    #Print the most popular tweets
    print('Writing popular tweets (retweets) to popular_tweets.txt')
    with open('popular_tweets'+str(year)+'.txt', 'w') as output:
        for twter in sorted_users.values():
            i = 0
            #Find golden globes 
            if twter.userName == 'goldenglobes':
                pass

            i = i + 1
            if i<2500:
                try:
                    if i<20:
                        output.write(twter.userName)
                        output.write('\r')
                except:
                    print('Username is unreadable')
                for twt in twter.tweets:
                    try:
                        if i<20:
                            output.write('   ')
                            output.write(twt.text)
                            output.write('\r')
                    except:
                        output.write('Error writing tweet to file\r')

    userTweetRelation = createRelation('Golden Globes', sorted_users.values(), words, keywords, hashtags)

    print('Writing userTweetRelation to userTweetRelationYEAR.txt')
    with open('userTweetRelation'+str(year)+'.txt', 'wb') as output:
        pickle.dump(userTweetRelation, output)

    #Program is complete
    print('Processing Complete')

    return


main()