# Fake pygame for Raspberry Pi
import time as _time
from pogles.egl import *
from pogles.platform import ppCreateNativeWindow

OPENGL = 1 << 0
DOUBLEBUF = 1 << 1

USEREVENT = 1 << 0

GL_RED_SIZE = 1
GL_GREEN_SIZE = 2
GL_BLUE_SIZE = 3
GL_ALPHA_SIZE = 4

K_LEFT = 1
K_RIGHT = 2
K_UP = 3
K_DOWN = 4
K_RETURN = 5
K_RSHIFT = 6
K_F1 = 7
K_F2 = 8
K_F3 = 9
K_F4 = 10
K_F5 = 11
K_ESCAPE = 12

def todo(what):
  print "TODO:", what

class Time(object):
  @staticmethod
  def get_ticks():
    return _time.time() * 1000

class Music(object):
  def set_endevent(self, event):
    pass

class Sound(object):
  def __init__(self, fileName):
    self.fileName = fileName

  def set_volume(self, volume):
    pass

  def play(self, loops):
    todo("play " + self.fileName)

class Mixer(object):
  def __init__(self):
    self.music = Music()
    self.Sound = Sound

  def pre_init(self, *args):
    pass

  def init(self, *args):
    pass

  def get_init(self):
    return (0, 0, 0)

class Display(object):
  def __init__(self):
    self.nativeWindow = None
    self.display = None
    self.context = None
    self.surface = None
    self.width = None
    self.height = None

  def init(self):
    pass

  def gl_set_attribute(self, attrib, value):
    pass

  def set_mode(self, resolution, flags):
    self.nativeWindow = ppCreateNativeWindow()
    self.display = eglGetDisplay()
    eglInitialize(self.display)

    attribs = [
      EGL_BUFFER_SIZE, 16,
      EGL_RED_SIZE, 5,
      EGL_GREEN_SIZE, 6,
      EGL_BLUE_SIZE, 5
    ]

    config = eglChooseConfig(self.display, attribs)[0]
    self.surface = eglCreateWindowSurface(self.display, config, self.nativeWindow, [])

    self.context = eglCreateContext(self.display, config, None, [EGL_CONTEXT_CLIENT_VERSION, 2])
    eglMakeCurrent(self.display, self.surface, self.surface, self.context)

    self.width = eglQuerySurface(self.display, self.surface, EGL_WIDTH)
    self.height = eglQuerySurface(self.display, self.surface, EGL_HEIGHT)

  def flip(self):
    eglSwapBuffers(self.display, self.surface)

  def list_modes(self):
    return [(self.width, self.height)]

  def set_caption(self, caption):
    pass

class Mouse(object):
  def set_visible(self, visible):
    pass

class Key(object):
  def set_repeat(self, delay, rate):
    pass

  def name(self, id):
    return "key-%d" % id

class Joystick(object):
  def init(self):
    pass

  def get_count(self):
    return 0

class Event(object):
  def pump(self):
    pass

  def get(self):
    return []

class Surface(object):
  def __init__(self, width, height):
    self.width = width
    self.height = height

  def get_size(self):
    return (self.width, self.height)

class Image(object):
  def tostring(self, surface, mode, flipped):
    assert mode == "RGBA"
    return "\x00" * (surface.width * surface.height * 4)

class Font(object):
  def __init__(self, fileName, size):
    self.fileName = fileName
    self._size = size

  def set_bold(self, bold):
    pass

  def set_italic(self, italic):
    pass

  def set_underline(self, underine):
    pass

  def size(self, text):
    return (self._size / 2 * len(text), self._size)

  def get_height(self):
    return self._size

  def render(self, text, antialias, color):
    s = self.size(text)
    return Surface(s[0], s[1])

class FontModule(object):
  def __init__(self):
    self.Font = Font

  def init(self):
    pass

def init():
  pass

time = Time()
mixer = Mixer()
display = Display()
mouse = Mouse()
key = Key()
joystick = Joystick()
event = Event()
font = FontModule()
image = Image()
