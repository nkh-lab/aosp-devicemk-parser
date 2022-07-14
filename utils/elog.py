def w(msg):
    print("  WARNING: " + msg)
    w.count = w.count + 1

w.count = 0

def e(msg):
    print("    ERROR: " + msg)