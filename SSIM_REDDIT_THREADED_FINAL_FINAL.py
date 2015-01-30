import sys
import numpy
from PIL import Image, ImageOps, ImageTk
import os
import cProfile, pstats, StringIO
import itertools
import re
import cv2
from Tkinter import Frame, Tk, Label, Button, Entry
import Tkinter
import tkMessageBox
from operator import attrgetter, itemgetter

from functions import *

import json

import sqlite3

total = 0

path,multisize = r'',0
macrosize = 11
dimensions = 64
thresholdlower = 0.25
thresholdupper = 1.0
scaling = ''
wmax = 0
hmax = 0
margin = 0

beforecount = 0
aftercount = 0

if __name__ == "__main__":
    
    def validatesize(reference,index,currstring):
        if(len(currstring) == 0):
            return (int(index) < int(reference)) and (len(currstring) <= int(reference))
        else:
            return (int(index) < int(reference)) and (len(currstring) <= int(reference)) and (currstring.replace('.','',1).replace('-','',1).isdigit() or currstring == '-')
    
    def enter():

        global path
        global macrosize
        global dimensions
        global thresholdlower
        global thresholdupper
        
        path = pathbox.get()
        macrosize = macrosizebox.get()
        dimensions = dimensionsbox.get()
        thresholdlower = thresholdlowerbox.get()
        if(thresholdupperbox.get() != ""):
            thresholdupper = thresholdupperbox.get()

        if(path != "" and macrosize != "" and dimensions != "" and thresholdlower != ""):
            macrosize = int(macrosizebox.get())
            dimensions = int(dimensionsbox.get())
            thresholdlower = float(thresholdlowerbox.get())
            if(thresholdupperbox.get() != ""):
                thresholdupper = float(thresholdupperbox.get())
            root.destroy()

    def callback(event):
        enter()

    def close():
        root.destroy()
        sys.exit(1)

    root = Tk()

    root.protocol("WM_DELETE_WINDOW", close)

    mainframe = Frame(root)

    mainframe.grid()

    vcmdsize = mainframe.register(validatesize)

    Label(mainframe, text="Path:").grid(row=0)
    pathbox = Entry(mainframe)
    pathbox.config(width=100)
    pathbox.grid(row=0,column=1)
    #pathbox.insert(0,r"C:\Users\Luke\Desktop\art\REFERENCES\REDDIT\images")
    #pathbox.insert(0,r"C:\Users\Luke\Desktop\art\REFERENCES\REDDIT\TEST")
    #pathbox.insert(0,r"C:\Users\Luke\Desktop\art\REFERENCES\REDDIT\images\FIT")
    pathbox.insert(0,r"C:\Users\Luke\Dropbox\Personal\deadringer-70298\testpat.1k")
    #pathbox.insert(0,r"C:\Users\Luke\Desktop\ALBUMS")
    #pathbox.insert(0,r"C:\Users\Luke\Desktop\ALBUMS\testpat.1k")
    #pathbox.insert(0,r"C:\Users\Luke\Desktop\ALBUMS\My wallpapers - Imgur")
    
    Label(mainframe, text="Macrosize:").grid(row=1)
    macrosizebox = Entry(mainframe,validate="key",validatecommand=(vcmdsize,3,'%i','%P'))
    macrosizebox.config(width=4)
    macrosizebox.grid(sticky='W',row=1,column=1)
    macrosizebox.insert(0,macrosize)

    Label(mainframe, text="Dimensions:").grid(row=2)
    dimensionsbox = Entry(mainframe,validate="key",validatecommand=(vcmdsize,3,'%i','%P'))
    dimensionsbox.config(width=4)
    dimensionsbox.grid(sticky='W',row=2,column=1)
    dimensionsbox.insert(0,dimensions)
    
    Label(mainframe, text="Lower threshold:").grid(row=3)
    thresholdlowerbox = Entry(mainframe,validate="key",validatecommand=(vcmdsize,4,'%i','%P'))
    thresholdlowerbox.config(width=4)
    thresholdlowerbox.grid(sticky='W',row=3,column=1)
    thresholdlowerbox.insert(0,thresholdlower)
    
    Label(mainframe, text="Upper Threshold:").grid(row=4)
    thresholdupperbox = Entry(mainframe,validate="key",validatecommand=(vcmdsize,4,'%i','%P'))
    thresholdupperbox.config(width=4)
    thresholdupperbox.grid(sticky='W',row=4,column=1)

    root.bind("<Return>",callback)

    Tkinter.Button(mainframe, text='Okay',command=enter).grid(sticky='NSEW',row=5,columnspan=2)

    root.mainloop()
    
    #sys.exit(1)

    imagelist = imagein(path,macrosize,dimensions)
    imagelist = optimize(imagelist,multisize)

    #sys.exit(1)

    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    try:
        cursor.execute('ALTER TABLE ssim ADD COLUMN "%s" real DEFAULT null' % makekey(macrosize,dimensions))
    except:
        pass

    conn.commit()

    conn.close()
    
    ssim_list = ssim(imagelist,macrosize,dimensions,thresholdlower,thresholdupper)

    print len(ssim_list)

    for value in ssim_list:
        if value == None:
            print value

    #sys.exit(1)
    '''
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    pr = cProfile.Profile()
    pr.enable()

    cursor.execute('BEGIN TRANSACTION')

    pair_dim = makekey(macrosize,dimensions)
    
    cursor.executemany('INSERT OR IGNORE INTO ssim (image_one,image_two,"%s") VALUES (?,?,?)' % pair_dim, [(pair[0][0].path,pair[0][1].path,pair[1]) for pair in ssim_list if pair[1] is not None])
    cursor.executemany('UPDATE ssim SET "%s"=? WHERE image_one=? AND image_two=?' % pair_dim, [(pair[1],pair[0][0].path,pair[0][1].path) for pair in ssim_list if pair[1] is not None])
    cursor.executemany('INSERT OR IGNORE INTO ssim (image_one,image_two,"%s") VALUES (?,?,?)' % pair_dim, [(pair[0][0].path,pair[0][1].path,'na') for pair in ssim_list if pair[1] is None])
    cursor.executemany('UPDATE ssim SET "%s"=? WHERE image_one=? AND image_two=?' % pair_dim, [('na',pair[0][0].path,pair[0][1].path) for pair in ssim_list if pair[1] is None])    
    '''
    '''
    i = 0
    pair_dim = makekey(macrosize,dimensions)
    for value in ssim_list:
        if i%1000 == 0:
            #print i,
            #print len(ssim_list)
            pass
        i = i + 1
        #print makekey(value[0][0].path,value[0][1].path)
        pair_name = makekey(value[0][0].path,value[0][1].path)
        if value[1] is not None:
            try:
                cursor.execute('INSERT INTO ssim (image_one,image_two,"%s") VALUES ("%s","%s",%f)' % (pair_dim,pair_name[0],pair_name[1],value[1]))
            except:
                cursor.execute('UPDATE ssim SET "%s"=%f WHERE image_one="%s" AND image_two="%s"' % (pair_dim,value[1],pair_name[0],pair_name[1]))
        else:
            try:
                cursor.execute('INSERT INTO ssim (image_one,image_two,"%s") VALUES ("%s","%s","%s")' % (pair_dim,pair_name[0],pair_name[1],'na'))
            except:
                cursor.execute('UPDATE ssim SET "%s"="%s" WHERE image_one="%s" AND image_two="%s"' % (pair_dim,'na',pair_name[0],pair_name[1]))
    
    conn.commit()
    
    pr.disable()
    s = StringIO.StringIO()
    sortby = 'time'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats(10)
    print s.getvalue()

    conn.close()
    '''
    print "WROTE VALUES"
    
    #sys.exit(1)

    ssim_list = [x for x in ssim_list if x is not None and x[1] >= thresholdlower and x[1] <= thresholdupper]

    ssim_list.sort(key=itemgetter(1), reverse=True)

    for imagepair,ssimval in ssim_list:
        imagepair.sort(key=attrgetter('h'),reverse=True)

    print str(len(ssim_list))+' results'

    #sys.exit(1)
    
    current = 0

    def move(delta):
        global current
        global ssim_list
        global wmax
        global hmax
        if not (0 <= current + delta < len(ssim_list)):
            tkMessageBox.showinfo('End', 'No more images')
            return
        current += delta

        wmax = float(wmax)
        hmax = float(hmax)
        
        image1 = cv2.imread(ssim_list[current][0][0].path)
        image1 = cv2.cvtColor(image1,cv2.COLOR_RGB2BGR)
        try:
            h1,w1 = image1.shape[:2]
        except:
            h1 = 0
            w1 = 0
            
        if(int(wmax/w1*h1) < hmax):
            image1 = cv2.resize(image1, (int(wmax),int(wmax/w1*h1)), interpolation=cv2.INTER_AREA)

        elif(int(hmax/h1*w1) < wmax):
            image1 = cv2.resize(image1, (int(hmax/h1*w1),int(hmax)), interpolation=cv2.INTER_AREA)

        image2 = cv2.imread(ssim_list[current][0][1].path)
        image2 = cv2.cvtColor(image2,cv2.COLOR_RGB2BGR)

        try:
            h2,w2 = image2.shape[:2]
        except:
            h2 = 0
            w2 = 0
            
        if(int(wmax/w2*h2) < hmax):
            image2 = cv2.resize(image2, (int(wmax),int(wmax/w2*h2)), interpolation=cv2.INTER_AREA)

        elif(int(hmax/h2*w2) < wmax):
            image2 = cv2.resize(image2, (int(hmax/h2*w2),int(hmax)), interpolation=cv2.INTER_AREA)

        image1 = Image.fromarray(image1)
        photo1 = ImageTk.PhotoImage(image1)
        imagelabel1['image'] = photo1
        imagelabel1.photo = photo1
        
        image2 = Image.fromarray(image2)
        photo2 = ImageTk.PhotoImage(image2)
        imagelabel2['image'] = photo2
        imagelabel2.photo = photo2

        imagetext1['text'] = ssim_list[current][0][0].path
        imagetext2['text'] = ssim_list[current][0][1].path

        if ssim_list[current][0][0].h > ssim_list[current][0][1].h and ssim_list[current][0][0].w > ssim_list[current][0][1].w:
            imagesize1.configure(foreground = 'red')
            imagesize2.configure(foreground = 'black')
        elif ssim_list[current][0][0].h < ssim_list[current][0][1].h and ssim_list[current][0][0].w < ssim_list[current][0][1].w:
            imagesize1.configure(foreground = 'black')
            imagesize2.configure(foreground = 'red')
        else:
            imagesize1.configure(foreground = 'black')
            imagesize2.configure(foreground = 'black')
        imagesize1['text'] = str(ssim_list[current][0][0].w)+' x '+str(ssim_list[current][0][0].h)
        imagesize2['text'] = str(ssim_list[current][0][1].w)+' x '+str(ssim_list[current][0][1].h)

        indexlabel['text'] = str(round(ssim_list[current][1]*100,2))+'%'
        countlabel['text'] = str(current+1)+'/'+str(len(ssim_list))

    def showimg(imgnum):
        global current
        global cleanedlist
        cv2.namedWindow("IMAGE",cv2.WINDOW_NORMAL)
        cv2.imshow("IMAGE",cv2.imread(cleanedlist[current][imgnum]))
        cv2.resizeWindow("IMAGE",500,500)

    root = Tk()

    wmax = 500
    hmax = 600

    root.grid_columnconfigure(0,weight=1)

    imageframe = Frame(root,width=wmax*2+100,height=hmax+100)
    imageframe.grid()
    imageframe.grid_propagate(False)
    imageframe.grid_columnconfigure(0,weight=1)
    imageframe.grid_columnconfigure(1,weight=0)
    imageframe.grid_columnconfigure(2,weight=1)
    imageframe.grid_rowconfigure(0,weight=1)

    dividerframe = Frame(imageframe,width=2)
    dividerframe.grid(sticky='NS',row=0,column=1)
    
    buttonframe = Frame(root)
    buttonframe.grid(sticky='WE',row=1,column=0)
    buttonframe.grid_columnconfigure(0,weight=1)
    buttonframe.grid_columnconfigure(1,weight=0)
    buttonframe.grid_columnconfigure(2,weight=1)

    imagelabel1 = Label(imageframe,background='white',width=wmax)
    imagelabel1.grid(sticky='NSEW',ipadx=5,row=0,column=0)
    imagelabel2 = Label(imageframe,background='white',width=wmax)
    imagelabel2.grid(sticky='NSEW',ipadx=5,row=0,column=2)
    imagetext1 = Label(imageframe)
    imagetext1.grid(row=1,column=0)
    imagetext2 = Label(imageframe)
    imagetext2.grid(row=1,column=2)

    imagesize1 = Label(imageframe)
    imagesize1.grid(row=2,column=0)
    imagesize2 = Label(imageframe)
    imagesize2.grid(row=2,column=2)
    
    indexlabel = Label(buttonframe)
    indexlabel.grid(row=0,column=1)
    
    countlabel = Label(buttonframe)
    countlabel.grid(row=1,column=1)
    
    Tkinter.Button(buttonframe, text='Prev'.center(20), command=lambda: move(-1)).grid(sticky='E',row=3,column=0)
    Tkinter.Button(buttonframe, text='Next'.center(20), command=lambda: move(+1)).grid(sticky='W',row=3,column=2)
    Tkinter.Button(buttonframe, text='Quit'.center(20), command=root.destroy).grid(sticky='EW',row=4,column=1)
    
    move(0)

    root.mainloop()
