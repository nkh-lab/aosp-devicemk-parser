# Coment line

ifeq (true,true) 
    include include-path/OK1.mk
endif

ifeq (true,)
    include include-path/NOK2.mk
else
    include include-path/OK3.mk
endif

ifeq (true,)
    include include-path/NOK4.mk
else ifeq (true,true)
    include include-path/OK5.mk
endif

ifneq (true,true) 
    include include-path/NOK6.mk
endif

ifneq (true,)
    include include-path/OK7.mk
else
    include include-path/NOK8.mk
endif

ifneq (true, )
    include include-path/OK9.mk
else ifneq (true,true)
    include include-path/NOK10.mk
endif

ifneq ( ,true)
    include include-path/OK11.mk
else
    include include-path/NOK12.mk
endif