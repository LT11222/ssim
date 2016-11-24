import sys
import numpy
import os
import itertools
import re
import cv2
from operator import attrgetter, itemgetter
import Tkinter as tk
import tkMessageBox
import gui
from functions import *
import sqlite3
import getsizeof

if __name__ == "__main__":
    
	root = tk.Tk()
	searchWindow = gui.searchWindow(root)
	root.mainloop()
	
	path = searchWindow.path
	macrosize = searchWindow.macrosize
	dimensions = searchWindow.dimensions
	thresholdlower = searchWindow.thresholdlower
	thresholdupper = searchWindow.thresholdupper
	
	imagelist = imagein(path,macrosize,dimensions)
	imagelist = optimize(imagelist)

	conn = sqlite3.connect('data.db')
	cursor = conn.cursor()
	
	try:
		cursor.execute('ALTER TABLE ssim ADD COLUMN "%s" real DEFAULT null' % makekey(macrosize,dimensions))
	except:
		pass

	conn.commit()

	conn.close()
	
	ssim_list = ssim(imagelist,macrosize,dimensions,thresholdlower,thresholdupper)
	
	#sys.exit(1)
	
	conn = sqlite3.connect('data.db')
	cursor = conn.cursor()
	cursor.execute('BEGIN TRANSACTION')
	pair_dim = makekey(macrosize,dimensions)
	
	cursor.executemany('INSERT OR IGNORE INTO ssim (image_one,image_two,"%s") VALUES (?,?,?)' % pair_dim, [(pair[0][0].path,pair[0][1].path,pair[1]) for pair in ssim_list])
	cursor.executemany('UPDATE ssim SET "%s"=? WHERE image_one=? AND image_two=?' % pair_dim, [(pair[1],pair[0][0].path,pair[0][1].path) for pair in ssim_list])
	
	conn.commit()
	conn.close()
	
	print "WROTE VALUES"
	
	#sys.exit(1)
	
	#ssim_list = [[[x[0][0].stripData(),x[0][1].stripData()],x[1]] for x in ssim_list if x is not None and x[1] >= thresholdlower and x[1] <= thresholdupper]
	ssim_list = [x for x in ssim_list if x is not None and x[1] >= thresholdlower and x[1] <= thresholdupper]
	#print total_size(ssim_list,verbose=False)
        
	#sys.exit(1)

	ssim_list.sort(key=itemgetter(1), reverse=True)

	for imagepair,ssimval in ssim_list:
		imagepair.sort(key=attrgetter('h'),reverse=True)

	print str(len(ssim_list))+' results'

	#sys.exit(1)
	
	root = tk.Tk()
	resultsWindow = gui.resultsWindow(root,ssim_list)
	root.mainloop()
