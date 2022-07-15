import os
import sys

from utils import utils
from mk_file_parser.mk_file_parser import *


def main():

    android_dir = utils.get_env_var("ANDROID_BUILD_TOP")

    wd = os.getcwd()
    os.chdir(android_dir)

    mk_f = MkFileParser(sys.argv[1])

    err_msg = mk_f.parse()

    if err_msg is None:
        includes = mk_f.get_includes()

        for i in includes:
            print("{0.name} {0.type}".format(i))

    os.chdir(wd)


if __name__ == "__main__":
    main()
