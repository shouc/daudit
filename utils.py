import re
import ipaddress
import platform
import subprocess
import logs
import os
import sys

password_regex = re.compile('^.*(?=.{6,16})(?=.*\d)(?=.*[A-Z])(?=.*[a-z]{2,})(?=.*[!@#$%^&*?\(\)]).*$')


def check_pwd(pwd: str):
    if password_regex.match(pwd):
        return 1
    return 0


def is_ip_internal(ip: str):
    try:
        return ipaddress.ip_address(ip.split()[0]).is_private
    except ValueError:
        logs.DEBUG(f"Not a correct IP: {ip}")
        return False


def os_name():
    return platform.system()


def execute_command(x: [str]):
    return subprocess.check_output(x).replace(b'\n', b'')


def whereis(name: str):
    if os_name() == "Windows":
        return []
    try:
        output = execute_command(["whereis", name])
    except FileNotFoundError:
        return []
    return [str(x) for x in output.split()[1:]]


def exists_file(path, file):
    if path[-1] == '/':
        path = path[:-1]
    if file[0] == '/':
        file = file[1:]
    return os.path.exists(f"{path}/{file}")


def abs_path_from_args(args):
    path = args.dir
    abs_path = None
    if path is not None:
        if not os.path.exists(path):
            logs.ERROR("'%s' is not a dir!" % path)
            sys.exit(0)
        abs_path = os.path.abspath(path)
    return abs_path


def get_ini_string(content, opt):
    re_obj = re.compile(f"{opt} *= *(.+)")
    matches = re_obj.findall(content)
    if len(matches) == 0:
        return False
    return matches[-1]


def get_ini_bool(content, opt):
    result = get_ini_string(content, opt)
    return result in [
        '1', 'yes', 'true', 'on'
    ]


def get_yaml(obj, opt_str):
    result = obj
    opts = opt_str.split(".")
    try:
        for opt in opts:
            result = result[opt]
        return result
    except KeyError:
        return None