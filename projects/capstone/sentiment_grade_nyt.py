import sys
import os
import json
reload(sys)
sys.setdefaultencoding('utf8')
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from dateutil.parser import parse
from dateutil.tz import tzutc
from datetime import datetime, date, time, timedelta

"""
Generate analysis of article data, including sentiment scores for selected text. Output JSON file will contain a list of dictionaries of the form:
    [
        {'_id':*, 'headline':*, 'pub_date':*, 'trade_date':*, 'headline_senti':*, 'summary_senti':*, 'headline_summary_senti':*, 'lead_paragraph_senti':*, 'keyword_in_headline':*, 'keyword_in_summary':* , 'keyword_org_rank_alt':* }, 
        {...},
        ...
    ]

    keys & values:
    - _id: article id
    - headline: original text of the main headline
    - pub_date: article's publishing date and time
    - trade_date: the immediate trading day that overlaps the article's publishing date, taken to be:
        - pub_date if:  pub_datetime < (closing time of trade_date) - (minimum market reaction time)
        - pub_date +1, otherwise  
    - headline_senti: sentiment score for the headline            
    - summary_senti: sentiment score for the abstract, or snippet if abstract unavailable
    - headline_summary_senti: sentiment score for the concatenated text of the headline followed by the summary
    - lead_paragraph_senti:''' 
    - keyword_in_headline: 1 if found in headline, 0 otherwise
    - keyword_in_summary: '''
    - keyword_org_rank_alt: if Google was mentioned under the keyword 'organization' along with N other organizations, the rank is 1/N; 0 if the Google was not mentioned

"""


years = [2016, 2015, 2014, 2013, 2012, 2011,
         2010, 2009, 2008, 2007, 2006, 2005, 2004]
months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

market_reaction_time_min_seconds = 0  # to be determined

sid = SentimentIntensityAnalyzer()

for year in years:
    for month in months:

        file_str = './data/ny_times/google/articles/' + \
            str(year) + '-' + '{:02}'.format(month) + '.json'
        out_file_str = './data/ny_times/google/sentiments/' + \
            str(year) + '-' + '{:02}'.format(month) + '.json'
        error_log_str = './data/ny_times/google/sentiments/' + \
            str(year) + '-' + '{:02}'.format(month) + '_error.txt'

        with open(file_str, 'r') as f_in:
            articles_dict = json.load(f_in)
        f_in.close()

        f_error_out = open(error_log_str, 'w')

        print "Processing " + str(year) + '-' + '{:02}'.format(month)

        result_set = {}
        articles = articles_dict['response']['docs']

        # analyze articles
        for article in articles:
            article_ana = {}
            
            try:
                article_ana['_id'] = unicode(article['_id'])
                article_ana['headline'] = unicode(article['headline']['main'])
                article_ana['headline_senti'] = sid.polarity_scores(article_ana['headline'])['compound']
                
                article_ana['pub_date'] = unicode(article['pub_date'])
                pub_datetime = parse(article_ana['pub_date'])

                # trading day open time for NYSE, NASDAQ = 14:30 UTC
                trade_datetime_open = datetime.combine(pub_datetime.date(), time(14,30, tzinfo=tzutc()))
                # article is associated with the next trading day if its publication time is on or after the effective trading day's open time (open time + market_reaction_time_min)
                trade_date = pub_datetime.date() if pub_datetime - \
                    timedelta(seconds=market_reaction_time_min_seconds) < trade_datetime_open else (pub_datetime + timedelta(days=1)).date()
                if trade_date.weekday() >= 5: # check if it falls on a weekend
                    trade_date += timedelta(days=(7 - trade_date.weekday()))
                article_ana['trade_date'] = unicode(trade_date)
                
                lead_paragraph = unicode(article['lead_paragraph'])
                article_ana['lead_paragraph_senti'] = sid.polarity_scores(lead_paragraph)['compound']

                if article['abstract'] is None and article['snippet'] is None:
                    f_error_out.write('No summary available for \'' + article_ana['headline'] + '\'')
                    continue  # skip over this article
                # will substitute abstract with snippet if abstract unavailable
                summary = unicode(article['abstract']) if article['abstract'] is not None else unicode(article['snippet'])
                article_ana['summary_senti'] = sid.polarity_scores(summary)['compound']

                article_ana['headline_summary_senti'] = sid.polarity_scores(article_ana['headline'] + '. ' + summary)['compound']
                article_ana['keyword_in_headline'] = 1 if ('Google' in article_ana['headline'] or 'GOOGLE' in article_ana['headline']) else 0
                article_ana['keyword_in_summary'] =  1 if ('Google' in summary or 'GOOGLE' in summary) else 0

                keywords = article['keywords']
                org_keywords = [word['value'] for word in keywords if word['name'] == 'organizations']
                keyword_org_rank = 0.0
                try:
                    keyword_org_rank = sum([1 for word in org_keywords if ('Google' in word or 'GOOGLE' in word)])/float(len(org_keywords))
                except ZeroDivisionError:
                    pass
                article_ana['keyword_org_rank_alt'] = keyword_org_rank

            except Exception as e:  # some 'docs' elements are not articles, e.g. "Interactive Feature", ignore
                print(str(e))
                f_error_out.write('\n Exception: ' + str(e) + '\n')
                json.dump(article, f_error_out)
                continue

            result_set[article_ana['_id']] = article_ana

        with open(out_file_str, 'w') as fout:
            json.dump(result_set, fout)
        fout.close()

        f_error_out.close()
        if os.path.getsize(error_log_str)==0:
            os.remove(error_log_str)



