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
import Log
from Task import Task

try:
  import ogg.vorbis
except ImportError:
  Log.warn("PyOGG not found. OGG files will be fully decoded prior to playing; expect absurd memory usage.")
  ogg = None

class Audio:
  def pre_open(self, frequency = 22050, bits = 16, stereo = True, bufferSize = 1024):
    pygame.mixer.pre_init(frequency, -bits, stereo and 2 or 1, bufferSize)
    return True
    
  def open(self, frequency = 22050, bits = 16, stereo = True, bufferSize = 1024):
    try:
      pygame.mixer.quit()
    except:
      pass

    try:
      pygame.mixer.init(frequency, -bits, stereo and 2 or 1, bufferSize)
    except:
      Log.warn("Audio setup failed. Trying with default configuration.")
      pygame.mixer.init()

    Log.debug("Audio configuration: %s" % str(pygame.mixer.get_init()))

    return True

  def getChannelCount(self):
    return pygame.mixer.get_num_channels()

  def getChannel(self, n):
    return Channel(n)

  def close(self):
    pygame.mixer.quit()

  def pause(self):
    pygame.mixer.pause()

  def unpause(self):
    pygame.mixer.unpause()

class Music(object):
  def __init__(self, fileName):
    pygame.mixer.music.load(fileName)

  @staticmethod
  def setEndEvent(event):
    pygame.mixer.music.set_endevent(event)

  def play(self, loops = -1, pos = 0.0):
    pygame.mixer.music.play(loops, pos)

  def stop(self):
    pygame.mixer.music.stop()

  def rewind(self):
    pygame.mixer.music.rewind()

  def pause(self):
    pygame.mixer.music.pause()

  def unpause(self):
    pygame.mixer.music.unpause()

  def setVolume(self, volume):
    pygame.mixer.music.set_volume(volume)

  def fadeout(self, time):
    pygame.mixer.music.fadeout(time)

  def isPlaying(self):
    return pygame.mixer.music.get_busy()

  def getPosition(self):
    return pygame.mixer.music.get_pos()

class Channel(object):
  def __init__(self, id):
    self.channel = pygame.mixer.Channel(id)

  def play(self, sound):
    self.channel.play(sound.sound)

  def stop(self):
    self.channel.stop()

  def setVolume(self, volume):
    self.channel.set_volume(volume)

  def fadeout(self, time):
    self.channel.fadeout(time)

class Sound(object):
  def __init__(self, fileName):
    self.sound   = pygame.mixer.Sound(fileName)

  def play(self, loops = 0):
    self.sound.play(loops)

  def stop(self):
    self.sound.stop()

  def setVolume(self, volume):
    self.sound.set_volume(volume)

  def fadeout(self, time):
    self.sound.fadeout(time)

class StreamingSound(Sound, Task):
  def __init__(self, engine, channel, fileName):
    Task.__init__(self)
    Sound.__init__(self, fileName)
    self.channel = channel

  def play(self):
    self.channel.play(self.sound)

  def stop(self):
    Sound.stop(self)
    self.channel.stop()

  def setVolume(self, volume):
    Sound.setVolume(self, volume)
    self.channel.setVolume(volume)

  def fadeout(self, time):
    Sound.fadeout(self, time)
    self.channel.fadeout(time)

if ogg:
  import struct
  from Numeric import reshape, array, zeros

  class OggStream(object):
    def __init__(self, inputFileName):
      self.file = ogg.vorbis.VorbisFile(inputFileName)

    def read(self, bytes = 4096):
      (data, bytes, bit) = self.file.read(bytes)
      return data[:bytes]

  class StreamingSound(Sound, Task):
    def __init__(self, engine, channel, fileName):
      Task.__init__(self)
      self.engine       = engine
      self.fileName     = fileName
      self.channel      = channel.channel
      self.playing      = False
      self.bufferSize   = 1024 * 64
      self.bufferCount  = 4
      self.volume       = 1.0
      self.buffer       = zeros((2 * self.bufferSize, 2))
      self.decodingRate = 4
      self._reset()

    def _reset(self):
      self.stream       = OggStream(self.fileName)
      self.soundBuffers = []
      self.bufferPos    = 0
      self.done         = False

      while len(self.soundBuffers) < self.bufferCount and not self.done:
        self._produceSoundBuffers()

    def __del__(self):
      self.engine.removeTask(self)

    def play(self):
      if self.playing:
        return

      self.engine.addTask(self, synchronized = False)
      self.playing = True

      while len(self.soundBuffers) < self.bufferCount and not self.done:
        self._produceSoundBuffers()
        
      self.channel.play(self.soundBuffers.pop())

    def stop(self):
      self.playing = False
      self.channel.stop()
      self.engine.removeTask(self)
      self._reset()

    def setVolume(self, volume):
      self.volume = volume

    def fadeout(self, time):
      self.stop()

    def _decodeStream(self):
      decodedBytes = 0
      data = self.stream.read()

      if not data:
        self.done = True
      else:
        data = struct.unpack("%dh" % (len(data) / 2), data)
        samples = len(data) / 2
        self.buffer[self.bufferPos:self.bufferPos + samples, 0] = data[0::2]
        self.buffer[self.bufferPos:self.bufferPos + samples, 1] = data[1::2]
        self.bufferPos += samples

      if self.bufferPos >= self.bufferSize or (self.done and self.bufferPos):
        soundBuffer = pygame.sndarray.make_sound(self.buffer[0:self.bufferPos])
        self.bufferPos = 0
        return soundBuffer

    def _produceSoundBuffers(self):
      # Decode enough that we have at least one full sound buffer
      # ready in the queue if possible
      while 1:
        for i in range(self.decodingRate):
          soundBuffer = self._decodeStream()
          if soundBuffer:
            self.soundBuffers.insert(0, soundBuffer)
        if self.soundBuffers or self.done:
          break

    def run(self, ticks):
      if not self.playing:
        return

      self.channel.set_volume(self.volume)
      
      if len(self.soundBuffers) < self.bufferCount:
        self._produceSoundBuffers()

      if not self.soundBuffers and self.done:
        self.stop()

      if not self.channel.get_queue() and self.soundBuffers:
        soundBuffer = self.soundBuffers.pop()
        try:
          self.channel.queue(soundBuffer)
        except TypeError:
          pass
