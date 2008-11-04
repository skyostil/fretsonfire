#
# Frets on Fire Makefile
#
TOP=.
PYTHON=python
PLATFORM=$(shell uname)

include data/Makefile

all:	dist

#
# Win32 binary & installer
#
ifneq "$(findstring Windows_NT, $(OS))" ""
PYTHON_LIBS=c:/python25/lib
MAKENSIS=/c/Program\ Files/NSIS/makeNSIS.exe

dist: graphics translations killscores
	@echo --- Compiling for win32
	$(PYTHON) setup.py sdist -o
	$(PYTHON) setup.py py2exe

	@echo --- Fixing PyOpenGL-ctypes
	cp -Lr $(PYTHON_LIBS)/site-packages/PyOpenGL-3.0.0a5-py2.5.egg dist/win32/data
	cp -Lr $(PYTHON_LIBS)/site-packages/setuptools-0.6c8-py2.5.egg dist/win32/data

	@echo --- Fixing miscellaneous things
	@unix2dos dist/win32/readme.txt
	@unix2dos dist/win32/copying.txt
	@unix2dos dist/win32/install.txt
	@rm -f dist/win32/w9xpopen.exe

installer: dist
	@echo --- Making installer for win32
	mkdir -p dist/win32/installer
	cp data/win32/installer/* dist/win32/installer
	$(MAKENSIS) dist/win32/installer/FretsOnFire.nsi
endif

ifneq "$(findstring Darwin, $(PLATFORM))" ""
dist: graphics translations killscores
	@echo --- Compiling for macosx
	#$(PYTHON) setup.py sdist -o
	$(PYTHON) setup.py py2app

	@echo --- Fixing miscellaneous things
	mv "dist/mac/Frets on Fire.app/Contents/MacOS/Frets on Fire" "dist/mac/Frets on Fire.app/Contents/MacOS/FretsOnFire.bin"
	cp data/launcher-macosx.sh "dist/mac/Frets on Fire.app/Contents/MacOS/Frets on Fire"
endif

sdist: graphics translations killscores
	$(PYTHON) setup.py sdist

clean:
	@rm -rf dist build

.PHONY: dist installer sdist

