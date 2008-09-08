#!/usr/bin/python
# -*- coding: iso-8859-1 -*-
#####################################################################
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

"""
Main game executable.
"""
import sys
import os

# This trickery is needed to get OpenGL 3.x working with py2exe
if hasattr(sys, "frozen") and os.name == "nt":
  import ctypes
  from ctypes import util
  sys.path.insert(0, "data/PyOpenGL-3.0.0a5-py2.5.egg")
  sys.path.insert(0, "data/setuptools-0.6c8-py2.5.egg")

# Register the latin-1 encoding
import codecs
import encodings.iso8859_1
import encodings.utf_8
codecs.register(lambda encoding: encodings.iso8859_1.getregentry())
codecs.register(lambda encoding: encodings.utf_8.getregentry())
assert codecs.lookup("iso-8859-1")
assert codecs.lookup("utf-8")

from GameEngine import GameEngine
from MainMenu import MainMenu
import Log
import Config
import Version
import getopt

usage = """%(prog)s [options]
Options:
  --verbose, -v         Verbose messages
  --play, -p [songName] Start playing the given song
""" % {"prog": sys.argv[0] }

if __name__ == "__main__":
  try:
    opts, args = getopt.getopt(sys.argv[1:], "vp:", ["verbose", "play="])
  except getopt.GetoptError:
    print usage
    sys.exit(1)

  songName = None
  for opt, arg in opts:
    if opt in ["--verbose", "-v"]:
      Log.quiet = False
    elif opt in ["--play", "-p"]:
      songName = arg

  while True:
    config = Config.load(Version.appName() + ".ini", setAsDefault = True)
    engine = GameEngine(config)
    menu   = MainMenu(engine, songName = songName)
    engine.setStartupLayer(menu)

    try:
      import psyco
      psyco.profile()
    except:
      Log.warn("Unable to enable psyco.")

    try:
      while engine.run():
        pass
    except KeyboardInterrupt:
        pass

    if engine.restartRequested:
      Log.notice("Restarting.")

      try:
        # Determine whether were running from an exe or not
        if hasattr(sys, "frozen"):
          if os.name == "nt":
            os.execl("FretsOnFire.exe", "FretsOnFire.exe", *sys.argv[1:])
          else:
            os.execl("./FretsOnFire", "./FretsOnFire", *sys.argv[1:])
        else:
          if os.name == "nt":
            bin = "c:/python25/python"
          else:
            bin = "/usr/bin/python"
          os.execl(bin, bin, "FretsOnFire.py", *sys.argv[1:])
      except:
        Log.warn("Restart failed.")
        raise
      break
    else:
      break
  engine.quit()
