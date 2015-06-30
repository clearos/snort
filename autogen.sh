#!/bin/sh

find $(pwd) -name configure.in | xargs touch

# Regenerate configuration files
libtoolize --automake --copy || exit 1
aclocal -I m4 || exit 1
automake --foreign --include-deps --add-missing --copy || exit 1
autoreconf -i -f || exit 1
