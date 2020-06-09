FILE_HELP = 'the name of the configuration file, leave blank if you' \
       ' wish the program to automatically detect it. (e.g. --file xxx.conf)'
DIR_HELP = 'the dir of configuration files, leave blank if you' \
       ' wish the program to automatically detect it. (e.g. --dir /etc/)'

SUPPORTED_DB = [{
    "name": "redis",
    "custom_args": {"--dir": DIR_HELP},
}, {
    "name": "mongodb",
    "custom_args": {"--file": FILE_HELP},
}, {
    "name": "mysql",
    "custom_args": {
        "--password": "Password of root account []",
        "--username": "Username of root account [root]",
        "--host": "Username of root account [127.0.0.1]",
        "--port": "Port of MySQL server [3306]",
    }
}, {
    "name": "hadoop",
    "custom_args": {"--dir": DIR_HELP},
}]
