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
            # Try to read nbt file, assuming the NBT file is GZipped.
            try:
                nbttag = None
                fileobj = open(nbtfile, 'rb')
                nbttag = NBTFile()
                nbttag.parse_file(fileobj = fileobj)
            except (OSError, IOError) as exc:
                if 'Not a gzipped file' in str(exc):
                    pass
                else:
                    raise
            finally:
                try:
                    fileobj.close()
                except Exception:
                    pass
            if not nbttag:
                # File is not GZipped. Try to open the NBT assuming no compression.
                try:
                    fileobj = open(nbtfile, 'rb')
                    nbttag = NBTFile()
                    nbttag.parse_file(buffer = fileobj)
                    fileobj.close()
                finally:
                    try:
                        fileobj.close()
                    except Exception:
                        pass
        except Exception as e:
            try:
                print(nbttag.pretty_tree())
            except Exception:
                pass
            sys.stderr.write("%s %s\n" % (type(e), str(e)))
            raise
        else:
            print(nbttag.pretty_tree())
    sys.exit(0)
