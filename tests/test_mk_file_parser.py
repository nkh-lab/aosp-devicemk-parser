from mk_file_parser.mk_file_parser import *
from utils import elog


def mocked_get_env_var(name):

    ret = ""

    if name == "ANDROID_BUILD_TOP":
        ret = os.getcwd()

    return ret


def assert_wrong_include(include):
    if "/NOK" in include:
        return False
    else:
        return True


def test_conditions_parsing(mocker):

    mocker.patch('utils.utils.get_env_var', mocked_get_env_var)

    EXPECTED_OK_INCLUDES = 9

    mk_f = MkFileParser("tests/data/TestConditions.mk")

    err_msg = mk_f.parse()

    assert err_msg is None

    if err_msg is None:
        assert len(mk_f.get_includes()) == EXPECTED_OK_INCLUDES

        for i in mk_f.get_includes():
            assert assert_wrong_include(i.name)


def test_gnu_functions_parsing(mocker):

    mocker.patch('utils.utils.get_env_var', mocked_get_env_var)

    EXPECTED_OK_INCLUDES = 3

    mk_f = MkFileParser("tests/data/TestGnuFunctions.mk")

    err_msg = mk_f.parse()

    assert err_msg is None

    if err_msg is None:
        assert len(mk_f.get_includes()) == EXPECTED_OK_INCLUDES

        for i in mk_f.get_includes():
            assert assert_wrong_include(i.name)


def mocked_get_build_var_1(name):

    elog.d(name)

    if name == "TEST_BOARD_PLATFORM_LIST":
        return "PLATFORM1 PLATFORM2 PLATFORM3"

    if name == "TEST_VENDOR_BOARD_PLATFORMS":
        return "PLATFORM2 PLATFORM3"

    if name == "TARGET_BOARD_PLATFORM":
        return "PLATFORM3"

    if name == "TARGET_PRODUCT":
        return "PRODUCT1"

    return ""


def test_google_functions_parsing(mocker):

    mocker.patch('utils.utils.get_env_var', mocked_get_env_var)
    mocker.patch('utils.utils.get_build_var', mocked_get_build_var_1)

    EXPECTED_OK_INCLUDES = 8

    mk_f = MkFileParser("tests/data/TestGoogleFunctions.mk")

    err_msg = mk_f.parse()

    assert err_msg is None

    if err_msg is None:
        assert len(mk_f.get_includes()) == EXPECTED_OK_INCLUDES

        for i in mk_f.get_includes():
            assert assert_wrong_include(i.name)
