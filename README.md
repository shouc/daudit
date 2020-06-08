DAudit
==============

By [Shou C](https://github.com/shouc/)

![Output](examples/output.png)


Installation
-----
```
$ git clone https://github.com/shouc/daudit.git
$ python3 -m pip install -r requirements.txt
```


Usage
-----

You can use the following command to print the help message
```
$ sudo python3 main.py -h
usage: main.py [-h] {redis} ...

This is a tool for detecting configuration issues of Redis, MySQL, etc!

positional arguments:
  {redis,mongodb}  commands
    redis          Check configurations of redis
    mongodb        Check configurations of mongodb


optional arguments:
  -h, --help  show this help message and exit
```


Redis
-----
[Advisory](https://redis.io/topics/security)
```
$ sudo python3 main.py redis -h
usage: main.py redis [-h] [--dir DIR]

optional arguments:
  -h, --help  show this help message and exit
  --dir DIR   the dir of redis configuration files, leave blank if you wish the program to automatically detect the location.
```

An example of checking Redis with configuration file /etc/redis/redis.conf
```
$ # both commands are equivalent
$ sudo python3 main.py redis
$ sudo python3 main.py redis --dir /etc/redis 
INFO Evaluating /etc/redis/redis.conf
INFO Checking exposure...
INFO Redis is only exposed to the intranet
INFO Checking setting of password...
WARNING No password has been set, consider setting 'requirepass [your_password]' in config file
INFO Checking commands...
WARNING Config command is exposed to every user, consider renaming this command
WARNING Flushall command is exposed to every user, consider renaming this command
WARNING Flushdb command is exposed to every user, consider renaming this command
```
Checks:
* exposure
* weak/no password
* command renaming

MongoDB
-----
[Advisory](https://docs.mongodb.com/manual/administration/security-checklist/)

```
$ sudo python3 main.py mongodb -h
usage: main.py mongodb [-h] [--dir DIR] [--file FILE]

optional arguments:
  -h, --help   show this help message and exit
  --dir DIR    the dir of configuration files, leave blank if you wish the program to automatically detect it. (e.g. --dir /etc/)
  --file FILE  the name of the configuration file, leave blank if you wish the program to automatically detect it. (e.g. --file xxx.conf)
```

An example of checking MongoDB with configuration file /etc/mongodb.conf
```
$ # both commands are equivalent
$ sudo python3 main.py mongodb
$ sudo python3 main.py mongodb --dir '/etc' --file mongodb.conf 
INFO Evaluating /etc/mongodb.conf
DEBUG Using MongoDB <= 2.4 conf file format (INI)
INFO Checking exposure...
DEBUG The instance is exposed on internal IP: 127.0.0.1
INFO Checking setting of authentication...
WARNING No authorization is enabled in configuration file. Consider set 'auth = true'
INFO Checking code execution issue...
WARNING JS code execution is enabled in configuration file. Consider set 'noscripting = true'
WARNING Object check is not enabled in configuration file. Consider set 'objcheck = true'
```
Checks:
* exposure
* authorization
* js code execution
* object check
