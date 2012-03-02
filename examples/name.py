# Python module
"""
Names for data values in Minecraft.

Example usage:
    name = Block(id, data).name
    name = Entity[id].name
    id = Biome.fromName(name).id
"""
from UserDict import UserDict
import unittest

class DataType(UserDict):
	"""Named Object Type. Abstract class."""
	@staticmethod
	def set_dicts():
		"""Initialize fast lookup dictionaries for id => name and for name => id"""
		for id,d in IDS.items():
			if d['name'] not in NAMES:
				NAMES[d['name']] = id
		

class UnknownDataType(Exception):
	"""Unknown Name"""

class BlockType(object):
	"""Named Block Type. Has the attributes id, data and name.
	Attributes are read-only. Writing will give propagate among all BlockTypes, and may give 
	unexpected results especially for the unknown blocktype."""
	def __init__(self, id=None, data=0, name="Unknown", aliases=(), known=True):
		self.id     = id
		self.data   = data
		self.name   = name
		self.aliases= aliases
		self.known  = known
	def __eq__(self, other):
		return isinstance(other, BlockType) and self.id==other.id and self.data==other.data \
				and self.name==other.name and self.known==other.known
	def clone(self,data=None,known=True):
		"""Clone and set self.known to false"""
		return self.__class__(self.id, self.data if data==None else data, self.name, (), known)
	def __str__(self):
		return self.name
	def __repr__(self):
		return "%s(%s, %s, %r, %s)" % (self.__class__.__name__, self.id, self.data, self.name, self.known)
	

class _BlockFactory(UserDict):
	"""Usage:
	Block = _BlockFactory( <list of all known blocks> )
	Block[id, data]:    returns a BlockType or raises KeyError if unknown
	Block(id, data):    returns a BlockType (may say "Unknown")
	Block[id]:          returns a BlockType or raises KeyError if unknown
	Block(id):          returns a BlockType (may say "Unknown")
	Block.byName(name): returns a BlockType (id may be None if unknown)
	name = Block(id).name
	try:
		id = Block.byName(name).id
	except KeyError:
		pass
	"""
	unknown = BlockType(None, None, "Unknown", known=False)
	def __init__(self, *blocklist):
		self.data  = {} # (id, data) => BlockType
		self.names = {} # name => BlockType
		for block in blocklist:
			key = (block.id, block.data)
			if key not in self.data:    # First match is returned, don't overwrite
				self.data[key] = block
			key = block.name.lower()
			if key not in self.names:
				self.names[key] = block
		for block in blocklist:
			# Re-run a second loop, to ensure that a name always takes precedence over a alias.
			for name in block.aliases:
				key = name.lower()
				if key not in self.names:
					self.names[key] = block
	def __call__(self, id, data=None):
		try:
			return self.data[(id,data)]
		except KeyError:
			pass
		try:
			return self.data[(id,None)].clone(data=data)
		except KeyError:
			pass
		try:
			return self.data[(id,0)].clone(data=data,known=False)
		except KeyError:
			return BlockType(id=id, data=data, known=False)
	def __getitem__(self, key):
		id, data = None, None
		try:
			id = key[0]
			data=key[1]
		except (IndexError, TypeError):
			id = key
		try:
			return self.data[(id,data)]
		except KeyError:
			pass
		try:
			return self.data[(id,None)].clone(data=data)
		except KeyError:
			pass
		try:
			if data==None:
				return self.data[(id,0)]
		except KeyError:
			pass
		raise KeyError((id,data))
	def byName(self, name):
		try:
			return self.names[name.lower()]
		except KeyError:
			return BlockType(id=None, data=None, name=name, known=False)
"""Usage:
Block[id, data]:    returns a BlockType or raises KeyError if unknown
Block(id, data):    returns a BlockType (may say "Unknown")
Block[id]:          returns a BlockType or raises KeyError if unknown
Block(id):          returns a BlockType (may say "Unknown")
Block.byName(name): returns a BlockType (id may be None if unknown)
"""
Block = _BlockFactory(
	BlockType(0,    0,    "Air"),
	BlockType(1,    0,    "Stone"),
	BlockType(2,    0,    "Grass Block", ("Grass", )),
	BlockType(3,    0,    "Dirt"),
	BlockType(4,    0,    "Cobblestone", ("Stonebrick", "Cobble stone", "Stone brick", )),
	BlockType(5,    0,    "Wooden Planks", ("Planks", "Wood", )),
	BlockType(6,    None, "Sapling"),
	BlockType(6,    0,    "Oak Sapling"),
	BlockType(6,    1,    "Spruce Sapling"),
	BlockType(6,    2,    "Birch Sapling"),
	BlockType(6,    3,    "Jungle Oak Sapling"),
	BlockType(17,   0,    "Wood", ("Log", )),
)


ITEMS = {

}

ENTITIES = {

}

BIOMES = {
	0 : "Ocean",
	1 : "Plains",
	2 : "Desert",
	3 : "Mountains",
	4 : "Forest",
	5 : "Taiga",
	6 : "Swamp",
	7 : "River",
	8 : "Nether",
	9 : "Sky",
	10: "Frozen Ocean",
	11: "Frozen River",
	12: "Ice Plains",
	13: "Ice Mountains",
	14: "Mushroom Island",
	15: "Mushroom Shore",
	16: "Beach",
	17: "Desert Hills",
	18: "Forest Hills",
	19: "Taiga Hills",
	20: "Mountains Edge",
	21: "Jungle",
	22: "Jungle Hills",
	255: "Unknown",
}


class blockTests(unittest.TestCase):
	def setUp(self):
		self.Block = _BlockFactory(
			BlockType(0,    0,    "Air"),
			BlockType(1,    0,    "Stone"),
			BlockType(2,    0,    "Grass Block", ("Grass", )),
			BlockType(3,    None, "Dirt"),
			BlockType(4,    0,    "Cobblestone", ("Stonebrick", "Cobble stone", "Stone brick", )),
			BlockType(5,    0,    "Wooden Planks", ("Planks", "Wood", )),
			BlockType(6,    None, "Sapling"),
			BlockType(6,    0,    "Oak Sapling"),
			BlockType(6,    1,    "Spruce Sapling"),
			BlockType(6,    2,    "Birch Sapling"),
			BlockType(17,   0,    "Wood", ("Log", )),
		)
	def testUnknownEqualsUnknown(self):
		self.assertEqual(self.Block.unknown, BlockType(None,None,"Unknown",known=False))
	def testCallWithData(self):
		self.assertEqual(self.Block(2, 0).name, "Grass Block")
	def testCallWithoutData(self):
		self.assertEqual(self.Block(2).name, "Grass Block")
	def testCallUnknownData(self):
		self.assertEqual(self.Block(2, 1).name, "Grass Block") # default to 2,0
		self.assertEqual(self.Block(2, 1).known, False)
	def testCallDefaultData(self):
		self.assertEqual(self.Block(3, 1).name, "Dirt") # default to 3,None
		self.assertEqual(self.Block(3, 1).known, True)
	def testIndexWithData(self):
		self.assertEqual(self.Block[2, 0].name, "Grass Block")
	def testIndexWithoutData(self):
		self.assertEqual(self.Block[2].name, "Grass Block")
	def testIndexUnknownData(self):
		self.assertEqual(self.Block[3, 1].name, "Dirt") # default to 3,None
		self.assertEqual(self.Block[3, 1].known, True)
	def testIndexUnknownDefaultData(self):
		self.assertEqual(self.Block[6, 5].name, "Sapling") # defaults to 6,None
		self.assertEqual(self.Block[6, 5].known, True)
	def testByName(self):
		self.assertEqual(self.Block.byName("Grass Block").id, 2)
	def testAliasByName(self):
		self.assertEqual(self.Block.byName("Grass").known, True)
		self.assertEqual(self.Block.byName("Grass").id, 2)
	def testLowercase(self):
		self.assertEqual(self.Block.byName("grass block").id, 2)
	def testDataByName(self):
		self.assertEqual(self.Block.byName("Spruce Sapling").data, 1)
		self.assertEqual(self.Block.byName("Sapling").data, None)
	def testNameOverridesAlias(self):
		self.assertEqual(self.Block.byName("Wood").id, 17)
	def testDefaultData(self):
		self.assertEqual(self.Block(6).name, "Sapling")
		self.assertEqual(self.Block(6, None).name, "Sapling")
		self.assertEqual(self.Block(6, 0).name, "Oak Sapling")
		self.assertEqual(self.Block(6).data, None)
		self.assertEqual(self.Block(0).data, 0)
	def testCallUnknownId(self):
		self.assertEqual(self.Block(9, 2).name, "Unknown")
		self.assertEqual(self.Block(9, 2).id, 9)
		self.assertEqual(self.Block(9, 2).data, 2)
		self.assertEqual(self.Block(9, 2).known, False)
		self.assertEqual(self.Block(9).data, None)
	def testIndexUnknownId(self):
		self.assertRaises(KeyError, self.Block.__getitem__, (9, 1))
		self.assertRaises(KeyError, self.Block.__getitem__, 9)
		self.assertRaises(KeyError, self.Block.__getitem__, (9,))
		self.assertRaises(KeyError, self.Block.__getitem__, (9,None))
		self.assertRaises(KeyError, self.Block.__getitem__, (2, 1)) # default to 2,0
		try:
			b = self.Block[9, 1]
		except KeyError as key:
			self.assertEqual(key.message,(9,1))
	def testIndexBadSyntax(self):
		self.assertRaises(KeyError, self.Block.__getitem__, ())
	def testUnknownName(self):
		self.assertEqual(self.Block.byName("Paved Lawn").known, False)
		self.assertEqual(self.Block.byName("Paved Lawn").name, "Paved Lawn")
		self.assertEqual(self.Block.byName("Paved Lawn").id, None)
		self.assertEqual(self.Block.byName("Paved Lawn").data, None)


if __name__ == '__main__':
	unittest.main()

