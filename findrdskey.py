#!/usr/bin/which python

import sys
import string


MAX_BITS = 16

# Rotate left: 0b1001 --> 0b0011
rol = lambda val, r_bits, max_bits: \
    (val << r_bits%max_bits) & (2**max_bits-1) | \
    ((val & (2**max_bits-1)) >> (max_bits-(r_bits%max_bits)))
 
# Rotate right: 0b1001 --> 0b1100
ror = lambda val, r_bits, max_bits: \
    ((val & (2**max_bits-1)) >> r_bits%max_bits) | \
    (val << (max_bits-(r_bits%max_bits)) & (2**max_bits-1))


def RDSEncrypt(loc, rrbit, sbit, key):
	locrr = ror(loc, rrbit, MAX_BITS)
	xorval = rol(key, sbit, MAX_BITS)
	return locrr ^ xorval

def RDSDecrypt(locbe, rrbit, sbit, key):
	xorval = rol(key, sbit, MAX_BITS)
	locrr = locbe ^ xorval
	loc = rol(locrr, rrbit, MAX_BITS)
	return loc

rrange = range(0, 0x10)
srange = range(0, 0x9)
keyrange = range(0, 0x100)

decloc = []
declocset = []

def decryptloc(i, encloc):
	dec = []
	decset = set()
	for rbit in rrange:
		for sbit in srange:
			for key in keyrange:
				locdec = RDSDecrypt(encloc[1], rbit, sbit, key)
				dec.append((locdec, encloc[0], rbit, sbit, key,))
				decset.add(locdec)
	decloc.append(dec)
	declocset.append(decset)


def findcommon(declocset):
	common = declocset[0]
	for i in range(1, len(declocset)):
		common = common & declocset[i]
	#print common, len(common)
	return common

def findkeys(decloc, commloc):
	for i in range(0, len(decloc)):
		for loc in decloc[i]:
			if commloc == loc[0]:
				print 'Found possible key ID %d: rbit: 0x%x\tsbit: 0x%x\tkey: 0x%x\tlocdec:%x'%(loc[1], loc[2], loc[3], loc[4], loc[0])


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.exit()

	f = open(sys.argv[1], 'r')
	lines = f.readlines()
	lines = map(string.strip, lines)
	encloc = []
	for line in lines:
		s = line.split(',')
		encloc.append((int(s[0], 16), int(s[1], 16)))
	for i in range(0, len(encloc)):
		decryptloc(i, encloc[i])
	common = findcommon(declocset)
	if len(common) == 1:
		while len(common) > 0:
			commloc = common.pop()
			print 'Found common location code: 0x%x'%commloc
			findkeys(decloc, commloc)
	else:
		print "Found %d common location codes, not 1. Can't find any keys."%len(common)


