import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time

class Graph:
	strfilename = ""
	frames = []
	fig = []
	axs = []
	graphs = []

	def __init__(self, strfilename):
		self.strfilename = strfilename
		self.frames = self.video_to_numpy()
		self.generate_graph_frame()

	def generate_graph_frame(self):
		plt.ion()
		self.fig = plt.figure()
		self.axs = [self.fig.add_subplot(311),self.fig.add_subplot(312),self.fig.add_subplot(313)]
		for i in range(0,3):
			self.axs[i].set_ylabel(["R","G","B"][i])
			self.axs[i].set_ylim([0, 255])
			self.axs[i].set_ylim([0, 255])
			graph, = self.axs[i].plot(range(0, self.frames[i][0][0].size), self.frames[i][0][0], c="blue")
			self.graphs.append(graph)

	def video_to_numpy(self):
		cap = cv2.VideoCapture(self.strfilename)
		frames = []
		while(1):
			ret, frame = cap.read()
			if ret == False:
				return np.flip(np.array(frames).transpose(3,2,1,0), 0)
			frames.append(frame)

	def update(self, x, y):
		for i in range(0,3):
			self.graphs[i].set_ydata(self.frames[i][x][y])
			self.graphs[i].set_xdata(range(0, self.frames[i][x][y].size))

	def func_event_lbutton(self, e, x, y, flags, param):
		if e == cv2.EVENT_LBUTTONDOWN:
			self.update(x, y)

	def show(self):
		cap = cv2.VideoCapture(self.strfilename)
		ret, frame = cap.read()
		cv2.imshow("thumnail", frame)
		cv2.setMouseCallback('thumnail',self.func_event_lbutton)
		cv2.waitKey(0)

def main():
	a = Graph("RGB.mp4")
	a.show()

main()
