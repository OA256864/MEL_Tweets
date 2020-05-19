# -*- coding: utf-8 -*-
"""
Created on Tue Nov 20 11:24:22 2018

@author: omar
"""
# -*- coding: utf-8 -*-
import tweepy
from tweepy import OAuthHandler
import sys,argparse,os
import sqlite3
import time


# TODO Twitter API credentials
# see http://docs.tweepy.org/en/v3.5.0/auth_tutorial.html
consumer_key = "YourOwnComsumerToken"
consumer_secret = "YourOwnConsummerSecret"
access_key = "YourOwnAccessToken"
access_secret = "YourOwnAccessSecret"

def getLastNamesFromList(fileName):
    fnf = open(fileName,"r")
    Names = set()
    while 1:
          lines = fnf.readlines(100000)
          if not lines:
             break
          for line in lines:
              fn = str(line.strip().lower())
              if fn not in Names:
                 Names.add(fn)
    return Names

def extract_lastname_from_userName(user_name, LastNames_set):
#    print query
    elemts = user_name.split(' ')
    for el in elemts:
        if el.lower() in LastNames_set:
           return el.lower()
    return None

##==============================================================================
#==============================================================================
def getAmbiguousUsers(api, db,lastName_seed,screenName_seed, seed_type):
    fwerr = open('usersException.txt' , "a") # users with whom APi genrates Exceptions
    processedLastNames = {} # Already processed Last Names

    # get already added users
    if os.path.exists('./' + 'usersAlreadyDone.txt') :
       fr = open('usersAlreadyDone.txt' , "r") # used to check already collected users
       while 1:
             lines = fr.readlines(100000)
             if not lines:
                break
             for line in lines:
                 processedLastNames[str(line.strip())] = True
       fr.close()
    # search ambiguous users from lastname seed list
    if seed_type == "ln":
        fnf = open(lastName_seed,"r")
        fw = open('usersAlreadyDone.txt' , "a")
        ap = 0 # number of already collected users
        while 1:
              lines = fnf.readlines(100000)
              if not lines:
                 break
              for line in lines:
                  query = str(line.strip().lower())
                  if query in processedLastNames:
                     print('already processed --> ' + query + ' ' + str(ap))
                     ap+=1
                     continue
                  # query with last name
                  Nbr_pages = 30   # Nbr of Twitter pages to search in
                  Nbr_users = 20   # Nbr of users per page
                  for i in range(Nbr_pages):
                      try:
                         statuss = api.search_users(q=query, page = i, count = Nbr_users)
                         for status in statuss:
                             db.insertIntoTable(status,query, lastNa =query,  userType= 'person' )
                      except Exception as e:
                             print(e)
                             fwerr.write(query + '\n')
                             print("exception of api query when screenName= %s ! \n"%query)
                  db.connect.commit()
                  fw.write(query + '\n')
                  print('lastName: {} processed'.format(query))
    # search ambiguous users from screename seed list
    elif seed_type == "sn":
         LastNames_set =  getLastNamesFromList(lastName_seed)
         fnf = open(screenName_seed,"r")
         fw = open('usersAlreadyDone.txt' , "a")
         ap = 0 # number of already collected users
         while 1:
               lines = fnf.readlines(100000)
               if not lines:
                  break
               for line in lines:
                   query = str(line.strip().lower())
                   if query in processedLastNames:
                      print('already processed --> ' + query + ' ' + str(ap))
                      ap+=1
                      continue
                   try:
                       user_info = api.get_user(screen_name = query) # Dictionary with many attributes (see https://developer.twitter.com/en/docs/tweets/data-dictionary/overview/user-object for more details)
                       user_name = user_info.name
                       user_description = user_info.description
                   except Exception as e:
                          print(e)
                          continue
                   l_name = extract_lastname_from_userName(user_name, LastNames_set)
                   print('\n extracted lastName = {} \n'.format(l_name))

                   if l_name != None:
                      # query with last name
                      Nbr_pages = 30   # Nbr of Twitter pages to search in
                      Nbr_users = 20   # Nbr of users per page
                      for i in range(Nbr_pages):
                          try:
                             statuss = api.search_users(q=l_name, page = i, count = Nbr_users)
                             for status in statuss:
                                 #print("insert "+query+" "+str(i)+"/"+str(Nbr_pages))
                                 db.insertIntoTable(status,query, lastNa =query,  userType= 'person' )
                          except Exception as e:
                                 print(e)
                                 fwerr.write(query + '\n')
                                 print("exception of api query when screenName= %s ! \n"%query)
                      db.connect.commit()
                      fw.write(query + '\n')
                      print('\nuser_name = {} \n user_description = {} '.format(user_name.encode('ascii','ignore') ,user_description.encode('ascii','ignore') ))
                      print('Extracted lastName: {} processed'.format(query))

    else:
        print('select seed_type param from {ln,sn} ')
    db.connect.commit()
    print ("db committed !")

#==============================================================================
def getUsers(api, db, lastName_seed,screenName_seed,seed_type):
    print("\nget Users starting...")
    getAmbiguousUsers( api, db,lastName_seed,screenName_seed,seed_type)

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

        # listedCount: number of lists, this user is member of
    def createUsersTable(self):
        self.c.execute('''create table twitterUsers(
        userId integer PRIMARY KEY,
        userScreenName text,
        userSearchQuery text,
        userSearchQueryType text,
        userSearchQueryFirstName text,
        userSearchQueryLasttName text,
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

    def insertIntoTable(self,status, _userSearchQuery, firstNa = None, lastNa = None, userType = None):
        #======================================================================
        userSearchQueryType =  userType
        userSearchQueryFirstName = firstNa
        userSearchQueryLasttName = lastNa
        #======================================================================
        userSearchQuery = _userSearchQuery.strip()
        userScreenName = status._json.get('screen_name').strip().encode('ascii','ignore')
        userId = int(status._json.get('id'))
        #======================================================================
        #======================================================================
        userName = status._json.get('name').strip().encode('ascii','ignore')
        userLocation = status._json.get('location').encode('ascii','ignore')
        userUrl = status._json.get('url')
        userDescription = status._json.get('description').strip().encode('ascii','ignore')
        followersCount = int(status._json.get('followers_count'))
        friends_count = int(status._json.get('friends_count'))
        listedCount = int(status._json.get('listed_count'))
        favouritesCount = int(status._json.get('favourites_count'))
        userCreatedAt = status._json.get('created_at')
        verified = status._json.get('verified')
        userLang = status._json.get('lang')
        profileBackgroundImageUrl  = status._json.get('profile_background_image_url')
        profileImageUrl = status._json.get('profile_image_url')
        profileBannerUrl = status._json.get('profile_banner_url')
        #======================================================================
        twitterUsers_sql = "INSERT OR IGNORE INTO twitterUsers (userId,userScreenName,userSearchQuery,userSearchQueryType,userSearchQueryFirstName,userSearchQueryLasttName ,userName,userLocation,userUrl,userDescription,followersCount,friends_count,listedCount,favouritesCount ,userCreatedAt,verified,lang, profileBackgroundImageUrl, profileImageUrl, profileBannerUrl ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"
        if verified == 1:
           if  userSearchQuery in userScreenName or userSearchQuery in userName:
               print userName  + " --> @" + userScreenName
               self.c.execute(twitterUsers_sql, (userId,userScreenName, userSearchQuery,userSearchQueryType,userSearchQueryFirstName,userSearchQueryLasttName, userName,userLocation,userUrl,userDescription,followersCount,friends_count,listedCount,favouritesCount ,userCreatedAt,verified,userLang, profileBackgroundImageUrl, profileImageUrl, profileBannerUrl))
           #else:
               #print(userSearchQuery+" is not ambiguous")

# get sting between two chars :
def getString_between( s, first, last ):
    try:
       start = s.index( first ) + len( first )
       end = s.index( last, start )
       return s[start:end]
    except ValueError:
           return ""

def main(argv):
    start_time = time.time()
    parser=argparse.ArgumentParser("Data Collection")
    parser.add_argument('-db_name',dest="db_name", type=str, help='ambiguous user DB name')
    parser.add_argument('-lastName_seed',dest="lastName_seed", type=str, help='lastName_seed for ambiguous users search')
    parser.add_argument('-screenName_seed',dest="screenName_seed",default=None, type=str, help='screenName_seed for ambiguous users search')
    parser.add_argument('-seed_type',dest="seed_type", type=str, help=' ln for lastname seed list / sn for screename seed list (Needs a screen name list using screenName_seed param )')

    # check args
    param=parser.parse_args()
    db_name = param.db_name
    lastName_seed = param.lastName_seed
    screenName_seed = param.screenName_seed
    seed_type = param.seed_type

    # Create/load DataBase
    if os.path.exists('./' + db_name) :
       db=Database(db_name)
       print('\nDatabase loaded !')
    else:
        db=Database(db_name)
        db.createUsersTable()
        print('\nDatabase created !')

    #authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    print ("authentification occured! \n"    )
#
    getUsers(api, db, lastName_seed,screenName_seed,seed_type)

    print("\n data Collected")
    print("--- %s seconds ---" % (time.time() - start_time))

main(sys.argv[1:])




