# -*- coding: utf-8 -*-
# install first
import GetOldTweets3 as got 
from bs4 import BeautifulSoup
import sentencetoroot as sentencetoroot
import sentence_preprocessing_manager as sentencepreprocessing

# python lib
import datetime
import time

def get_tweets(start_dt, end_dt, keyword, max_tweets=-1):
    start = start_dt
    end = (datetime.datetime.strptime(end_dt, "%Y-%m-%d") 
            + datetime.timedelta(days=1)).strftime("%Y-%m-%d")

    path = "data/tweet/"
    savedfilename = path + "twitter_" + datetime.datetime.now().strftime("%Y%m%d_%H%M") + "_" + keyword + '.json'
    with open(savedfilename, 'w') as fout:
        print("Collecting data start.. from {} to {} with keyword {}".format(start_dt, end_dt, keyword))
        # get data
        start_time = time.time()
        tweetCriteria = got.manager.TweetCriteria().setQuerySearch(keyword)\
            .setSince(start)\
            .setUntil(end)\
            .setMaxTweets(max_tweets)
        try:
            tweets = got.manager.TweetManager.getTweets(tweetCriteria)
        except:
            print("An error occured during an HTTP request: HTTP Error 429: Too Many Requests\n")
            return
        print("Collecting data end.. {0:0.2f} Minutes".format((time.time() - start_time)/60))
        print("=== Total num of tweets is {} ===".format(len(tweets)))
            
        # write
        for tweet in tweets:
            body = tweet.text
            body_preprocessing = sentencepreprocessing.getPreprocessingSent(body)
            body_preprocessing_sentencetoroot, body_preprocessing_sentencetoroot_tag = sentencetoroot.getSentencetoroot_mm(body_preprocessing)

            fout.write('{\n')
            fout.write('\t' + '"keyword": "' + keyword + '",\n')
            fout.write('\t' + '"date": "' + str(int(tweet.date.timestamp())) + '",\n')
            fout.write('\t' + '"body": ' + repr(body) + ',\n')
            fout.write('\t' + '"body_preprocessing": "' + body_preprocessing + '",\n')
            fout.write('\t' + '"body_preprocessing_sentencetoroot": "' + body_preprocessing_sentencetoroot + '",\n')
            fout.write('\t' + '"body_preprocessing_sentencetoroot_tag": "' + body_preprocessing_sentencetoroot_tag + '",\n')
            fout.write('\t' + '"name": ' + '""' + ',\n')
            fout.write('\t' + '"fullname": ' + '""' + '\n')
            fout.write('}')

if __name__ == '__main__':
#    get_tweets("2020-03-23", "2020-03-25", '총선')
#    get_tweets("2020-03-23", "2020-03-25", '더불어민주당')
#    get_tweets("2020-03-23", "2020-03-25", '미래통합당')
#    get_tweets("2020-03-23", "2020-03-25", '민주당')
#    get_tweets("2020-03-23", "2020-03-25", '통합당')
    get_tweets("2020-03-23", "2020-03-23", '코로나')




