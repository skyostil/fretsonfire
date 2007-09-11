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
from Menu import Menu
import Player
import Dialogs
import Song
import Data
import Theme
from Audio import Sound
from Language import _

import pygame
import math
import random
from OpenGL.GL import *

class GameResultsScene:
  pass

class GameResultsSceneServer(GameResultsScene, SceneServer):
  pass

class GameResultsSceneClient(GameResultsScene, SceneClient):
  def createClient(self, libraryName, songName):
    self.libraryName     = libraryName
    self.songName        = songName
    self.stars           = 0
    self.accuracy        = 0
    self.counter         = 0
    self.showHighscores  = False
    self.highscoreIndex  = None
    self.taunt           = None
    self.uploadingScores = False
    self.nextScene       = None
    
    items = [
      (_("Replay"),            self.replay),
      (_("Change Song"),       self.changeSong),
      (_("Quit to Main Menu"), self.quit),
    ]
    self.menu = Menu(self.engine, items, onCancel = self.quit, pos = (.2, .5))
      
    self.engine.resource.load(self, "song", lambda: Song.loadSong(self.engine, songName, library = self.libraryName, notesOnly = True), onLoad = self.songLoaded)
    self.engine.loadSvgDrawing(self, "background", "keyboard.svg")
    Dialogs.showLoadingScreen(self.engine, lambda: self.song, text = _("Chilling..."))
    
  def keyPressed(self, key, unicode):
    ret = SceneClient.keyPressed(self, key, unicode)

    c = self.controls.keyPressed(key)
    if self.song and (c in [Player.KEY1, Player.KEY2, Player.CANCEL, Player.ACTION1, Player.ACTION2] or key == pygame.K_RETURN):
      scores = self.song.info.getHighscores(self.player.difficulty)
      if not scores or self.player.score > scores[-1][0] or len(scores) < 5:
        if self.player.cheating:
          Dialogs.showMessage(self.engine, _("No highscores for cheaters!"))
        else:
          name = Dialogs.getText(self.engine, _("%d points is a new high score! Please enter your name:") % self.player.score, self.player.name)
          if name:
            self.player.name = name
          self.highscoreIndex = self.song.info.addHighscore(self.player.difficulty, self.player.score, self.stars, self.player.name)
          self.song.info.save()

          if self.engine.config.get("game", "uploadscores"):
            self.uploadingScores = True
            fn = lambda: self.song.info.uploadHighscores(self.engine.config.get("game", "uploadurl"), self.song.getHash())
            self.engine.resource.load(self, "uploadResult", fn)

      self.showHighscores = True
      self.engine.view.pushLayer(self.menu)
      return True
    
    return ret

  def hidden(self):
    SceneClient.hidden(self)
    if self.nextScene:
      self.nextScene()
    
  def quit(self):
    self.engine.view.popLayer(self.menu)
    self.session.world.finishGame()
    
  def replay(self):
    self.engine.view.popLayer(self.menu)
    self.session.world.deleteScene(self)
    self.nextScene = lambda: self.session.world.createScene("GuitarScene", libraryName = self.libraryName, songName = self.songName)
  
  def changeSong(self):
    self.engine.view.popLayer(self.menu)
    self.session.world.deleteScene(self)
    self.nextScene = lambda: self.session.world.createScene("SongChoosingScene")
   
  def songLoaded(self, song):
    song.difficulty = self.player.difficulty
    notes = len([1 for time, event in song.track.getAllEvents() if isinstance(event, Song.Note)])
    
    if notes:
      # 5 stars at 95%, 4 stars at 75%
      f = float(self.player.notesHit) / notes
      self.stars    = int(5.0   * (f + .05))
      self.accuracy = int(100.0 * f)

      taunt = None
      if self.player.score == 0:
        taunt = "jurgen1.ogg"
      elif self.accuracy >= 99.0:
        taunt = "myhero.ogg"
      elif self.stars in [0, 1]:
        taunt = random.choice(["jurgen2.ogg", "jurgen3.ogg", "jurgen4.ogg", "jurgen5.ogg"])
      elif self.stars == 5:
        taunt = random.choice(["perfect1.ogg", "perfect2.ogg", "perfect3.ogg"])
        
      if taunt:
        self.engine.resource.load(self, "taunt", lambda: Sound(self.engine.resource.fileName(taunt)))

  def run(self, ticks):
    SceneClient.run(self, ticks)
    self.time    += ticks / 50.0
    self.counter += ticks
    
    if self.counter > 5000 and self.taunt:
      self.taunt.setVolume(self.engine.config.get("audio", "guitarvol"))
      self.taunt.play()
      self.taunt = None
    
  def anim(self, start, ticks):
    return min(1.0, float(max(start, self.counter)) / ticks)

  def render(self, visibility, topMost):
    SceneClient.render(self, visibility, topMost)
    
    bigFont = self.engine.data.bigFont
    font    = self.engine.data.font

    v = ((1 - visibility) ** 2)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glEnable(GL_COLOR_MATERIAL)

    self.engine.view.setOrthogonalProjection(normalize = True)
    try:
      t = self.time / 100
      w, h, = self.engine.view.geometry[2:4]
      r = .5
      self.background.transform.reset()
      self.background.transform.translate(v * 2 * w + w / 2 + math.cos(t / 2) * w / 2 * r, h / 2 + math.sin(t) * h / 2 * r)
      self.background.transform.rotate(-t)
      self.background.transform.scale(math.sin(t / 8) + 2, math.sin(t / 8) + 2)
      self.background.draw()
      
      if self.showHighscores:
        scale = 0.0017
        d = self.player.difficulty
        
        text = _("Highest Scores (%s)") % d
        w, h = font.getStringSize(text)
        Theme.setBaseColor(1 - v)
        font.render(text, (.5 - w / 2, .05 - v))
        
        x = .1
        y = .15 + v
        for i, scores in enumerate(self.song.info.getHighscores(d)):
          score, stars, name = scores
          if i == self.highscoreIndex and (self.time % 10.0) < 5.0:
            Theme.setSelectedColor(1 - v)
          else:
            Theme.setBaseColor(1 - v)
          font.render("%d." % (i + 1), (x, y),    scale = scale)
          font.render(unicode(score), (x + .05, y),   scale = scale)
          font.render(unicode(Data.STAR2 * stars + Data.STAR1 * (5 - stars)), (x + .25, y), scale = scale * .9)
          font.render(name, (x + .5, y), scale = scale)
          y += h
          
        if self.uploadingScores:
          Theme.setBaseColor(1 - v)
          if self.uploadResult is None:
            text = _("Uploading Scores...")
          else:
            success, ordinal = self.uploadResult
            if success:
              if ordinal > 0:
                text = _("You're #%d on the world charts!") % ordinal
              else:
                text = ""
            else:
              text = _("Score upload failed")
          font.render(text, (.05, .7 + v), scale = 0.001)
        return
      
      Theme.setBaseColor(1 - v)
      text = _("Song Finished!")
      w, h = font.getStringSize(text)
      font.render(text, (.5 - w / 2, .05 - v))
      
      text = "%d" % (self.player.score * self.anim(1000, 2000))
      w, h = bigFont.getStringSize(text)
      bigFont.render(text, (.5 - w / 2, .11 + v + (1.0 - self.anim(0, 1000) ** 3)), scale = 0.0025)
      
      if self.counter > 1000:
        scale = 0.0017
        text = (Data.STAR2 * self.stars + Data.STAR1 * (5 - self.stars))
        w, h = bigFont.getStringSize(Data.STAR1, scale = scale)
        x = .5 - w * len(text) / 2
        for i, ch in enumerate(text):
          bigFont.render(ch, (x + 100 * (1.0 - self.anim(1000 + i * 200, 1000 + (i + 1) * 200)) ** 2, .35 + v), scale = scale)
          x += w
      
      if self.counter > 2500:
        text = _("Accuracy: %d%%") % self.accuracy      
        w, h = font.getStringSize(text)
        font.render(text, (.5 - w / 2, .55 + v))
        text = _("Longest note streak: %d") % self.player.longestStreak
        w, h = font.getStringSize(text)
        font.render(text, (.5 - w / 2, .55 + h + v))
    finally:
      self.engine.view.resetProjection()
