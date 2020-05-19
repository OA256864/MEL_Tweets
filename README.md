
**Multimodal Entity Linking** (MEL) consists in combining information from several modalities (textual, visual...) to map an ambiguous mention to an entity in a knowledge base (KB). We propose a MEL dataset based on Twitter posts, and elaborate a process for collecting and constructing a fully annotated MEL dataset, where entities are defined in a Twitter KB. This repository contains:
- the data and their annotation that correspond to the corpus used in our LREC 2020 article [1].
- the programs that allows to build your own MEL dataset from Twitter, with the process proposed at ECIR 2020 [2]

## Conda install example
```
conda create -n mael python=2.7
conda activate mael
conda install -c conda-forge tweepy python-wget
conda install -c anaconda nltk
conda install numpy # for program splitGroudTruths.py only
# with python 2.7 only
conda install configparser
```

## Corpus

### Released Corpus
The corpus is available at [this address](https://drive.google.com/open?id=1kkRpVJpo-U6Gt_r4Ly-ciq4pAY03CoTg) under the licence [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/).
We provide the identifiers of the tweets that were used in [1,2]. Due to the Twitter policy we do not release the full (*hydratated*) content : see [here](https://developer.twitter.com/en/developer-terms/more-on-restricted-use-cases) at *Redistribution of Twitter content*. We also provide a program to retrieve a Tweet content from its ID and convert it to the appropriate format. All the material is in the folder `corpus`:
- `mel_train_ids` 35,976 ids of the training evaluation corpus 
- `mel_dev_ids` 16,599 ids of the dev evaluation corpus 
- `mel_test_ids` 36,521 ids of the test evaluation corpus 
- `kb` 2,657,213 ids of the knowledge database

Send us a mail if you have problem.

### Build your own Corpus
You can create a corpus similar to that we used by using the program we provide. For this, you need [Twitter API credentials](https://developer.twitter.com/en.html). Then use the programs and seed files in `code/corpus`. The steps are:
- collect data and store them into a (sqlite3) database
- convert data into files to create (i) the knowledge database (ii) the evaluation corpus

A seed file is a text file that contain all Twitter screen names (@xxxx, one per line) to query. The corresponding accounts are collected as is:
- all the tweets (up to the imit of the Twitter API) of the timeline to create the knowledge database
- the recent tweets as possible samples to be included in the evaluation corpus

#### Collect data from Twitter
To collect data and store it in the database `my_knowledge.db` let report your Twitter API credentials into `twitterDataDB.py` (line 24-27), then:

```
python twitterDataDB.py -db_name my_knowledge.db  -seed_file seed_files/xxx.txt -query e
python twitterDataDB.py -db_name my_knowledge.db  -seed_file seed_files/yyy.txt -query m
```
If you use `-query e` it collects tweet from *entities* to create the knowledge database. With `-query m` it collects tweets with potential *mentions* to create the evaluation corpus.

#### Create the knowledge database
Once data are stored in `my_knowledge.db` you can create the corresponding file with `sqlite3 my_knowledge.db` then:
```
sqlite> .output timelineKB.txt
sqlite> .separator "\t" "\n"
sqlite> select ('@'||userScreenName),tweetId,replace(replace(replace(tweetFullText,CHAR(10),' '),CHAR(13),' '),CHAR(9),' '),mediaURL from timeLineTweets where mediaURL!='' order by userScreenName;

```
The knowledge dataset is then the text file `timelineKB.txt`. It has one line per sample and the columns (tab separator) are:
- original screen names
- tweet identifiers
- textual content
- visual content (image URL)

You can download the images using their URL (fourth column)

#### Create the evaluation corpus
You need to identify *ambiguous users* such that the corpus is more challenging. To seek ambiguous last names use:

```
python get_ambiguous_users.py -db_name ambiguousUsers.db \
                              -lastName_seed seed_files/popLastNames.txt \
                              -screenName_seed seed_files/HouseRepublicans.txt \
                              -seed_type ln
```
use `-seed_type sn` to seek ambiguous screen names (less useful).

A version of such a database of ambiguous users is available [here](https://drive.google.com/open?id=1qYGTUJlkzyFbSTeGP-g1PVefkq8VgUwA).

Then let generate a map between screen names and mentions, using `sqlite3 ambiguousUsers.db`:
```
sqlite> .output mapSreenNameToMention.txt
sqlite> select ('@'||userScreenName),userSearchQueryLasttName from twitterUsers;
```
Using `mapSreenNameToMention.txt`, you can now generate tweets with ambiguous mentions from table `searchTweets` in `my_knowledge.db`:
```
python generate_groundTruthTweets.py -db_name my_knowledge.db  -o groundTruth.txt
```

You can finally create the corresponding {Train/Dev/Test}.txt files with:

```
python splitGroudTruths.py -i groundTruth.txt
```

### Quick test the full pipeline
Since the full process is quite long, we provide a small seed file to test the programs. 

```
python twitterDataDB.py -db_name test0.db  -seed_file quick_test/AAA.txt -query e
python twitterDataDB.py -db_name test0.db  -seed_file quick_test/AAA.txt -query m
sqlite3 test0.db < quick_test/create_timeline.sql
wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1qYGTUJlkzyFbSTeGP-g1PVefkq8VgUwA' -O ambiguousUsers.db.gz
gunzip ambiguousUsers.db.gz
sqlite3 ambiguousUsers.db < quick_test/create_mapSreenNameToMention.sql
python generate_groundTruthTweets.py -db_name test0.db -o groundTruth.txt
```
As of May 2020, groundTruth.txt has only 4 tweets for this quick test, splitted into 2 tweets for Train.txt and one in Dev.txt and Test.txt.


## Model

**TODO**

## Reference
If you find this material useful for your research, please cite

```
[1] O. Adjali, R. Besançon, O. Ferret, H. Le Borgne and B. Grau (2020) Building a Multimodal Entity Linking Dataset From Tweets, 12th International Conference on Language Resources and Evaluation (LREC)
[2] O. Adjali, R. Besançon, O. Ferret, H. Le Borgne and B. Grau (2020) Multimodal Entity Linking for Tweets, 42nd European Conference on Information Retrieval (ECIR): Advances in Information Retrieval
```

Bibtex entries:
```
@inproceedings{adjali2020ecir,
    title={Multimodal Entity Linking for Tweets},
    author={Adjali, Omar and Besancon, romaric and Ferret, olivier and {Le Borgne}, Herv{\'e} and Grau, Brigitte},
    booktitle={European Conference on Information Retrieval (ECIR)},
    year={2020},
    month={april},
    day={14--17},
    address={Lisbon, Portugal}
}

@inproceedings{adjali2020lrec,
    title={Building a Multimodal Entity Linking Dataset From Tweets},
    author={Adjali, Omar and Besancon, romaric and Ferret, olivier and {Le Borgne}, Herv{\'e} and Grau, Brigitte},
    booktitle={International Conference on Language Resources and Evaluation (LREC)},
    year={2020},
    month={may},
    day={11--16},
    address={Marseille, France}
}
```
