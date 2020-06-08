Big Data Audit
==============

By [Shou C](https://github.com/shouc/)

![Output](examples/output.png)


Installation
-----
```
git clone https://github.com/shouc/BDA.git
python3 -m pip install -r requirements.txt
```


Usage
-----

You can use the following command to print the help message
```
$ sudo python3 main.py -h
usage: main.py [-h] {redis} ...

This is a tool for detecting configuration issues of Redis, MySQL, etc!

positional arguments:
  {redis}     commands
    redis     Check configurations of redis

optional arguments:
  -h, --help  show this help message and exit
```


Redis
-----
```
$ sudo python3 main.py redis -h
usage: main.py redis [-h] [--dir DIR]

optional arguments:
  -h, --help  show this help message and exit
  --dir DIR   the dir of redis configuration files, leave blank if you wish the program to automatically detect the location.
```

An example of Redis with configuration dir /etc/redis
```
$ # both commands are equivalent
$ sudo python3 main.py redis
$ sudo python3 main.py redis /etc/redis 
[Info]: Checking exposure...
[Pass]: Redis is only accessible on this computer
[Info]: Checking setting of password...
[Pass]: Password is strong
[Info]: Checking commands...
[Pass]: Config command is protected strongly
[Warning]: Flushall command is exposed to every login user, try renaming this command
[Warning]: Flushdb command is exposed to every login user, try renaming this command
```
Checks:
* exposure to internet
* weak/no password
* command renaming
