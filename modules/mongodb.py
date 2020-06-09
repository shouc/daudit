import interface
import logs
import re
import utils
import os
import yaml
import yaml.parser
import sys


class Mongodb(interface.Interface):
    POSSIBLE_CONF_FILENAMES = [
        "mongod.conf",
        "mongod.cfg",
        "mongodb.conf"
    ]

    def __init__(self, dir=None, file=None):
        super().__init__()
        self.conf_path = dir
        self.conf_file = file
        if not dir:
            self.conf_path = self.get_paths(files_appear=self.POSSIBLE_CONF_FILENAMES)
        if not self.conf_file:
            fs = utils.which_exist(self.conf_path, self.POSSIBLE_CONF_FILENAMES)
            if len(fs) == 0:
                logs.ERROR("Cannot find the configuration file in given configuration path, "
                           "please specify (e.g. --file=mongod.conf!)")
                sys.exit(0)
            if len(fs) > 1:
                logs.ERROR("Multiple configuration file in configuration path found (listed below), "
                           "please specify  (e.g. --file=mongod.conf)")
                sys.exit(0)
            self.conf_file = fs[0]
        self.conf_file = os.path.join(self.conf_path, self.conf_file)
        logs.INFO(f"Evaluating {self.conf_file}")
        self.conf_content = None
        self.is_ini = False
        self.read_content()

    def enumerate_path(self):
        return list({
            *utils.whereis("mongodb"),
            "/usr/local/etc/", # homebrew
            "/etc/", # apt & yum
        })

    def read_content(self):
        try:
            with open(self.conf_file) as fp:
                self.conf_content = yaml.load(fp, Loader=yaml.FullLoader)
                logs.DEBUG("Using MongoDB > 2.4 conf file format (YAML)")
                return True
        except yaml.parser.ParserError:
            try:
                with open(self.conf_file) as fp:
                    self.conf_content = fp.read()
            except FileNotFoundError:
                logs.ERROR("Failed to open MongoDB conf file")
            self.is_ini = True
            logs.DEBUG("Using MongoDB <= 2.4 conf file format (INI)")
            return False
        except FileNotFoundError:
            logs.ERROR("Failed to open MongoDB conf file")

    def is_auth_0(self):
        return utils.get_ini_bool(self.conf_content, 'auth')

    def get_bind_ip_0(self):
        return utils.split_ip(utils.get_ini_string(self.conf_content, 'bind_ip'))

    def is_no_scripting_0(self):
        return utils.get_ini_bool(self.conf_content, 'noscripting')

    def is_obj_check_0(self):
        return utils.get_ini_bool(self.conf_content, 'objcheck')

    def is_auth_1(self):
        return utils.get_yaml_bool(self.conf_content, 'security.authorization')

    def get_bind_ip_1(self):
        if utils.get_yaml_bool(self.conf_content, "net.bindIpAll"):
            return ["0.0.0.0"]
        return utils.split_ip(utils.get_yaml_string(self.conf_content, "net.bindIp"))

    def is_support_scripting_1(self):
        return utils.get_yaml_bool(self.conf_content, 'security.javascriptEnabled', default=True)

    def is_obj_check_1(self):
        return utils.get_yaml_bool(self.conf_content, 'net.wireObjectCheck')

    def check_conf(self):
        if self.is_ini:
            logs.INFO("Checking exposure...")
            ips = self.get_bind_ip_0()
            if len(ips) == 0:
                logs.ERROR("No IP is extracted from config file. Is the config file correct?")
            for ip in ips:
                if not utils.is_internal(ip):
                    logs.ISSUE(f"The instance is exposed on external IP: {ip}")
                    continue
                logs.DEBUG(f"The instance is only exposed on internal IP: {ip}")
            logs.INFO("Checking setting of authentication...")
            if not self.is_auth_0():
                logs.ISSUE("No authorization is enabled in configuration file. ")
                logs.RECOMMENDATION("auth = true")

            else:
                logs.DEBUG("Authorization is enabled but still remember to set password :)")
            logs.INFO("Checking code execution issue...")
            if not self.is_no_scripting_0():
                logs.ISSUE("JS code execution is enabled in configuration file.")
                logs.RECOMMENDATION("noscripting = true")

            else:
                logs.DEBUG("JS code execution is disabled")
            logs.INFO("Checking object check issue...")
            if not self.is_obj_check_0():
                logs.ISSUE("Object check is not enabled in configuration file.")
                logs.RECOMMENDATION("noscripting = true")
            else:
                logs.DEBUG("Object check is enabled")
        else:
            logs.INFO("Checking exposure...")
            ips = self.get_bind_ip_1()
            if len(ips) == 0:
                logs.ERROR("No IP is extracted from config file. Is the config file correct?")
            for ip in ips:
                if ip == "*" or ip == "0.0.0.0" or ip == "::":
                    logs.ISSUE("The instance is exposed to everyone (0.0.0.0). ")
                    logs.RECOMMENDATION("net.bindIp to internal IPs and net.bindIpAll to false")
                    continue
                if not utils.is_internal(ip):
                    logs.ISSUE(f"The instance is exposed on external IP: {ip}")
                    continue
                logs.INFO(f"The instance is exposed on internal IP: {ip}")
            logs.INFO("Checking setting of authentication...")
            if not self.is_auth_1():
                logs.ISSUE("No authorization is enabled in configuration file. ")
                logs.RECOMMENDATION("security.authorization = true")

            else:
                logs.INFO("Authorization is enabled but still remember to set password :)")
            logs.INFO("Checking code execution issue...")
            if self.is_support_scripting_1():
                logs.ISSUE("JS code execution is enabled in configuration file.")
                logs.RECOMMENDATION("security.javascriptEnabled = false'")
            else:
                logs.DEBUG("JS code execution is disabled")
            logs.INFO("Checking object check issue...")
            if not self.is_obj_check_1():
                logs.ISSUE("Object check is not enabled in configuration file.")
                logs.RECOMMENDATION("net.wireObjectCheck = true")
            else:
                logs.DEBUG("Object check is enabled")
