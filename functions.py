import cv2
import os
import numpy
from multiprocessing import Lock, Pool, Value, Array
import custmem as cm
import sqlite3
from getsizeof import total_size
import sys
import cProfile, pstats, StringIO

blurdim = 11
blursigma = 1.5
aspectratio = 0.01
lock = Lock()
counter = Value('i',0)

def makekey(str1,str2):
	if type(str1) is str and type(str2) is str:
		templist = sorted([str1,str2])
		return [templist[0],templist[1]]
	else:
		return str(str1)+','+str(str2)

class imageObj():
	def __init__(self,img,path,dimensions,margin):
		self.path = path
		self.h,self.w,dim = img.shape
		self.image = [0,0,0,0]

		grayscale = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
		grayscale = cv2.resize(grayscale,(dimensions*2,dimensions*2),interpolation=cv2.INTER_NEAREST)
		grayscale = cv2.resize(grayscale,(dimensions,dimensions),interpolation=cv2.INTER_AREA)
		grayscale = numpy.asarray(grayscale, dtype=int)
		grayscale = numpy.pad(grayscale,margin+1,mode='constant')
		self.image[0] = grayscale

		color = img
		color = cv2.resize(color,(dimensions*2,dimensions*2),interpolation=cv2.INTER_NEAREST)
		color = cv2.resize(color,(dimensions,dimensions),interpolation=cv2.INTER_AREA)
		color = numpy.asarray(color, dtype=int)

		self.image[1] = numpy.pad(color[:,:,0],margin+1,mode='constant')
		self.image[2] = numpy.pad(color[:,:,1],margin+1,mode='constant')
		self.image[3] = numpy.pad(color[:,:,2],margin+1,mode='constant')	

		self.used = 0

        def stripData(self):
                self.image = 0
                return self

def mssim_test(imagepair):
	lowest = 2.0
	
	with lock:
		counter.value += 1
		if counter.value%10000 == 0:
			print str((counter.value*100)/total)+'%'+' - '+str(counter.value)+' - '+str(total)
	
	for chan in xrange(4):
		ssim = cm.ssim(imagepair[0].image[chan],imagepair[1].image[chan],dimensions,macrosize)
		if ssim < thresholdlower:
			return imagepair,'na'
		elif ssim < lowest:
			lowest = ssim
			
	if lowest >= thresholdlower and lowest <= thresholdupper:
		return imagepair,lowest

def init(macrosize_in,dimensions_in,thresholdlower_in,thresholdupper_in,total_in,counter_in,lock_in):
	global macrosize
	global dimensions
	global thresholdlower
	global thresholdupper
	global total
	global counter
	global lock
	macrosize = macrosize_in
	dimensions = dimensions_in
	thresholdlower = thresholdlower_in
	thresholdupper = thresholdupper_in
	total = total_in
	counter = counter_in
	lock = lock_in

def printtable(cursor):
	cursor.execute('SELECT * FROM ssim')
	rows = cursor.fetchall()
	for row in rows:
		for value in row:
			print value,
		print ''

def perms(imagelist):
	for i in xrange(len(imagelist)+1):
		for j in xrange(i+1,len(imagelist)):
			yield (imagelist[i].path,imagelist[j].path)

def combos(imagelist,cursor):
	pair_dim = makekey(macrosize,dimensions)
	
        for i in xrange(len(imagelist)+1):
		for j in xrange(i+1,len(imagelist)):
			try:
                                templist = cursor.execute('SELECT "%s" FROM ssim WHERE image_one = "%s" AND image_two = "%s"' % pair_dim,imagelist[i].path,imagelist[j].path).fetchall()
				if type(templist) == float or templist.encode('ascii') == 'na':
					yield [imagelist[i],imagelist[j]]
					#continue
				else:
					yield [imagelist[i],imagelist[j]]
			except:
				yield [imagelist[i],imagelist[j]]
			
def triangle(numin):
	return int(numin*(numin-1)/2)

def ssim(imagelist,macrosize,dimensions,thresholdlower,thresholdupper):
	counter.value = 0
	numprocesses = 3
	total = triangle(len(imagelist))
	pool = Pool(processes=numprocesses, initializer=init, initargs=(macrosize,dimensions,thresholdlower,thresholdupper,total,counter,lock))
	init(macrosize,dimensions,thresholdlower,thresholdupper,total,counter,lock)

	conn = sqlite3.connect('data.db')
	cursor = conn.cursor()
	cursor.execute('BEGIN TRANSACTION')

	pr = cProfile.Profile()
        pr.enable()
	
	ssim_list = pool.map_async(mssim_test, combos(imagelist,cursor), int(triangle(len(imagelist))/float(numprocesses))).get(9999999)
	#ssim_list = map(mssim_test, combos(imagelist,cursor))

        pr.disable()
        s = StringIO.StringIO()
        sortby = 'time'
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats(10)
        print s.getvalue()
        
	pool.close()
	pool.join()

	conn.close()
	
	print "FINISHED SSIM"
	return ssim_list

def openimage(path):
	with lock:
		counter.value += 1
		if counter.value%10 == 0:
			print str((counter.value*100)/total)+'%'+' - '+str(counter.value)+' - '+str(total)
	
	img = cv2.imread(path,cv2.CV_LOAD_IMAGE_COLOR)
	
	if img is not None:
		return imageObj(img,path,dimensions,margin)
	else:
		return None

def imageiterator(root,files):
	for i in xrange(len(files)):
		yield root[i]+'\\'+files[i]
                #yield files[i]

def init_imagein(margin_in,dimensions_in,total_in,counter_in):
	global margin
	global dimensions
	global total
	global counter
	margin = margin_in
	dimensions = dimensions_in
	total = total_in
	counter = counter_in

def imagein(path,macrosize,dimensions):
	
	margin = (macrosize-1)/2
	count = 0
	imagelist = []
	dirlen = 0
	img = 0
	numprocesses = 2

	for root, dirs, files in os.walk(path):
		dirlen += len(files)

	rootvals = []
	filevals = []
	
	for value in os.walk(path):
		rootvals +=[value[0]]*len(value[2])
		filevals += value[2]

	pool = Pool(processes=numprocesses, initializer=init_imagein, initargs=(margin,dimensions,dirlen,counter))
	imagelist += pool.map_async(openimage, imageiterator(rootvals,filevals), dirlen/numprocesses).get(9999999)

	imagelist = [image for image in imagelist if image is not None]
	
	return imagelist

def optimize(imagelist_in):
	ratio1,ratio2 = 0,0
	for img1index in xrange(len(imagelist_in)):
		for img2index in xrange(img1index+1,len(imagelist_in)):

			ratio1 = float(imagelist_in[img1index].h)/imagelist_in[img1index].w
			ratio2 = float(imagelist_in[img2index].h)/imagelist_in[img2index].w
			
			if ((ratio1-ratio2)/ratio2)>aspectratio or ((ratio2-ratio1)/ratio1)>aspectratio:
				continue

			else:
				imagelist_in[img1index].used = 1
				imagelist_in[img2index].used = 1

	imagelist_in = [image for image in imagelist_in if image.used == 1]

	return imagelist_in

def ssim_gen(ssim_list):
	for i in xrange(len(ssim_list)):
		pair_name = makekey(ssim_list[i][0][0].path,ssim_list[i][0][1].path)
		yield (pair_name[0],pair_name[1],ssim_list[i][1])
