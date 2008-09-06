ifneq "$(findstring Windows_NT, $(OS))" ""
  INKSCAPE="c:/Program Files/inkscape/inkscape.exe"
else
  INKSCAPE=inkscape
endif

all: graphics

IMAGES=\
2x.png \
3x.png \
4x.png \
ball1.png \
ball2.png \
cassette.png \
editor.png \
glow.png \
keyboard.png \
koopa.png \
koopa2.png \
left.png \
light.png \
loading.png \
logo.png \
mods/Chilly/flame1.png \
mods/Chilly/flame2.png \
mods/Chilly/logo.png \
mods/Chilly/neck.png \
mods/LightGraphics/2x.png \
mods/LightGraphics/3x.png \
mods/LightGraphics/4x.png \
mods/LightGraphics/ball1.png \
mods/LightGraphics/ball2.png \
mods/LightGraphics/cassette.png \
mods/LightGraphics/editor.png \
mods/LightGraphics/flame1.png \
mods/LightGraphics/flame2.png \
mods/LightGraphics/glow.png \
mods/LightGraphics/keyboard.png \
mods/LightGraphics/left.png \
mods/LightGraphics/light.png \
mods/LightGraphics/loading.png \
mods/LightGraphics/logo.png \
mods/LightGraphics/neck.png \
mods/LightGraphics/pose.png \
mods/LightGraphics/right.png \
mods/LightGraphics/star.png \
mods/LightGraphics/star1.png \
mods/LightGraphics/star2.png \
neck.png \
pose.png \
right.png \
songs/tutorial/esc.png \
songs/tutorial/keyboard.png \
songs/tutorial/pose.png \
stage_audience1.png \
stage_audience2.png \
stage_background.png \
stage_bassdrum.png \
stage_drums.png \
stage_light.png \
stage_lights1.png \
stage_lights2.png \
stage_speakers.png \
stage_speaker_cones.png \
star.png \
star1.png \
star2.png \

graphics: $(IMAGES)

%.png: %.svg
	$(INKSCAPE) -e "$@" -D -f "$<" -b black -y 0.0

