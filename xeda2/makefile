#--------------------------------------------------------------------------
#
#    Makefile for the MCC18 compiler
#
#--------------------------------------------------------------------------
VPATH = ui/

UI_FILES = $(patsubst ui/%.ui, %_ui.py, $(wildcard ui/*.ui))

RESOURCE_FILES = $(patsubst ui/%.qrc, %_rc.py, $(wildcard ui/*.qrc))

default: compile

compile: $(UI_FILES) $(RESOURCE_FILES)

%_rc.py : %.qrc
	c:\Python27\Lib\site-packages\PySide\pyside-rcc -o $@  $<

%_ui.py : %.ui
	c:\Python27\scripts\pyside-uic -o $@ $<

clean:
	del *_ui.py
	del *_rc.py
	del *.pyc
