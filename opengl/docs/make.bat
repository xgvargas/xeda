@echo off

if "%1" == "full" goto full

%VIRTUAL_ENV%\Scripts\sphinx-build.exe -b html -d _out\_doctree . _out\html
goto end

:full

rd /s /q _tmp
%VIRTUAL_ENV%\Scripts\sphinx-apidoc.exe -o _tmp -T -f ..

del _tmp\*_ui.rst
del _tmp\*_rc.rst
del _tmp\*_lex.rst
del _tmp\*_tab.rst

echo Modules > modules.rst
echo ======= >> modules.rst
echo. >> modules.rst
echo .. toctree:: >> modules.rst
echo     :maxdepth: 4 >> modules.rst
echo. >> modules.rst

for %%F in (_tmp\*.rst) do (
    echo %%~nF module > %%~nF.rst
    echo =================================== >> %%~nF.rst
    echo. >> %%~nF.rst
    echo .. automodule:: %%~nF >> %%~nF.rst
    echo     %%~nF >> modules.rst
)

rd /s/q _tmp
rd /s/q _out\html

%VIRTUAL_ENV%\Scripts\sphinx-build.exe -b html -v -a -E -d _out\_doctree . _out\html

:end
