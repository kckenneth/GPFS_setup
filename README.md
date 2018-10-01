This is a step by step instructions on how to set up GPFS (General Parallel File System) in virtual servers at Softlayer. 

# Softlayer
Softlayer is a cloud service provider that is now under IBM acquisition. You can setup virtual servers at the Softlayer Cloud, privision as many as you want, customize the server specification, create a cluster, submit your job, tear down the server, etc etc. 

# GPFS
GPFS is a filesystem that require license fee. In contrast, HDFS was developed to counter GPFS and it is an opensource. There are pros and cons in both file system. Here we will explore how to set up GPFS in your virutal servers. I detailed how to provision virtual servers in softlayer and setup GPFS here. 
https://github.com/kckenneth/GPFS_setup/blob/master/gpfs_setup.md

# Mumbler
This is a program that will detect the bigrams (two words such as `financial analysis`, `football field`, etc), and will generate how many of user specified bigrams in the repository. We will download the bigram repository made by Google at 2009. This repo consists of all bigrams before 2009. We will create an application that will search all key words user input from the repository. 

We first download the repo into our virtual servers or nodes. We will then create an application that will search the key words in parallel across all the nodes we will provision in the softlayer cloud. 

I detailed how to set up query here.  
https://github.com/kckenneth/GPFS_setup/blob/master/mumbler.md

# Running Mumbler

Running Flask WSGIServer at the Virtual Servers
For gpfs1
```
$ ssh root@198.23.88.163
# cd /gpfs/gpfsfpo/bigrams
# python2 flask_server.py 198.23.88.163 gpfs1_bigrams.db
```
For gpfs2
```
$ ssh root@198.23.88.163
# cd /gpfs/gpfsfpo/bigrams
# python2 flask_server.py 198.23.88.166 gpfs2_bigrams.db
```
For gpfs3
```
$ ssh root@198.23.88.163
# cd /gpfs/gpfsfpo/bigrams
# python2 flask_server.py 198.23.88.162 gpfs3_bigrams.db
```

Running Mumbler  
This will take a few seconds. 
```
$ ssh root@19823.88.163
# cd /gpfs/gpfsfpo/bigrams/
# python2 mumbler.py financial 5
```
This is the output from 'financial 5' run. 
```
This is the query word ...financial statements ) or indicate
```
If you want to see more of the bigrams, remove the pound sign in `mumbler.py` script in line `79`. If you open the bigram outputs, this will look like this. 
```
item {u'Count': 1221, u'SecondWord': u"'", u'FirstWord': u'financial'}
item {u'Count': 3500, u'SecondWord': u')', u'FirstWord': u'financial'}
item {u'Count': 587, u'SecondWord': u'*', u'FirstWord': u'financial'}
item {u'Count': 47299, u'SecondWord': u'-', u'FirstWord': u'financial'}
item {u'Count': 70147, u'SecondWord': u'.', u'FirstWord': u'financial'}
item {u'Count': 271, u'SecondWord': u'/', u'FirstWord': u'financial'}
item {u'Count': 108, u'SecondWord': u'0', u'FirstWord': u'financial'}
```





