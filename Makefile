TOP=.
PYTHON=python
PYTHON_LIBS=c:/python25/lib
MAKENSIS=/c/Program\ Files/NSIS/makeNSIS.exe

include data/Makefile

all:	dist

dist: graphics
	@echo --- Compiling
	cd src; $(PYTHON) setup.py py2exe; cd ..

	@echo --- Fixing PyOpenGL-ctypes
	cp -Lr $(PYTHON_LIBS)/site-packages/PyOpenGL-3.0.0a5-py2.5.egg dist/data
	cp -Lr $(PYTHON_LIBS)/site-packages/setuptools-0.6c8-py2.5.egg dist/data

	@echo --- Fixing miscellaneous things
	@unix2dos dist/readme.txt
	@unix2dos dist/copying.txt
	@rm -f dist/w9xpopen.exe

installer: dist
	@echo --- Making installer
	mkdir -p dist/installer
	cp data/win32/installer/FretsOnFire.nsi dist/installer
	$(MAKENSIS) dist/installer/FretsOnFire.nsi

run:	dist
	@cd dist ; ./FretsOnFire.exe ; cd ..

clean:
	@rm -rf dist build

.PHONY: dist installer

