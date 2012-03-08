#!/usr/bin/env python3.2
import os,sys,re,struct,gzip
import nbt
wf= '/Users/freek/Library/Application Support/minecraft/saves/MountainWorld'
wm = nbt.world.WorldFolder(wf, nbt.world.NEWMCREGION)
wa = nbt.world.WorldFolder(wf, nbt.world.ANVIL)
cm = wm.get_chunk(17,-40)
ca = wa.get_chunk(17,-40)
mcr = cm.nbt['Level']
anv = ca.nbt['Level']

# print (cm.nbt.pretty_tree())
print (ca.nbt.pretty_tree())
# print(wa.get_chunk(13,-21).nbt['Level']['Biomes'])
# print(wa.get_chunk(13,-21).nbt['Level']['HeightMap'])
# print(type(wa.get_chunk(13,-21).nbt['Level']['Biomes'][3]))
# print(wa.get_chunk(13,-21).nbt['Level']['Biomes'][3])
# print(wa.get_chunk(13,-21).nbt['Level']['Biomes'][0:-1:16])
# print(wa.get_chunk(13,-21).nbt['Level']['Biomes'][0:16])
# nt = nbt.nbt.NBTFile('bigtest.nbt')
# print (nt.pretty_tree())

h = cm.nbt['Level']['HeightMap']
print(h)
h[4] = 66
print(h)

# Tag_... is not subscriptable
# bt = gzip.GzipFile("bigtest.nbt")
# bt.read(1)
