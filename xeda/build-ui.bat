for %%R in (ui\*.ui) do c:\Python27\scripts\pyside-uic %%R -o %%~nR_ui.py
for %%R in (ui\*.qrc) do c:\Python27\Lib\site-packages\PySide\pyside-rcc %%R -o %%~nR_rc.py
