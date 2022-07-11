
import argparse
import os
import sys

# Locals imports
from mk_file_parser.mk_file_parser import *
from output_builders import puml_builder
from output_builders import text_builder
from utils import utils


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

    android_dir = utils.get_env_var("ANDROID_BUILD_TOP")

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
    target_product = utils.get_build_var("TARGET_PRODUCT")

    return os.popen("find device -name {target_product}.mk".format(**locals())).read().rstrip()


def get_board_config_mk():
    product_device = utils.get_build_var("PRODUCT_DEVICE")

    product_device_folder = os.popen(
        "find device -name {product_device}".format(**locals())).read().rstrip()

    if product_device_folder == "":
        product_device_folder = os.popen(
            "find vendor -name {product_device}".format(**locals())).read().rstrip()

    return "{product_device_folder}/BoardConfig.mk".format(**locals())


def main():
    arg_parser = argparse.ArgumentParser()

    arg_parser.add_argument("--puml", nargs='?', const="")
    arg_parser.add_argument("--text", nargs='?', const="")

    args = arg_parser.parse_args(sys.argv[1:])

    print("Parsing make files dependencies...")
    files = parse()

    if files is None:
        return
    elif len(files):
        print("Built output files:")

        if args.puml is not None and args.puml != "":
            puml_output_file = args.puml
        else:
            path, name = os.path.split(files[0].name)
            puml_output_file = os.path.abspath(
                "./" + name.replace(".mk", ".puml"))

        puml_builder.build(puml_output_file, files)
        print("PUML: {puml_output_file}".format(**locals()))

        if args.text is not None:
            if args.text != "":
                text_output_file = os.path.abspath(args.text)
            else:
                path, name = os.path.split(files[0].name)
                text_output_file = os.path.abspath(
                    "./" + name.replace(".mk", ".txt"))

            text_builder.build(text_output_file, files)
            print("Text: {text_output_file}".format(**locals()))
    else:
        print("Error: Parsing failed!")


if __name__ == "__main__":
    main()
