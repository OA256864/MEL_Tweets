# -*- coding: utf-8 -*-
"""
Created on Tue Nov 27 11:56:23 2018

@author: omar

WARNING: need the file 'mapSreenNameToMention.txt'
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


def mention_processing(db_curs, output_filename):
    #==============================================================================
    punct = ['~', ':', "'", "'s", '+', '[', '\\', '@', '^', '{', '%', '(', '-', '"', '*', '|', ',', '&', '<', '`', '}', '.', '_', '=', ']', '!', '>', ';', '?', '#', '$', ')', '/']

    f = open('mapSreenNameToMention.txt',mode="r")
    fw = open(output_filename,mode="w")
    mapSreenNameToMention = {}
    while 1:
          lines = f.readlines(100000)
          if not lines:
             break
          for line in lines:
              mention = line.split('|')[1].strip()
              screenName = str(line.split('|')[0].strip())
              mapSreenNameToMention[screenName] = mention
    print ('Users loaded')
    nbrException = 0
    i = 0
    query = "SELECT tweetId, querySearch,replace(replace(replace(tweetFullText,'\n',' '),'\r',' '),'\t',' '),mediaURL FROM searchTweets WHERE mediaURL!='';"
#        self.c.execute (query)
#            rows = self.c.fetchall()
    for row in db_curs.execute (query):

        querySearch = row[1]
        if querySearch not in mapSreenNameToMention:
           continue
        mention =  mapSreenNameToMention[querySearch]

        tweetId = int(row[0])
        tweetFullText = row[2]
        # ignore tweets with more than 4 '@' (screenNames)
        if tweetFullText.count('@') > 4:
          continue
        #=============================== Clean tweets from URLs================
        httpStr = ''
        for x in tweetFullText.split(None):
            if "http" in str(x):
                httpStr = str(x)
        tweetFullText = tweetFullText.replace(httpStr,'')
        #=====ignore tweets where mention is between many otehrs===============
        k = 0
        qsi = 0
        for x in tweetFullText.split(None):
            if str(querySearch) in str(x):
               qsi = k
               break
            k +=1
        patt =  tweetFullText.split(None)
        if qsi == len(patt)-1 and '@' in patt[qsi -1]:
            continue

        if ('@' in patt[qsi -1] and '@' in patt[qsi +1]):
           continue
        if ('@' in patt[qsi -1] and '#' in patt[qsi +1]):
           continue
        if ('via' in patt[qsi -1]):
           continue
        if qsi == 0 and ('@' in patt[qsi +1]):
           continue
        if tweetFullText.split(patt[qsi])[0].count('@') > 2:
           continue
        if tweetFullText.split(patt[qsi])[1].count('@') > 1:
           continue
        if qsi == len(patt)-2 and '@' in patt[qsi +1]:
            continue
        #======================================================================
        # replace screen Name with mention
        tweetFullText = tweetFullText.replace(querySearch,mention)

        try:
           startPos = tweetFullText.index(mention)
        except:
              nbrException+=1
              continue
        endPos = startPos + len(mention)
        #=====ignore tweets without image======================================
        mediaURL = row[3]
        if  mediaURL=='' or mediaURL==None or mediaURL=='none':
            continue
        fw.write(str(tweetId) + '\t' + str(startPos) + '\t' + str(endPos) +'\t' + mention +  '\t'+ str(querySearch) + '\t' + str(tweetFullText) + '\t' + str(mediaURL) + '\n')
        i+=1
    print('nbrOfTweets = ' + str(i))


def main(argv):
    start_time = time.time()
    parser=argparse.ArgumentParser("Mention ground truth replacement")
    parser.add_argument('-db_name',dest="db_name", type=str, help='DB name')
    parser.add_argument('-o',dest="out_name", type=str, help='output file name')

    # check args
    param=parser.parse_args()
    db_name = param.db_name
    out_name = param.out_name

    # load DataBase
    if os.path.exists('./' + db_name) :
       connect = sqlite3.connect(db_name)
       curs = connect.cursor()
       mention_processing(curs,out_name)
       print('Database loaded !')
    else:
        print(db_name +  ' does not exist!')

    print("\n Processing done!")
    print("--- %s seconds ---" % (time.time() - start_time))

main(sys.argv[1:])
