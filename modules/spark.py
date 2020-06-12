# Copyright: [DAudit] - See LICENSE for details.
# Authors: Shou Chaofan (@shouc),
import interface
import logs
import utils
import os
import re
import sys


class Spark(interface.Interface):
    def __init__(self, file):
        super().__init__()
        logs.INFO("Assuming no configuration property has been changed by CLI or SparkConf object")
        if file is None:
            conf_path = self.get_paths(expected_file=[
                "spark-defaults.conf",
            ])
            self.file = os.path.join(conf_path, "spark-defaults.conf")
        else:
            self.file = file
        logs.INFO(f"Evaluating file {self.file}")
        self.content = {}
        self.parse_content()

    def parse_content(self):
        try:
            fp = open(self.file)
            for i in fp.readlines():
                kv_temp = re.compile("\s+").split(i)
                if len(kv_temp) == 2:
                    self.content[kv_temp[0]] = kv_temp[1]
            fp.close()
        except FileNotFoundError:
            logs.ERROR("Spark Unknown Issue")
            sys.exit(0)

    def enumerate_path(self):
        return list({
            *utils.whereis("spark"),
            "/local/spark/etc/spark",  # apt,
            "/etc/spark",  # apt
        })

    def check_acl(self):
        if utils.get_item_from_obj(self.content, "spark.acls.enable", default="false") == "false":
            logs.ISSUE("Access control not enabled for web portal")
            logs.RECOMMENDATION("spark.acls.enable = true")
        else:
            logs.DEBUG("Access control is enabled for web portal")

        if utils.get_item_from_obj(self.content, "spark.history.ui.acls.enable", default="false") == "false":
            logs.ISSUE("Access control not enabled for history server")
            logs.RECOMMENDATION("spark.history.ui.acls.enable = true")
        else:
            logs.DEBUG("Access control is enabled for history server")

    def check_authentication(self):
        if utils.get_item_from_obj(self.content, "spark.authenticate", default="false") == "false":
            logs.ISSUE("Everyone can visit the instance")
            logs.RECOMMENDATION("spark.authenticate = true")
        else:
            logs.DEBUG("Authentication is enabled")
            password = utils.get_item_from_obj(self.content, "spark.authenticate.secret", default="")
            if utils.check_pwd(password):
                logs.DEBUG('Password is strong')
            else:
                logs.ISSUE('Password could be easily guessed.')
                logs.RECOMMENDATION("spark.authenticate.secret [stronger passwor]")

    def check_ssl(self):
        if utils.get_item_from_obj(self.content, "spark.ssl.enabled", default="false") == "false":
            logs.ISSUE("SSL is not enabled")
            logs.RECOMMENDATION("spark.ssl.enable = true")
        else:
            logs.DEBUG('SSL is enabled')

    def check_encryption(self):
        if utils.get_item_from_obj(self.content, "spark.network.crypto.enabled", default="false") == "false":
            logs.ISSUE("Network encryption is not enabled")
            logs.RECOMMENDATION("spark.network.crypto.enable = true")
        else:
            logs.DEBUG('Network encryption is enabled')

        if utils.get_item_from_obj(self.content, "spark.io.encryption.enabled", default="false") == "false":
            logs.ISSUE("Disk encryption is not enabled")
            logs.RECOMMENDATION("spark.io.encryption.enable = true")
        else:
            logs.DEBUG('Disk encryption is enabled')

    def check_xss(self):
        if utils.get_item_from_obj(self.content, "spark.ui.xXssProtection", default="1;mode=block") == "0":
            logs.ISSUE("XSS protection is not enabled")
            logs.RECOMMENDATION("spark.ui.xXssProtection = 1")
        else:
            logs.DEBUG('XSS protection is enabled')

        if utils.get_item_from_obj(self.content, "spark.ui.xContentTypeOptions.enabled", default="true") == "false":
            logs.ISSUE("CORB protection is not enabled")
            logs.RECOMMENDATION("spark.ui.xContentTypeOptions.enabled = true")
        else:
            logs.DEBUG('CORB protection is enabled')

    def check_logging(self):
        if utils.get_item_from_obj(self.content, "spark.eventLog.enabled", default="false") == "false":
            logs.ISSUE("Logging is not enabled")
            logs.RECOMMENDATION("spark.eventLog.enabled = true")
        else:
            logs.DEBUG('Logging is enabled')

    def check_conf(self):
        logs.INFO("Checking ACL")
        self.check_acl()
        logs.INFO("Checking XSS")
        self.check_xss()
        logs.INFO("Checking SSL")
        self.check_ssl()
        logs.INFO("Checking encryption")
        self.check_encryption()
        logs.INFO("Checking web ui authentication")
        self.check_authentication()
        logs.INFO("Checking logging")
        self.check_logging()
