.output timelineKB.txt
.separator "\t" "\n"
select ('@'||userScreenName),tweetId,replace(replace(replace(tweetFullText,CHAR(10),' '),CHAR(13),' '),CHAR(9),' '),mediaURL from timeLineTweets where mediaURL!='' order by userScreenName;

