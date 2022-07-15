## Intro
Unit and Component Tests

## Unit Tests
Unit tests based on PyTest and environment agnostic (all dependencies are mocked).

### Install depedencies
```
pip install pytest-mock
```

### How to run
```
pytest tests/
```

## Component Tests
Component tests require real einvorement (sourced and lunched target).

### How to run
Source and lunch target:
```
$ . ./build/envsetup.sh
$ lunch ncar_x86-userdebug
$ cd vendor/nkh-lab/tools/devicemk-parser/
```
And run Component Test script.

For example `ctest_parse_single_mk.py` for parsing single mk file:
```
$ python tests/ctest_parse_single_mk.py build/make/target/product/aosp_x86.mk
build/make/target/product/generic_system.mk 2
build/make/target/product/handheld_system_ext.mk 2
build/make/target/product/telephony_system_ext.mk 2
build/make/target/product/aosp_product.mk 2
device/generic/goldfish/x86-vendor.mk 3
build/make/target/product/emulator_vendor.mk 2
build/make/target/board/generic_x86/device.mk 2
```