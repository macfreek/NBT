#!/usr/bin/env python

# Test of nbt speed

import io,os,sys,gzip,time,struct,array

# Search parent directory first, to make sure we test the local nbt module, 
# not an installed nbt module.
extrasearchpath = os.path.realpath(os.path.join(sys.path[0],os.pardir))
sys.path.insert(1, extrasearchpath) # insert ../ just after ./



def chunkinit(blockBytes):
    return list(unpack("32768B", blocksBytes))

f = gzip.GzipFile('mcregion.nbt')
# f = open('anvil.nbt')
data = f.read()
f.close

import nbt_old as nbt

def speedtest_TAG_Byte_Array_list(data, repeat=1000):
	start = time.time()
	for i in xrange(repeat):
		mynbt = nbt.NBTFile(buffer=io.BytesIO(data)) # parsing takes 2.7 ms
		blocksBytes = mynbt['Level']['Blocks'].value
		blockdata = list(struct.unpack("32768B", blocksBytes)) # converting takes 0.5 ms
		assert len(blockdata) == 32768
	return (time.time() - start)/repeat

def speedtest_TAG_Byte_Array_bytes(data, repeat=1000):
	start = time.time()
	for i in xrange(repeat):
		mynbt = nbt.NBTFile(buffer=io.BytesIO(data)) # parsing takes 2.7 ms
		blocksBytes = mynbt['Level']['Blocks'].value
		blockdata = bytes(blocksBytes) # converting takes 0.5 ms
		assert len(blockdata) == 32768
	return (time.time() - start)/repeat

def speedtest_TAG_Byte_Array_bytearray(data, repeat=1000):
	start = time.time()
	for i in xrange(repeat):
		mynbt = nbt.NBTFile(buffer=io.BytesIO(data))  # parsing takes 3.1 ms
		blocksBytes = mynbt['Level']['Blocks'].value
		blockdata = bytearray(blocksBytes) # converting takes 0.5 ms
		assert len(blockdata) == 32768
	return (time.time() - start)/repeat

def speedtest_TAG_Byte_Array_array(data, repeat=1000):
	start = time.time()
	for i in xrange(repeat):
		mynbt = nbt.NBTFile(buffer=io.BytesIO(data))  # parsing takes 3.1 ms
		blocksBytes = mynbt['Level']['Blocks'].value
		blockdata = array.array('B', blocksBytes)
		assert len(blockdata) == 32768
	return (time.time() - start)/repeat

def speedtest_tuple_to_list(data, repeat=1000):
	mynbt = nbt.NBTFile(buffer=io.BytesIO(data))
	blocksBytes = mynbt['Level']['Blocks'].value
	blocksBytes = struct.unpack("32768B", blocksBytes)
	start = time.time()
	for i in xrange(repeat):
		blockdata = list(blocksBytes) # converting takes 0.5 ms
	return (time.time() - start)/repeat

def speedtest_unpack(data, repeat=1000):
	mynbt = nbt.NBTFile(buffer=io.BytesIO(data))
	blocksBytes = mynbt['Level']['Blocks'].value
	blockdata = struct.unpack("32768B", blocksBytes)
	start = time.time()
	for i in xrange(repeat):
		blockdata = struct.unpack("32768B", blocksBytes) # converting takes 0.5 ms
	return (time.time() - start)/repeat

def speedtest_list(data, repeat=1000):
	mynbt = nbt.NBTFile(buffer=io.BytesIO(data))
	blocksBytes = mynbt['Level']['Blocks'].value
	start = time.time()
	for i in xrange(repeat):
		blockdata = [i for i in blocksBytes]
	return (time.time() - start)/repeat

def speedtest_bytes(data, repeat=1000):
	mynbt = nbt.NBTFile(buffer=io.BytesIO(data))
	blocksBytes = mynbt['Level']['Blocks'].value
	start = time.time()
	for i in xrange(repeat):
		blockdata = bytes(blocksBytes) # converting takes 0.5 ms
	return (time.time() - start)/repeat

def speedtest_bytearray(data, repeat=1000):
	mynbt = nbt.NBTFile(buffer=io.BytesIO(data))
	blocksBytes = mynbt['Level']['Blocks'].value
	start = time.time()
	for i in xrange(repeat):
		blockdata = bytearray(blocksBytes) # converting takes 0.5 ms
	return (time.time() - start)/repeat

def speedtest_array(data, repeat=1000):
	mynbt = nbt.NBTFile(buffer=io.BytesIO(data))
	blocksBytes = mynbt['Level']['Blocks'].value
	start = time.time()
	for i in xrange(repeat):
		blockdata = array.array('B', blocksBytes)
	return (time.time() - start)/repeat

def speedtest_nbtparse(data, repeat=1000):
	start = time.time()
	for i in xrange(repeat):
		mynbt = nbt.NBTFile(buffer=io.BytesIO(data))  # parsing takes 3.1 ms
	return (time.time() - start)/repeat

def speedtest_pointer(data, repeat=1000):
	mynbt = nbt.NBTFile(buffer=io.BytesIO(data))  # parsing takes 3.1 ms
	start = time.time()
	for i in xrange(repeat):
		blocksBytes = mynbt['Level']['Blocks'].value
	return (time.time() - start)/repeat



repeat = 1000
for test in (
			# speedtest_TAG_Byte_Array_list, speedtest_TAG_Byte_Array_bytes, \
			# speedtest_TAG_Byte_Array_bytearray, speedtest_TAG_Byte_Array_array, \
			speedtest_tuple_to_list, speedtest_unpack, speedtest_list, \
			speedtest_bytes, speedtest_bytearray, speedtest_array, \
			speedtest_nbtparse, speedtest_pointer, \
			):
	duration = test(data, repeat)
	print("%-36s %8.5f ms" % (test.__name__, 1000*duration))


