from utils import utils

# Python implementation of some custom functions
# from android/device/google/coral/utils.mk


# $(call match-word,w1,w2)
# checks if w1 == w2
# returns true or empty
def match_word(w1, w2):
    if w1 == w2:
        return "true"

    return ""

# $(call match-word-in-list,w,wlist)
# does an exact match of word w in word list wlist
# returns true or empty
def match_word_in_list(w, wlist):
    for i in wlist.split():
        if w == i:
            return "true"
    return ""

# $(call is-board-platform,bp)
# returns true or empty
def is_board_platform(bp):
    return match_word(bp, utils.get_build_var("TARGET_BOARD_PLATFORM"))


# $(call is-board-platform-in-list,bpl)
# returns true or empty
def is_board_platform_in_list(bpl):
    bp = utils.get_build_var("TARGET_BOARD_PLATFORM")

    return match_word_in_list(bp, bpl)


# $(call get-vendor-board-platforms,v)
# returns list of board platforms for vendor v
def get_vendor_board_platforms(v):

    return utils.get_build_var("{v}_BOARD_PLATFORMS".format(**locals()))

# $(call is-vendor-board-platform,vendor)
# returns true or empty
def is_vendor_board_platform(vendor):
    bp = utils.get_build_var("TARGET_BOARD_PLATFORM")

    return match_word_in_list(bp, get_vendor_board_platforms(vendor))

# $(call is-product-in-list,pl)
# returns true or empty
def is_product_in_list(tpl):
    tp = utils.get_build_var("TARGET_PRODUCT")

    return match_word_in_list(tp, tpl)
