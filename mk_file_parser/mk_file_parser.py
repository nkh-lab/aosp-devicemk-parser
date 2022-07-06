import re

from utils.utils import *


class MkFileInclude:

    TYPE_INCLUDE = 0
    TYPE_INHERIT = 1
    TYPE_INHERIT_IF_EXISTS = 2

    PATTERN_TYPE = [

        ["include (.*)",                                TYPE_INCLUDE],
        ["\$\(call inherit-product,(.*)\)",             TYPE_INHERIT],
        ["\$\(call inherit-product-if-exists,(.*)\)",   TYPE_INHERIT_IF_EXISTS]
    ]

    def __init__(self, name, type):
        self.name = name
        self.type = type

    def type_str(self):
        if self.type == MkFileInclude.TYPE_INHERIT:
            return "inherit-product"
        if self.type == MkFileInclude.TYPE_INHERIT_IF_EXISTS:
            return "inherit-product-if-exists"
        else:
            return "include"

class MkFileParseError:

    def __init__(self):
        self.message = None


class MkFileParser:

    def __init__(self, file):
        self.file = file

        self.includes = []

    def parse(self):
        ret_err_msg = None

        android_dir = get_env_var("ANDROID_BUILD_TOP")

        file_abs_path = android_dir + "/" + self.file

        with open(file_abs_path) as f:
            for line in f.readlines():
                ret_err_msg = self._parse_line(line)
                if ret_err_msg is not None:
                    break

        return ret_err_msg

    def get_includes(self):

        return self.includes

    def _parse_line(self, line):
        ret_err = MkFileParseError()

        if self._is_comment(line) == True:
            return ret_err.message

        if self._is_include(line, ret_err) == True:
            return ret_err.message

    def _is_comment(self, line):
        return line.strip().startswith("#")

    def _is_include(self, line, o_err):

        for row in MkFileInclude.PATTERN_TYPE:
            p = re.compile(row[0])
            res = p.search(line)

            if res is not None:
                include_path = self._resolve_build_vars(
                    res.group(1).strip().rstrip())
                self.includes.append(MkFileInclude(include_path, row[1]))
                return True

        return False

    def _resolve_build_vars(self, line):
        p_build_var = re.compile("\$\((.*)\)")
        res = p_build_var.search(line)

        if res is not None:
            build_var_name = res.group(1)
            build_var_value = get_build_var(build_var_name)
            if build_var_value != "":
                return line.replace("$({build_var_name})".format(**locals()), build_var_value)

        return line
