import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.colors as mcolors
import random
import math

from socket import*
from threading import Thread
import threading
import time
import re
import os
import gc
import struct
import sys

import json

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from matplotlib.ticker import MultipleLocator

import colorama


button_state_list = {
    "exit":False, 
    "json record":False,  
    "fsm":"off", 
    "scan":False,
    "fsm_sm":"off",
    "detect_switch":False,
    "detect_mode":"m1"
    }

button_dict = {}

sendmsglist=[]

radar_msg_list = []

next_af_msg_list = []

radar_sheet_grid_list = []

query_filter_area_msg_list = []

radar_sheet_func_msg_list = []
radar_sheet_msg_dict = {"sector":True}

filter_scan_func_msg_list = []

filter_scan_func_exit_msg_list = []

filter_scan_func_state = {"scan_state":False}

cur_shots_list = []

DynamicPlotThread_msg_list = []

DynamicPlotThread_state_dict = {"draw shot":True}

data_file_path_list = {
    "config_filter_areas_data_json_path":"",
    "config_radar_collect_config_json_path":"",
    "log_once_run_log_folder_path":""
    "radar_box_statistics_path"
}



test_ld6001_data = bytes([0x64, 0x61 , 0x74 , 0x61 , 0x5F , 0x73 , 0x74 , 0x61 , 0x74 , 0x69 , 0x73 , 0x74 , 0x69 , 0x63 , 0x73 , 0x3A , 0xD8 , 0xFF , 0xFF , 0xFF , 0x82 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0xBE , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x00 , 0x5A , 0x65 , 0x6E , 0x64])

# selected_scan_area_list = [
#     {
#         "area_name":"",
#         "area_rect_device":[],
#         "area_rect_show":{
#             "x1":0,
#             "y1":0,
#             "x3":0,
#             "y3":0,
#         }
#     }
# ]
selected_scan_area_list = []
filtered_scan_area_list = []
test_ss_area_list = []



def exit_button_callback():
    button_state_list["exit"] = True
    time.sleep(1)
    os._exit(0)

def json_record_button_callback():
    if button_state_list["json record"] == True:
        button_state_list["json record"] = False
        button_dict["json record switch"]["text"] = "json record off"
    else:
        button_state_list["json record"] = True
        button_dict["json record switch"]["text"] = "json record on"

def detect_switch_button_callback():
    print("detect_switch_button_callback press once")
    if button_state_list["detect_switch"] == True:
        button_state_list["detect_switch"] = False
        button_dict["detect switch"]["text"] = "detect off"
        sendmsglist.append("stop detect")
        
    else:
        button_state_list["detect_switch"] = True
        button_dict["detect switch"]["text"] = "detect on"
        if button_state_list["detect_mode"] == "m1":
            sendmsglist.append("start detect1")
        elif button_state_list["detect_mode"] == "m2":
            sendmsglist.append("start detect2")

def detect_mode_button_callback():
    print("detect_mode_button_callback press once")
    if button_state_list["detect_mode"] == "m1":
        button_state_list["detect_mode"] = "m2"
        button_dict["detect mode"]["text"] = "detect m2"
        sendmsglist.append("start detect2")
        button_state_list["detect_switch"] = True
        button_dict["detect switch"]["text"] = "detect on"
    else:
        button_state_list["detect_mode"] = "m1"
        button_dict["detect mode"]["text"] = "detect m1"
        sendmsglist.append("start detect1")
        button_state_list["detect_switch"] = True
        button_dict["detect switch"]["text"] = "detect on"

def fsm_button_callback():
    if button_state_list["fsm"] == "ss":
        button_state_list["fsm"] = "fs"
        button_dict["fsm"]["text"] = "fsm:fs"

    elif button_state_list["fsm"] == "fs":
        button_state_list["fsm"] = "fss"
        button_dict["fsm"]["text"] = "fsm:fss"

    elif button_state_list["fsm"] == "fss":
        button_state_list["fsm"] = "fsf"
        button_dict["fsm"]["text"] = "fsm:fsf"
    
    elif button_state_list["fsm"] == "fsf":
        button_state_list["fsm"] = "off"
        button_dict["fsm"]["text"] = "fsm:off"

    elif button_state_list["fsm"] == "off":
        button_state_list["fsm"] = "ss"
        button_dict["fsm"]["text"] = "fsm:ss"

def fsm_sm_button_callback():
    if button_state_list["fsm_sm"] == "sel":
        button_state_list["fsm_sm"] = "fil"
        button_dict["fsm_sm"]["text"] = "fsm_sm:fil"

    elif button_state_list["fsm_sm"] == "fil":
        button_state_list["fsm_sm"] = "off"
        button_dict["fsm_sm"]["text"] = "fsm_sm:off"

    elif button_state_list["fsm_sm"] == "off":
        button_state_list["fsm_sm"] = "sel"
        button_dict["fsm_sm"]["text"] = "fsm_sm:sel"

def cfsm_button_callback():
    msg={}
    msg["type"] = "cfsm clear"
    next_af_msg_list.append(msg)

def show_track_button_callback():
    msg={}
    msg["type"] = "show track"
    filter_scan_func_msg_list.append(msg)

def scan_track_button_callback():
    msg={}
    msg["type"] = "scan track"
    msg["scan_type"] = "once"
    filter_scan_func_msg_list.append(msg)

def scan_track_plus_button_callback():
    msg={}
    msg["type"] = "scan track"
    msg["scan_type"] = "period"
    filter_scan_func_msg_list.append(msg)

def pause_scan_button_callback():
    print("pause scan button express once")
    if button_state_list["scan"] == True:
        button_state_list["scan"] = False
        button_dict["pause scan"]["text"] = "pause scan"
    else:
        button_state_list["scan"] = True
        button_dict["pause scan"]["text"] = "scanning"

def sync_pause_scan_button(new_state):
    if new_state == True:
        button_state_list["scan"] = True
        button_dict["pause scan"]["text"] = "scanning"
    else:
        button_state_list["scan"] = False
        button_dict["pause scan"]["text"] = "pause scan"

def exit_scan_button_callback():
    msg={}
    msg["type"] = "exit scan"
    if len(filter_scan_func_exit_msg_list)==0:
        filter_scan_func_exit_msg_list.append(msg)

def sector_button_callback():
    print("sector button express once")
    if radar_sheet_msg_dict["sector"] == True:
        radar_sheet_msg_dict["sector"] = False
        button_dict["radar sector"]["text"] = "sector off"
        msg={}
        msg["type"] = "sector hide"
        radar_sheet_func_msg_list.append(msg)
        print("hide")
    else:
        radar_sheet_msg_dict["sector"] = True
        button_dict["radar sector"]["text"] = "sector on"
        msg={}
        msg["type"] = "sector show"
        radar_sheet_func_msg_list.append(msg)
        print("show")

class tk_button():
    def __init__(self, window, name, text, width, height, callback, b_x=0, b_y=0, b_anchor='s') -> None:
        self.window = window
        
        button = tk.Button(window,width=width, height=height, text=text, padx=1, pady=1, anchor='center', command = callback)
        button.place(x = b_x, y = b_y)
        button_dict[name] = button

def line_slope(x1, y1, x2, y2):
    try:
        return (y2 - y1) / (x2 - x1)
    except(ZeroDivisionError):
        return 0

def rect_2p_to_xywh(x1, y1, x2, y2):
    rect_line_slope = line_slope(x1, y1, x2, y2)
    rect_xywh = {}

    if rect_line_slope > 0:
        if y2 > y1:
            rect_xywh['xy'] = (x1, y1)
            rect_xywh['w'] = x2 - x1
            rect_xywh['h'] = y2 - y1
        else:
            rect_xywh['xy'] = (x2, y2)
            rect_xywh['w'] = x1 - x2
            rect_h = y1 - y2
    else:
        if y2 > y1:
            rect_xywh['xy'] = (x2, y1)
            rect_xywh['w'] = x1 - x2
            rect_xywh['h'] = y2 - y1
        else:
            rect_xywh['xy'] = (x1, y2)
            rect_xywh['w'] = x2 - x1
            rect_xywh['h'] = y1 - y2
    return rect_xywh

def is_point_in_rect(x, y, rect):
    x1, y1, x2, y2 = rect[0], rect[1], rect[2], rect[3]
    if x1<= x<= x2 and y1<= y<= y2:
        return True
    else:
        return False
    
def onclick(event):
    # print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %(event.button, event.x, event.y, event.xdata, event.ydata))
    # print(len(radar_sheet_grid_list))
    if event.xdata!=None and event.ydata!=None:
        for item in radar_sheet_grid_list:
            rect_xy13 = []
            rect_xy13.append(item["x1y1"][0])
            rect_xy13.append(item["x1y1"][1])
            rect_xy13.append(item["x3y3"][0])
            rect_xy13.append(item["x3y3"][1])
            if is_point_in_rect(event.xdata, event.ydata, rect_xy13):
                msg={}
                msg["type"] = "any"
                msg["posi"] = item
                # print(msg)
                next_af_msg_list.append(msg)
                break

def Rectangular_to_Polar(x, y):  # 直角坐标转极坐标，输出的thata为角度值
    try:
        r = np.sqrt(np.square(x) + np.square(y))
        theta = np.degrees(np.arctan(y / x))
        return round(r, 2), round(theta, 2)
    except ZeroDivisionError:
        # print("ZeroDivisionError")
        return (0, 0)

def Polar_to_Rectangular(r, theta):  # 极坐标转直角坐标，输入的thata需为角度值
    
    x = r * np.cos(math.radians(theta))
    y = r * np.sin(math.radians(theta))
    return round(x, 2), round(y, 2)

class radar_sheet():
    def __init__(self, radar_tk_window, sheet_type, radar_normal_angel, radar_theta, radar_distance, sheet_dis_reso, filter_area_reso, scan_interval_time) -> None:
        self.tk_window = radar_tk_window
        self.sheet_type = sheet_type
        self.radar_normal_angel = radar_normal_angel
        self.radar_theta = radar_theta
        self.sheet_distance = radar_distance+(int(radar_distance/5))
        self.sortnum = 36+1
        self.radar_valid_dis = radar_distance
        self.sheet_dis_reso = sheet_dis_reso

        if self.sheet_dis_reso > radar_distance:
            self.sheet_dis_reso = radar_distance
        if self.sheet_dis_reso <= 0:
            self.sheet_dis_reso = 36

        self.filter_area_reso = filter_area_reso
        if self.filter_area_reso < self.sheet_dis_reso:
            self.filter_area_reso = self.sheet_dis_reso

        if self.filter_area_reso%self.sheet_dis_reso != 0:
            self.filter_area_reso = self.sheet_dis_reso*int(self.filter_area_reso/self.sheet_dis_reso)
        
        print(f"self.sheet_dis_reso={self.sheet_dis_reso}")
        print(f"self.filter_area_reso={self.filter_area_reso}")

        self.theta = np.pi*radar_normal_angel/180
        self.width = np.pi*radar_theta/180
        self.colors = plt.cm.viridis(self.radar_valid_dis / 10.)

        self.sector_scan_filter_list = {}
        self.sector_scan_filter_list["mutex_rects"] = []

        

        self.fig = plt.figure()

        self.cid = self.fig.canvas.mpl_connect('button_press_event', onclick)

        if sheet_type == "polar":
            self.ax_radar = self.fig.add_subplot(projection='polar')

            self.theta = np.pi*radar_normal_angel/180
            self.width = np.pi*radar_theta/180
            self.colors = plt.cm.viridis(self.radar_valid_dis / 10.)

            self.ax_radar.bar(self.theta, self.radar_valid_dis, width=self.width, bottom=0.0, color=self.colors, alpha=0.5)

            self.ax_radar.set_thetamin(0)
            self.ax_radar.set_thetamax(360)
            self.ax_radar.set_rlim(0, self.radar_valid_dis)

            plt.setp(self.ax_radar.get_xticklabels(), visible=False)
            plt.setp(self.ax_radar.get_yticklabels(), visible=False)

            a=[i*np.pi/18 for i in range(1,37)]
            b =sorted([i for i in range(1,37)],reverse=True)
            plt.thetagrids([i*180/np.pi for i in a],b)

            self.ax_radar.grid(False,color='black',linestyle=':',linewidth=0.5)
        else:
            self.ax_radar = self.fig.add_subplot()

            plt.gca().set_aspect('equal', adjustable='box')

            self.ax_radar.set_xlim(xmin=-self.sheet_distance, xmax=self.sheet_distance)
            self.ax_radar.set_ylim(ymin=0, ymax=self.sheet_distance)
            self.ax_radar.xaxis.set_major_locator(MultipleLocator(self.sheet_dis_reso))
            self.ax_radar.yaxis.set_major_locator(MultipleLocator(self.sheet_dis_reso))

            if self.sheet_distance/self.sheet_dis_reso > 35:
                for tick in self.ax_radar.get_xticklabels():
                    tick.set_rotation(90)
            elif self.sheet_distance/self.sheet_dis_reso > 15:
                for tick in self.ax_radar.get_xticklabels():
                    tick.set_rotation(45)
            

            self.ax_radar.grid(True,color='black',linestyle=':',linewidth=0.5)

            self.radar_region_sector_color = "cadetblue"
            # arc
            arc = matplotlib.patches.Arc((0,0), self.radar_valid_dis*2, \
                                            self.radar_valid_dis*2, angle=0, \
                                            theta1=self.radar_normal_angel-self.radar_theta/2, \
                                            theta2=self.radar_normal_angel+self.radar_theta/2, \
                                            linestyle=':', \
                                            color = self.radar_region_sector_color, linewidth = 1.5)
            self.ax_radar.add_patch(arc)
            self.radar_sector_arc = arc

            self.ax_radar.plot(0, 0, 'o', picker=5, color="black", markersize = 12)

            # start line
            arc_start_line_angel_with_0 = (180-self.radar_theta)/2
            arc_start_xy = Polar_to_Rectangular(self.radar_valid_dis, arc_start_line_angel_with_0)

            x1, y1 = 0, 0
            x2, y2 = arc_start_xy[0], arc_start_xy[1]


            arc_start_line_x = np.linspace(x1, x2, 100)
            arc_start_line_y = np.linspace(y1, y2, 100)

            self.radar_sector_arc_start_line = self.ax_radar.plot(arc_start_line_x, \
                                                                    arc_start_line_y, \
                                                                    color = self.radar_region_sector_color, \
                                                                    markersize = 1, linestyle=':')

            # end line
            arc_end_line_angel_with_0 = 180-(180-self.radar_theta)/2
            arc_end_xy = Polar_to_Rectangular(self.radar_valid_dis, arc_end_line_angel_with_0)

            x1, y1 = 0, 0
            x2, y2 = arc_end_xy[0], arc_end_xy[1]


            arc_end_line_x = np.linspace(x1, x2, 100)
            arc_end_line_y = np.linspace(y1, y2, 100)

            self.radar_sector_arc_end_line = self.ax_radar.plot(arc_end_line_x, \
                                                                arc_end_line_y, \
                                                                color = self.radar_region_sector_color, \
                                                                markersize = 1, linestyle=':')

            self.radar_sector_valid = True
            # plt.gca().add_patch(plt.Rectangle(xy=(0, 36), width=72, height=108, edgecolor='green', fill=False, linewidth=2))
            # self.valid_dis = 600

            rect_x_list = list(range(0-self.filter_area_reso, -self.radar_valid_dis-self.filter_area_reso, -self.filter_area_reso))
            rect_y_list = list(range(0, self.radar_valid_dis, self.filter_area_reso))

            self.scan_rect_xy_list = []

            for rect_x in rect_x_list:
                for rect_y in rect_y_list:
                    rect_xy_item = [rect_x, rect_y]
                    self.scan_rect_xy_list.append(rect_xy_item)

            rect_x_list = list(range(0, self.radar_valid_dis, self.filter_area_reso))
            for rect_x in rect_x_list:
                for rect_y in rect_y_list:
                    rect_xy_item = [rect_x, rect_y]
                    self.scan_rect_xy_list.append(rect_xy_item)

            print(f"len(self.scan_rect_xy_list)={len(self.scan_rect_xy_list)}")

            print(f"self.scan_rect_xy_list={self.scan_rect_xy_list}")

            self.grid_list = []

            

            for o_item in self.scan_rect_xy_list:
                grid_item = {}
                grid_item["x1y1"] = o_item
                temp_item = [o_item[0]+self.filter_area_reso, o_item[1]]  
                grid_item["x2y2"] = temp_item
                temp_item = [o_item[0]+self.filter_area_reso, o_item[1]+self.filter_area_reso]
                grid_item["x3y3"] = temp_item
                temp_item = [o_item[0], o_item[1]+self.filter_area_reso]  
                grid_item["x4y4"] = temp_item
                self.grid_list.append(grid_item)
            
            # radar_sheet_grid_list = self.grid_list

            for item in self.grid_list:
                radar_sheet_grid_list.append(item)

            print(f"radar_sheet_grid_list={radar_sheet_grid_list}")


            for item in self.scan_rect_xy_list:
                plt.gca().add_patch(plt.Rectangle(xy=(item[0], item[1]), width=self.filter_area_reso, height=self.filter_area_reso, edgecolor='green', fill=False, linewidth=1.5, alpha=0.5))

            # test_scan = plt.gca().add_patch(plt.Rectangle(xy=(-540, 540), width=self.filter_area_reso, height=self.filter_area_reso, edgecolor='red', fill=False, linewidth=2))
            # test_scan.remove()

            self.rect_filters = []

            self.win_screen_high = radar_tk_window.winfo_screenheight()
            self.win_screen_width = radar_tk_window.winfo_screenwidth()

            self.statistics_label_default = "cover_count=--, total_min:--, total_max:--, total_avg:--"
            self.statistics_label = tk.Label(self.tk_window, text=self.statistics_label_default,width=1,height=5,padx=200, pady=2, borderwidth=1, fg='blue')
            self.statistics_label.pack(padx = self.win_screen_width/2, pady = 10, anchor = 'w')


            self.set_scan_interval_time_frame = tk.Frame (self.tk_window)

            #创建一个Label控件
            self.set_scan_label = tk.Label (self.set_scan_interval_time_frame)
            #创建一个Entry控件
            self.set_scan_entry = tk.Entry (self.set_scan_interval_time_frame)
            #读取用户输入的表达式
            self.set_scan_expression = tk.StringVar ()
            #将用户输入的表达式显示在Entry控件上
            self.set_scan_entry ["textvariable"] = self.set_scan_expression
            #创建-一个 Button控件.当用户输入完毕后，单击此按钮即计算表达式的结果
            self.scan_interval_time = scan_interval_time
            self.set_scan_button = tk.Button (self.set_scan_interval_time_frame, text="set:"+str(self.scan_interval_time),command=self.set_scan_func)

            self.set_scan_entry.focus ()
            self.set_scan_interval_time_frame.pack ()
            #Entry控件位于窗体的上方
            self.set_scan_entry .pack(side="left")
            #Label控件位于窗体的左方
            self.set_scan_label .pack (side="left")
            #Button控件位于窗体的右方
            self.set_scan_button.pack (side="right")
        

        # 将 matplotlib 图形嵌入到 tkinter 窗口中
        canvas = FigureCanvasTkAgg(self.fig, master=self.tk_window)   
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        pass
    
    def set_scan_func(self):
        print("set_scan_func")
        input_str = self.set_scan_expression.get()
        input_int = 0
        try:
            input_int = int(input_str)
        except:
            print("Unexpected error:", sys.exc_info()[0])
        else:
            self.scan_interval_time = input_int
            self.set_scan_button["text"] = "set:"+str(self.scan_interval_time)
        print(f"self.scan_interval_time={self.scan_interval_time}")

    def rect_filter_new_area(self, name, sx, sy, ex, ey, ec, fc, alpha, fill, linewidth):
        # print("rect_filter_new_area")
        rect_filter_dict = {}
        rect_filter_dict["name"]=name

        rect_xywh = rect_2p_to_xywh(sx, sy, ex, ey)

        rect_filter_dict["xywh"]=rect_xywh
        rect_filter_dict[name]=plt.gca().add_patch(plt.Rectangle(xy=rect_xywh["xy"], width=rect_xywh["w"], height=rect_xywh["h"], ec=ec, fc=fc, alpha=alpha, fill=fill, linewidth=linewidth))
        self.rect_filters.append(rect_filter_dict)
        pass

    def _rect_filter_move(self, name, sx, sy, ex, ey, ec, fc, alpha, fill, linewidth):
        # print("rect_filter_move")
        find_name = 0
        for item in self.rect_filters:
            if name in item:
                find_name = 1
                item[name].remove()
                self.rect_filters.remove(item)
                break
        self.rect_filter_new_area(name, sx, sy, ex, ey, ec, fc, alpha, fill, linewidth)
        pass

    # def test_area_rect_move(self, name, sx, sy, ex, ey, fil_co='blue'):
    #     self._rect_filter_move(name, sx, sy, ex, ey, ec='blue', fc=fil_co, alpha=0.1, fill=True, linewidth=1)
    
    def rect_filter_move_show_track(self, name, sx, sy, ex, ey):
        self._rect_filter_move(name, sx, sy, ex, ey, ec='blue', fc='green', alpha=0.2, fill=True, linewidth=1)

    def mutex_rect_name(self, name):
        return "mutex_rect_"+name
    def _sheet_selected_rect_move(self, type_name, rect, ec, fc, alpha, fill, linewidth, rect_inside_offset=3, text_show=False, text_offset_x="center", text_offset_y="center"):
        ret = True
        _type_name = type_name
        if "mutex_rect_" not in type_name:
            rect_name = type_name + "_" + str(rect[0]) + "_" + str(rect[1]) + "_" + str(rect[2]) + "_" + str(rect[3] )
        else:
            rect_name = type_name
            _type_name = "mutex_rects"
        # print(f"type_name={type_name}")
        # print(f"_type_name={_type_name}")
        # print(f"rect_name={rect_name}")
        find_name = 0
        if _type_name not in self.sector_scan_filter_list:
            self.sector_scan_filter_list[_type_name] = []
        for item in self.sector_scan_filter_list[_type_name]:
            if rect_name in item:
                # print("in item")
                find_name = 1
                item[rect_name].remove()
                if "index text" in item:
                    item["index text"].set_visible(False)
                self.sector_scan_filter_list[_type_name].remove(item)

                if text_show:
                    for item_1 in self.sector_scan_filter_list[_type_name]:
                        item_number = self.sector_scan_filter_list[_type_name].index(item_1)
                        item_1["index text"].set_text(str(item_number))
                ret = False
                break
        if find_name == 0:
            # print("find name == 0")
            sector_filter_dict = {}
            
            sector_filter_dict["name"] = rect_name

            rect_xywh = rect_2p_to_xywh(rect[0]+rect_inside_offset, rect[1]+rect_inside_offset, rect[2]-rect_inside_offset, rect[3]-rect_inside_offset)
            sector_filter_dict["xy"] = rect
            sector_filter_dict[rect_name]=self.ax_radar.add_patch(plt.Rectangle(xy=rect_xywh["xy"], width=rect_xywh["w"], height=rect_xywh["h"], edgecolor=ec, fc=fc, fill=fill, linewidth=linewidth, alpha=alpha))
            if text_show:
                sector_filter_dict["index text"] = self.ax_radar.text(rect[0]+self.filter_area_reso/2-6, rect[1]+self.filter_area_reso/2-6, str(len(self.sector_scan_filter_list[_type_name])), alpha=0.2)
            self.sector_scan_filter_list[_type_name].append(sector_filter_dict)
            ret = True
        # print(f"self.sector_scan_filter_list={self.sector_scan_filter_list}")

        return ret
    
    def scan_area_order_rect_move(self, type_name, rect):
        self._sheet_selected_rect_move(type_name, rect, ec='red', fc="green", alpha=0.8, fill=False, linewidth=1, text_show=True)

    def selected_area_rect_move(self, type_name, rect):
        self._sheet_selected_rect_move(type_name, rect, ec='blue', fc="green", alpha=0.8, fill=False, linewidth=1.5, rect_inside_offset=8)

    def filtered_area_rect_move(self, type_name, rect):
        self._sheet_selected_rect_move(type_name, rect, ec='darkkhaki', fc="green", alpha=0.8, fill=False, linewidth=1.5, rect_inside_offset=14)
    
    def test_area_rect_move(self, type_name, rect=[], fc="blue"):
        _rect = rect
        if len(_rect)<4:
            _rect = [0, 0, 0, 0]
        return self._sheet_selected_rect_move(type_name, _rect, ec='blue', fc=fc, alpha=0.15, fill=True, linewidth=1, rect_inside_offset=0)

    def scan_area_order_rect_move_clear_all(self, type_name):
        if type_name in self.sector_scan_filter_list:
            print(f"self.sector_scan_filter_list[{type_name}]={self.sector_scan_filter_list[type_name]}")
            for item in self.sector_scan_filter_list[type_name][:]:
                print(f"item={item}")
                rect_name = item["name"]
                item[rect_name].remove()
                item["index text"].set_visible(False)
                self.sector_scan_filter_list[type_name].remove(item)
                print(f"self.sector_scan_filter_list[{type_name}]={self.sector_scan_filter_list[type_name]}")
            # self.sector_scan_filter_list.clear()
        

    def show_sector(self):
        if self.radar_sector_valid != True:
            # arc
            arc = matplotlib.patches.Arc((0,0), self.radar_valid_dis*2, self.radar_valid_dis*2, angle=0, theta1=self.radar_normal_angel-self.radar_theta/2, theta2=self.radar_normal_angel+self.radar_theta/2, linestyle=':', color = "blue", linewidth = 1.5)
            self.ax_radar.add_patch(arc)
            self.radar_sector_arc = arc

            self.ax_radar.plot(0, 0, 'o', picker=5, color="black", markersize = 12)

            # start line
            arc_start_line_angel_with_0 = (180-self.radar_theta)/2
            arc_start_xy = Polar_to_Rectangular(self.radar_valid_dis, arc_start_line_angel_with_0)

            x1, y1 = 0, 0
            x2, y2 = arc_start_xy[0], arc_start_xy[1]


            arc_start_line_x = np.linspace(x1, x2, 100)
            arc_start_line_y = np.linspace(y1, y2, 100)

            self.radar_sector_arc_start_line = self.ax_radar.plot(arc_start_line_x, arc_start_line_y, color = "blue", markersize = 1, linestyle=':')

            # end line
            arc_end_line_angel_with_0 = 180-(180-self.radar_theta)/2
            arc_end_xy = Polar_to_Rectangular(self.radar_valid_dis, arc_end_line_angel_with_0)

            x1, y1 = 0, 0
            x2, y2 = arc_end_xy[0], arc_end_xy[1]


            arc_end_line_x = np.linspace(x1, x2, 100)
            arc_end_line_y = np.linspace(y1, y2, 100)

            self.radar_sector_arc_end_line = self.ax_radar.plot(arc_end_line_x, arc_end_line_y, color = "blue", markersize = 1, linestyle=':')
            self.radar_sector_valid = True
        else:
            print("radar sector already exist")

    def hide_sector(self):
        if self.radar_sector_valid == True:
            try:
                self.radar_sector_arc.remove()
                self.radar_sector_arc_start_line.remove()
                self.radar_sector_arc_end_line.remove()
            except:
                print("hide_sector error:", sys.exc_info()[0])
            self.radar_sector_valid = False
    def save_fig(self, path):
        plt.savefig(path)



class radar_shot():
    def __init__(self, radar_sheet, polar_theta=0, polar_r=0, rectx=0, recty=0, shot_type="act shot") -> None:
        self.rectx = rectx
        self.recty = recty
        self.polar_theta = polar_theta
        self.polar_r = polar_r
        self.shot_type = shot_type

        colors=list(mcolors.TABLEAU_COLORS.keys())
        # self.color = 'red'
        if self.shot_type == "act shot":
            self.color = mcolors.TABLEAU_COLORS[colors[random.randint(0, len(colors)-1)]]
        elif self.shot_type == "mark shot":
            self.color = "black"

        self.ax = radar_sheet.ax_radar
        self.radar_sheet = radar_sheet
        if radar_sheet.sheet_type == "polar":
            pt, = self.ax.plot(np.pi*polar_theta/180, polar_r, 'o', picker=5, color=self.color, markersize = 8)
            self.pt = pt
        else:
            pt, = self.ax.plot(rectx, recty, 'o', picker=5, color=self.color, markersize = 8)
            self.pt = pt
        pass
    
    def newlocation(self, polar_theta, polar_r, rect_x, rect_y):
        try:
            self.pt.remove()
        except ValueError:
            # print("ignore shot")
            pass

        if self.radar_sheet.sheet_type == "polar":
            self.polar_theta = polar_theta
            self.polar_r = polar_r
            pt, = self.ax.plot(np.pi*polar_theta/180, polar_r, 'o', picker=5, color=self.color, markersize = 8)
            self.pt = pt
        else:
            pt, = self.ax.plot(rect_x, rect_y, 'o', picker=5, color=self.color, markersize = 8)
            self.pt = pt
        
    
    def del_shot(self):
        try:
            self.pt.remove()
        except ValueError:
            # print("ignore shot")
            pass


class DynamicPlotThread(Thread):
    def __init__(self, radar_sheet, objects):
        Thread.__init__(self)
        self.radar_sheet = radar_sheet
        self.objects = objects

        self.shots = []

        self.runtimes = 0

    def run(self):
        while True:
            if len(self.objects)>0:
                self.runtimes += 1

                for ishot in self.shots:
                    ishot["shot shot"].del_shot()
                
                draw_cnt = 0
                while True:
                    self.radar_sheet.fig.canvas.draw()
                    time.sleep(0.5)
                    draw_cnt+=1
                    if draw_cnt >= 10:
                        break

                time.sleep(1)
                
                for iobject in self.objects:
                    print("creat new shot")
                    jobject = iobject
                    jobject["shot shot"] = radar_shot(self.radar_sheet, jobject["x"], jobject["y"], jobject["x"], jobject["y"])
                    self.shots.append(jobject)
                
                self.objects.clear()

                draw_cnt = 0
                while True:
                    self.radar_sheet.fig.canvas.draw()
                    time.sleep(0.5)
                    draw_cnt+=1
                    if draw_cnt >= 20:
                        break

                localtime = time.localtime()
                once_run_radar_origin_data_log_folder = data_file_path_list["radar_box_statistics_path"]+"/"+ re.sub('[-]', '_', str(time.strftime("%Y-%m-%d", localtime)))
                if os.path.exists(once_run_radar_origin_data_log_folder)==False:
                    os.mkdir(once_run_radar_origin_data_log_folder)
                
                once_run_statistics_folder_path = once_run_radar_origin_data_log_folder+"/"+re.sub('[:]', '_', str(time.strftime("%H:%M:%S", localtime)))
                if os.path.exists(once_run_statistics_folder_path)==False:
                    os.mkdir(once_run_statistics_folder_path)

                once_run_statistics_pic_path = once_run_statistics_folder_path+"/"+"radar_box_statistics.png"

                pic_collections_path = data_file_path_list["radar_box_statistics_path"]+"/"+ "pic_collections"
                if os.path.exists(pic_collections_path)==False:
                    os.mkdir(pic_collections_path)
                
                pic_collections_item_path = pic_collections_path+"/"+re.sub('[-]', '_', str(time.strftime("%Y-%m-%d", localtime)))+"_"+re.sub('[:]', '_', str(time.strftime("%H:%M:%S", localtime)))+".png"

                self.radar_sheet.save_fig(once_run_statistics_pic_path)
                self.radar_sheet.save_fig(pic_collections_item_path)

                # once_run_statistics_filter_areas_data_json_path = once_run_statistics_folder_path+"/"+"filter_areas_data.json"

                # while DynamicPlotThread_state_dict["draw shot"]==False:
                #     time.sleep(0.5)

            time.sleep(0.5)



socket_client_ulimit = 30
socket_client_rcv_timeout = 360
socket_port = 5001

sockets = []
mysockets = []

def mysocket_monitor():
    mysocketmonitorfile = open('mysocketmonitor.txt', 'w')
    length = len(threading.enumerate())
    mysocketmonitorfile.write('thread count: ' + str(length) + '\n')
    mysocketmonitorfile.write('client count: ' + str(len(sockets)) + '\n\n')
    mysocketmonitorfile.write('client list:\n')
    socketlistcount = 0
    for isocket in sockets:
        socketlistcount += 1
        mysocketmonitorfile.write('[' + str(socketlistcount) + ']' + str(isocket) + '\n\n')
    mysocketmonitorfile.close()

def sendMsg(client_socket):
    while True: 
        if len(sendmsglist)>0:
            send_buf = sendmsglist.pop()
            send_buf = send_buf.encode("utf-8")
            try:
                client_socket.send(send_buf)
            except (BrokenPipeError, OSError):
                print('sendMsg() remove socket')
                if client_socket in sockets:
                    sockets.remove(client_socket)
                for item_sock in mysockets:
                    if item_sock['socket']==client_socket:
                        mysockets.remove(item_sock)
                if client_socket.fileno()!=-1:
                    client_socket.shutdown(2)
                    client_socket.close()
                # mysocket_monitor()
                gc.collect()
                break
            except:
                print('unknow exception')
                if client_socket in sockets:
                    sockets.remove(client_socket)
                for item_sock in mysockets:
                    if item_sock['socket']==client_socket:
                        mysockets.remove(item_sock)
                if client_socket.fileno()!=-1:
                    client_socket.shutdown(2)
                    client_socket.close()
                # mysocket_monitor()
                gc.collect()
                break
        else:
            time.sleep(0.2)


def readMsg(client_socket, access_date, access_time, radar_data_list):
    msg_count = 0
    rcv_buf = bytes()
    read_posi = 0

    radar_head_mark = "data_statistics:".encode()
    radar_tail_mark = "end".encode()
    
    while True:
        try:
            recv_data = client_socket.recv(65536)
            # print(f"recv_data len={len(recv_data)}")
            # print(f"recv_data={recv_data}")
        except ConnectionResetError:
            print('readMsg(1) remove socket')
            if client_socket in sockets:
                sockets.remove(client_socket)
            for item_sock in mysockets:
                if item_sock['socket']==client_socket:
                    if item_sock in mysockets:
                        mysockets.remove(item_sock)
            if client_socket.fileno()!=-1:
                client_socket.shutdown(2)
                client_socket.close()
            # mysocket_monitor()
            gc.collect()
            break
        except OSError:
            print('readMsg(2) remove socket')
            if client_socket in sockets:
                sockets.remove(client_socket)
            for item_sock in mysockets:
                if item_sock['socket']==client_socket:
                    if item_sock in mysockets:
                        mysockets.remove(item_sock)
            if client_socket.fileno()!=-1:
                client_socket.shutdown(2)
                client_socket.close()
            # mysocket_monitor()
            gc.collect()
            break
        except:
            print("unknow exception")

        if len(recv_data) > 0:
            for item_sock in mysockets:
                if item_sock['socket']==client_socket:
                    item_sock['rcvtimeouttimer']=0
            msg_count += 1
            rcv_buf += recv_data
            # client_socket.send(recv_data)
            read_len=0
            try:
                while read_len<len(recv_data):
                    # print(f"read_posi={read_posi}")
                    radar_head_posi = rcv_buf[read_posi:].find(radar_head_mark)
                    radar_tail_posi = rcv_buf[read_posi+radar_head_posi:].find(radar_tail_mark)
                    # print(f"radar_head_posi={radar_head_posi}")
                    # print(f"radar_tail_posi={radar_tail_posi}")
                    if radar_head_posi != -1 and radar_tail_posi != -1:
                        radar_data_frame_head = radar_head_posi
                        radar_data_frame_tail = radar_tail_posi

                        objects_data_len = radar_tail_posi - (radar_head_posi+len("data_statistics:"))
                        radar_data_frame_tail += len(radar_tail_mark)
                        print(f"objects_data_len={objects_data_len}")
                        objects_count = objects_data_len/8

                        objects_data = rcv_buf[read_posi+radar_head_posi+len("data_statistics:"):read_posi+radar_tail_posi]
                        
                        read_counter = 0
                        
                        try:
                            while read_counter < objects_count:
                                object_xy = {}
                                object_xy["x"] = struct.unpack(">i", objects_data[read_counter*8 : read_counter*8+4])[0]
                                object_xy["y"] = struct.unpack(">i", objects_data[read_counter*8+4 : read_counter*8+8])[0]
                                radar_data_list.append(object_xy)
                                read_counter+=1
                                print(f"read_counter={read_counter}")
                            print(f"radar_data_list={radar_data_list}")
                            # print(type(radar_data_frame))
                        except:
                            print("unpack error")
                            print("Unexpected error:", sys.exc_info()[0])
                            pass
                        read_posi += radar_data_frame_tail-radar_data_frame_head

                        read_len += (radar_data_frame_tail-radar_data_frame_head)

                    elif radar_head_posi == -1:
                        # print("radar_head_posi error")
                        read_posi = len(rcv_buf)
                        break
                    elif radar_tail_posi == -1:
                        # print("continue recv...\n")
                        break
                    else:
                        print("other\n")

            except UnicodeDecodeError:
                # mysocketlog.write("recv_data is not 'utf-8'\n")
                print("recv_data is not 'utf-8'\n")
        else:
            print('readMsg(2) client disconnect, remove socket')
            if client_socket in sockets:
                sockets.remove(client_socket)
            for item_sock in mysockets:
                if item_sock['socket']==client_socket:
                    if item_sock in mysockets:
                        mysockets.remove(item_sock)
            if client_socket.fileno()!=-1:
                client_socket.shutdown(2)
                client_socket.close()
            # mysocket_monitor()
            gc.collect()
            break


def socktimer(client_socket):
    notimeout = True
    while notimeout:
        time.sleep(1)
        nofind = 1
        for item_sock in mysockets:
            if item_sock['socket']==client_socket:
                nofind = 0
                item_sock['rcvtimeouttimer']+=1
                if item_sock['rcvtimeouttimer'] >= socket_client_rcv_timeout:
                    print('rcv timeout, remove socket')
                    if item_sock['socket'].fileno()!=-1:
                        item_sock['socket'].shutdown(2)
                        item_sock['socket'].close()
                    if item_sock in mysockets:
                        mysockets.remove(item_sock)
                    notimeout = False
                    gc.collect()
        if nofind==1:
            notimeout = False
            gc.collect()
            break

def monitor_test():
    while True:
        time.sleep(5)
        # length = len(threading.enumerate())
        # print('\nthread len='+str(length)+'\n')
        mysocket_monitor()


def tcp_creator(radar_data_list):

    time.sleep(2)

    t = Thread(target = monitor_test)
    t.start()

    mysocket_monitor()

    mysocket1 = ('', socket_port)
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(mysocket1)
    print('socket bind success')

    server_socket.listen()
    print('listen...')

    while True:
        if len(sockets) < socket_client_ulimit:
            client_socket,client_info = server_socket.accept()
            sockets.append(client_socket)
            
            print('\n---')
            # print(mysockets)
            print('new client:', client_info, 'fd=', client_socket.fileno())
            for item_sock in mysockets:
                if item_sock['socket'].getpeername()[0] == client_socket.getpeername()[0]:
                    print('remove')
                    item_sock['socket'].shutdown(2)
                    item_sock['socket'].close()
                    if item_sock in mysockets:
                        mysockets.remove(item_sock)
                    print(mysockets)
            

            localtime = time.localtime()
            localtimestr = time.strftime("%Y-%m-%d %H:%M:%S", localtime)

#            print('[new client][time: ' + localtimestr + ']' + ' [fd=' + str(client_socket.fileno()) + \
#                ', statistic: ' + str(len(sockets)) + '/' + str(socket_client_ulimit) + ']')

            access_date = re.sub('[-]', '_', str(time.strftime("%Y-%m-%d", localtime)))
            access_time = re.sub('[-]', '_', str(time.strftime("%H:%M:%S", localtime)))

            t = Thread(target = readMsg, args = (client_socket, access_date, access_time, radar_data_list))
            t.start()
            t = Thread(target = sendMsg, args = (client_socket,))
            t.start()

            mysocketitem = {'socket':client_socket, 'rcvtimeouttimer':0}
            mysockets.append(mysocketitem)

            t = Thread(target = socktimer, args = (client_socket,))
            t.start()
            print(mysockets)

            length = len(threading.enumerate())
            print('thread count='+str(length))
            print('client count=' + str(len(sockets))+'\n')

            mysocket_monitor()
        else:
            time.sleep(2)

if __name__ == '__main__':

    # 创建 tkinter 窗口
    radar_tk_window = tk.Tk()
    radar_tk_window.title("radar collect tool")

    win_screen_high = radar_tk_window.winfo_screenheight()
    win_screen_width = radar_tk_window.winfo_screenwidth()
    screen_size_str = str(int(win_screen_width/2))+"x"+str(int(win_screen_high/2))
    radar_tk_window.geometry(screen_size_str)
    try:
        radar_tk_window.iconbitmap("logo.ico")
    except:
        print("Unexpected error:", sys.exc_info()[0])

    radar_collect_config_json_default = {
        "radar_sheet_config":{
            "radar_normal_angel": 90,
            "radar_theta": 120,
            "radar_distance": 800,
            "radar_sheet_dis_reso": 36,
            "radar_filter_area_reso": 108
        },
        "radar_scan_config": {
            "interval_time": 5
        }
    }

    localtime = time.localtime()
    radar_log_folder = 'radar_logs_' + re.sub('[-]', '_', str(time.strftime("%Y-%m-%d", localtime)))

    my_radar_config_folder = "data/configs"
    my_radar_logs_folder = "data/logs"
    my_radarbox_logs_folder = "data/radarbox_logs"
    if os.path.exists('data')==False:
        os.mkdir('data')

    if os.path.exists(my_radar_config_folder)==False:
        os.mkdir(my_radar_config_folder)
    if os.path.exists(my_radar_logs_folder)==False:
        os.mkdir(my_radar_logs_folder)
    if os.path.exists(my_radarbox_logs_folder)==False:
        os.mkdir(my_radarbox_logs_folder)
    
    

    data_file_path_list["log_once_run_log_folder_path"] = my_radar_logs_folder

    data_file_path_list["config_filter_areas_data_json_path"] = my_radar_config_folder+"/"+"config_filter_areas_data.json"

    data_file_path_list["config_radar_collect_config_json_path"] = my_radar_config_folder+"/"+"config_radar_collect_config.json"

    data_file_path_list["radar_box_statistics_path"] = my_radarbox_logs_folder
    


    radar_collect_config_json = {}
    try:
        with open(data_file_path_list["config_radar_collect_config_json_path"], 'r') as f:
            radar_collect_config_json = json.load(f)
    except:
        with open(data_file_path_list["config_radar_collect_config_json_path"], 'w') as f:
            json.dump(radar_collect_config_json_default, f, indent=4)
        with open(data_file_path_list["config_radar_collect_config_json_path"], 'r') as f:
            radar_collect_config_json = json.load(f)
    
    radar_sheet_config = {}
    if "radar_sheet_config" in radar_collect_config_json:
        radar_sheet_config = radar_collect_config_json["radar_sheet_config"]
    for item in radar_collect_config_json_default["radar_sheet_config"]:
        if item not in radar_sheet_config:
            print(colorama.Fore.YELLOW+"missing "+item+" in "+data_file_path_list["config_radar_collect_config_json_path"]+"->radar_sheet_config")
            print(colorama.Style.RESET_ALL)
            # radar_collect_config_json = radar_collect_config_json_default
            radar_sheet_config = radar_collect_config_json_default["radar_sheet_config"]
            break
    
    radar_scan_config = {}
    if "radar_scan_config" in radar_collect_config_json:
        radar_scan_config = radar_collect_config_json["radar_scan_config"]
    for item in radar_collect_config_json_default["radar_scan_config"]:
        if item not in radar_scan_config:
            print(colorama.Fore.YELLOW+"missing "+item+" in "+data_file_path_list["config_radar_collect_config_json_path"]+"->radar_scan_config")
            print(colorama.Style.RESET_ALL)
            # radar_collect_config_json = radar_collect_config_json_default
            radar_scan_config = radar_collect_config_json_default["radar_scan_config"]
            break
    
    radar_collect_config_json["radar_sheet_config"] = radar_sheet_config
    radar_collect_config_json["radar_scan_config"] = radar_scan_config
    print(f"radar_collect_config_json={radar_collect_config_json}")


    radar_sheet1 = radar_sheet(
        radar_tk_window, 
        "rect", 
        radar_sheet_config["radar_normal_angel"], 
        radar_sheet_config["radar_theta"], 
        radar_sheet_config["radar_distance"], 
        radar_sheet_config["radar_sheet_dis_reso"], 
        radar_sheet_config["radar_filter_area_reso"], 
        radar_scan_config["interval_time"])
    
    plt.title('swqz 60GHz radarbox collect')

    radar_original_data = [
        
    ]

    t = Thread(target = tcp_creator, args = (radar_original_data, ))
    t.start()

    statistics = []

    objects = []



    dynamic_plot = DynamicPlotThread(radar_sheet1, radar_original_data)
    dynamic_plot.start()


    tk.mainloop()

    os._exit(0)