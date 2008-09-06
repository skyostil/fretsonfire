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

"""A bunch of dialog functions for interacting with the user."""

import pygame
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import os
import fnmatch

from View import Layer, BackgroundLayer
from Input import KeyListener
from Camera import Camera
from Mesh import Mesh
from Menu import Menu
from Language import _
from Texture import Texture
import Theme
import Log
import Song
import Data
import Player
import Guitar

def wrapText(font, pos, text, rightMargin = 0.9, scale = 0.002, visibility = 0.0):
  """
  Wrap a piece of text inside given margins.
  
  @param pos:         (x, y) tuple, x defines the left margin
  @param text:        Text to wrap
  @param rightMargin: Right margin
  @param scale:       Text scale
  @param visibility:  Visibility factor [0..1], 0 is fully visible
  """
  x, y = pos
  space = font.getStringSize(" ", scale = scale)[0]

  for n, word in enumerate(text.split(" ")):
    w, h = font.getStringSize(word, scale = scale)
    if x + w > rightMargin or word == "\n":
      x = pos[0]
      y += h
    if word == "\n":
      continue
    glPushMatrix()
    glRotate(visibility * (n + 1) * -45, 0, 0, 1)
    font.render(word, (x, y + visibility * n), scale = scale)
    glPopMatrix()
    x += w + space
  return (x - space, y)

def fadeScreen(v):
  """
  Fade the screen to a dark color to make whatever is on top easier to read.
  
  @param v: Visibility factor [0..1], 0 is fully visible
  """
  glEnable(GL_BLEND)
  glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
  glEnable(GL_COLOR_MATERIAL)

  glBegin(GL_TRIANGLE_STRIP)
  glColor4f(0, 0, 0, .3 - v * .3)
  glVertex2f(0, 0)
  glColor4f(0, 0, 0, .3 - v * .3)
  glVertex2f(1, 0)
  glColor4f(0, 0, 0, .9 - v * .9)
  glVertex2f(0, 1)
  glColor4f(0, 0, 0, .9 - v * .9)
  glVertex2f(1, 1)
  glEnd()
  

class GetText(Layer, KeyListener):
  """Text input layer."""
  def __init__(self, engine, prompt = "", text = ""):
    self.text = text
    self.prompt = prompt
    self.engine = engine
    self.time = 0
    self.accepted = False
    
  def shown(self):
    self.engine.input.addKeyListener(self, priority = True)
    self.engine.input.enableKeyRepeat()
    
  def hidden(self):
    self.engine.input.removeKeyListener(self)
    self.engine.input.disableKeyRepeat()
    
  def keyPressed(self, key, unicode):
    self.time = 0
    c = self.engine.input.controls.getMapping(key)
    if (c in [Player.KEY1] or key == pygame.K_RETURN) and not self.accepted:
      self.engine.view.popLayer(self)
      self.accepted = True
    elif c in [Player.CANCEL, Player.KEY2] and not self.accepted:
      self.text = None
      self.engine.view.popLayer(self)
      self.accepted = True
    elif key == pygame.K_BACKSPACE and not self.accepted:
      self.text = self.text[:-1]
    elif unicode and ord(unicode) > 31 and not self.accepted:
      self.text += unicode
    return True
    
  def run(self, ticks):
    self.time += ticks / 50.0
  
  def render(self, visibility, topMost):
    self.engine.view.setOrthogonalProjection(normalize = True)
    font = self.engine.data.font
    
    try:
      v = (1 - visibility) ** 2
      
      fadeScreen(v)
      Theme.setBaseColor(1 - v)

      if (self.time % 10) < 5 and visibility > .9:
        cursor = "|"
      else:
        cursor = ""

      pos = wrapText(font, (.1, .33 - v), self.prompt)

      Theme.setSelectedColor(1 - v)
      
      if self.text is not None:
        pos = wrapText(font, (.1, (pos[1] + v) + .08 + v / 4), self.text)
        font.render(cursor, pos)
      
    finally:
      self.engine.view.resetProjection()

class GetKey(Layer, KeyListener):
  """Key choosing layer."""
  def __init__(self, engine, prompt = "", key = None):
    self.key = key
    self.prompt = prompt
    self.engine = engine
    self.time = 0
    self.accepted = False
    
  def shown(self):
    self.engine.input.addKeyListener(self, priority = True)
    
  def hidden(self):
    self.engine.input.removeKeyListener(self)
    
  def keyPressed(self, key, unicode):
    c = self.engine.input.controls.getMapping(key)
    if c in [Player.CANCEL, Player.KEY2] and not self.accepted:
      self.key = None
      self.engine.view.popLayer(self)
      self.accepted = True
    elif not self.accepted:
      self.key = key
      self.engine.view.popLayer(self)
      self.accepted = True
    return True
    
  def run(self, ticks):
    self.time += ticks / 50.0
  
  def render(self, visibility, topMost):
    self.engine.view.setOrthogonalProjection(normalize = True)
    font = self.engine.data.font
    
    try:
      v = (1 - visibility) ** 2
      
      fadeScreen(v)
      Theme.setBaseColor(1 - v)

      pos = wrapText(font, (.1, .33 - v), self.prompt)

      Theme.setSelectedColor(1 - v)

      if self.key is not None:
        text = pygame.key.name(self.key).capitalize()
        pos = wrapText(font, (.1, (pos[1] + v) + .08 + v / 4), text)
      
    finally:
      self.engine.view.resetProjection()

class LoadingScreen(Layer, KeyListener):
  """Loading screen layer."""
  def __init__(self, engine, condition, text, allowCancel = False):
    self.engine       = engine
    self.text         = text
    self.condition    = condition
    self.ready        = False
    self.allowCancel  = allowCancel
    self.time         = 0.0

  def shown(self):
    self.engine.input.addKeyListener(self, priority = True)

  def keyPressed(self, key, unicode):
    c = self.engine.input.controls.getMapping(key)
    if self.allowCancel and c == Player.CANCEL:
      self.engine.view.popLayer(self)
    return True
    
  def hidden(self):
    self.engine.boostBackgroundThreads(False)
    self.engine.input.removeKeyListener(self)

  def run(self, ticks):
    self.time += ticks / 50.0
    if not self.ready and self.condition():
      self.engine.view.popLayer(self)
      self.ready = True
  
  def render(self, visibility, topMost):
    self.engine.view.setOrthogonalProjection(normalize = True)
    font = self.engine.data.font

    if not font:
      return

    if visibility > 0.9:
      self.engine.boostBackgroundThreads(True)
    else:
      self.engine.boostBackgroundThreads(False)
    
    try:
      v = (1 - visibility) ** 2
      fadeScreen(v)

      w, h = self.engine.view.geometry[2:4]
      self.engine.data.loadingImage.transform.reset()
      self.engine.data.loadingImage.transform.translate(w / 2, (1.0 - v * .25) * h / 2)
      self.engine.data.loadingImage.transform.scale(1, -1)
      self.engine.data.loadingImage.draw(color = (1, 1, 1, visibility))

      Theme.setBaseColor(1 - v)
      w, h = font.getStringSize(self.text)
      x = .5 - w / 2
      y = .6 - h / 2 + v * .5
      
      font.render(self.text, (x, y))
      
    finally:
      self.engine.view.resetProjection()

class MessageScreen(Layer, KeyListener):
  """Message screen layer."""
  def __init__(self, engine, text, prompt = _("<OK>")):
    self.engine = engine
    self.text = text
    self.time = 0.0
    self.prompt = prompt

  def shown(self):
    self.engine.input.addKeyListener(self, priority = True)

  def keyPressed(self, key, unicode):
    c = self.engine.input.controls.getMapping(key)
    if c in [Player.KEY1, Player.KEY2, Player.CANCEL] or key == pygame.K_RETURN:
      self.engine.view.popLayer(self)
    return True
    
  def hidden(self):
    self.engine.input.removeKeyListener(self)

  def run(self, ticks):
    self.time += ticks / 50.0
  
  def render(self, visibility, topMost):
    self.engine.view.setOrthogonalProjection(normalize = True)
    font = self.engine.data.font

    if not font:
      return
    
    try:
      v = (1 - visibility) ** 2
      fadeScreen(v)

      x = .1
      y = .3 + v * 2
      Theme.setBaseColor(1 - v)
      pos = wrapText(font, (x, y), self.text, visibility = v)

      w, h = font.getStringSize(self.prompt, scale = 0.001)
      x = .5 - w / 2
      y = pos[1] + 3 * h + v * 2
      Theme.setSelectedColor(1 - v)
      font.render(self.prompt, (x, y), scale = 0.001)
      
    finally:
      self.engine.view.resetProjection()
      
class SongChooser(Layer, KeyListener):
  """Song choosing layer."""
  def __init__(self, engine, prompt = "", selectedSong = None, selectedLibrary = None):
    self.prompt         = prompt
    self.engine         = engine
    self.time           = 0
    self.accepted       = False
    self.selectedIndex  = 0
    self.camera         = Camera()
    self.cassetteHeight = .8
    self.cassetteWidth  = 4.0
    self.libraryHeight  = 1.2
    self.libraryWidth   = 4.0
    self.itemAngles     = None
    self.itemLabels     = None
    self.selectedOffset = 0.0
    self.cameraOffset   = 0.0
    self.selectedItem   = None
    self.song           = None
    self.songCountdown  = 1024
    self.songLoader     = None
    self.initialItem    = selectedSong
    self.library        = selectedLibrary
    self.searchText     = ""

    # Use the default library if this one doesn't exist
    if not self.library or not os.path.isdir(self.engine.resource.fileName(self.library)):
      self.library = Song.DEFAULT_LIBRARY

    self.loadCollection()
    self.engine.resource.load(self, "cassette",     lambda: Mesh(self.engine.resource.fileName("cassette.dae")), synch = True)
    self.engine.resource.load(self, "label",        lambda: Mesh(self.engine.resource.fileName("label.dae")), synch = True)
    self.engine.resource.load(self, "libraryMesh",  lambda: Mesh(self.engine.resource.fileName("library.dae")), synch = True)
    self.engine.resource.load(self, "libraryLabel", lambda: Mesh(self.engine.resource.fileName("library_label.dae")), synch = True)
    
    self.engine.loadSvgDrawing(self, "background", "cassette.svg")

  def loadCollection(self):
    self.loaded = False
    self.engine.resource.load(self, "libraries", lambda: Song.getAvailableLibraries(self.engine, self.library), onLoad = self.libraryListLoaded)
    showLoadingScreen(self.engine, lambda: self.loaded, text = _("Browsing Collection..."))

  def libraryListLoaded(self, libraries):
    self.engine.resource.load(self, "songs",     lambda: Song.getAvailableSongs(self.engine, self.library), onLoad = self.songListLoaded)

  def songListLoaded(self, songs):
    if self.songLoader:
      self.songLoader.cancel()
    self.selectedIndex = 0
    self.items         = self.libraries + self.songs
    self.itemAngles    = [0.0] * len(self.items)
    self.itemLabels    = [None] * len(self.items)
    self.loaded        = True
    self.searchText    = ""
    if self.initialItem is not None:
      for i, item in enumerate(self.items):
        if isinstance(item, Song.SongInfo) and self.initialItem == item.songName:
          self.selectedIndex =  i
          break
        elif isinstance(item, Song.LibraryInfo) and self.initialItem == item.libraryName:
          self.selectedIndex =  i
          break
    # Load labels for libraries right away
    for i, item in enumerate(self.items):
      if isinstance(item, Song.LibraryInfo):
        self.loadItemLabel(i)
    self.updateSelection()
    
  def shown(self):
    self.engine.input.addKeyListener(self, priority = True)
    self.engine.input.enableKeyRepeat()
    
  def hidden(self):
    if self.songLoader:
      self.songLoader.cancel()
    if self.song:
      self.song.fadeout(1000)
      self.song = None
    self.engine.input.removeKeyListener(self)
    self.engine.input.disableKeyRepeat()
    
  def getSelectedSong(self):
    if isinstance(self.selectedItem, Song.SongInfo):
      return self.selectedItem.songName

  def getSelectedLibrary(self):
    return self.library

  def loadItemLabel(self, i):
    # Load the item label if it isn't yet loaded
    item = self.items[i]
    if self.itemLabels[i] is None:
      if isinstance(item, Song.SongInfo):
        label = self.engine.resource.fileName(self.library, item.songName,    "label.png")
      else:
        assert isinstance(item, Song.LibraryInfo)
        label = self.engine.resource.fileName(item.libraryName, "label.png")
      if os.path.exists(label):
        self.itemLabels[i] = Texture(label)

  def updateSelection(self):
    self.selectedItem  = self.items[self.selectedIndex]
    self.songCountdown = 1024
    self.loadItemLabel(self.selectedIndex)
    
  def keyPressed(self, key, unicode):
    if not self.items or self.accepted:
      return

    c = self.engine.input.controls.getMapping(key)
    if c in [Player.KEY1] or key == pygame.K_RETURN:
      if self.matchesSearch(self.selectedItem):
        if isinstance(self.selectedItem, Song.LibraryInfo):
          self.library     = self.selectedItem.libraryName
          self.initialItem = None
          self.loadCollection()
        else:
          self.engine.view.popLayer(self)
          self.accepted = True
        if not self.song:
          self.engine.data.acceptSound.play()
    elif c in [Player.CANCEL, Player.KEY2]:
      if self.library != Song.DEFAULT_LIBRARY:
        self.initialItem = self.library
        self.library     = os.path.dirname(self.library)
        self.loadCollection()
      else:
        self.selectedItem = None
        self.engine.view.popLayer(self)
        self.accepted = True
      if not self.song:
        self.engine.data.cancelSound.play()
    elif c in [Player.UP, Player.ACTION1]:
      if self.matchesSearch(self.items[self.selectedIndex]):
        while 1:
          self.selectedIndex = (self.selectedIndex - 1) % len(self.items)
          if self.matchesSearch(self.items[self.selectedIndex]):
            break
      self.updateSelection()
      if not self.song:
        self.engine.data.selectSound.play()
    elif c in [Player.DOWN, Player.ACTION2]:
      if self.matchesSearch(self.items[self.selectedIndex]):
        while 1:
          self.selectedIndex = (self.selectedIndex + 1) % len(self.items)
          if self.matchesSearch(self.items[self.selectedIndex]):
            break
      self.updateSelection()
      if not self.song:
        self.engine.data.selectSound.play()
    elif key == pygame.K_BACKSPACE and not self.accepted:
      self.searchText = self.searchText[:-1]
    elif unicode and ord(unicode) > 31 and not self.accepted:
      self.searchText += unicode
      self.doSearch()
    return True

  def matchesSearch(self, item):
    if not self.searchText:
      return True
    if isinstance(item, Song.SongInfo):
      if self.searchText.lower() in item.name.lower() or self.searchText.lower() in item.artist.lower():
        return True
    elif isinstance(item, Song.LibraryInfo):
      if self.searchText.lower() in item.name.lower():
        return True
    return False

  def doSearch(self):
    if not self.searchText:
      return
      
    for i, item in enumerate(self.items):
      if self.matchesSearch(item):
          self.selectedIndex =  i
          self.updateSelection()
          break

  def songLoaded(self, song):
    self.songLoader = None

    if self.song:
      self.song.stop()
    
    song.setGuitarVolume(self.engine.config.get("audio", "guitarvol"))
    song.setBackgroundVolume(self.engine.config.get("audio", "songvol"))
    song.setRhythmVolume(self.engine.config.get("audio", "rhythmvol"))
    song.play()
    self.song = song

  def playSelectedSong(self):
    song = self.getSelectedSong()
    if not song:
      return
    
    if self.songLoader:
      self.songLoader.cancel()
      # Don't start a new song loader until the previous one is finished
      if self.songLoader.isAlive():
        self.songCountdown = 256
        return

    if self.song:
      self.song.fadeout(1000)

    self.songLoader = self.engine.resource.load(self, None, lambda: Song.loadSong(self.engine, song, playbackOnly = True, library = self.library),
                                                onLoad = self.songLoaded)
    
  def run(self, ticks):
    self.time += ticks / 50.0

    if self.songCountdown > 0:
      self.songCountdown -= ticks
      if self.songCountdown <= 0:
        self.playSelectedSong()

    d = self.cameraOffset - self.selectedOffset
    self.cameraOffset -= d * ticks / 192.0
    
    for i in range(len(self.itemAngles)):
      if i == self.selectedIndex:
        self.itemAngles[i] = min(90, self.itemAngles[i] + ticks / 2.0)
      else:
        self.itemAngles[i] = max(0,  self.itemAngles[i] - ticks / 2.0)
    
  def renderCassette(self, color, label):
    if not self.cassette:
      return

    if color:
      glColor3f(*color)

    glEnable(GL_COLOR_MATERIAL)
    self.cassette.render("Mesh_001")
    glColor3f(.1, .1, .1)
    self.cassette.render("Mesh")

    # Draw the label if there is one
    if label is not None:
      glEnable(GL_TEXTURE_2D)
      label.bind()
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
      glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
      glColor3f(1, 1, 1)
      glMatrixMode(GL_TEXTURE)
      glScalef(1, -1, 1)
      glMatrixMode(GL_MODELVIEW)
      self.label.render("Mesh_001")
      glMatrixMode(GL_TEXTURE)
      glLoadIdentity()
      glMatrixMode(GL_MODELVIEW)
      glDisable(GL_TEXTURE_2D)
  
  def renderLibrary(self, color, label):
    if not self.libraryMesh:
      return

    if color:
      glColor3f(*color)

    glEnable(GL_NORMALIZE)
    glEnable(GL_COLOR_MATERIAL)
    self.libraryMesh.render("Mesh_001")
    glColor3f(.1, .1, .1)
    self.libraryMesh.render("Mesh")

    # Draw the label if there is one
    if label is not None:
      glEnable(GL_TEXTURE_2D)
      label.bind()
      glColor3f(1, 1, 1)
      glMatrixMode(GL_TEXTURE)
      glScalef(1, -1, 1)
      glMatrixMode(GL_MODELVIEW)
      self.libraryLabel.render()
      glMatrixMode(GL_TEXTURE)
      glLoadIdentity()
      glMatrixMode(GL_MODELVIEW)
      glDisable(GL_TEXTURE_2D)
    glDisable(GL_NORMALIZE)
  
  def render(self, visibility, topMost):
    v = (1 - visibility) ** 2

    # render the background
    t = self.time / 100
    w, h, = self.engine.view.geometry[2:4]
    r = .5
    self.background.transform.reset()
    self.background.transform.translate(v * 2 * w + w / 2 + math.sin(t / 2) * w / 2 * r, h / 2 + math.cos(t) * h / 2 * r)
    self.background.transform.rotate(-t)
    self.background.transform.scale(math.sin(t / 8) + 2, math.sin(t / 8) + 2)
    self.background.draw()
      
    # render the item list
    try:
      glMatrixMode(GL_PROJECTION)
      glPushMatrix()
      glLoadIdentity()
      gluPerspective(60, self.engine.view.aspectRatio, 0.1, 1000)
      glMatrixMode(GL_MODELVIEW)
      glLoadIdentity()
      
      glEnable(GL_DEPTH_TEST)
      glDisable(GL_CULL_FACE)
      glDepthMask(1)
      
      offset = 10 * (v ** 2)
      self.camera.origin = (-10 + offset, -self.cameraOffset, 4   + offset)
      self.camera.target = (  0 + offset, -self.cameraOffset, 2.5 + offset)
      self.camera.apply()
      
      y = 0.0
      for i, item in enumerate(self.items):
        if not self.matchesSearch(item):
          continue
        
        c = math.sin(self.itemAngles[i] * math.pi / 180)
        
        if isinstance(item, Song.SongInfo):
          h = c * self.cassetteWidth + (1 - c) * self.cassetteHeight
        else:
          h = c * self.libraryWidth + (1 - c) * self.libraryHeight
        
        d = (y + h * .5 + self.camera.origin[1]) / (4 * (self.camera.target[2] - self.camera.origin[2]))

        if i == self.selectedIndex:
          self.selectedOffset = y + h / 2
          Theme.setSelectedColor()
        else:
          Theme.setBaseColor()
          
        glTranslatef(0, -h / 2, 0)
        
        glPushMatrix()
        if abs(d) < 1.2:
          if isinstance(item, Song.SongInfo):
            glRotate(self.itemAngles[i], 0, 0, 1)
            self.renderCassette(item.cassetteColor, self.itemLabels[i])
          elif isinstance(item, Song.LibraryInfo):
            glRotate(-self.itemAngles[i], 0, 0, 1)
            if i == self.selectedIndex:
              glRotate(self.time * 4, 1, 0, 0)
            self.renderLibrary(item.color, self.itemLabels[i])
        glPopMatrix()
        
        glTranslatef(0, -h / 2, 0)
        y += h
      glDisable(GL_DEPTH_TEST)
      glDisable(GL_CULL_FACE)
      glDepthMask(0)
      
    finally:
      glMatrixMode(GL_PROJECTION)
      glPopMatrix()
      glMatrixMode(GL_MODELVIEW)
    
    # render the song info
    self.engine.view.setOrthogonalProjection(normalize = True)
    font = self.engine.data.font
    
    try:
      glEnable(GL_BLEND)
      glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
      glEnable(GL_COLOR_MATERIAL)
      Theme.setBaseColor(1 - v)

      if self.searchText:
        text = _("Filter: %s") % (self.searchText) + "|"
        if not self.matchesSearch(self.items[self.selectedIndex]):
          text += " (%s)" % _("Not found")
        font.render(text, (.05, .7 + v), scale = 0.001)
      elif self.songLoader:
        font.render(_("Loading Preview..."), (.05, .7 + v), scale = 0.001)

      x = .6
      y = .15
      font.render(self.prompt, (x, .05 - v))

      Theme.setSelectedColor(1 - v)
      
      item  = self.items[self.selectedIndex]

      if self.matchesSearch(item):
        angle = self.itemAngles[self.selectedIndex]
        f = ((90.0 - angle) / 90.0) ** 2
        pos = wrapText(font, (x, y), item.name, visibility = f, scale = 0.0016)

        if isinstance(item, Song.SongInfo):
          Theme.setBaseColor(1 - v)
          wrapText(font, (x, pos[1] + font.getHeight() * 0.0016), item.artist, visibility = f, scale = 0.0016)

          Theme.setSelectedColor(1 - v)
          scale = 0.0011
          w, h = font.getStringSize(self.prompt, scale = scale)
          x = .6
          y = .5 + f / 2.0
          if len(item.difficulties) > 3:
            y = .42 + f / 2.0
            
          for d in item.difficulties:
            scores = item.getHighscores(d)
            if scores:
              score, stars, name = scores[0]
            else:
              score, stars, name = "---", 0, "---"
            Theme.setBaseColor(1 - v)
            font.render(unicode(d),     (x, y),           scale = scale)
            font.render(unicode(Data.STAR2 * stars + Data.STAR1 * (5 - stars)), (x, y + h), scale = scale * .9)
            Theme.setSelectedColor(1 - v)
            font.render(unicode(score), (x + .15, y),     scale = scale)
            font.render(name,       (x + .15, y + h),     scale = scale)
            y += 2 * h + f / 4.0
        elif isinstance(item, Song.LibraryInfo):
          Theme.setBaseColor(1 - v)
          if item.songCount == 1:
            songCount = _("One song in this library")
          else:
            songCount = _("%d songs in this library") % item.songCount
          wrapText(font, (x, pos[1] + 3 * font.getHeight() * 0.0016), songCount, visibility = f, scale = 0.0016)
    finally:
      self.engine.view.resetProjection()

class FileChooser(BackgroundLayer, KeyListener):
  """File choosing layer."""
  def __init__(self, engine, masks, path, prompt = ""):
    self.masks          = masks
    self.path           = path
    self.prompt         = prompt
    self.engine         = engine
    self.accepted       = False
    self.selectedFile   = None
    self.time           = 0.0
    self.menu           = None

    self.engine.loadSvgDrawing(self, "background", "editor.svg")

  def _getFileCallback(self, fileName):
    return lambda: self.chooseFile(fileName)

  def _getFileText(self, fileName):
    f = os.path.join(self.path, fileName)
    if fileName == "..":
      return _("[Parent Folder]")
    if os.path.isdir(f):
      return _("%s [Folder]") % fileName
    return fileName

  def getFiles(self):
    files = [".."]
    for fn in os.listdir(self.path):
      if fn.startswith("."): continue
      f = os.path.join(self.path, fn)
      for mask in self.masks:
        if fnmatch.fnmatch(fn, mask):
          break
      else:
        if not os.path.isdir(f):
          continue
      files.append(fn)
    files.sort()
    return files

  def updateFiles(self):
    if self.menu:
      self.engine.view.popLayer(self.menu)
    self.menu = Menu(self.engine, choices = [(self._getFileText(f), self._getFileCallback(f)) for f in self.getFiles()], onClose = self.close, onCancel = self.cancel)
    self.engine.view.pushLayer(self.menu)

  def chooseFile(self, fileName):
    path = os.path.abspath(os.path.join(self.path, fileName))
    if os.path.isdir(path):
      self.path = path
      self.updateFiles()
      return
    self.selectedFile = path
    accepted = True
    self.engine.view.popLayer(self.menu)
    self.engine.view.popLayer(self)
    self.menu = None
    
  def cancel(self):
    self.accepted = True
    self.engine.view.popLayer(self)

  def close(self):
    if not self.menu:
      self.accepted = True
      self.engine.view.popLayer(self)
    
  def shown(self):
    self.updateFiles()
    
  def getSelectedFile(self):
    return self.selectedFile
  
  def run(self, ticks):
    self.time += ticks / 50.0
    
  def render(self, visibility, topMost):
    v = (1 - visibility) ** 2

    # render the background    
    t = self.time / 100
    w, h, = self.engine.view.geometry[2:4]
    r = .5
    self.background.transform.reset()
    self.background.transform.translate(v * 2 * w + w / 2 + math.sin(t / 2) * w / 2 * r, h / 2 + math.cos(t) * h / 2 * r)
    self.background.transform.rotate(-t)
    self.background.transform.scale(math.sin(t / 8) + 2, math.sin(t / 8) + 2)
    self.background.draw()
      
    self.engine.view.setOrthogonalProjection(normalize = True)
    font = self.engine.data.font
    
    try:
      glEnable(GL_BLEND)
      glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
      glEnable(GL_COLOR_MATERIAL)
      Theme.setBaseColor(1 - v)
      wrapText(font, (.1, .05 - v), self.prompt)
    finally:
      self.engine.view.resetProjection()

class ItemChooser(BackgroundLayer, KeyListener):
  """Item menu layer."""
  def __init__(self, engine, items, selected = None, prompt = ""):
    self.prompt         = prompt
    self.engine         = engine
    self.accepted       = False
    self.selectedItem   = None
    self.time           = 0.0
    self.menu = Menu(self.engine, choices = [(c, self._callbackForItem(c)) for c in items], onClose = self.close, onCancel = self.cancel)
    if selected and selected in items:
      self.menu.selectItem(items.index(selected))
    self.engine.loadSvgDrawing(self, "background", "editor.svg")
    
  def _callbackForItem(self, item):
    def cb():
      self.chooseItem(item)
    return cb
    
  def chooseItem(self, item):
    self.selectedItem = item
    accepted = True
    self.engine.view.popLayer(self.menu)
    self.engine.view.popLayer(self)
    
  def cancel(self):
    self.accepted = True
    self.engine.view.popLayer(self)

  def close(self):
    self.accepted = True
    self.engine.view.popLayer(self)
    
  def shown(self):
    self.engine.view.pushLayer(self.menu)
    
  def getSelectedItem(self):
    return self.selectedItem
  
  def run(self, ticks):
    self.time += ticks / 50.0
    
  def render(self, visibility, topMost):
    v = (1 - visibility) ** 2

    # render the background    
    t = self.time / 100
    w, h, = self.engine.view.geometry[2:4]
    r = .5
    self.background.transform.reset()
    self.background.transform.translate(v * 2 * w + w / 2 + math.sin(t / 2) * w / 2 * r, h / 2 + math.cos(t) * h / 2 * r)
    self.background.transform.rotate(-t)
    self.background.transform.scale(math.sin(t / 8) + 2, math.sin(t / 8) + 2)
    self.background.draw()
      
    self.engine.view.setOrthogonalProjection(normalize = True)
    font = self.engine.data.font
    
    try:
      glEnable(GL_BLEND)
      glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
      glEnable(GL_COLOR_MATERIAL)
      Theme.setBaseColor(1 - v)
      wrapText(font, (.1, .05 - v), self.prompt)
    finally:
      self.engine.view.resetProjection()
      
      
class BpmEstimator(Layer, KeyListener):
  """Beats per minute value estimation layer."""
  def __init__(self, engine, song, prompt = ""):
    self.prompt         = prompt
    self.engine         = engine
    self.song           = song
    self.accepted       = False
    self.bpm            = None
    self.time           = 0.0
    self.beats          = []
    
  def shown(self):
    self.engine.input.addKeyListener(self, priority = True)
    self.song.play()
  
  def hidden(self):
    self.engine.input.removeKeyListener(self)
    self.song.fadeout(1000)
    
  def keyPressed(self, key, unicode):
    if self.accepted:
      return True
      
    c = self.engine.input.controls.getMapping(key)
    if key == pygame.K_SPACE:
      self.beats.append(self.time)
      if len(self.beats) > 12:
        diffs = [self.beats[i + 1] - self.beats[i] for i in range(len(self.beats) - 1)]
        self.bpm = 60000.0 / (sum(diffs) / float(len(diffs)))
        self.beats = self.beats[-12:]
    elif c in [Player.CANCEL, Player.KEY2]:
      self.engine.view.popLayer(self)
      self.accepted = True
      self.bpm      = None
    elif c in [Player.KEY1] or key == pygame.K_RETURN:
      self.engine.view.popLayer(self)
      self.accepted = True
      
    return True
  
  def run(self, ticks):
    self.time += ticks
    
  def render(self, visibility, topMost):
    v = (1 - visibility) ** 2

    self.engine.view.setOrthogonalProjection(normalize = True)
    font = self.engine.data.font
    
    fadeScreen(v)
          
    try:
      glEnable(GL_BLEND)
      glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
      glEnable(GL_COLOR_MATERIAL)
      Theme.setBaseColor(1 - v)
      wrapText(font, (.1, .2 - v), self.prompt)
      
      if self.bpm is not None:
        Theme.setSelectedColor(1 - v)
        wrapText(font, (.1, .5 + v),  _("%.2f beats per minute") % (self.bpm))
    finally:
      self.engine.view.resetProjection()
      
class KeyTester(Layer, KeyListener):
  """Keyboard configuration testing layer."""
  def __init__(self, engine, prompt = ""):
    self.prompt         = prompt
    self.engine         = engine
    self.accepted       = False
    self.time           = 0.0
    self.controls       = Player.Controls()
    self.fretColors     = Theme.fretColors
    
  def shown(self):
    self.engine.input.addKeyListener(self, priority = True)
  
  def hidden(self):
    self.engine.input.removeKeyListener(self)
    
  def keyPressed(self, key, unicode):
    if self.accepted:
      return True

    self.controls.keyPressed(key)
    c = self.engine.input.controls.getMapping(key)
    if c in [Player.CANCEL]:
      self.engine.view.popLayer(self)
      self.accepted = True
    return True

  def keyReleased(self, key):
    self.controls.keyReleased(key)
  
  def run(self, ticks):
    self.time += ticks
    
  def render(self, visibility, topMost):
    v = (1 - visibility) ** 2

    self.engine.view.setOrthogonalProjection(normalize = True)
    font = self.engine.data.font
    
    fadeScreen(v)
          
    try:
      glEnable(GL_BLEND)
      glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
      glEnable(GL_COLOR_MATERIAL)
      Theme.setBaseColor(1 - v)
      wrapText(font, (.1, .2 - v), self.prompt)

      for n, c in enumerate(Guitar.KEYS):
        if self.controls.getState(c):
          glColor3f(*self.fretColors[n])
        else:
          glColor3f(.4, .4, .4)
        font.render("#%d" % (n + 1), (.5 - .15 * (2 - n), .4 + v))

      if self.controls.getState(Player.ACTION1) or \
         self.controls.getState(Player.ACTION2):
        Theme.setSelectedColor(1 - v)
      else:
        glColor3f(.4, .4, .4)
      font.render(_("Pick!"), (.45, .5 + v))
        
    finally:
      self.engine.view.resetProjection()
      
def _runDialog(engine, dialog):
  """Run a dialog in a sub event loop until it is finished."""
  if not engine.running:
    return
  
  engine.view.pushLayer(dialog)

  while engine.running and dialog in engine.view.layers:
    engine.run()

def getText(engine, prompt, text = ""):
  """
  Get a string of text from the user.
  
  @param engine:  Game engine
  @param prompt:  Prompt shown to the user
  @param text:    Default text
  """
  d = GetText(engine, prompt, text)
  _runDialog(engine, d)
  return d.text

def getKey(engine, prompt, key = None):
  """
  Ask the user to choose a key.
  
  @param engine:  Game engine
  @param prompt:  Prompt shown to the user
  @param key:     Default key
  """
  d = GetKey(engine, prompt, key)
  _runDialog(engine, d)
  return d.key

def chooseSong(engine, prompt = _("Choose a Song"), selectedSong = None, selectedLibrary = None):
  """
  Ask the user to select a song.
  
  @param engine:           Game engine
  @param prompt:           Prompt shown to the user
  @param selectedSong:     Name of song to select initially
  @param selectedLibrary:  Name of the library where to search for the songs or None for the default library

  @returns a (library, song) pair
  """
  d = SongChooser(engine, prompt, selectedLibrary = selectedLibrary, selectedSong = selectedSong)
  _runDialog(engine, d)
  return (d.getSelectedLibrary(), d.getSelectedSong())
  
def chooseFile(engine, masks = ["*.*"], path = ".", prompt = _("Choose a File")):
  """
  Ask the user to select a file.
  
  @param engine:  Game engine
  @param masks:   List of glob masks for files that are acceptable
  @param path:    Initial path
  @param prompt:  Prompt shown to the user
  """
  d = FileChooser(engine, masks, path, prompt)
  _runDialog(engine, d)
  return d.getSelectedFile()
  
def chooseItem(engine, items, prompt, selected = None):
  """
  Ask the user to one item from a list.
  
  @param engine:    Game engine
  @param items:     List of items
  @param prompt:    Prompt shown to the user
  @param selected:  Item selected by default
  """
  d = ItemChooser(engine, items, prompt = prompt, selected = selected)
  _runDialog(engine, d)
  return d.getSelectedItem()
  
def testKeys(engine, prompt = _("Play with the keys and press Escape when you're done.")):
  """
  Have the user test the current keyboard configuration.
  
  @param engine:  Game engine
  @param prompt:  Prompt shown to the user
  """
  d = KeyTester(engine, prompt = prompt)
  _runDialog(engine, d)
  
def showLoadingScreen(engine, condition, text = _("Loading..."), allowCancel = False):
  """
  Show a loading screen until a condition is met.
  
  @param engine:      Game engine
  @param condition:   A function that will be polled until it returns a true value
  @param text:        Text shown to the user
  @type  allowCancel: bool
  @param allowCancel: Can the loading be canceled
  @return:            True if the condition was met, Fales if the loading was canceled.
  """
  
  # poll the condition first for some time
  n = 0
  while n < 32:
    n += 1
    if condition():
      return True
    engine.run()

  d = LoadingScreen(engine, condition, text, allowCancel)
  _runDialog(engine, d)
  return d.ready

def showMessage(engine, text):
  """
  Show a message to the user.
  
  @param engine:  Game engine
  @param text:    Message text
  """
  Log.notice("%s" % text)
  d = MessageScreen(engine, text)
  _runDialog(engine, d)

def estimateBpm(engine, song, prompt):
  """
  Ask the user to estimate the beats per minute value of a song.
  
  @param engine:  Game engine
  @param song:    Song instance
  @param prompt:  Prompt shown to the user
  """
  d = BpmEstimator(engine, song, prompt)
  _runDialog(engine, d)
  return d.bpm
  
