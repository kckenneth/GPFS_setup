import sqlite3 as sq
import pickle
import cPickle as cp
import sys
import os
import time

"""
This program will create SQL database using sqlite3. The bigram and counts we stored 
in binary format by pickle will be inserted into SQL table so that we can query in later step.
"""

def load_pickle(input_file):
    # input_file = '/gpfs/gpfsfpo/bigrams/bigrams-0.txt'
    # bigrams-0.txt is a dictionary {'bigram key': 'bigram count value'} in binary format
    with open(input_file, 'r') as f:
        return cp.load(f)


def split_bigram(bigram):
    """return bigram into two unigrams"""
    try:
        f, s = bigram.split(' ')
    except Exception as e:
        return None
    else:
        return (f, s)


def create_database_table(target_db):
    """Creating SQL table"""
    # target_db = gpfsX_bigrams.db
    # table name = bigram_counts
    with sq.connect(target_db) as conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT SQLITE_VERSION()")
            cur.execute("DROP TABLE IF EXISTS bigram_counts")
            cur.execute('''CREATE TABLE IF NOT EXISTS bigram_counts
                           (FirstWord TEXT NOT NULL, SecondWord TEXT NOT NULL, Count INTEGER, PRIMARY KEY (FirstWord, SecondWord))''')
            conn.commit()
        except sq.Error as e:
            if conn:
                conn.rollback()
            print 'error occurred: %s' % e.args[0]
            sys.exit(1)

def insert_into_database(input_data, target_db):
    """updating the table with bigram and its count data"""
    # input_data = {"bigram key":"bigram count value"} dictionary
    # target_db = gpfsX_bigrams.db
    
    with sq.connect(target_db) as conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT SQLITE_VERSION()")
            # cur.execute("DROP TABLE IF EXISTS bigram_counts")
            cur.execute("CREATE TABLE IF NOT EXISTS bigram_counts(FirstWord TEXT NOT NULL, SecondWord TEXT NOT NULL, Count INTEGER, PRIMARY KEY (FirstWord, SecondWord))")
            conn.commit()
            for bigram, count in input_data.iteritems():
                t = split_bigram(bigram)
                if t:
                    f, s = t[0], t[1]
                    cur.execute('SELECT * FROM bigram_counts WHERE FirstWord=:first AND SecondWord=:second', {"first": f, "second": s})
                    res = cur.fetchall()
                    if len(res) == 0:
                        cur.execute("INSERT INTO bigram_counts VALUES(?, ?, ?)", (f, s, count))
                        # print 'inserted row: first: %s second: %s count: %s' % (f, s, count)
                    else:
                        cur.execute("UPDATE bigram_counts SET Count=? WHERE FirstWord=? AND SecondWord=?", (int(res[0][2] + int(count)), f, s))
                        # print 'updated row: first: %s second: %s count: %s' % (f, s, int(res[0][2]) + int(count))
            conn.commit()
        except sq.Error as e:
            if conn:
                conn.rollback()
            print 'error occurred: %s' % e.args[0]
            sys.exit(1)


if __name__ == '__main__':

    # python2 create_db.py /gpfs/gpfsfpo/bigrams/ gpfs1 0 33 /gpfs/gpfsfpo/bigrams/
    
    if len(sys.argv) != 6:
        print 'enter the gpfs .txt data filepath e.g. /gpfs/gpfsfpo/bigrams'
        print 'enter node name prefix e.g. gpfsN'
        print 'enter start and end input file indexes'
        print 'enter db file output path'
    else:
        fs_path = sys.argv[1]
        node_prefix = sys.argv[2]
        fstart_index = int(sys.argv[3])
        fend_index = int(sys.argv[4])
        db_path = sys.argv[5]

        db_file = os.path.join(db_path, ''.join([node_prefix, '_bigrams.db']))
        print 'creating database : %s' % db_file
        create_database_table(db_file)


        for i in range(fstart_index, fend_index+1, 1):
            fname = ''.join([r'bigrams-', str(i), '.txt'])
            in_file = os.path.join(fs_path, fname)
            # in_file = '/gpfs/gpfsfpo/bigrams/bigrams-0.txt'
            print 'reading: %s' % in_file
            t = time.time()
            dataset = load_pickle(in_file)
            print 'time taken to load file: %s' % (time.time() - t)

            insert_into_database(dataset, db_file)
            print 'insert completed for: %s\n' % in_file
