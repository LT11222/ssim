#!python

import numpy
cimport numpy
cimport cython
from libc.stdlib cimport malloc, free, calloc

def ssim(numpy.ndarray[int, ndim=2, mode="c"] arr1in, numpy.ndarray[int, ndim=2, mode="c"] arr2in, int iidim, int macrosize):

	cdef double c1 = 6.5025
	cdef double c2 = 58.5225
	
	cdef int i = 0
	cdef int j = 0
	
	cdef int fulldim = arr1in.shape[0]

	cdef int* fullimg = <int*>calloc(fulldim*fulldim*5,sizeof(int))
	#cdef int* fullimg = <int*>malloc(fulldim*fulldim*5*sizeof(int))
	
	cdef int* fullimgptr = &fullimg[0]+fulldim*5+5
	cdef int* fullimgptrrow = &fullimg[0]+fulldim*5
	cdef int* fullimgptrcol = &fullimg[0]+5
	cdef int* fullimgptrneg = &fullimg[0]
	
	cdef int* arr1ptr = &arr1in[0,0]+1+fulldim
	cdef int* arr2ptr = &arr2in[0,0]+1+fulldim
	
	cdef int arr1val
	cdef int arr2val
	
	cdef int* fullimgptr_d = &fullimg[0]+(macrosize)*fulldim*5+(macrosize)*5
	cdef int* fullimgptr_a = &fullimg[0]
	cdef int* fullimgptr_c = &fullimg[0]+(macrosize)*fulldim*5
	cdef int* fullimgptr_b = &fullimg[0]+(macrosize)*5
	
	cdef double mu1sqval = 0.0
	cdef double mu2sqval = 0.0
	cdef double mu12val = 0.0
	
	cdef double mu1temp = 0.0
	cdef double mu2temp = 0.0
	cdef double sigma1temp = 0.0
	cdef double sigma2temp = 0.0
	cdef double sigma12temp = 0.0
	
	cdef double num = 0.0
	cdef double denom = 0.0
	cdef double res = 0.0
	cdef double index = 0.0
	
	cdef int subval = (fulldim-macrosize)
	cdef int largesubval = subval*5
	
	cdef int largemacro = macrosize+1
	cdef int largemacromult = largemacro*5
	
	with nogil:
		for i in xrange(macrosize):
			for j in xrange(1,fulldim-1):

				arr1val = arr1ptr[0]
				arr2val = arr2ptr[0]

				fullimgptr[0] = arr1val + fullimgptrrow[0] + fullimgptrcol[0] - fullimgptrneg[0]
				fullimgptr[1] = arr2val + fullimgptrrow[1] + fullimgptrcol[1] - fullimgptrneg[1]
				fullimgptr[2] = arr1val*arr1val + fullimgptrrow[2] + fullimgptrcol[2] - fullimgptrneg[2]
				fullimgptr[3] = arr2val*arr2val + fullimgptrrow[3] + fullimgptrcol[3] - fullimgptrneg[3]
				fullimgptr[4] = arr1val*arr2val + fullimgptrrow[4] + fullimgptrcol[4] - fullimgptrneg[4]

				fullimgptr = fullimgptr + 5
				fullimgptrrow = fullimgptrrow + 5
				fullimgptrcol = fullimgptrcol + 5
				fullimgptrneg = fullimgptrneg + 5
				arr1ptr = arr1ptr + 1
				arr2ptr = arr2ptr + 1
				
			fullimgptr = fullimgptr + 10
			fullimgptrrow = fullimgptrrow + 10
			fullimgptrcol = fullimgptrcol + 10
			fullimgptrneg = fullimgptrneg + 10
			arr1ptr = arr1ptr + 2
			arr2ptr = arr2ptr + 2

	fullimgptr = &fullimg[0]+macrosize*fulldim*5+5
	fullimgptrrow = &fullimg[0]+macrosize*fulldim*5
	fullimgptrcol = &fullimg[0]+(macrosize-1)*fulldim*5+5
	fullimgptrneg = &fullimg[0]+(macrosize-1)*fulldim*5
	
	arr1ptr = &arr1in[0,0]+macrosize*fulldim+1
	arr2ptr = &arr2in[0,0]+macrosize*fulldim+1
	
	with nogil:
		for i in xrange(macrosize,fulldim-1):
			for j in xrange(macrosize):

				arr1val = arr1ptr[0]
				arr2val = arr2ptr[0]

				fullimgptr[0] = arr1val + fullimgptrrow[0] + fullimgptrcol[0] - fullimgptrneg[0]
				fullimgptr[1] = arr2val + fullimgptrrow[1] + fullimgptrcol[1] - fullimgptrneg[1]
				fullimgptr[2] = arr1val*arr1val + fullimgptrrow[2] + fullimgptrcol[2] - fullimgptrneg[2]
				fullimgptr[3] = arr2val*arr2val + fullimgptrrow[3] + fullimgptrcol[3] - fullimgptrneg[3]
				fullimgptr[4] = arr1val*arr2val + fullimgptrrow[4] + fullimgptrcol[4] - fullimgptrneg[4]

				fullimgptr = fullimgptr + 5
				fullimgptrrow = fullimgptrrow + 5
				fullimgptrcol = fullimgptrcol + 5
				fullimgptrneg = fullimgptrneg + 5
				arr1ptr = arr1ptr + 1
				arr2ptr = arr2ptr + 1
				
			fullimgptr = fullimgptr + largesubval
			fullimgptrrow = fullimgptrrow + largesubval
			fullimgptrcol = fullimgptrcol + largesubval
			fullimgptrneg = fullimgptrneg + largesubval
			arr1ptr = arr1ptr + subval
			arr2ptr = arr2ptr + subval

	fullimgptr = &fullimg[0]+(macrosize)*fulldim*5+(macrosize)*5
	fullimgptrrow = &fullimg[0]+(macrosize)*fulldim*5+(macrosize-1)*5
	fullimgptrcol = &fullimg[0]+(macrosize-1)*fulldim*5+(macrosize)*5
	fullimgptrneg = &fullimg[0]+(macrosize-1)*fulldim*5+(macrosize-1)*5
	
	arr1ptr = &arr1in[0,0]+(macrosize)*fulldim+(macrosize)
	arr2ptr = &arr2in[0,0]+(macrosize)*fulldim+(macrosize)
	
	cdef double macrosq = macrosize*macrosize
	cdef double macrocube = macrosize*macrosize*macrosize*macrosize
	
	cdef double mean1 = 0.0
	cdef double mean2 = 0.0
	cdef double variance1 = 0.0
	cdef double variance2 = 0.0
	cdef double covariance = 0.0
	
	with nogil:
		for i in xrange(iidim):
			for j in xrange(iidim):

				arr1val = arr1ptr[0]
				arr2val = arr2ptr[0]
				
				fullimgptr[0] = arr1val + fullimgptrrow[0] + fullimgptrcol[0] - fullimgptrneg[0]
				fullimgptr[1] = arr2val + fullimgptrrow[1] + fullimgptrcol[1] - fullimgptrneg[1]
				fullimgptr[2] = arr1val*arr1val + fullimgptrrow[2] + fullimgptrcol[2] - fullimgptrneg[2]
				fullimgptr[3] = arr2val*arr2val + fullimgptrrow[3] + fullimgptrcol[3] - fullimgptrneg[3]
				fullimgptr[4] = arr1val*arr2val + fullimgptrrow[4] + fullimgptrcol[4] - fullimgptrneg[4]

				mu1temp = fullimgptr_d[0]+fullimgptr_a[0]-fullimgptr_c[0]-fullimgptr_b[0]
				mu2temp = fullimgptr_d[1]+fullimgptr_a[1]-fullimgptr_c[1]-fullimgptr_b[1]
				sigma1temp = fullimgptr_d[2]+fullimgptr_a[2]-fullimgptr_c[2]-fullimgptr_b[2]
				sigma2temp = fullimgptr_d[3]+fullimgptr_a[3]-fullimgptr_c[3]-fullimgptr_b[3]
				sigma12temp = fullimgptr_d[4]+fullimgptr_a[4]-fullimgptr_c[4]-fullimgptr_b[4]
				
				mu1sqval = mu1temp*mu1temp
				mu2sqval = mu2temp*mu2temp
				mu12val = mu1temp*mu2temp

				mean1 = mu1temp*(1.0/macrosq)
				mean2 = mu2temp*(1.0/macrosq)

				variance1 = (sigma1temp*macrosq-mu1sqval)*(1.0/macrocube)
				variance2 = (sigma2temp*macrosq-mu2sqval)*(1.0/macrocube)
				covariance = (sigma12temp*macrosq-mu12val)*(1.0/macrocube)
				
				num = (2.0*mean1*mean2+c1)*(2.0*covariance+c2)
				denom = (mean1*mean1+mean2*mean2+c1)*(variance1+variance2+c2)

				res = num*(1.0/denom)
				
				index = index + res
				
				fullimgptr = fullimgptr + 5
				fullimgptrrow = fullimgptrrow + 5
				fullimgptrcol = fullimgptrcol + 5
				fullimgptrneg = fullimgptrneg + 5
				
				arr1ptr = arr1ptr + 1
				arr2ptr = arr2ptr + 1
				
				fullimgptr_d = fullimgptr_d + 5
				fullimgptr_a = fullimgptr_a + 5
				fullimgptr_c = fullimgptr_c + 5
				fullimgptr_b = fullimgptr_b + 5
				
			fullimgptr = fullimgptr + largemacromult
			fullimgptrrow = fullimgptrrow + largemacromult
			fullimgptrcol = fullimgptrcol + largemacromult
			fullimgptrneg = fullimgptrneg + largemacromult
			
			arr1ptr = arr1ptr + largemacro
			arr2ptr = arr2ptr + largemacro
			
			fullimgptr_d = fullimgptr_d + largemacromult
			fullimgptr_a = fullimgptr_a + largemacromult
			fullimgptr_c = fullimgptr_c + largemacromult
			fullimgptr_b = fullimgptr_b + largemacromult

	try:
		return index/(float(iidim)*float(iidim))
	
	finally:
		free(fullimg)
		
def ssim2(numpy.ndarray[int, ndim=2, mode="c"] arr1in, numpy.ndarray[int, ndim=2, mode="c"] arr2in, int iidim, int macrosize):

	cdef double c1 = 6.5025
	cdef double c2 = 58.5225
	
	cdef int i = 0
	cdef int j = 0
	
	cdef int fulldim = arr1in.shape[0]

	cdef int* fullimg = <int*>calloc(fulldim*fulldim*5,sizeof(int))
	#cdef int* fullimg = <int*>malloc(fulldim*fulldim*5*sizeof(int))
	
	cdef int* fullimgptr = &fullimg[0]+fulldim*5+5
	cdef int* fullimgptrrow = &fullimg[0]+fulldim*5
	cdef int* fullimgptrcol = &fullimg[0]+5
	cdef int* fullimgptrneg = &fullimg[0]
	
	cdef int* arr1ptr = &arr1in[0,0]+1+fulldim
	cdef int* arr2ptr = &arr2in[0,0]+1+fulldim
	
	cdef int arr1val
	cdef int arr2val
	
	cdef int* fullimgptr_d = &fullimg[0]+(macrosize)*fulldim*5+(macrosize)*5
	cdef int* fullimgptr_a = &fullimg[0]
	cdef int* fullimgptr_c = &fullimg[0]+(macrosize)*fulldim*5
	cdef int* fullimgptr_b = &fullimg[0]+(macrosize)*5
	
	cdef double mu1sqval = 0.0
	cdef double mu2sqval = 0.0
	cdef double mu12val = 0.0
	
	cdef double mu1temp = 0.0
	cdef double mu2temp = 0.0
	cdef double sigma1temp = 0.0
	cdef double sigma2temp = 0.0
	cdef double sigma12temp = 0.0
	
	cdef double num = 0.0
	cdef double denom = 0.0
	cdef double res = 0.0
	cdef double index = 0.0
	
	cdef int subval = (fulldim-macrosize)
	cdef int largesubval = subval*5
	
	cdef int subwindows = iidim/macrosize
	
	cdef int largemacro = macrosize+1+(iidim-(subwindows*macrosize))
	#cdef int largemacro = macrosize+1
	cdef int largemacromult = largemacro*5
	
	with nogil:
		for i in xrange(1,fulldim-1):
			for j in xrange(1,fulldim-1):

				arr1val = arr1ptr[0]
				arr2val = arr2ptr[0]

				fullimgptr[0] = arr1val + fullimgptrrow[0] + fullimgptrcol[0] - fullimgptrneg[0]
				fullimgptr[1] = arr2val + fullimgptrrow[1] + fullimgptrcol[1] - fullimgptrneg[1]
				fullimgptr[2] = arr1val*arr1val + fullimgptrrow[2] + fullimgptrcol[2] - fullimgptrneg[2]
				fullimgptr[3] = arr2val*arr2val + fullimgptrrow[3] + fullimgptrcol[3] - fullimgptrneg[3]
				fullimgptr[4] = arr1val*arr2val + fullimgptrrow[4] + fullimgptrcol[4] - fullimgptrneg[4]

				fullimgptr = fullimgptr + 5
				fullimgptrrow = fullimgptrrow + 5
				fullimgptrcol = fullimgptrcol + 5
				fullimgptrneg = fullimgptrneg + 5
				arr1ptr = arr1ptr + 1
				arr2ptr = arr2ptr + 1
				
			fullimgptr = fullimgptr + 10
			fullimgptrrow = fullimgptrrow + 10
			fullimgptrcol = fullimgptrcol + 10
			fullimgptrneg = fullimgptrneg + 10
			arr1ptr = arr1ptr + 2
			arr2ptr = arr2ptr + 2

	fullimgptr = &fullimg[0]+(macrosize)*fulldim*5+(macrosize)*5
	fullimgptrrow = &fullimg[0]+(macrosize)*fulldim*5+(macrosize-1)*5
	fullimgptrcol = &fullimg[0]+(macrosize-1)*fulldim*5+(macrosize)*5
	fullimgptrneg = &fullimg[0]+(macrosize-1)*fulldim*5+(macrosize-1)*5
	
	cdef double macrosq = macrosize*macrosize
	cdef double macrocube = macrosize*macrosize*macrosize*macrosize
	
	cdef double mean1 = 0.0
	cdef double mean2 = 0.0
	cdef double variance1 = 0.0
	cdef double variance2 = 0.0
	cdef double covariance = 0.0
	
	cdef int counter = 0
	
	cdef int stepval = iidim/subwindows
	
	for i in xrange(subwindows):
		for j in xrange(subwindows):
			
			mu1temp = fullimgptr_d[0]+fullimgptr_a[0]-fullimgptr_c[0]-fullimgptr_b[0]
			mu2temp = fullimgptr_d[1]+fullimgptr_a[1]-fullimgptr_c[1]-fullimgptr_b[1]
			sigma1temp = fullimgptr_d[2]+fullimgptr_a[2]-fullimgptr_c[2]-fullimgptr_b[2]
			sigma2temp = fullimgptr_d[3]+fullimgptr_a[3]-fullimgptr_c[3]-fullimgptr_b[3]
			sigma12temp = fullimgptr_d[4]+fullimgptr_a[4]-fullimgptr_c[4]-fullimgptr_b[4]
			
			mu1sqval = mu1temp*mu1temp
			mu2sqval = mu2temp*mu2temp
			mu12val = mu1temp*mu2temp

			mean1 = mu1temp*(1.0/macrosq)
			mean2 = mu2temp*(1.0/macrosq)

			variance1 = (sigma1temp*macrosq-mu1sqval)*(1.0/macrocube)
			variance2 = (sigma2temp*macrosq-mu2sqval)*(1.0/macrocube)
			covariance = (sigma12temp*macrosq-mu12val)*(1.0/macrocube)
			
			num = (2.0*mean1*mean2+c1)*(2.0*covariance+c2)
			denom = (mean1*mean1+mean2*mean2+c1)*(variance1+variance2+c2)

			res = num*(1.0/denom)
			
			#print str(i)+','+str(j)+' - '+str(res)
			
			index = index + res
			
			fullimgptr_d = fullimgptr_d + 5*stepval
			fullimgptr_a = fullimgptr_a + 5*stepval
			fullimgptr_c = fullimgptr_c + 5*stepval
			fullimgptr_b = fullimgptr_b + 5*stepval
			counter = counter + stepval
			
		fullimgptr_d = fullimgptr_d + largemacromult
		fullimgptr_a = fullimgptr_a + largemacromult
		fullimgptr_c = fullimgptr_c + largemacromult
		fullimgptr_b = fullimgptr_b + largemacromult
		counter = counter + largemacro - macrosize - 1

	#print counter
	#print (iidim-1)*(iidim-1)
	#print iidim*iidim
	#print fulldim*fulldim
	#print '-----------------------------'
	
	try:
		return index/(float(subwindows)*float(subwindows))
	
	finally:
		free(fullimg)