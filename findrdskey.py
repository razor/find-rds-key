#!/usr/bin/which python

import sys
import string

'''
def rshift16(val, n):
	lsb = val & ((1 << n) - 1)
	val = (val >> n) | (lsb << (16 - n))
	return val

def lshift16(val, n):
	msb = val & ~(0xFFFF >> n)
	val = (val << n) | msb
	return val
'''

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

rrange = range(0, 0xF)
srange = range(0, 9)
keyrange = range(0, 0x100)

decloc = []
declocset = []

'''
def findkey(i, encloc, loccur):
	for rbit in rrange:
		for sbit in srange:
			for key in keyrange:
				locdec = RDSDecrypt(encloc[i], rbit, sbit, key)
				if i == 0:
					loccur = locdec
					print i, hex(rbit), hex(sbit), hex(key), hex(loccur)
				if (i+1) < len(encloc):
					ret = findkey(i+1, encloc, loccur)
				if loccur == locdec:
					print 'Found key: ', i, hex(encloc[i]), hex(locdec), hex(rbit), hex(sbit), hex(key)
'''

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
	for i in range(1, len(declocset)-1):
		common = common & declocset[i]
	#print common, len(common)
	return common

def findkeys(decloc, commloc):
	for i in range(0, len(decloc)-1):
		for loc in decloc[i]:
			if commloc == loc[0]:
				print 'Found possible key ID %d: rbit: 0x%x\tsbit: 0x%x\tkey: 0x%x'%(loc[1], loc[2], loc[3], loc[4])


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
		commloc = common.pop()
		print 'Found common location code: 0x%x'%commloc
		findkeys(decloc, commloc)
	else:
		print "Found %d common location codes, not 1. Can't find any keys."%len(common)


