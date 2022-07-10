import re

from mk_functions.mk_functions import *
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


class MkFileCondition:
    TYPE_IFEQ = 0
    TYPE_IFNEQ = 1
    TYPE_ELSEIF = 2
    TYPE_ELSE = 3
    TYPE_ENDIF = 4

    PATTERN_TYPE = [
        # Keep order!
        ["else *(if.*\(.*\))",      TYPE_ELSEIF],
        ["ifeq *\((.*)\)",          TYPE_IFEQ],
        ["ifneq *\((.*)\)",         TYPE_IFNEQ],
        ["else",                    TYPE_ELSE],
        ["endif",                   TYPE_ENDIF],
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

                        self._conditions.append(MkFileCondition(condition_state))
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
                self.includes.append(MkFileInclude(include_path, row[1]))
                return True

        return False

    def _resolve_build_vars(self, line):
        p_build_var = re.compile("\$\(([A-Za-z0-9_]*)\)")

        while True:
            res = p_build_var.search(line)

            if res is not None:
                found_match = res.group(0) 
                build_var_name = res.group(1)

                if build_var_name == "LOCAL_PATH":
                    build_var_value = self._local_path
                else:
                    build_var_value = get_build_var(build_var_name)
                line = line.replace(found_match, build_var_value)
            else:
                break

        return line

    def _resolve_make_functions(self, line):
        p_function = re.compile("\$\(([a-z-]*) (.*),(.*)\)")

        while True:
            res = p_function.search(line)

            if res is not None:
                found_match = res.group(0) 
                function = res.group(1)
                arg1 = res.group(2)
                arg2 = res.group(3)

                function = function.replace("-","_")

                ret = eval(function)(arg1, arg2)

                line = line.replace(found_match, ret)
                break
            else:
                break

        return line

