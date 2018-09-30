# Mumbler 

Since we will be using python, we need to install the program and its dependencies in every node. I installed dependencies as necessary. These commands were executed in every node. 
```
# apt install python3
# apt install python3-pip
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

This is the actual step in preprocessing the bigram dataset. Do this in all 3 nodes: gpfs1, gpfs2 and gpfs3. 
```
# mkdir -p /gpfs/gpfsfpo/bigrams
# cd /gpfs/gpfsfpo/bigrams/
# vi downzip_pp.py
```
Note  
In downzip_pp.py (Download Zip file and PreProcess), in order to run from CLI, you might want to check the python path and update in shebang. 
```
# which python3
/usr/bin/python3
```

