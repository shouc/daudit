import argparse
import utils
import modules


DIR_HELP = 'the dir of configuration files, leave blank if you' \
       ' wish the program to automatically detect it. (e.g. --dir /etc/)'


def main():
    parser = argparse.ArgumentParser(
        description="This is a tool for detecting configuration issues of Redis, MongoDB, etc!")
    subparsers = parser.add_subparsers(help='commands')
    for i in modules.SUPPORTED_DB:
        name = i["name"]
        custom_args = i["custom_args"]
        fragment_func_args = ""
        for arg in custom_args:
            if arg == "--dir":
                fragment_func_args += "dir=utils.abs_path_from_args(args),"
                continue
            elif arg == "--file":
                fragment_func_args += "file=utils.file_from_args(args),"
                continue
            else:
                arg = arg.replace("--", "")
                fragment_func_args += f"{arg}=args.{arg},"

        exec(f"""def __{name}(args):
    from modules.{name} import {name.capitalize()}
    r = {name.capitalize()}(
        {fragment_func_args}
    )
    r.check_conf()
    """)
        setting_check_parser = subparsers.add_parser(name, help=f'Check configurations of {name}')
        for arg in custom_args:
            setting_check_parser.add_argument(arg, dest=arg.replace("--", ""), action='store',
                                          help=custom_args[arg])
        setting_check_parser.set_defaults(func=eval(f"__{name}"))
    args = parser.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()