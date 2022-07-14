# Coment line

ifeq (,$(filter-out test1,test1))
  include include-path/OK1.mk
else
  include include-path/NOK2.mk
endif

ifneq (,$(filter test1,test1))
  include include-path/OK3.mk
else
  include include-path/NOK4.mk  
endif

ifneq (,$(filter test1,test1))
  include include-path/OK5.mk
else ifneq (,$(filter test1,test1))
  include include-path/NOK6.mk  
endif