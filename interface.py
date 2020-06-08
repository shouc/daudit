import os
import logs
import utils
import sys


class Interface(object):
    def __init__(self):
        pass

    def enumerate_path(self) -> [str]:
        return []

    def get_paths(self, expected_file):
        result = []
        paths = self.enumerate_path()
        for path in paths:
            if (not utils.exists_file(path, expected_file)) or (not os.path.exists(path)):
                continue
            result.append(path)
        if len(result) == 0:
            logs.ERROR("Cannot find configuration file location, please specify it!")
            sys.exit(0)
        if len(result) > 1:
            logs.ERROR("Multiple configuration file locations found (listed below), please specify it!")
            for k,v in enumerate(result):
                logs.INFO(f"[{k}]. {v}")
            sys.exit(0)
        return result[0]

    def check_conf(self):
        pass

    def __del__(self):
        pass