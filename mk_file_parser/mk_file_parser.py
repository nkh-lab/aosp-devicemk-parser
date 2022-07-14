import os
import re

from mk_functions import mk_functions
from utils import utils


class MkFileInclude:

    TYPE_INCLUDE = 0
    TYPE_INCLUDE_IF_EXIST = 1
    TYPE_INHERIT = 2
    TYPE_INHERIT_IF_EXISTS = 3

    PATTERN_TYPE = [
        # Keep order!
        [r"-include (.*)",                               TYPE_INCLUDE_IF_EXIST],
        [r"include (.*)",                                TYPE_INCLUDE],
        [r"\$\(call inherit-product,(.*)\)",             TYPE_INHERIT],
        [r"\$\(call inherit-product-if-exists,(.*)\)",   TYPE_INHERIT_IF_EXISTS]
    ]

    def __init__(self, name, type):
        self.name = name
        self.type = type


class MkFileCondition:
    TYPE_IFEQ = 0
    TYPE_IFNEQ = 1
    TYPE_ELSEIF = 2
    TYPE_ELSE = 3
    TYPE_ENDIF = 4

    PATTERN_TYPE = [
        # Keep order!
        [r"else *(if.*\(.*\))",      TYPE_ELSEIF],
        [r"ifeq *\((.*)\)",          TYPE_IFEQ],
        [r"ifneq *\((.*)\)",         TYPE_IFNEQ],
        [r"else",                    TYPE_ELSE],
        [r"endif",                   TYPE_ENDIF],
    ]

    def __init__(self, state):
        self.state = state


class MkFileParseError:

    def __init__(self):
        self.message = None


class MkFileParser:

    def __init__(self, file):
        self.file = file
        self.includes = []

        self._conditions = []
        self._local_path, name = os.path.split(file)
        self._android_dir_slash = utils.get_env_var("ANDROID_BUILD_TOP") + "/"

    def parse(self):
        ret_err_msg = None

        file_abs_path = self._android_dir_slash + self.file

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

        if self._is_condition(line, ret_err) == True:
            return ret_err.message

        if len(self._conditions) and self._conditions[-1].state == False:
            return ret_err.message

        if self._is_include(line, ret_err) == True:
            return ret_err.message

    def _is_comment(self, line):
        return line.strip().startswith("#")

    def _is_condition(self, line, o_err):

        for row in MkFileCondition.PATTERN_TYPE:
            if row[1] == MkFileCondition.TYPE_IFEQ or row[1] == MkFileCondition.TYPE_IFNEQ:
                p = re.compile(row[0])
                res = p.search(line)

                if res is not None:
                    cond_body = res.group(1)

                    cond_body = self._resolve_build_vars(cond_body)
                    cond_body = self._resolve_make_functions(cond_body)
                    #print("cond_body: {cond_body}".format(**locals()))

                    p = re.compile("(.*),(.*)")
                    res = p.search(cond_body)

                    if res is not None:
                        arg1 = res.group(1).strip()
                        arg2 = res.group(2).strip()

                        condition_state = False
                        if arg1 == arg2:
                            condition_state = True

                        if row[1] == MkFileCondition.TYPE_IFNEQ:
                            condition_state = not condition_state

                        self._conditions.append(
                            MkFileCondition(condition_state))
                        return True

            if row[1] == MkFileCondition.TYPE_ELSEIF:
                p = re.compile(row[0])
                res = p.search(line)

                if res is not None:
                    else_state = not self._conditions[-1].state
                    self._conditions.pop()
                    if (else_state == False):
                        self._conditions.append(MkFileCondition(else_state))
                        return True
                    else:
                        return self._is_condition(res.group(1), o_err)

            if row[1] == MkFileCondition.TYPE_ELSE:
                p = re.compile(row[0])
                res = p.search(line)

                if res is not None:
                    else_state = not self._conditions[-1].state
                    self._conditions.pop()
                    self._conditions.append(MkFileCondition(else_state))
                    return True

            if row[1] == MkFileCondition.TYPE_ENDIF:
                p = re.compile(row[0])
                res = p.search(line)

                if res is not None:
                    if len(self._conditions):
                        self._conditions.pop()
                    return True

        return False

    def _is_include(self, line, o_err):

        for row in MkFileInclude.PATTERN_TYPE:
            p = re.compile(row[0])
            res = p.search(line)

            if res is not None:
                include_path = self._resolve_build_vars(
                    res.group(1).strip().rstrip())

                for i in self._intellisense_include_path(include_path):
                    self.includes.append(MkFileInclude(i, row[1]))
                return True

        return False

    def _resolve_build_vars(self, line):
        p_build_var = re.compile(r"\$\(([A-Za-z0-9_]*)\)")

        while True:
            res = p_build_var.search(line)

            if res is not None:
                found_match = res.group(0)
                build_var_name = res.group(1)

                if build_var_name == "LOCAL_PATH":
                    build_var_value = self._local_path
                else:
                    build_var_value = utils.get_build_var(build_var_name)
                line = line.replace(found_match, build_var_value)
            else:
                break

        return line

    def _resolve_make_functions(self, line):
        p_function = re.compile(r"\$\(([a-z-]*) (.*),(.*)\)")

        while True:
            res = p_function.search(line)

            if res is not None:
                found_match = res.group(0)
                function = res.group(1)
                arg1 = res.group(2)
                arg2 = res.group(3)

                function = function.replace("-", "_")

                # TODO: Add option to load module with implemented custom functions
                if function != "call":
                    ret = getattr(mk_functions, function)(arg1, arg2)
                    line = line.replace(found_match, ret)
                break
            else:
                break

        return line

    def _intellisense_include_path(self, found_include):
        includes = []
        # Do relative path if it is absolute
        rel_path = self._do_relative_path(found_include)

        if "*" in rel_path:
            path, name = os.path.split(rel_path)
            for i in os.popen("find {path} -name {name}".format(**locals())).read().splitlines():
                includes.append(i)
        else:
            includes.append(rel_path)

        return includes

    def _do_relative_path(self, path):
        return path.replace(self._android_dir_slash, "")
