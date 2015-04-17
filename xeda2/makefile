#--------------------------------------------------------------------------
#
#    Makefile for PySide
#
#--------------------------------------------------------------------------


UIC = c:\Python27\scripts\pyside-uic
# UIC = venv\Scripts\pyside-uic

RCC = c:\Python27\Lib\site-packages\PySide\pyside-rcc
# RCC = venv\Lib\site-packages\PySide\pyside-rcc -py3

NIX = $(ProgramFilesX86)\git\bin


#--------------------------------------------------------------------------
VPATH = ui/

UI_FILES = $(patsubst ui/%.ui, %_ui.py, $(wildcard ui/*.ui))

RESOURCE_FILES = $(patsubst ui/%.qrc, %_rc.py, $(wildcard ui/*.qrc))

IMAGE_FILES = $(patsubst ui/%.svg, ui/%.extracted, $(wildcard ui/*.svg))

default: compile

compile: $(UI_FILES) $(RESOURCE_FILES)


.SECONDARY: $(IMAGE_FILES)

%.extracted : %.svg
	$(NIX)\bash.exe d:\bin\svg-extract.sh -f -o ui -s $@ $<

%_rc.py : %.qrc $(IMAGE_FILES)
	$(RCC) -o $@ $<

%_ui.py : %.ui
	$(UIC) -o $@ $<

clean:
	del *_ui.py
	del *_rc.py
	del *.pyc
	-rd /s /q __pycache__
	-$(NIX)\cat ui/*.extracted | $(NIX)\xargs $(NIX)\rm.exe
	del ui\*.extracted

.PHONY: images dist

images: $(IMAGE_FILES)

dist:
#	python setup-2exe.py
	python setup-cx.py build
#	python setup-cx.py bdist_msi
	"$(ProgramFilesX86)\Inno Setup 5\ISCC.exe" setup.iss
