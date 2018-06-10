import sys
import csv
import json
reload(sys)
sys.setdefaultencoding('utf8')

"""
Filter collected NY Times data to retain only those that mention at least one of the following terms in their headline, abstract, snippet, or lead paragraph:	
'Google', 'GOOGLE'

"""

years = [2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007, 2006, 2005, 2004]
months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
search_terms = ['Google', 'GOOGLE']
# Other related terms that includes Alphabet's other subsidiaries: 
#   'Alphabet', 'Calico', 'CapitalG', 'Chronicle', 'DeepMind', 'Google', 'Fiber', 'GV', 'Jigsaw', 'Sidewalk', 'Labs', 'Verily', 'Waymo', 'X'
# Subset of terms with less ambiguity:
#   'Calico','CapitalG','DeepMind','Google','Waymo'

for year in years:
    for month in months:
        
        file_str = './data/ny_times/all/' + \
            str(year) + '-' + '{:02}'.format(month) + '.json'
        out_file_str = './data/ny_times/google/' + \
            str(year) + '-' + '{:02}'.format(month) + '.json'
        error_log_str = './data/ny_times/google/' + \
            str(year) + '-' + '{:02}'.format(month) + '_error.txt'

        with open(file_str, 'r') as f_in:
            mydict = json.load(f_in)
        f_in.close()

        f_error_out = open(error_log_str, 'w')

        print "Processing " + str(year) + '-' + '{:02}'.format(month)

        articles = mydict['response']['docs']
        articles_retained = []
        count = 0
        for article in articles:
            try:
                main_headline = unicode(article['headline']['main'])
                snippet = unicode(article['snippet'])
                abstract = unicode(article['abstract'])
                lead_paragraph = unicode(article['lead_paragraph'])
            except Exception as e:  # some 'docs' elements are not articles, e.g. "Interactive Feature", ignore
                print(str(e))
                f_error_out.write('\n Exception: ' + str(e) + '\n')
                json.dump(article, f_error_out)
                continue
         
            search_term_found = False
            for term in search_terms:
                if (term in main_headline) or (term in snippet) or (term in abstract) or (term in lead_paragraph):
                    search_term_found = True
                    break

            if search_term_found:
                articles_retained.append(article)
                count += 1
                print(unicode(count) + '\t' + main_headline + '\n')

        mydict['response']['docs'] = articles_retained
        mydict['response']['meta']['hits'] = count

        with open(out_file_str, 'w') as fout:
            json.dump(mydict, fout)
        fout.close()

        f_error_out.close()

        
