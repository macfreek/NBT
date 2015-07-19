#!/bin/sh
pychecker -#200 -q examples/*.py tests/*.py nbt doc/sphinxext/restbuilder.py
pyflakes nbt examples tests doc/sphinxext
pep8 --ignore=W191,E101,W191,E225,E501 nbt examples tests doc/sphinxext