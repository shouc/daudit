import interface
import logs
import re
import utils
import os
import yaml
import yaml.parser


class MongoDB(interface.Interface):
    def __init__(self, conf_path=None):
        super().__init__()
        self.conf_path = conf_path
        if not conf_path:
            self.conf_path = self.get_paths("mongodb.conf")
        self.conf_file = os.path.join(self.conf_path, 'mongodb.conf')
        logs.INFO(f"Evaluating {self.conf_file}")
        self.conf_content = None
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
                self.conf_content = yaml.load(fp)
                logs.DEBUG("Using MongoDB > 2.4, with conf file in YAML")
                return True
        except yaml.parser.ParserError:
            try:
                with open(self.conf_file) as fp:
                    self.conf_content = fp.read()
            except FileNotFoundError:
                logs.ERROR("Failed to open MongoDB conf file")
            logs.DEBUG("Using MongoDB <= 2.4")
            return False
        except FileNotFoundError:
            logs.ERROR("Failed to open MongoDB conf file")

    def is_auth_0(self):
        return utils.get_ini_bool(self.conf_content, 'auth')

    def get_bind_ip_0(self):
        return utils.get_ini_string(self.conf_content, 'bind_ip')

    def is_support_scripting_0(self):
        return utils.get_ini_bool(self.conf_content, 'noscripting')

    def is_obj_check_0(self):
        return utils.get_ini_bool(self.conf_content, 'objcheck')

    def is_auth_1(self):


    def check_conf(self):
        logs.INFO("Checking exposure...")
        self.check_exposure()
        logs.INFO("Checking setting of password...")
        self.check_password_setting()
        logs.INFO("Checking commands...")
        self.check_command()
