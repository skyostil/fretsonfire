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

from ConfigParser import ConfigParser
from OpenGL.GL import *
import math
import Theme

class Layer(object):
  def __init__(self, stage, drawing):
    self.stage       = stage
    self.drawing     = drawing
    self.position    = (0.0, 0.0)
    self.angle       = 0.0
    self.scale       = (1.0, 1.0)
    self.color       = (1.0, 1.0, 1.0, 1.0)
    self.srcBlending = GL_SRC_ALPHA
    self.dstBlending = GL_ONE_MINUS_SRC_ALPHA
    self.effects     = []
  
  def render(self, visibility):
    w, h, = self.stage.engine.view.geometry[2:4]
    self.drawing.transform.reset()
    self.drawing.transform.translate(w / 2, h / 2)
    self.drawing.transform.scale(self.scale[0], -self.scale[1])
    self.drawing.transform.translate(self.position[0] * w / 2, -self.position[1] * h / 2)
    self.drawing.transform.rotate(self.angle)

    # Blend in all the effects
    for effect in self.effects:
      effect.apply()
    
    glBlendFunc(self.srcBlending, self.dstBlending)
    self.drawing.draw(color = self.color)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

class Effect(object):
  def __init__(self, layer, options):
    self.layer     = layer
    self.stage     = layer.stage
    self.intensity = float(options.get("intensity", 1.0))

  def apply(self):
    pass

  def step(self, threshold, x):
    return (x > threshold) and 1 or 0

  def linstep(self, min, max, x):
    if x < min:
      return 0
    if x > max:
      return 1
    return (x - min) / (max - min)

  def smoothstep(self, min, max, x):
    if x < min:
      return 0
    if x > max:
      return 1
    def f(x):
      return -2 * x**3 + 3*x**2
    return f((x - min) / (max - min))

  def getNoteColor(self, note):
    if note >= len(Theme.fretColors) - 1:
      return Theme.fretColors[-1]
    elif note <= 0:
      return Theme.fretColors[0]
    f2  = note % 1.0
    f1  = 1.0 - f2
    c1 = Theme.fretColors[int(note)]
    c2 = Theme.fretColors[int(note) + 1]
    return (c1[0] * f1 + c2[0] * f2, \
            c1[1] * f1 + c2[1] * f2, \
            c1[2] * f1 + c2[2] * f2)

class LightEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    self.lightNumber = int(options.get("light_number", 0))
    self.fadeTime    = int(options.get("fade_time",    500))

  def apply(self):
    if len(self.stage.averageNotes) < self.lightNumber + 1 or not self.stage.lastPickPos:
      self.layer.color = (0.0, 0.0, 0.0, 0.0)
      return

    t  = self.stage.pos - self.stage.lastPickPos
    t  = 1.0 - self.linstep(0, self.fadeTime, t)
    t  = (0.5 + 0.5 * t) * self.intensity
    c  = self.getNoteColor(self.stage.averageNotes[self.lightNumber])

    self.layer.color = (c[0] * t, c[1] * t, c[2] * t, self.intensity)

class RotateOnMissEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    self.fadeTime = int(options.get("fade_time", 200))
    self.freq     = float(options.get("frequency",  6))

  def apply(self):
    if not self.stage.lastMissPos:
      return
    
    t  = self.stage.pos - self.stage.lastMissPos
    t  = 1.0 - self.smoothstep(0, self.fadeTime, t)

    if t:
      t = math.sin(t * self.freq)
      self.layer.drawing.transform.rotate(t * self.intensity)

class WiggleToBeatEffect(Effect):
  def __init__(self, layer, options):
    Effect.__init__(self, layer, options)
    self.fadeTime = int(options.get("fade_time", 200))
    self.delay    = int(options.get("delay", 0))
    self.freq     = float(options.get("frequency",  6))
    self.xmag     = float(options.get("xmagnitude", 0.1))
    self.ymag     = float(options.get("ymagnitude", 0.1))

  def apply(self):
    if not self.stage.lastBeatPos:
      return
    
    t  = self.stage.pos - self.stage.lastBeatPos
    t  = 1.0 - self.smoothstep(0, self.fadeTime, t)

    if t:
      w, h, = self.stage.engine.view.geometry[2:4]
      t **= 2
      s, c = t * math.sin(t * self.freq), t * math.cos(t * self.freq)
      self.layer.drawing.transform.translate(self.xmag * w * s, self.ymag * h * c)

class Stage(object):
  def __init__(self, guitarScene, configFileName):
    self.scene            = guitarScene
    self.engine           = guitarScene.engine
    self.config           = ConfigParser()
    self.backgroundLayers = []
    self.foregroundLayers = []
    self.textures         = {}
    self.reset()

    self.config.read(configFileName)

    # Build the layers
    for i in range(32):
      section = "layer%d" % i
      if self.config.has_section(section):
        def get(value, type = str, default = None):
          if self.config.has_option(section, value):
            return type(self.config.get(section, value))
          return default
        
        xres    = get("xres", int, 256)
        yres    = get("yres", int, 256)
        texture = get("texture")

        try:
          drawing = self.textures[texture]
        except KeyError:
          drawing = self.engine.loadSvgDrawing(self, None, texture, textureSize = (xres, yres))
          self.textures[texture] = drawing
          
        layer = Layer(self, drawing)

        layer.position    = (get("xpos",   float, 0.0), get("ypos",   float, 0.0))
        layer.scale       = (get("xscale", float, 1.0), get("yscale", float, 1.0))
        layer.angle       = math.pi * get("angle", float, 0.0) / 180.0
        layer.srcBlending = globals()["GL_%s" % get("src_blending", str, "src_alpha").upper()]
        layer.dstBlending = globals()["GL_%s" % get("dst_blending", str, "one_minus_src_alpha").upper()]
        layer.color       = (get("color_r", float, 1.0), get("color_g", float, 1.0), get("color_b", float, 1.0), get("color_a", float, 1.0))

        # Load any effects
        fxClasses = {
          "light":          LightEffect,
          "rotate_on_miss": RotateOnMissEffect,
          "wiggle_to_beat": WiggleToBeatEffect,
        }
        
        for j in range(32):
          fxSection = "layer%d:fx%d" % (i, j)
          if self.config.has_section(fxSection):
            type = self.config.get(fxSection, "type")

            if not type in fxClasses:
              continue

            options = self.config.options(fxSection)
            options = dict([(opt, self.config.get(fxSection, opt)) for opt in options])

            fx = fxClasses[type](layer, options)
            layer.effects.append(fx)

        if get("foreground", int):
          self.foregroundLayers.append(layer)
        else:
          self.backgroundLayers.append(layer)

  def reset(self):
    self.lastBeatPos        = None
    self.lastQuarterBeatPos = None
    self.lastMissPos        = None
    self.lastPickPos        = None
    self.beat               = 0
    self.quarterBeat        = 0
    self.pos                = 0.0
    self.playedNotes        = []
    self.averageNotes       = [0.0]

  def triggerPick(self, pos, notes):
    self.lastPickPos      = pos
    self.playedNotes      = self.playedNotes[-3:] + [sum(notes) / float(len(notes))]
    self.averageNotes[-1] = sum(self.playedNotes) / float(len(self.playedNotes))

  def triggerMiss(self, pos):
    self.lastMissPos = pos

  def triggerQuarterBeat(self, pos, quarterBeat):
    self.lastQuarterBeatPos = pos
    self.quarterBeat        = quarterBeat

  def triggerBeat(self, pos, beat):
    self.lastBeatPos  = pos
    self.beat         = beat
    self.averageNotes = self.averageNotes[-4:] + self.averageNotes[-1:]

  def _renderLayers(self, layers, visibility):
    self.engine.view.setOrthogonalProjection(normalize = True)
    try:
      for layer in layers:
        layer.render(visibility)
    finally:
      self.engine.view.resetProjection()

  def run(self, pos, period):
    self.pos    = pos
    quarterBeat = int(4 * pos / period)

    if quarterBeat > self.quarterBeat:
      self.triggerQuarterBeat(pos, quarterBeat)

    beat = quarterBeat / 4

    if beat > self.beat:
      self.triggerBeat(pos, beat)

  def render(self, visibility):
    self._renderLayers(self.backgroundLayers, visibility)
    self.scene.renderGuitar()
    self._renderLayers(self.foregroundLayers, visibility)
