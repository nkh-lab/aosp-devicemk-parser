from __future__ import print_function

import os

from mk_file_parser.mk_file_parser import *


def build(output_file, files):
    with open(output_file, 'w') as out:
        print("@startuml", file=out)
        print("", file=out)

        for f_idx, f in enumerate(files):
            path, name = os.path.split(f.name)
            # Do escaped '*'
            if name.startswith("*"):
                name = "~" + name
            color = ""
            if f.exists == False:
                color = " #LightCoral"
            print("file F{f_idx}{color}[\n    {name}\n    {path}\n]".format(
                **locals()), file=out)

        print("F0 -right-> F1 : $PRODUCT_DEVICE", file=out)

        for f_idx, f in enumerate(files):
            if f.includes is not None:
                for i_idx, i in enumerate(f.includes):
                    i_global_idx = _get_idx(files, i.name)
                    type = _type_to_puml_str(i.type)
                    print(
                        "F{f_idx} -down-> F{i_global_idx} : {type}".format(**locals()), file=out)

        print("", file=out)
        print("legend left", file=out)
        print("    Legend", file=out)
        print("    | Symbol | Meaning |", file=out)
        print("    |<#LightCoral>| File not found in AOSP tree |", file=out)
        print("endlegend", file=out)
        print("", file=out)

        print("@enduml", file=out)


def _get_idx(files, name):
    for i, f in enumerate(files):
        if f.name == name:
            return i
    return None


def _type_to_puml_str(include_type):
    if include_type == MkFileInclude.TYPE_INCLUDE:
        return "include"
    if include_type == MkFileInclude.TYPE_INCLUDE_IF_EXIST:
        return "\" -include\""
    if include_type == MkFileInclude.TYPE_INHERIT:
        return "inherit-product"
    if include_type == MkFileInclude.TYPE_INHERIT_IF_EXISTS:
        return "inherit-product-if-exists"
    else:
        return "ERROR"
