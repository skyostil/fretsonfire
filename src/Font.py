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
import numpy
from OpenGL.GL import *
import sys

from Texture import Texture, TextureAtlas, TextureAtlasFullException

class Font:
  """A texture-mapped font."""
  def __init__(self, fileName, size, bold = False, italic = False, underline = False, outline = True,
               scale = 1.0, reversed = False, systemFont = False):
    pygame.font.init()
    self.size             = size
    self.scale            = scale
    self.glyphCache       = {}
    self.glyphSizeCache   = {}
    self.outline          = outline
    self.glyphTextures    = []
    self.reversed         = reversed
    self.stringCache      = {}
    self.stringCacheLimit = 256
    # Try loading a system font first if one was requested
    self.font           = None
    if systemFont and sys.platform != "win32":
      try:
        self.font       = pygame.font.SysFont(None, size)
      except:
        pass
    if not self.font:
      self.font         = pygame.font.Font(fileName, size)
    self.font.set_bold(bold)
    self.font.set_italic(italic)
    self.font.set_underline(underline)

  def getStringSize(self, s, scale = 0.002):
    """
    Get the dimensions of a string when rendered with this font.

    @param s:       String
    @param scale:   Scale factor
    @return:        (width, height) tuple
    """
    w = 0
    h = 0
    scale *= self.scale
    for ch in s:
      try:
        s = self.glyphSizeCache[ch]
      except:
        s = self.glyphSizeCache[ch] = self.font.size(ch)
      w += s[0]
      h = max(s[1], h)
    return (w * scale, h * scale)

  def getHeight(self):
    """@return: The height of this font"""
    return self.font.get_height() * self.scale

  def getLineSpacing(self):
    """@return: The line spacing of this font"""
    return self.font.get_linesize() * self.scale
    
  def setCustomGlyph(self, character, texture):
    """
    Replace a character with a texture.

    @param character:   Character to replace
    @param texture:     L{Texture} instance
    """
    texture.setFilter(GL_LINEAR, GL_LINEAR)
    texture.setRepeat(GL_CLAMP, GL_CLAMP)
    self.glyphCache[character]     = (texture, (0.0, 0.0, texture.size[0], texture.size[1]))
    s = .75 * self.getHeight() / float(texture.pixelSize[0])
    self.glyphSizeCache[character] = (texture.pixelSize[0] * s, texture.pixelSize[1] * s)

  def _renderString(self, text, pos, direction, scale):
    if not text:
      return

    if not (text, scale) in self.stringCache:
      currentTexture = None
      #x, y           = pos[0], pos[1]
      x, y           = 0.0, 0.0
      vertices       = numpy.empty((4 * len(text), 2), numpy.float32)
      texCoords      = numpy.empty((4 * len(text), 2), numpy.float32)
      vertexCount    = 0
      cacheEntry     = []

      for i, ch in enumerate(text):
        g, coordinates     = self.getGlyph(ch)
        w, h               = self.getStringSize(ch, scale = scale)
        tx1, ty1, tx2, ty2 = coordinates

        # Set the initial texture
        if currentTexture is None:
          currentTexture = g

        # If the texture changed, flush the geometry
        if currentTexture != g:
          cacheEntry.append((currentTexture, vertexCount, numpy.array(vertices[:vertexCount]), numpy.array(texCoords[:vertexCount])))
          currentTexture = g
          vertexCount = 0

        vertices[vertexCount + 0]  = (x,     y)
        vertices[vertexCount + 1]  = (x + w, y)
        vertices[vertexCount + 2]  = (x + w, y + h)
        vertices[vertexCount + 3]  = (x,     y + h)
        texCoords[vertexCount + 0] = (tx1, ty2)
        texCoords[vertexCount + 1] = (tx2, ty2)
        texCoords[vertexCount + 2] = (tx2, ty1)
        texCoords[vertexCount + 3] = (tx1, ty1)
        vertexCount += 4

        x += w * direction[0]
        y += w * direction[1]
      cacheEntry.append((currentTexture, vertexCount, vertices[:vertexCount], texCoords[:vertexCount]))

      # Don't store very short strings
      if len(text) > 5:
        # Limit the cache size
        if len(self.stringCache) > self.stringCacheLimit:
          del self.stringCache[self.stringCache.keys()[0]]
        self.stringCache[(text, scale)] = cacheEntry
    else:
      cacheEntry = self.stringCache[(text, scale)]

    glPushMatrix()
    glTranslatef(pos[0], pos[1], 0)
    for texture, vertexCount, vertices, texCoords in cacheEntry:
      texture.bind()
      glVertexPointer(2, GL_FLOAT, 0, vertices)
      glTexCoordPointer(2, GL_FLOAT, 0, texCoords)
      glDrawArrays(GL_QUADS, 0, vertexCount)
    glPopMatrix()

  def render(self, text, pos = (0, 0), direction = (1, 0), scale = 0.002):
    """
    Draw some text.

    @param text:      Text to draw
    @param pos:       Text coordinate tuple (x, y)
    @param direction: Text direction vector (x, y, z)
    @param scale:     Scale factor
    """
    glEnable(GL_TEXTURE_2D)
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)

    scale *= self.scale

    if self.reversed:
      text = "".join(reversed(text))

    if self.outline:
      glPushAttrib(GL_CURRENT_BIT)
      glColor4f(0, 0, 0, glGetFloatv(GL_CURRENT_COLOR)[3])
      self._renderString(text, (pos[0] + 0.003, pos[1] + 0.003), direction, scale)
      glPopAttrib()

    self._renderString(text, pos, direction, scale)
    
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)
    glDisable(GL_TEXTURE_2D)

  def _allocateGlyphTexture(self):
    t = TextureAtlas(size = glGetInteger(GL_MAX_TEXTURE_SIZE))
    t.texture.setFilter(GL_LINEAR, GL_LINEAR)
    t.texture.setRepeat(GL_CLAMP, GL_CLAMP)
    self.glyphTextures.append(t)
    return t

  def getGlyph(self, ch):
    """
    Get a (L{Texture}, coordinate tuple) pair for a given character.

    @param ch:    Character
    @return:      (L{Texture} instance, coordinate tuple)
    """
    try:
      return self.glyphCache[ch]
    except KeyError:
      s = self.font.render(ch, True, (255, 255, 255))

      # Draw outlines
      """
      import Image, ImageFilter
      srcImg = Image.fromstring("RGBA", s.get_size(), pygame.image.tostring(s, "RGBA"))
      img    = Image.fromstring("RGBA", s.get_size(), pygame.image.tostring(s, "RGBA"))
      for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
          a = 0
          ns = 3
          n = 0
          for ny in range(max(0, y - ns), min(img.size[1], y + ns)):
            for nx in range(max(0, x - ns), min(img.size[0], x + ns)):
              a += srcImg.getpixel((nx, ny))[3]
              n += 1
          if a and srcImg.getpixel((x, y))[3] == 0:
            img.putpixel((x, y), (0, 0, 0, a / n))
      s = pygame.image.fromstring(img.tostring(), s.get_size(), "RGBA")
      """

      if not self.glyphTextures:
        texture = self._allocateGlyphTexture()
      else:
        texture = self.glyphTextures[-1]

      # Insert the texture into the glyph cache
      try:
        coordinates = texture.add(s)
      except TextureAtlasFullException:
        # Try again with a fresh atlas
        texture = self._allocateGlyphTexture()
        return self.getGlyph(ch)

      self.glyphCache[ch] = (texture, coordinates)
      return (texture, coordinates)
