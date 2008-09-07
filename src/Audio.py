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
import time
import sys
from Task import Task

# Yeah, py2exe is weird...
if hasattr(sys, "frozen"):
  import pygame.mixer_music
  pygame.mixer.music = sys.modules["pygame.mixer_music"]

# Pyglet-based audio is still experimental at the moment
#import pyglet

# OGG support disabled due to incompatibility with Python 2.5
#try:
#  import ogg.vorbis
#except ImportError:
#  Log.warn("PyOGG not found. OGG files will be fully decoded prior to playing; expect absurd memory usage.")

if "pyglet" in sys.modules:
  class AudioPyglet(Task):
    def __init__(self, channels = 8):
      Task.__init__(self)
      self.eventLoop = pyglet.app.EventLoop()
      self.channels = [Channel(i) for i in range(channels)]

    def pre_open(self, frequency = 22050, bits = 16, stereo = True, bufferSize = 1024):
      return True

    def open(self, frequency = 22050, bits = 16, stereo = True, bufferSize = 1024):
      return True

    def getChannelCount(self):
      return len(self.channels)

    def getChannel(self, n):
      return self.channels[n]

    def close(self):
      if self.eventLoop:
        self.eventLoop.exit()
        self.eventLoop = None

    def run(self, ticks):
      self.eventLoop.idle()

    def pause(self):
      for ch in self.channels:
        ch.pause()

    def unpause(self):
      for ch in self.channels():
        ch.play()

  class Music(object):
    def __init__(self, fileName):
      self.source = pyglet.media.load(fileName, streaming = True)
      self.player = pyglet.media.Player()

    @staticmethod
    def setEndEvent(event):
      # TODO
      pass

    def play(self, loops = -1, pos = 0.0):
      self.player.queue(self.source)
      self.player.seek(pos)
      if loops > 0:
        self.player.eos_action = pyglet.media.Player.EOS_LOOP
      else:
        self.player.eos_action = pyglet.media.Player.EOS_PAUSE
      self.player.play()

    def stop(self):
      self.player.pause()
      self.rewind()

    def rewind(self):
      self.player.seek(0.0)

    def pause(self):
      self.player.pause()

    def unpause(self):
      self.player.play()

    def setVolume(self, volume):
      self.player.volume = volume

    def fadeout(self, time):
      # TODO
      self.stop()

    def isPlaying(self):
      return self.player.playing

    def getPosition(self):
      # TODO: figure out a way to increase precision here
      #self.player._audio.pump()
      return self.player.time * 1000.0

  class Channel(object):
    def __init__(self, id):
      self.source = None

    def play(self, sound):
      self.source = sound.source
      self.source.play()

    def stop(self):
      if self.source:
        self.source.stop()

    def pause(self):
      if self.source:
        self.source.pause()

    def setVolume(self, volume):
      if self.source:
        self.source.value = volume

    def fadeout(self, time):
      # TODO
      self.stop()

  class Sound(object):
    def __init__(self, fileName, streaming = False):
      self.source = pyglet.media.load(fileName, streaming = streaming)
      self.player = pyglet.media.Player()

    def play(self, loops = 0):
      self.player.queue(self.source)
      if loops > 0:
        self.player.eos_action = pyglet.media.Player.EOS_LOOP
      else:
        self.player.eos_action = pyglet.media.Player.EOS_PAUSE
      self.player.play()

    def stop(self):
      self.player.pause()
      self.player.seek(0.0)

    def setVolume(self, volume):
      self.player.volume = volume

    def fadeout(self, time):
      # TODO
      self.stop()

else: # pygame
  class Audio(Task):
    def __init__(self):
      Task.__init__(self)

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

if "ogg.vorbis" in sys.modules:
  import struct
  import numpy

  class OggStream(object):
    def __init__(self, inputFileName):
      self.file = ogg.vorbis.VorbisFile(inputFileName)

    def read(self, bytes = 4096):
      (data, bytes, bit) = self.file.read(bytes)
      return data[:bytes]

  class StreamingOggSound(Sound, Task):
    def __init__(self, engine, channel, fileName):
      Task.__init__(self)
      self.engine       = engine
      self.fileName     = fileName
      self.channel      = channel.channel
      self.playing      = False
      self.bufferSize   = 1024 * 64
      self.bufferCount  = 8
      self.volume       = 1.0
      self.buffer       = numpy.zeros((2 * self.bufferSize, 2), dtype = numpy.int16)
      self.decodingRate = 4
      self._reset()

    def _reset(self):
      self.stream        = OggStream(self.fileName)
      self.buffersIn     = [pygame.sndarray.make_sound(numpy.zeros((self.bufferSize, 2), dtype = numpy.int16)) for i in range(self.bufferCount + 1)]
      self.buffersOut    = []
      self.buffersBusy   = []
      self.bufferPos     = 0
      self.done          = False
      self.lastQueueTime = time.time()

      while len(self.buffersOut) < self.bufferCount and not self.done:
        self._produceSoundBuffers()

    def __del__(self):
      self.engine.removeTask(self)

    def play(self):
      if self.playing:
        return

      self.engine.addTask(self, synchronized = False)
      self.playing = True

      while len(self.buffersOut) < self.bufferCount and not self.done:
        self._produceSoundBuffers()

      self.channel.play(self.buffersOut.pop())

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
      # No available buffers to fill?
      if not self.buffersIn or self.done:
        return

      data = self.stream.read()

      if not data:
        self.done = True
      else:
        data = struct.unpack("%dh" % (len(data) / 2), data)
        samples = len(data) / 2
        self.buffer[self.bufferPos:self.bufferPos + samples, 0] = data[0::2]
        self.buffer[self.bufferPos:self.bufferPos + samples, 1] = data[1::2]
        self.bufferPos += samples

      # If we have at least one full buffer decode, claim a buffer and copy the
      # data over to it.
      if self.bufferPos >= self.bufferSize or (self.done and self.bufferPos):
        # Claim the sound buffer and copy the data
        if self.bufferPos < self.bufferSize:
          self.buffer[self.bufferPos:]  = 0
        soundBuffer = self.buffersIn.pop()
        pygame.sndarray.samples(soundBuffer)[:] = self.buffer[0:self.bufferSize]

        # Discard the copied sound data
        n = max(0, self.bufferPos - self.bufferSize)
        self.buffer[0:n] = self.buffer[self.bufferSize:self.bufferSize+n]
        self.bufferPos   = n

        return soundBuffer

    def _produceSoundBuffers(self):
      # Decode enough that we have at least one full sound buffer
      # ready in the queue if possible
      while not self.done:
        for i in xrange(self.decodingRate):
          soundBuffer = self._decodeStream()
          if soundBuffer:
            self.buffersOut.insert(0, soundBuffer)
        if self.buffersOut:
          break

    def run(self, ticks):
      if not self.playing:
        return

      self.channel.set_volume(self.volume)

      if len(self.buffersOut) < self.bufferCount:
        self._produceSoundBuffers()

      if not self.channel.get_queue() and self.buffersOut:
        # Queue one decoded sound buffer and mark the previously played buffer as free
        soundBuffer = self.buffersOut.pop()
        self.buffersBusy.insert(0, soundBuffer)
        self.lastQueueTime = time.time()
        self.channel.queue(soundBuffer)
        if len(self.buffersBusy) > 2:
          self.buffersIn.insert(0, self.buffersBusy.pop())

      if not self.buffersOut and self.done and time.time() - self.lastQueueTime > 4:
        self.stop()

  class StreamingSound(Sound, Task):
    def __init__(self, engine, channel, fileName):
      Task.__init__(self)
      Sound.__init__(self, fileName)
      self.channel = channel

    def __new__(cls, engine, channel, fileName):
      frequency, format, stereo = pygame.mixer.get_init()
      if fileName.lower().endswith(".ogg"):
        if frequency == 44100 and format == -16 and stereo:
          return StreamingOggSound(engine, channel, fileName)
        else:
          Log.warn("Audio settings must match stereo 16 bits at 44100 Hz in order to stream OGG files.")
      return super(StreamingSound, cls).__new__(cls, engine, channel, fileName)

    def play(self):
      self.channel.play(self)

    def stop(self):
      Sound.stop(self)
      self.channel.stop()

    def setVolume(self, volume):
      Sound.setVolume(self, volume)
      self.channel.setVolume(volume)

    def fadeout(self, time):
      Sound.fadeout(self, time)
      self.channel.fadeout(time)

else: # pyglet & pygame
  class StreamingSound(Sound, Task):
    def __init__(self, engine, channel, fileName):
      Sound.__init__(self, fileName)

