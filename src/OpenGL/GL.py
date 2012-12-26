# Fake GL for Raspberry Pi
from pogles.gles2 import *
from array import array
import pogles
import pygame
import numpy
import transformations

GL_CLAMP = GL_CLAMP_TO_EDGE
GL_MODULATE = 0
GL_COLOR_MATERIAL = 0

def todo(what):
  print "TODO:", what

def glGetIntegerv(param):
  # Why does querying the viewport crash?
  if param == GL_VIEWPORT:
    return [0, 0, pygame.display.width, pygame.display.height]
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

_colorEnabled = False
_textureEnabled = False

def glEnable(param):
  global _colorEnabled
  global _textureEnabled
  if param == GL_TEXTURE_2D:
    _textureEnabled = True
  elif param == GL_COLOR_MATERIAL:
    _colorEnabled = True
  else:
    pogles.gles2.glEnable(param)

def glDisable(param):
  global _colorEnabled
  global _textureEnabled
  if param == GL_TEXTURE_2D:
    _textureEnabled = False
  elif param == GL_COLOR_MATERIAL:
    _colorEnabled = False
  else:
    pogles.gles2.glDisable(param)

GL_PERSPECTIVE_CORRECTION_HINT = 0
GL_NICEST = 0

def glHint(hint, value):
  pass

GL_MODELVIEW = 0x1700
GL_PROJECTION = 0x1701

_modelviewStack = [transformations.identity_matrix()]
_projectionStack = [transformations.identity_matrix()]
_textureStack = [transformations.identity_matrix()]
_activeStack = _modelviewStack

def glMatrixMode(mode):
  global _activeStack
  if mode == GL_MODELVIEW:
    _activeStack = _modelviewStack
  elif mode == GL_TEXTURE:
    _activeStack = _textureStack
  else:
    assert mode == GL_PROJECTION
    _activeStack = _projectionStack

def glLoadIdentity():
  _activeStack[0] = transformations.identity_matrix()

def glOrtho(left, right, bottom, top, zNear, zFar):
  m = transformations.identity_matrix()
  m[0, 0] = 2.0 / (right - left)
  m[1, 1] = 2.0 / (top - bottom)
  m[2, 2] = -2.0 / (zFar - zNear)
  m[3, 0] = -(right + left) / float(right - left)
  m[3, 1] = -(top + bottom) / float(top - bottom)
  m[3, 2] = -(zFar + zNear) / float(zFar - zNear)
  m = numpy.transpose(m)
  _activeStack[0] = _activeStack[0].dot(m)

def glPushMatrix():
  _activeStack.insert(0, _activeStack[0])

def glPopMatrix():
  _activeStack.pop(0)

def glMultMatrixf(matrix):
  m = numpy.transpose(numpy.reshape(matrix, (4, 4)))
  _activeStack[0] = _activeStack[0].dot(m)

def glScalef(x, y, z):
  m = numpy.array([
      [x, 0, 0, 0],
      [0, y, 0, 0],
      [0, 0, z, 0],
      [0, 0, 0, 1]])
  _activeStack[0] = _activeStack[0].dot(m)

def glTranslatef(x, y, z):
  m = transformations.translation_matrix((x, y, z))
  _activeStack[0] = _activeStack[0].dot(m)

def glRotate(angle, x, y, z):
  m = transformations.rotation_matrix(numpy.radians(angle), (x, y, z))
  _activeStack[0] = _activeStack[0].dot(m)

_maxVertices = 16
_vertexIndex = 0
_primitive = None
_color = array('f', [1, 1, 1, 1] * _maxVertices)
_texCoord = array('f', [0, 0] * _maxVertices)
_position = array('f', [0, 0, 0, 1] * _maxVertices)

_vertSource = """
attribute vec4 a_position;
attribute vec4 a_color;

uniform mat4 u_modelviewProjectionMatrix;

varying vec4 v_color;

void main()
{
    gl_Position = u_modelviewProjectionMatrix * a_position;
    v_color = a_color;
}
"""

_fragSource = """
varying vec4 v_color;

void main()
{
    gl_FragColor = v_color;
}
"""

def _createShader(type, source):
  shader = glCreateShader(type)
  glShaderSource(shader, source)
  glCompileShader(shader)
  compiled = glGetShaderiv(shader, GL_COMPILE_STATUS)
  if not compiled:
    glDeleteShader(shader)
    raise Exception("Error compiling shader:\n%s" % glGetShaderInfoLog(shader))
  return shader

def _createProgram(vertSource, fragSource):
  vertShader = _createShader(GL_VERTEX_SHADER, vertSource)
  fragShader = _createShader(GL_FRAGMENT_SHADER, fragSource)
  program = glCreateProgram()

  glAttachShader(program, vertShader)
  glAttachShader(program, fragShader)

  glBindAttribLocation(program, 0, 'a_position')
  glBindAttribLocation(program, 1, 'a_color')
  glLinkProgram(program)
  glDeleteShader(vertShader)
  glDeleteShader(fragShader)

  linked = glGetProgramiv(program, GL_LINK_STATUS)
  if not linked:
    glDeleteProgram(program)
    raise Exception("Error linking program:\n%s" % glGetProgramInfoLog(program))
  return program

def glColor4f(r, g, b, a):
  i = _vertexIndex * 4
  _color[i] = r
  _color[i + 1] = g
  _color[i + 2] = b
  _color[i + 3] = a

def glBegin(primitive):
  global _vertexIndex
  global _primitive
  _vertexIndex = 0
  _primitive = primitive

_program = None
_u_modelviewProjectionMatrix = None

def glEnd():
  global _program
  global _u_modelviewProjectionMatrix
  print "Drawing", _vertexIndex, "vertices"
  if not _program:
    _program = _createProgram(_vertSource, _fragSource)
    _u_modelviewProjectionMatrix = glGetUniformLocation(_program, "u_modelviewProjectionMatrix")
  glUseProgram(_program)

  mvpMatrix = numpy.transpose(_modelviewStack[0].dot(_projectionStack[0]))
  #print "modelview:"
  #print _modelviewStack[0]
  #print "projection:"
  #print _projectionStack[0]
  glUniformMatrix4fv(_u_modelviewProjectionMatrix, False, mvpMatrix.reshape([16]).tolist())

  #import random
  #for i in range(_vertexIndex):
  #  _position[i * 4] = random.random()
  #  _position[i * 4 + 1] = random.random()

  #print mvpMatrix
  #print _primitive
  #print _position[0:_vertexIndex * 4]
  glVertexAttribPointer(0, 4, GL_FLOAT, False, 0, _position.buffer_info()[0])
  glEnableVertexAttribArray(0)
  if _colorEnabled:
    glVertexAttribPointer(1, 4, GL_FLOAT, False, 0, _color.buffer_info()[0])
    glEnableVertexAttribArray(1)

  pogles.gles2.glDrawArrays(_primitive, 0, _vertexIndex)
  glDisableVertexAttribArray(0)
  glDisableVertexAttribArray(1)

def glTexCoord2f(x, y):
  i = _vertexIndex * 2
  _texCoord[i] = x
  _texCoord[i + 1] = y

def glVertex2f(x, y):
  global _vertexIndex
  i = _vertexIndex * 4
  _position[i] = x
  _position[i + 1] = y
  _position[i + 2] = 0
  _position[i + 3] = 1
  _vertexIndex += 1
  i = (_vertexIndex - 1) * 2
  glTexCoord2f(_texCoord[i], _texCoord[i + 1])
  i = (_vertexIndex - 1) * 4
  glColor4f(_color[i], _color[i + 1], _color[i + 2], _color[i + 3])

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
