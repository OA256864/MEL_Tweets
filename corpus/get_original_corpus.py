# -*- coding: utf-8 -*-
#

# Possible environment:
#   conda create --name mael python=3.8
#   conda activate mael
#   pip install tweepy
import tweepy
from tweepy import OAuthHandler
from collections import defaultdict

# get mapping for ambiguous mentions
screenname2mention= defaultdict(str)
with open('mapSreenNameToMention.txt','r') as ff:
    for mm in ff.readlines():
        sn_men = mm.strip().split('|')
        screenname2mention[sn_men[0]] = sn_men[1]

def replace_mention(full_text,screenname2mention):
    all_screennames = [word for word in full_text.split() if word.startswith('@')]
    new_text = full_text
    for sn in all_screennames:
        mention = screenname2mention.get(sn)
        if mention is not None:
            new_text=new_text.replace(sn, mention)
    return new_text

# main process
def process_list_ids(ids_filename,screenname2mention):
    f_ids = open(ids_filename,'r')
    for ii in f_ids.readlines():
        id_of_tweet = ii.strip() # e.g id_of_tweet='1065824565706686464'
        print("get tweet {}".format(id_of_tweet))
        try:
            tweet = api.get_status(id_of_tweet, tweet_mode="extended")
            # TODO process [text] and [img URL] as you want
            # you need to dowload the image afterward
            print("\t\t[raw text]: {}".format(tweet.full_text))
            print("\t\t[modified text]: {}".format( replace_mention(tweet.full_text,screenname2mention)))
            print("\t\t[img url]: {}".format(tweet.entities['media'][0]['media_url']))
        except tweepy.TweepError as e:
            print("\t\terror code {} message: {}".format(e.args[0][0]['code'],e.args[0][0]['message']))
    f_ids.close()

#Twitter API credentials (TODO set your own from your Twitter developper account)
CONSUMER_KEY = "xxxx"
CONSUMER_SECRET = "yyyy"
ACCESS_KEY = "zzz"
ACCESS_KEY_SECRET = "www"

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_KEY_SECRET)
api = tweepy.API(auth)

# process all ids of the training/validation/test dataset
process_list_ids('mel_train_ids',screenname2mention)
process_list_ids('mel_dev_ids',screenname2mention)
process_list_ids('mel_test_ids',screenname2mention)
