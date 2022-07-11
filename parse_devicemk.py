from __future__ import print_function
import argparse
import os
import re
import sys

from utils.utils import *
from mk_file_parser.mk_file_parser import *


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
                print(f)
                mk_file = MkFileParser(f)
                err_msg = mk_file.parse()

                if err_msg is None:
                    includes = mk_file.get_includes()
                    files.append(MkFile(f, True, includes))
                    for i in includes:
                        if is_file_in_work(i.name, files_to_parse, files) == False:
                            files_to_parse.append(i.name)
            else:
                files.append(MkFile(f))

        os.chdir(wd)

    return files


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
