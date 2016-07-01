#--------------------------------------------------------------------------
#
#    Makefile for PySide
#
#--------------------------------------------------------------------------


# UIC = c:\Python27\scripts\pyside-uic
# RCC = c:\Python27\Lib\site-packages\PySide\pyside-rcc
# LUP = c:\Python27\Lib\site-packages\PySide\lupdate
# LRL = c:\Python27\Lib\site-packages\PySide\lrelease

UIC = $(VIRTUAL_ENV)\Scripts\pyside-uic
RCC = $(VIRTUAL_ENV)\Lib\site-packages\PySide\pyside-rcc -py3
LUP = $(VIRTUAL_ENV)\Lib\site-packages\PySide\pyside-lupdate
LRL = $(VIRTUAL_ENV)\Lib\site-packages\PySide\lrelease


#--------------------------------------------------------------------------
VPATH = ui/

UI_FILES = $(patsubst ui/%.ui, %_ui.py, $(wildcard ui/*.ui))

RESOURCE_FILES = $(patsubst ui/%.qrc, %_rc.py, $(wildcard ui/*.qrc))

IMAGE_FILES = $(patsubst ui/%.svg, ui/%.extracted, $(wildcard ui/*.svg))

TRANSLATION_FILES = $(patsubst i18n/%.ts, i18n/%.qm, $(wildcard i18n/*.ts))

default: $(UI_FILES) $(RESOURCE_FILES) $(TRANSLATION_FILES) ui\exeicon.ico

.SECONDARY: $(IMAGE_FILES)

%.extracted : %.svg
	bash d:\bin\svg-extract.sh -f -o ui -s $@ $<

%_rc.py : %.qrc $(IMAGE_FILES)
	$(RCC) -o $@ $<

%_ui.py : %.ui
	$(UIC) -o $@ $<

%.qm : %.ts
	$(LRL) $< -qm $@

ui\exeicon.ico : ui/icon.extracted
#	curl -X POST -F "key=df23zr!4" -F "MAX_FILE_SIZE=3072000" -F "sizes[]=16" -F "sizes[]=32" -F "sizes[]=48" -F "bpp=32" -F "image=@ui/icon256.png;type=image/png;filename=icon256.png" -o ui\exeicon.ico http://www.icoconverter.com/index.php
	echo -e "from PIL import Image\na=Image.open('ui/icon256.png')\na.save('ui/exeicon.ico', sizes=[(16,16), (32, 32), (48, 48)])" | c:/python27/python

clean:
	-rm *_ui.py *_rc.py *.pyc *_lex.py *_tab.py stack.dat
	-rm i18n/*.qm
	-rm -r __pycache__
	-cat ui/*.extracted | xargs rm.exe
	-rm ui/*.extracted ui/exeicon.ico

.PHONY: images dist update

images: $(IMAGE_FILES)

dist:
# versao usando o Esky
	-rm -r dist
	python setup-esky.py bdist_esky
	"c:\Program Files\7-Zip\7z.exe" x -odist\pack dist\*.zip
	"$(ProgramFilesX86)\Inno Setup 5\ISCC.exe" setup.iss

# versao do cx-freeze
# .............

update:
	$(LUP) -verbose -noobsolete $(wildcard i18n/*.pro)
