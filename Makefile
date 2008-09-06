TOP=.
CXFREEZE=/c/cygwin/home/sami/proj/cx_Freeze-3.0.3/FreezePython
PYTHON=python
PYTHON_LIBS=/c/apps/actpython/lib
MAKENSIS=/c/Program\ Files/NSIS/makeNSIS.exe

include data/Makefile

all:	dist

dist: graphics
	@echo --- Building EXE
	$(CXFREEZE) --target-dir dist --base-name=Win32GUI.exe --include-modules \
encodings.string_escape,\
encodings.iso8859_1,\
OpenGL.arrays.numpymodule,\
OpenGL.arrays.ctypesarrays,\
OpenGL.arrays.ctypespointers,\
OpenGL.arrays.strings,\
OpenGL.arrays.numbers,\
OpenGL.arrays.nones,\
SongChoosingScene,\
GuitarScene,\
GameResultsScene --exclude-modules matplotlib,Tkinter src/FretsOnFire.py

	@echo --- Copying data
	cd src; $(PYTHON) setup.py install_data --install-dir ../dist ; cd ..

	@echo --- Fixing PyOpenGL-ctypes
	mkdir -p dist/OpenGL-3.0.0a4-py2.4.egg-info
	cp -Lr $(PYTHON_LIBS)/site-packages/OpenGL-3.0.0a4-py2.4.egg/EGG-INFO/* dist/OpenGL-3.0.0a4-py2.4.egg-info

	@echo --- Adding missing stuff
	cp data/win32/lib/*.dll \
	   data/icon.ico \
  	 dist

	@echo --- Fixing text files
	@unix2dos dist/readme.txt
	@unix2dos dist/copying.txt

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

