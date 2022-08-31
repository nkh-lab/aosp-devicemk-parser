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

ifeq (true,)
    include include-path/NOK13.mk
else ifeq (true,)
    include include-path/NOK14.mk
else
    include include-path/OK15.mk
endif

ifeq (true,)
    include include-path/NOK16.mk
else ifeq (true,true)
    ifeq (true,true)
        include include-path/OK17.mk
    else
        include include-path/NOK19.mk 
    endif
else
    include include-path/NOK20.mk
endif

ifeq (true,true)
    include include-path/OK21.mk
else ifeq (true,true)
    include include-path/NOK22.mk
endif

ifdef DEFINED_VAR
    include include-path/OK23.mk
else
    include include-path/NOK24.mk
endif

ifdef UNDEFINED_VAR
    include include-path/NOK25.mk
else ifdef DEFINED_VAR
    include include-path/OK26.mk
else
    include include-path/NOK27.mk
endif

ifndef UNDEFINED_VAR
    include include-path/OK28.mk
else
    include include-path/NOK29.mk
endif

ifdef UNDEFINED_VAR
    include include-path/NOK30.mk
else ifndef UNDEFINED_VAR
    include include-path/OK31.mk
else
    include include-path/NOK32.mk
endif
