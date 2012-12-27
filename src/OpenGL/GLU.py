# Fake GLU for Raspberry Pi
import pogles
from array import array
from GL import glMultMatrixf
import numpy
import transformations
import math

def gluBuild2DMipmaps(target, internalFormat, width, height, format, type, data):
  pixels = array("c", data)
  pogles.gles2.glTexImage2D(target, 0, format, width, height, 0, format, type, pixels.buffer_info()[0])
  pogles.gles2.glGenerateMipmap(target)

def gluPerspective(fovy, aspect, zNear, zFar):
  range = math.tan(numpy.radians(fovy / 2.0)) * zNear
  left = -range * aspect
  right = range * aspect
  bottom = -range
  top = range

  m = numpy.zeros((4, 4))
  m[0, 0] = (2.0 * zNear) / (right - left)
  m[1, 1] = (2.0 * zNear) / (top - bottom)
  m[2, 2] = -(zFar + zNear) / float(zFar - zNear)
  m[2, 3] = -1
  m[3, 2] = -(2.0 * zFar * zNear) / (zFar - zNear)
  glMultMatrixf(m)

def _normalize(v):
  return v / math.sqrt(numpy.dot(v, v))

def gluLookAt(eyeX, eyeY, eyeZ, centerX, centerY, centerZ, upX, upY, upZ):
  eye = numpy.array([eyeX, eyeY, eyeZ])
  center = numpy.array([centerX, centerY, centerZ])
  up = numpy.array([upX, upY, upZ])

  f = _normalize(center - eye)
  u = _normalize(up)
  s = _normalize(numpy.cross(f, u))
  u = numpy.cross(s, f)

  m = transformations.identity_matrix()
  m[0, 0] = s[0]
  m[1, 0] = s[1]
  m[2, 0] = s[2]
  m[0, 1] = u[0]
  m[1, 1] = u[1]
  m[2, 1] = u[2]
  m[0, 2] = -f[0]
  m[1, 2] = -f[1]
  m[2, 2] = -f[2]
  m[3, 0] = -numpy.dot(s, eye)
  m[3, 1] = -numpy.dot(u, eye)
  m[3, 2] = numpy.dot(f, eye)
  glMultMatrixf(m)
