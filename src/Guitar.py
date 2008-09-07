#####################################################################
# -*- coding: iso-8859-1 -*-                                        #
#                                                                   #
# Frets on Fire                                                     #
# Copyright (C) 2006 Sami Kyostila                                  #
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

import Player
from Song import Note, Tempo
from Mesh import Mesh
import Theme

from OpenGL.GL import *
import math
import numpy

KEYS = [Player.KEY1, Player.KEY2, Player.KEY3, Player.KEY4, Player.KEY5]

class Guitar:
  def __init__(self, engine, editorMode = False):
    self.engine         = engine
    self.boardWidth     = 4.0
    self.boardLength    = 12.0
    self.beatsPerBoard  = 5.0
    self.strings        = 5
    self.fretWeight     = [0.0] * self.strings
    self.fretActivity   = [0.0] * self.strings
    self.fretColors     = Theme.fretColors
    self.playedNotes    = []
    self.editorMode     = editorMode
    self.selectedString = 0
    self.time           = 0.0
    self.pickStartPos   = 0
    self.leftyMode      = False
    self.currentBpm     = 50.0
    self.currentPeriod  = 60000.0 / self.currentBpm
    self.targetBpm      = self.currentBpm
    self.lastBpmChange  = -1.0
    self.baseBeat       = 0.0
    self.setBPM(self.currentBpm)
    self.vertexCache    = numpy.empty((8 * 4096, 3), numpy.float32)
    self.colorCache     = numpy.empty((8 * 4096, 4), numpy.float32)

    engine.resource.load(self,  "noteMesh", lambda: Mesh(engine.resource.fileName("note.dae")))
    engine.resource.load(self,  "keyMesh",  lambda: Mesh(engine.resource.fileName("key.dae")))
    engine.loadSvgDrawing(self, "glowDrawing", "glow.png")
    engine.loadSvgDrawing(self, "neckDrawing", "neck.png")
    engine.loadSvgDrawing(self, "stringDrawing", "string.png")
    engine.loadSvgDrawing(self, "barDrawing", "bar.png")
    engine.loadSvgDrawing(self, "noteDrawing", "note.png")

  def selectPreviousString(self):
    self.selectedString = (self.selectedString - 1) % self.strings

  def selectString(self, string):
    self.selectedString = string % self.strings

  def selectNextString(self):
    self.selectedString = (self.selectedString + 1) % self.strings

  def setBPM(self, bpm):
    self.earlyMargin       = 60000.0 / bpm / 3.5
    self.lateMargin        = 60000.0 / bpm / 3.5
    self.noteReleaseMargin = 60000.0 / bpm / 2
    self.bpm               = bpm
    self.baseBeat          = 0.0
      
  def renderNeck(self, visibility, song, pos):
    if not song:
      return

    def project(beat):
      return .5 * beat / beatsPerUnit

    v            = visibility
    w            = self.boardWidth
    l            = self.boardLength
    beatsPerUnit = self.beatsPerBoard / self.boardLength
    offset       = (pos - self.lastBpmChange) / self.currentPeriod + self.baseBeat

    glEnable(GL_TEXTURE_2D)
    self.neckDrawing.texture.bind()
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    
    glBegin(GL_TRIANGLE_STRIP)
    glColor4f(1, 1, 1, 0)
    glTexCoord2f(0.0, project(offset - 2 * beatsPerUnit))
    glVertex3f(-w / 2, 0, -2)
    glTexCoord2f(1.0, project(offset - 2 * beatsPerUnit))
    glVertex3f( w / 2, 0, -2)
    
    glColor4f(1, 1, 1, v)
    glTexCoord2f(0.0, project(offset - 1 * beatsPerUnit))
    glVertex3f(-w / 2, 0, -1)
    glTexCoord2f(1.0, project(offset - 1 * beatsPerUnit))
    glVertex3f( w / 2, 0, -1)
    
    glTexCoord2f(0.0, project(offset + l * beatsPerUnit * .7))
    glVertex3f(-w / 2, 0, l * .7)
    glTexCoord2f(1.0, project(offset + l * beatsPerUnit * .7))
    glVertex3f( w / 2, 0, l * .7)
    
    glColor4f(1, 1, 1, 0)
    glTexCoord2f(0.0, project(offset + l * beatsPerUnit))
    glVertex3f(-w / 2, 0, l)
    glTexCoord2f(1.0, project(offset + l * beatsPerUnit))
    glVertex3f( w / 2, 0, l)
    glEnd()
    
    glDisable(GL_TEXTURE_2D)
    
  def renderTracks(self, visibility):
    w = self.boardWidth / self.strings
    v = 1.0 - visibility

    if self.editorMode:
      x = (self.strings / 2 - self.selectedString) * w
      s = 2 * w / self.strings
      z1 = -0.5 * visibility ** 2
      z2 = (self.boardLength - 0.5) * visibility ** 2
      
      glColor4f(1, 1, 1, .15)
      
      glBegin(GL_TRIANGLE_STRIP)
      glVertex3f(x - s, 0, z1)
      glVertex3f(x + s, 0, z1)
      glVertex3f(x - s, 0, z2)
      glVertex3f(x + s, 0, z2)
      glEnd()

    sw = 0.035
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    Theme.setBaseColor(1 - v)
    self.stringDrawing.texture.bind()
    for n in range(self.strings - 1, -1, -1):
      glBegin(GL_TRIANGLE_STRIP)
      glTexCoord2f(0.0, 0.0)
      glVertex3f((n - self.strings / 2) * w - sw, -v, -2)
      glTexCoord2f(1.0, 0.0)
      glVertex3f((n - self.strings / 2) * w + sw, -v, -2)
      glTexCoord2f(0.0, 1.0)
      glVertex3f((n - self.strings / 2) * w - sw, -v, self.boardLength)
      glTexCoord2f(1.0, 1.0)
      glVertex3f((n - self.strings / 2) * w + sw, -v, self.boardLength)
      glEnd()
      v *= 2
    glDisable(GL_TEXTURE_2D)
      
  def renderBars(self, visibility, song, pos):
    if not song:
      return
    
    w            = self.boardWidth
    v            = 1.0 - visibility
    sw           = 0.04
    beatsPerUnit = self.beatsPerBoard / self.boardLength
    pos         -= self.lastBpmChange
    offset       = pos / self.currentPeriod * beatsPerUnit
    currentBeat  = pos / self.currentPeriod
    beat         = int(currentBeat)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_TEXTURE_2D)
    self.barDrawing.texture.bind()
     
    glPushMatrix()
    while beat < currentBeat + self.beatsPerBoard:
      z = (beat - currentBeat) / beatsPerUnit

      if z > self.boardLength * .8:
        c = (self.boardLength - z) / (self.boardLength * .2)
      elif z < 0:
        c = max(0, 1 + z)
      else:
        c = 1.0
        
      glRotate(v * 90, 0, 0, 1)

      if (beat % 1.0) < 0.001:
        Theme.setBaseColor(visibility * c * .75)
      else:
        Theme.setBaseColor(visibility * c * .5)

      glBegin(GL_TRIANGLE_STRIP)
      glTexCoord2f(0.0, 0.0)
      glVertex3f(-(w / 2), -v, z + sw)
      glTexCoord2f(0.0, 1.0)
      glVertex3f(-(w / 2), -v, z - sw)
      glTexCoord2f(1.0, 0.0)
      glVertex3f(w / 2,    -v, z + sw)
      glTexCoord2f(1.0, 1.0)
      glVertex3f(w / 2,    -v, z - sw)
      glEnd()
      
      if self.editorMode:
        beat += 1.0 / 4.0
      else:
        beat += 1
    glPopMatrix()

    Theme.setSelectedColor(visibility * .5)
    glBegin(GL_TRIANGLE_STRIP)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-w / 2, 0,  sw)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-w / 2, 0, -sw)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(w / 2,  0,  sw)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(w / 2,  0, -sw)
    glEnd()

    glDisable(GL_TEXTURE_2D)

  def renderNote(self, length, color, flat = False, tailOnly = False, isTappable = False):
    if not self.noteMesh:
      return

    glColor4f(*color)
    glEnable(GL_TEXTURE_2D)
    self.noteDrawing.texture.bind()

    if flat:
      glScalef(1, .1, 1)

    size = (.1, length + 0.00001)
    glBegin(GL_TRIANGLE_STRIP)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-size[0], 0, 0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f( size[0], 0, 0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-size[0], 0, size[1])
    glTexCoord2f(1.0, 1.0)
    glVertex3f( size[0], 0, size[1])
    glEnd()
    glDisable(GL_TEXTURE_2D)

    if tailOnly:
      return
    
    glPushMatrix()
    glEnable(GL_DEPTH_TEST)
    glDepthMask(1)
    if color[3] > .9:
      glDisable(GL_BLEND)
    glShadeModel(GL_SMOOTH)
    self.noteMesh.render("Mesh_001")
    if isTappable:
      self.noteMesh.render("Mesh_003")
    glColor4f(.75 * color[0], .75 * color[1], .75 * color[2], color[3])
    self.noteMesh.render("Mesh")
    glColor4f(.25 * color[0], .25 * color[1], .25 * color[2], color[3])
    self.noteMesh.render("Mesh_002")
    glDepthMask(0)
    glPopMatrix()
    glEnable(GL_BLEND)

  def renderNotes(self, visibility, song, pos):
    if not song:
      return

    # Update dynamic period
    self.currentPeriod = 60000.0 / self.currentBpm
    self.targetPeriod  = 60000.0 / self.targetBpm

    beatsPerUnit = self.beatsPerBoard / self.boardLength
    w = self.boardWidth / self.strings
    track = song.track

    for time, event in track.getEvents(pos - self.currentPeriod * 2, pos + self.currentPeriod * self.beatsPerBoard):
      if isinstance(event, Tempo):
        if (pos - time > self.currentPeriod or self.lastBpmChange < 0) and time > self.lastBpmChange:
          self.baseBeat         += (time - self.lastBpmChange) / self.currentPeriod
          self.targetBpm         = event.bpm
          self.lastBpmChange     = time
        continue
      
      if not isinstance(event, Note):
        continue
        
      c = self.fretColors[event.number]

      x  = (self.strings / 2 - event.number) * w
      z  = ((time - pos) / self.currentPeriod) / beatsPerUnit
      z2 = ((time + event.length - pos) / self.currentPeriod) / beatsPerUnit

      if z > self.boardLength * .8:
        f = (self.boardLength - z) / (self.boardLength * .2)
      elif z < 0:
        f = min(1, max(0, 1 + z2))
      else:
        f = 1.0

      color      = (.1 + .8 * c[0], .1 + .8 * c[1], .1 + .8 * c[2], 1 * visibility * f)
      length     = event.length / self.currentPeriod / beatsPerUnit
      flat       = False
      tailOnly   = False
      isTappable = event.tappable
      
      # Clip the played notes to the origin
      if z < 0:
        if event.played:
          tailOnly = True
          length += z
          z = 0
          if length <= 0:
            continue
        else:
          color = (.2 + .4, .2 + .4, .2 + .4, .5 * visibility * f)
          flat  = True

      glPushMatrix()
      glTranslatef(x, (1.0 - visibility) ** (event.number + 1), z)
      self.renderNote(length, color = color, flat = flat, tailOnly = tailOnly, isTappable = isTappable)
      glPopMatrix()

    # Draw a waveform shape over the currently playing notes
    vertices = self.vertexCache
    colors   = self.colorCache

    glBlendFunc(GL_SRC_ALPHA, GL_ONE)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_COLOR_ARRAY)
    glVertexPointer(3, GL_FLOAT, 0, vertices)
    glColorPointer(4, GL_FLOAT, 0, colors)

    for time, event in self.playedNotes:
      t     = time + event.length
      dt    = t - pos
      proj  = 1.0 / self.currentPeriod / beatsPerUnit

      # Increase these values to improve performance
      step1 = dt * proj * 25
      step2 = 10.0

      if dt < 1e-3:
        continue

      dStep = (step2 - step1) / dt
      x     = (self.strings / 2 - event.number) * w
      c     = self.fretColors[event.number]
      s     = t
      step  = step1

      vertexCount    = 0

      def waveForm(t):
        u = ((t - time) * -.1 + pos - time) / 64.0 + .0001
        return (math.sin(event.number + self.time * -.01 + t * .03) + math.cos(event.number + self.time * .01 + t * .02)) * .1 + .1 + math.sin(u) / (5 * u)

      i     = 0
      a1    = 0.0
      zStep = step * proj

      while t > time and t - step > pos and i < len(vertices) / 8:
        z  = (t - pos) * proj
        a2 = waveForm(t - step)

        colors[i    ]   = \
        colors[i + 1]   = (c[0], c[1], c[2], .5)
        colors[i + 2]   = \
        colors[i + 3]   = (1, 1, 1, .75)
        colors[i + 4]   = \
        colors[i + 5]   = \
        colors[i + 6]   = \
        colors[i + 7]   = (c[0], c[1], c[2], .5)
        vertices[i    ] = (x - a1, 0, z)
        vertices[i + 1] = (x - a2, 0, z - zStep)
        vertices[i + 2] = (x, 0, z)
        vertices[i + 3] = (x, 0, z - zStep)
        vertices[i + 4] = (x + a1, 0, z)
        vertices[i + 5] = (x + a2, 0, z - zStep)
        vertices[i + 6] = (x + a2, 0, z - zStep)
        vertices[i + 7] = (x - a2, 0, z - zStep)

        i    += 8
        t    -= step
        a1    = a2
        step  = step1 + dStep * (s - t)
        zStep = step * proj

      glDrawArrays(GL_TRIANGLE_STRIP, 0, i)
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_COLOR_ARRAY)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

  def renderFrets(self, visibility, song, controls):
    w = self.boardWidth / self.strings
    v = 1.0 - visibility
    
    glEnable(GL_DEPTH_TEST)
    
    for n in range(self.strings):
      f = self.fretWeight[n]
      c = self.fretColors[n]

      if f and (controls.getState(Player.ACTION1) or controls.getState(Player.ACTION2)):
        f += 0.25

      glColor4f(.1 + .8 * c[0] + f, .1 + .8 * c[1] + f, .1 + .8 * c[2] + f, visibility)
      y = v + f / 6
      x = (self.strings / 2 - n) * w

      if self.keyMesh:
        glPushMatrix()
        glTranslatef(x, y + v * 6, 0)
        glDepthMask(1)
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glShadeModel(GL_SMOOTH)
        glRotatef(90, 0, 1, 0)
        glLightfv(GL_LIGHT0, GL_POSITION, (5.0, 10.0, -10.0, 0.0))
        glLightfv(GL_LIGHT0, GL_AMBIENT,  (.2, .2, .2, 0.0))
        glLightfv(GL_LIGHT0, GL_DIFFUSE,  (1.0, 1.0, 1.0, 0.0))
        glRotatef(-90, 1, 0, 0)
        glRotatef(-90, 0, 0, 1)
        self.keyMesh.render()
        glDisable(GL_LIGHTING)
        glDisable(GL_LIGHT0)
        glDepthMask(0)
        glPopMatrix()

      f = self.fretActivity[n]

      if f:
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        s = 0.0
        self.glowDrawing.texture.bind()

        glEnable(GL_TEXTURE_2D)
        glDisable(GL_DEPTH_TEST)
        glPushMatrix()
        glTranslate(x, y, 0)
        glRotate(f + self.time * .1, 0, 1, 0)
        size = (.22 * (f + 1.5), .22 * (f + 1.5))

        if self.playedNotes:
          t = math.cos(math.pi + (self.time - self.playedNotes[0][0]) * 0.01)
        else:
          t = math.cos(self.time * 0.01)

        while s < .5:
          ms = (1 - s) * f * t * .25 + .75
          glColor3f(c[0] * ms, c[1] * ms, c[2] * ms)
          glBegin(GL_TRIANGLE_STRIP)
          glTexCoord2f(0.0, 0.0)
          glVertex3f(-size[0] * f, 0, -size[1] * f)
          glTexCoord2f(1.0, 0.0)
          glVertex3f( size[0] * f, 0, -size[1] * f)
          glTexCoord2f(0.0, 1.0)
          glVertex3f(-size[0] * f, 0,  size[1] * f)
          glTexCoord2f(1.0, 1.0)
          glVertex3f( size[0] * f, 0,  size[1] * f)
          glEnd()
          glTranslatef(0, ms * .2, 0)
          glScalef(.8, 1, .8)
          glRotate(ms * 20, 0, 1, 0)
          s += 0.2

        glPopMatrix()
        glEnable(GL_DEPTH_TEST)

        glDisable(GL_TEXTURE_2D)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

      v *= 1.5
    glDisable(GL_DEPTH_TEST)

  def render(self, visibility, song, pos, controls):
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_COLOR_MATERIAL)
    if self.leftyMode:
      glScalef(-1, 1, 1)

    self.renderNeck(visibility, song, pos)
    self.renderTracks(visibility)
    self.renderBars(visibility, song, pos)
    self.renderNotes(visibility, song, pos)
    self.renderFrets(visibility, song, controls)
    if self.leftyMode:
      glScalef(-1, 1, 1)

  def getMissedNotes(self, song, pos):
    if not song:
      return

    m1      = self.lateMargin
    m2      = self.lateMargin * 2
    track   = song.track
    notes   = [(time, event) for time, event in track.getEvents(pos - m1, pos - m2) if isinstance(event, Note)]
    notes   = [(time, event) for time, event in notes if (time >= (pos - m2)) and (time <= (pos - m1))]
    notes   = [(time, event) for time, event in notes if not event.played]

    return notes
    
  def getRequiredNotes(self, song, pos):
    track = song.track
    notes = [(time, event) for time, event in track.getEvents(pos - self.lateMargin, pos + self.earlyMargin) if isinstance(event, Note)]
    notes = [(time, event) for time, event in notes if not event.played]
    notes = [(time, event) for time, event in notes if (time >= (pos - self.lateMargin)) and (time <= (pos + self.earlyMargin))]
    if notes:
      t     = min([time for time, event in notes])
      notes = [(time, event) for time, event in notes if time - t < 1e-3]
    return notes

  def controlsMatchNotes(self, controls, notes):
    result = True
    
    # no notes?
    if not notes:
      result = False

    # check each valid chord
    chords = {}
    for time, note in notes:
      if not time in chords:
        chords[time] = []
      chords[time].append((time, note))

    for notes in chords.values():
      # matching keys?
      requiredKeys = [note.number for time, note in notes]

      for n, k in enumerate(KEYS):
        if n in requiredKeys and not controls.getState(k):
          result = False
          break
        if not n in requiredKeys and controls.getState(k):
          # The lower frets can be held down
          if n > max(requiredKeys):
            result = False
            break
    return result

  def areNotesTappable(self, notes):
    if not notes:
      return
    for time, note in notes:
      if not note.tappable:
        return False
    return True
  
  def startPick(self, song, pos, controls):
    if not song:
      return False
    
    self.playedNotes = []
    notes = self.getRequiredNotes(song, pos)
    match = self.controlsMatchNotes(controls, notes)

    """
    if match:
      print "\033[0m",
    else:
      print "\033[31m",
    print "MATCH?",
    n = [note.number for time, note in notes]
    for i, k in enumerate(KEYS):
      if i in n:
        if controls.getState(k):
          print " [#] ",
        else:
          print "  #  ",
      else:
        if controls.getState(k):
          print " [.] ",
        else:
          print "  .  ",
    print
    """

    if match:
      self.pickStartPos = pos
      for time, note in notes:
        self.pickStartPos = max(self.pickStartPos, time)
        note.played       = True
      self.playedNotes = notes
      return True
    return False

  def endPick(self, pos):
    for time, note in self.playedNotes:
      if time + note.length > pos + self.noteReleaseMargin:
        self.playedNotes = []
        return False
      
    self.playedNotes = []
    return True
    
  def getPickLength(self, pos):
    if not self.playedNotes:
      return 0.0
    
    # The pick length is limited by the played notes
    pickLength = pos - self.pickStartPos
    for time, note in self.playedNotes:
      pickLength = min(pickLength, note.length)
    return pickLength

  def run(self, ticks, pos, controls):
    self.time += ticks
    
    # update frets
    if self.editorMode:
      if (controls.getState(Player.ACTION1) or controls.getState(Player.ACTION2)):
        activeFrets = [i for i, k in enumerate(KEYS) if controls.getState(k)] or [self.selectedString]
      else:
        activeFrets = []
    else:
      activeFrets = [note.number for time, note in self.playedNotes]
    
    for n in range(self.strings):
      if controls.getState(KEYS[n]) or (self.editorMode and self.selectedString == n):
        self.fretWeight[n] = 0.5
      else:
        self.fretWeight[n] = max(self.fretWeight[n] - ticks / 64.0, 0.0)
      if n in activeFrets:
        self.fretActivity[n] = min(self.fretActivity[n] + ticks / 32.0, 1.0)
      else:
        self.fretActivity[n] = max(self.fretActivity[n] - ticks / 64.0, 0.0)

    for time, note in self.playedNotes:
      if pos > time + note.length:
        return False

    # update bpm
    diff = self.targetBpm - self.currentBpm
    self.currentBpm += diff * .03

    return True
