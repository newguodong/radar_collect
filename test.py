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

ax_radar = fig.add_subplot()

plt.gca().set_aspect('equal', adjustable='box')
ax_radar.set_xlim(xmin=-800, xmax=800)
ax_radar.set_ylim(ymin=0, ymax=800)
ax_radar.xaxis.set_major_locator(MultipleLocator(36))
ax_radar.yaxis.set_major_locator(MultipleLocator(36))

ax_radar.grid(False,color='black',linestyle=':',linewidth=0.5)

# plt.gca().add_patch(plt.Rectangle(xy=(0, 36), width=72, height=108, edgecolor='red', fill=False, linewidth=2))

rect_x_list = list(range(0-108, -520-108, -108))
rect_y_list = list(range(0, 600, 108))

rect_xy_list = []

for rect_x in rect_x_list:
    for rect_y in rect_y_list:
        rect_xy_item = [rect_x, rect_y]
        rect_xy_list.append(rect_xy_item)

rect_x_list = list(range(0, 520, 108))
for rect_x in rect_x_list:
    for rect_y in rect_y_list:
        rect_xy_item = [rect_x, rect_y]
        rect_xy_list.append(rect_xy_item)

print(len(rect_xy_list))

print(rect_xy_list)

# for item in rect_xy_list:

rect2 = {"sx":0, "sy":0, "ex":0, "ey":0}

rect4_list = []

# if rect2['sx']<rect2['ex']:

def line_slope(x1, y1, x2, y2):
    try:
        return (y2 - y1) / (x2 - x1)
    except(ZeroDivisionError):
        return 0

rect_xy = ()
rect_w = 0
rect_h = 0

rect_line_slope = line_slope(rect2['sx'], rect2['sy'], rect2['ex'], rect2['ey'])

if rect_line_slope > 0:
    if rect2['ey'] > rect2['sy']:
        rect_xy = (rect2['sx'], rect2['sy'])
        rect_w = rect2['ex'] - rect2['sx']
        rect_h = rect2['ey'] - rect2['sy']
    else:
        rect_xy = (rect2['ex'], rect2['ey'])
        rect_w = rect2['sx'] - rect2['ex']
        rect_h = rect2['sy'] - rect2['ey']
else:
    if rect2['ey'] > rect2['sy']:
        rect_xy = (rect2['ex'], rect2['sy'])
        rect_w = rect2['sx'] - rect2['ex']
        rect_h = rect2['ey'] - rect2['sy']
    else:
        rect_xy = (rect2['sx'], rect2['ey'])
        rect_w = rect2['ex'] - rect2['sx']
        rect_h = rect2['sy'] - rect2['ey']

print(f"rect_xy={rect_xy}")
print(f"rect_w={rect_w}")
print(f"rect_h={rect_h}")


plt.gca().add_patch(plt.Rectangle(xy=rect_xy, width=rect_w, height=rect_h, edgecolor='green', fill=False, linewidth=1))

plt.show()