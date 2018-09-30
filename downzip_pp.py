import sys
import os
import pickle
import mmap
from StringIO import StringIO
from zipfile import ZipFile
from urllib import urlopen 
from collections import OrderedDict

""" 
This program will download English bigram repository at Google in 2009 and earlier. 
Since the uncompressing the zipped file takes up 1.7GB for each file, the program will 
preprocess on the fly during unzipping. It will also retrieve data: bigram and its count and 
store them in binary format using pickle. 
"""

def generate_filenames(prefix, start, end):
    """This will generate filenames such as prefixstart.csv ...to prefixend.csv"""

    filenames = []
    start = int(start)
    end = int(end)
    
    for i in range(start, end+1, 1):
        filename = ''.join([prefix, str(i), '.csv'])
        filenames.append(filename)
    return filenames

def generate_url(url_base='', filename='', archive_type='.zip'):
    """This will generate url_basefilename.zip"""
    return ''.join([url_base, filename, archive_type])

def download_file(uri, filename):
    
    url = urlopen(uri)
    odic = OrderedDict()
	# retrieving essential data bigrams and its count on the fly
    # filename = googlebooks-eng-all-2gram-20090715-0.csv ... googlebooks-eng-all-2gram-20090715-99.csv
    with ZipFile(StringIO(url.read())) as zipfile:
        with zipfile.open(filename) as f:
            for line in f:
                fields = line.rstrip().split('\t')
                try:
                    # only keep standard English characters
                    # k = bigram key, v = bigram count value
                    k = fields[0].encode('utf8').decode('ascii').lower()
                except UnicodeDecodeError as e:
                    continue
                else:
                    v = int(fields[2])
                    if k in odic:
                        odic[k] += v       # keep adding the match count if the bigram exists
                    else:
                        odic[k] = v        # assign a new match count if the bigram does not exist yet
    return odic


if __name__ == '__main__':

    names = generate_filenames('googlebooks-eng-all-2gram-20090715-', 67, 99)
    
    url_base = 'http://storage.googleapis.com/books/ngrams/books/'
    file_ext = '.zip'
    
    for i, name in enumerate(names, start=67):
        url_str = generate_url(url_base, name, file_ext)
        print 'downloading and parsing file from %s\n' % (url_str)
        this_dict = download_file(url_str, name)
        
        output_filename = ''.join(['bigrams-', str(i), '.txt'])
        print 'writing file... %s' % (output_filename)
        # saving {"bigram":"count"} dict in binary format
        with open(output_filename, 'wb') as outputfile:
            pickle.dump(this_dict, outputfile)
