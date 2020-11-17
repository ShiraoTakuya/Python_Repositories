import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Definition of initial parameters for waveform
t_s = np.arange(0,1,0.01)
sig_V = np.zeros(100)
omega = 2*np.pi*1 #f = 1Hz

# Initialization of plt
fig = plt.figure()
axs = [fig.add_subplot(111)]

def update(t):
	print(t) # 2 zeros occur. I don't know why it occurs.
	axs[0].cla()
	axs[0].set_xlim([0, 1])
	axs[0].set_ylim([-1, 1])
	sig_V[:] = np.append(np.sin(omega*t),sig_V)[0:-1]
	axs[0].plot(t_s, sig_V, c="blue")

anim = FuncAnimation(fig, update, frames=t_s, interval=10)

anim.save("oscilloscope.gif", writer = 'imagemagick')
plt.show()
