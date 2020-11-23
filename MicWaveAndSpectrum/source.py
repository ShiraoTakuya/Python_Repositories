import cv2
import matplotlib.pyplot as plt
import numpy as np
import pyaudio
from matplotlib.animation import FuncAnimation

# Definition of initial parameters for waveform and spectrum
N = 4096
RATE = 40000
t_s = np.arange(0,N/RATE,1/RATE)
f_hz = np.arange(0,RATE,RATE/N)

class mic:
	def __init__(self):
		self.CHUNK = N
		self.RATE = RATE
		self.stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=self.RATE, input=True, output=True, frames_per_buffer=self.CHUNK)
	def read(self):
		return np.frombuffer(self.stream.read(self.CHUNK), dtype="int16") / 32768

def main():
	mic_inst = mic()

	# Initialization of plt
	fig = plt.figure()
	axs = [fig.add_subplot(211),fig.add_subplot(212)]

	def update(t):
		wave = mic_inst.read()
		spectrum = np.abs(np.fft.fft(wave) / (N/2))
		axs[0].cla()
		axs[0].set_xlim([0, N/RATE])
		axs[0].set_ylim([-1, 1])
		axs[0].set_xlabel("t[s]")
		axs[0].set_ylabel("signal")
		axs[0].plot(t_s, wave, c="blue")
		axs[1].cla()
		axs[1].set_yscale('log')
		axs[1].set_xlim([0, int(RATE/2)])
		axs[1].set_ylim([0.0001, 1])		
		axs[1].set_xlabel("f[Hz]")
		axs[1].set_ylabel("Amplitude")
		axs[1].plot(f_hz, spectrum, c="blue")
		plt.tight_layout()

	anim = FuncAnimation(fig, update, interval=100)
	plt.show()

main()
