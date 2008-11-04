NOTE: The following is mostly for historical interest, as it concerns an old version of the game.


Readme for building and packing Frets on Fire and components on Mac OS X.

********************************************************************************
1. Requirements
********************************************************************************

- MacPython 2.4 (Assumed by this document to be in 
/Library/Frameworks/Python.framework/Versions/Current, not a required location)
- XCode 2.4 or better for building universal apps/libs
- py2app (http://undefined.org/python/)
- The external libraries may require additional resources that are not listed
here. To fix these, install DarwinPorts, and - whenever the system complains
about a missing libary/resource - type:

sudo port install <library_name>, e.g.,
sudo port install zlib

- OpenGL.framework
- AGL.framework

- All the FretsOnFire requirements

********************************************************************************
2. Externals
********************************************************************************

All the stuff should be located under a single folder. For example:

~/Projects/FretsOnFire/

~/Projects/glew/
~/Projects/amanith/
~/Projects/PyAmanith/

--------------------------------------------------------------------------------
2.1. GLEW (universal)

The version in the Internet at the time of building this was not compatible with
Intel Macs. The XCode project in glew/GLEW is used to build libGLEW.dylib into
glew/lib, and it will use OpenGL.framework and AGL.framework.

Copy GLEW into glew. Build XCode project. The results should be
glew/lib/libGLEW.dylib

If something fails later on in the process concerning this lib, copy to
/usr/local/lib (or wherever your system knows where to look for dylibs)

--------------------------------------------------------------------------------
2.2. amanith (universal)

XCode project for building universal dylib should be placed into amanith/amanith
folder. Uses single-precision floating-point.

Copy amanith as amanith/amanith. Build XCode project. The result should be
amanith/lib/libamanith.dylib

If something fails later on in the process concerning this lib, copy to
/usr/local/lib (or wherever your system knows where to look for dylibs)

--------------------------------------------------------------------------------
2.3. PyAmanith (universal)

Copy the files in MacSupport/PyAmanith.../ - folder over the ones in the 
original bundle. (This will change the doubles to floats). Then run:

python setup_mac.py build

and/or

python setup_mac.py install

The result should be: 
/Library/Frameworks/Python.framework/Versions/Current/lib/
python2.4/site-packages/_amanith.so, .../amanith.py, and .../amanith.pyc

--------------------------------------------------------------------------------
2.4. macholib

Adds a feature to macholib (LC_UUID support).

- Install py2app from the Internet (http://undefined.org/python/)
- python setup.py install

Should replace any existing macholib. Check the python site-packages folder.

********************************************************************************
3. Frets On Fire
********************************************************************************

Changes to Mac build:

- src/Audio.py: Added the pre_open - stuff
- src/GameEngine.py: pre_open - stuff usage detected from platform
- src/setup_mac.py
- data/icon_mac_composed.icns
- data/icon_mac.tiff
- data/icon_mac.svg

--------------------------------------------------------------------------------
3.1. Building

python setup_mac.py py2app

********************************************************************************
4. Help
********************************************************************************

- Download latest Mac revision of the FretsOnFire source code, and see if the
problem goes away.
- Visit the Frets on Fire website and forums for troubleshooting info.
- tero<dot>pihlajakoski<at>gmail<dot>com.
