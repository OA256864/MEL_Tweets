# Download and create dataset

All the following material is released under the [licence CC-BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/3.0/)

mel_dataset.tar.bz2 available [here](https://drive.google.com/open?id=1kkRpVJpo-U6Gt_r4Ly-ciq4pAY03CoTg)
ambiguousUsers.db.gz available [here](https://drive.google.com/open?id=1qYGTUJlkzyFbSTeGP-g1PVefkq8VgUwA)

In practice, you can run:
```
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1qYGTUJlkzyFbSTeGP-g1PVefkq8VgUwA' -O ambiguousUsers.db.gz
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1kkRpVJpo-U6Gt_r4Ly-ciq4pAY03CoTg' -O mel_dataset.tar.bz2
```

Let `gunzip ambiguousUsers.db.gz` then  create the screennames/mention mapping file with `sqlite3 ambiguousUsers.db` and:
```
sqlite> .output mapSreenNameToMention.txt
sqlite> select ('@'||userScreenName),userSearchQueryLasttName from twitterUsers;
```

Then modify the script `get_original_corpus.py` to process all the tweets as wanted. The current script only displays the full text of the tweets (raw and with modified screennames with ambiguous mentions) and the images URL (and skips non existing tweets).
```
conda create --name mael python=3.8
conda activate mael
pip install tweepy

tar xjf mel_dataset.tar.bz2
python get_original_corpus.py
```
Finaly, let download the images from their URLs.

# md5sum

md5sum of uncompressed files:
```
afbd9692d98eeffeb4e4008ae3c02a39  mel_dev_ids
8e5036b5c337a6cf0461d3f478858d2c  mel_test_ids
475fec98ad3e26c2798c217136466cd9  mel_train_ids
6ed8a18f479d03932587d07485f6a5e2  kb

8a8d1f8b6676992915da4f33b7b8db52  ambiguousUsers.db
```

