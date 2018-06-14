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
Generate analysis of article data, including sentiment scores for selected text. Output will contain a list of dictionaries of the form:
    [
        {'headline':*, 'pub_date':*, 'trade_date':*, 'headline_senti':*, 'summary_senti':*, 'headline_summary_senti':*, 'lead_paragraph_senti':*, 'search_term_in_headline':*, 'search_term_in_summary':* }, 
        {...},
        ...
    ]

    keys & values:
    - headline: original text of the main headline
    - pub_date: article's publishing date and time
    - trade_date is the immediate trading day that could've been affected by the article based on its publishing date, taken to be:
        - pub_date if:  pub_datetime < (closing time of trade_date) - (minimum market reaction time)
        - pub_date +1, otherwise  
    - headline_senti: sentiment score for the headline            
    - summary_senti: sentiment score for the abstract, or snippet if abstract unavailable
    - headline_summary_senti: sentiment score for the concatenated text of the headline followed by the summary
    - lead_paragraph_senti:''' 
    - search_term_in_headline: 1 if found in headline, 0 otherwise
    - search_term_in_summary: '''

"""


years = [2016, 2015, 2014, 2013, 2012, 2011,
         2010, 2009, 2008, 2007, 2006, 2005, 2004]
months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

market_reaction_time_min_seconds = 0

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

        result_set = []
        articles = articles_dict['response']['docs']

        # analyze each article
        for article in articles:
            article_ana = {}
            
            try:
                article_ana['headline'] = unicode(article['headline']['main'])
                article_ana['headline_senti'] = sid.polarity_scores(article_ana['headline'])
                
                article_ana['pub_date'] = unicode(article['pub_date'])
                pub_datetime = parse(article_ana['pub_date'])
                # pub_date = date(pub_datetime.year, pub_datetime.month, pub_datetime.day)
                # pub_time = time(pub_datetime.hour, pub_datetime.minute, tzinfo=pub_datetime.tzinfo)
                # effective trading day close time = 21:00UTC - market_reaction_time_min
                trade_datetime_close = datetime.combine(pub_datetime.date(), time(21,0, tzinfo=tzutc()))
                # article is associate with the next trading day if its publication time is on or after the effective trading day's close time
                trade_date = pub_datetime.date() if pub_datetime + \
                    timedelta(seconds=market_reaction_time_min_seconds) < trade_datetime_close else (pub_datetime + timedelta(days=1)).date()
                article_ana['trade_date'] = unicode(trade_date)
                
                lead_paragraph = unicode(article['lead_paragraph'])
                article_ana['lead_paragraph_senti'] = sid.polarity_scores(lead_paragraph)

                if article['abstract'] is None and article['snippet'] is None:
                    f_error_out.write('No summary available for \'' + article_ana['headline'] + '\'')
                    continue  # skip over this article
                # will substitute abstract with snippet if abstract unavailable
                summary = unicode(article['abstract']) if article['abstract'] is not None else unicode(article['snippet'])
                article_ana['summary_senti'] = sid.polarity_scores(summary)

                article_ana['headline_summary_senti'] = sid.polarity_scores(article_ana['headline'] + '. ' + summary)
                article_ana['search_term_in_headline'] = 1 if ('Google' in article_ana['headline'] or 'GOOGLE' in article_ana['headline']) else 0
                article_ana['search_term_in_summary'] =  1 if ('Google' in summary or 'GOOGLE' in summary) else 0

            except Exception as e:  # some 'docs' elements are not articles, e.g. "Interactive Feature", ignore
                print(str(e))
                f_error_out.write('\n Exception: ' + str(e) + '\n')
                json.dump(article, f_error_out)
                continue

            result_set.append(article_ana)

        with open(out_file_str, 'w') as fout:
            json.dump(result_set, fout)
        fout.close()

        f_error_out.close()
        if os.path.getsize(error_log_str)==0:
            os.remove(error_log_str)



