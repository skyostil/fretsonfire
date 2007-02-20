PYTHON=c:/apps/actpython/python

all:	dist

dist:
	@echo --- Building EXE
	@cd src ; $(PYTHON) setup.py py2exe ; cd ..

	@echo --- Fixing PyOpenGL
	@cd dist/data ; \
        mkdir OpenGL ; \
        cp ../../data/PyOpenGL__init__.pyc OpenGL/__init__.pyo ; \
        zip library.zip OpenGL/__init__.pyo ; \
        rm -rf OpenGL ; \
        cd ../../

	@echo --- Removing useless stuff
	@rm dist/w9xpopen.exe

	@echo --- Adding missing stuff
	cp /c/winnt/system32/msvcp71.dll dist

	@echo --- Fixing text files
	@unix2dos dist/readme.txt
	@unix2dos dist/copying.txt

run:	dist
	@cd dist ; ./KeyboardHero.exe ; cd ..

clean:
	@rm -rf dist build

.PHONY: dist

