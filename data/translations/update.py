#!/usr/bin/python
import os

translations = {
  "fr":  "french",
  "ger": "german",
  "po":  "polish",
  "rus": "russian",
  "sw":  "swedish",
  "por": "brazilian_portuguese",
  "he":  "hebrew",
  "es":  "spanish",
  "it":  "italian",
  "gl":  "galician",
}

files = ["fretsonfire", "tutorial"]

for id, lang in translations.items():
  print "%s:" % lang,
  f = ["%s_%s.po" % (fn, id) for fn in files]
  ret = os.system("msgcat " + " ".join(f) + " | msgfmt - -o %s.mo" % lang)
  if not ret:
    print "ok"
  else:
    print "error", ret
  
