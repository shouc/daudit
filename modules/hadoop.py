import interface
import logs
import re
import utils
import os
import xml.etree.ElementTree
import collections
import sys


class Hadoop(interface.Interface):
    def __init__(self, dir=None):
        super().__init__()
        if dir is None:
            self.conf_path = self.get_paths(files_appear=[
                "core-site.xml",
                "hdfs-site.xml",
                "mapred-site.xml",
                "yarn-site.xml",
            ])
        else:
            self.conf_path = dir
        logs.INFO(f"Evaluating directory {self.conf_path}")
        self.core_file = os.path.join(self.conf_path, "core-site.xml")
        self.core_obj = self.xml_conf_to_obj(self.core_file)
        self.hdfs_file = os.path.join(self.conf_path, "hdfs-site.xml")
        self.hdfs_obj = self.xml_conf_to_obj(self.hdfs_file)
        self.mr_file = os.path.join(self.conf_path, "mapred-site.xml")
        self.mr_obj = self.xml_conf_to_obj(self.mr_file)
        self.yarn_file = os.path.join(self.conf_path, "yarn-site.xml")
        self.yarn_obj = self.xml_conf_to_obj(self.yarn_file)
        self.conf_obj = {**self.core_obj, **self.hdfs_obj, **self.mr_obj, **self.yarn_obj}

    def enumerate_path(self):
        return list({
            *utils.whereis("hadoop"),
            "/usr/local/cellar/hadoop/3.2.1/libexec/etc/hadoop/", # homebrew
            "/local/hadoop/etc/hadoop", # apt,
            "/etc/hadoop", # apt
        })

    @staticmethod
    def xml_conf_to_obj(file):
        res = {}
        try:
            root = xml.etree.ElementTree.parse(file).getroot()
            props = root.findall(".//property")
            for prop in props:
                name = prop.find(".//name").text
                try:
                    value = prop.find(".//value").text
                    res[name] = value
                except AttributeError:
                    continue
        except FileNotFoundError:
            logs.INFO(f"{file} not found, skipped.")
        except Exception as e:
            logs.ERROR(e)
            sys.exit(0)
        return res

    def check_global_ac(self):
        logs.INFO("Checking global access control")
        auth_method = utils.get_item_from_obj(self.conf_obj, "hadoop.security.authentication", default="simple")
        if auth_method == "simple":
            logs.WARN("Everyone can access the instance")
            logs.RECOMMENDATION("Consider setting property hadoop.security.authentication = kerberos")
        else:
            logs.DEBUG(f"Authentication method [{auth_method}] enabled")
        if utils.get_item_from_obj(self.conf_obj, "hadoop.security.authorization", default="false") == "false":
            logs.WARN("Authorization is not enabled")
            logs.RECOMMENDATION("Consider setting property hadoop.security.authorization = true based on the context. "
                                "This can increase granularity for access control. ")
        else:
            logs.DEBUG("Authorization enabled")

    def check_web_portal_ac(self):
        logs.INFO("Checking web portal access control")
        auth_method = utils.get_item_from_obj(self.conf_obj, "hadoop.http.authentication.type", default="simple")
        if auth_method == "simple":
            logs.WARN("Everyone can access the web portal")
            logs.RECOMMENDATION("Consider setting property hadoop.http.authentication.type = kerberos")
            if utils.get_item_from_obj(self.conf_obj, "hadoop.http.authentication.simple.anonymous.allowed",
                                       default="true") == "true":
                logs.WARN("Anonymous is allowed to access web portal.")
                logs.RECOMMENDATION("Consider setting property "
                                    "hadoop.http.authentication.simple.anonymous.allowed = false")
        else:
            logs.DEBUG(f"Authentication method [{auth_method}] enabled")

    def check_cors(self):
        logs.INFO("Checking web portal cross origin policy")

        if utils.get_item_from_obj(self.conf_obj, "hadoop.http.cross-origin.enabled",
                                   default="false") == "true":
            allowed_origins = utils.split_ip(
                utils.get_item_from_obj(self.conf_obj, "hadoop.http.cross-origin.allowed-origins",
                                       default="true")
            )
            if "*" in allowed_origins:
                logs.WARN("Cross origin is wildcard.")
                logs.RECOMMENDATION("Consider qualify it based on the context.")
            else:
                logs.DEBUG(f"CORS is enabled but only allowed to {','.join(allowed_origins)}")
        else:
            logs.DEBUG("CORS is off")

    def check_ssl(self):
        logs.INFO("Checking SSL")

        if utils.get_item_from_obj(self.conf_obj, "hadoop.ssl.enabled",
                                   default="false") == "false":
            logs.WARN("SSL is disabled.")
            logs.RECOMMENDATION("Consider config SSL in core-site.xml.")
        else:
            logs.DEBUG("SSL is enabled.")

    def check_nfs_export_range(self):
        logs.INFO("Checking export range")

        allowed_hosts = utils.get_item_from_obj(self.conf_obj, "nfs.exports.allowed.hosts", default="* rw")
        if allowed_hosts == "* rw":
            logs.WARN("NFS is exposed to internet for read and write.")
            logs.RECOMMENDATION("Consider qualify nfs.exports.allowed.hosts.")
        else:
            logs.DEBUG(f"NFS host priv: {allowed_hosts}. Evaluate based on the context.")

    def check_registry_ac(self):
        logs.INFO("Checking registry access control")

        if utils.get_item_from_obj(self.conf_obj, "hadoop.registry.rm.enabled", default="false") == "true":
            if  utils.get_item_from_obj(self.conf_obj, "hadoop.registry.secure", default="false") == "false":
                logs.WARN("registry.secure is not enabled. ")
                logs.RECOMMENDATION("Consider setting hadoop.registry.secure = true based on context. ")
            else:
                logs.DEBUG(f"Registry security is enabled.")
        else:
            logs.DEBUG("Registry is not enabled. ")

    def check_fs_permission(self):
        logs.INFO("Checking hdfs permission")
        if utils.get_item_from_obj(self.conf_obj, "dfs.permissions.enabled",
                                   default="true") == "false":
            logs.WARN("HDFS does not have access control. Everyone could conduct CURD operations on the instance.")
            logs.RECOMMENDATION("Consider setting dfs.permissions.enabled = true")
        else:
            logs.DEBUG("HDFS permission system is enabled.")
        if utils.get_item_from_obj(self.conf_obj, "dfs.namenode.acls.enabled",
                                   default="false") == "false":
            logs.WARN("HDFS ACLs is not enabled.")
            logs.RECOMMENDATION("Consider setting dfs.namenode.acls.enabled = true to increase granularity"
                                " of control based on context.")
        else:
            logs.DEBUG("HDFS ACLs is enabled.")

    def check_conf(self):
        self.check_cors()
        self.check_ssl()
        self.check_global_ac()
        self.check_web_portal_ac()
        self.check_registry_ac()
        self.check_fs_permission()
        self.check_nfs_export_range()
