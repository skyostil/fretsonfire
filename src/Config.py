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
import Log
import Resource
import os

encoding  = "iso-8859-1"
config    = None
prototype = {}

class Option:
  """A prototype configuration key."""
  def __init__(self, **args):
    for key, value in args.items():
      setattr(self, key, value)
      
def define(section, option, type, default = None, text = None, options = None, prototype = prototype):
  """
  Define a configuration key.
  
  @param section:    Section name
  @param option:     Option name
  @param type:       Key type (e.g. str, int, ...)
  @param default:    Default value for the key
  @param text:       Text description for the key
  @param options:    Either a mapping of values to text descriptions
                    (e.g. {True: 'Yes', False: 'No'}) or a list of possible values
  @param prototype:  Configuration prototype mapping
  """
  if not section in prototype:
    prototype[section] = {}
    
  if type == bool and not options:
    options = [True, False]
    
  prototype[section][option] = Option(type = type, default = default, text = text, options = options)

def load(fileName = None, setAsDefault = False):
  """Load a configuration with the default prototype"""
  global config
  c = Config(prototype, fileName)
  if setAsDefault and not config:
    config = c
  return c

class Config:
  """A configuration registry."""
  def __init__(self, prototype, fileName = None):
    """
    @param prototype:  The configuration protype mapping
    @param fileName:   The file that holds this configuration registry
    """
    self.prototype = prototype

    # read configuration
    self.config = ConfigParser()

    if fileName:
      if not os.path.isfile(fileName):
        path = Resource.getWritableResourcePath()
        fileName = os.path.join(path, fileName)
      self.config.read(fileName)
  
    self.fileName  = fileName
  
    # fix the defaults and non-existing keys
    for section, options in prototype.items():
      if not self.config.has_section(section):
        self.config.add_section(section)
      for option in options.keys():
        type    = options[option].type
        default = options[option].default
        if not self.config.has_option(section, option):
          self.config.set(section, option, str(default))
    
  def get(self, section, option):
    """
    Read a configuration key.
    
    @param section:   Section name
    @param option:    Option name
    @return:          Key value
    """
    try:
      type    = self.prototype[section][option].type
      default = self.prototype[section][option].default
    except KeyError:
      Log.warn("Config key %s.%s not defined while reading." % (section, option))
      type, default = str, None
  
    value = self.config.has_option(section, option) and self.config.get(section, option) or default
    if type == bool:
      value = str(value).lower()
      if value in ("1", "true", "yes", "on"):
        value = True
      else:
        value = False
    else:
      value = type(value)
      
    #Log.debug("%s.%s = %s" % (section, option, value))
    return value

  def set(self, section, option, value):
    """
    Set the value of a configuration key.
    
    @param section:   Section name
    @param option:    Option name
    @param value:     Value name
    """
    try:
      prototype[section][option]
    except KeyError:
      Log.warn("Config key %s.%s not defined while writing." % (section, option))
    
    if not self.config.has_section(section):
      self.config.add_section(section)

    if type(value) == unicode:
      value = value.encode(encoding)
    else:
      value = str(value)

    self.config.set(section, option, value)
    
    f = open(self.fileName, "w")
    self.config.write(f)
    f.close()

def get(section, option):
  """
  Read the value of a global configuration key.
  
  @param section:   Section name
  @param option:    Option name
  @return:          Key value
  """
  global config
  return config.get(section, option)
  
def set(section, option, value):
  """
  Write the value of a global configuration key.
  
  @param section:   Section name
  @param option:    Option name
  @param value:     New key value
  """
  global config
  return config.set(section, option, value)
