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

import pygame
from pygame.mixer import Sound
from OpenGL.GL import *
import math
import socket

from View import BackgroundLayer
from Menu import Menu, Choice
from Editor import Editor, Importer, GHImporter
from Credits import Credits
from Lobby import Lobby
from Svg import SvgDrawing
from Language import _
import Dialogs
import Config
import Mod

class ConfigChoice(Choice):
  def __init__(self, config, section, option, autoApply = False):
    self.config    = config
    self.section   = section
    self.option    = option
    self.changed   = False
    self.value     = None
    self.autoApply = autoApply
    o = config.prototype[section][option]
    v = config.get(section, option)
    if isinstance(o.options, dict):
      values     = o.options.values()
      values.sort()
      try:
        valueIndex = values.index(o.options[v])
      except KeyError:
        valueIndex = 0
    elif isinstance(o.options, list):
      values     = o.options
      try:
        valueIndex = values.index(v)
      except ValueError:
        valueIndex = 0
    else:
      raise RuntimeError("No usable options for %s.%s." % (section, option))
    Choice.__init__(self, text = o.text, callback = self.change, values = values, valueIndex = valueIndex)
    
  def change(self, value):
    o = self.config.prototype[self.section][self.option]
    
    if isinstance(o.options, dict):
      for k, v in o.options.items():
        if v == value:
          value = k
          break
    
    self.changed = True
    self.value   = value
    
    if self.autoApply:
      self.apply()

  def apply(self):
    if self.changed:
      self.config.set(self.section, self.option, self.value)

class KeyConfigChoice(Choice):
  def __init__(self, engine, config, section, option):
    self.engine  = engine
    self.config  = config
    self.section = section
    self.option  = option
    self.changed = False
    self.value   = None
    Choice.__init__(self, text = "", callback = self.change)

  def getText(self, selected):
    def keycode(k):
      try:
        return int(k)
      except:
        return getattr(pygame, k)
    o = self.config.prototype[self.section][self.option]
    v = self.config.get(self.section, self.option)
    return "%s: %s" % (o.text, pygame.key.name(keycode(v)).capitalize())
    
  def change(self):
    o = self.config.prototype[self.section][self.option]

    if isinstance(o.options, dict):
      for k, v in o.options.items():
        if v == value:
          value = k
          break

    key = Dialogs.getKey(self.engine, _("Press a key for '%s' or Escape to cancel.") % (o.text))

    if key:
      self.config.set(self.section, self.option, key)
      self.engine.input.reloadControls()

  def apply(self):
    pass

class MainMenu(BackgroundLayer):
  def __init__(self, engine):
    self.engine              = engine
    self.time                = 0.0
    self.nextLayer           = None
    self.visibility          = 0.0
    
    self.engine.loadSvgDrawing(self, "background", "keyboard.svg")
    self.engine.loadSvgDrawing(self, "guy",        "pose.svg")
    self.engine.loadSvgDrawing(self, "logo",       "logo.svg")
    self.song = Sound(self.engine.resource.fileName("menu.ogg"))
    self.song.play(-1)

    newMultiplayerMenu = [
      (_("Host Multiplayer Game"), self.hostMultiplayerGame),
      (_("Join Multiplayer Game"), self.joinMultiplayerGame),
    ]

    applyItem = [(_("Apply New Settings"), self.applySettings)]

    self.modSettings = [
      ConfigChoice(self.engine.config, "mods",  "mod_" + m) for m in Mod.getAvailableMods(self.engine)
    ] + applyItem
    
    self.gameSettings = [
      (_("Mod settings"), self.modSettings),
      ConfigChoice(self.engine.config, "game",  "language"),
      ConfigChoice(self.engine.config, "game",  "leftymode", autoApply = True),
      ConfigChoice(self.engine.config, "game",  "uploadscores", autoApply = True),
    ]
    gameSettingsMenu = Menu(self.engine, self.gameSettings + applyItem)

    keySettings = [
      (_("Test Keys"), lambda: Dialogs.testKeys(self.engine)),
      KeyConfigChoice(self.engine, self.engine.config, "player", "key_action1"),
      KeyConfigChoice(self.engine, self.engine.config, "player", "key_action2"),
      KeyConfigChoice(self.engine, self.engine.config, "player", "key_1"),
      KeyConfigChoice(self.engine, self.engine.config, "player", "key_2"),
      KeyConfigChoice(self.engine, self.engine.config, "player", "key_3"),
      KeyConfigChoice(self.engine, self.engine.config, "player", "key_4"),
      KeyConfigChoice(self.engine, self.engine.config, "player", "key_5"),
      KeyConfigChoice(self.engine, self.engine.config, "player", "key_left"),
      KeyConfigChoice(self.engine, self.engine.config, "player", "key_right"),
      KeyConfigChoice(self.engine, self.engine.config, "player", "key_up"),
      KeyConfigChoice(self.engine, self.engine.config, "player", "key_down"),
      KeyConfigChoice(self.engine, self.engine.config, "player", "key_cancel"),
    ]
    keySettingsMenu = Menu(self.engine, keySettings)
    
    modes = self.engine.video.getVideoModes()
    modes.reverse()
    Config.define("video",  "resolution", str,   "640x480", text = _("Video Resolution"), options = ["%dx%d" % (m[0], m[1]) for m in modes])
    self.videoSettings = [
      ConfigChoice(self.engine.config, "video",  "resolution"),
      ConfigChoice(self.engine.config, "video",  "fullscreen"),
      ConfigChoice(self.engine.config, "video",  "fps"),
      ConfigChoice(self.engine.config, "video",  "multisamples"),
      #ConfigChoice(self.engine.config, "opengl", "svgshaders"),    # shaders broken at the moment
      ConfigChoice(self.engine.config, "opengl", "svgquality"),
      ConfigChoice(self.engine.config, "video", "fontscale"),
    ]
    videoSettingsMenu = Menu(self.engine, self.videoSettings + applyItem)

    self.audioSettings = [
      ConfigChoice(self.engine.config, "audio",  "delay"),
      ConfigChoice(self.engine.config, "audio",  "frequency"),
      ConfigChoice(self.engine.config, "audio",  "bits"),
      ConfigChoice(self.engine.config, "audio",  "buffersize"),
      ConfigChoice(self.engine.config, "audio",  "screwupvol"),
    ]
    audioSettingsMenu = Menu(self.engine, self.audioSettings + applyItem)

    self.settings = [
      (_("Game Settings"),     gameSettingsMenu),
      (_("Key Settings"),      keySettingsMenu),
      (_("Video Settings"),    videoSettingsMenu),
      (_("Audio Settings"),    audioSettingsMenu),
    ]
    settingsMenu = Menu(self.engine, self.settings)
    
    editorMenu = Menu(self.engine, [
      (_("Edit Existing Song"),            self.startEditor),
      (_("Import New Song"),               self.startImporter),
      (_("Import Guitar Hero(tm) Songs"),  self.startGHImporter),
    ])
    
    mainMenu = [
      (_("Play Game"),   self.newSinglePlayerGame),
      (_("Tutorial"),    self.showTutorial),
      (_("Song Editor"), editorMenu),
      (_("Settings >"),  settingsMenu),
      (_("Credits"),     self.showCredits),
      (_("Quit"),        self.quit),
    ]
    self.menu = Menu(self.engine, mainMenu, onClose = lambda: self.engine.view.popLayer(self))

  def shown(self):
    self.engine.view.pushLayer(self.menu)
    self.engine.stopServer()
    
  def applySettings(self):
    for option in self.settings + self.videoSettings + self.audioSettings + self.gameSettings + self.modSettings:
      if isinstance(option, ConfigChoice):
        option.apply()
    self.engine.restart()

  def hidden(self):
    self.engine.view.popLayer(self.menu)

    if self.song:
      self.song.fadeout(1000)
    
    if self.nextLayer:
      self.engine.view.pushLayer(self.nextLayer())
      self.nextLayer = None
    else:
      self.engine.quit()

  def quit(self):
    self.engine.view.popLayer(self.menu)

  def catchErrors(function):
    def harness(self, *args, **kwargs):
      try:
        try:
          function(self, *args, **kwargs)
        except:
          import traceback
          traceback.print_exc()
          raise
      except socket.error, e:
        Dialogs.showMessage(self.engine, unicode(e[1]))
      except KeyboardInterrupt:
        pass
      except Exception, e:
        if e:
          Dialogs.showMessage(self.engine, unicode(e))
    return harness

  def launchLayer(self, layerFunc):
    if not self.nextLayer:
      self.nextLayer = layerFunc
      self.engine.view.popAllLayers()

  def showTutorial(self):
    if self.engine.isServerRunning():
      return
    self.engine.startServer()
    self.engine.resource.load(self, "session", lambda: self.engine.connect("127.0.0.1"), synch = True)

    if Dialogs.showLoadingScreen(self.engine, lambda: self.session and self.session.isConnected):
      self.launchLayer(lambda: Lobby(self.engine, self.session, singlePlayer = True, tutorial = True))
  showTutorial = catchErrors(showTutorial)

  def newSinglePlayerGame(self):
    if self.engine.isServerRunning():
      return
    self.engine.startServer()
    self.engine.resource.load(self, "session", lambda: self.engine.connect("127.0.0.1"), synch = True)

    if Dialogs.showLoadingScreen(self.engine, lambda: self.session and self.session.isConnected):
      self.launchLayer(lambda: Lobby(self.engine, self.session, singlePlayer = True))
  newSinglePlayerGame = catchErrors(newSinglePlayerGame)

  def hostMultiplayerGame(self):
    self.engine.startServer()
    self.engine.resource.load(self, "session", lambda: self.engine.connect("127.0.0.1"))

    if Dialogs.showLoadingScreen(self.engine, lambda: self.session and self.session.isConnected):
      self.launchLayer(lambda: Lobby(self.engine, self.session))
  hostMultiplayerGame = catchErrors(hostMultiplayerGame)

  def joinMultiplayerGame(self, address = None):
    if not address:
      address = Dialogs.getText(self.engine, _("Enter the server address:"), "127.0.0.1")

    if not address:
      return
    
    self.engine.resource.load(self, "session", lambda: self.engine.connect(address))

    if Dialogs.showLoadingScreen(self.engine, lambda: self.session and self.session.isConnected, text = _("Connecting...")):
      self.launchLayer(lambda: Lobby(self.engine, self.session))
  joinMultiplayerGame = catchErrors(joinMultiplayerGame)

  def startEditor(self):
    self.launchLayer(lambda: Editor(self.engine))
  startEditor = catchErrors(startEditor)

  def startImporter(self):
    self.launchLayer(lambda: Importer(self.engine))
  startImporter = catchErrors(startImporter)

  def startGHImporter(self):
    self.launchLayer(lambda: GHImporter(self.engine))
  startGHImporter = catchErrors(startGHImporter)

  def showCredits(self):
    self.launchLayer(lambda: Credits(self.engine))
  showCredits = catchErrors(showCredits)

  def run(self, ticks):
    self.time += ticks / 50.0
    
  def render(self, visibility, topMost):
    self.visibility = visibility
    v = 1.0 - ((1 - visibility) ** 2)
      
    t = self.time / 100
    w, h, = self.engine.view.geometry[2:4]
    r = .5
    self.background.transform.reset()
    self.background.transform.translate((1 - v) * 2 * w + w / 2 + math.cos(t / 2) * w / 2 * r, h / 2 + math.sin(t) * h / 2 * r)
    self.background.transform.rotate(-t)
    self.background.transform.scale(math.sin(t / 8) + 2, math.sin(t / 8) + 2)
    self.background.draw()

    self.logo.transform.reset()
    self.logo.transform.translate(.5 * w, .8 * h + (1 - v) * h * 2 * 0)
    f1 = math.sin(t * 16) * .025
    f2 = math.cos(t * 17) * .025
    self.logo.transform.scale(1 + f1 + (1 - v) ** 3, -1 + f2 + (1 - v) ** 3)
    self.logo.draw()
    
    self.guy.transform.reset()
    self.guy.transform.translate(.75 * w + (1 - v) * 2 * w, .35 * h)
    self.guy.transform.scale(-.9, .9)
    self.guy.transform.rotate(math.pi)
    self.guy.draw()
