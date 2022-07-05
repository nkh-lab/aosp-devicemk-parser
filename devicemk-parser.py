from __future__ import print_function
import argparse
import os
import re
import sys


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
            return line.replace("$({build_var_name})".format(**locals()), build_var_value)

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


def parse():
    files = []
    files_to_parse = []

    android_dir = get_env_var("ANDROID_BUILD_TOP")

    if android_dir == "":
        print("Error: The script must be run from Android setup environment!")
        print("       Do environment setup, lunch device and then run the script!")
        return None

    wd = os.getcwd()
    os.chdir(android_dir)

    device_mk = get_device_mk()

    if device_mk != "":
        board_config_mk = get_board_config_mk()

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

        os.chdir(wd)

    return files


def get_env_var(name):
    cached_value = get_env_var.dict.get(name)
    if cached_value is None:
        value = os.popen("echo ${name}".format(**locals())).read().rstrip()
        get_env_var.dict[name] = value
        # print("name: {name}, value: {value}".format(**locals()))
        return value
    return cached_value


get_env_var.dict = {}


def get_build_var(name):
    cached_value = get_build_var.dict.get(name)
    if cached_value is None:
        value = os.popen(
            "soong_ui --dumpvar-mode {name}".format(**locals())).read().rstrip()
        get_build_var.dict[name] = value
        # print("name: {name}, value: {value}".format(**locals()))
        return value
    return cached_value


get_build_var.dict = {}


def get_device_mk():
    target_product = get_build_var("TARGET_PRODUCT")

    return os.popen("find device -name {target_product}.mk".format(**locals())).read().rstrip()


def get_board_config_mk():
    product_device = get_build_var("PRODUCT_DEVICE")

    product_device_folder = os.popen(
        "find device -name {product_device}".format(**locals())).read().rstrip()

    if product_device_folder == "":
        product_device_folder = os.popen(
            "find vendor -name {product_device}".format(**locals())).read().rstrip()

    return "{product_device_folder}/BoardConfig.mk".format(**locals())


def build_text_output(output_file, files):
    with open(output_file, 'w') as out:
        for f_idx, f in enumerate(files):
            print("F{f_idx}: {0.name}".format(f, **locals()), file=out)

            if f.includes is not None:
                for i_idx, i in enumerate(f.includes):
                    print("    I{i_idx}: {0.type}: {0.name}".format(
                        i, **locals()), file=out)


def build_puml_output(output_file, files):
    with open(output_file, 'w') as out:
        print("@startuml", file=out)
        print("", file=out)

        for f_idx, f in enumerate(files):
            path, name = os.path.split(f.name)
            color = ""
            if f.exists == False:
                color = " #LightCoral"
            print("file F{f_idx}{color}[\n    {name}\n    {path}\n]".format(
                **locals()), file=out)

        print("F0 -right-> F1 : $PRODUCT_DEVICE", file=out)

        for f_idx, f in enumerate(files):
            if f.includes is not None:
                for i_idx, i in enumerate(f.includes):
                    i_global_idx = get_idx(files, i.name)
                    type = i.type_str()
                    print(
                        "F{f_idx} -down-> F{i_global_idx} : {type}".format(**locals()), file=out)

        print("", file=out)
        print("@enduml", file=out)


def get_idx(files, name):
    for i, f in enumerate(files):
        if f.name == name:
            return i
    return None


def main():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("--puml")
    arg_parser.add_argument("--text")

    args = arg_parser.parse_args(sys.argv[1:])

    print("Parsing make files dependencies...")
    files = parse()

    if files is None:
        return
    elif len(files):
        print("Built output files:")

        puml_output_file = ""
        if args.puml is not None:
            puml_output_file = args.puml
        else:
            path, name = os.path.split(files[0].name)
            puml_output_file = os.path.abspath(
                "./" + name.replace(".mk", ".puml"))

        build_puml_output(puml_output_file, files)
        print("PUML: {puml_output_file}".format(**locals()))

        if args.text is not None:
            text_output_file = os.path.abspath(args.text)
            build_text_output(text_output_file, files)
            print("Text: {text_output_file}".format(**locals()))
    else:
        print("Error: Parsing failed!")


if __name__ == "__main__":
    main()
