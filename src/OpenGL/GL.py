# Fake GL for Raspberry Pi
from pogles.gles2 import *
from array import array
import pogles
import pygame

GL_CLAMP = GL_CLAMP_TO_EDGE
GL_MODULATE = 0
GL_COLOR_MATERIAL = 0

def todo(what):
  print "TODO:", what

def glGetIntegerv(param):
  # Why does querying the viewport crash?
  if param == GL_VIEWPORT:
    return [0, 0, pygame.display.width, pygame.display.height]
  elif param == GL_MAX_TEXTURE_SIZE:
    return 1024
  return pogles.gles2.glGetIntegerv(param)

glGetInteger = glGetIntegerv

GL_CURRENT_COLOR = 1

def glGetFloatv(param):
  if param == GL_CURRENT_COLOR:
    return [0, 0, 0, 0]
  return pogles.gles2.glGetFloatv(param)

def glGenTextures(count):
  result = pogles.gles2.glGenTextures(count)
  return result[0] if count == 1 else result

def glEnable(param):
  if param == GL_TEXTURE_2D or param == GL_COLOR_MATERIAL:
    return
  pogles.gles2.glEnable(param)

def glDisable(param):
  if param == GL_TEXTURE_2D or param == GL_COLOR_MATERIAL:
    return
  pogles.gles2.glDisable(param)

GL_PERSPECTIVE_CORRECTION_HINT = 0
GL_NICEST = 0

def glHint(hint, value):
  pass

GL_MODELVIEW = 0x1700
GL_PROJECTION = 0x1701

def glMatrixMode(mode):
  pass

def glLoadIdentity():
  pass

def glOrtho(left, right, bottom, top, near, far):
  pass

def glPushMatrix():
  pass

def glPopMatrix():
  pass

def glMultMatrixf(matrix):
  pass

def glScalef(x, y, z):
  pass

def glTranslatef(x, y, z):
  pass

def glRotate(angle, x, y, z):
  pass

def glColor4f(r, g, b, a):
  pass

def glBegin(primitive):
  pass

def glEnd():
  pass

def glTexCoord2f(x, y):
  pass

def glVertex2f(x, y):
  pass

GL_VERTEX_ARRAY = 1 << 0
GL_TEXTURE_COORD_ARRAY = 1 << 1

def glEnableClientState(state):
  pass

def glDisableClientState(state):
  pass

GL_CURRENT_BIT = 1 << 0

def glPushAttrib(attrib):
  pass

def glPopAttrib():
  pass

def glTexImage2D(target, level, internalFormat, width, height, border, format, type, data):
  pixels = array("c", data)
  pogles.gles2.glTexImage2D(target, level, format, width, height, border, format, type, pixels.buffer_info()[0])

def glTexSubImage2D(target, level, xOffset, yOffset, width, height, format, type, data):
  pixels = array("c", data)
  pogles.gles2.glTexSubImage2D(target, level, xOffset, yOffset, width, height, format, type, pixels.buffer_info()[0])

GL_QUADS = 0

def glVertexPointer(size, type, offset, data):
  pass

def glTexCoordPointer(size, type, offset, data):
  pass

def glDrawArrays(mode, offset, count):
  pass
