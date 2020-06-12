# Copyright: [DAudit] - See LICENSE for details.
# Authors: Shou Chaofan (@shouc),
import logs
import utils
import sys


class Interface(object):
    def __init__(self):
        pass

    def enumerate_path(self) -> [str]:
        return []

    def __test_exp_files(self, path, expected_files):
        for f in expected_files:
            if not utils.exists_file(path, f):
                return False
        return True

    def __test_files_appear(self, path, files_appear):
        appeared = False
        for f in files_appear:
            if utils.exists_file(path, f):
                appeared = True
        return appeared

    def get_paths(self, expected_file="", expected_files=None, files_appear=None):
        result = []
        paths = self.enumerate_path()
        for path in paths:
            if expected_files and (not self.__test_exp_files(path, expected_files)):
                continue
            if expected_file != "" and (not utils.exists_file(path, expected_file)):
                continue
            if files_appear is not None and (not self.__test_files_appear(path, files_appear)):
                continue
            result.append(path)
        if len(result) == 0:
            logs.ERROR("Cannot find configuration file location, please specify")
            sys.exit(0)
        if len(result) > 1:
            logs.ERROR("Multiple configuration file locations found (listed below), "
                       "please specify  (e.g. --dir=/etc)")
            for k,v in enumerate(result):
                logs.INFO(f"[{k}]. {v}")
            sys.exit(0)
        return result[0]

    def check_conf(self):
        pass

    def __del__(self):
        pass