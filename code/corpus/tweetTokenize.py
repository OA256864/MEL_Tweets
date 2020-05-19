import glob
from multiprocessing import Pool
import sys
from nltk import TweetTokenizer
import os
import re
import codecs
import time
import argparse

def preprocess_tweet(tweet):
    tweet = tweet.lower()
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+)|(http?://[^\s]+))','<url>',tweet)
    tweet = re.sub('(\@[^\s]+)','<user>',tweet)
    try:
        tweet = tweet.decode('unicode_escape').encode('ascii','ignore')
    except:
        pass
    return tweet

def tokenize_tweets(input_file_name, out_file_name,type_file):
    outf = open(out_file_name,'w')
    infn = open(input_file_name,'r')
    tknzr = TweetTokenizer()
   
    while 1:                       
          lines = infn.readlines(100000)                         
          if not lines:                    
             break                            
          for line in lines:
              # ignore blank lines                 
              if not line.strip():
                 continue   
              if type_file =='split':
                 tweetId, startPos, endPos, mention, screenName,tweet,mediaURL = line.strip().split('\t')  # test,dev,train tokenization 
              elif type_file =='kb':             
                  x, y,tweet,mediaURL = line.strip().split('\t')  # timeline tokenization
              else:
                  sys.exit("set type param from {split,kb}")

              tweet = tknzr.tokenize(str(tweet))            
#             if not 6 < len(tweet) < 110:
#                    continue
              if len(tweet) < 6:
                 continue
              tweet = preprocess_tweet(' '.join(tweet))
#             out_fs.write(id+'\t'+timestamp+'\t'+username+'\t'+tweet+'\n')                
#             out_fs.write( str(tweetId) + '\t' + str(startPos) + '\t' + str(endPos) +'\t' + mention +  '\t'+ str(screenName) + '\t' + str(tweet) + '\t' + str(mediaURL) + '\n')
              outf.write(str(tweet) +'\n')  

def main(argv):
    start_time = time.time()
    parser=argparse.ArgumentParser("Data Collection")
    parser.add_argument('-i',dest="in_file", type=str, help='input file kb or split file')
    parser.add_argument('-t',dest="type_file", type=str, help='type file set kb or split')
    parser.add_argument('-o',dest="out_file", type=str, help='output tokenized file')
 

    # check args
    param=parser.parse_args() 
    in_file = param.in_file   
    type_file = param.type_file    
    out_file = param.out_file 
    tokenize_tweets(in_file, out_file,type_file)    


    print("\n data tokenized")       
    print("--- %s seconds ---" % (time.time() - start_time))
    
main(sys.argv[1:])   

