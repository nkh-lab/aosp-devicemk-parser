## Intro
Simple tests for quick verification. 

## How to run
Example: Use ad hoc `TestConditions.mk`
```
$ python tests/test_mk_file_parser.py vendor/nkh-lab/tools/aosp-devicemk-parser/tests/data/TestConditions.mk
include-path/OK1.mk 0
include-path/OK3.mk 0
include-path/OK5.mk 0
include-path/OK7.mk 0
include-path/OK9.mk 0
include-path/OK11.mk 0
include-path/OK15.mk 0
include-path/OK17.mk 0
include-path/OK21.mk 0
```
Example: Use ad hoc `TestMkFunctions.mk`
```
$ python tests/test_mk_file_parser.py vendor/nkh-lab/tools/aosp-devicemk-parser/tests/data/TestMkFunctions.mk
include-path/OK1.mk 0
include-path/OK3.mk 0
include-path/OK4.mk 0
```
Example: Use real mk file for test
```
$ python tests/test_mk_file_parser.py device/nkh-lab/ncar/ncar_x86.mk
device/generic/car/emulator/aosp_car_emulator.mk 1
build/make/target/product/aosp_x86.mk 1
device/nkh-lab/ncar/ncar_x86/device-ncar_x86.mk 1
```