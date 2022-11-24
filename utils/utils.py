import os
import subprocess


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
        with open(os.devnull, 'w') as DEVNULL:
            value = subprocess.check_output(
                ["soong_ui", "--dumpvar-mode", name], text=True, stderr=DEVNULL).rstrip()
        get_build_var.dict[name] = value
        # Debug
        #print("name: {name}, value: {value}".format(**locals()))
        return value
    return cached_value


get_build_var.dict = {}
