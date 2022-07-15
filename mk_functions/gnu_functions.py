import re


def filter(pattern, text):
    # print("filter()")
    #print("pattern: {pattern}".format(**locals()))
    #print("text:    {text}".format(**locals()))

    ret = ""

    for p in pattern.split():
        re_p = re.compile("(" + p.replace("%", ".*") + ")")

        while True:
            res = re_p.search(text)

            if res is not None:
                value = res.group(1)
                text = text.replace(value, "", 1)

                if ret == "":
                    ret = value
                else:
                    ret = ret + " " + value
            else:
                break

    return ret


def filter_out(pattern, text):
    # print("filter-out()")
    #print("pattern: {pattern}".format(**locals()))
    #print("text:    {text}".format(**locals()))

    for p in pattern.split():
        re_p = re.compile("(" + p.replace("%", ".*") + ")")

        while True:
            res = re_p.search(text)

            if res is not None:
                value = res.group(1)
                text = text.replace(value, "", 1)
            else:
                break

    return " ".join(text.split())


def findstring(find, str):
    if find in str:
        return find
    else:
        return ""
