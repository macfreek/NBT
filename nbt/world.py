"""Handle a world folder, containing .mcr or .mca region files"""

import os, glob, re
from . import region
from . import chunk


class Format(object):
	"""world folder"""
	# format constants
	extension = None
	chunkclass = chunk.Chunk

class ALPHA(Format):
	"""Alpha format world folder"""
	pass

class MCREGION(Format):
	"""McRegion world folder"""
	extension = 'mcr'
	chunkclass = chunk.Chunk
	# chunkclass = chunk.McRegionChunk  # TODO: change to McRegionChunk when done

class NEWMCREGION(Format):
	"""McRegion world folder"""
	
	# TODO: test class for easy debugging
	extension = 'mcr'
	chunkclass = chunk.McRegionChunk

class ANVIL(Format):
	"""Anvil world folder"""
	extension = 'mca'
	chunkclass = chunk.AnvilChunk

class UnknownWorldFormat(Exception):
	"""Unknown or invalid world folder"""
	def __init__(self, msg):
		self.msg = msg

class InconceivedChunk(Exception):
	"""Specified does not exist in world file"""

class WorldFolder(object):
	def __init__(self, world_folder, format=None):
		self.worldfolder = world_folder
		self.format = format
		self.regionfiles = {}
		self.regions     = {}
		self.chunks      = None
		# Trigger OSError for non-existant directories or permission errors.
		# This is needed, because glob.glob silently returns no files.
		os.listdir(world_folder)
		filenames = None
		if self.format == None:
			# may raise UnknownWorldFormat
			self.format, filenames = self.guessformat()
		else:
			filenames = self.get_filenames(self.format)
			if len(filenames) == 0:
				raise UnknownWorldFormat("Empty world or not a "+self.format.__doc__)
		for filename in filenames:
			m = re.match(r"r.(\-?\d+).(\-?\d+).mc[ra]", os.path.basename(filename))
			if m:
				x = int(m.group(1))
				z = int(m.group(2))
			else:
				raise UnknownWorldFormat("Unrecognized filename format %s" % os.path.basename(filename))
			self.regionfiles[(x,z)] = filename

	def guessformat(self):
		for format in (ANVIL, MCREGION):
			filenames = self.get_filenames(format)
			if len(filenames) > 0:
				return format, filenames
		raise UnknownWorldFormat("Empty world or not a McRegion or Anvil format")

	def get_filenames(self, format):
		# Warning: glob returns a empty list if the directory is unreadable, without raising an Exception
		return list(glob.glob(os.path.join(self.worldfolder,'region','r.*.*.'+format.extension)))
	
	def get_regionfiles(self):
		"""return a list of full path with region files"""
		return self.regionfiles.values()
	
	def get_region(self, x,z):
		"""Get a region using x,z coordinates of a region. Cache results."""
		if (x,z) not in self.regions:
			if (x,z) in self.regionfiles:
				self.regions[(x,z)] = region.RegionFile(self.regionfiles[(x,z)])
			else:
				# Return an empty RegionFile object
				# TODO: this does not yet allow for saving of the region file
				self.regions[(x,z)] = region.RegionFile()
		return self.regions[(x,z)]
	
	def iter_regions(self):
		for x,z in self.regionfiles.keys():
			yield self.get_region(x,z)

	def iter_nbt(self):
		"""Returns an iterable list of all NBT. Use this function if you only 
		want to loop through the chunks once, and don't need the block or data arrays."""
		# TODO: Implement BoundingBox
		# TODO: Implement sort order
		for region in self.iter_regions():
			for c in region.iter_chunks():
				yield c

	def iter_chunks(self):
		"""Returns an iterable list of all chunks. Use this function if you only 
		want to loop through the chunks once or have a very large world."""
		# TODO: Implement BoundingBox
		# TODO: Implement sort order
		for region in self.iter_regions():
			for c in region.iter_chunks():
				yield self.format.chunkclass(c)

	def get_chunk(self,x,z):
		"""Return a chunk specified by the chunk coordinates x,z."""
		# TODO: Implement (calculate region filename from x,z, see if file exists.)
		rx,x = divmod(x,32)
		rz,z = divmod(z,32)
		nbt = self.get_region(rx,rz).get_chunk(x,z)
		if nbt == None:
			raise InconceivedChunk("Chunk %s,%s not present in world" % (32*rx+x,32*rz+z))
		return self.format.chunkclass(nbt)
	
	def get_chunks(self, boundingbox=None):
		"""Returns a list of all chunks. Use this function if you access the chunk
		list frequently and want to cache the result."""
		if self.chunks == None:
			self.chunks = list(self.iter_chunks())
		return self.chunks
	
	def chunk_count(self):
		c = 0
		for r in self.iter_regions():
			c += r.chunk_count()
		return c 
	
	def get_boundingbox(self):
		"""Return minimum and maximum x and z coordinates of the chunks."""
		b = BoundingBox()
		for rx,rz in self.regionfiles.keys():
			region = self.get_region(rx,rz)
			rx,rz = 32*rx,32*rz
			for cc in region.get_chunk_coords():
				x,z = (rx+cc['x'],rz+cc['z'])
				b.expand(x,None,z)
		return b
	
	def cache_test(self):
		"""Debug routine: loop through all chunks, fetch them again by coordinates, and check if the same object is returned."""
		# TODO: make sure this test succeeds (at least True,True,False, preferable True,True,True)
		# TODO: Move this function to test class.
		for rx,rz in self.regionfiles.keys():
			region = self.get_region(rx,rz)
			rx,rz = 32*rx,32*rz
			for cc in region.get_chunk_coords():
				x,z = (rx+cc['x'],rz+cc['z'])
				c1 = self.format.chunkclass(region.get_chunk(cc['x'],cc['z']))
				c2 = self.get_chunk(x,z)
				correct_coords = (c2.get_coords() == (x,z))
				is_comparable = (c1 == c2) # test __eq__ function
				is_equal = (c1 == c2) # test if id(c1) == id(c2), thus they point to the same memory location
				print x,z,c1,c2,correct_coords,is_comparable,is_equal
	
	def __str__(self):
		return "%s(%s,%s)" % (self.__class__.__name__,self.worldfolder, self.format)


class BoundingBox(object):
	"""A bounding box of x,y,z coordinates"""
	def __init__(self,minx=None, maxx=None, miny=None, maxy=None, minz=None, maxz=None):
		self.minx,self.maxx = minx, maxx
		self.miny,self.maxy = miny, maxy
		self.minz,self.maxz = minz, maxz
	def expand(self,x,y,z):
		if x != None:
			if self.minx is None or x < self.minx:
				self.minx = x
			if self.maxx is None or x > self.maxx:
				self.maxx = x
		if y != None:
			if self.miny is None or y < self.miny:
				self.miny = y
			if self.maxy is None or y > self.maxy:
				self.maxy = y
		if z != None:
			if self.minz is None or z < self.minz:
				self.minz = z
			if self.maxz is None or z > self.maxz:
				self.maxz = z
	def lenx(self):
		return self.maxx-self.minx+1
	def leny(self):
		return self.maxy-self.miny+1
	def lenz(self):
		return self.maxz-self.minz+1
	def __str__(self):
		return "%s(%s,%s,%s,%s,%s,%s)" % (self.__class__.__name__,self.minx,self.maxx,
				self.miny,self.maxy,self.minz,self.maxz)
