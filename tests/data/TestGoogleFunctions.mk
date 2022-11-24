# Coment line

ifeq ($(call is-board-platform-in-list,$(TEST_BOARD_PLATFORM_LIST)),true)
  include include-path/OK1.mk
else
  include include-path/NOK2.mk
endif

ifneq ($(call is-board-platform-in-list,$(TEST_BOARD_PLATFORM_LIST)),true)
  include include-path/NOK3.mk
else
  include include-path/OK4.mk  
endif

ifeq ($(call is-vendor-board-platform,TEST_VENDOR),true)
  include include-path/OK5.mk
else
  include include-path/NOK6.mk
endif

ifneq ($(call is-vendor-board-platform,TEST_VENDOR),true)
  include include-path/NOK7.mk
else
  include include-path/OK8.mk  
endif

ifeq ($(call is_board_platform,PLATFORM3),true)
  include include-path/OK9.mk
else
  include include-path/NOK10.mk
endif

ifneq ($(call is_board_platform,PLATFORM3),true)
  include include-path/NOK11.mk
else
  include include-path/OK12.mk  
endif

ifeq ($(call is-product-in-list,PRODUCT1 PRODUCT2 PRODUCT3),true)
  include include-path/OK13.mk
else
  include include-path/NOK14.mk
endif

ifneq ($(call is-product-in-list,PRODUCT1 PRODUCT2 PRODUCT3),true)
  include include-path/NOK15.mk
else
  include include-path/OK16.mk  
endif

ifeq ($(call is-platform-sdk-version-at-least,31),true)
  include include-path/OK17.mk
endif

ifneq ($(call is-platform-sdk-version-at-least,33),true)
  include include-path/OK18.mk
endif
