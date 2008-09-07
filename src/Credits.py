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
from OpenGL.GL import *
from OpenGL.GLU import *
import math

from View import Layer
from Input import KeyListener
from Language import _
import MainMenu
import Song
import Version
import Player

class Element:
  """A basic element in the credits scroller."""
  def getHeight(self):
    """@return: The height of this element in fractions of the screen height"""
    return 0

  def render(self, offset):
    """
    Render this element.
    
    @param offset: Offset in the Y direction in fractions of the screen height
    """
    pass

class Text(Element):
  def __init__(self, font, scale, color, alignment, text):
    self.text      = text
    self.font      = font
    self.color     = color
    self.alignment = alignment
    self.scale     = scale
    self.size      = self.font.getStringSize(self.text, scale = scale)

  def getHeight(self):
    return self.size[1]

  def render(self, offset):
    if self.alignment == "left":
      x = .1
    elif self.alignment == "right":
      x = .9 - self.size[0]
    elif self.alignment == "center":
      x = .5 - self.size[0] / 2
    glColor4f(*self.color)
    self.font.render(self.text, (x, offset), scale = self.scale)

class Picture(Element):
  def __init__(self, engine, fileName, height):
    self.height = height
    self.engine = engine
    engine.loadSvgDrawing(self, "drawing", fileName)

  def getHeight(self):
    return self.height

  def render(self, offset):
    self.drawing.transform.reset()
    w, h = self.engine.view.geometry[2:4]
    self.drawing.transform.translate(.5 * w, h - (.5 * self.height + offset) * h * float(w) / float(h))
    self.drawing.transform.scale(1, -1)
    self.drawing.draw()
    
class Credits(Layer, KeyListener):
  """Credits scroller."""
  def __init__(self, engine, songName = None):
    self.engine      = engine
    self.time        = 0.0
    self.offset      = 1.0
    self.songLoader  = self.engine.resource.load(self, "song", lambda: Song.loadSong(self.engine, "defy", playbackOnly = True),
                                                 onLoad = self.songLoaded)
    self.engine.loadSvgDrawing(self, "background1", "editor.svg")
    self.engine.loadSvgDrawing(self, "background2", "keyboard.svg")
    self.engine.loadSvgDrawing(self, "background3", "cassette.svg")
    self.engine.boostBackgroundThreads(True)

    nf = self.engine.data.font
    bf = self.engine.data.bigFont
    ns = 0.002
    bs = 0.001
    hs = 0.003
    c1 = (1, 1, .5, 1)
    c2 = (1, .75, 0, 1)

    space = Text(nf, hs, c1, "center", " ")
    self.credits = [
      Text(nf, ns, c2, "center", _("Unreal Voodoo")),
      Text(nf, ns, c1, "center", _("presents")),
      Text(nf, bs, c2, "center", " "),
      Picture(self.engine, "logo.svg", .25),
      Text(nf, bs, c2, "center", " "),
      Text(nf, bs, c2, "center", _("Version %s") % Version.version()),
      space,
      Text(nf, ns, c1, "left",   _("Game Design,")),
      Text(nf, ns, c1, "left",   _("Programming:")),
      Text(nf, ns, c2, "right",  "Sami Kyostila"),
      space,
      Text(nf, ns, c1, "left",   _("Music,")),
      Text(nf, ns, c1, "left",   _("Sound Effects:")),
      Text(nf, ns, c2, "right",  "Tommi Inkila"),
      space,
      Text(nf, ns, c1, "left",   _("Graphics:")),
      Text(nf, ns, c2, "right",  "Joonas Kerttula"),
      space,
      Text(nf, ns, c1, "left",   _("Introducing:")),
      Text(nf, ns, c2, "right",  "Mikko Korkiakoski"),
      Text(nf, ns, c2, "right",  _("as Jurgen, Your New God")),
      space,
      Text(nf, ns, c2, "right",  "Marjo Hakkinen"),
      Text(nf, ns, c2, "right",  _("as Groupie")),
      space,
      Text(nf, ns, c1, "left",   _("Song Credits:")),
      Text(nf, ns, c2, "right",  _("Bang Bang, Mystery Man")),
      Text(nf, bs, c2, "right",  _("music by Mary Jo and Tommi Inkila")),
      Text(nf, bs, c2, "right",  _("lyrics by Mary Jo")),
      space,
      Text(nf, ns, c2, "right",  _("Defy The Machine")),
      Text(nf, bs, c2, "right",  _("music by Tommi Inkila")),
      space,
      Text(nf, ns, c2, "right",  _("This Week I've Been")),
      Text(nf, ns, c2, "right",  _("Mostly Playing Guitar")),
      Text(nf, bs, c2, "right",  _("composed and performed by Tommi Inkila")),
      space,
      Text(nf, ns, c1, "left",   _("Testing:")),
      Text(nf, ns, c2, "right",  "Mikko Korkiakoski"),
      Text(nf, ns, c2, "right",  "Tomi Kyostila"),
      Text(nf, ns, c2, "right",  "Jani Vaarala"),
      Text(nf, ns, c2, "right",  "Juho Jamsa"),
      Text(nf, ns, c2, "right",  "Olli Jakola"),
      space,
      Text(nf, ns, c1, "left",   _("Mac OS X port:")),
      Text(nf, ns, c2, "right",  "Tero Pihlajakoski"),
      space,
      Text(nf, ns, c1, "left",   _("Special thanks to:")),
      Text(nf, ns, c2, "right",  "Tutorial inspired by adam02"),
      space,
      Text(nf, ns, c1, "left",   _("Made with:")),
      Text(nf, ns, c2, "right",  "Python"),
      Text(nf, bs, c2, "right",  "http://www.python.org"),
      space,
      Text(nf, ns, c2, "right",  "PyGame"),
      Text(nf, bs, c2, "right",  "http://www.pygame.org"),
      space,
      Text(nf, ns, c2, "right",  "PyOpenGL"),
      Text(nf, bs, c2, "right",  "http://pyopengl.sourceforge.net"),
      space,
      Text(nf, ns, c2, "right",  "Amanith Framework"),
      Text(nf, bs, c2, "right",  "http://www.amanith.org"),
      space,
      Text(nf, ns, c2, "right",  "Illusoft Collada module 1.4"),
      Text(nf, bs, c2, "right",  "http://colladablender.illusoft.com"),
      space,
      Text(nf, ns, c2, "right",  "Psyco specializing compiler"),
      Text(nf, bs, c2, "right",  "http://psyco.sourceforge.net"),
      space,
      Text(nf, ns, c2, "right",  "MXM Python Midi Package 0.1.4"),
      Text(nf, bs, c2, "right",  "http://www.mxm.dk/products/public/pythonmidi"),
      space,
      space,
      Text(nf, bs, c1, "center", _("Source Code available under the GNU General Public License")),
      Text(nf, bs, c2, "center", "http://www.unrealvoodoo.org"),
      space,
      space,
      space,
      space,
      Text(nf, bs, c1, "center", _("Copyright 2006-2008 by Unreal Voodoo")),
    ]

  def songLoaded(self, song):
    self.engine.boostBackgroundThreads(False)
    song.play()

  def shown(self):
    self.engine.input.addKeyListener(self)

  def hidden(self):
    if self.song:
      self.song.fadeout(1000)
    self.engine.input.removeKeyListener(self)
    self.engine.view.pushLayer(MainMenu.MainMenu(self.engine))

  def quit(self):
    self.engine.view.popLayer(self)

  def keyPressed(self, key, unicode):
    if self.engine.input.controls.getMapping(key) in [Player.CANCEL, Player.KEY1, Player.KEY2] or key == pygame.K_RETURN:
      self.songLoader.cancel()
      self.quit()
    return True
  
  def run(self, ticks):
    self.time   += ticks / 50.0
    if self.song:
      self.offset -= ticks / 5000.0

    if self.offset < -6.1:
      self.quit()
  
  def render(self, visibility, topMost):
    v = 1.0 - ((1 - visibility) ** 2)
    
    # render the background    
    t = self.time / 100 + 34
    w, h, = self.engine.view.geometry[2:4]
    r = .5
    for i, background in [(0, self.background1), (1, self.background2), (2, self.background3)]:
      background.transform.reset()
      background.transform.translate((1 - v) * 2 * w + w / 2 + math.cos(t / 2) * w / 2 * r, h / 2 + math.sin(t) * h / 2 * r)
      background.transform.translate(0, -h * (((self.offset + i * 2) % 6.0) - 3.0))
      background.transform.rotate(math.sin(t * 4 + i) / 2)
      background.transform.scale(math.sin(t / 8) + 3, math.sin(t / 8) + 3)
      background.draw()
    
    self.engine.view.setOrthogonalProjection(normalize = True)
    font = self.engine.data.font

    # render the scroller elements
    y = self.offset
    glTranslatef(-(1 - v), 0, 0)
    try:
      for element in self.credits:
        h = element.getHeight()
        if y + h > 0.0 and y < 1.0:
          element.render(y)
        y += h
        if y > 1.0:
          break
    finally:
      self.engine.view.resetProjection()
