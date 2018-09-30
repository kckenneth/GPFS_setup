|Title |  GPFS Installation |
|-----------|----------------------------------|
|Author | Kenneth Chen |
|Utility | IBM, Softlayer, GPFS |
|Date | 9/10/2018 |

# Week4
# GPFS Setup

### I. Keygen generation to setup ssh key pairs later on virtual servers

In your local host terminal (laptop),
```
$ ssh-keygen -f ~/.ssh/w251 -b 2048 -t rsa 
```

Add your public key to your softlayer account.  
`--note` flag is for softlayer account.  
`w251key` the identifier after that is for later use when we communicate with the virtual servers we will provision later on.  
You don't need to privision vs to add ssh key to your softlayer account. 
```
$ slcli sshkey add -f ~/.ssh/w251.pub --note 'added during HW2' w251key

SSH key added: 49:aa:25:77:c3:b9:32:f5:30:0a:0a:f0:d3:94:09:d0
```   

### II. Provision four vs 
##### This step is being done in local host, laptop

A. Get three virtual servers provisioned, 2 vCPUs, 4G RAM, UBUNTU_16_64, two local disks 25G each, in San Jose. Make sure you attach a keypair. Pick intuitive names such as gpfs1, gpfs2, gpfs3. Note their internal ip addresses.

You can first test run the virtual server by using the flag `--test`. It will show you how much it will charge for each parameters. If you need help with the flag, you can call `slcli vs create --help`. Since I'm creating two local disks, I used `--disk=25` twice because the flag allows multiple occurence. 

Test running
```
$ slcli vs create -d hou02 --os UBUNTU_LATEST_64 --cpu 1 --memory 1024 --hostname saltmaster --domain someplace.net --disk=25 --disk=25 --test  

:................................................................:......:
:                                                           Item : cost :
:................................................................:......:
:                                     1 x 2.0 GHz or higher Core : 0.02 :
:                                                           1 GB : 0.01 :
: Ubuntu Linux 18.04 LTS Bionic Beaver Minimal Install (64 bit)  : 0.00 :
:                                                  25 GB (LOCAL) : 0.00 :
:                                                  25 GB (LOCAL) : 0.00 :
:                                        Reboot / Remote Console : 0.00 :
:                      100 Mbps Public & Private Network Uplinks : 0.00 :
:                                       0 GB Bandwidth Allotment : 0.00 :
:                                                   1 IP Address : 0.00 :
:                                                      Host Ping : 0.00 :
:                                               Email and Ticket : 0.00 :
:                                         Automated Notification : 0.00 :
:          Unlimited SSL VPN Users & 1 PPTP VPN User per account : 0.00 :
:                    Nessus Vulnerability Assessment & Reporting : 0.00 :
:                                              Total hourly cost : 0.04 :
:................................................................:......:
```

I will provision 4 virtual servers. You can also see the flags in short form and long form. Note the hostname for three vs. Also make sure you'd use the identifer for `--key` flag. The identifier you created when you generated keygen on earlier step. 

```
$ slcli vs create -d hou02 --os UBUNTU_LATEST_64 --cpu 1 --memory 1024 --hostname saltmaster --domain someplace.net --key w251key
$ slcli vs create --datacenter=sjc01 --hostname=gpfs1 --domain=softlayer.com --billing=hourly --cpu=2 --memory=4096 --os=UBUNTU_16_64 --disk=25 --disk=25 --key w251key
$ slcli vs create --datacenter=sjc01 --hostname=gpfs2 --domain=softlayer.com --billing=hourly --cpu=2 --memory=4096 --os=UBUNTU_16_64 --disk=25 --disk=25 --key w251key
$ slcli vs create --datacenter=sjc01 --hostname=gpfs3 --domain=softlayer.com --billing=hourly --cpu=2 --memory=4096 --os=UBUNTU_16_64 --disk=25 --disk=25  --key w251key
```
Checking all virtual servers provisioned
```
$ slcli vs list 
:..........:............:................:...............:............:........:
:    id    :  hostname  :   primary_ip   :   backend_ip  : datacenter : action :
:..........:............:................:...............:............:........:
: 62391253 :   gpfs1    : 198.23.88.163  :  10.91.105.3  :   sjc01    :   -    :
: 62391273 :   gpfs2    : 198.23.88.166  :  10.91.105.14 :   sjc01    :   -    :
: 62391283 :   gpfs3    : 198.23.88.162  :  10.91.105.16 :   sjc01    :   -    :
: 62391225 : saltmaster : 184.173.26.246 : 10.77.200.159 :   hou02    :   -    :
:..........:............:................:...............:............:........:
```
### III. Setting up keygen in 3 nodes 
[This step I found is optional, the keygen in the node is much more useful. However if you generate with id_rsa, it might work. Since I already have id_rsa (private key) in my laptop, I don't want to mess up with the existing ones.]  

Since we already provisioned 3 virtual servers or nodes with `--key w251` key, the w251.pub public key is automatically added to each node ~/.ssh/authorized_keys file during privisioning. We also like them to communicate each other without requiring any passwords. So we need to add the private key (i.e., the key in our local host, laptop) to each of the three ndoes. The saltmaster node I created just in case, I need to communicate those 3 nodes from other servers.  
`-i` flag is to specify the private key directory. Since we're connecting to the server, we need password. Instead of typing the password, just providing the key will bypass the password step. We're also directing the private key to be copied into virtual server .ssh directory.

```
$ scp -i ~/.ssh/w251 ~/.ssh/w251 root@198.23.88.166:/root/.ssh/
```
If you come across a warning message, go to 
```
$ cd ~/.ssh
$ vi known_hosts
```
delete ECDSA key  

Logging into each node separately, while in the node following three commands will be executed. It's better to open three separate terminals. There is no default .bash_profile and nodefile. So calling vi will automatically create those file. Every time when you call `vi`, type in the script after the respective commands. In nodefile, depending on the node you're in, you change the `:quorum:` position accordingly. 

```
$ ssh -i ~/.ssh/w251 root@198.23.88.166
```
In the node
```
# vi /root/.bash_profile
export PATH=$PATH:/usr/lpp/mmfs/bin
```
export path is for `mmcrcluster` call in later step. You can also use `PATH=/usr/lpp/mmfs/bin:$PATH`. Since bash_profile is readonly file, you need to source it so that it can be activated. 
```
$ source .bash_profile
```

```
# vi /root/nodefile
gpfs1:quorum:
gpfs2::
gpfs3::

# vi /etc/hosts
127.0.0.1 		   localhost.localdomain localhost
10.91.105.14   gpfs1
10.91.105.3    gpfs2
10.91.105.16   gpfs3
```

You can delete the rest of the DNS in /etc/hosts. 


#### Checking nodes communication 

Now we're going to check all nodes communication without password. So the idea is create the ssh-keygen in one node, which will generate private and public key. Make sure you'd use id_rsa. Not other customized names which doesn't work as expected. 

```
# ssh-keygen -f ~/.ssh/id_rsa -b 2048 -t rsa 
# cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys 
# chmod 600 ~/.ssh/authorized_keys
```

You now copy all files in the `.ssh` directory:  
- authorized_keys  
- id_rsa  
- id_rsa.pub  
to all nodes in the cluster. We have 3 nodes set up in our cluster. So we need to copy all files into the other 2 nodes. 

```
# scp ~/.ssh/* root@198.23.88.166:/root/.ssh/
# scp ~/.ssh/* root@198.23.88.162:/root/.ssh/
```
You open 3 individual terminals. In each terminal, ssh into individual nodes and check if those scp works from gpfs1 node. After all done, try this from each node (each terminal). You'll be sshing from gpfs1 to gpfs1. It doesn't matter. We want to add the information into known_hosts. You'll do those in other two terminals as well. 
```
# ssh gpfs1
yes
exit
# ssh gpfs2
yes
exit
# ssh gpfs3
yes 
exit
```
After you're done, make sure they work. Now in GPFS1 node (terminal), 
```
# vi test.sh
```
Copy the following script
```
#!/bin/bash

# Edit node list
nodes="gpfs1 gpfs2 gpfs3"

# Test ssh configuration
for i in $nodes
do for j in $nodes
 do echo -n "Testing ${i} to ${j}: "
 ssh  ${i} "ssh ${j} date"
 done
done
```
run the script. If all nodes communicate without password (In order for GPFS to work, each node must communicate passwordless), you'd see your script works. If nodes communication fails, you'd see some errors here. 
```
# ./test.sh
root@gpfs1:~# ./test.sh
Testing gpfs1 to gpfs1: Thu Sep 27 23:49:24 UTC 2018
Testing gpfs1 to gpfs2: Thu Sep 27 23:49:24 UTC 2018
Testing gpfs1 to gpfs3: Thu Sep 27 23:49:24 UTC 2018
Testing gpfs2 to gpfs1: Thu Sep 27 23:49:25 UTC 2018
Testing gpfs2 to gpfs2: Thu Sep 27 23:49:25 UTC 2018
Testing gpfs2 to gpfs3: Thu Sep 27 23:49:26 UTC 2018
Testing gpfs3 to gpfs1: Thu Sep 27 23:49:26 UTC 2018
Testing gpfs3 to gpfs2: Thu Sep 27 23:49:27 UTC 2018
Testing gpfs3 to gpfs3: Thu Sep 27 23:49:27 UTC 2018
```

### IV. Installing GPFS in each node

Download GPFS tar
```
# apt-get update
# apt-get install ksh binutils libaio1 g++ make m4
# curl -O http://1D7C9.http.dal05.cdn.softlayer.net/icp-artifacts/Spectrum_Scale_ADV_501_x86_64_LNX.tar
# tar -xvf Spectrum_Scale_ADV_501_x86_64_LNX.tar
```

Then install GPFS with:

```
# ./Spectrum_Scale_Advanced-5.0.1.0-x86_64-Linux-install --silent
# cd /usr/lpp/mmfs/5.0.1.0/gpfs_debs
# dpkg -i *.deb
# /usr/lpp/mmfs/bin/mmbuildgpl
```
The first command is agreeing the license agreement. The `--silent` option to accept the license agreement automatically. If installing all .deb doesn't work, 
```
# dpkg -i gpfs.base*deb gpfs.gpl*deb gpfs.license*.deb gpfs.gskit*deb gpfs.msg*deb gpfs.ext*deb gpfs.compression*deb gpfs.adv*deb gpfs.crypto*deb
# /usr/lpp/mmfs/bin/mmbuildgpl
```
### V. Creating Cluster in One Node (GPFS1)

```
# mmcrcluster -C kenneth -p gpfs1 -s gpfs2 -R /usr/bin/scp -r /usr/bin/ssh -N /root/nodefile
```
You will see this message
```
mmcrcluster: Performing preliminary node verification ...
mmcrcluster: Processing quorum and other critical nodes ...
mmcrcluster: Processing the rest of the nodes ...
mmcrcluster: Finalizing the cluster data structures ...
mmcrcluster: Command successfully completed
mmcrcluster: Warning: Not all nodes have proper GPFS license designations.
    Use the mmchlicense command to designate licenses as needed.
mmcrcluster: Propagating the cluster configuration data to all
  affected nodes.  This is an asynchronous process.
```

To accept the license in all nodes
```
# mmchlicense server -N all
```

To start GPFS 
```
# mmstartup -a

Fri Sep 28 00:36:46 UTC 2018: mmstartup: Starting GPFS ...
```
Note  
If you ever need to shut down GPFS, do so by
```
# mmshutdown -a
```

To check the status of GPFS
```
# mmgetstate -a

 Node number  Node name        GPFS state  
-------------------------------------------
       1      gpfs1            arbitrating
       2      gpfs2            arbitrating
       3      gpfs3            arbitrating
```
Wait a few seconds, and try again, you'd see all nodes are active in GPFS
```
 Node number  Node name        GPFS state  
-------------------------------------------
       1      gpfs1            active
       2      gpfs2            active
       3      gpfs3            active
```
NOTE  
Although you launched GPFS from one node, you can check in other nodes after launch. GPFS launch and installation is different. You need to install GPFS in every node individually. However you can launch GPFS from one node. If there's an error, you can check at `/var/adm/ras/mmfs.log.latest`.

### To lookup GPFS details
This will show you even if your GPFS are down. Make sure you'd check `mmgetstate -a`. 
```
# mmlscluster

GPFS cluster information
========================
  GPFS cluster name:         kenneth.gpfs1
  GPFS cluster id:           10445230950671284009
  GPFS UID domain:           kenneth.gpfs1
  Remote shell command:      /usr/bin/ssh
  Remote file copy command:  /usr/bin/scp
  Repository type:           CCR

 Node  Daemon node name  IP address    Admin node name  Designation
--------------------------------------------------------------------
   1   gpfs1             10.91.105.3   gpfs1            quorum
   2   gpfs2             10.91.105.14  gpfs2            
   3   gpfs3             10.91.105.16  gpfs3  
```

### Check the mounted disk

```
# fdisk -l | grep Disk | grep bytes

Disk /dev/xvdc: 25 GiB, 26843545600 bytes, 52428800 sectors
Disk /dev/xvda: 25 GiB, 26843701248 bytes, 52429104 sectors
Disk /dev/xvdh: 64 MiB, 67125248 bytes, 131104 sectors
Disk /dev/xvdb: 2 GiB, 2147483648 bytes, 4194304 sectors
```
### To check the mounted directory

```
# mount | grep ' \/ '

/dev/xvda2 on / type ext4 (rw,relatime,data=ordered)
```
Note  
This could mean (I'm still learning), the OS is installed in `xvda` partition 2. So we rather not touch on that disk. We will use the other disk. If you remember, we provisioned two local disks in the beginning. So the other disk would be `xvdc`. So we will use the other disk.  

```
# vi /root/diskfile.fpo
```
Copy the following lines
```
%pool:
pool=system
allowWriteAffinity=yes
writeAffinityDepth=1

%nsd:
device=/dev/xvdc
servers=gpfs1
usage=dataAndMetadata
pool=system
failureGroup=1

%nsd:
device=/dev/xvdc
servers=gpfs2
usage=dataAndMetadata
pool=system
failureGroup=2

%nsd:
device=/dev/xvdc
servers=gpfs3
usage=dataAndMetadata
pool=system
failureGroup=3
```

Setup the disk in all nodes
```
mmcrnsd -F /root/diskfile.fpo
```

Check if it's already setup
```
mmcrnsd -m

 Disk name    NSD volume ID      Device         Node name                Remarks       
---------------------------------------------------------------------------------------
 gpfs1nsd     0A5B69035BAD7D63   /dev/xvdc      gpfs1                    server node
 gpfs2nsd     7F0001015BAD7D64   /dev/xvdc      gpfs2                    server node
 gpfs3nsd     7F0001015BAD7D67   /dev/xvdc      gpfs3                    server node
```

### Create a file system 
This is what I think happening. First we launched 3 virtual servers. We then installed GPFS in each of those nodes. We made sure they can communicate without passwords. Since we want to communicate with those nodes at ease. Also the nodes can also communicate with each other at ease. Basically you're combining all nodes so that you increase your capacity. Conceptually every node is like state in the US. But by combining all states (nodes), you have more capacity (federal), and more resources. Of course you'd need an elected leader, which is a quorum manager. Here GPFS is our quorum manager. 

Now since we have established all disks from every node, we want them to communicate efficiently. Basically if you have an address on your disk, you don't want them to be the same as in other nodes. Otherwise, it would be a disaster. So you'll need to streamline all address across all the nodes you created. So when you create a file system, this will create `inode` system that will become a backbone of GPFS across all nodes in your cluster. 

Replication 1 means the data won't be replicated. If 2, the data will be replicated twice. 

```
mmcrfs gpfsfpo -F /root/diskfile.fpo -A yes -Q no -r 1 -R 1

...
Clearing Inode Allocation Map
Clearing Block Allocation Map
Formatting Allocation Map for storage pool system
Completed creation of file system /dev/gpfsfpo.
```

Check the filesystem
```
mmlsfs all
```

Mount the filesystem in all nodes. Before we mount, you can check before and after filesystem. So first check how the filesystem looks like. 
```
# df -h

Filesystem      Size  Used Avail Use% Mounted on
udev            2.0G     0  2.0G   0% /dev
tmpfs           395M  5.6M  389M   2% /run
/dev/xvda2       24G  3.9G   21G  17% /
tmpfs           2.0G     0  2.0G   0% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
tmpfs           2.0G     0  2.0G   0% /sys/fs/cgroup
/dev/xvda1      240M   36M  192M  16% /boot
tmpfs           396M     0  396M   0% /run/user/0
```

Mount the filesystem in all nodes 
```
# mmmount all -a
```
Check the filesystem
```
# df -h 

Filesystem      Size  Used Avail Use% Mounted on
udev            2.0G     0  2.0G   0% /dev
tmpfs           395M  5.6M  389M   2% /run
/dev/xvda2       24G  3.9G   21G  17% /
tmpfs           2.0G     0  2.0G   0% /dev/shm
tmpfs           5.0M     0  5.0M   0% /run/lock
tmpfs           2.0G     0  2.0G   0% /sys/fs/cgroup
/dev/xvda1      240M   36M  192M  16% /boot
tmpfs           396M     0  396M   0% /run/user/0
gpfsfpo          75G  1.6G   74G   3% /gpfs/gpfsfpo
```

You'd see the `gpfsfpo 75G` after mounting the file system in our cluster. You can also check by 
```
# cd /gpfs/gpfsfpo
# df -h .

Filesystem      Size  Used Avail Use% Mounted on
gpfsfpo          75G  1.6G   74G   3% /gpfs/gpfsfpo
```

Check you create a file and check across all nodes in the cluster
```
# touch aa
# ls -l
total 0
# ssh gpfs2 'ls -l /gpfs/gpfsfpo'
total 0
# ssh gpfs3 'ls -l /gpfs/gpfsfpo'
total 0
```


# Mumbler 

Download google two-gram 27G data set - English version 20090715 from this repository  
http://storage.googleapis.com/books/ngrams/books/datasetsv2.html

```
# mkdir mumbler
# cd mumbler
# wget http://storage.googleapis.com/books/ngrams/books/googlebooks-eng-all-2gram-20090715-{0..99}.csv.zip
```

