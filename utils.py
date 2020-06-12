# Copyright: [DAudit] - See LICENSE for details.
# Authors: Shou Chaofan (@shouc),
import re
import ipaddress
import platform
import subprocess
import logs
import os
import sys
import socket

password_regex = re.compile('^.*(?=.{6,16})(?=.*\d)(?=.*[A-Z])(?=.*[a-z]{2,})(?=.*[!@#$%^&*?\(\)]).*$')


def check_pwd(pwd: str):
    if password_regex.match(pwd):
        return 1
    return 0


def check_normal_pwd(pwd: str):
    return len(pwd) > 16


def file_from_args(args):
    file = args.file
    if file is None:
        return None
    return file


def is_internal(x: str):
    x = x.replace(" ", "")
    is_ip_re = re.compile(r"((^\s*((([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}"
                          r"|2[0-4][0-9]|25[0-5]))\s*$)|(^\s*((([0-9A-Fa-f]{1,4}:){7}([0-9A-Fa-f]{1,4}|:))|"
                          r"(([0-9A-Fa-f]{1,4}:){6}(:[0-9A-Fa-f]{1,4}|((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
                          r"(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|(([0-9A-Fa-f]{1,4}:){5}"
                          r"(((:[0-9A-Fa-f]{1,4})"
                          r"{1,2})|:((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3})|:))|"
                          r"(([0-9A-Fa-f]{1,4}:){4}(((:[0-9A-Fa-f]{1,4}){1,3})|((:[0-9A-Fa-f]{1,4})?:"
                          r"((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|"
                          r"(([0-9A-Fa-f]{1,4}:){3}(((:[0-9A-Fa-f]{1,4}){1,4})|((:[0-9A-Fa-f]{1,4}){0,2}:"
                          r"((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|"
                          r"(([0-9A-Fa-f]{1,4}:){2}(((:[0-9A-Fa-f]{1,4}){1,5})|((:[0-9A-Fa-f]{1,4}){0,3}:"
                          r"((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))|"
                          r"(([0-9A-Fa-f]{1,4}:){1}(((:[0-9A-Fa-f]{1,4}){1,6})|((:[0-9A-Fa-f]{1,4}){0,4}:"
                          r"((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:))"
                          r"|(:(((:[0-9A-Fa-f]{1,4}){1,7})|((:[0-9A-Fa-f]{1,4}){0,5}:"
                          r"((25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)){3}))|:)))"
                          r"(%.+)?\s*$))")
    is_host_re = re.compile("[a-zA-Z0-9.]+")
    if x == "0.0.0.0" or x == "::":
        return False
    if is_ip_re.match(x) is not None:
        return ipaddress.ip_address(x).is_private
    elif is_host_re.match(x) is not None:
        try:
            ip = socket.gethostbyname(x)
            return ipaddress.ip_address(ip).is_private
        except socket.gaierror:
            logs.ERROR(f"Unknown host: {x}")
    elif x == "%" or x == "*":
        return False
    else:
        logs.ERROR(f"Unknown host: {x}")


def ask(c):
    logs.INFO(c)
    v = input("Type Y/y to perform this action and anything else to skip [Y]")
    if v == "Y" or v == "y" or v == "":
        return True
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


def get_ini_string(content, opt, default=""):
    re_obj = re.compile(f" *(#|) *([a-zA-Z0-9-_]*) *{opt} *= *(.+)")
    result = []
    matches = re_obj.findall(content)
    for i in matches:
        if not i[0] == "#" and i[1] == '':
            result.append(i[2])
    if len(result) == 0:
        return default
    return result[-1]


def get_ini_bool(content, opt, default="false"):
    result = get_ini_string(content, opt, default=default)
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


def get_yaml_string(obj, opt_str, default=""):
    return get_yaml(obj, opt_str) or default


def get_yaml_bool(obj, opt_str, default=False):
    result = get_yaml(obj, opt_str)
    if result is None:
        return default
    return result or result == "enabled"


def split_ip(s):
    return [
        x.replace(" ", "") for x in s.split(",")
    ]


def which_exist(path, files):
    result = []
    for i in files:
        if exists_file(path, i):
            result.append(i)
    return result


def get_weak_passwords():
    with open("external/weak_passwords.txt") as f:
        result = [x.replace("\n", "") for x in f.readlines()]
    return result


def get_item_from_obj(obj, key, default=""):
    try:
        return obj[key]
    except KeyError:
        return default
