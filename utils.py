import re
import ipaddress
import platform
import subprocess
import logs

password_regex = re.compile('^.*(?=.{6,16})(?=.*\d)(?=.*[A-Z])(?=.*[a-z]{2,})(?=.*[!@#$%^&*?\(\)]).*$')


def check_pwd(pwd: str):
    if password_regex.match(pwd):
        return 1
    return 0


def is_ip_internal(ip: str):
    try:
        return ipaddress.ip_address(ip).is_private
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
