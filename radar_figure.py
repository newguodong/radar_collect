import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import random
import time
import os


class radar_sheet():
    def __init__(self, radar_normal_angel, radar_theta, radar_distance, sortnum) -> None:
        self.radar_normal_angel = 90
        self.radar_theta = 120
        self.radar_distance = 800
        self.sortnum = sortnum+1

        self.theta = np.pi*radar_normal_angel/180
        self.width = np.pi*radar_theta/180
        self.colors = plt.cm.viridis(radar_distance / 10.)

        self.fig = plt.figure()

        self.ax_radar = self.fig.add_subplot(projection='polar')

        self.theta = np.pi*radar_normal_angel/180
        self.width = np.pi*radar_theta/180
        self.colors = plt.cm.viridis(radar_distance / 10.)

        self.ax_radar.bar(self.theta, radar_distance, width=self.width, bottom=0.0, color=self.colors, alpha=0.5)

        self.ax_radar.set_thetamin(0)
        self.ax_radar.set_thetamax(360)
        self.ax_radar.set_rlim(0, radar_distance)

        plt.setp(self.ax_radar.get_xticklabels(), visible=False)
        plt.setp(self.ax_radar.get_yticklabels(), visible=False)

        a=[i*np.pi/18 for i in range(1,37)]
        b =sorted([i for i in range(1,37)],reverse=True)
        plt.thetagrids([i*180/np.pi for i in a],b)

        self.ax_radar.grid(False,color='black',linestyle=':',linewidth=0.5)

        pass

    def refresh_sheet(self):
        self.ax_radar.set_thetamin(0)
        self.ax_radar.set_thetamax(360)
        self.ax_radar.set_rlim(0, self.radar_distance)

        plt.setp(self.ax_radar.get_xticklabels(), visible=False)
        plt.setp(self.ax_radar.get_yticklabels(), visible=False)

        a=[i*np.pi/18 for i in range(1,37)]
        b =sorted([i for i in range(1,37)],reverse=True)
        plt.thetagrids([i*180/np.pi for i in a],b)

        self.ax_radar.grid(False,color='black',linestyle=':',linewidth=0.5)
        self.ax_radar.bar(self.theta, self.radar_distance, width=self.width, bottom=0.0, color=self.colors, alpha=0.5)


class radar_shot():
    def __init__(self, radar_sheet, polar_theta=0, polar_r=0, rectx=0, recty=0) -> None:
        self.rectx = rectx
        self.recty = recty
        self.polar_theta = polar_theta
        self.polar_r = polar_r

        # colors=list(mcolors.TABLEAU_COLORS.keys())
        # self.color = mcolors.TABLEAU_COLORS[colors[random.randint(0, len(colors))]]

        # colors=list(mcolors.TABLEAU_COLORS.keys())
        self.color = 'red'

        self.ax = radar_sheet
        pt, = self.ax.plot(np.pi*polar_theta/180, polar_r, 'o', picker=5, color=self.color)
        self.pt = pt
        pass
    
    def newlocation(self, polar_theta, y):
        self.pt.remove()
        pt, = self.ax.plot(np.pi*polar_theta/180, y, 'o', picker=5, color=self.color)
        self.pt = pt


radar1 = radar_sheet(90, 120, 800, 36)
object1 = radar_shot(radar1.ax_radar, 30, 750)
# object2 = radar_shot(radar1.ax_radar, 60, 400)
# object3 = radar_shot(radar1.ax_radar, 100, 500)



plt.draw()
# read_posi = 0
# while(True):
#     b = np.fromfile("radardata.bin", dtype=np.uint8, count=30, offset=read_posi)
#     if len(b)==30:

#         object1.polar_theta+=1
#         object2.polar_theta+=3
#         object3.polar_theta+=1
#         object1.newlocation(object1.polar_theta, object1.polar_r)
#         object2.newlocation(object2.polar_theta, object2.polar_r)
#         object3.newlocation(object3.polar_theta, object3.polar_r)
#         plt.pause(0.5)
#     else:
#         print("data not enough")

def Rectangular_to_Polar(x, y):  # 直角坐标转极坐标，输出的thata为角度值
    r = np.sqrt(np.square(x) + np.square(y))
    theta = np.degrees(np.arctan(y / x))
    return round(r, 2), round(theta, 2)

def Polar_to_Rectangular(r, theta):  # 极坐标转直角坐标，输入的thata需为角度值
    theta = theta * (np.pi / 180)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return round(x, 2), round(y, 2)

read_posi = 0
read_counter = 0

try:
    os.remove("radardata.bin")
except FileNotFoundError:
    print("already clean")
    
while(True):
    try:
        radardata_frame = np.fromfile("radardata.bin", dtype=np.uint8, count=30, offset=read_posi)
        print(f"radardata_frame={radardata_frame}")
        print(f"read_posi={read_posi}")

        if len(radardata_frame)==30:
            print(radardata_frame)
            read_posi += 30
            read_counter += 1
            print(f"read_counter={read_counter}")

            radardata = list(radardata_frame)
            object1_x = radardata[4]+radardata[5]*256
            object1_y = radardata[6]+radardata[7]*256-2**15

            object1_posi = Rectangular_to_Polar(object1_x, object1_y)
            print(object1_posi)

            object1.polar_r = object1_posi[0]/10
            print(f"object1.polar_r={object1.polar_r}")
            object1.polar_theta = object1_posi[1]
            object1.newlocation(object1.polar_theta, object1.polar_r)
            plt.pause(0.5)

        else:
            time.sleep(1)
            print("data not enough")
    except FileNotFoundError:
        print("wait...")
        time.sleep(1)

