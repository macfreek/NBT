#!/usr/bin/env python
"""
Counter the number of biomes in the world. Works only for Anvil-based world folders.
"""
import locale, os, sys
from struct import pack, unpack

# local module
try:
	import nbt
except ImportError:
	# nbt not in search path. Let's see if it can be found in the parent folder
	extrasearchpath = os.path.realpath(os.path.join(sys.path[0],os.pardir))
	if not os.path.exists(os.path.join(extrasearchpath,'nbt')):
		raise
	sys.path.append(extrasearchpath)
from nbt.region import RegionFile
from nbt.chunk import Chunk
from nbt.world import WorldFolder,ANVIL,UnknownWorldFormat

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
	# 255: "Not yet calculated",
}


def print_results(biome_totals):
	locale.setlocale(locale.LC_ALL, 'en_US')
	for id,count in enumerate(biome_totals):
		if id == 255 or (count == 0 and id not in BIOMES):
			continue
		if id in BIOMES:
			biome = BIOMES[id]+" (%d)" % id
		else:
			biome = "Unknown (%d)" % id
		print locale.format_string("%-25s %10d", (biome,count))


def main(world_folder):
	try:
		world = WorldFolder(world_folder, ANVIL)
	except UnknownWorldFormat as msg:
		sys.stderr.write(msg.msg+"\n")
		sys.exit(4)
	biome_totals = [0]*256 # 256 counters for 256 biome IDs
	
	try:
		for chunk in world.iter_nbt():
			for biomeid in chunk["Level"]["Biomes"]:
				biome_totals[biomeid] += 1

	except KeyboardInterrupt:
		print_results(biome_totals)
		return 4 # EINTR
	
	print_results(biome_totals)
	return 0 # NOERR


if __name__ == '__main__':
	if (len(sys.argv) == 1):
		print "No world folder specified!"
		sys.exit(64) # EX_USAGE
	world_folder = sys.argv[1]
	if (not os.path.exists(world_folder)):
		print "No such folder as "+filename
		sys.exit(72) # EX_IOERR
	
	sys.exit(main(world_folder))
