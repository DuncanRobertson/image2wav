#!/usr/bin/python
#
#  image2wav.py
#
#  duncan@linuxbandwagon.com
#
version = '0.2'  
#  image2wav.py
#
#
#  developed on Redhat Linux 7.3 using python v 1.5.2
#
# 0.2 17/10/2004
#  fixed so works on current python, PIL and linux env (2.3.4, debian sarge)
#
#  requires the Python Imageing Library to be installed.
#
#  simple program to take an image file and create
#  a wav file that will display the image (or an
#  approximation) when played through a spectrum analyser.
#
#  creates mono 44100 16 bit samples
#
#  TODO: selectable output sample length
#        more error checking
#        map colour images to stereo WAV files
#
# Despite the triviality of this program, it is copyright the author
# under the terms of the Gnu Public License. See
# http://www.gnu.org/licenses/gpl
# 

import Image, wave, array, sys, struct

#############################################################################
#
#  FFT code from http://www.python.org/topics/scicomp/recipes_in_python.html
#
"""
Find 2^n that is equal to or greater than.
"""
def nextpow2(i):
    n = 2
    while n < i: n = n * 2
    return n

"""
Return bit-reversed list, whose length is assumed to be 2^n:
eg. 0111 <--> 1110 for N=2^4.
"""
def bitrev(x):
    N, x = len(x), x[:]
    if N != nextpow2(N): raise ValueError, 'N is not power of 2'
    for i in range(N):
    	k, b, a = 0, N>>1, 1
    	while b >= a:
    	    if b & i: k = k | a
	    if a & i: k = k | b
	    b, a = b>>1, a<<1
	if i < k:		# important not to swap back
	    x[i], x[k] = x[k], x[i]
    return x


"""
FFT using Cooley-Tukey algorithm where N = 2^n.  The choice of
e^{-j2\pi/N} or e^{j2\pi/N} is made by 'sign=-1' or 'sign=1'
respectively.  Since I prefer Engineering convention, I chose
'sign=-1' as the default.

FFT is performed as follows:
1. bit-reverse the array.
2. partition the data into group of m = 2, 4, 8, ..., N data points.
3. for each group with m data points,
    1. divide into upper half (section A) and lower half (section B),
	each containing m/2 data points.
    2. divide unit circle by m.
    3. apply "butterfly" operation 
	    |a| = |1  w||a|	or	a, b = a+w*b, a-w*b
	    |b|   |1 -w||b|
	where a and b are data points of section A and B starting from
	the top of each section, and w is data points along the unit
	circle starting from z = 1+0j.
FFT ends after applying "butterfly" operation on the entire data array
as whole, when m = N.
"""
def fft(x, sign=-1):
    from cmath import pi, exp
    N, W = len(x), []
    for i in range(N):		# exp(-j...) is default
	W.append(exp(sign * 2j * pi * i / N))
    x = bitrev(x)
    m = 2
    while m <= N:
	for s in range(0, N, m):
	    for i in range(m/2):
		n = i * N / m
	    	a, b = s + i, s + i + m/2
	        x[a], x[b] = x[a] + W[n % N] * x[b], x[a] - W[n % N] * x[b]
        m = m * 2
    return x


"""
Inverse FFT with normalization by N, so that x == ifft(fft(x)) within
round-off errors.
"""
def ifft(X):
    N, x = len(X), fft(X, sign=1)	# e^{j2\pi/N}
    for i in range(N):
	x[i] = x[i] / float(N)
    return x

#######################################################################
#
#
#  step 1 - open the image file
#

# some options - mebbe make them command line switchable
# if there is a need.
preserve_aspect = 1
fft_window = 1024

filename = sys.argv[1]

im = Image.open(filename)

print 'Image format and dimensions:'
print im.format, im.size, im.mode

#
#  step 2 - get the data as an array that we can feed to
#           the fft
# (resize to 1024 wide, for 1024 window thang...)

# convert to grayscale
mim = im.convert('L')

# resize so width is 1/2 of fft window (we pad out the other half with 0s)
if preserve_aspect == 1:
   ratio = (fft_window / 2.0) / mim.size[0]
   mim = mim.resize((fft_window / 2,int(mim.size[1] * ratio)))
else:
   mim = mim.resize((fft_window / 2,mim.size[1]))

pad = [0] * (fft_window / 2)

#
#  step 3 IFFT it
#
results = []

print 'transforming.....'
for i in range(mim.size[1]):
   print i,' of ',mim.size[1]
   slice = []
   for j in range(mim.size[0]):
      # print (j,i)
      slice.append(mim.getpixel((j,i)))

   result = ifft(slice + pad)
   results.append(result)


samplelength = len(results[0]) * len(results)
print 'sample length in seconds: ',samplelength / 44100.0

#
#  step 4 - save the resultant wav
#

wfile = wave.open(filename+'.wav','w')
wfile.setparams((1,2,44100,samplelength,'NONE',''))

max = 0.0 
min = 0.0
print 'finding max amplitude'
for slice in results:
   for i in slice:
      if abs(i.real) > max:
         max = abs(i.real)

print 'max amplitude is ',max

bigint = 2**14
written = 0
print 'writing....'
for slice in results:
   print 'written ',written,' of ',samplelength
   buff = ''
   for i in slice:
      val = i.real
      buff = buff + struct.pack('h',int(val * bigint / max))
   wfile.writeframes(buff)
   written = written + (len(buff) / 2)

wfile.close()
