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
}

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
            if DynamicPlotThread_state_dict["draw shot"]==False:
                self.objects.clear()

                if len(DynamicPlotThread_msg_list)>0:
                    msg = DynamicPlotThread_msg_list.pop()
                    if msg["type"] == "clear all shots":
                        for ishot in self.shots:
                            if ishot["shot status"]==1:
                                    ishot["shot time"] = 0
                                    ishot["shot status"] = 0
                                    ishot["shot shot"].del_shot()
            
                self.radar_sheet.fig.canvas.draw()
                while DynamicPlotThread_state_dict["draw shot"]==False:
                    self.objects.clear()
                    time.sleep(0.5)
                self.objects.clear()

            self.runtimes += 1
            
            for iobject in self.objects:
                modify_mark = 0
                new_mark = 0
                shot_counter = 0
                if len(self.shots) > 0:
                    for ishot in self.shots:
                        if ishot["shot_id"] != iobject["id"]:
                            shot_counter += 1
                        else:
                            ishot_index = self.shots.index(ishot)
                    if shot_counter >= len(self.shots):
                        new_mark = 1
                    else:
                        modify_mark = 1
                    
                    if new_mark:
                        # print("new_mark")
                        jobject = iobject
                        jobject["shot_id"] = iobject["id"]
                        jobject["shot status"] = 1
                        jobject["shot time"] = 0
                        jobject["shot shot"] = radar_shot(self.radar_sheet, jobject["polar_theta"], jobject["polar_r"], jobject["rect_x"], jobject["rect_y"])
                        self.shots.append(jobject)
                    elif modify_mark:
                        # print("modify_mark")

                        # print(f"ishot_index={ishot_index}")
                        self.shots[ishot_index]["id"] = iobject["id"]
                        self.shots[ishot_index]["polar_theta"] = iobject["polar_theta"]
                        self.shots[ishot_index]["polar_r"] = iobject["polar_r"]
                        self.shots[ishot_index]["rect_x"] = iobject["rect_x"]
                        self.shots[ishot_index]["rect_y"] = iobject["rect_y"]
                        self.shots[ishot_index]["speed"] = iobject["speed"]
                        self.shots[ishot_index]["dis_reso"] = iobject["dis_reso"]

                        self.shots[ishot_index]["shot status"] = 1
                        self.shots[ishot_index]["shot time"] = 0

                        self.shots[ishot_index]["shot shot"].newlocation(self.shots[ishot_index]["polar_theta"], self.shots[ishot_index]["polar_r"], self.shots[ishot_index]["rect_x"], self.shots[ishot_index]["rect_y"])
                else:
                    print("creat new shot")
                    jobject = iobject
                    jobject["shot_id"] = iobject["id"]
                    jobject["shot status"] = 1
                    jobject["shot time"] = 0
                    jobject["shot shot"] = radar_shot(self.radar_sheet, jobject["polar_theta"], jobject["polar_r"], jobject["rect_x"], jobject["rect_y"])
                    self.shots.append(jobject)
            
            self.objects.clear()
            # if len(self.shots) > 0:
            #     for ishot in self.shots:
            #         if ishot["shot time"]<1:
            #             print(ishot)
            #     print("")
            
            
            for ishot in self.shots:
                if ishot["shot status"]==1:
                    ishot["shot time"] += 1
                    if ishot["shot time"] >= 3:
                        ishot["shot time"] = 0
                        ishot["shot status"] = 0
                        ishot["shot shot"].del_shot()
            
            if len(DynamicPlotThread_msg_list)>0:
                msg = DynamicPlotThread_msg_list.pop()
                if msg["type"] == "clear all shots":
                    for ishot in self.shots:
                        if ishot["shot status"]==1:
                                ishot["shot time"] = 0
                                ishot["shot status"] = 0
                                ishot["shot shot"].del_shot()
            
            self.radar_sheet.fig.canvas.draw()

            # while DynamicPlotThread_state_dict["draw shot"]==False:
            #     time.sleep(0.5)

            time.sleep(0.5)



socket_client_ulimit = 30
socket_client_rcv_timeout = 360
socket_port = 5000

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

# radar_head_mark = b'\xAA\xFF\x03\x00'
# radar_tail_mark = b'\x55\xCC'
radar_head_mark = bytes([0x4d, 0x62])
radar_tail_mark = bytes([0x4a])

radar_cmd_head_mark = bytes([0xfd, 0xfc, 0xfb, 0xfa])
radar_cmd_tail_mark = bytes([4, 3, 2, 1])
def readMsg(client_socket, access_date, access_time, radar_data_list):
    msg_count = 0
    rcv_buf = bytes()
    read_posi = 0
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
                        radar_data_frame_tail = radar_tail_posi+len(radar_tail_mark)
                        
                        # print(f"read_posi={read_posi}")
                        # radar_data_frame = struct.unpack(str(radar_data_frame_tail-radar_data_frame_head)+"B", rcv_buf[read_posi+radar_data_frame_head:read_posi+radar_data_frame_tail])
                        try:
                            radar_data_frame = struct.unpack(str(radar_data_frame_tail-radar_data_frame_head)+"B", rcv_buf[read_posi+radar_data_frame_head:read_posi+radar_data_frame_tail])
                            # print(type(radar_data_frame))
                        except:
                            print("unpack error")
                            read_posi = len(rcv_buf)
                            print("Unexpected error:", sys.exc_info()[0])
                            pass
                        # print(f"read_posi={read_posi}")
                        read_posi += radar_data_frame_tail-radar_data_frame_head
                        # print(f"radar_data_frame={radar_data_frame}")

                        radar_data_frame_dict = {}
                        radar_data_frame_dict["radar_model"] = "ld6001"
                        radar_data_frame_dict["data"] = list(radar_data_frame)
                        radar_data_list.append(radar_data_frame_dict)


                        read_len += len(radar_data_frame)

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

#input: 补码值(16进制或者十进制具可)
#output: 原码值(十进制)
#支持两个字节输入，若支持更多字节, 0x800后补00到字节长度, 0xFFFF后补FF到字节长度
def get_char_hex_data_abs( hex_data ):
	if (hex_data & 0x80 == 0x80):
		return -((hex_data-1) ^ 0xFF)
	else:
		return hex_data


def radar_computer_ld6001(data_in):
    objects = [
        {"radar_model":"ld6001", "id":1, "rect_x":10, "rect_y":10, "speed":40, "dis_reso":75},
        {"radar_model":"ld6001", "id":2, "rect_x":10, "rect_y":20, "speed":50, "dis_reso":75}
    ]

    radar_objects_data = []

    data_in_data = data_in["data"]

    objects_number = data_in_data[5]

    radar_objects = []

    print(f"objects_number={objects_number}")

    if len(data_in_data)>=objects_number*8+14:

        if objects_number > 0:
            for item in range(0, objects_number):
                radar_objects_data.append(data_in_data[12+item*8:12+8+item*8])

            for radar_object in radar_objects_data:
                radar_object_dict = {}
                radar_object_dict["radar_model"] = "ld6001"
                radar_object_dict["id"] = radar_object[0]
                radar_object_dict["distance"]  = radar_object[1]
                radar_object_dict["pitch_angel"]  = radar_object[2]
                radar_object_dict["horizontal_angle"]  = radar_object[3]
                radar_object_dict["rect_x"] = radar_object[6]
                # if radar_object_dict["rect_x"]&int('10000000', 2):
                #     radar_object_dict["rect_x"] = ~(radar_object_dict["rect_x"]-1)
                radar_object_dict["rect_x"] = get_char_hex_data_abs(radar_object_dict["rect_x"])
                radar_object_dict["rect_x"] = radar_object_dict["rect_x"]*10
                radar_object_dict["rect_y"] = radar_object[7]*10
                radar_object_dict["speed"] = 0
                radar_object_dict["dis_reso"] = 10
                polar_posi = Rectangular_to_Polar(radar_object_dict["rect_x"], radar_object_dict["rect_y"])
                radar_object_dict["polar_r"]  = polar_posi[0]
                radar_object_dict["polar_theta"]  = polar_posi[1]
                
                
                radar_objects.append(radar_object_dict)
            print(f"radar_objects={radar_objects}")
        else:
            pass
    return radar_objects


def radar_data_analyse(data_in, data_out):
    while(True):
        if button_state_list["exit"]==False:
            if len(data_in) > 0:

                if button_state_list["json record"]==True:
                    # print(f"len(data_in)={len(data_in)}")
                    localtime = time.localtime()
                    once_run_radar_origin_data_log_folder = data_file_path_list["log_once_run_log_folder_path"]+"/"+ re.sub('[-]', '_', str(time.strftime("%Y-%m-%d", localtime)))
                    if os.path.exists(once_run_radar_origin_data_log_folder)==False:
                        os.mkdir(once_run_radar_origin_data_log_folder)
                    
                    radar_origin_data_name = 'radar_origin_data.json'
                    once_run_radar_origin_data_log_path = once_run_radar_origin_data_log_folder+"/"+radar_origin_data_name
                    radar_data_json = []
                    try:
                        with open(once_run_radar_origin_data_log_path, 'r') as f:
                            radar_data_json = json.load(f)
                    except:
                        print("ignore")

                    objects_data_item = {}
                    for idata_in in data_in:
                        radar_data_list = radar_computer_ld6001(idata_in)
                        # print(f"radar_data_list={radar_data_list}")
                        localtime = time.localtime()
                        localtimestr = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
                        objects_data_item["time"]=localtimestr
                        objects_data_item["data"]=radar_data_list
                        radar_data_json.append(objects_data_item)
                    
                    with open(once_run_radar_origin_data_log_path, 'w') as f:
                        json.dump(radar_data_json, f, indent=4)
                else:
                    pass

                data_in_1 = data_in.pop()
                if len(data_in_1["data"]) > 0:
                    print(f"data_in_1={data_in_1['data']}")
                    data_in.clear()
                    radar_data_list = radar_computer_ld6001(data_in_1)
                    # print(f"radar_data_list={radar_data_list}")
                    for i_data in radar_data_list:
                        data_out.append(i_data)

                        if button_state_list["scan"]==True:
                            cur_shots_list.append(radar_data_list)
                    # print(f"data_out={data_out}")
            else:
                time.sleep(0.2)
        else:
            time.sleep(0.2)

def query_filter_area(radar_sheet):
    # for i in radar_sheet.scan_rect_xy_list:
    #     radar_sheet.rect_filter_move("area", i[0], i[1])
    while True:
        if len(radar_msg_list) > 0:
            radar_cmd_msg = radar_msg_list.pop()
            # print(f"radar_cmd_msg={radar_cmd_msg}")

            radar_cmd_msg_bytes = bytes(radar_cmd_msg)

            if radar_cmd_msg_bytes[6]==0xc1:

                area_filter_data = []

                filter_type = radar_cmd_msg_bytes[10]
                print(f"filter_type={filter_type}")
                area_filter_data.append(radar_cmd_msg_bytes[12:12+8])
                area_filter_data.append(radar_cmd_msg_bytes[12+8:12+8+8])
                area_filter_data.append(radar_cmd_msg_bytes[12+8+8:12+8+8+8])

                area_filter_xy = []

                for item in area_filter_data:
                    area_filter_item = {}
                    area_filter_item["area1_sx"] = struct.unpack("h", item[0:2])[0]/10
                    area_filter_item["area1_sy"] = struct.unpack("h", item[2:4])[0]/10
                    area_filter_item["area1_ex"] = struct.unpack("h", item[4:6])[0]/10
                    area_filter_item["area1_ey"] = struct.unpack("h", item[6:8])[0]/10
                    area_filter_xy.append(area_filter_item)
                # print(f"area_filter_xy={area_filter_xy}")

                if radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name("test_scan")) == True:
                    radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name("test_scan"))

                rect_number = 1
                for item in area_filter_xy:
                    rect_name = "area"+str(rect_number)
                    rect_number+=1
                    item_rect = [item["area1_sx"], item["area1_sy"], item["area1_ex"], item["area1_ey"]]
                    
                    if filter_type == 1:
                        if radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name(rect_name), item_rect, fc="green") == False:
                            radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name(rect_name), item_rect, fc="green")
                    elif filter_type == 2:
                        if radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name(rect_name), item_rect, fc="red") == False:
                            radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name(rect_name), item_rect, fc="red")
                    elif filter_type == 0:
                        if radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name(rect_name), item_rect, fc="gray") == False:
                            radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name(rect_name), item_rect, fc="gray")
                    else:
                        pass
        elif len(query_filter_area_msg_list) > 0:
            msg = query_filter_area_msg_list.pop()

            if msg["type"] == "clear":
                for rect_number in range(1, 4):
                    rect_name = "area"+str(rect_number)
                    radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name(rect_name))
        else:
            time.sleep(0.2)

def filter_area_select(radar_sheet):
    runtimes = 0
    # print(f"radar_sheet.scan_rect_xy_list={radar_sheet.scan_rect_xy_list}")

    print("start scan...")
    areas_counts = len(radar_sheet.scan_rect_xy_list)

    areas_counter = -1

    time.sleep(2)

    filter_areas_data_json = []
    try:
        with open(data_file_path_list["config_filter_areas_data_json_path"], 'r') as f:
            filter_areas_data_json = json.load(f)
    except:
        print("ignore")
    else:
        for item in filter_areas_data_json:
            radar_sheet.scan_area_order_rect_move("scan_area_order", item)

    while True:
        if len(next_af_msg_list)>0:
            msg = next_af_msg_list.pop()

            if filter_scan_func_state["scan_state"]!=True:
                sel_area_item = []
                if msg["type"] == "any":
                    msg_posi = msg["posi"]
                    sel_area_item.append(msg_posi["x1y1"][0])
                    sel_area_item.append(msg_posi["x1y1"][1])
                    sel_area_item.append(msg_posi["x3y3"][0])
                    sel_area_item.append(msg_posi["x3y3"][1])

                    # print(f"sel_area_item={sel_area_item}")
                    # print(f"msg['type']={msg['type']}")

                    if button_state_list["fsm"] == "ss":
                        print("ss")
                        rect_xy13 = [msg_posi["x1y1"][0], msg_posi["x1y1"][1], msg_posi["x3y3"][0], msg_posi["x3y3"][1]]

                        for rect_number in range(1, 4):
                            rect_name = "area"+str(rect_number)
                            radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name(rect_name))

                        if rect_xy13 in test_ss_area_list:
                            test_ss_area_list.remove(rect_xy13)
                            if radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name("test_scan"), rect_xy13) == True:
                                radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name("test_scan"), rect_xy13)
                            scan_areas = []
                        else:
                            if len(test_ss_area_list)>0:
                                    test_ss_area_list.clear()
                                    if radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name("test_scan"), rect_xy13) == True:
                                        radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name("test_scan"), rect_xy13)
                                    radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name("test_scan"), rect_xy13)
                                    test_ss_area_list.append(rect_xy13)
                                    scan_areas = []
                                    scan_areas.append(sel_area_item)
                            
                            else:
                                if radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name("test_scan"), rect_xy13) == False:
                                    radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name("test_scan"), rect_xy13)
                                test_ss_area_list.append(rect_xy13)
                                scan_areas = []
                                scan_areas.append(sel_area_item)
                    elif button_state_list["fsm"] == "fs":
                        print("fs")
                        filter_areas_data_json = []
                        try:
                            with open(data_file_path_list["config_filter_areas_data_json_path"], 'r') as f:
                                filter_areas_data_json = json.load(f)
                        except:
                            print("ignore")

                        if sel_area_item not in filter_areas_data_json:
                            filter_areas_data_json.append(sel_area_item)
                        else:
                            filter_areas_data_json.remove(sel_area_item)
                        radar_sheet.scan_area_order_rect_move("scan_area_order", sel_area_item)

                        
                        with open(data_file_path_list["config_filter_areas_data_json_path"], 'w') as f:
                            json.dump(filter_areas_data_json, f, indent=4)
                        pass
                    elif button_state_list["fsm"] == "fss":
                        print("fss")
                        is_new_rect = 1
                        for item in selected_scan_area_list[:]:
                            if sel_area_item == item["area_rect_device"]:
                                is_new_rect = 0
                                radar_sheet.selected_area_rect_move("selected_area_rect", sel_area_item)
                                selected_scan_area_list.remove(item)

                        if is_new_rect:
                            if len(selected_scan_area_list)<3:
                                selected_scan_area_list_item = {}
                                selected_scan_area_list_item["area_rect_device"] = sel_area_item
                                selected_scan_area_list_item["area_rect_show"] = {}
                                selected_scan_area_list_item["area_rect_show"]["x1"] = msg_posi["x1y1"][0]
                                selected_scan_area_list_item["area_rect_show"]["y1"] = msg_posi["x1y1"][1]
                                selected_scan_area_list_item["area_rect_show"]["x2"] = msg_posi["x3y3"][0]
                                selected_scan_area_list_item["area_rect_show"]["y2"] = msg_posi["x3y3"][1]
                                selected_scan_area_list_item["area_name"] = \
                                str(selected_scan_area_list_item["area_rect_show"]["x1"])+"_"+\
                                str(selected_scan_area_list_item["area_rect_show"]["y1"])+"_"+\
                                str(selected_scan_area_list_item["area_rect_show"]["x2"])+"_"+\
                                str(selected_scan_area_list_item["area_rect_show"]["y2"])
                                selected_scan_area_list.append(selected_scan_area_list_item)

                                radar_sheet.selected_area_rect_move("selected_area_rect", sel_area_item)

                    elif button_state_list["fsm"] == "fsf":
                        print("fsf")
                        is_new_rect = 1
                        for item in filtered_scan_area_list[:]:
                            if sel_area_item == item["area_rect_device"]:
                                is_new_rect = 0
                                radar_sheet.filtered_area_rect_move("filtered_area_rect", sel_area_item)
                                filtered_scan_area_list.remove(item)
                        
                        if is_new_rect:
                            if len(filtered_scan_area_list)<3:
                                filtered_scan_area_list_item = {}
                                filtered_scan_area_list_item["area_rect_device"] = sel_area_item
                                filtered_scan_area_list_item["area_rect_show"] = {}
                                filtered_scan_area_list_item["area_rect_show"]["x1"] = msg_posi["x1y1"][0]
                                filtered_scan_area_list_item["area_rect_show"]["y1"] = msg_posi["x1y1"][1]
                                filtered_scan_area_list_item["area_rect_show"]["x2"] = msg_posi["x3y3"][0]
                                filtered_scan_area_list_item["area_rect_show"]["y2"] = msg_posi["x3y3"][1]
                                filtered_scan_area_list_item["area_name"] = \
                                str(filtered_scan_area_list_item["area_rect_show"]["x1"])+"_"+\
                                str(filtered_scan_area_list_item["area_rect_show"]["y1"])+"_"+\
                                str(filtered_scan_area_list_item["area_rect_show"]["x2"])+"_"+\
                                str(filtered_scan_area_list_item["area_rect_show"]["y2"])

                                filtered_scan_area_list.append(filtered_scan_area_list_item)

                                radar_sheet.filtered_area_rect_move("filtered_area_rect", sel_area_item)

                    elif button_state_list["fsm"] == "off":
                        # print("off")
                        pass

                elif msg["type"] == "cfsm clear":
                    print("cfsm clear")
                    filter_areas_data_json = []
                    with open(data_file_path_list["config_filter_areas_data_json_path"], 'w') as f:
                        json.dump(filter_areas_data_json, f, indent=4)
                    radar_sheet.scan_area_order_rect_move_clear_all("scan_area_order")
                    pass

                elif msg["type"] == "clear ss":
                    radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name("test_scan"))
                    test_ss_area_list.clear()
                    pass
        else:
            time.sleep(0.2)

def filter_scan_func(radar_sheet, statistics):
    cover_count = 0
    total_shots_min = 0
    total_shots_max = 0
    total_shots_avg = 0
    exit_scan_mark = False
    exit_scan_hide_full = True
    total_avg_str = "--"
    while True:
        if len(filter_scan_func_msg_list)>0:
            msg = filter_scan_func_msg_list.pop()
            if msg["type"] == "show track":
                print("show track")
                filter_areas_data_json = []
                try:
                    with open(data_file_path_list["config_filter_areas_data_json_path"], 'r') as f:
                        filter_areas_data_json = json.load(f)
                except:
                    print("ignore")
                for item in filter_areas_data_json:
                    radar_sheet.rect_filter_move_show_track("show track", item[0], item[1], item[2], item[3])
                    time.sleep(1)
                radar_sheet.rect_filter_move_show_track("show track", 0, 0, 0, 0)
            if msg["type"] == "scan track":
                filter_scan_func_state["scan_state"] = True
                exit_scan_mark = False
                exit_scan_hide_full = True
                cover_count = 0
                total_shots_min = 0
                total_shots_max = 0
                total_shots_avg = 0
                radar_sheet.statistics_label.config(text = radar_sheet.statistics_label_default)
                while True:
                    print("scan track")
                    filter_areas_data_json = []
                    try:
                        with open(data_file_path_list["config_filter_areas_data_json_path"], 'r') as f:
                            filter_areas_data_json = json.load(f)
                    except:
                        print("ignore")
                    
                    if len(filter_areas_data_json)==0:
                        print("len(filter_areas_data_json)==0, break")
                        filter_scan_func_state["scan_state"] = False
                        break

                    sync_pause_scan_button(True)

                    localtime = time.localtime()
                    once_run_radar_origin_data_log_folder = data_file_path_list["log_once_run_log_folder_path"]+"/"+ re.sub('[-]', '_', str(time.strftime("%Y-%m-%d", localtime)))
                    if os.path.exists(once_run_radar_origin_data_log_folder)==False:
                        os.mkdir(once_run_radar_origin_data_log_folder)
                    
                    once_run_statistics_folder_path = once_run_radar_origin_data_log_folder+"/"+re.sub('[:]', '_', str(time.strftime("%H:%M:%S", localtime)))
                    if os.path.exists(once_run_statistics_folder_path)==False:
                        os.mkdir(once_run_statistics_folder_path)

                    once_run_statistics_json_path = once_run_statistics_folder_path+"/"+"statistics.json"
                    once_run_statistics_pic_path = once_run_statistics_folder_path+"/"+"statistics.png"

                    once_run_statistics_filter_areas_data_json_path = once_run_statistics_folder_path+"/"+"filter_areas_data.json"

                    with open(once_run_statistics_filter_areas_data_json_path, 'w') as f:
                        json.dump(filter_areas_data_json, f, indent=4)
                    
                    scan_data = {}
                    localtimestr = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
                    scan_data["start_time"]=localtimestr
                    scan_data["end_time"]="-"
                    scan_data["time_use"]="-"
                    scan_data["total shots"] = 0
                    scan_data["data"] = []
                    once_total_shots = 0

                    statistics.clear()
                    once_scan_start_timestamp = int(time.time())

                    show_shots_mark_list = []
                    for item in filter_areas_data_json:
                        while button_state_list["scan"]==False:
                            print("scan pause")
                            time.sleep(1)
                        scan_areas = []
                        scan_areas.append(item)
                        # radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name("test_scan"))
                        # sendmsglist.append("rfs")
                        # time.sleep(3)
                        if radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name("test_scan"), item) == False:
                            radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name("test_scan"), item)
                        test_ss_area_list.clear()
                        test_ss_area_list.append(item)
                        
                        # set_filter_area_packer(scan_areas, filtertype=1)
                        time.sleep(1)
                        # ------------------------------
                        scan_data_item = {}
                        localtime = time.localtime()
                        localtimestr = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
                        scan_data_item["start_time"]=localtimestr
                        scan_data_item["end_time"]="-"
                        scan_data_item["time_use"] = "-"
                        scan_data_item["filter_area"] = item
                        scan_data_item_start_timestamp = int(time.time())
                        cur_shots_list.clear()
                        time.sleep(radar_sheet.scan_interval_time)
                        rect_xy13 = []
                        rect_xy13.append(item[0])
                        rect_xy13.append(item[1])
                        rect_xy13.append(item[2])
                        rect_xy13.append(item[3])
                        max_shots = 0
                        print(f"cur_shots_list={cur_shots_list}")
                        
                        show_shots_mark = []
                        for item in cur_shots_list:
                            shot_counter = 0
                            for i_item in item:
                                if is_point_in_rect(i_item["rect_x"], i_item["rect_y"], rect_xy13):
                                    shot_counter+=1
                                if shot_counter>max_shots:
                                    max_shots = shot_counter
                                    show_shots_mark.append(i_item)
                                    
                        
                        for item in show_shots_mark:
                            shot_mark = radar_shot(radar_sheet, item["polar_theta"], item["polar_r"], item["rect_x"], item["rect_y"], shot_type="mark shot")
                            show_shots_mark_list.append(shot_mark)
                        show_shots_mark.clear()
                        print(f"len(show_shots_mark_list)={len(show_shots_mark_list)}")
                        print(f"show_shots_mark_list={show_shots_mark_list}")

                        cur_shots_list.clear()
                        scan_data_item["total_shots"] = max_shots
                        localtime = time.localtime()
                        localtimestr = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
                        scan_data_item["end_time"]=localtimestr
                        once_total_shots += scan_data_item["total_shots"]
                        scan_data_item_end_timestamp = int(time.time())
                        scan_data_item["time_use"] = scan_data_item_end_timestamp - scan_data_item_start_timestamp
                        scan_data["data"].append(scan_data_item)
                        print(f'scan_data_item={scan_data_item}')
                        print("")
                        # ------------------------------
                        if once_total_shots < total_shots_min:
                            total_shots_min = once_total_shots
                        if once_total_shots > total_shots_max:
                            total_shots_max = once_total_shots
                        show_label = "cover_count="+str(cover_count)+", " + \
                                "total_min="+str(total_shots_min)+", " + \
                                "total_max="+str(total_shots_max)+", " + \
                                total_avg_str
                        
                        radar_sheet.statistics_label.config(text = show_label)

                        time.sleep(1)
                    
                        if len(filter_scan_func_exit_msg_list) > 0:
                            exit_msg = filter_scan_func_exit_msg_list.pop()
                            if exit_msg["type"] == "exit scan":
                                if item != filter_areas_data_json[-1]:
                                    exit_scan_hide_full = False
                                exit_scan_mark = True
                                break
                    scan_data["total shots"] = once_total_shots
                    localtime = time.localtime()
                    localtimestr = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
                    scan_data["end_time"]=localtimestr
                    once_scan_end_timestamp = int(time.time())
                    scan_data["time_use"] = once_scan_end_timestamp-once_scan_start_timestamp
                    statistics.append(scan_data)
                    print(f"statistics={statistics}")
                    with open(once_run_statistics_json_path, 'w') as f:
                            json.dump(statistics, f, indent=4)

                    if exit_scan_hide_full == True:
                        radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name("test_scan"))
                        pass

                    cover_count+=1
                    if once_total_shots < total_shots_min:
                        total_shots_min = once_total_shots
                    if once_total_shots > total_shots_max:
                        total_shots_max = once_total_shots
                    
                    total_shots_total = 0.0
                    for item in statistics:
                        total_shots_total += item["total shots"]
                    total_shots_avg = total_shots_total/len(statistics)
                    total_avg_str = "total_avg="+str(total_shots_avg)

                    show_label = "cover_count="+str(cover_count)+", " + \
                                "total_min="+str(total_shots_min)+", " + \
                                "total_max="+str(total_shots_max)+", " + \
                                total_avg_str
                    
                    radar_sheet.statistics_label.config(text = show_label)
                    DynamicPlotThread_state_dict["draw shot"] = False
                    clear_shot_msg = {}
                    clear_shot_msg["type"] = "clear all shots"
                    DynamicPlotThread_msg_list.append(clear_shot_msg)
                    time.sleep(3)
                    radar_sheet.save_fig(once_run_statistics_pic_path)
                    time.sleep(1)

                    DynamicPlotThread_state_dict["draw shot"] = True

                    for item in show_shots_mark_list:
                        item.del_shot()
                    show_shots_mark_list.clear()

                    radar_sheet.test_area_rect_move(radar_sheet.mutex_rect_name("test_scan"))

                    try:
                        if msg["scan_type"]=="period":
                            
                            if exit_scan_mark == True:
                                filter_scan_func_state["scan_state"] = False
                                sync_pause_scan_button(False)
                                print("exit scan")
                                break
                            print("period scan...")
                            pass
                        else:
                            statistics.clear()
                            sync_pause_scan_button(False)
                            filter_scan_func_state["scan_state"] = False
                            print("scan once, break")
                            break
                    except(KeyError):
                        statistics.clear()
                        sync_pause_scan_button(False)
                        filter_scan_func_state["scan_state"] = False
                        print("KeyError, break")
                        break
            filter_scan_func_msg_list.clear()
            filter_scan_func_exit_msg_list.clear()

                    

        else:
            cur_shots_list.clear()
            time.sleep(0.5)


def radar_sheet_func(radar_sheet):
    while True:
        if len(radar_sheet_func_msg_list)>0:
            msg = radar_sheet_func_msg_list.pop()
            print(f"msg={msg}")
            if msg["type"] == "sector show":
                # radar_sheet_msg_dict["sector"] = True
                radar_sheet.show_sector()
            elif msg["type"] == "sector hide":
                # radar_sheet_msg_dict["sector"] = False
                radar_sheet.hide_sector()
        else:
            time.sleep(0.5)

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
    if os.path.exists('data')==False:
        os.mkdir('data')

    if os.path.exists(my_radar_config_folder)==False:
        os.mkdir(my_radar_config_folder)
    if os.path.exists(my_radar_logs_folder)==False:
        os.mkdir(my_radar_logs_folder)
    
    

    data_file_path_list["log_once_run_log_folder_path"] = my_radar_logs_folder

    data_file_path_list["config_filter_areas_data_json_path"] = my_radar_config_folder+"/"+"config_filter_areas_data.json"

    data_file_path_list["config_radar_collect_config_json_path"] = my_radar_config_folder+"/"+"config_radar_collect_config.json"


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
    
    plt.title('24GHz radar collect')

    radar_original_data = [
        {"radar_model":"ld6001", "data":[]}
    ]

    t = Thread(target = tcp_creator, args = (radar_original_data, ))
    t.start()

    t = Thread(target = query_filter_area, args = (radar_sheet1, ))
    t.start()

    statistics = [
        {
            "start_time":"2023-11-16:00:00:00",
            "end_time":"2023-11-16:00:00:00",
            "time_use":100,
            "total shots": 1,
            "data": [
                {"start_time":"2023-11-16:00:00:00", "end_time":"2023-11-16:00:00:00", "time_use":10, "filter_area":[0, 1, 2, 3], "total_shots":0},
                {"start_time":"2023-11-16:00:00:00", "end_time":"2023-11-16:00:00:00", "time_use":10, "filter_area":[4, 5, 6, 7], "total_shots":1}
            ],
        },
        {
            "start_time":"2023-11-16:00:00:00",
            "end_time":"2023-11-16:00:00:00",
            "time_use":100,
            "total shots": 2,
            "data": [
                {"start_time":"2023-11-16:00:00:00", "end_time":"2023-11-16:00:00:00", "time_use":10, "filter_area":[0, 1, 2, 3], "total_shots":1},
                {"start_time":"2023-11-16:00:00:00", "end_time":"2023-11-16:00:00:00", "time_use":10, "filter_area":[4, 5, 6, 7], "total_shots":1}
            ],
        },
    ]

    statistics = []

    t = Thread(target = filter_area_select, args = (radar_sheet1, ))
    t.start()

    t = Thread(target = radar_sheet_func, args = (radar_sheet1, ))
    t.start()

    t = Thread(target = filter_scan_func, args = (radar_sheet1, statistics))
    t.start()

    # objects = [
    #     {"radar_model":"ld6001", "id":1, "rect_x":100, "rect_y":200, "speed":40, "dis_reso":75},
    #     {"radar_model":"ld6001", "id":2, "rect_x":300, "rect_y":400, "speed":50, "dis_reso":75}
    # ]
    # objects = [
    #     {"radar_model":"ld6001", "id":1, "polar_r":100, "polar_theta":200, "speed":40, "dis_reso":75},
    #     {"radar_model":"ld6001", "id":2, "polar_r":300, "polar_theta":400, "speed":50, "dis_reso":75}
    # ]
    objects = []

    t = Thread(target = radar_data_analyse, args=(radar_original_data, objects))
    t.start()


    dynamic_plot = DynamicPlotThread(radar_sheet1, objects)
    dynamic_plot.start()

    tk_button(radar_tk_window, name = "exit", text="exit", width=len("exit"), height=1, b_x = 0, b_y = 0, callback=exit_button_callback)

    tk_button(radar_tk_window, name = "json record switch", text="json record off", width=len("json record off"), height=1, b_x = 180, b_y = 0, callback=json_record_button_callback)
    tk_button(radar_tk_window, name = "detect switch", text="detect off", width=len("detect off"), height=1, b_x = 350, b_y = 0, callback=detect_switch_button_callback)
    tk_button(radar_tk_window, name = "detect mode", text="detect m1", width=len("detect m1"), height=1, b_x = 450, b_y = 0, callback=detect_mode_button_callback)

    tk_button(radar_tk_window, name = "fsm", text="fsm:off", width=len("fsm:off"), height=1, b_x = 1200, b_y = 0, callback=fsm_button_callback)
    tk_button(radar_tk_window, name = "cfsm", text="dfsm", width=len("cfsm"), height=1, b_x = 1280, b_y = 0, callback=cfsm_button_callback)
    tk_button(radar_tk_window, name = "show trace", text="show trace", width=len("show trace"), height=1, b_x = 1320, b_y = 0, callback=show_track_button_callback)
    tk_button(radar_tk_window, name = "scan trace", text="scan trace", width=len("scan trace"), height=1, b_x = 1400, b_y = 0, callback=scan_track_button_callback)
    tk_button(radar_tk_window, name = "scan trace+", text="scan trace+", width=len("scan trace+"), height=1, b_x = 1490, b_y = 0, callback=scan_track_plus_button_callback)
    tk_button(radar_tk_window, name = "pause scan", text="pause scan", width=len("pause scan"), height=1, b_x = 1580, b_y = 0, callback=pause_scan_button_callback)
    tk_button(radar_tk_window, name = "exit scan", text="exit scan", width=len("exit scan"), height=1, b_x = 1660, b_y = 0, callback=exit_scan_button_callback)
    tk_button(radar_tk_window, name = "fsm_sm", text="fsm_sm:off", width=len("fsm_sm:off"), height=1, b_x = 1740, b_y = 0, callback=fsm_sm_button_callback)
    tk.mainloop()

    os._exit(0)