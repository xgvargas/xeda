..\..\venv\Scripts\sphinx-apidoc.exe -o . -f ..

more +2 modules.rst > modules.rst.tmp
echo Modules > modules.rst
echo ======= >> modules.rst
type modules.rst.tmp >> modules.rst
del modules.rst.tmp

..\..\venv\Scripts\sphinx-build.exe -b html -v -a -E -d _out\_doctree . _out\html
