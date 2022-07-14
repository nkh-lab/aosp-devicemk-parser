from mk_file_parser.mk_file_parser import *


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


def test_mk_functions_parsing(mocker):

    mocker.patch('utils.utils.get_env_var', mocked_get_env_var)

    EXPECTED_OK_INCLUDES = 3

    mk_f = MkFileParser("tests/data/TestMkFunctions.mk")

    err_msg = mk_f.parse()

    assert err_msg is None

    if err_msg is None:
        assert len(mk_f.get_includes()) == EXPECTED_OK_INCLUDES

        for i in mk_f.get_includes():
            assert assert_wrong_include(i.name)
