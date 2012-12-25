# Fake GLU for Raspberry Pi
import pogles
from array import array

def gluBuild2DMipmaps(target, internalFormat, width, height, format, type, data):
  pixels = array("c", data)
  pogles.gles2.glTexImage2D(target, 0, format, width, height, 0, format, type, pixels.buffer_info()[0])
  pogles.gles2.glGenerateMipmap(target)
