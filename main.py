import argparse
import utils
import modules


DIR_HELP = 'the dir of configuration files, leave blank if you' \
       ' wish the program to automatically detect it. (e.g. --dir /etc/)'
FILE_HELP = 'the name of the configuration file, leave blank if you' \
       ' wish the program to automatically detect it. (e.g. --file xxx.conf)'


def main():
    parser = argparse.ArgumentParser(
        description="This is a tool for detecting configuration issues of Redis, MongoDB, etc!")
    subparsers = parser.add_subparsers(help='commands')
    for i in modules.SUPPORTED_DB:
        name = i["name"]
        need_file_args = not i["is_conf_file_constant"]
        exec(f"""def __{name}(args):
    from modules.{name} import {name.capitalize()}
    r = {name.capitalize()}(
        conf_path=utils.abs_path_from_args(args),
        {'conf_file=utils.file_from_args(args)' if need_file_args else ''}
    )
    r.check_conf()
    """)
        setting_check_parser = subparsers.add_parser(name, help=f'Check configurations of {name}')
        setting_check_parser.add_argument('--dir', dest="dir", action='store',
                                          help=DIR_HELP)
        if need_file_args:
            setting_check_parser.add_argument('--file', dest="file", action='store',
                                              help=FILE_HELP)
        setting_check_parser.set_defaults(func=eval(f"__{name}"))
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()