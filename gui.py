import Tkinter as tk
import tkMessageBox
import sys
import cv2
from PIL import Image, ImageOps, ImageTk

class searchWindow(tk.Frame):

	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.grid()
		self.parent.protocol("WM_DELETE_WINDOW", self.close)
		vcmdsize = self.register(self.validatesize)

		tk.Label(self, text="Path:").grid(row=0)
		self.pathbox = tk.Entry(self)
		self.pathbox.config(width=100)
		self.pathbox.grid(row=0,column=1)
		
		#self.pathbox.insert(0,r"C:\Users\Luke\Desktop\ALBUMS\Dump - Imgur")
		self.pathbox.insert(0,r"C:\Users\Luke\Dropbox\Personal\deadringer-70298\testpat.1k")

		tk.Label(self, text="Macrosize:").grid(row=1)
		self.macrosizebox = tk.Entry(self,validate="key",validatecommand=(vcmdsize,3,'%i','%P'))
		self.macrosizebox.config(width=4)
		self.macrosizebox.grid(sticky='W',row=1,column=1)
		self.macrosizebox.insert(0,5)

		tk.Label(self, text="Dimensions:").grid(row=2)
		self.dimensionsbox = tk.Entry(self,validate="key",validatecommand=(vcmdsize,3,'%i','%P'))
		self.dimensionsbox.config(width=4)
		self.dimensionsbox.grid(sticky='W',row=2,column=1)
		self.dimensionsbox.insert(0,64)

		tk.Label(self, text="Lower threshold:").grid(row=3)
		self.thresholdlowerbox = tk.Entry(self,validate="key",validatecommand=(vcmdsize,4,'%i','%P'))
		self.thresholdlowerbox.config(width=4)
		self.thresholdlowerbox.grid(sticky='W',row=3,column=1)
		self.thresholdlowerbox.insert(0,0.5)

		tk.Label(self, text="Upper Threshold:").grid(row=4)
		self.thresholdupperbox = tk.Entry(self,validate="key",validatecommand=(vcmdsize,4,'%i','%P'))
		self.thresholdupperbox.config(width=4)
		self.thresholdupperbox.grid(sticky='W',row=4,column=1)

		self.parent.bind("<Return>",self.enter)

		tk.Button(self, text='Okay',command=self.enter).grid(sticky='NSEW',row=5,columnspan=2)
		
		self.thresholdupper = 1.0

	def validatesize(self,reference,index,currstring):
		if(len(currstring) == 0):
			return (int(index) < int(reference)) and (len(currstring) <= int(reference))
		else:
			return (int(index) < int(reference)) and (len(currstring) <= int(reference)) and (currstring.replace('.','',1).replace('-','',1).isdigit() or currstring == '-')

	def enter(self,event=0):
		self.path = self.pathbox.get()
		self.macrosize = self.macrosizebox.get()
		self.dimensions = self.dimensionsbox.get()
		self.thresholdlower = self.thresholdlowerbox.get()
		if(self.thresholdupperbox.get() != ""):
			self.thresholdupper = self.thresholdupperbox.get()

		if(self.path != "" and self.macrosize != "" and self.dimensions != "" and self.thresholdlower != ""):
			self.macrosize = int(self.macrosizebox.get())
			self.dimensions = int(self.dimensionsbox.get())
			self.thresholdlower = float(self.thresholdlowerbox.get())
			if(self.thresholdupperbox.get() != ""):
				self.thresholdupper = float(self.thresholdupperbox.get())
			self.parent.destroy()

	def close(self):
		self.parent.destroy()
		sys.exit(1)
		
class resultsWindow(tk.Frame):
	def __init__(self, parent,imagelist):
		self.imagelist = imagelist
		tk.Frame.__init__(self, parent)
		self.parent = parent
		self.grid()
		self.current = 0
		self.wmax = 500
		self.hmax = 600
		
		self.grid_columnconfigure(0,weight=1)

		self.imageframe = tk.Frame(self,width=self.wmax*2+100,height=self.hmax+100)
		self.imageframe.grid()
		self.imageframe.grid_propagate(False)
		self.imageframe.grid_columnconfigure(0,weight=1)
		self.imageframe.grid_columnconfigure(1,weight=0)
		self.imageframe.grid_columnconfigure(2,weight=1)
		self.imageframe.grid_rowconfigure(0,weight=1)

		self.dividerframe = tk.Frame(self.imageframe,width=2)
		self.dividerframe.grid(sticky='NS',row=0,column=1)
		
		self.buttonframe = tk.Frame(self)
		self.buttonframe.grid(sticky='WE',row=1,column=0)
		self.buttonframe.grid_columnconfigure(0,weight=1)
		self.buttonframe.grid_columnconfigure(1,weight=0)
		self.buttonframe.grid_columnconfigure(2,weight=1)

		self.imagelabel1 = tk.Label(self.imageframe,background='white',width=self.wmax)
		self.imagelabel1.grid(sticky='NSEW',ipadx=5,row=0,column=0)
		self.imagelabel2 = tk.Label(self.imageframe,background='white',width=self.wmax)
		self.imagelabel2.grid(sticky='NSEW',ipadx=5,row=0,column=2)
		self.imagetext1 = tk.Label(self.imageframe)
		self.imagetext1.grid(row=1,column=0)
		self.imagetext2 = tk.Label(self.imageframe)
		self.imagetext2.grid(row=1,column=2)

		self.imagesize1 = tk.Label(self.imageframe)
		self.imagesize1.grid(row=2,column=0)
		self.imagesize2 = tk.Label(self.imageframe)
		self.imagesize2.grid(row=2,column=2)
		
		self.indexlabel = tk.Label(self.buttonframe)
		self.indexlabel.grid(row=0,column=1)
		
		self.countlabel = tk.Label(self.buttonframe)
		self.countlabel.grid(row=1,column=1)
		
		tk.Button(self.buttonframe, text='Prev'.center(20), command=lambda: self.move(-1)).grid(sticky='E',row=3,column=0)
		tk.Button(self.buttonframe, text='Next'.center(20), command=lambda: self.move(+1)).grid(sticky='W',row=3,column=2)
		tk.Button(self.buttonframe, text='Quit'.center(20), command=self.parent.destroy).grid(sticky='EW',row=4,column=1)
		
		self.move(0)
		
	def move(self,delta):
		if not (0 <= self.current + delta < len(self.imagelist)):
			tkMessageBox.showinfo('End', 'No more images')
			return
		self.current += delta
		
		self.wmax = float(self.wmax)
		self.hmax = float(self.hmax)

		image1 = cv2.imread(self.imagelist[self.current][0][0].path)
		image1 = cv2.cvtColor(image1,cv2.COLOR_RGB2BGR)
		try:
			h1,w1 = image1.shape[:2]
		except:
			h1 = 0
			w1 = 0
			
		if(int(self.wmax/w1*h1) < self.hmax):
			image1 = cv2.resize(image1, (int(self.wmax),int(self.wmax/w1*h1)), interpolation=cv2.INTER_AREA)

		elif(int(self.hmax/h1*w1) < self.wmax):
			image1 = cv2.resize(image1, (int(self.hmax/h1*w1),int(self.hmax)), interpolation=cv2.INTER_AREA)

		image2 = cv2.imread(self.imagelist[self.current][0][1].path)
		image2 = cv2.cvtColor(image2,cv2.COLOR_RGB2BGR)

		try:
			h2,w2 = image2.shape[:2]
		except:
			h2 = 0
			w2 = 0
			
		if(int(self.wmax/w2*h2) < self.hmax):
			image2 = cv2.resize(image2, (int(self.wmax),int(self.wmax/w2*h2)), interpolation=cv2.INTER_AREA)

		elif(int(self.hmax/h2*w2) < self.wmax):
			image2 = cv2.resize(image2, (int(self.hmax/h2*w2),int(self.hmax)), interpolation=cv2.INTER_AREA)

		image1 = Image.fromarray(image1)
		photo1 = ImageTk.PhotoImage(image1)
		self.imagelabel1['image'] = photo1
		self.imagelabel1.photo = photo1
		
		image2 = Image.fromarray(image2)
		photo2 = ImageTk.PhotoImage(image2)
		self.imagelabel2['image'] = photo2
		self.imagelabel2.photo = photo2

		self.imagetext1['text'] = self.imagelist[self.current][0][0].path
		self.imagetext2['text'] = self.imagelist[self.current][0][1].path

		if self.imagelist[self.current][0][0].h > self.imagelist[self.current][0][1].h and self.imagelist[self.current][0][0].w > self.imagelist[self.current][0][1].w:
			self.imagesize1.configure(foreground = 'red')
			self.imagesize2.configure(foreground = 'black')
		elif self.imagelist[self.current][0][0].h < self.imagelist[self.current][0][1].h and self.imagelist[self.current][0][0].w < self.imagelist[self.current][0][1].w:
			self.imagesize1.configure(foreground = 'black')
			self.imagesize2.configure(foreground = 'red')
		else:
			self.imagesize1.configure(foreground = 'black')
			self.imagesize2.configure(foreground = 'black')
		self.imagesize1['text'] = str(self.imagelist[self.current][0][0].w)+' x '+str(self.imagelist[self.current][0][0].h)
		self.imagesize2['text'] = str(self.imagelist[self.current][0][1].w)+' x '+str(self.imagelist[self.current][0][1].h)

		self.indexlabel['text'] = str(round(self.imagelist[self.current][1]*100,2))+'%'
		self.countlabel['text'] = str(self.current+1)+'/'+str(len(self.imagelist))

	def showimg(imgnum):
		global current
		global cleanedlist
		cv2.namedWindow("IMAGE",cv2.WINDOW_NORMAL)
		cv2.imshow("IMAGE",cv2.imread(cleanedlist[current][imgnum]))
		cv2.resizeWindow("IMAGE",500,500)
