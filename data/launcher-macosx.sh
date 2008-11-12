#!/bin/sh
cd "$(dirname "$0")"
while true; do
  LD_LIBRARY_PATH=../Frameworks ./FretsOnFire.bin
  RET=$?
  # If we werem't given back the magic restart code, don't restart the game
  if [ "$RET" -ne "100" ]; then
    exit $RET
  fi
done
