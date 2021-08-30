# Download and create dataset

All the following material is released under the [licence CC-BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/3.0/)

mel_dataset.tar.bz2 available [here](https://drive.google.com/open?id=1kkRpVJpo-U6Gt_r4Ly-ciq4pAY03CoTg)
ambiguousUsers.db.gz available [here](https://drive.google.com/open?id=1qYGTUJlkzyFbSTeGP-g1PVefkq8VgUwA)

In practice, you can run:
```
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1qYGTUJlkzyFbSTeGP-g1PVefkq8VgUwA' -O ambiguousUsers.db.gz
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1kkRpVJpo-U6Gt_r4Ly-ciq4pAY03CoTg' -O mel_dataset.tar.bz2
```

The script `get_original_corpus.py` allows to retrieve the tweets from the tweet ids (the script can be modified to process the tweet as wanted). The twitter API credentials must be specified in the file `twitterAPI.credentials`. The current script outputs the full text of the tweets and the images URL (and skip non existing tweets) and, in case of the kb, the screen name of its author (to get its timeline).
The download of the images from the URLs in not included in the script: it must be performed separately.

```
conda create --name mael python=3.8
conda activate mael
pip install tweepy

tar xjf mel_dataset.tar.bz2
python get_original_corpus.py
```

Then, the script `replace_ambiguous_mentions.py` creates the evaluation dataset by replacing the screen names by ambiguous mentions, according to the data from `ambiguousUsers.db`.

Let `gunzip ambiguousUsers.db.gz` then  create the screennames/mention mapping file with `sqlite3 ambiguousUsers.db` and:
```
sqlite> .output mapSreenNameToMention.txt
sqlite> select ('@'||userScreenName),userSearchQueryLasttName from twitterUsers;
```

and then replace the mentions:

```
python replace_ambiguous_mentions.py mapSreenNameToMention.txt train_tweets.txt > train.txt
```

The output format is: one line per tweet, with the following tab-separated fields:

- tweet id
- start position of mention to disambiguate
- end position of mention to disambiguate
- text of mention to disambiguate
- disambiguated screen name
- text of tweet
- url of associated image


# md5sum

md5sum of uncompressed files:
```
afbd9692d98eeffeb4e4008ae3c02a39  mel_dev_ids
8e5036b5c337a6cf0461d3f478858d2c  mel_test_ids
475fec98ad3e26c2798c217136466cd9  mel_train_ids
6ed8a18f479d03932587d07485f6a5e2  kb

8a8d1f8b6676992915da4f33b7b8db52  ambiguousUsers.db
```

