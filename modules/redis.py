# Copyright: [DAudit] - See LICENSE for details.
# Authors: Shou Chaofan (@shouc),
import interface
import logs
import re
import utils
import os


class Redis(interface.Interface):
    def __init__(self, dir=None):
        super().__init__()
        self.conf_path = dir
        if not dir:
            self.conf_path = self.get_paths(expected_file="redis.conf")
        self.conf_file = os.path.join(self.conf_path, 'redis.conf')
        logs.INFO(f"Evaluating {self.conf_file}")
        self.conf_content = None
        self.read_content()
        self.combine_include()

    def enumerate_path(self):
        return list({
            *utils.whereis("redis"),
            "/etc/redis/", # apt & yum
            "/usr/local/etc/", # homebrew
            "/etc/", # yum
        })

    def read_content(self):
        try:
            fp = open(self.conf_file)
            self.conf_content = fp.read()
            fp.close()
        except FileNotFoundError:
            logs.ERROR("Redis Error")

    def ip_extraction(self):
        ip_re = re.compile("((# |)bind (.+?)\.(.+?)\.(.+?)\.(.+))")
        temp_result = []
        for i in ip_re.findall(self.conf_content):
            if i[0][0] != "#":
                temp_result.append(i[0].replace("bind ", ""))
        return temp_result

    def password_extraction(self):
        password_re = re.compile("((# |)requirepass (.+))")
        temp_result = []
        for i in password_re.findall(self.conf_content):
            if i[0][0] != "#":
                temp_result.append(i[0].replace("requirepass ", ""))
        return temp_result

    def config_extraction(self):
        config_re = re.compile("((# |)rename-command (.+) (.+))")
        temp_result = {}
        for i in config_re.findall(self.conf_content):
            if i[0][0] != "#":
                temp_result[i[2].lower()] = i[3]
        return temp_result

    def add_file(self, file_path):
        try:
            fp = open(file_path)
            self.conf_content += "\n"
            self.conf_content += fp.read()
            fp.close()
        except FileNotFoundError:
            logs.WARN("Include file %s cannot be found" % file_path)

    def combine_include(self):
        include_re = re.compile("((# |)include (.+).conf)")
        for i in include_re.findall(self.conf_content):
            try:
                if i[0][0] != "#":
                    self.add_file(i[2])
            except IndexError:
                pass

    def check_exposure(self):
        try:
            ips = self.ip_extraction()[0].split()
            for ip in ips:
                if not utils.is_internal(ip):
                    logs.ISSUE(f"Redis is set to be exposed to the internet ({ip}).")
                    logs.RECOMMENDATION("bind [internal_ip]")
                else:
                    logs.DEBUG(f"Redis is only exposed to internal network ({ip})")
        except IndexError:
            logs.ERROR("No IP is extracted from config file. Is the config file correct?")

    def check_password_setting(self):
        if not len(self.password_extraction()):
            logs.ISSUE("No password has been set. ")
            logs.RECOMMENDATION("requirepass [your_password]")

            return 0
        password = self.password_extraction()[0]
        if utils.check_pwd(password):
            logs.DEBUG('Password is strong')
        else:
            logs.ISSUE('Password could be easily guessed.')
            logs.RECOMMENDATION("requirepass [stronger passwor]")

    def check_command(self):
        rename_settings = self.config_extraction()
        for i in ["config", "debug", "shutdown", "flushdb", "flushall", "eval"]:
            if i not in rename_settings:
                logs.ISSUE(f"{i} command is exposed to every user.")
                logs.RECOMMENDATION(f"rename-command {i} [UUID]")
            else:
                if utils.check_normal_pwd(rename_settings[i]) or rename_settings[i] == '""':
                    logs.DEBUG('Config command is protected by random string or disabled')
                else:
                    logs.ISSUE(f'{i} command\' new name could be easily guessed. ')
                    logs.RECOMMENDATION(f"rename-command {i} [UUID]")

    def check_conf(self):
        logs.INFO("Checking exposure...")
        self.check_exposure()
        logs.INFO("Checking setting of password...")
        self.check_password_setting()
        logs.INFO("Checking commands...")
        self.check_command()
