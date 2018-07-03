import os
import csv
import json
from dateutil.parser import parse
from datetime import datetime, date, timedelta


"""
Generate CSV containing analyzed and raw article data, along with stock prices, to be used for feature selection

"""

prices = {} # Date : Closing_price_adjusted_for_splits
with open ('./data/GOOG.csv') as prices_csv:
    reader = csv.reader(prices_csv)
    header = reader.next()
    date_index, price_index = header.index('Date'), header.index('Close')
    for row in reader:
        prices[row[date_index]] = row[price_index]
prices_csv.close()

outfile = open('./data/ny_times/google/news_features.csv', "w")
writer = csv.writer(outfile, delimiter=',')

years = [2016, 2015, 2014, 2013, 2012, 2011,
         2010, 2009, 2008, 2007, 2006, 2005, 2004]
months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
# years = [2016]
# months = [12]


writer.writerow(['id', 'pub_date', 'headline_senti', 'summary_senti',
                 'headline_summary_senti', 'lead_paragraph_senti', 'keyword_in_headline', 
                 'keyword_in_summary', #'keyword_is_major', 'keyword_rank',
                 'keyword_org_rank_alt', 'section_name', 'type_of_material',
                 'print_page', 'word_count', 'trade_date', 'price'])

articles_count = 0
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
            articles_count +=1
            row = []
            try:
                id = unicode(article['_id'])
                try:
                    s = sentiments_dict[id]
                except KeyError:
                    # article doesn't exist in sentiments file probably due missing critical fields, e.g. both 'snippet' and 'abstract' --> skip
                    continue    
                row.append(id)
                row.append(s['pub_date'])              
                row.append(s['headline_senti'])
                row.append(s['summary_senti'])
                row.append(s['headline_summary_senti'])
                row.append(s['lead_paragraph_senti'])
                row.append(s['keyword_in_headline'])
                row.append(s['keyword_in_summary'])

                ## attributes 'rank' and 'is_major'/'isMajor' only became available circa 2013 --> omitting these for uniformity with older format
                # keywords_org = [keyword for keyword in article['keywords'] if (
                #     keyword['name'] == "organizations" and ("Google" in unicode(keyword['value']) or "GOOGLE" in unicode(keyword['value'])))]
                # if len(keywords_org)==1:
                #     try: #account for article's keyword change: 'is_major' -> 'isMajor'
                #         row.append(keywords_org[0]['is_major'])
                #     except KeyError:
                #         row.append(keywords_org[0]['isMajor'])
                #     row.append(keywords_org[0]['rank']) 
                # else:
                #     row.append('N')
                #     row.append(0)                       
                row.append(s['keyword_org_rank_alt'])
                row.append(article['section_name'])
                row.append(article['type_of_material']) 
                row.append(article['print_page'] if article['print_page'] is not None else 0)
                row.append(article['word_count'])
                
                # if trade date not found in Yahoo's historical stock data, most likely the date fell on a holiday, use the next available trade date 
                trade_date_found, tries = False, 0
                trade_date = s['trade_date']
                while not trade_date_found and tries <=4:                                        
                    try:                        
                        price = prices[trade_date]
                        trade_date_found = True
                        row.append(trade_date)
                        row.append(price)
                    except KeyError as e:
                        trade_date = unicode((parse(trade_date) + timedelta(days=1)).date())
                        pass
                    tries +=1
                # row.append(1 if tries>1 else 0) #mark entries where trade_date was adjusted if it falls on a holiday        
    
                writer.writerow(row)
            except KeyError as e:
                print ('KeyError: ' + str(e) + '\t' + unicode(s['pub_date'] + '| ' + row))

outfile.close()

print("Period: " + str(min(months)) + '/' + str(min(years)) + ' - ' + str(max(months)) + '/' + str(max(years)))
print("Articles processed: " + str(articles_count))
