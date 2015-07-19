#!/usr/bin/env python
import sys
import os
import logging

import unittest
try:
    from unittest import skip as _skip
except ImportError:
    # Python 2.6 has an older unittest API. The backported package is available from pypi.
    import unittest2 as unittest

# local modules
import downloadsample
from utils import open_files

# Search parent directory first, to make sure we test the local nbt module, 
# not an installed nbt module.
parentdir = os.path.realpath(os.path.join(os.path.dirname(__file__),os.pardir))
if parentdir not in sys.path:
    sys.path.insert(1, parentdir) # insert ../ just after ./

from nbt.world import McRegionWorldFolder, AnvilWorldFolder, WorldFolder, \
    BoundingBox, UnknownWorldFormat
from nbt.region import RegionFile, InconceivedChunk
from nbt.nbt import NBTFile

_DEFINED_CHUNKS_ROWS = {
    # Chunks defined in Sample World.
    #x: [ z,z,z,z,z,z ]
    -1: [                              16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32],
     0: [                           15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31],
     1: [                        14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32],
     2: [                           15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32],
     3: [                        14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33],
     4: [4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33],
     5: [4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33],
     6: [4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33],
     7: [  5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33],
     8: [  5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33],
     9: [    6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33],
    10: [      7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32],
    11: [      7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32],
    12: [      7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32],
    13: [      7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32],
    14: [      7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32],
    15: [      7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32],
    16: [      7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32],
    17: [      7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31],
    18: [      7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31],
    19: [      7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29],
    20: [      7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28],
    21: [      7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28],
    22: [      7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26],
    23: [        8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26],
    24: [          9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25],
    25: [          9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25],
    26: [               11,12,13,14,15,16,17,18,19,20,21,22,23,24],
}
DEFINED_CHUNKS = [(x,z) for x,z_vals in _DEFINED_CHUNKS_ROWS.items() for z in z_vals]

class BasicMethodTest(unittest.TestCase):
    """Tests the methods of the WorldFolder classes."""
    # Define class variables
    world = None
    worlddir = None
    @classmethod
    def setUpClass(cls):
        """Download sample world, and copy Anvil files to temporary folders."""
        if cls.world == None:
            downloadsample.install()
            cls.worlddir = downloadsample.temp_anvil_world()
            cls.world = WorldFolder(cls.worlddir)
    @classmethod
    def tearDownClass(cls):
        """Remove temporary folders with Anvil or McRegion files."""
        if cls.world != None:
            downloadsample.cleanup_temp_world(cls.worlddir)
            cls.world = None
            cls.worlddir = None
    
    def test_get_filenames(self):
        filenames = self.world.get_filenames()
        self.assertEqual(len(filenames), 4)
        self.assertIn(os.path.join(self.worlddir, 'region/r.-1.0.mca'), filenames)
        self.assertIn(os.path.join(self.worlddir, 'region/r.-1.1.mca'), filenames)
        self.assertIn(os.path.join(self.worlddir, 'region/r.0.0.mca'), filenames)
        self.assertIn(os.path.join(self.worlddir, 'region/r.0.1.mca'), filenames)
    def test_get_regionfiles(self):
        filenames = self.world.get_regionfiles()
        self.assertEqual(len(filenames), 4)
        self.assertIn(os.path.join(self.worlddir, 'region/r.-1.0.mca'), filenames)
        self.assertIn(os.path.join(self.worlddir, 'region/r.-1.1.mca'), filenames)
        self.assertIn(os.path.join(self.worlddir, 'region/r.0.0.mca'), filenames)
        self.assertIn(os.path.join(self.worlddir, 'region/r.0.1.mca'), filenames)
    def test_nonempty(self):
        self.assertTrue(self.world.nonempty())
    def test_get_existing_region(self):
        regionfile = self.world.get_region(-1,0)
        self.assertTrue(isinstance(regionfile, RegionFile))
    @unittest.skip("Known error")
    def test_get_nonexisting_region(self):
        # TODO: this currently fails! Need to fix world.py
        regionfile = self.world.get_region(1,1)
    def test_chunk_count(self):
        self.assertEqual(self.world.chunk_count(), len(DEFINED_CHUNKS))
    def test_iter_regions(self):
        regions = list(self.world.iter_regions())
        self.assertEqual(len(regions), 4)
        filenames = []
        for region in regions:
            self.assertTrue(isinstance(region, RegionFile))
            filenames.append(os.path.basename(region.filename))
        self.assertIn('r.-1.0.mca', filenames)
        self.assertIn('r.-1.1.mca', filenames)
        self.assertIn('r.0.0.mca', filenames)
        self.assertIn('r.0.1.mca', filenames)
    def test_iter_nbt(self):
        """Test if iter_nbt yields NBTFiles, and yields all possible locations."""
        nbts = list(self.world.iter_nbt())
        self.assertEqual(len(nbts), len(DEFINED_CHUNKS))
        nbt_locs = []
        for nbt in nbts:
            self.assertTrue(isinstance(nbt, NBTFile))
            nbt_locs.append((nbt.loc.x,nbt.loc.z))
        for loc in DEFINED_CHUNKS:
            self.assertIn(loc, nbt_locs)
    def test_get_existing_nbt(self):
        nbt = self.world.get_nbt(-1,32)
        nbt = self.world.get_nbt(0,15)
        nbt = self.world.get_nbt(4,4)
        nbt = self.world.get_nbt(9,33)
    def test_get_non_existing_nbt(self):
        self.assertRaises(InconceivedChunk, self.world.get_nbt, 2,14)
    def test_get_nbt_in_non_existing_region(self):
        self.assertRaises(InconceivedChunk, self.world.get_nbt, 34,14)
    def test_get_boundingbox(self):
        bb = self.world.get_boundingbox()
        self.assertTrue(isinstance(bb, BoundingBox))
        self.assertEqual(bb.minx, -1)
        self.assertEqual(bb.maxx, 26)
        self.assertEqual(bb.miny, 4)
        self.assertEqual(bb.maxy, 33)

    @unittest.skip("Callbacks not implemented yet")
    def test_region_callback_unthreaded(self):
        callback_function = lambda x: x
        callback_results = list(self.world.call_for_each_region(callback_function, threaded=False))
        iter_results = [callback_function(the_nbt) for the_nbt in iter_nbt()]
        self.assertEqual(callback_results, iter_results)
    @unittest.skip("Callbacks not implemented yet")
    def test_region_callback_threaded(self):
        callback_function = lambda x: x # TODO: make this an object that keeps track how often it is called with what parameters.
        callback_results = list(self.world.call_for_each_region(callback_function))
        iter_results = [callback_function(the_nbt) for the_nbt in iter_nbt()]
        self.assertEqual(callback_results, iter_results)
        # TODO: check callback stats
    @unittest.skip("Callbacks not implemented yet")
    def test_region_callback_boxed(self):
        callback_function = lambda x: x # TODO: make this an object that keeps track how often it is called with what parameters.
        bb = BoundingBox() # TODO: add sensible parameters
        callback_results = list(self.world.call_for_each_region(callback_function, boundingbox=bb))
        iter_results = [callback_function(the_nbt) for the_nbt in iter_nbt(boundingbox=bb)]
        self.assertEqual(callback_results, iter_results)
        # TODO: check callback stats

    @unittest.skip("Callbacks not implemented yet")
    def test_nbt_callback_unthreaded(self):
        callback_function = lambda x: x
        callback_results = list(self.world.call_for_each_nbt(callback_function, threaded=False))
        iter_results = [callback_function(the_nbt) for the_nbt in iter_nbt()]
        self.assertEqual(callback_results, iter_results)
    @unittest.skip("Callbacks not implemented yet")
    def test_nbt_callback_threaded(self):
        callback_function = lambda x: x # TODO: make this an object that keeps track how often it is called with what parameters.
        callback_results = list(self.world.call_for_each_nbt(callback_function))
        iter_results = [callback_function(the_nbt) for the_nbt in iter_nbt()]
        self.assertEqual(callback_results, iter_results)
        # TODO: check callback stats
    @unittest.skip("Callbacks not implemented yet")
    def test_nbt_callback_boxed(self):
        callback_function = lambda x: x # TODO: make this an object that keeps track how often it is called with what parameters.
        bb = BoundingBox() # TODO: add sensible parameters
        callback_results = list(self.world.call_for_each_nbt(callback_function, boundingbox=bb))
        iter_results = [callback_function(the_nbt) for the_nbt in iter_nbt(boundingbox=bb)]
        self.assertEqual(callback_results, iter_results)
        # TODO: check callback stats

    @unittest.skip("Chunks not yet supported")
    def test_get_chunk(self,x,z):
        chunk = self.world.get_chunk(1,1) # TODO: pick another number.
        # TODO: test contents
    @unittest.skip("Chunks not yet supported")
    def test_get_chunks(self):
        chunks = list(self.world.get_chunks())
        # TODO: test length, contents
    @unittest.skip("Chunks not yet supported")
    def test_iter_chunks(self):
        chunks = list(self.world.iter_chunks())
        # TODO: test length, contents
    @unittest.skip("Chunks not yet supported")
    def test_boxed_sorted_iter_chunks(self):
        bb = BoundingBox() # TODO: add sensible parameters
        sortorder = lambda xyz: (xyz[0], xyz[2], xyz[1]) # TODO: create default sort orders
        chunks = list(self.world.iter_chunks(boundingbox=bb))
        # TODO: test length, contents
    @unittest.skip("Chunks not yet supported")
    def test_boxed_get_chunks(self):
        bb = BoundingBox() # TODO: add sensible parameters
        chunks = list(self.world.iter_chunks(boundingbox=bb))
        # TODO: test length, contents
    
    def test_location(self):
        """
        Debug routine: loop through all chunks, fetch them again by coordinates,
        and check if the same object is returned.
        """
        for nbt in self.world.iter_nbt():
            chunk = self.world.chunkclass(nbt)
            self.assertEqual((nbt.loc.x, nbt.loc.z), chunk.get_coords())
    @unittest.skip("Known failure. NBTFile objects have no equality test.")
    def test_equality(self):
        """
        Debug routine: loop through all chunks, fetch them again by coordinates,
        and check if the same object is returned.
        """
        # TODO: Add NBT.__eq__()
        for nbt in self.world.iter_nbt():
            # iter_nbt is not cached, but get_nbts is.
            nbt2 = self.world.get_nbt(nbt.loc.x, nbt.loc.z)
            self.assertEqual(nbt, nbt2)
    def test_region_caching(self):
        region1 = self.world.get_region(-1,1)
        region2 = self.world.get_region(-1,1)
        self.assertEqual(id(region1), id(region2))
    @unittest.skip("Known failure. NBTs are not cached")
    def test_nbt_caching(self):
        # TODO: Add caching to region.get_nbt()
        nbt1 = self.world.get_nbt(13,21)
        nbt2 = self.world.get_nbt(13,21)
        self.assertEqual(id(nbt1), id(nbt2))


class AnvilMcRegionFormatTest(unittest.TestCase):
    # TODO: add tests to check if a correct worldfolder is returned
    pass


class UnreadableWorldTest(unittest.TestCase):
    pass
    # TODO: add tests for:
    # - world folder unreadable (no r bit)
    # - world folder unreadable (no x bit)
    # - region file unreadable (no r bit)


class FileOpenCloseTest(unittest.TestCase):
    """Tests if region files wihtin a world are properly closed or retained open for caching."""
    def setUp(self):
        """Download sample world, and copy Anvil and McRegion files to temporary folders."""
        if ScriptTestCase.worldfolder == None:
            downloadsample.install()
            ScriptTestCase.worldfolder = downloadsample.worlddir
        if ScriptTestCase.mcregionfolder == None:
            ScriptTestCase.mcregionfolder = downloadsample.temp_mcregion_world()
        if ScriptTestCase.anvilfolder == None:
            ScriptTestCase.anvilfolder = downloadsample.temp_anvil_world()

    def tearDown(self):
        """Remove temporary folders with Anvil and McRegion files."""
        if ScriptTestCase.mcregionfolder != None:
            downloadsample.cleanup_temp_world(ScriptTestCase.mcregionfolder)
        if ScriptTestCase.anvilfolder != None:
            downloadsample.cleanup_temp_world(ScriptTestCase.anvilfolder)
        ScriptTestCase.worldfolder = None
        ScriptTestCase.mcregionfolder = None
        ScriptTestCase.anvilfolder = None

    # a new Worldfolder object should not open a file
    # fetching a specific object should open that file
    # fetching a specific object should cache that file (remain open when region object is not used)
    # iter_regions should NOT cache regions, (even if list is kept?)
    # get_regions should cache regions, even if list is deleted
    # get_region, followed by iter_regions should yield the same region object. This object should be cached, the rest should not.
    # get_nbt, followed by iter_nbt. One region should be cached, the rest should not.
    


class NBTWriteTest(unittest.TestCase):
    """Tests writing NBT objects to a world folder."""
    # TODO: Write Tests
    
    pass

    # def set_nbt(self,x,z,nbt):
    #     """
    #     Set a chunk. Overrides the NBT if it already existed. If the NBT did not exists,
    #     adds it to the Regionfile. May create a new Regionfile if that did not exist yet.
    #     nbt must be a nbt.NBTFile instance, not a Chunk or regular TAG_Compound object.
    #     """
    #     raise NotImplemented()
    #     # TODO: implement

    
    # def test00FileProperties(self):
    #     self.assertEqual(self.region.get_size(), self.length)
    #     self.assertEqual(self.region.chunk_count(), 2)
    #
    # def testSectors(self):
    #     """Test if RegionFile._sectors() detects the correct overlap."""
    #     sectors = self.region._sectors()
    #     chunk00metadata = self.region.metadata[0,0]
    #     chunk10metadata = self.region.metadata[1,0]
    #     self.assertEqual(len(sectors), 4)
    #     self.assertEqual(sectors[0], True)
    #     self.assertEqual(sectors[1], True)
    #     self.assertEqual(len(sectors[2]), 1)
    #     self.assertIn(chunk00metadata, sectors[2])
    #     self.assertNotIn(chunk10metadata, sectors[2])
    #     self.assertEqual(len(sectors[3]), 2)
    #     self.assertIn(chunk00metadata, sectors[3])
    #     self.assertIn(chunk10metadata, sectors[3])
    #
    # def testMetaDataLengths(self):
    #     chunk00metadata = self.region.metadata[0,0]
    #     chunk10metadata = self.region.metadata[1,0]
    #     self.assertEqual(chunk00metadata.blocklength, 4)
    #     self.assertEqual(chunk00metadata.length, 10240)
    #     self.assertEqual(chunk10metadata.blocklength, 3)
    #     self.assertEqual(chunk10metadata.length, 613566756)
    #
    # def testMetaDataLengthCalculations(self):
    #     chunk00metadata = self.region.metadata[0,0]
    #     chunk10metadata = self.region.metadata[1,0]
    #     self.assertEqual(chunk00metadata.requiredblocks(), 3)
    #     self.assertEqual(chunk10metadata.requiredblocks(), 149797)
    #
    # def testMetaDataStatus(self):
    #     # performa low-level read, ensure it does not read past the file length
    #     # and does not modify the file
    #     chunk00metadata = self.region.metadata[0,0]
    #     chunk10metadata = self.region.metadata[1,0]
    #     self.assertIn(chunk00metadata.status,
    #                 (RegionFile.STATUS_CHUNK_OVERLAPPING,
    #                  RegionFile.STATUS_CHUNK_OUT_OF_FILE))
    #     self.assertIn(chunk10metadata.status,
    #                 (RegionFile.STATUS_CHUNK_MISMATCHED_LENGTHS,
    #                  RegionFile.STATUS_CHUNK_OVERLAPPING,
    #                  RegionFile.STATUS_CHUNK_OUT_OF_FILE))
    #
    # def testChunkRead(self):
    #     """
    #     Perform a low-level read, ensure it does not read past the file length
    #     and does not modify the file.
    #     """
    #     # Does not raise a ChunkDataError(), since the data can be read,
    #     # even though it is shorter than specified in the header.
    #     data = self.region.get_blockdata(0, 0)
    #     self.assertEqual(len(data), 8187)
    #     data = self.region.get_blockdata(1, 0)
    #     self.assertEqual(len(data), 4091)
    #     self.assertEqual(self.region.get_size(), self.length)
    #
    # def testDeleteChunk(self):
    #     """Try to remove the chunk 1,0 with ridiculous large size.
    #     This should be reasonably fast."""
    #     self.region.unlink_chunk(1, 0)
    #     self.assertEqual(self.region.chunk_count(), 1)



if __name__ == '__main__':
    logger = logging.getLogger("nbt.tests.worldtests")
    if len(logger.handlers) == 0:
        # Logging is not yet configured. Configure it.
        logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='%(levelname)-8s %(message)s')
    unittest.main(verbosity=2)
