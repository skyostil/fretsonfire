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
import Config
import Song
from Language import _

LEFT    = 0x1
RIGHT   = 0x2
UP      = 0x4
DOWN    = 0x8
ACTION1 = 0x10
ACTION2 = 0x20
KEY1    = 0x40
KEY2    = 0x80
KEY3    = 0x100
KEY4    = 0x200
KEY5    = 0x400
CANCEL  = 0x800

SCORE_MULTIPLIER = [0, 10, 20, 30]

# define configuration keys
Config.define("player", "key_left",     str, "K_LEFT",   text = _("Move left"))
Config.define("player", "key_right",    str, "K_RIGHT",  text = _("Move right"))
Config.define("player", "key_up",       str, "K_UP",     text = _("Move up"))
Config.define("player", "key_down",     str, "K_DOWN",   text = _("Move down"))
Config.define("player", "key_action1",  str, "K_RETURN", text = _("Pick"))
Config.define("player", "key_action2",  str, "K_RSHIFT", text = _("Secondary Pick"))
Config.define("player", "key_1",        str, "K_F1",     text = _("Fret #1"))
Config.define("player", "key_2",        str, "K_F2",     text = _("Fret #2"))
Config.define("player", "key_3",        str, "K_F3",     text = _("Fret #3"))
Config.define("player", "key_4",        str, "K_F4",     text = _("Fret #4"))
Config.define("player", "key_5",        str, "K_F5",     text = _("Fret #5"))
Config.define("player", "key_cancel",   str, "K_ESCAPE", text = _("Cancel"))
Config.define("player", "name",         str, "")
Config.define("player", "difficulty",   int, Song.EASY_DIFFICULTY)

class Controls:
  def __init__(self):
    def keycode(name):
      k = Config.get("player", name)
      try:
        return int(k)
      except:
        return getattr(pygame, k)
    
    self.flags = 0
    self.controlMapping = {
      keycode("key_left"):      LEFT,
      keycode("key_right"):     RIGHT,
      keycode("key_up"):        UP,
      keycode("key_down"):      DOWN,
      keycode("key_action1"):   ACTION1,
      keycode("key_action2"):   ACTION2,
      keycode("key_1"):         KEY1,
      keycode("key_2"):         KEY2,
      keycode("key_3"):         KEY3,
      keycode("key_4"):         KEY4,
      keycode("key_5"):         KEY5,
      keycode("key_cancel"):    CANCEL,
    }
    
    # Multiple key support
    self.heldKeys = {}

  def getMapping(self, key):
    return self.controlMapping.get(key)

  def keyPressed(self, key):
    c = self.getMapping(key)
    if c:
      self.toggle(c, True)
      if c in self.heldKeys and not key in self.heldKeys[c]:
        self.heldKeys[c].append(key)
      return c
    return None

  def keyReleased(self, key):
    c = self.getMapping(key)
    if c:
      if c in self.heldKeys:
        if key in self.heldKeys[c]:
          self.heldKeys[c].remove(key)
          if not self.heldKeys[c]:
            self.toggle(c, False)
            return c
        return None
      self.toggle(c, False)
      return c
    return None

  def toggle(self, control, state):
    prevState = self.flags
    if state:
      self.flags |= control
      return not prevState & control
    else:
      self.flags &= ~control
      return prevState & control

  def getState(self, control):
    return self.flags & control

class Player(object):
  def __init__(self, owner, name):
    self.owner    = owner
    self.controls = Controls()
    self.reset()
    
  def reset(self):
    self.score         = 0
    self._streak       = 0
    self.notesHit      = 0
    self.longestStreak = 0
    self.cheating      = False
    
  def getName(self):
    return Config.get("player", "name")
    
  def setName(self, name):
    Config.set("player", "name", name)
    
  name = property(getName, setName)
  
  def getStreak(self):
    return self._streak
    
  def setStreak(self, value):
    self._streak = value
    self.longestStreak = max(self._streak, self.longestStreak)
    
  streak = property(getStreak, setStreak)
    
  def getDifficulty(self):
    return Song.difficulties.get(Config.get("player", "difficulty"))
    
  def setDifficulty(self, difficulty):
    Config.set("player", "difficulty", difficulty.id)
    
  difficulty = property(getDifficulty, setDifficulty)
  
  def addScore(self, score):
    self.score += score * self.getScoreMultiplier()
    
  def getScoreMultiplier(self):
    try:
      return SCORE_MULTIPLIER.index((self.streak / 10) * 10) + 1
    except ValueError:
      return len(SCORE_MULTIPLIER)
