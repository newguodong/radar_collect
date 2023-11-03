import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import random

from socket import*
from threading import Thread
import threading
import time
import re
import os
import gc
import struct

import json

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from matplotlib.ticker import MultipleLocator


fig = plt.figure()

ax_radar = fig.add_subplot(projection='polar')

fig1 = plt.figure()
ax_radar1 = fig1.add_subplot()

plt.gca().set_aspect('equal', adjustable='box')
ax_radar1.set_xlim(xmin=-800, xmax=800)
ax_radar1.set_ylim(ymin=0, ymax=800)
ax_radar1.xaxis.set_major_locator(MultipleLocator(36))
ax_radar1.yaxis.set_major_locator(MultipleLocator(36))

ax_radar1.grid(False,color='black',linestyle=':',linewidth=0.5)

plt.show()