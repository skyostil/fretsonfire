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

from OpenGL.GL import *
import pygame
import os
import sys

from Engine import Engine, Task
from Video import Video
from Audio import Audio
from View import View
from Input import Input, KeyListener, SystemEventListener
from Resource import Resource
from Data import Data
from Server import Server
from Session import ClientSession
from Svg import SvgContext, SvgDrawing, LOW_QUALITY, NORMAL_QUALITY, HIGH_QUALITY
from Debug import DebugLayer
from Language import _
import Network
import Log
import Config
import Dialogs
import Theme
import Version
import Mod

# define configuration keys
Config.define("engine", "tickrate",     float, 1.0)
Config.define("engine", "highpriority", bool,  True)
Config.define("game",   "uploadscores", bool,  False, text = _("Upload Highscores"),    options = {False: _("No"), True: _("Yes")})
Config.define("game",   "uploadurl",    str,   "http://fretsonfire.sourceforge.net/play")
Config.define("game",   "leftymode",    bool,  False, text = _("Lefty mode"),           options = {False: _("No"), True: _("Yes")})
Config.define("game",   "tapping",      bool,  True,  text = _("Tappable notes"),       options = {False: _("No"), True: _("Yes")})
Config.define("video",  "fullscreen",   bool,  False, text = _("Fullscreen Mode"),      options = {False: _("No"), True: _("Yes")})
Config.define("video",  "multisamples", int,   4,     text = _("Antialiasing Quality"), options = {0: _("None"), 2: _("2x"), 4: _("4x"), 6: _("6x"), 8: _("8x")})
Config.define("video",  "resolution",   str,   "640x480")
Config.define("video",  "fps",          int,   80,    text = _("Frames per Second"), options = dict([(n, n) for n in range(1, 120)]))
#Config.define("opengl", "svgquality",   int,   NORMAL_QUALITY,  text = _("SVG Quality"), options = {LOW_QUALITY: _("Low"), NORMAL_QUALITY: _("Normal"), HIGH_QUALITY: _("High")})
Config.define("audio",  "frequency",    int,   44100, text = _("Sample Frequency"), options = [8000, 11025, 22050, 32000, 44100, 48000])
Config.define("audio",  "bits",         int,   16,    text = _("Sample Bits"), options = [16, 8])
Config.define("audio",  "stereo",       bool,  True)
Config.define("audio",  "buffersize",   int,   2048,  text = _("Buffer Size"), options = [256, 512, 1024, 2048, 4096, 8192, 16384, 32768, 65536])
Config.define("audio",  "delay",        int,   100,   text = _("A/V delay"), options = dict([(n, n) for n in range(0, 301)]))
Config.define("audio",  "screwupvol", float,   0.25,  text = _("Screw Up Sounds"), options = {0.0: _("Off"), .25: _("Quiet"), .5: _("Loud"), 1.0: _("Painful")})
Config.define("audio",  "guitarvol",  float,    1.0,  text = _("Guitar Volume"),   options = dict([(n / 100.0, "%02d/10" % (n / 9)) for n in range(0, 110, 10)]))
Config.define("audio",  "songvol",    float,    1.0,  text = _("Song Volume"),     options = dict([(n / 100.0, "%02d/10" % (n / 9)) for n in range(0, 110, 10)]))
Config.define("audio",  "rhythmvol",  float,    1.0,  text = _("Rhythm Volume"),   options = dict([(n / 100.0, "%02d/10" % (n / 9)) for n in range(0, 110, 10)]))
Config.define("video",  "fontscale",  float,    1.0,  text = _("Text scale"),      options = dict([(n / 100.0, "%3d%%" % n) for n in range(50, 260, 10)]))

class FullScreenSwitcher(KeyListener):
  """
  A keyboard listener that looks for special built-in key combinations,
  such as the fullscreen toggle (Alt-Enter).
  """
  def __init__(self, engine):
    self.engine = engine
    self.altStatus = False
  
  def keyPressed(self, key, unicode):
    if key == pygame.K_LALT:
      self.altStatus = True
    elif key == pygame.K_RETURN and self.altStatus:
      if not self.engine.toggleFullscreen():
        Log.error("Unable to toggle fullscreen mode.")
      return True
    elif key == pygame.K_d and self.altStatus:
      self.engine.setDebugModeEnabled(not self.engine.isDebugModeEnabled())
      return True
    elif key == pygame.K_g and self.altStatus and self.engine.isDebugModeEnabled():
      self.engine.debugLayer.gcDump()
      return True

  def keyReleased(self, key):
    if key == pygame.K_LALT:
      self.altStatus = False
      
class SystemEventHandler(SystemEventListener):
  """
  A system event listener that takes care of restarting the game when needed
  and reacting to screen resize events.
  """
  def __init__(self, engine):
    self.engine = engine

  def screenResized(self, size):
    self.engine.resizeScreen(size[0], size[1])
    
  def restartRequested(self):
    self.engine.restart()
    
  def quit(self):
    self.engine.quit()

class GameEngine(Engine):
  """The main game engine."""
  def __init__(self, config = None):
    """
    Constructor.

    @param config:  L{Config} instance for settings
    """

    if not config:
      config = Config.load()
      
    self.config  = config
    
    fps          = self.config.get("video", "fps")
    tickrate     = self.config.get("engine", "tickrate")
    Engine.__init__(self, fps = fps, tickrate = tickrate)
    
    pygame.init()
    
    self.title             = _("Frets on Fire")
    self.restartRequested  = False
    self.handlingException = False
    self.video             = Video(self.title)
    self.audio             = Audio()

    Log.debug("Initializing audio.")
    frequency    = self.config.get("audio", "frequency")
    bits         = self.config.get("audio", "bits")
    stereo       = self.config.get("audio", "stereo")
    bufferSize   = self.config.get("audio", "buffersize")
    
    self.audio.pre_open(frequency = frequency, bits = bits, stereo = stereo, bufferSize = bufferSize)
    pygame.init()
    self.audio.open(frequency = frequency, bits = bits, stereo = stereo, bufferSize = bufferSize)

    Log.debug("Initializing video.")
    width, height = [int(s) for s in self.config.get("video", "resolution").split("x")]
    fullscreen    = self.config.get("video", "fullscreen")
    multisamples  = self.config.get("video", "multisamples")
    self.video.setMode((width, height), fullscreen = fullscreen, multisamples = multisamples)

    # Enable the high priority timer if configured
    if self.config.get("engine", "highpriority"):
      Log.debug("Enabling high priority timer.")
      self.timer.highPriority = True

    viewport = glGetIntegerv(GL_VIEWPORT)
    h = viewport[3] - viewport[1]
    w = viewport[2] - viewport[0]
    geometry = (0, 0, w, h)
    self.svg = SvgContext(geometry)
    self.svg.setRenderingQuality(self.config.get("opengl", "svgquality"))
    glViewport(int(viewport[0]), int(viewport[1]), int(viewport[2]), int(viewport[3]))

    self.input     = Input()
    self.view      = View(self, geometry)
    self.resizeScreen(w, h)

    self.resource  = Resource(Version.dataPath())
    self.server    = None
    self.sessions  = []
    self.mainloop  = self.loading
    
    # Load game modifications
    Mod.init(self)
    theme = Config.load(self.resource.fileName("theme.ini"))
    Theme.open(theme)

    # Make sure we are using the new upload URL
    if self.config.get("game", "uploadurl").startswith("http://kempele.fi"):
      self.config.set("game", "uploadurl", "http://fretsonfire.sourceforge.net/play")

    self.addTask(self.audio, synchronized = False)
    self.addTask(self.input, synchronized = False)
    self.addTask(self.view)
    self.addTask(self.resource, synchronized = False)
    self.data = Data(self.resource, self.svg)
    
    self.input.addKeyListener(FullScreenSwitcher(self), priority = True)
    self.input.addSystemEventListener(SystemEventHandler(self))

    self.debugLayer         = None
    self.startupLayer       = None
    self.loadingScreenShown = False

    Log.debug("Ready.")

  def setStartupLayer(self, startupLayer):
    """
    Set the L{Layer} that will be shown when the all
    the resources have been loaded. See L{Data}

    @param startupLayer:    Startup L{Layer}
    """
    self.startupLayer = startupLayer

  def isDebugModeEnabled(self):
    return bool(self.debugLayer)
    
  def setDebugModeEnabled(self, enabled):
    """
    Show or hide the debug layer.

    @type enabled: bool
    """
    if enabled:
      self.debugLayer = DebugLayer(self)
    else:
      self.debugLayer = None
    
  def toggleFullscreen(self):
    """
    Toggle between fullscreen and windowed mode.

    @return: True on success
    """
    if not self.video.toggleFullscreen():
      # on windows, the fullscreen toggle kills our textures, se we must restart the whole game
      self.input.broadcastSystemEvent("restartRequested")
      self.config.set("video", "fullscreen", not self.video.fullscreen)
      return True
    self.config.set("video", "fullscreen", self.video.fullscreen)
    return True
    
  def restart(self):
    """Restart the game."""
    if not self.restartRequested:
      self.restartRequested = True
      self.input.broadcastSystemEvent("restartRequested")
    else:
      self.quit()
    
  def quit(self):
    self.audio.close()
    Engine.quit(self)

  def resizeScreen(self, width, height):
    """
    Resize the game screen.

    @param width:   New width in pixels
    @param height:  New height in pixels
    """
    self.view.setGeometry((0, 0, width, height))
    self.svg.setGeometry((0, 0, width, height))
    
  def isServerRunning(self):
    return bool(self.server)

  def startServer(self):
    """Start the game server."""
    if not self.server:
      Log.debug("Starting server.")
      self.server = Server(self)
      self.addTask(self.server, synchronized = False)

  def connect(self, host):
    """
    Connect to a game server.

    @param host:  Name of host to connect to
    @return:      L{Session} connected to remote server
    """
    Log.debug("Connecting to host %s." % host)
    session = ClientSession(self)
    session.connect(host)
    self.addTask(session, synchronized = False)
    self.sessions.append(session)
    return session

  def stopServer(self):
    """Stop the game server."""
    if self.server:
      Log.debug("Stopping server.")
      self.removeTask(self.server)
      self.server = None

  def disconnect(self, session):
    """
    Disconnect a L{Session}

    param session:    L{Session} to disconnect
    """
    if session in self.sessions:
      Log.debug("Disconnecting.")
      self.removeTask(session)
      self.sessions.remove(session)

  def loadSvgDrawing(self, target, name, fileName, textureSize = None):
    """
    Load an SVG drawing synchronously.
    
    @param target:      An object that will own the drawing
    @param name:        The name of the attribute the drawing will be assigned to
    @param fileName:    The name of the file in the data directory
    @param textureSize  Either None or (x, y), in which case the file will
                        be rendered to an x by y texture
    @return:            L{SvgDrawing} instance
    """
    return self.data.loadSvgDrawing(target, name, fileName, textureSize)

  def loading(self):
    """Loading state loop."""
    done = Engine.run(self)
    self.clearScreen()
    
    if self.data.essentialResourcesLoaded():
      if not self.loadingScreenShown:
        self.loadingScreenShown = True
        Dialogs.showLoadingScreen(self, self.data.resourcesLoaded)
        if self.startupLayer:
          self.view.pushLayer(self.startupLayer)
        self.mainloop = self.main
      self.view.render()
    self.video.flip()
    return done

  def clearScreen(self):
    self.svg.clear(*Theme.backgroundColor)

  def main(self):
    """Main state loop."""

    # Tune the scheduler priority so that transitions are as smooth as possible
    if self.view.isTransitionInProgress():
      self.boostBackgroundThreads(False)
    else:
      self.boostBackgroundThreads(True)
    
    done = Engine.run(self)
    self.clearScreen()
    self.view.render()
    if self.debugLayer:
      self.debugLayer.render(1.0, True)
    self.video.flip()
    return done

  def run(self):
    try:
      return self.mainloop()
    except KeyboardInterrupt:
      sys.exit(0)
    except SystemExit:
      sys.exit(0)
    except Exception, e:
      def clearMatrixStack(stack):
        try:
          glMatrixMode(stack)
          for i in range(16):
            glPopMatrix()
        except:
          pass

      if self.handlingException:
        # A recursive exception is fatal as we can't reliably reset the GL state
        sys.exit(1)

      self.handlingException = True
      Log.error("%s: %s" % (e.__class__, e))
      import traceback
      traceback.print_exc()

      clearMatrixStack(GL_PROJECTION)
      clearMatrixStack(GL_MODELVIEW)
      
      Dialogs.showMessage(self, unicode(e))
      self.handlingException = False
      return True
