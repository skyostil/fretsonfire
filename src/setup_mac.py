"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

import sys, SceneFactory, Version
import amanith

APP = ['FretsOnFire.py']
dataFiles = [
  "default.ttf",
  "title.ttf",
  "international.ttf",
  "keyboard.svg",
  "cassette.svg",
  "editor.svg",
  "key.dae",
  "note.dae",
  "cassette.dae",
  "label.dae",
  "library.dae",
  "library_label.dae",
  "crunch1.ogg",
  "crunch2.ogg",
  "crunch3.ogg",
  "out.ogg",
  "start.ogg",
  "in.ogg",
  "star1.svg",
  "star2.svg",
  "glow.svg",
  "ball1.svg",
  "ball2.svg",
  "left.svg",
  "right.svg",
  "fiba1.ogg",
  "fiba2.ogg",
  "fiba3.ogg",
  "fiba4.ogg",
  "fiba5.ogg",
  "fiba6.ogg",
  "neck.svg",
  "pose.svg",
  "logo.svg",
  "menu.ogg",  
  "2x.svg",  
  "3x.svg",  
  "4x.svg",
  "perfect1.ogg",
  "perfect2.ogg",
  "perfect3.ogg",
  "myhero.ogg",
  "jurgen1.ogg",
  "jurgen2.ogg",
  "jurgen3.ogg",
  "jurgen4.ogg",
  "jurgen5.ogg",
  "icon.png",
  "flame1.svg",
  "flame2.svg",
  "ghmidimap.txt",
]

modFiles = [
  "mods/Chilly/theme.ini",
  "mods/Chilly/flame1.svg",
  "mods/Chilly/flame2.svg",
  "mods/Chilly/logo.svg",
  "mods/Chilly/neck.svg",
]

dataFiles = ["../data/" + f for f in dataFiles]
modFiles =  ["../data/" + f for f in modFiles]

def songFiles(song, extra = []):
  return ["../data/songs/%s/%s" % (song, f) for f in ["guitar.ogg", "notes.mid", "song.ini", "song.ogg"] + extra]

dataFiles = [
  (".", ["../readme.txt", "../copying.txt"]),
  ("data", dataFiles),
  ("data/songs/defy",     songFiles("defy", ["label.png"])),
  ("data/songs/bangbang", songFiles("bangbang", ["label.png"])),
  ("data/songs/twibmpg",  songFiles("twibmpg", ["label.png"])),
  ("data/songs/tutorial", songFiles("tutorial", ["esc.svg", "keyboard.svg", "script.txt", "pose.svg"])),
  ("data/mods/Chilly",    modFiles),
  ("data/translations",   glob.glob("../data/translations/*.mo")),
]

OPTIONS = {
 'argv_emulation': True,
 'dist_dir': '../dist',
 'dylib_excludes': 'OpenGL,AGL',
 'frameworks' : '../../amanith/lib/libamanith.dylib, ../../glew/lib/libGLEW.dylib', 
 'iconfile': '../data/icon_mac_composed.icns',
 'includes': SceneFactory.scenes + ['amanith'],
 'excludes': ['glew.gl.apple'
      "glew.gl.ati",
      "glew.gl.atix",
      "glew.gl.hp",
      "glew.gl.ibm",
      "glew.gl.ingr",
      "glew.gl.intel",
      "glew.gl.ktx",
      "glew.gl.mesa",
      "glew.gl.oml",
      "glew.gl.pgi",
      "glew.gl.rend",
      "glew.gl.s3",
      "glew.gl.sgi",
      "glew.gl.sgis",
      "glew.gl.sgix",
      "glew.gl.sun",
      "glew.gl.sunx",
      "glew.gl.threedfx",
      "glew.gl.win",
      "ode",
      "unicodedata",
      "_ssl",
      "bz2",
      "email",
      "calendar",
      "bisect",
      "difflib",
#      "dis",
      "doctest",
      "ftplib",
      "getpass",
      "gopherlib",
      "heapq",
#      "inspect",
#      "locale",
      "macpath",
      "macurl2path",
      "GimpGradientFile",
      "GimpPaletteFile",
      "PaletteFile"
 ]
}

setup(
    version=Version.version(),
    description="Rockin' it Oldskool!",
    name="Frets on Fire",
    url="http://www.unrealvoodoo.org",
    app=APP,
    data_files=dataFiles,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
