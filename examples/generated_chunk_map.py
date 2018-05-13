#!/usr/bin/env python
"""
Prints a map of the entire world.
"""

import locale, os, sys
import re, math
from struct import pack, unpack
# local module
try:
    import nbt
except ImportError:
    # nbt not in search path. Let's see if it can be found in the parent folder
    extrasearchpath = os.path.realpath(os.path.join(__file__,os.pardir,os.pardir))
    if not os.path.exists(os.path.join(extrasearchpath,'nbt')):
        raise
    sys.path.append(extrasearchpath)
from nbt.region import RegionFile
from nbt.chunk import Chunk
from nbt.world import WorldFolder,McRegionWorldFolder
# PIL module (not build-in)
try:
    from PIL import Image
except ImportError:
    # PIL not in search path. Let's see if it can be found in the parent folder
    sys.stderr.write("Module PIL/Image not found. Pillow (a PIL fork) can be found at http://python-pillow.org//\n")
    # Note: it may also be possible that PIL is installed, but JPEG support is disabled or broken
    sys.exit(70) # EX_SOFTWARE

def main(world_folder, show=True):
    world = WorldFolder(world_folder)  # map still only supports McRegion maps
    bb = world.get_boundingbox()
    map = Image.new('RGB', (bb.lenx(),bb.lenz()))

    for region in world.iter_regions():
        sys.stdout.write(".")
        sys.stdout.flush()
        for chunk_meta in region.metadata.values():
            x = 32*region.x + chunk_meta.x
            z = 32*region.z + chunk_meta.z
            if (x, None, z) not in bb:
                continue
            x -= bb.minx
            z -= bb.minz
            status = chunk_meta.status
            if status == 0:
                color = (255,255,255) # white
            elif status == 1:
                color = (63,63,63) # dark gray
            else:
                color = (255,0,0) # red
            map.putpixel((x,z), color)
    sys.stdout.write("\n")
    filename = os.path.basename(world_folder)+"_chunks.png"
    map.save(filename,"PNG")
    print("Saved map as %s" % filename)
    map.show()
    return 0 # NOERR


if __name__ == '__main__':
    if (len(sys.argv) == 1):
        print("No world folder specified!")
        sys.exit(64) # EX_USAGE
    if sys.argv[1] == '--noshow' and len(sys.argv) > 2:
        show = False
        world_folder = sys.argv[2]
    else:
        show = True
        world_folder = sys.argv[1]
    # clean path name, eliminate trailing slashes. required for os.path.basename()
    world_folder = os.path.normpath(world_folder)
    if (not os.path.exists(world_folder)):
        print("No such folder as "+world_folder)
        sys.exit(72) # EX_IOERR
    
    sys.exit(main(world_folder, show))
