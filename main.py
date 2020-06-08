import argparse
import utils


def __redis(args):
    from modules.redis import Redis
    r = Redis(conf_path=utils.abs_path_from_args(args))
    r.check_conf()


DIR_HELP = 'the dir of configuration files, leave blank if you' \
       ' wish the program to automatically detect the location.'
SUPPORTED_DB = ["redis"]


def main():
    parser = argparse.ArgumentParser(
        description="This is a tool for detecting configuration issues of Redis, MySQL, etc!")
    for i in SUPPORTED_DB:
        subparsers = parser.add_subparsers(help='commands')
        setting_check_parser = subparsers.add_parser(i, help=f'Check configurations of {i}')
        setting_check_parser.add_argument('--dir', dest="dir", action='store',
                                          help=DIR_HELP)
        setting_check_parser.set_defaults(func=eval(f"__{i}"))
        args = parser.parse_args()
        args.func(args)


if __name__ == '__main__':
    main()