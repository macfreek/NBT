#!/usr/bin/env python
"""
Reads a NBT file, and print its contents in human-readable format.
"""

import locale, os, sys

# local module
try:
    import nbt
except ImportError:
    # nbt not in search path. Let's see if it can be found in the parent folder
    extrasearchpath = os.path.realpath(os.path.join(__file__,os.pardir,os.pardir))
    if not os.path.exists(os.path.join(extrasearchpath,'nbt')):
        raise
    sys.path.append(extrasearchpath)
from nbt.nbt import NBTFile


if __name__ == '__main__':
    if (len(sys.argv) == 1):
        print("No file(s) specified!")
        sys.exit(64) # EX_USAGE
    for nbtfile in sys.argv[1:]:
        try:
            print(nbtfile)
            nbttag = NBTFile(nbtfile)
            print(nbttag.pretty_tree())
        except IOError as e:
            sys.stderr.write("%s: %s\n" % (e.filename, e.strerror))
            sys.exit(72) # EX_IOERR
    sys.exit(0)

