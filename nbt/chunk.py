""" Handle a single chunk of data (16x16x128 blocks) """
from io import BytesIO
from struct import pack, unpack
import array, math

class Chunk(object):
	"""Chunk class, representing a McRegion Chunk."""
	def __init__(self, nbt):
		chunk_data = nbt['Level']
		self.coords = chunk_data['xPos'],chunk_data['zPos']
		self.blocks = BlockArray(chunk_data['Blocks'].value, chunk_data['Data'].value)
		# raise NotImplemented("Use McRegionChunk() or AnvilChunk()")

	def get_coords(self):
		return (self.coords[0].value,self.coords[1].value)

	def __repr__(self):
		return self.__class__.__name__+"("+str(self.coords[0])+","+str(self.coords[1])+")"

""" Convenience class for dealing with a Block/data byte array """
class BlockArray(object):
	def __init__(self, blocksBytes=None, dataBytes=None):
		if (blocksBytes != None):
			if isinstance(blocksBytes, (bytearray, array.array)):
				self.blocksList = list(blocksBytes)
			else: # blockList is a string
				self.blocksList = list(unpack("32768B", blocksBytes)) # A list of bytes
		else:
			self.blocksList = [0]*32768 # Create an empty block list (32768 entries of zero (air))
		
		if (dataBytes != None):
			if isinstance(dataBytes, (bytearray, array.array)):
				self.dataList = list(dataBytes)
			else: # dataBytes is a string
				self.dataList = list(unpack("16384B", dataBytes))
		else:
			self.dataList = [0]*16384 # Create an empty data list (32768 4-bit entries of zero make 16384 byte entries)

	# Get all block entries
	def get_all_blocks(self):
		return self.blocksList
	
	# Get all data entries
	def get_all_data(self):
		bits = []
		for b in self.dataList:
			# The first byte of the Blocks arrays correspond 
			# to the LEAST significant bits of the first byte of the Data. 
			# NOT to the MOST significant bits, as you might expected.
			bits.append(b & 15) # Little end of the byte
			bits.append((b >> 4) & 15) # Big end of the byte
		return bits

	# Get all block entries and data entries as tuples
	def get_all_blocks_and_data(self):
		return zip(self.get_all_blocks(), self.get_all_data())

	def get_blocks_struct(self):
		cur_x = 0
		cur_y = 0
		cur_z = 0
		blocks = {}
		for block_id in self.blocksList:
			blocks[(cur_x,cur_y,cur_z)] = block_id
			cur_y += 1
			if (cur_y > 127):
				cur_y = 0
				cur_z += 1
				if (cur_z > 15):
					cur_z = 0
					cur_x += 1
		return blocks

	# Give blockList back as a byte array
	def get_blocks_byte_array(self, buffer=False):
		if buffer:
			length = len(self.blocksList)
			return BytesIO(pack(">i", length)+self.get_blocks_byte_array())
		else:
			return array.array('B', self.blocksList).tostring()

	def get_data_byte_array(self, buffer=False):
		if buffer:
			length = len(self.dataList)
			return BytesIO(pack(">i", length)+self.get_data_byte_array())
		else:
			return array.array('B', self.dataList).tostring()

	def generate_heightmap(self, buffer=False, as_array=False):
		"""Returns a byte array containing the highest non-air block."""
		# TODO: this implementation set the highest non-air block.
		# In Minecraft, the nbt['Level']['HeightMap'] contain the highest solid block.
		if buffer:
			return BytesIO(pack(">i", 256)+self.generate_heightmap()) # Length + Heightmap, ready for insertion into Chunk NBT
		else:
			bytes = []
			for z in range(16):
				for x in range(16):
					for y in range(127, -1, -1):
						offset = y + z*128 + x*128*16
						if (self.blocksList[offset] != 0 or y == 0):
							bytes.append(y+1)
							break
			if (as_array):
				return bytes
			else:
				return array.array('B', bytes).tostring()

	def set_blocks(self, list=None, dict=None, fill_air=False):
		if list:
			# Inputting a list like self.blocksList
			self.blocksList = list
		elif dict:
			# Inputting a dictionary like result of self.get_blocks_struct()
			list = []
			for x in range(16):
				for z in range(16):
					for y in range(128):
						coord = x,y,z
						offset = y + z*128 + x*128*16
						if (coord in dict):
							list.append(dict[coord])
						else:
							if (self.blocksList[offset] and not fill_air):
								list.append(self.blocksList[offset])
							else:
								list.append(0) # Air
			self.blocksList = list
		else:
			# None of the above...
			return False
		return True

	def set_block(self, x,y,z, id, data=0):
		offset = y + z*128 + x*128*16
		self.blocksList[offset] = id
		if (offset % 2 == 1):
			# offset is odd
			index = (offset-1)/2
			b = self.dataList[index]
			self.dataList[index] = (b & 240) + (data & 15) # modify lower bits, leaving higher bits in place
		else:
			# offset is even
			index = offset/2
			b = self.dataList[index]
			self.dataList[index] = (b & 15) + (data << 4 & 240) # modify ligher bits, leaving lower bits in place

	# Get a given X,Y,Z or a tuple of three coordinates
	def get_block(self, x,y,z, coord=False):
		"""
		Laid out like:
		(0,0,0), (0,1,0), (0,2,0) ... (0,127,0), (0,0,1), (0,1,1), (0,2,1) ... (0,127,1), (0,0,2) ... (0,127,15), (1,0,0), (1,1,0) ... (15,127,15)
		
		blocks = []
		for x in xrange(15):
		  for z in xrange(15):
		    for y in xrange(127):
		      blocks.append(Block(x,y,z))
		"""
		
		offset = y + z*128 + x*128*16 if (coord == False) else coord[1] + coord[2]*128 + coord[0]*128*16
		return self.blocksList[offset]

	# Get a given X,Y,Z or a tuple of three coordinates
	def get_data(self, x,y,z, coord=False):
		offset = y + z*128 + x*128*16 if (coord == False) else coord[1] + coord[2]*128 + coord[0]*128*16
		# The first byte of the Blocks arrays correspond 
		# to the LEAST significant bits of the first byte of the Data. 
		# NOT to the MOST significant bits, as you might expected.
		if (offset % 2 == 1):
			# offset is odd
			index = (offset-1)/2
			b = self.dataList[index]
			return b & 15 # Get little (last 4 bits) end of byte
		else:
			# offset is even
			index = offset/2
			b = self.dataList[index]
			return (b >> 4) & 15 # Get big end (first 4 bits) of byte

	def get_block_and_data(self, x,y,z, coord=False):
		return (self.get_block(x,y,z,coord),self.get_data(x,y,z,coord))



class BaseChunk(object):
	"""Abstract Chunk class."""
	def __init__(self, nbt):
		self.nbt = nbt
		self.level = nbt['Level']
		
		# self.blockdata is a flat arrays of (block id, data) tuples in native order
		# In McRegion the length is 32768 and order is XZY, thus index = (x*16)+z)*16+y
		# In Anvil the length is n*4096 and order is YZZ, thus index = (y*16)+z)*16+x,
		#   with n = 0...16 (thus lenght 0...65536)
		# blockdata[i] = (256*addblocks[i] + blocks[i], data[i])
		self.blockdata = []
		
		# ordered list of integers defining the y (section height) of a defined section
		self.section_y = []
		
		# It's number crunching time.
		self.parse_blocks() # set self.blockdata

	def get_coords(self):
		"""Return the x,z coordinates of the chunk. Multiply by 16 to get the global block coordinates."""
		return (self.level['xPos'].value, self.level['xPos'].value)

	def update_heightmap(self):
		"""Set nbt['Level']['HeightMap'] bases on self.blockdata"""
		# self.level["HeightMap"] is a flat array of integers (0-127) in native ZX order, 
		# Note that the heightmap contains the topmost SOLID block. Grass, etc. is ignored.
		# Not implemented
		pass

	def generate_heightmap(self, buffer=False, as_array=False):
		"""Returns a byte array containing the highest non-air block."""
		if self._nbtisdirty:
			self.update_nbt()
		return self.level["HeightMap"]

	def update_lightlevels(self):
		"""Set nbt['Level']['SkyLight'] and nbt['Level']['BlockLight'] bases on self.blockdata"""
		"""Set self.sections[i]['SkyLight'] and self.sections[i]['BlockLight'] bases on self.blockdata"""
		# Not implemented
		pass

	#
	# NBT functions
	#

	def parse_blocks(self):
		"""Read NBT and fill self.blocksList and self.dataList"""
		# TODO: to be written
		self._nbtisdirty = False
	
	def update_block_nbt(self):
		""""""

	def update_nbt(self):
		"""Update self.nbt based on self.blockdata and self.heightmap"""
		self.update_heightmap()
		self.update_lightlevels()
		self.update_block_nbt()
		self._nbtisdirty = False

	def get_nbt(self):
		"""Update the nbt and return it"""
		if self._nbtisdirty:
			self.update_nbt()
		return self.nbt

	#
	# Block retrieval functions
	#

	def get_block_id(self, x, y, z):
		"""Return the block id of the block at the x,y,z coordinates relative to this chunk"""
	
	def get_data(self, x, y, z):
		"""Return the data id of the block at the x,y,z coordinates relative to this chunk"""
	
	def get_block_and_data(self, x, y, z):
		"""Return a tuple block id, data of the block at the x,y,z coordinates relative to this chunk"""
	
	def get_all_blocks(self):
		"""Iterate over all block ids"""
	
	def get_all_blocks_and_data(self):
		"""Iterate over (block id, data) tuples, including undefined (air) blocks"""
	
	def get_defined_block_ids(self):
		"""Iterate over all defined block ids, possibly excluding some air blocks"""
	
	def get_defined_blocks_and_data(self):
		"""Iterate over all defined (block id, data) tuples, possibly excluding some air blocks"""
	
	#
	# Structured block functions and block setting functions
	#
	
	def get_defined_blocks_struct(self):
		"""Return a dict with defined (x,y,z): (block id, data) tuples, undefined air blocks may be excluded."""


	def set_block(self, x,y,z, id, data=0):
		"""Set the block to specified id and data value."""


	def set_all_blocks_and_data(self, list):
		"""Replace all blocks with the given (block id, data) tuples. All blocks should be specified in a flat list of 32768 entries in native XZY order.
		WARNING: this function behaves slightly different for McRegion and Anvil"""
		"""Replace all blocks with the given (block id, data) tuples. All blocks should be specified in a flat list of a multiple of 4096 entries in native YZX order. If the list is smaller than 65536, the remaining blocks are zeroed (set to air)
		WARNING: this function behaves slightly different for McRegion and Anvil"""

	def set_blocks(self, dict=None, fill_air=False):
		"""Replace blocks with specificied (x,y,z) coordinates. Each item is a (block id,data) tuple
		WARNING: the syntax of this function has changed; for lists, use set_all_blocks_and_data().
		It also now requires a (block id, data) tuple"""

	#
	# Deprecated functions
	#

	def get_all_data(self):
		raise NotImplementedError()

	def get_blocks_byte_array(self, buffer=False):
		"""Give blockList back as a byte array"""
		raise NotImplementedError("Use get_all_blocks instease of get_blocks_byte_array")

	def get_data_byte_array(self, buffer=False):
		raise NotImplementedError()
	
	#
	# Biome functions
	#
	
	def get_biome(self, x, z):
		"""Return the biome IDs at the specified x,z coordinated (relative to this chunk). An ID of 255 means "Undetermined"."""
	
	def get_biomes(self):
		"""Return a list of biome IDs. The list if a flat array of integers in ZX order. An ID of 255 means "Undetermined"."""
		# self.biomes is a flat array of integers (0-255) in ZX order. (i = (z * 16 + x))
		# Since biome IDs are not stored in McRegion format, it always set to 255 ("undetermined")
		return 256*[255]
	
	#
	# Section functions.  These methods are only available for Anvil.
	#
	
	def get_section_blocks_and_data(self, height):
		"""Return a list of 4096 (block id, data) tuples in YZX order, for the given section height. The section height is 1/16 of the block height."""
	
	def iter_defined_sections(self):
		"""Iterate over each defined section: a list of 4096 (block id, data) tuples in YZX order. This is a reasonably fast routine. For even greater speed, don't use a Chunk class and iterate the NBT yourself."""

	def iter_overworld_y_sections(self):
		"""Iterate over all sections between . This is a particular fast routine for printing maps of the overworld."""
	
	def get_max_section_height(self):
		"""Return the height of the highest defined section. Multiple by 16 and add 15 to get the height of the highest defined block. This method is only available for Anvil."""
	
	#
	# Height map routines
	#

	def get_min_floor_height(self):
		"""Return the lowest Y (height) where sun can reach in this chunk."""

	def get_max_floor_height(self):
		"""Return the highest Y (height) + 1 where sun can't reach in this chunk."""

	def get_min_defined_block_height(self):
		"""Return the lowest Y (height) where a block is defined. Should be 0, really."""

	def get_max_defined_block_height(self):
		"""Return the highest non-air block. This is a slow routine. For a fast alternative, use get_max_floor_height() 
		for the lower boundary and 16*get_max_section_height()+15 for the upper boundary()."""




class McRegionChunk(BaseChunk):
	"""Representation of a Chunk in McRegion format."""
	def __init__(self, nbt):
		self.nbt = nbt
		self.level = nbt['Level']
		
		# self.blockdata is a flat array of integers in native XZY order, 
		# each an integer with combined Blocks and Data values:
		# blockdata[i] = blocks[i] << 4 + data[i]   with   i = (x*16)+z)*16+y
		self.blockdata = []
		
		# self.level["HeightMap"] is a flat array of integers (0-127) in native ZX order, 
		# Note that the heightmap contains the topmost SOLID block. Grass, etc. is ignored.
		
		# self.biomes is a flat array of integers (0-255) in ZX order. (i = (z * 16 + x))
		# Since biome IDs are not stored in McRegion format, it always set to 255 ("undetermined")
		self.biomes    = 256*[255]
		
		# self.blocks is deprecated: it used to refer to a BlockArray instance. 
		# It's functionality (and all it's variables are now present in McRegionChunk)
		self.blocks    = self  # for backward compatibility
		
		# It's number crunching time.
		self.parse_blocks() # set self.blockdata

	def parse_blocks(self):
		"""Read NBT and fill self.blockdata and self.heightmap"""
		# TODO: to be written
		self._nbtisdirty = False

	def update_nbt(self):
		"""Update self.nbt based on self.blockdata and self.heightmap"""
		# TODO: to be written
		self._nbtisdirty = False

	def get_nbt(self):
		"""Update the nbt['Level']"""
		if self._nbtisdirty:
			self.update_nbt()
		return self.nbt


		
		# TODO: this implementation set the highest non-air block.
		# In Minecraft, the nbt['Level']['HeightMap'] contain the highest solid block.
		if buffer:
			return BytesIO(pack(">i", 256)+self.generate_heightmap()) # Length + Heightmap, ready for insertion into Chunk NBT
		else:
			bytes = []
			for z in range(16):
				for x in range(16):
					for y in range(127, -1, -1):
						offset = y + z*128 + x*128*16
						if (self.blocksList[offset] != 0 or y == 0):
							bytes.append(y+1)
							break
			if (as_array):
				return bytes
			else:
				return array.array('B', bytes).tostring()


	# Get all block entries
	def get_all_blocks(self):
		return self.blocksList
	
	# Get all data entries
	def get_all_data(self):
		bits = []
		for b in self.dataList:
			# The first byte of the Blocks arrays correspond 
			# to the LEAST significant bits of the first byte of the Data. 
			# NOT to the MOST significant bits, as you might expected.
			bits.append(b & 15) # Little end of the byte
			bits.append((b >> 4) & 15) # Big end of the byte
		return bits

	# Get all block entries and data entries as tuples
	def get_all_blocks_and_data(self):
		return zip(self.get_all_blocks(), self.get_all_data())

	def get_blocks_struct(self):
		cur_x = 0
		cur_y = 0
		cur_z = 0
		blocks = {}
		for block_id in self.blocksList:
			blocks[(cur_x,cur_y,cur_z)] = block_id
			cur_y += 1
			if (cur_y > 127):
				cur_y = 0
				cur_z += 1
				if (cur_z > 15):
					cur_z = 0
					cur_x += 1
		return blocks

	# Give blockList back as a byte array
	def get_blocks_byte_array(self, buffer=False):
		if buffer:
			length = len(self.blocksList)
			return BytesIO(pack(">i", length)+self.get_blocks_byte_array())
		else:
			return array.array('B', self.blocksList).tostring()

	def get_data_byte_array(self, buffer=False):
		if buffer:
			length = len(self.dataList)
			return BytesIO(pack(">i", length)+self.get_data_byte_array())
		else:
			return array.array('B', self.dataList).tostring()

	def generate_heightmap(self, buffer=False, as_array=False):
		"""Returns a byte array containing the highest non-air block."""
		if self._nbtisdirty:
			self.update_nbt()
		return self.level["HeightMap"]

	def set_blocks(self, list=None, dict=None, fill_air=False):
		if list:
			# Inputting a list like self.blocksList
			self.blocksList = list
		elif dict:
			# Inputting a dictionary like result of self.get_blocks_struct()
			list = []
			for x in range(16):
				for z in range(16):
					for y in range(128):
						coord = x,y,z
						offset = y + z*128 + x*128*16
						if (coord in dict):
							list.append(dict[coord])
						else:
							if (self.blocksList[offset] and not fill_air):
								list.append(self.blocksList[offset])
							else:
								list.append(0) # Air
			self.blocksList = list
		else:
			# None of the above...
			return False
		return True

	def set_block(self, x,y,z, id, data=0):
		offset = y + z*128 + x*128*16
		self.blocksList[offset] = id
		if (offset % 2 == 1):
			# offset is odd
			index = (offset-1)/2
			b = self.dataList[index]
			self.dataList[index] = (b & 240) + (data & 15) # modify lower bits, leaving higher bits in place
		else:
			# offset is even
			index = offset/2
			b = self.dataList[index]
			self.dataList[index] = (b & 15) + (data << 4 & 240) # modify ligher bits, leaving lower bits in place

	# Get a given X,Y,Z or a tuple of three coordinates
	def get_block(self, x,y,z, coord=False):
		"""
		Laid out like:
		(0,0,0), (0,1,0), (0,2,0) ... (0,127,0), (0,0,1), (0,1,1), (0,2,1) ... (0,127,1), (0,0,2) ... (0,127,15), (1,0,0), (1,1,0) ... (15,127,15)
		
		blocks = []
		for x in xrange(15):
		  for z in xrange(15):
		    for y in xrange(127):
		      blocks.append(Block(x,y,z))
		"""
		
		offset = y + z*128 + x*128*16 if (coord == False) else coord[1] + coord[2]*128 + coord[0]*128*16
		return self.blocksList[offset]

	# Get a given X,Y,Z or a tuple of three coordinates
	def get_data(self, x,y,z, coord=False):
		offset = y + z*128 + x*128*16 if (coord == False) else coord[1] + coord[2]*128 + coord[0]*128*16
		# The first byte of the Blocks arrays correspond 
		# to the LEAST significant bits of the first byte of the Data. 
		# NOT to the MOST significant bits, as you might expected.
		if (offset % 2 == 1):
			# offset is odd
			index = (offset-1)/2
			b = self.dataList[index]
			return b & 15 # Get little (last 4 bits) end of byte
		else:
			# offset is even
			index = offset/2
			b = self.dataList[index]
			return (b >> 4) & 15 # Get big end (first 4 bits) of byte

	def get_block_and_data(self, x,y,z, coord=False):
		return (self.get_block(x,y,z,coord),self.get_data(x,y,z,coord))


class AnvilChunk(BaseChunk):
	def __init__(self, nbt):
		self.nbt = nbt
		self.level = nbt['Level']  # stored for efficiency
		
		
		self.coords = self.level['xPos'],self.level['zPos']
		
		# self.blockdata is a flat array of integers in native YZX order, 
		# each an integer with combined AddBlocks, Blocks and Data values:
		# blockdata[i] = addblocks[i] << 8 + blocks[i] << 4 + data[i] 
		# with   i = (y*16)+z)*16+x
		self.blockdata = []
		
		# heightmap is a flat array of integers (0-255) in native ZX order, 
		# Note that the heightmap contains the topmost SOLID block. Grass, etc. is ignored.
		self.heightmap = []
		# self.biomes is a flat array of integers (0-255) in native ZX order. (i = (z * 16 + x))
		self.biomes    = []
		# self.blocks is deprecated: it used to refer to a BlockArray instance. 
		# It's functionality (and all it's variables are now present in McRegionChunk)
		self.blocks = self  # for backward compatibility
		# self.sections contains a pointer
		self.sections  = {}
		# It's number crunching time.
		self.parse_blocks() # set self.blockdata
	def parse_blocks(self):
		"""Read NBT and fill self.blockdata and self.heightmap"""
		# TODO: to be written
		self._nbtisdirty = False
	def update_heightmap(self):
		# Not implemented
		pass
	def update_lightlevels(self):
		# Not implemented
		pass
	def update_nbt(self):
		"""Update self.nbt based on self.blockdata and self.heightmap"""
		# TODO: to be written
		self.update_heightmap()
		self.update_lightlevels()
		self._nbtisdirty = False
	def get_nbt(self):
		"""Update the nbt['Level']"""
		if self._nbtisdirty:
			self.update_nbt()
		return self.nbt

