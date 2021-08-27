#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# copyright  Copyright (C) 2021 by CEA - LIST
#

import sys,argparse
import re
from collections import defaultdict

#----------------------------------------------------------------------

def replace_ambiguous(screenname2mention,f):
    for line in f:
        try:
            tweetid,content,img=line.rstrip().split("\t")
        except ValueError:
            sys.stderr.write("--Warning: incomplete line for tweet {}\n".format(tweetid))
            continue
        
        found=False
        for sn in re.finditer("@\w+",content):
            name=sn.group(0)
            if name in screenname2mention:
                mention=screenname2mention[name]
                text=content.replace(name,mention)
                pos_begin=sn.start()
                pos_end=pos_begin+len(mention)
                print("\t".join(map(str,[tweetid,pos_begin,pos_end,mention,name,text,img])))
                found=True
                continue
        if not found:
            sys.stderr.write("--Warning: no ambiguous screen name found for tweet {}\n".format(tweetid))
            continue
            

#----------------------------------------------------------------------
# main function
def main(argv):
    # parse command-line arguments
    parser=argparse.ArgumentParser(description="")
    # optional arguments
    #parser.add_argument("--arg",type=int,default=42,help="description")
    # positional arguments
    parser.add_argument("ambiguous",type=argparse.FileType('r',encoding='UTF-8'),help="the file containing the ambiguous mentions with their possible screen names")
    parser.add_argument("tweets_file",type=argparse.FileType('r',encoding='UTF-8'),help="a file containing tweets in which some ambiguous mentions are present")
    
    param=parser.parse_args()

    # do main
    # get mapping for ambiguous mentions
    screenname2mention= defaultdict(str)
    for mm in param.ambiguous.readlines():
        sn,mention = mm.rstrip().split('|')
        screenname2mention[sn] = mention

    replace_ambiguous(screenname2mention,param.tweets_file)
    
if __name__ == "__main__":
    main(sys.argv[1:])
