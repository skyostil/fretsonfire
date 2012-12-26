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
    i = _vertexIndex * 4
    return [_color[i], _color[i + 1], _color[i + 2], _color[i + 3]]
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
attribute vec2 a_texCoord;

uniform mat4 u_modelviewProjectionMatrix;

varying vec4 v_color;
varying vec2 v_texCoord;

void main()
{
    gl_Position = u_modelviewProjectionMatrix * a_position;
    v_color = a_color;
    v_texCoord = a_texCoord;
}
"""

_fragSource = """
varying vec4 v_color;
varying vec2 v_texCoord;

uniform sampler2D u_texture;
uniform bool u_textureEnabled;

void main()
{
    vec4 color = v_color;
    if (u_textureEnabled)
        color = texture2D(u_texture, v_texCoord) * color;
    /*gl_FragColor += vec4(v_texCoord.x, v_texCoord.y, 0.2, 1.0);*/
    /*color.a = 0.5;*/
    gl_FragColor = color;
}
"""

def _createShader(type, source):
  shader = glCreateShader(type)
  glShaderSource(shader, source)
  glCompileShader(shader)
  compiled = glGetShaderiv(shader, GL_COMPILE_STATUS)
  if not compiled:
    raise Exception("Error compiling shader:\n%s" % glGetShaderInfoLog(shader))
  return shader

def _createProgram(vertSource, fragSource):
  vertShader = _createShader(GL_VERTEX_SHADER, vertSource)
  fragShader = _createShader(GL_FRAGMENT_SHADER, fragSource)
  program = glCreateProgram()

  glAttachShader(program, vertShader)
  glAttachShader(program, fragShader)

  glBindAttribLocation(program, 0, "a_position")
  glBindAttribLocation(program, 1, "a_color")
  glBindAttribLocation(program, 2, "a_texCoord")
  glLinkProgram(program)
  glDeleteShader(vertShader)
  glDeleteShader(fragShader)

  linked = glGetProgramiv(program, GL_LINK_STATUS)
  if not linked:
    raise Exception("Error linking program:\n%s" % glGetProgramInfoLog(program))
  return program

def glColor4f(r, g, b, a):
  i = _vertexIndex * 4
  _color[i] = r
  _color[i + 1] = g
  _color[i + 2] = b
  _color[i + 3] = a
  glVertexAttrib4f(1, r, g, b, a)

def glBegin(primitive):
  global _vertexIndex
  global _primitive
  _vertexIndex = 0
  _primitive = primitive

_program = None
_u_modelviewProjectionMatrix = None
_u_textureEnabled = False

def _useDefaultProgram():
  global _program
  global _u_modelviewProjectionMatrix
  global _u_textureEnabled
  if not _program:
    _program = _createProgram(_vertSource, _fragSource)
    _u_modelviewProjectionMatrix = glGetUniformLocation(_program, "u_modelviewProjectionMatrix")
    _u_textureEnabled = glGetUniformLocation(_program, "u_textureEnabled")
  glUseProgram(_program)

def _applyUniforms():
  #mvpMatrix = numpy.transpose(_modelviewStack[0].dot(_projectionStack[0]))
  mvpMatrix = numpy.transpose(_projectionStack[0].dot(_modelviewStack[0]))
  #print "modelview:"
  #print _modelviewStack[0]
  #print "projection:"
  #print _projectionStack[0]
  #print "mvp:"
  #print mvpMatrix
  #mvpMatrix = transformations.identity_matrix()
  #print "modelview:"
  glUniformMatrix4fv(_u_modelviewProjectionMatrix, False, mvpMatrix.reshape([16]).tolist())
  glUniform1i(_u_textureEnabled, 1 if _textureEnabled else 0)

def glEnd():
  _useDefaultProgram()
  _applyUniforms()

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
  else:
    glVertexAttrib4f(1, 1, 1, 1, 1)
  if _textureEnabled:
    glVertexAttribPointer(2, 2, GL_FLOAT, False, 0, _texCoord.buffer_info()[0])
    glEnableVertexAttribArray(2)

  pogles.gles2.glDrawArrays(_primitive, 0, _vertexIndex)
  glDisableVertexAttribArray(0)
  glDisableVertexAttribArray(1)
  glDisableVertexAttribArray(2)

def glTexCoord2f(x, y):
  i = _vertexIndex * 2
  _texCoord[i] = x
  _texCoord[i + 1] = y
  glVertexAttrib2f(2, x, y)

def glVertex2f(x, y):
  global _vertexIndex
  i = _vertexIndex * 4
  _position[i] = x
  _position[i + 1] = y
  _position[i + 2] = 0
  _position[i + 3] = 1
  _vertexIndex += 1
  i = _vertexIndex * 2
  j = (_vertexIndex - 1) * 2
  _texCoord[i] = _texCoord[j]
  _texCoord[i + 1] = _texCoord[j + 1]
  i = _vertexIndex * 4
  j = (_vertexIndex - 1) * 4
  _color[i] = _color[j]
  _color[i + 1] = _color[j + 1]
  _color[i + 2] = _color[j + 2]
  _color[i + 3] = _color[j + 3]

GL_VERTEX_ARRAY = 1 << 0
GL_TEXTURE_COORD_ARRAY = 1 << 1

def glEnableClientState(state):
  if state == GL_VERTEX_ARRAY:
    glEnableVertexAttribArray(0)
  elif state == GL_TEXTURE_COORD_ARRAY:
    glEnableVertexAttribArray(2)

def glDisableClientState(state):
  if state == GL_VERTEX_ARRAY:
    glDisableVertexAttribArray(0)
  elif state == GL_TEXTURE_COORD_ARRAY:
    glDisableVertexAttribArray(2)

GL_CURRENT_BIT = 1 << 0

_attribStack = []

def glPushAttrib(attrib):
  assert attrib == GL_CURRENT_BIT
  _attribStack.insert(0, glGetFloatv(GL_CURRENT_COLOR))

def glPopAttrib():
  color = _attribStack.pop(0)
  glColor4f(color[0], color[1], color[2], color[3])

def glTexImage2D(target, level, internalFormat, width, height, border, format, type, data):
  pixels = array("c", data)
  pogles.gles2.glTexImage2D(target, level, format, width, height, border, format, type, pixels.buffer_info()[0])

def glTexSubImage2D(target, level, xOffset, yOffset, width, height, format, type, data):
  pixels = array("c", data)
  pogles.gles2.glTexSubImage2D(target, level, xOffset, yOffset, width, height, format, type, pixels.buffer_info()[0])

GL_QUADS = 0

_vertexPointer = None
_texCoordPointer = None

def glVertexPointer(size, type, stride, data):
  global _vertexPointer
  _vertexPointer = data
  glVertexAttribPointer(0, size, type, False, stride, data.buffer_info()[0])

def glTexCoordPointer(size, type, stride, data):
  global _texCoordPointer
  _texCoordPointer = data
  glVertexAttribPointer(2, size, type, False, stride, data.buffer_info()[0])

def glDrawArrays(mode, start, count):
  _useDefaultProgram()
  _applyUniforms()
  import random
  #for i in range(count):
    #_vertexPointer[i * 2] /= random.random()
    #_vertexPointer[i * 2 + 1] = random.random()
    #_vertexPointer[i * 2] *= 1.1
    #_vertexPointer[i * 2 + 1] *= 1.1
  #glVertexAttribPointer(0, 2, GL_FLOAT, False, 0, _vertexPointer.buffer_info()[0])
  #glVertexAttribPointer(2, 2, GL_FLOAT, False, 0, _texCoordPointer.buffer_info()[0])
  #print "DRAW ARRAYS", mode, start, count
  #print _textureEnabled
  #print _vertexPointer
  #glViewport(0, 0, 320, 240)
  if not _colorEnabled:
    glVertexAttrib4f(1, 1, 1, 1, 1)
  #glVertexAttrib4f(1, 0, 1, 0, 1)
  #print _texCoordPointer
  pogles.gles2.glDrawArrays(mode, start, count)
