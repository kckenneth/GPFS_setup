# Mumbler 

Since we will be using python, we need to install the program and its dependencies in every node. I installed dependencies as necessary. These commands were executed in every node. I also installed python2.7 in case. 
```
# apt update
# apt upgrade
# apt install python2.7 python-pip
# apt install python3 python3-pip
```

# Download Bigram and Preprocess on the fly

Preliminary checking the bigram file, there are 100 and each is about 278MB zip file. Unzipping them into .csv takes up 1.7 GB. 100 of them will require 170GB space. We only have 75GB in total from 3 nodes. We need to figure out a way to preprocess the data on the fly. Otherwise we run out of our 75GB disk space really quick. We will download the zipfile, unzip the file and will retrieve all essential data we want on the fly, i.e., bigram (2 words) and its count. We're not interested in year, page_count and volume_count. We will then dump the data in binary format which can be done in python by pickle.dump(). 

First we will download 1/3 of the data into each of the node. Data won't be replicated across the node. So in order to process the search query in every file in each node and later aggregate the result from each node, you can already imagine that each node has to communicate each other. That's why we set up earlier ssh communication between each node without password. 

### Bigram Dataset

Download google two-gram 27G data set - English version 20090715 from this repository  
http://storage.googleapis.com/books/ngrams/books/datasetsv2.html  
This is **optional** for my knowledge. You don't need to download all files. 
```
# wget http://storage.googleapis.com/books/ngrams/books/googlebooks-eng-all-2gram-20090715-{0..99}.csv.zip
```

This is the actual step in preprocessing the bigram dataset. Do this in all 3 nodes: gpfs1, gpfs2 and gpfs3. In downzip_pp.py (Download Zip file and PreProcess), in order to run from CLI, you might want to check the python path and update in shebang. 
```
# which python3
/usr/bin/python3

# mkdir -p /gpfs/gpfsfpo/bigrams
# cd /gpfs/gpfsfpo/bigrams/
# vi downzip_pp.py
```
You copy and paste from downzip_pp.py. Update the shebang accordingly if you want to run directly from the root as in `# ./downzip_pp.py 0 33`. But this will require to change the script in sys.argv[] position because having #! shebang allows you to run without calling python in CLI. Besides, with the enumerate function in the script which doesn't allow to starting index with string object, I had to manually edit the starting and ending file index. So in gpfs1 `downzip_pp.py`,  
- in line 60, names = generate_filenames('xxx...', 0, 33)    
- in line 65, enumerate(names, start=0)  

So just run as `python2 downzip_pp.py 0 33` in gpfs1.  
```
# chmod 755 downzip_pp.py
# python2 downzip_pp.py
```
In gpfs2, to recap
```
# apt update
# apt upgrade
# apt install python2.7 python-pip
# apt install python3 python3-pip

# mkdir -p /gpfs/gpfsfpo/bigrams
# cd /gpfs/gpfsfpo/bigrams/
# vi downzip_pp.py
```
Make sure you update the index from 34 to 66 in gpfs2 and 67 to 99 in gpfs3. 
```
# python2 downzip_pp.py 
```
Repeat the CLI in gpfs3 as well. This will take hours to download and preprocess those 34, 33, 33 = 100 files in all nodes. You'd see that all those bigrams-0.txt ... bigrams-99.txt output, each with 47.6MB will be viewable in all of the nodes although you're downloading separate indexes from separate nodes. You'll get the idea what this is the case here. 

# Setting up SQL database (foo.db) by sqlite3 in all nodes
More details --> https://docs.python.org/2/library/sqlite3.html  

Basically, we will setup sqlite3 (non standard SQL) in all 3 nodes so that once we query our words, all 3 nodes can execute our jobs in parallel and will generate output. To create a SQL database (file.db), you need to know 5 basic functions of sqlite3. 

1. connect()  
2. cursor()  
3. execute()  
4. commit()  
5. close()  

### 1. connect()
This method will establish a connection to the database (f00.db). 

### 2. cursor ()
This will create an object where you can execute your input data. 

### 3. execute() 
This is where you create your table, insert your data into the table. 

### 4. commit()
Anything you inserted into the table will be lost unless you commit. So you must commit changes. 

### 5. close()
Closing the .db but you can call it back when necessary. 

In gpfs1, 
```
# cd /gpfs/gpfsfpo/bigrams/
# vi create_db.py
```
copy and paste `create_db.py` script lines

#### create_db.py details
This program will create SQL table using sqlite3 in python. Bigrams in binary format are loaded and split into two unigrams. So creating two columns for each first and second unigram. The third column is their associated count value. So if the bigram is 'Financial Analysis' and count value is '2', it becomes FirstWord = Financial, SecondWord = Analysis and Count = 2. As we're inserting values to the `bigram_counts` table, as long as the bigrams already exists in the table, the count will be aggregated. It takes time to build the SQL table. But by doing so, i.e, aggregating the counts now, it becomes so much faster when you search the query in later step. I also created an index for both first and second word. The idea of creating index is to help search quickly. You can read up about the indexing in SQL table here a lot more.  
https://www.guru99.com/sqlite-view-index-trigger.html

Basically, indexing in SQL is also similar to indexing in books for certain words. Instead of scanning all the words in the book from the beginning to the end, by searching in index in the last part of book can help you quickly localize your search word. However, after several trials and runs, I realized I cannot create index for both first and second unigram because they are not unique. For example, 

| FirstWord | SecondWord | 
|:---------:|:----------:| 
| financial | analysis |  
| financial | capacity |  
| forgery | analysis | 

In this case, FirstWord has duplicate entry on 'financial' and SecondWord has on 'analysis' although each entry considered together with FirstWord and SecondWord are unique in their own way. So I ended up not creating an index. 

In gpfs1 node, run the following script. This will create `gpfs1_bigrams.db` database. Similary, in gpfs2 and gpfs3 node, run the same commands with `gpfs2 34 66` and `gpfs3 67 99` changes respectively. The rest of the directory should be the same. 
```
# chmod 755 create_db.py
# python2 create_db.py /gpfs/gpfsfpo/bigrams/ gpfs1 0 33 /gpfs/gpfsfpo/bigrams/
```
You can still view `gpfs1_bigrams.db`, `gpfs2_bigrams.db`, `gpfs3_bigrams.db` in every node. You might ask what the use of separating databases when we're seeing all databases from every node. The idea is when it comes to running query in each node, imagine if we had created a single solitary `gpfs_bigrams.db` albeit executable in every node, each node will be executing their query on the same database, which is in fact redundant effort. We want every node query to be unique on its own effort in searching in the unscanned database. That's why we created three separate database here. 

If you check after .db creation, each .db has about ~1.7GB, and the total makes up ~ 5.2 GB. If we didn't save in downloaded zip file in binary format, it would take up 160GB. 

```
# ls *.db -altr -h

-rw-r--r-- 1 root root 1.7G Oct  1 03:08 gpfs3_bigrams.db
-rw-r--r-- 1 root root 1.7G Oct  1 03:09 gpfs2_bigrams.db
-rw-r--r-- 1 root root 1.8G Oct  1 03:12 gpfs1_bigrams.db
```

# Setting up Flask in each node 

We like to establish a web-base app by Flask where we can send the query by web approach and execute the database search in each node. 

```
# vi flask_server.py
```
copy and paste the `flask_server.py` script. Due to some libraries usages, you need to install dependencies in every node.  Installing `gevent~=1.2.2` because latest version does not support `wsgi`, and you need to change it to `pywsgi`. 
```
# chmod 755 flask_server.py
# pip2 install flask_restful sqlalchemy 
# pip2 install -U 'gevent~=1.2.2'
```
In gpfs1 node, 
```
# python2 flask_server.py 198.23.88.163 gpfs1_bigrams.db
```
Similarly in gpfs2 node, 
```
# python2 flask_server.py 198.23.88.166 gpfs2_bigrams.db
```
In gpfs3 node,
```
# python2 flask_server.py 198.23.88.162 gpfs3_bigrams.db
```
Note  
When you execute flask_server.py and it the IP and port is being used, you can kill the program. It could be due to prior run and you did not shut down the program completely. First we will check which program is using the port. Then kill the program by `<PID>`. 
```
# lsof -i :5000

COMMAND  PID USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
python2 1358 root    6u  IPv4 313630      0t0  TCP a3.58.17c6.ip4.static.sl-reverse.com:5000 (LISTEN)
```
You can also check which particular job is running by `jobs`. Although this wouldn't tell you PID, but it's good to know. 
```
# jobs

[1]+  Running                 python2 flask_server.py 198.23.88.163 gpfs1_bigrams.db &
```
To kill the program 
```
# kill -9 <PID>
```

# Running Mumbler

```
# python2 mumbler.py science 5
```






