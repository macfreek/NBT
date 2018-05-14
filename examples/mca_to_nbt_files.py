#!/usr/bin/env python
"""
Extract raw NBT data from MCA (or MCR) region files, and store them in separate unencrypted NBT files.
Useful for debugging NBT.
"""
import locale, os, sys
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
from nbt.region import RegionFile, RegionFileFormatError
from nbt.chunk import Chunk
from nbt.world import WorldFolder,UnknownWorldFormat


def main(region_file):
    region = RegionFile(region_file)
    for m in region.get_metadata():
        try:
            nbt_data = region.get_blockdata(m.x, m.z)
        except RegionFileFormatError as exc:
            print("Chunk %d,%d give error: %s" % (m.x, m.z, exc))
        
        # Chunk filename are not the same as alpha-level files, but look a bit like it.
        chunk_file = 'c.%d.%d.dat' % (m.x, m.z)
        chunk_path = os.path.join(os.path.dirname(region_file), chunk_file)
        with open(chunk_path, 'wb') as f:
            f.write(nbt_data)
            print("Chunk %d,%d written to %s" % (m.x, m.z, chunk_file))
    
    return 0 # NOERR


if __name__ == '__main__':
    if (len(sys.argv) == 1):
        print("No region file specified!")
        sys.exit(64) # EX_USAGE
    region_file = sys.argv[1]
    # clean path name, eliminate trailing slashes:
    region_file = os.path.normpath(region_file)
    if (not os.path.exists(region_file)):
        print("No such file %s" % (region_file))
        sys.exit(72) # EX_IOERR
    
    sys.exit(main(region_file))
