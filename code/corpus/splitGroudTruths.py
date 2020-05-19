# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 12:55:46 2019

@author: omar
"""

import numpy as np
import sys,argparse,os

import random


parser=argparse.ArgumentParser("Corpus splitting")
parser.add_argument('-i',dest="corpus_file", type=str, help='ground truth file name')


# check args
param=parser.parse_args()
corpus_file = param.corpus_file

f = open(corpus_file,mode="r")

mapTweetId = {}

# goupe tweets by screen name
nbrTweetsFromGT = 0
while 1:
      lines = f.readlines(100000)
      if not lines:
         break
      for line in lines:

          if not line.strip():
             continue
#          print(line)
          tweetId = line.split('\t')[0].strip()
          startPos = line.split('\t')[1]
          endPos = line.split('\t')[2]
          mention = line.split('\t')[3]
          screenName = line.split('\t')[4]
          tweetFullText = line.split('\t')[5]
          mediaURL = str(line.split('\t')[6]).strip()

          if screenName not in mapTweetId:
             mapTweetId[screenName] = []
          lin = str(tweetId) + '\t' + str(startPos) + '\t' + str(endPos) +'\t' + mention +  '\t'+ str(screenName) + '\t' + str(tweetFullText) + '\t' + str(mediaURL) + '\n'
          mapTweetId[screenName].append(lin)
          nbrTweetsFromGT+= 1

# init Train,Test, Dev splits
fdev = open('Dev.txt',mode="w")
ftrain = open('Train.txt',mode="w")
ftest = open('Test.txt',mode="w")

nbrTweetDev = 0
nbrTweetTest = 0
nbrTweetTrain = 0

# spliting with 50% of all entities are unique to each split

# Get Test Tweets
for screenNameI in  sorted(mapTweetId)[:int(len(mapTweetId)/6)]:
    for lin in mapTweetId[screenNameI]:
        ftest.write(lin)
        nbrTweetTest += 1

# Get Train Tweets
for screenNameI in  sorted(mapTweetId)[int(len(mapTweetId)/6):int(len(mapTweetId)/3)]:
    for lin in mapTweetId[screenNameI]:
        ftrain.write(lin)
        nbrTweetTrain += 1

# Get Dev Tweets
for screenNameI in  sorted(mapTweetId)[int(len(mapTweetId)/3):int(len(mapTweetId)/2)]:
    for lin in mapTweetId[screenNameI]:
        fdev.write(lin)
        nbrTweetDev += 1


# remaining 50%  is randomly spreaded in each split
remainingScreens  = sorted(mapTweetId)[int(len(mapTweetId)/2):]
remainingTweets = []
for screenNameI in remainingScreens:
    for lin in mapTweetId[screenNameI]:
        remainingTweets.append(lin)
# random split
random.shuffle(remainingTweets)

#
for lin in  remainingTweets[:int(len(remainingTweets) * 0.4)]:
     ftest.write(lin)
for lin in  remainingTweets[int(len(remainingTweets) * 0.4) : int(0.9 * len(remainingTweets))]:
     ftrain.write(lin)
for lin in  remainingTweets[ int(len(remainingTweets)* 0.9) :]:
     fdev.write(lin)

print('nbrTweetsFrom Ground truth = ' + str(nbrTweetsFromGT))
print('nbrEntities = ' + str(len(mapTweetId.values() )))




