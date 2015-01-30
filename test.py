import sys
import numpy
import os
import cProfile, pstats, StringIO

from functions import *

total = 0

path,multisize = r'',0
macrosize = 3
dimensions = 4
thresholdlower = 0.25
thresholdupper = 1.0
scaling = ''
wmax = 0
hmax = 0
margin = (macrosize-1)/2

beforecount = 0
aftercount = 0

if __name__ == "__main__":
    testarray = numpy.array(range(dimensions**2))
    testarray = numpy.reshape(testarray,(dimensions,dimensions))
    print testarray
    testarray = numpy.pad(testarray,margin+1,mode='constant')
    print testarray
    testarray = numpy.cumsum(numpy.cumsum(testarray,axis=0),axis=1)
    print testarray
