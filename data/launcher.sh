#!/bin/sh

# traverse symlinks
SCRIPT="$0"
if [ -L "${SCRIPT}" ]; then
    SCRIPT="`readlink -f "${SCRIPT}"`"
fi

# go to the program directory
cd "`dirname "$SCRIPT"`"

# set the ld path
export LD_LIBRARY_PATH={$LD_LIBRARY_PATH}:.

# run game
exec ./FretsOnFire.bin $@

# return exitcode
EXITCODE="$?"
exit ${EXITCODE}

