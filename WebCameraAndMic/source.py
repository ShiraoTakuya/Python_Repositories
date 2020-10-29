import cv2
import numpy as np
import pyaudio

class mic:
	def __init__(self):
		self.CHUNK = 4096
		self.RATE = 16000
		self.stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=self.RATE, input=True, output=True, frames_per_buffer=self.CHUNK)
	def read(self):
		return np.frombuffer(self.stream.read(self.CHUNK), dtype="int16") / 32768

class cam:
	def __init__(self):
		self.camera = cv2.VideoCapture(0)
	def read(self):
		ret, frame = self.camera.read()
		return frame


## MAIN BEGIN ##

cam = cam()
mic = mic()

while True:
	cv2.imshow('cam', cam.read())
	cv2.imshow('min', mic.read().reshape((64,64)))
	if cv2.waitKey(1) & 0xFF == ord('q'):
		break
cv2.destroyAllWindows()

## MAIN END ##