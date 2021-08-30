#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# copyright  Copyright (C) 2021 by CEA - LIST
#

import tweepy
from tweepy import OAuthHandler
import argparse,sys,os

#----------------------------------------------------------------------
# Twitter API credentials
credentials={}
try:
    with open(os.path.join(os.path.dirname(__file__),"twitterAPI.credentials")) as fcred:
        for line in fcred:
            name,value=line.rstrip().split("=")
            credentials[name.strip()]=value.strip()
except IOError:
    sys.stderr.write("Error: failed to open file twitterAPI.credentials\n")
    exit(1)

try:
    auth = tweepy.OAuthHandler(credentials["CONSUMER_KEY"],
                               credentials["CONSUMER_SECRET"])
    auth.set_access_token(credentials["ACCESS_KEY"],
                          credentials["ACCESS_KEY_SECRET"])
    api = tweepy.API(auth)
except Exception as e:
    sys.stderr.write("Error: twitter authentification failed: {}\n".format(str(e)))
    exit(1)
#----------------------------------------------------------------------

def process_list_ids(fids, fout=sys.stdout, output_author=False, sample=None):
    tweetids=fids.readlines()
    if sample:
        tweetids=tweetids[:sample]
    for ii in tweetids:
        id_of_tweet = ii.strip() # e.g id_of_tweet='1065824565706686464'
        try:
            # TODO process [text] and [img URL] as you want
            # you need to dowload the image afterward

            # here, simply output the tweet id, tweet content and image url
            
            tweet = api.get_status(id_of_tweet, tweet_mode="extended")
            content=tweet.full_text.replace("\t","    ").replace("\n"," ")
            img=tweet.entities['media'][0]['media_url']
            if not img:
                sys.stderr.write("--Warning: no image found for tweet id {}\n".format(id_of_tweet))
            
            if output_author:
                fout.write("\t".join([tweet.author.screen_name,id_of_tweet,content,img])+"\n")
            else:
                fout.write("\t".join([id_of_tweet,content,img])+"\n")
            
        except tweepy.TweepError as e:
            sys.stderr.write("--Error on tweet {}: code {}, message: {}\n".format(id_of_tweet,e.args[0][0]['code'],e.args[0][0]['message']))

#----------------------------------------------------------------------
# main function
def main(argv):
    # parse command-line arguments
    parser=argparse.ArgumentParser(description="get tweets from a list of tweet ids, using twitter API")
    # optional arguments
    parser.add_argument("--author",action="store_true",help="output the screen name of the author of the tweet (to get the timeline tweets in the KB)")
    parser.add_argument("--sample",type=int,help="get only the first X tweets (for test)")
    # positional arguments
    parser.add_argument("input_file",nargs="*",type=argparse.FileType('r',encoding='UTF-8'),help="the file containing the list of tweet ids, one per line")
    
    param=parser.parse_args()

    # do main
    if len(param.input_file):
        for f in param.input_file:
            process_list_ids(f,output_author=param.author,sample=param.sample)
    else:
        # use default names  
        # get mel_train_ids, mel_test_ids, mel_dev_ids
        for f in ("train","dev","test"):
            try:
                filename="mel_%s_ids"%f
                with open(filename) as fin:
                    with open("%s_tweets.txt"%f,"w") as fout:
                        process_list_ids(fin,fout,sample=param.sample)
            except IOError:
                sys.stderr.write("Error: failed to open file %s\n"%filename)
        # get kb
        try:
            with open("kb") as fin:
                with open("timeline_KB.txt","w") as fout:
                    process_list_ids(fin,fout,output_author=True,sample=param.sample)
        except IOError:
            sys.stderr.write("Error: failed to open file %s\n"%f)
                
if __name__ == "__main__":
    main(sys.argv[1:])

