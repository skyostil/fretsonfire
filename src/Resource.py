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

import os
from Queue import Queue, Empty
from threading import Thread, BoundedSemaphore
import time
import shutil
import stat

from Task import Task
import Log
import Version

class Loader(Thread):
  def __init__(self, target, name, function, resultQueue, loaderSemaphore, onLoad = None):
    Thread.__init__(self)
    self.semaphore   = loaderSemaphore
    self.target      = target
    self.name        = name
    self.function    = function
    self.resultQueue = resultQueue
    self.result      = None
    self.onLoad      = onLoad
    self.exception   = None
    self.time        = 0.0
    self.canceled    = False
    if target and name:
      setattr(target, name, None)

  def run(self):
    self.semaphore.acquire()
    # Reduce priority on posix
    if os.name == "posix":
      os.nice(5)
    self.load()
    self.semaphore.release()
    self.resultQueue.put(self)

  def __str__(self):
    return "%s(%s) %s" % (self.function.__name__, self.name, self.canceled and "(canceled)" or "")

  def cancel(self):
    self.canceled = True

  def load(self):
    try:
      start = time.time()
      self.result = self.function()
      self.time = time.time() - start
    except:
      import sys
      self.exception = sys.exc_info()

  def finish(self):
    if self.canceled:
      return
    
    Log.notice("Loaded %s.%s in %.3f seconds" % (self.target.__class__.__name__, self.name, self.time))
    
    if self.exception:
      raise self.exception[0], self.exception[1], self.exception[2]
    if self.target and self.name:
      setattr(self.target, self.name, self.result)
    if self.onLoad:
      self.onLoad(self.result)
    return self.result

  def __call__(self):
    self.join()
    return self.result

class Resource(Task):
  def __init__(self, dataPath = os.path.join("..", "data")):
    self.resultQueue = Queue()
    self.dataPaths = [dataPath]
    self.loaderSemaphore = BoundedSemaphore(value = 1)
    self.loaders = []

  def addDataPath(self, path):
    if not path in self.dataPaths:
      self.dataPaths = [path] + self.dataPaths

  def removeDataPath(self, path):
    if path in self.dataPaths:
      self.dataPaths.remove(path)

  def fileName(self, *name, **args):
    if not args.get("writable", False):
      for dataPath in self.dataPaths:
        readOnlyPath = os.path.join(dataPath, *name)
        # If the requested file is in the read-write path and not in the
        # read-only path, use the existing read-write one.
        if os.path.isfile(readOnlyPath):
          return readOnlyPath
        readWritePath = os.path.join(getWritableResourcePath(), *name)
        if os.path.isfile(readWritePath):
          return readWritePath
      return readOnlyPath
    else:
      readOnlyPath = os.path.join(self.dataPaths[-1], *name)
      try:
        # First see if we can write to the original file
        if os.access(readOnlyPath, os.W_OK):
          return readOnlyPath
        # If the original file does not exist, see if we can write to its directory
        if not os.path.isfile(readOnlyPath) and os.access(os.path.dirname(readOnlyPath), os.W_OK):
          return readOnlyPath
      except:
        raise
      
      # If the resource exists in the read-only path, make a copy to the
      # read-write path.
      readWritePath = os.path.join(getWritableResourcePath(), *name)
      if not os.path.isfile(readWritePath) and os.path.isfile(readOnlyPath):
        Log.notice("Copying '%s' to writable data directory." % "/".join(name))
        try:
          os.makedirs(os.path.dirname(readWritePath))
        except:
          pass
        shutil.copy(readOnlyPath, readWritePath)
        self.makeWritable(readWritePath)
      # Create directories if needed
      if not os.path.isdir(readWritePath) and os.path.isdir(readOnlyPath):
        Log.notice("Creating writable directory '%s'." % "/".join(name))
        os.makedirs(readWritePath)
        self.makeWritable(readWritePath)
      return readWritePath

  def makeWritable(self, path):
    os.chmod(path, stat.S_IWRITE | stat.S_IREAD | stat.S_IEXEC)
  
  def load(self, target = None, name = None, function = lambda: None, synch = False, onLoad = None):
    Log.notice("Loading %s.%s %s" % (target.__class__.__name__, name, synch and "synchronously" or "asynchronously"))
    l = Loader(target, name, function, self.resultQueue, self.loaderSemaphore, onLoad = onLoad)
    if synch:
      l.load()
      return l.finish()
    else:
      self.loaders.append(l)
      l.start()
      return l

  def run(self, ticks):
    try:
      loader = self.resultQueue.get_nowait()
      loader.finish()
      self.loaders.remove(loader)
    except Empty:
      pass

def getWritableResourcePath():
  """
  Returns a path that holds the configuration for the application.
  """
  path = "."
  appname = Version.appName()
  if os.name == "posix":
    path = os.path.expanduser("~/." + appname)
  elif os.name == "nt":
    try:
      path = os.path.join(os.environ["APPDATA"], appname)
    except:
      pass
  try:
    os.mkdir(path)
  except:
    pass
  return path
