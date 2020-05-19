# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 11:24:22 2018

@author: omar adjali
"""
# -*- coding: utf-8 -*-
import tweepy
from tweepy import OAuthHandler
import sys,argparse,os
import sqlite3

import json
import wget
import configparser

import math
import time
import itertools
import random

# TODO Twitter API credentials
# see http://docs.tweepy.org/en/v3.5.0/auth_tutorial.html
consumer_key = "YourOwnComsumerToken"
consumer_secret = "YourOwnConsummerSecret"
access_key = "YourOwnAccessToken"
access_secret = "YourOwnAccessSecret"

def tweet_media_urls(tweet_status):
    media = tweet_status._json.get('extended_entities', {}).get('media', [])
    if (len(media) == 0):
       return []
    else:
        return [item['media_url'] for item in media]

def create_folder(output_folder):
    if not os.path.exists(output_folder):
       os.makedirs(output_folder)

def getTweetStatusData(status):

#==============================================================================
     tweetId =  int(status._json.get('id'))
     UserScreenName = status._json.get('user', {}).get('screen_name').strip().encode('ascii','ignore')
     UserId = int(status._json.get('user', {}).get('id' ))
     fullText = status._json.get('full_text').strip().encode('ascii','ignore')  #full_text
     created_at =  str(status._json.get('created_at'))
     media = status._json.get('entities', {}).get('media', [])
     mediaURL = ""
     if (len(media) > 0):
         mediaURL = media[0]['media_url']
 #        for media_url in [item['media_url'] for item in media]:
 #            # Only download if there is not a picture with the same name in the folder already
 #            media_url;
 #            #file_name = os.path.split(media_url)[1]
 #            #if not os.path.exists(os.path.join(output_folder, file_name)):
 #            #wget.download(media_url +":orig", out=output_folder+'/'+file_name)
     retweetCount =  int(status._json.get('retweet_count'))
     favoriteCount = int(status._json.get('favorite_count'))
     lang = status._json.get('lang')
#==============================================================================

#==============================================================================
     UserName = status._json.get('user', {}).get('name').strip().encode('ascii','ignore')
     UserLocation = status._json.get('user', {}).get('location').encode('ascii','ignore')
     UserURL = status._json.get('user', {}).get('url')
     UserDescr = status._json.get('user', {}).get('description').strip().encode('ascii','ignore')
     UserFollowers_count = int(status._json.get('user', {}).get('followers_count'))
     UserFriends_count = int(status._json.get('user', {}).get('friends_count'))
     UserListed_count = int(status._json.get('user', {}).get('listed_count'))
     UserFavourites_count = int(status._json.get('user', {}).get('favourites_count'))
     UserCreatedAt = status._json.get('user', {}).get('created_at')
     UserVerified = status._json.get('user', {}).get('verified')
     UserLang = status._json.get('user', {}).get('lang')
     UserProfileBackgroundImageUrl  = status._json.get('user', {}).get('profile_background_image_url')
     UserProfileImageUrl = status._json.get('user', {}).get('profile_image_url')
     UserProfileBannerUrl = status._json.get('user', {}).get('profile_banner_url')
#==============================================================================

     return tweetId, UserScreenName, UserId , fullText, created_at , mediaURL , retweetCount , favoriteCount ,lang,
     UserName, UserLocation, UserURL, UserDescr, UserFollowers_count , UserFriends_count , UserListed_count, UserFavourites_count, UserCreatedAt, UserVerified, UserLang, UserProfileBackgroundImageUrl ,
     UserProfileImageUrl , UserProfileBannerUrl

def getDataFromSeed(api,seedFile,queryType,db):
    f = open(seedFile , "r") # db file
    totalNbrQuery = 0
    totalNbrTweet = 0
    while 1:
          lines = f.readlines(100000)
          if not lines:
             break
          for line in lines:
              screenName = line.strip()
              queriesNbr , tweetNbr = getUserData(screenName, api,queryType, db)
              print("\n number of queries from " + screenName + " user Timeline = %d and tweets = %d \n"%(queriesNbr,tweetNbr) )
              totalNbrQuery += queriesNbr
              totalNbrTweet += tweetNbr
              print("\n number of Total queries =  %d and tweets = %d \n"%(totalNbrQuery,totalNbrTweet) )
              print(" \n User_TimeLine Limit--> " + str(getApiUserTimeLineLimit(api)) + "\n"  )
              print("search Limit--> " + str(getApiSearchLimit(api)) + "\n" )
    print("\n number of Total queries =  %d and tweets = %d \n"%(totalNbrQuery,totalNbrTweet) )

#==============================================================================

#==============================================================================
def getUserData(screen_name ,api, queryType, db):
    print("get user " + screen_name + " Data starting... \n")
    new_tweets = []
    nbrTweets = 0
    numberQuery = 0
    searchFile = open("searchQueries.Completed" , "a")
    #make initial request for most recent tweets (200 is the maximum allowed count)
    try:
        if queryType == 'e':# timeline entity collection
           status = api.user_timeline(screen_name = screen_name , count=200, tweet_mode='extended', include_rts=False, exclude_replies=False)
        else: # mentions collection
           status = api.search(q=screen_name ,count=200, tweet_mode='extended',include_rts=False, exclude_replies=False, lang='en')

        numberQuery +=1
        print("Query done! \n")
        # get the last 200 tweets
        for tweet_status in status:
            new_tweets.append(tweet_status)
            nbrTweets += 1
            #print tweets data
            acceptTweet = db.insertIntoTable(tweet_status,screen_name,queryType)
            if acceptTweet:
               nbrTweets += 1
    except Exception as e:
           print(e)
           print("exception of api query when screenName= %s ! \n"%screen_name)
           ftbr = open("toBeRemovedFromSeedFile.error" , "a")
           ftbr.write(screen_name + str(e) +  "\n")

    #While tweets remain, extract
    j = 0
    while len(new_tweets)  > 0:
             #update the id of the oldest tweet less one
             oldestId = new_tweets[-1].id - 1
             j += 1
             new_tweets = []
             try:

                 if (queryType == 'e'):
                    status = api.user_timeline(screen_name=screen_name, count=200, max_id=str(oldestId),tweet_mode='extended' ,include_rts=False, exclude_replies=False)
                 else:
                     status = api.search(q=screen_name , count=200 , max_id=str(oldestId), tweet_mode='extended',include_rts=False, exclude_replies=False, lang='en')

                 numberQuery +=1

                 for tweet_status in status:
                     new_tweets.append(tweet_status)
                     #print tweets data
                     acceptTweet = db.insertIntoTable(tweet_status,screen_name,queryType)
                     if acceptTweet:
                        nbrTweets += 1

                 if nbrTweets % 20 == 0:
                    db.connect.commit()

             except Exception as e:
                    print(e)
                    print("exception of api query when screenName= %s ! \n"%screen_name)
                    ftbr = open("toBeRemovedFromSeedFile.error" , "a")
                    ftbr.write(screen_name + str(e) +  "\n")
#             if j == 2:
#                break
    searchFile.write(screen_name +  "\n")
    db.connect.commit()
    print ("db committed !")
    return numberQuery, nbrTweets
#==============================================================================

#==============================================================================
def getTweets(api,seedFile, db,query):
    print("get_tweets starting...")
    if query == 'e':
       print('\n collect timeline entities...\n')
       getDataFromSeed(api,seedFile,query,db)
    elif query == 'm':
        print('\n collect mentions...\n')
        getDataFromSeed(api,seedFile,query,db)
    else:
        print('set query param from {e,m}')


def getApiSearchLimit(api):
    rls = api.rate_limit_status()
    limit = rls.get('resources',{}).get('search', {}).get('/search/tweets', {}).get('limit')
    remaining = rls.get('resources',{}).get('search', {}).get('/search/tweets', {}).get('limit')
    resetTime = rls.get('resources',{}).get('search', {}).get('/search/tweets', {}).get('reset')
    unixTime = resetTime
    resetTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(resetTime))
    timeToReset = unixTime - time.time()
    return limit, remaining, resetTime, timeToReset

def getApiUserTimeLineLimit(api):
    rls = api.rate_limit_status()

    limit = rls.get('resources',{}).get('statuses', {}).get('/statuses/user_timeline', {}).get('limit')
    remaining = rls.get('resources',{}).get('statuses', {}).get('/statuses/user_timeline', {}).get('limit')
    resetTime = rls.get('resources',{}).get('statuses', {}).get('/statuses/user_timeline', {}).get('reset')
    unixTime = resetTime
    resetTime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(resetTime))
    timeToReset = unixTime - time.time()
    return limit, remaining, resetTime, timeToReset

class Database:
    def __init__(self,filename):
        self.connect = sqlite3.connect(filename)
        self.c = self.connect.cursor()
    def getEntityName(self,entityId):
        query="select ID_ENTITE, VALEUR, wiki_title, type  from ENTITE WHERE ID_ENTITE= ?;"
        bind=(entityId,)
        self.c.execute(query,bind)
        row=self.c.fetchone()
        if row==None:
            sys.stderr.write("Warning: entity %s not found in database\n"%(entityId))
            return "NIL"
        else:
            return row

    def createTweetsTable(self):
        self.c.execute('''create table allTweets(
        tweetId integer PRIMARY KEY,
        userScreenName text,
        userId integer,
        tweetFullText text,
        createdAt text,
        mediaURL text,
        retweetCount integer,
        favoriteCount integer,
        lang text

           )''')

    def createTimelineTweetsTable(self):
        self.c.execute('''create table timeLineTweets(
        tweetId integer PRIMARY KEY,
        userScreenName text,
        userId integer,
        tweetFullText text,
        createdAt text,
        mediaURL text,
        retweetCount integer,
        favoriteCount integer,
        lang text

           )''')

    def createSearchTweetsTable(self):
        self.c.execute('''create table searchTweets(
        tweetId integer PRIMARY KEY,
        userScreenName text,
        querySearch text,
        userId integer,
        tweetFullText text,
        createdAt text,
        mediaURL text,
        retweetCount integer,
        favoriteCount integer,
        lang text

           )''')

        # listedCount: number of lists, this user is member of
    def createUsersTable(self):
        self.c.execute('''create table twitterUsers(
        userId integer PRIMARY KEY,
        userScreenName text,
        userName text,
        userLocation text,
        userUrl text,
        userDescription text,
        followersCount integer,
        friends_count integer,
        listedCount integer,
        favouritesCount integer,
        userCreatedAt text,
        verified text,
        lang text,
        profileBackgroundImageUrl text,
        profileImageUrl text,
        profileBannerUrl text
        )''')

    def insertIntoTable(self,status,querySearch_,queryType):
        #==============================================================================
        tweetId =  int(status._json.get('id'))
        userScreenName = status._json.get('user', {}).get('screen_name').strip().encode('ascii','ignore')
        userId = int(status._json.get('user', {}).get('id' ))
        tweetFullText = status._json.get('full_text').strip().encode('ascii','ignore')  #full_text
        createdAt =  str(status._json.get('created_at'))
        media = status._json.get('entities', {}).get('media', [])
        mediaURL = ""
        if (len(media) > 0):
            mediaURL = media[0]['media_url']
     #        for media_url in [item['media_url'] for item in media]:
     #            # Only download if there is not a picture with the same name in the folder already
     #            media_url;
     #            #file_name = os.path.split(media_url)[1]
     #            #if not os.path.exists(os.path.join(output_folder, file_name)):
     #            #wget.download(media_url +":orig", out=output_folder+'/'+file_name)
        retweetCount =  int(status._json.get('retweet_count'))
        favoriteCount = int(status._json.get('favorite_count'))
        lang = status._json.get('lang')
    #==============================================================================

    #==============================================================================
        userName = status._json.get('user', {}).get('name').strip().encode('ascii','ignore')
        userLocation = status._json.get('user', {}).get('location').encode('ascii','ignore')
        userUrl = status._json.get('user', {}).get('url')
        userDescription = status._json.get('user', {}).get('description').strip().encode('ascii','ignore')
        followersCount = int(status._json.get('user', {}).get('followers_count'))
        friends_count = int(status._json.get('user', {}).get('friends_count'))
        listedCount = int(status._json.get('user', {}).get('listed_count'))
        favouritesCount = int(status._json.get('user', {}).get('favourites_count'))
        userCreatedAt = status._json.get('user', {}).get('created_at')
        verified = status._json.get('user', {}).get('verified')
        userLang = status._json.get('user', {}).get('lang')
        profileBackgroundImageUrl  = status._json.get('user', {}).get('profile_background_image_url')
        profileImageUrl = status._json.get('user', {}).get('profile_image_url')
        profileBannerUrl = status._json.get('user', {}).get('profile_banner_url')
        querySearch = str(querySearch_.strip())
    #==============================================================================
        # add new user query
        twitterUsers_sql = "INSERT OR IGNORE INTO twitterUsers (userId,userScreenName,userName,userLocation,userUrl,userDescription,followersCount,friends_count,listedCount,favouritesCount ,userCreatedAt,verified,lang, profileBackgroundImageUrl, profileImageUrl, profileBannerUrl ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        # add new entity Tweets to TL query
        TimelineTweets_sql = "INSERT OR IGNORE INTO timeLineTweets (tweetId, userScreenName, userId, tweetFullText, createdAt, mediaURL, retweetCount, favoriteCount, lang) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        # add new entity/mention Tweets to Global table query
        allTweets_sql = "INSERT OR IGNORE INTO allTweets (tweetId, userScreenName, userId, tweetFullText, createdAt, mediaURL, retweetCount, favoriteCount, lang) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"
        # add new mention Tweets to mention query
        searchTweets_sql = "INSERT OR IGNORE INTO searchTweets (tweetId, userScreenName,querySearch, userId, tweetFullText, createdAt, mediaURL, retweetCount, favoriteCount, lang,querySearch) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,?,?)"

        # Filter tweets
        if isTweetValid(tweetFullText):
           if queryType == 'e':
              self.c.execute(TimelineTweets_sql, ( tweetId, userScreenName, userId, tweetFullText, createdAt, mediaURL, retweetCount, favoriteCount, lang ))
              self.c.execute(twitterUsers_sql, (userId,userScreenName,userName,userLocation,userUrl,userDescription,followersCount,friends_count,listedCount,favouritesCount ,userCreatedAt,verified,userLang, profileBackgroundImageUrl, profileImageUrl, profileBannerUrl))
           else:
               self.c.execute(searchTweets_sql, (tweetId, userScreenName,querySearch, userId, tweetFullText, createdAt, mediaURL, retweetCount, favoriteCount, lang,querySearch))
               self.c.execute(allTweets_sql, (tweetId, userScreenName, userId, tweetFullText, createdAt, mediaURL, retweetCount, favoriteCount, lang))
           return True
        else:
            return False

'''
Filter tweet from reTweet and @ enumerations
'''
def isTweetValid(text):
    textTweet = text.split(None)
          #print line
    if ("RT" in textTweet[0]):
       return False
    indeX = 0
    for i in range(len(textTweet)):
        if "@" not in textTweet[i] :
           indeX = i
           break

    remainingText = textTweet[indeX:]
    #Check in the remaining text, if it contains a mention @xxxxxx
    containsMention = False
    for rwds in remainingText:
        if "@" in rwds:
           containsMention = True
           break
    return containsMention


def main(argv):
    start_time = time.time()
    parser=argparse.ArgumentParser("Data Collection")
    parser.add_argument('-db_name',dest="db_name", type=str, help='DB name')
    parser.add_argument('-seed_file',dest="seed_file", type=str, help='seed file for search query')
    parser.add_argument("-query",dest="query",default='e' ,help="pass e for entities search / m for mentions search", type = str)

          # check args
    param=parser.parse_args()
    # check args
    param=parser.parse_args()
    db_name = param.db_name
    seed_file = param.seed_file
    query = param.query
    #authorize twitter, initialize tweepy
    if os.path.exists('./' + db_name) :
       db=Database(db_name)
       print('Database loaded !')
    else:
        db=Database(db_name)
        db.createSearchTweetsTable()
        db.createTweetsTable()
        db.createTimelineTweetsTable()
        db.createUsersTable()
        print('Database created !')

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    print ("authentification occured! \n"    )

    print("search Limit--> {}".format( getApiSearchLimit(api) ))
    print("User_TimeLine Limit--> {}".format(getApiUserTimeLineLimit(api)))

    # Main dat collection func
    getTweets(api, seed_file, db,query)

    print("\n data Collected")
    print("--- %s seconds ---" % (time.time() - start_time))

main(sys.argv[1:])




