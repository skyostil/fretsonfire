#!/bin/sh
export LD_LIBRARY_PATH=$(dirname $0)
exec ./FretsOnFire.bin $@
