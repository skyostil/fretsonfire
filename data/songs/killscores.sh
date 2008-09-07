for f in */song.ini; do cat "$f" | grep -v ^scores > "$f.tmp" ; mv "$f.tmp" "$f"; echo "Reset scores for $f"; done
