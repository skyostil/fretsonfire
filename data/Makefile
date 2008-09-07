TOP?=..
PYTHON?=python

ifneq "$(findstring Windows_NT, $(OS))" ""
  INKSCAPE="c:/Program Files/inkscape/inkscape.exe"
else
  INKSCAPE=inkscape
endif

all: graphics translations
DATA=$(TOP)/data

# Only PNG files that can be generated automatically are listed here
IMAGES=\
$(DATA)/2x.png \
$(DATA)/3x.png \
$(DATA)/4x.png \
$(DATA)/ball1.png \
$(DATA)/ball2.png \
$(DATA)/cassette.png \
$(DATA)/editor.png \
$(DATA)/keyboard.png \
$(DATA)/koopa.png \
$(DATA)/koopa2.png \
$(DATA)/left.png \
$(DATA)/light.png \
$(DATA)/loading.png \
$(DATA)/logo.png \
$(DATA)/mods/Chilly/flame1.png \
$(DATA)/mods/Chilly/flame2.png \
$(DATA)/mods/Chilly/logo.png \
$(DATA)/mods/Chilly/neck.png \
$(DATA)/mods/LightGraphics/2x.png \
$(DATA)/mods/LightGraphics/3x.png \
$(DATA)/mods/LightGraphics/4x.png \
$(DATA)/mods/LightGraphics/ball1.png \
$(DATA)/mods/LightGraphics/ball2.png \
$(DATA)/mods/LightGraphics/cassette.png \
$(DATA)/mods/LightGraphics/editor.png \
$(DATA)/mods/LightGraphics/flame1.png \
$(DATA)/mods/LightGraphics/flame2.png \
$(DATA)/mods/LightGraphics/keyboard.png \
$(DATA)/mods/LightGraphics/left.png \
$(DATA)/mods/LightGraphics/light.png \
$(DATA)/mods/LightGraphics/loading.png \
$(DATA)/mods/LightGraphics/logo.png \
$(DATA)/mods/LightGraphics/pose.png \
$(DATA)/mods/LightGraphics/right.png \
$(DATA)/mods/LightGraphics/star.png \
$(DATA)/mods/LightGraphics/star1.png \
$(DATA)/mods/LightGraphics/star2.png \
$(DATA)/pose.png \
$(DATA)/right.png \
$(DATA)/songs/tutorial/esc.png \
$(DATA)/songs/tutorial/keyboard.png \
$(DATA)/songs/tutorial/pose.png \
$(DATA)/stage_audience1.png \
$(DATA)/stage_audience2.png \
$(DATA)/stage_background.png \
$(DATA)/stage_bassdrum.png \
$(DATA)/stage_drums.png \
$(DATA)/stage_light.png \
$(DATA)/stage_lights1.png \
$(DATA)/stage_lights2.png \
$(DATA)/stage_speakers.png \
$(DATA)/stage_speaker_cones.png \
$(DATA)/star.png \
$(DATA)/star1.png \
$(DATA)/star2.png

graphics: $(IMAGES)

translations:
	@pushd $(TOP)/data/translations ; $(PYTHON) update.py ; popd

killscores:
	@pushd $(TOP)/data/songs ; ./killscores.sh ; popd

%.png: %.svg
	$(INKSCAPE) -e "$@" -D -f "$<" -b black -y 0.0

.PHONY: graphics translations killscores
