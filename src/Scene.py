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

from Player import Player
from View import BackgroundLayer
from Session import MessageHandler, Message
from Input import KeyListener
from Camera import Camera
import Network
import Player
import Config

from OpenGL.GL import *
from OpenGL.GLU import *
import math
import colorsys
import pygame

Config.define("network", "updateinterval", int, 72)

# Messages from client to server
class CreateActor(Message): pass
class ControlEvent(Message): pass

# Messages from server to client
class ActorCreated(Message): pass
class ActorDeleted(Message): pass
class ActorData(Message): pass
class ControlData(Message): pass

class Scene(MessageHandler, BackgroundLayer):
  def __init__(self, engine, owner, **args):
    self.objects = Network.ObjectCollection()
    self.args    = args
    self.owner   = owner
    self.engine  = engine
    self.actors  = []
    self.camera  = Camera()
    self.world   = None
    self.space   = None
    self.time    = 0.0
    self.actors  = []
    self.players = []
    self.createCommon(**args)

  def addPlayer(self, player):
    self.players.append(player)

  def removePlayer(self, player):
    self.players.remove(player)

  def createCommon(self, **args):
    pass

  def runCommon(self, ticks, world):
    pass
    
  def run(self, ticks):
    self.time += ticks / 50.0

  def handleActorCreated(self, sender, id, owner, name):
    actor = globals()[name](self, owner)
    self.objects[id] = actor
    self.actors.append(actor)

  def handleActorDeleted(self, sender, id):
    actor = self.objects[id]
    self.actors.remove(actor)
    del self.objects[id]

class SceneClient(Scene, KeyListener):
  def __init__(self, engine, owner, session, **args):
    Scene.__init__(self, engine, owner, **args)
    self.session = session
    self.player = self.session.world.getLocalPlayer()
    self.controls = Player.Controls()
    self.createClient(**args)

  def createClient(self, **args):
    pass

  def createActor(self, name):
    self.session.sendMessage(CreateActor(name = name))

  def shown(self):
    self.engine.input.addKeyListener(self)

  def hidden(self):
    self.engine.input.removeKeyListener(self)

  def keyPressed(self, key, unicode):
    c = self.controls.keyPressed(key)
    if c:
      self.session.sendMessage(ControlEvent(flags = self.controls.flags))
      return True
    return False

  def keyReleased(self, key):
    c = self.controls.keyReleased(key)
    if c:
      self.session.sendMessage(ControlEvent(flags = self.controls.flags))
      return True
    return False

  def handleControlData(self, sender, owner, flags):
    # TODO: player mapping
    for player in self.session.world.players:
      if player.owner == owner:
        player.controls.flags = flags
        break

  def handleActorData(self, sender, id, data):
    actor = self.objects[id]
    actor.setState(*data)

  def run(self, ticks):
    self.runCommon(ticks, self.session.world)
    Scene.run(self, ticks)
    
  def render3D(self):
    for actor in self.actors:
      actor.render()

  def render(self, visibility, topMost):
    font = self.engine.data.font

    # render the scene
    try:
      glMatrixMode(GL_PROJECTION)
      glPushMatrix()
      glLoadIdentity()
      gluPerspective(60, self.engine.view.aspectRatio, 0.1, 1000)
      glMatrixMode(GL_MODELVIEW)
      glLoadIdentity()
      
      glPushMatrix()
      self.camera.apply()
  
      self.render3D()
    finally:
      glPopMatrix()
      glMatrixMode(GL_PROJECTION)
      glPopMatrix()
      glMatrixMode(GL_MODELVIEW)

class SceneServer(Scene):
  def __init__(self, engine, owner, server, **args):
    Scene.__init__(self, engine, owner, **args)
    self.server = server
    self.updateInterval = self.engine.config.get("network", "updateinterval")
    self.updateCounter = 0
    self.changedControlData = {}

  def handleControlEvent(self, sender, flags):
    self.changedControlData[sender] = flags

  def handleControlData(self, sender, owner, flags):
    # TODO: player mapping
    for player in self.server.world.players:
      if player.owner == owner:
        player.controls.flags = flags
        break

  def handleCreateActor(self, sender, name):
    id = self.objects.generateId()
    self.server.broadcastMessage(ActorCreated(owner = sender, name = name, id = id))

  def handleSessionClosed(self, session):
    for actor in self.actors:
      if actor.owner == session.id:
        id = self.objects.id(actor)
        self.server.broadcastMessage(ActorDeleted(id = id))

  def handleSessionOpened(self, session):
    for actor in self.actors:
      id = self.objects.id(actor)
      session.sendMessage(ActorCreated(owner = actor.owner, name = actor.__name__, id = id))

  def broadcastState(self):
    for actor in self.actors:
      id = self.objects.id(actor)
      self.server.broadcastMessage(ActorData(id = id, data = actor.getState()), meToo = False)

    for sender, flags in self.changedControlData.items():
      self.server.broadcastMessage(ControlData(owner = sender, flags = flags))
    self.changedControlData = {}

  def run(self, ticks):
    self.runCommon(ticks, self.server.world)
    Scene.run(self, ticks)

    self.updateCounter += ticks
    if self.updateCounter > self.updateInterval:
      self.updateCounter %= self.updateInterval
      self.broadcastState()
