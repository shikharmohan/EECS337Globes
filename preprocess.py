print('Loading application dependencies')
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


def keywordCheck(string):
    """Check to see if the word is not a symbol or short word"""
    if ((string != 'RT') 
    and (string != '#') 
    and (string != 'at') 
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

#Creates an relation between tweeter and tweets/hashtags/keywords
def createRelation(name, top_tweeter_list, word_list, keyword_list, hashtag_list):

    Relation = relation()
    Relation.name = name
    Relation.tweeters = top_tweeter_list
    Relation.words_dict = word_list
    Relation.tags = hashtag_list
    Relation.tagwords = keyword_list

    return Relation

#Parses the tweet from the corpus and updates various lists
def tweetProcess(json_object, keyword_list, tweeter_list, word_list, user_list, atuser_list):

    #Create the tweet object
    twt = tweet()
    twt.text = json_object['text']
    twt.tweetId = json_object['id']

    #Create the tweeter object
    twter = tweeter()
    twter.tweets.append(twt)
    twter.userName = json_object['user']['screen_name']
    twter.userId = json_object['user']['id']


    text = nltk.wordpunct_tokenize(twt.text)
    
    #Bools
    mention = False
    retweet = False
    recent = False
    hashtag = False

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

        #If the user mentioned is not in the user list, create a reference to the atuser 
                if (word not in user_list) and (word not in atuser_list):

                    atuser_twter = tweeter()
                    atuser_twter.userName = word
                    atuser_twter.score = 1
                    atuser_twter.userId = -1

                    atuser_twt = tweet()
                    atuser_twt.text = twt.text
                    atuser_twt.score = 1
                    atuser_twt.tweetId = -1

                    atuser_twter.tweets.append(atuser_twt)

                    atuser_list[word] = atuser_twter
                    
                    recent = True

                #Check to see if the retweet belongs to a atuser
                if (word in atuser_list) and (not recent):
                    exists = False

                    atuser = atuser_list[word]

                    atuser_twt = tweet()
                    atuser_twt.text = twt.text

                    for gt in atuser.tweets:
                        if atuser_twt.text == gt.text:
                            exists = True
                            gt.score = gt.score + 1
                            
                    if exists != True:
                        atuser.tweets.append(atuser_twt)

                    atuser.score = atuser.score + 1

            #Otherwise, increase the original tweeter's and tweet's score
                if (word in user_list) and (not recent):
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
        if 'at' in word:
            mention = True
        if 'RT' in word:
            retweet = True

        #Add word to the master word list, or increase its score.
        if word not in word_list:
            word_list[word] = 1
        else:
            freq = word_list[word]
            word_list[word] = freq + 1

    #Check to see if tweeter has a atuser
    if twter.userName in atuser_list.keys() and not recent:
        

        #Copy the information from the atuser to the tweeter
        atuser = atuser_list[twter.userName]

        for t in atuser.tweets:
            twter.tweets.append(t)

        twter.score = twter.score + atuser.score
        try:
            del atuser_list[twter.userName]
        except KeyError:
            pass

    #Add tweeter to the master tweeter list
    if twter.userId not in tweeter_list:
        tweeter_list[twter.userId] = twter
        user_list[twter.userName] = twter.userId
    else:
        tweeter_list[twter.userId].tweets.append(twt)
            
def main():
    file_data = []
    json_data = []
    
    #Lists
    hashtags = {}
    keywords = {}
    words = {} 
    tweeters = {}
    atuser_tweeters = {}
    userTable = {}

    json_file = sys.argv[1]
    if(json_file == 'gg15mini.json'):
        year = 2015
    else:
        year = 2013

        #open corpus
    with open(json_file, 'r') as f:
        text = f.readline()
        json_data = json.loads(text)

    print('Loading completed.  Processing tweets...')

    #Parse the text from the tweets
    progress = 0
    for item in json_data:
        progress += 1
        if progress % 10000 == 0:
            print str(progress) + ' tweets processed'
        try:
            tweetProcess(item, hashtags, tweeters, words, userTable, atuser_tweeters)
        except:
            print(item['id'])
            print('An error occurred parsing this line')
            print(item['created_at'])
    

    #Start Processing
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
    print('Sorting atusers')
    sorted_atusers = OrderedDict(sorted(atuser_tweeters.items(), key=lambda atuser_tweeters: atuser_tweeters[1].score, reverse=True))
    print('Sorting keywords')
    sorted_keywords = OrderedDict(sorted(filtered_keywords.items(), key=lambda filtered_keywords: filtered_keywords[1], reverse=True))

    #Write the most popular hashtags to file
    print('Writing popular hashtags to hashtags.txt')

    with open('hashtags.txt', 'w') as output:
        for word in sorted_hashtags:
            try:
                output.write(word)
                output.write('\r')
            except:
                output.write('Error writing hashtag to file \r')

    #Print the most popular users
    print('Writing users to tweeters.txt')

    with open('tweeters.txt', 'w') as output:
        for user in sorted_users:
            try:
                output.write(sorted_users[user].userName)
                output.write(' ')
                output.write(str(sorted_users[user].score))
                output.write('\r')
            except:
                output.write('Error writing user to file\r')

    #Print the most popular users
    print('Writing keywords to popular_keywords.txt')

    with open('popular_keywords.txt', 'w') as output:
        for word in sorted_keywords.keys():
            try:
                output.write(word)
                output.write(' ')
                output.write(str(keywords[word]))
                output.write('\r')
            except:
                output.write('Error writing keyword to file\r')

    #Print the most popular tweets
    print('Writing retweets to retweets.txt')
    i = 0

    with open('retweets.txt', 'w') as output:
        for twter in sorted_users.values():

            # if twter.userName == 'goldenglobes':
            #     pass

            i = i + 1
            if i<3000:
                try:
                    if i<10:
                        output.write(twter.userName)
                        output.write('\r')
                except:
                    print('Username is unreadable')
                for twt in twter.tweets:
                    try:
                        #Only write the top tweets
                        if i<20:
                            output.write('   ')
                            output.write(twt.text)
                            output.write('\r')
                    except:
                        output.write('Error writing tweet to file\r')

    print('Writing Relation to userTweetRelation.txt')

    with open('userTweetRelation.txt', 'wb') as output:
        pickle.dump(createRelation('Golden Globes', sorted_users.values(), words, sorted_keywords.values(), hashtags), output)

    print('Writing atuser tweets to atusers.txt')

    with open('atusers'+year+'.txt', 'w') as output:
        for atUser in sorted_atusers.values():
            try:
                output.write(atUser.userName)
                output.write('\r')
            except:
                output.write('Error writing username to file\r')
            for t in atUser.tweets:
                try:
                    output.write('    ')
                    output.write(t.text)
                    output.write('\r')
                except:
                    output.write('Error writing tweet to file\r')

    #Program is complete
    print('Tweet processing complete')

main()
