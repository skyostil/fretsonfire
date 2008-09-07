#####################################################################
# -*- coding: iso-8859-1 -*-                                        #
#                                                                   #
# Frets on Fire                                                     #
# Copyright (C) 2006 Sami Kyöstilä                                  #
#                                                                   #
# This program is free software; you can redistribute it and/or     #
# modify it under the terms of the GNU General Public License       #
# as published by the Free Software Foundation; either version 2    #
# of the License, or (at your option) any later version.            #
#                                                                   #
# This program is distributed in the hope that it will be useful,   #
# but WITHOUT ANY WARRANTY; without even the implied warranty of    #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the     #
# GNU General Public License for more details.                      #
#                                                                   #
# You should have received a copy of the GNU General Public License #
# along with this program; if not, write to the Free Software       #
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,        #
# MA  02110-1301, USA.                                              #
#####################################################################

# Keyboard Hero setup script
from distutils.core import setup
import sys, SceneFactory, Version, glob, os

try:
  import py2exe
except ImportError:
  pass

options = {
  "py2exe": {
    "dist_dir":  "../dist",
    "includes":  SceneFactory.scenes,
    "excludes":  [
      "OpenGL",   # OpenGL must be excluded and handled manually due to a py2exe bug
      "glew.gl.apple",
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
      "_ssl",
      "bz2",
      "email",
      "calendar",
      "doctest",
      "ftplib",
      "getpass",
      "gopherlib",
      "macpath",
      "macurl2path",
      "GimpGradientFile",
      "GimpPaletteFile",
      "PaletteFile",
      "macosx",
      "matplotlib",
      "Tkinter",
      "curses",
    ],
    "optimize":  2,
  }
}

dataFiles = [
  "default.ttf",
  "title.ttf",
  "international.ttf",
  "keyboard.png",
  "cassette.png",
  "editor.png",
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
  "star1.png",
  "star2.png",
  "glow.png",
  "ball1.png",
  "ball2.png",
  "left.png",
  "right.png",
  "fiba1.ogg",
  "fiba2.ogg",
  "fiba3.ogg",
  "fiba4.ogg",
  "fiba5.ogg",
  "fiba6.ogg",
  "neck.png",
  "pose.png",
  "logo.png",
  "menu.ogg",  
  "2x.png",  
  "3x.png",  
  "4x.png",
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
  "ghmidimap.txt",
  "stage_background.png",
  "stage_audience1.png",
  "stage_audience2.png",
  "stage_drums.png",
  "stage_bassdrum.png",
  "stage_light.png",
  "stage_lights1.png",
  "stage_lights2.png",
  "stage_speakers.png",
  "stage_speaker_cones.png",
  "stage.ini",
  "loading.png",
  "bar.png",
  "string.png",
  "note.png"
]

chillyModFiles = [
  "mods/Chilly/theme.ini",
  "mods/Chilly/flame1.png",
  "mods/Chilly/flame2.png",
  "mods/Chilly/logo.png",
  "mods/Chilly/neck.png"
]

lightModFiles = [
  "mods/LightGraphics/stage.ini",
  "mods/LightGraphics/2x.png",
  "mods/LightGraphics/3x.png",
  "mods/LightGraphics/4x.png",
  "mods/LightGraphics/ball1.png",
  "mods/LightGraphics/ball2.png",
  "mods/LightGraphics/cassette.png",
  "mods/LightGraphics/editor.png",
  "mods/LightGraphics/flame1.png",
  "mods/LightGraphics/flame2.png",
  "mods/LightGraphics/glow.png",
  "mods/LightGraphics/keyboard.png",
  "mods/LightGraphics/left.png",
  "mods/LightGraphics/light.png",
  "mods/LightGraphics/loading.png",
  "mods/LightGraphics/logo.png",
  "mods/LightGraphics/neck.png",
  "mods/LightGraphics/pose.png",
  "mods/LightGraphics/right.png",
  "mods/LightGraphics/star1.png",
  "mods/LightGraphics/star2.png",
  "mods/LightGraphics/star.png",
  "mods/LightGraphics/2x.png",
  "mods/LightGraphics/3x.png",
  "mods/LightGraphics/4x.png",
  "mods/LightGraphics/ball1.png",
  "mods/LightGraphics/ball2.png",
  "mods/LightGraphics/cassette.png",
  "mods/LightGraphics/editor.png",
  "mods/LightGraphics/flame1.png",
  "mods/LightGraphics/flame2.png",
  "mods/LightGraphics/glow.png",
  "mods/LightGraphics/keyboard.png",
  "mods/LightGraphics/left.png",
  "mods/LightGraphics/light.png",
  "mods/LightGraphics/loading.png",
  "mods/LightGraphics/logo.png",
  "mods/LightGraphics/neck.png",
  "mods/LightGraphics/pose.png",
  "mods/LightGraphics/right.png",
  "mods/LightGraphics/star1.png",
  "mods/LightGraphics/star2.png",
  "mods/LightGraphics/star.png"
]

dataFiles      = ["../data/" + f for f in dataFiles]
chillyModFiles = ["../data/" + f for f in chillyModFiles]
lightModFiles  = ["../data/" + f for f in lightModFiles]

def songFiles(song, extra = []):
  return ["../data/songs/%s/%s" % (song, f) for f in ["guitar.ogg", "notes.mid", "song.ini", "song.ogg"] + extra]

dataFiles = [
  (".", ["../readme.txt",     "../copying.txt"]),
  ("data",                    dataFiles),
  ("data/songs/defy",         songFiles("defy", ["label.png"])),
  ("data/songs/bangbang",     songFiles("bangbang", ["label.png"])),
  ("data/songs/twibmpg",      songFiles("twibmpg", ["label.png"])),
  ("data/songs/tutorial",     songFiles("tutorial", ["esc.png", "keyboard.png", "script.txt", "pose.png"])),
  ("data/mods/Chilly",        chillyModFiles),
  ("data/mods/LightGraphics", lightModFiles),
  ("data/translations",       glob.glob("../data/translations/*.mo")),
]

if os.name == "nt":
  setup(version = Version.version(),
        description = "Rockin' it Oldskool!",
        name = "Frets on Fire",
        url = "http://www.unrealvoodoo.org",
        windows = [
          {
            "script":          "FretsOnFire.py",
            "icon_resources":  [(1, "../data/icon.ico")]
          }
        ],
        zipfile = "data/library.zip",
        data_files = dataFiles,
        options = options)
else:
  setup(version = Version.version(),
        description = "Rockin' it Oldskool!",
        name = "Frets on Fire",
        url = "http://www.unrealvoodoo.org",
        data_files = dataFiles,
        options = options)

