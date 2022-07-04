import os
import re


class Include:
    TYPE_INCLUDE = 0
    TYPE_INHERIT = 1
    TYPE_INHERIT_IF_EXISTS = 2

    def __init__(self, name, type):
        self.name = name
        self.type = type

    def type_str(self):
        if self.type == Include.TYPE_INHERIT:
            return "inherit-product"
        if self.type == Include.TYPE_INHERIT_IF_EXISTS:
            return "inherit-product-if-exists"
        else:
            return "include"


class MkFile:

    def __init__(self, name, exists=False, includes=None):
        self.name = name
        self.exists = exists
        self.includes = includes


def is_file_in_work(file, to_parse, parsed):
    if file in to_parse:
        return True
    else:
        for f in parsed:
            if f.name == file:
                return True
    return False


def resolve_build_vars(line):
    p_build_var = re.compile("\$\((.*)\)")
    res = p_build_var.search(line)

    if res is not None:
        build_var_name = res.group(1)
        build_var_value = get_build_var(build_var_name)
        if build_var_value != "":
            return line.replace("$(%s)" % build_var_name, build_var_value)

    return line


def parse_line(line):
    if parse_line_is_comment(line):
        return None

    out_line = parse_line_call_inherit_product(line)

    if out_line is None:
        out_line = parse_line_call_inherit_product_if_exists(line)
    else:
        return out_line

    if out_line is None:
        out_line = parse_line_include(line)
    else:
        return out_line

    return out_line


def parse_line_is_comment(line):
    return line.strip().startswith("#")


def parse_line_call_inherit_product(line):
    p = re.compile("\$\(call inherit-product,(.*)\)")
    res = p.search(line)

    if res is not None:
        include_path = resolve_build_vars(res.group(1).strip().rstrip())
        return Include(include_path, Include.TYPE_INHERIT)

    return None


def parse_line_call_inherit_product_if_exists(line):
    p = re.compile("\$\(call inherit-product-if-exists,(.*)\)")
    res = p.search(line)

    if res is not None:
        include_path = resolve_build_vars(res.group(1).strip().rstrip())
        return Include(include_path, Include.TYPE_INHERIT_IF_EXISTS)

    return None


def parse_line_include(line):
    p = re.compile("include (.*)")
    res = p.search(line)

    if res is not None:
        include_path = resolve_build_vars(res.group(1).strip().rstrip())
        return Include(include_path, Include.TYPE_INCLUDE)

    return None


def parse_file(android_dir, file):
    includes = []

    file_abs_path = android_dir + "/" + file

    with open(file_abs_path) as t:
        for line in t.readlines():
            include = parse_line(line)
            if include is not None:
                includes.append(include)

    return includes


def parse(android_dir):
    files = []
    files_to_parse = []

    device_mk = get_device_mk()
    board_config_mk = get_board_config_mk(device_mk)

    files_to_parse.append(device_mk)
    files_to_parse.append(board_config_mk)

    while len(files_to_parse):
        f = files_to_parse.pop(0)

        if os.path.exists(f):
            includes = parse_file(android_dir, f)
            files.append(MkFile(f, True, includes))
            for i in includes:
                if is_file_in_work(i.name, files_to_parse, files) == False:
                    files_to_parse.append(i.name)
        else:
            files.append(MkFile(f))

    return files


def get_env_var(name):
    cached_value = get_env_var.dict.get(name)
    if cached_value is None:
        value = os.popen("echo $%s" % name).read().rstrip()
        get_env_var.dict[name] = value
        #print ("name: %s, value: %s" % (name, value))
        return value
    return cached_value


get_env_var.dict = {}


def get_build_var(name):
    cached_value = get_build_var.dict.get(name)
    if cached_value is None:
        value = os.popen("soong_ui --dumpvar-mode %s" % name).read().rstrip()
        get_build_var.dict[name] = value
        #print ("name: %s, value: %s" % (name, value))
        return value
    return cached_value


get_build_var.dict = {}


def get_device_mk():
    target_product = get_build_var("TARGET_PRODUCT")
    product_manufacturer = get_build_var("PRODUCT_MANUFACTURER")

    return os.popen("find device/{product_manufacturer} -name {target_product}.mk".format(**locals())).read().rstrip()


def get_board_config_mk(device_mk):
    product_device = get_build_var("PRODUCT_DEVICE")
    path, name = os.path.split(device_mk)

    return "{path}/{product_device}/BoardConfig.mk".format(**locals())


def build_txt(files):
    f_idx = 0
    for f in files:
        print("F%d: %s" % (f_idx, f.name))
        i_idx = 0
        for i in f.includes:
            print("    I%d: %d: %s" % (i_idx, i.type, i.name))
            i_idx += 1
        f_idx += 1


def build_puml(files):
    print("@startuml")
    print("")

    for f_idx, f in enumerate(files):
        path, name = os.path.split(f.name)
        color = ""
        if f.exists == False:
            color = " #LightCoral"
        print(
            "file F{f_idx}{color}[\n    {name}\n    {path}\n]".format(**locals()))

    print("F0 -right-> F1 : $PRODUCT_DEVICE")

    for f_idx, f in enumerate(files):
        if f.includes is not None:
            for i_idx, i in enumerate(f.includes):
                print("F%d -down-> F%d : %s" %
                      (f_idx, get_idx(files, i.name), i.type_str()))

    print("")
    print("@enduml")


def get_idx(files, name):
    for i, f in enumerate(files):
        if f.name == name:
            return i
    return None


def main():

    android_build_top = get_env_var("ANDROID_BUILD_TOP")

    if android_build_top == "":
        print("Error: The script must be run from Android setup environment!")
        print("       Do environment setup, lunch device and then run the script!")
        return

    wd = os.getcwd()
    os.chdir(android_build_top)

    files = parse(android_build_top)

    # build_txt(files)
    build_puml(files)

    os.chdir(wd)


if __name__ == "__main__":
    main()
