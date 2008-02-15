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

from Scene import SceneServer, SceneClient
from Song import Note, TextEvent, PictureEvent, loadSong
from Menu import Menu
from Guitar import Guitar, KEYS
from Language import _
import Player
import Dialogs
import Data
import Theme
import View
import Audio
import Stage
import Settings

import math
import pygame
import random
import os
from OpenGL.GL import *

class GuitarScene:
  pass

class GuitarSceneServer(GuitarScene, SceneServer):
  pass

class GuitarSceneClient(GuitarScene, SceneClient):
  def createClient(self, libraryName, songName):
    self.guitar           = Guitar(self.engine)
    self.visibility       = 0.0
    self.libraryName      = libraryName
    self.songName         = songName
    self.done             = False
    self.sfxChannel       = self.engine.audio.getChannel(self.engine.audio.getChannelCount() - 1)
    self.lastMultTime     = None
    self.cheatCodes       = [
      ([117, 112, 116, 111, 109, 121, 116, 101, 109, 112, 111], self.toggleAutoPlay),
      ([102, 97, 115, 116, 102, 111, 114, 119, 97, 114, 100],   self.goToResults)
    ]
    self.enteredCode      = []
    self.song             = None
    self.autoPlay         = False
    self.lastPickPos      = None
    self.lastSongPos      = 0.0
    self.keyBurstTimeout  = None
    self.keyBurstPeriod   = 30
    self.camera.target    = (0, 0, 4)
    self.camera.origin    = (0, 3, -3)

    self.loadSettings()
    self.engine.resource.load(self, "song",          lambda: loadSong(self.engine, songName, library = libraryName), onLoad = self.songLoaded)
    
    self.stage            = Stage.Stage(self, self.engine.resource.fileName("stage.ini"))
    
    self.engine.loadSvgDrawing(self, "fx2x",   "2x.svg", textureSize = (256, 256))
    self.engine.loadSvgDrawing(self, "fx3x",   "3x.svg", textureSize = (256, 256))
    self.engine.loadSvgDrawing(self, "fx4x",   "4x.svg", textureSize = (256, 256))

    Dialogs.showLoadingScreen(self.engine, lambda: self.song, text = _("Tuning Guitar..."))

    settingsMenu = Settings.GameSettingsMenu(self.engine)
    settingsMenu.fadeScreen = True

    self.menu = Menu(self.engine, [
      (_("Return to Song"),    lambda: None),
      (_("Restart Song"),      self.restartSong),
      (_("Change Song"),       self.changeSong),
      (_("Settings"),          settingsMenu),
      (_("Quit to Main Menu"), self.quit),
    ], fadeScreen = True, onClose = self.resumeGame)

    self.restartSong()

  def pauseGame(self):
    if self.song:
      self.song.pause()

  def resumeGame(self):
    self.loadSettings()
    if self.song:
      self.song.unpause()

  def loadSettings(self):
    self.delay            = self.engine.config.get("audio", "delay")
    self.screwUpVolume    = self.engine.config.get("audio", "screwupvol")
    self.guitarVolume     = self.engine.config.get("audio", "guitarvol")
    self.songVolume       = self.engine.config.get("audio", "songvol")
    self.rhythmVolume     = self.engine.config.get("audio", "rhythmvol")
    self.guitar.leftyMode = self.engine.config.get("game",  "leftymode")

    if self.song:
      self.song.setBackgroundVolume(self.songVolume)
      self.song.setRhythmVolume(self.rhythmVolume)
    
  def songLoaded(self, song):
    song.difficulty = self.player.difficulty
    self.delay += song.info.delay

    # If tapping is disabled, remove the tapping indicators
    if not self.engine.config.get("game", "tapping"):
      for time, event in self.song.track.getAllEvents():
        if isinstance(event, Note):
          event.tappable = False

  def quit(self):
    if self.song:
      self.song.stop()
      self.song  = None
    self.done = True
    self.engine.view.popLayer(self.menu)
    self.session.world.finishGame()

  def changeSong(self):
    if self.song:
      self.song.stop()
      self.song  = None
    self.engine.view.popLayer(self.menu)
    self.session.world.deleteScene(self)
    self.session.world.createScene("SongChoosingScene")

  def restartSong(self):
    self.engine.data.startSound.play()
    self.engine.view.popLayer(self.menu)
    self.player.reset()
    self.stage.reset()
    self.enteredCode     = []
    self.autoPlay        = False
    self.engine.collectGarbage()
    
    if not self.song:
      return
      
    self.countdown    = 8.0
    self.guitar.endPick(0)
    self.song.stop()

  def run(self, ticks):
    SceneClient.run(self, ticks)
    pos = self.getSongPosition()

    # update song
    if self.song:
      # update stage
      self.stage.run(pos, self.guitar.currentPeriod)

      if self.countdown <= 0 and not self.song.isPlaying() and not self.done:
        self.goToResults()
        return
        
      if self.autoPlay:
        notes = self.guitar.getRequiredNotes(self.song, pos)
        notes = [note.number for time, note in notes]
        
        changed = False
        held = 0
        for n, k in enumerate(KEYS):
          if n in notes and not self.controls.getState(k):
            changed = True
            self.controls.toggle(k, True)
          elif not n in notes and self.controls.getState(k):
            changed = True
            self.controls.toggle(k, False)
          if self.controls.getState(k):
            held += 1
        if changed and held:
          self.doPick()
      
      self.song.update(ticks)
      if self.countdown > 0:
        self.guitar.setBPM(self.song.bpm)
        self.countdown = max(self.countdown - ticks / self.song.period, 0)
        if not self.countdown:
          self.engine.collectGarbage()
          self.song.setGuitarVolume(self.guitarVolume)
          self.song.setBackgroundVolume(self.songVolume)
          self.song.setRhythmVolume(self.rhythmVolume)
          self.song.play()

    # update board
    if not self.guitar.run(ticks, pos, self.controls):
      # done playing the current notes
      self.endPick()

    # missed some notes?
    if self.guitar.getMissedNotes(self.song, pos) and not self.guitar.playedNotes:
      self.song.setGuitarVolume(0.0)
      self.player.streak = 0

    # late pick
    if self.keyBurstTimeout is not None and self.engine.timer.time > self.keyBurstTimeout:
      self.keyBurstTimeout = None
      notes = self.guitar.getRequiredNotes(self.song, pos)
      if self.guitar.controlsMatchNotes(self.controls, notes):
        self.doPick()

  def endPick(self):
    score = self.getExtraScoreForCurrentlyPlayedNotes()
    if not self.guitar.endPick(self.song.getPosition()):
      self.song.setGuitarVolume(0.0)
    self.player.addScore(score)

  def render3D(self):
    self.stage.render(self.visibility)
    
  def renderGuitar(self):
    self.guitar.render(self.visibility, self.song, self.getSongPosition(), self.controls)

  def getSongPosition(self):
    if self.song:
      if not self.done:
        self.lastSongPos = self.song.getPosition()
        return self.lastSongPos - self.countdown * self.song.period - self.delay
      else:
        # Nice speeding up animation at the end of the song
        return self.lastSongPos + 4.0 * (1 - self.visibility) * self.song.period - self.delay
    return 0.0
    
  def doPick(self):
    if not self.song:
      return

    pos = self.getSongPosition()
    
    if self.guitar.playedNotes:
      # If all the played notes are tappable, there are no required notes and
      # the last note was played recently enough, ignore this pick
      if self.guitar.areNotesTappable(self.guitar.playedNotes) and \
         not self.guitar.getRequiredNotes(self.song, pos) and \
         pos - self.lastPickPos <= self.song.period / 2:
        return
      self.endPick()

    self.lastPickPos = pos

    if self.guitar.startPick(self.song, pos, self.controls):
      self.song.setGuitarVolume(self.guitarVolume)
      self.player.streak += 1
      self.player.notesHit += len(self.guitar.playedNotes)
      self.player.addScore(len(self.guitar.playedNotes) * 50)
      self.stage.triggerPick(pos, [n[1].number for n in self.guitar.playedNotes])
      if self.player.streak % 10 == 0:
        self.lastMultTime = pos
    else:
      self.song.setGuitarVolume(0.0)
      self.player.streak = 0
      self.stage.triggerMiss(pos)
      self.sfxChannel.play(self.engine.data.screwUpSound)
      self.sfxChannel.setVolume(self.screwUpVolume)
        
  def toggleAutoPlay(self):
    self.autoPlay = not self.autoPlay
    if self.autoPlay:
      Dialogs.showMessage(self.engine, _("Jurgen will show you how it is done."))
    else:
      Dialogs.showMessage(self.engine, _("Jurgen has left the building."))
    return self.autoPlay

  def goToResults(self):
    if self.song:
      self.song.stop()
      self.song  = None
      self.done  = True
      self.session.world.deleteScene(self)
      self.session.world.createScene("GameResultsScene", libraryName = self.libraryName, songName = self.songName)

  def keyPressed(self, key, unicode):
    control = self.controls.keyPressed(key)

    if control in (Player.ACTION1, Player.ACTION2):
      for k in KEYS:
        if self.controls.getState(k):
          self.keyBurstTimeout = None
          break
      else:
        self.keyBurstTimeout = self.engine.timer.time + self.keyBurstPeriod
        return True
      
    if control in (Player.ACTION1, Player.ACTION2) and self.song:
      self.doPick()
    elif control in KEYS and self.song:
      # Check whether we can tap the currently required notes
      pos   = self.getSongPosition()
      notes = self.guitar.getRequiredNotes(self.song, pos)

      if self.player.streak > 0 and \
         self.guitar.areNotesTappable(notes) and \
         self.guitar.controlsMatchNotes(self.controls, notes):
        self.doPick()
    elif control == Player.CANCEL:
      self.pauseGame()
      self.engine.view.pushLayer(self.menu)
      return True
    elif key >= ord('a') and key <= ord('z'):
      # cheat codes
      n = len(self.enteredCode)
      for code, func in self.cheatCodes:
        if n < len(code):
          if key == code[n]:
            self.enteredCode.append(key)
            if self.enteredCode == code:
              self.enteredCode     = []
              self.player.cheating = True
              func()
            break
      else:
        self.enteredCode = []
    
  def getExtraScoreForCurrentlyPlayedNotes(self):
    if not self.song:
      return 0
 
    noteCount  = len(self.guitar.playedNotes)
    pickLength = self.guitar.getPickLength(self.getSongPosition())
    if pickLength > 1.1 * self.song.period / 4:
      return int(.1 * pickLength * noteCount)
    return 0

  def keyReleased(self, key):
    if self.controls.keyReleased(key) in KEYS and self.song:
      # Check whether we can tap the currently required notes
      pos   = self.getSongPosition()
      notes = self.guitar.getRequiredNotes(self.song, pos)
      if self.player.streak > 0 and \
         self.guitar.areNotesTappable(notes) and \
         self.guitar.controlsMatchNotes(self.controls, notes):
        self.doPick()
      # Otherwise we end the pick if the notes have been playing long enough
      elif self.lastPickPos is not None and pos - self.lastPickPos > self.song.period / 2:
        self.endPick()
  def render(self, visibility, topMost):
    SceneClient.render(self, visibility, topMost)
    
    font    = self.engine.data.font
    bigFont = self.engine.data.bigFont
      
    self.visibility = v = 1.0 - ((1 - visibility) ** 2)

    self.engine.view.setOrthogonalProjection(normalize = True)
    try:
      # show countdown
      if self.countdown > 1:
        Theme.setBaseColor(min(1.0, 3.0 - abs(4.0 - self.countdown)))
        text = _("Get Ready to Rock")
        w, h = font.getStringSize(text)
        font.render(text,  (.5 - w / 2, .3))
        if self.countdown < 6:
          scale = 0.002 + 0.0005 * (self.countdown % 1) ** 3
          text = "%d" % (self.countdown)
          w, h = bigFont.getStringSize(text, scale = scale)
          Theme.setSelectedColor()
          bigFont.render(text,  (.5 - w / 2, .45 - h / 2), scale = scale)

      w, h = font.getStringSize(" ")
      y = .05 - h / 2 - (1.0 - v) * .2

      # show song name
      if self.countdown and self.song:
        Theme.setBaseColor(min(1.0, 4.0 - abs(4.0 - self.countdown)))
        Dialogs.wrapText(font, (.05, .05 - h / 2), self.song.info.name + " \n " + self.song.info.artist, rightMargin = .6, scale = 0.0015)

      Theme.setSelectedColor()
      
      font.render("%d" % (self.player.score + self.getExtraScoreForCurrentlyPlayedNotes()),  (.6, y))
      font.render("%dx" % self.player.getScoreMultiplier(), (.6, y + h))

      # show the streak counter and miss message
      if self.player.streak > 0 and self.song:
        text = _("%d hit") % self.player.streak
        factor = 0.0
        if self.lastPickPos:
            diff = self.getSongPosition() - self.lastPickPos
            if diff > 0 and diff < self.song.period * 2:
              factor = .25 * (1.0 - (diff / (self.song.period * 2))) ** 2
        factor = (1.0 + factor) * 0.002
        tw, th = font.getStringSize(text, scale = factor)
        font.render(text, (.16 - tw / 2, y + h / 2 - th / 2), scale = factor)
      elif self.lastPickPos is not None and self.countdown <= 0:
        diff = self.getSongPosition() - self.lastPickPos
        alpha = 1.0 - diff * 0.005
        if alpha > .1:
          Theme.setSelectedColor(alpha)
          glPushMatrix()
          glTranslate(.1, y + 0.000005 * diff ** 2, 0)
          glRotatef(math.sin(self.lastPickPos) * 25, 0, 0, 1)
          font.render(_("Missed!"), (0, 0))
          glPopMatrix()

      # show the streak balls
      if self.player.streak >= 30:
        glColor3f(.5, .5, 1)
      elif self.player.streak >= 20:
        glColor3f(1, 1, .5)
      elif self.player.streak >= 10:
        glColor3f(1, .5, .5)
      else:
        glColor3f(.5, 1, .5)
        
      s = min(39, self.player.streak) % 10 + 1
      font.render(Data.BALL2 * s + Data.BALL1 * (10 - s),   (.67, y + h * 1.3), scale = 0.0011)

      # show multiplier changes
      if self.song and self.lastMultTime is not None:
        diff = self.getSongPosition() - self.lastMultTime
        if diff > 0 and diff < self.song.period * 2:
          m = self.player.getScoreMultiplier()
          c = (1, 1, 1)
          if self.player.streak >= 40:
            texture = None
          elif m == 1:
            texture = None
          elif m == 2:
            texture = self.fx2x.texture
            c = (1, .5, .5)
          elif m == 3:
            texture = self.fx3x.texture
            c = (1, 1, .5)
          elif m == 4:
            texture = self.fx4x.texture
            c = (.5, .5, 1)
            
          f = (1.0 - abs(self.song.period * 1 - diff) / (self.song.period * 1)) ** 2
          
          # Flash the screen
          glBegin(GL_TRIANGLE_STRIP)
          glColor4f(c[0], c[1], c[2], (f - .5) * 1)
          glVertex2f(0, 0)
          glColor4f(c[0], c[1], c[2], (f - .5) * 1)
          glVertex2f(1, 0)
          glColor4f(c[0], c[1], c[2], (f - .5) * .25)
          glVertex2f(0, 1)
          glColor4f(c[0], c[1], c[2], (f - .5) * .25)
          glVertex2f(1, 1)
          glEnd()
            
          if texture:
            glPushMatrix()
            glEnable(GL_TEXTURE_2D)
            texture.bind()
            size = (texture.pixelSize[0] * .002, texture.pixelSize[1] * .002)
            
            glTranslatef(.5, .15, 0)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE)
            
            f = .5 + .5 * (diff / self.song.period) ** 3
            glColor4f(1, 1, 1, min(1, 2 - f))
            glBegin(GL_TRIANGLE_STRIP)
            glTexCoord2f(0.0, 0.0)
            glVertex2f(-size[0] * f, -size[1] * f)
            glTexCoord2f(1.0, 0.0)
            glVertex2f( size[0] * f, -size[1] * f)
            glTexCoord2f(0.0, 1.0)
            glVertex2f(-size[0] * f,  size[1] * f)
            glTexCoord2f(1.0, 1.0)
            glVertex2f( size[0] * f,  size[1] * f)
            glEnd()
            
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glPopMatrix()
 
      # show the comments
      if self.song and self.song.info.tutorial:
        glColor3f(1, 1, 1)
        pos = self.getSongPosition()
        for time, event in self.song.track.getEvents(pos - self.song.period * 2, pos + self.song.period * 4):
          if isinstance(event, PictureEvent):
            if pos < time or pos > time + event.length:
              continue
            
            try:
              picture = event.picture
            except:
              self.engine.loadSvgDrawing(event, "picture", os.path.join(self.libraryName, self.songName, event.fileName))
              picture = event.picture
              
            w, h, = self.engine.view.geometry[2:4]
            fadePeriod = 500.0
            f = (1.0 - min(1.0, abs(pos - time) / fadePeriod) * min(1.0, abs(pos - time - event.length) / fadePeriod)) ** 2
            picture.transform.reset()
            picture.transform.translate(w / 2, (f * -2 + 1) * h / 2)
            picture.transform.scale(1, -1)
            picture.draw()
          elif isinstance(event, TextEvent):
            if pos >= time and pos <= time + event.length:
              text = _(event.text)
              w, h = font.getStringSize(text)
              font.render(text, (.5 - w / 2, .67))
    finally:
      self.engine.view.resetProjection()
