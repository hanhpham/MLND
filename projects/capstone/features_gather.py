import os
import csv
import json


"""
Generate CSV containing analyzed and raw article data, along with stock prices, to be used for feature selection

"""

outfile = open('./data/ny_times/google/news_features.csv', "w")
writer = csv.writer(outfile, delimiter=',')

# years = [2016, 2015, 2014, 2013, 2012, 2011,
#          2010, 2009, 2008, 2007, 2006, 2005, 2004]
# months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
years = [2016]
months = [12]


writer.writerow(['id', 'trade_date', 'headline_senti', 'summary_senti',
                 'headline_summary_senti', 'lead_paragraph_senti', 'keyword_in_headline', 
                 'keyword_in_summary', 'keyword_org_rank', 'section_name', 'type_of_material', 'word_count'])

for year in years:
    for month in months:

        sentiments_file = './data/ny_times/google/sentiments/' + \
            str(year) + '-' + '{:02}'.format(month) + '.json'
        raw_articles_file = './data/ny_times/google/articles/' + \
            str(year) + '-' + '{:02}'.format(month) + '.json'
        
        with open(raw_articles_file, 'r') as f_in:
            raw_articles_dict = json.load(f_in)
        f_in.close()

        with open(sentiments_file, 'r') as f_in:
            sentiments_dict = json.load(f_in)
        f_in.close()
        
        articles = raw_articles_dict['response']['docs']

        for article in articles:
            row = []
            try:
                id = unicode(article['_id'])
                s = sentiments_dict[id]
                row.append(id)
                row.append(s['trade_date'])
                row.append(s['headline_senti'])
                row.append(s['summary_senti'])
                row.append(s['headline_summary_senti'])
                row.append(s['lead_paragraph_senti'])
                row.append(s['keyword_in_headline'])
                row.append(s['keyword_in_summary'])
                row.append(s['keyword_org_rank'])
                row.append(s['section_name'])
                row.append(s['type_of_material'])
                row.append(s['word_count'])
            except Exception as e:
                print (str(e) + '\n' + str(s))  #hp todo: clearer msg, add stock price, check trade date determination in test output

            writer.writerow(row)      

outfile.close()