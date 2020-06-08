import os
import logs
import argparse


def __redis(args):
    path = args.dir
    abs_path = None
    if path is not None:
        if not os.path.exists(path):
            logs.ERROR("'%s' is not a dir!" % path)
            return
        abs_path = os.path.abspath(path)
    from modules.redis import Redis
    r = Redis(conf_path=abs_path)
    r.check_conf()


DIR_HELP = 'the dir of redis configuration files, leave blank if you' \
       ' wish the program to automatically detect the location.'

def main():
    parser = argparse.ArgumentParser(
        description="This is a tool for detecting configuration issues of Redis, MySQL, etc!")
    subparsers = parser.add_subparsers(help='commands')

    # Redis
    setting_check_parser = subparsers.add_parser('redis', help='Check configurations of redis')
    setting_check_parser.add_argument('--dir', dest="dir", action='store',
                                      help=DIR_HELP)
    setting_check_parser.set_defaults(func=__redis)
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()