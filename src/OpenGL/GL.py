# Fake GL for Raspberry Pi
from pogles.gles2 import *
from array import array
import pogles
import pygame
import numpy
import transformations

GL_CLAMP = GL_CLAMP_TO_EDGE
GL_MODULATE = 0
GL_COLOR_MATERIAL = 0xb57
GL_NORMALIZE = 0xba1

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
_lightingEnabled = False

def glEnable(param):
  global _colorEnabled
  global _textureEnabled
  global _lightingEnabled
  if _currentList:
    _currentList.commands.append(lambda: glEnable(param))
    return
  if param == GL_TEXTURE_2D:
    _textureEnabled = True
  elif param == GL_COLOR_MATERIAL:
    _colorEnabled = True
  elif param == GL_LIGHTING:
    _lightingEnabled = True
  elif param >= GL_LIGHT0 and param < GL_LIGHT0 + 8:
    pass
  else:
    pogles.gles2.glEnable(param)

def glDisable(param):
  global _colorEnabled
  global _textureEnabled
  global _lightingEnabled
  if _currentList:
    _currentList.commands.append(lambda: glDisable(param))
    return
  if param == GL_TEXTURE_2D:
    _textureEnabled = False
  elif param == GL_COLOR_MATERIAL:
    _colorEnabled = False
  elif param == GL_LIGHTING:
    _lightingEnabled = False
  elif param >= GL_LIGHT0 and param < GL_LIGHT0 + 8:
    pass
  else:
    pogles.gles2.glDisable(param)

GL_PERSPECTIVE_CORRECTION_HINT = 0
GL_NICEST = 0

def glHint(hint, value):
  pass

def glDeleteTextures(names):
  if not type(names) == list:
    names = [names]
  pogles.gles2.glDeleteTextures(names)

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
  if _currentList:
    _currentList.commands.append(lambda: glLoadIdentity())
    return
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
  if _currentList:
    _currentList.commands.append(lambda: glPushMatrix())
    return
  _activeStack.insert(0, _activeStack[0])

def glPopMatrix():
  if _currentList:
    _currentList.commands.append(lambda: glPopMatrix())
    return
  _activeStack.pop(0)

def glMultMatrixf(matrix):
  m = numpy.transpose(numpy.reshape(matrix, (4, 4)))
  _activeStack[0] = _activeStack[0].dot(m)

def glScalef(x, y, z):
  if _currentList:
    _currentList.commands.append(lambda: glScalef(x, y, z))
    return
  m = numpy.array([
      [x, 0, 0, 0],
      [0, y, 0, 0],
      [0, 0, z, 0],
      [0, 0, 0, 1]])
  _activeStack[0] = _activeStack[0].dot(m)

def glTranslatef(x, y, z):
  if _currentList:
    _currentList.commands.append(lambda: glTranslatef(x, y, z))
    return
  m = transformations.translation_matrix((x, y, z))
  _activeStack[0] = _activeStack[0].dot(m)

def glRotate(angle, x, y, z):
  if _currentList:
    _currentList.commands.append(lambda: glRotate(angle, x, y, z))
    return
  m = transformations.rotation_matrix(numpy.radians(angle), (x, y, z))
  _activeStack[0] = _activeStack[0].dot(m)

glRotatef = glRotate

_maxVertices = 16
_vertexIndex = 0
_primitive = None
_perVertexAttributes = 0
_color = array('f', [1, 1, 1, 1] * _maxVertices)
_texCoord = array('f', [0, 0] * _maxVertices)
_position = array('f', [0, 0, 0, 1] * _maxVertices)
_normal = array('f', [0, 0, 0] * _maxVertices)

_vertSource = """
attribute vec4 a_position;
attribute vec4 a_color;
attribute vec2 a_texCoord;
attribute vec3 a_normal;

uniform mat4 u_modelviewProjectionMatrix;

varying vec4 v_color;
varying vec2 v_texCoord;
varying vec3 v_normal;

void main()
{
    gl_Position = u_modelviewProjectionMatrix * a_position;
    v_color = a_color;
    v_texCoord = a_texCoord;
    v_normal = a_normal;
}
"""

_fragSource = """
varying vec4 v_color;
varying vec2 v_texCoord;
varying vec3 v_normal;

uniform sampler2D u_texture;
uniform bool u_textureEnabled;

void main()
{
    vec4 color = v_color;
    if (u_textureEnabled)
        color = texture2D(u_texture, v_texCoord) * color;
    /*gl_FragColor += vec4(v_texCoord.x, v_texCoord.y, 0.2, 1.0);*/
    /*color.a += 0.3;*/
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
  glBindAttribLocation(program, 3, "a_normal")
  glLinkProgram(program)
  glDeleteShader(vertShader)
  glDeleteShader(fragShader)

  linked = glGetProgramiv(program, GL_LINK_STATUS)
  if not linked:
    raise Exception("Error linking program:\n%s" % glGetProgramInfoLog(program))
  return program

def glBegin(primitive):
  global _primitive
  global _perVertexAttributes
  _primitive = primitive
  _perVertexAttributes = 0

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
  global _vertexIndex

  if _currentList:
    _currentList.position.extend(_position[:_vertexIndex * 4])
    if _perVertexAttributes & 1 << 1:
      _currentList.color.extend(_color[:_vertexIndex * 4])
    if _perVertexAttributes & 1 << 2:
      _currentList.texCoord.extend(_texCoord[:_vertexIndex * 2])
    if _perVertexAttributes & 1 << 3:
      _currentList.normal.extend(_normal[:_vertexIndex * 3])
    if not _currentList.commands or _currentList.commands[-1] != _primitive:
      _currentList.commands.append( _primitive)
    _vertexIndex = 0
    return

  _useDefaultProgram()
  _applyUniforms()

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
  glVertexAttribPointer(3, 3, GL_FLOAT, False, 0, _normal.buffer_info()[0])
  glEnableVertexAttribArray(3)

  pogles.gles2.glDrawArrays(_primitive, 0, _vertexIndex)
  glDisableVertexAttribArray(0)
  glDisableVertexAttribArray(1)
  glDisableVertexAttribArray(2)
  glDisableVertexAttribArray(3)

  _vertexIndex = 0

def glColor4f(r, g, b, a):
  global _perVertexAttributes
  _perVertexAttributes |= 1 << 1
  i = _vertexIndex * 4
  _color[i] = r
  _color[i + 1] = g
  _color[i + 2] = b
  _color[i + 3] = a
  glVertexAttrib4f(1, r, g, b, a)

def glColor3f(r, g, b):
  glColor4f(r, g, b, 1)

def glTexCoord2f(x, y):
  global _perVertexAttributes
  _perVertexAttributes |= 1 << 2
  i = _vertexIndex * 2
  _texCoord[i] = x
  _texCoord[i + 1] = y
  glVertexAttrib2f(2, x, y)

def glNormal3f(x, y, z):
  global _perVertexAttributes
  _perVertexAttributes |= 1 << 3
  i = _vertexIndex * 3
  _normal[i] = x
  _normal[i + 1] = y
  _normal[i + 2] = z
  glVertexAttrib3f(3, x, y, z)

def glVertex3f(x, y, z):
  global _vertexIndex
  i = _vertexIndex * 4
  _position[i] = x
  _position[i + 1] = y
  _position[i + 2] = z
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
  i = _vertexIndex * 3
  j = (_vertexIndex - 1) * 3
  _normal[i] = _normal[j]
  _normal[i + 1] = _normal[j + 1]
  _normal[i + 2] = _normal[j + 2]

def glVertex2f(x, y):
  glVertex3f(x, y, 0)

GL_VERTEX_ARRAY = 1
GL_COLOR_ARRAY = 2
GL_TEXTURE_COORD_ARRAY = 3

def glEnableClientState(state):
  if state == GL_VERTEX_ARRAY:
    glEnableVertexAttribArray(0)
  elif state == GL_COLOR_ARRAY:
    glEnableVertexAttribArray(1)
  elif state == GL_TEXTURE_COORD_ARRAY:
    glEnableVertexAttribArray(2)

def glDisableClientState(state):
  if state == GL_VERTEX_ARRAY:
    glDisableVertexAttribArray(0)
  elif state == GL_COLOR_ARRAY:
    glDisableVertexAttribArray(1)
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
_colorPointer = None

def glVertexPointer(size, type, stride, data):
  global _vertexPointer
  _vertexPointer = data
  glVertexAttribPointer(0, size, type, False, stride, data.buffer_info()[0])

def glColorPointer(size, type, stride, data):
  global _colorPointer
  _colorPointer = data
  glVertexAttribPointer(1, size, type, False, stride, data.buffer_info()[0])

def glTexCoordPointer(size, type, stride, data):
  global _texCoordPointer
  _texCoordPointer = data
  glVertexAttribPointer(2, size, type, False, stride, data.buffer_info()[0])

def glDrawArrays(mode, start, count):
  _useDefaultProgram()
  _applyUniforms()
  if not _colorEnabled:
    glVertexAttrib4f(1, 1, 1, 1, 1)
  pogles.gles2.glDrawArrays(mode, start, count)

GL_LIGHTING = 0x0b50
GL_LIGHT0 = 0x4000
GL_SMOOTH = 0x1d01
GL_POSITION = 0x1203
GL_AMBIENT = 0x1200
GL_DIFFUSE = 0x1201
GL_FRONT_AND_BACK = 0x0408
GL_SHININESS = 0x1601
GL_SPECULAR = 0x1202

def glShadeModel(model):
  pass

def glLightfv(light, param, value):
  pass

def glMaterialf(face, param, value):
  pass

def glMaterialfv(face, param, value):
  pass

GL_COMPILE = 0x1300

class DisplayList(object):
  def __init__(self):
    self.commands = []
    self.position = array("f")
    self.color = array("f")
    self.texCoord = array("f")
    self.normal = array("f")

  def call(self):
    for command in self.commands:
      if type(command) == int:
        self.draw(command)
      else:
        command()

  def draw(self, primitive):
    _useDefaultProgram()
    _applyUniforms()

    # TODO: Use VBOs
    glVertexAttribPointer(0, 4, GL_FLOAT, False, 0, self.position.buffer_info()[0])
    glEnableVertexAttribArray(0)
    if len(self.color):
      glVertexAttribPointer(1, 4, GL_FLOAT, False, 0, self.color.buffer_info()[0])
      glEnableVertexAttribArray(1)
    else:
      i = _vertexIndex * 4
      glVertexAttrib4f(1, _color[i], _color[i + 1], _color[i + 2], _color[i + 3])
    if len(self.texCoord):
      glVertexAttribPointer(2, 2, GL_FLOAT, False, 0, self.texCoord.buffer_info()[0])
      glEnableVertexAttribArray(2)
    if len(self.normal):
      glVertexAttribPointer(3, 3, GL_FLOAT, False, 0, self.normal.buffer_info()[0])
      glEnableVertexAttribArray(3)

    count = len(self.position) / 4
    pogles.gles2.glDrawArrays(primitive, 0, count)

    glDisableVertexAttribArray(0)
    glDisableVertexAttribArray(1)
    glDisableVertexAttribArray(2)
    glDisableVertexAttribArray(3)

_lists = []
_currentList = None

def glGenLists(n):
  assert n == 1
  _lists.append(DisplayList())
  return len(_lists) - 1

def glNewList(name, mode):
  global _currentList
  assert mode == GL_COMPILE
  _currentList = _lists[name]

def glEndList():
  global _currentList
  _currentList = None

def glCallList(name):
  if _currentList:
    _currentList.commands.append(lambda: glCallList(name))
    return
  _lists[name].call()
