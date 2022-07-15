import inspect
import sys


def w(msg):
    print("  WARNING: " + msg)
    w.count = w.count + 1


w.count = 0


def e(msg):
    print("    ERROR: " + msg)
    sys.exit(1)


def d(msg):
    print("    DEBUG: {caller}(): {msg}".format(
        caller=inspect.stack()[1][3], msg=msg))
