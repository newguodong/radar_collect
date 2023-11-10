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


button_msg_list = {"exit":False, "json record":False, "scan mode":"multi", "area1 filter":False, "area2 filter":False, "area3 filter":False}
button_dict = {}

sendmsglist=[]

radar_msg_list = []

next_af_msg_list = []

radar_sheet_grid_list = []

query_filter_area_msg_list = []

radar_sheet_func_msg_list = []
radar_sheet_msg_dict = {"sector":True}



def exit_button_callback():
    button_msg_list["exit"] = True
    time.sleep(1)
    os._exit(0)

def json_record_button_callback():
    if button_msg_list["json record"] == True:
        button_msg_list["json record"] = False
        button_dict["json record switch"]["text"] = "json record off"
    else:
        button_msg_list["json record"] = True
        button_dict["json record switch"]["text"] = "json record on"

def scan_mode_button_callback():
    print("scan mode button express once")
    if button_msg_list["scan mode"] == "multi":
        button_msg_list["scan mode"] = "single"
        button_dict["scan mode"]["text"] = "scan mode single"
        sendmsglist.append("trace single")
    else:
        button_msg_list["scan mode"] = "multi"
        button_dict["scan mode"]["text"] = "scan mode multi"
        sendmsglist.append("trace multi")

def filter_query_button_callback():
    print("filter query button express once")
    sendmsglist.append("query filter")

def set_filter_area_packer(areas, filtertype = 1):
    cmd_str = "set filter: "
    cmd_str += str(filtertype)+", "

    areas_pad_item = [0, 0, 0, 0]
    while len(areas)<3:
        areas.append(areas_pad_item)
    # print(f"areas={areas}")

    for item in areas:
        for xy in item:
            xy = xy*10
            cmd_str += str(xy)
            cmd_str += ", "
    cmd_str += "end"

    # print(f"cmd_str={cmd_str}")
    sendmsglist.append(cmd_str)
        

def set_filter_button_callback():
    print("set filter button express once")
    sendmsglist.append("set filter: 1, -2160, 3240, -1080, 4320, 0, 0, 0, 0, 0, 3240, 1080, 4320, end")

def area1_filter_button_callback():
    print("area1 filter button express once")
    if button_msg_list["area1 filter"] == True:
        button_msg_list["area1 filter"] = False
        button_dict["area1 filter"]["text"] = "area1 filter off"
    else:
        button_msg_list["area1 filter"] = True
        button_dict["area1 filter"]["text"] = "area1 filter on"

def area2_filter_button_callback():
    print("area2 filter button express once")
    if button_msg_list["area2 filter"] == True:
        button_msg_list["area2 filter"] = False
        button_dict["area2 filter"]["text"] = "area2 filter off"
    else:
        button_msg_list["area2 filter"] = True
        button_dict["area2 filter"]["text"] = "area2 filter on"

def area3_filter_button_callback():
    print("area3 filter button express once")
    if button_msg_list["area3 filter"] == True:
        button_msg_list["area3 filter"] = False
        button_dict["area3 filter"]["text"] = "area3 filter off"
    else:
        button_msg_list["area3 filter"] = True
        button_dict["area3 filter"]["text"] = "area3 filter on"

def next_af_button_callback():
    msg={}
    msg["type"] = "next"
    next_af_msg_list.append(msg)

def prev_af_button_callback():
    msg={}
    msg["type"] = "prev"
    next_af_msg_list.append(msg)

def radar_rfs_button_callback():
    sendmsglist.append("rfs")
    msg={}
    msg["type"] = "clear"
    next_af_msg_list.append(msg)

    query_filter_area_msg_list.append(msg)

def radar_clear_query_button_callback():
    msg={}
    msg["type"] = "clear"
    next_af_msg_list.append(msg)

    query_filter_area_msg_list.append(msg)

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
    print('button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
          (event.button, event.x, event.y, event.xdata, event.ydata))
    # print(len(radar_sheet_grid_list))
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
            print(msg)
            next_af_msg_list.append(msg)
            break
            
    

class radar_sheet():
    def __init__(self, radar_tk_window, sheet_type, radar_normal_angel, radar_theta, radar_distance, sortnum, dis_reso) -> None:
        self.tk_window = radar_tk_window
        self.sheet_type = sheet_type
        self.radar_normal_angel = 90
        self.radar_theta = 120
        self.radar_distance = 800
        self.sortnum = sortnum+1
        self.radar_valid_dis = 600

        self.theta = np.pi*radar_normal_angel/180
        self.width = np.pi*radar_theta/180
        self.colors = plt.cm.viridis(radar_distance / 10.)

        

        self.fig = plt.figure()

        self.cid = self.fig.canvas.mpl_connect('button_press_event', onclick)

        if sheet_type == "polar":
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
        else:
            self.ax_radar = self.fig.add_subplot()

            plt.gca().set_aspect('equal', adjustable='box')

            self.ax_radar.set_xlim(xmin=-self.radar_distance, xmax=self.radar_distance)
            self.ax_radar.set_ylim(ymin=0, ymax=self.radar_distance)
            self.ax_radar.xaxis.set_major_locator(MultipleLocator(dis_reso))
            self.ax_radar.yaxis.set_major_locator(MultipleLocator(dis_reso))
            

            self.ax_radar.grid(False,color='black',linestyle=':',linewidth=0.5)

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
            # plt.gca().add_patch(plt.Rectangle(xy=(0, 36), width=72, height=108, edgecolor='green', fill=False, linewidth=2))
            # self.valid_dis = 600

            rect_x_list = list(range(0-108, -520-108, -108))
            rect_y_list = list(range(0, 600, 108))

            self.scan_rect_xy_list = []

            for rect_x in rect_x_list:
                for rect_y in rect_y_list:
                    rect_xy_item = [rect_x, rect_y]
                    self.scan_rect_xy_list.append(rect_xy_item)

            rect_x_list = list(range(0, 520, 108))
            for rect_x in rect_x_list:
                for rect_y in rect_y_list:
                    rect_xy_item = [rect_x, rect_y]
                    self.scan_rect_xy_list.append(rect_xy_item)

            print(len(self.scan_rect_xy_list))

            print(self.scan_rect_xy_list)

            self.grid_list = []

            

            for o_item in self.scan_rect_xy_list:
                grid_item = {}
                grid_item["x1y1"] = o_item
                temp_item = [o_item[0]+108, o_item[1]]  
                grid_item["x2y2"] = temp_item
                temp_item = [o_item[0]+108, o_item[1]+108]  
                grid_item["x3y3"] = temp_item
                temp_item = [o_item[0], o_item[1]+108]  
                grid_item["x4y4"] = temp_item
                self.grid_list.append(grid_item)
            
            # radar_sheet_grid_list = self.grid_list

            for item in self.grid_list:
                radar_sheet_grid_list.append(item)

            print(f"radar_sheet_grid_list={radar_sheet_grid_list}")


            for item in self.scan_rect_xy_list:
                plt.gca().add_patch(plt.Rectangle(xy=(item[0], item[1]), width=108, height=108, edgecolor='green', fill=False, linewidth=1))

            test_scan = plt.gca().add_patch(plt.Rectangle(xy=(-540, 540), width=108, height=108, edgecolor='red', fill=False, linewidth=2))
            test_scan.remove()

            self.rect_filters = []

        

        # 将 matplotlib 图形嵌入到 tkinter 窗口中
        canvas = FigureCanvasTkAgg(self.fig, master=self.tk_window)   
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        pass

    def rect_filter_new_area(self, name, sx, sy, ex, ey):
        # print("rect_filter_new_area")
        rect_filter_dict = {}
        rect_filter_dict["name"]=name

        rect_xywh = rect_2p_to_xywh(sx, sy, ex, ey)

        rect_filter_dict["xywh"]=rect_xywh
        rect_filter_dict[name]=plt.gca().add_patch(plt.Rectangle(xy=rect_xywh["xy"], width=rect_xywh["w"], height=rect_xywh["h"], edgecolor='red', fill=False, linewidth=2))
        self.rect_filters.append(rect_filter_dict)
        pass

    def rect_filter_move(self, name, sx, sy, ex, ey):
        # print("rect_filter_move")
        find_name = 0
        for item in self.rect_filters:
            if name in item:
                find_name = 1
                item[name].remove()
                self.rect_filters.remove(item)
                break
        self.rect_filter_new_area(name, sx, sy, ex, ey)
        pass

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



class radar_shot():
    def __init__(self, radar_sheet, polar_theta=0, polar_r=0, rectx=0, recty=0) -> None:
        self.rectx = rectx
        self.recty = recty
        self.polar_theta = polar_theta
        self.polar_r = polar_r

        colors=list(mcolors.TABLEAU_COLORS.keys())
        # self.color = 'red'
        self.color = mcolors.TABLEAU_COLORS[colors[random.randint(0, len(colors)-1)]]

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
            self.radar_sheet.fig.canvas.draw()
            time.sleep(0.5)
            for ishot in self.shots:
                if ishot["shot status"]==1:
                    ishot["shot time"] += 1
                    if ishot["shot time"] >= 3:
                        # ishot["shot time"] = 0
                        ishot["shot status"] = 0
                        ishot["shot shot"].del_shot()



socket_client_ulimit = 30
socket_client_rcv_timeout = 360
socket_port = 5000

sockets = []
mysockets = []
mysockets_log = []



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
radar_head_mark = bytes([0xaa, 0xff, 0x03, 0x00])
radar_tail_mark = bytes([0x55, 0xcc])

radar_cmd_head_mark = bytes([0xfd, 0xfc, 0xfb, 0xfa])
radar_cmd_tail_mark = bytes([4, 3, 2, 1])
def readMsg(client_socket, access_date, access_time, radar_data_list):
    msg_count = 0
    rcv_buf = bytes()
    read_posi = 0
    last_read_posi = 0
    one_dataframe_data = bytes()
    send_sn_counter = 0
    picture_count = 0
    # radar_data_frame = 0
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
                        if len(radar_data_frame)==30:
                            # print(radar_data_frame)
                            # myradar_data = open('radardata.bin', 'ab')
                            # myradar_data.write(bytes(radar_data_frame))
                            # myradar_data.close()

                            # print("radar data recved")

                            radar_data_frame_dict = {}
                            radar_data_frame_dict["radar_model"] = "ld2450"
                            radar_data_frame_dict["data"] = list(radar_data_frame)
                            radar_data_list.append(radar_data_frame_dict)


                            read_len += len(radar_data_frame)
                            
                        else:
                            print("radar_data_frame len error")
                            print(f"len(radar_data_frame)={len(radar_data_frame)}")
                            read_posi = len(rcv_buf)
                            # while True:
                            #     time.sleep(1)
                    elif radar_head_posi == -1 and radar_tail_posi == -1:
                        radar_cmd_head_posi = rcv_buf[read_posi:].find(radar_cmd_head_mark)
                        radar_cmd_tail_posi = rcv_buf[read_posi+radar_cmd_head_posi:].find(radar_cmd_tail_mark)

                        if radar_cmd_head_posi != -1 and radar_cmd_tail_posi != -1:
                            radar_cmd_frame_head = radar_cmd_head_posi
                            radar_cmd_frame_tail = radar_cmd_tail_posi+len(radar_cmd_tail_mark)
                            
                            # print(f"read_posi={read_posi}")
                            try:
                                radar_cmd_frame = struct.unpack(str(radar_cmd_frame_tail-radar_cmd_frame_head)+"B", rcv_buf[read_posi+radar_cmd_frame_head:read_posi+radar_cmd_frame_tail])
                            except:
                                print("cmd unpack error")
                                read_posi = len(rcv_buf)
                                print("Unexpected error:", sys.exc_info()[0])
                                pass
                            # print(f"read_posi={read_posi}")
                            read_posi += radar_cmd_frame_tail-radar_cmd_frame_head

                            # print(f"rcv cmd:{radar_cmd_frame}")

                            #---------------------------------------
                            radar_msg_list.append(list(radar_cmd_frame))
                            #---------------------------------------

                            read_len += len(radar_cmd_frame)

                        elif radar_cmd_head_posi == -1:
                            print("radar_cmd_head_posi error")
                            read_posi = len(rcv_buf)
                            break
                        elif radar_cmd_frame_tail == -1:
                            print("cmd continue recv...\n")
                            break
                        else:
                            print("cmd other\n")

                    elif radar_head_posi == -1:
                        print("radar_head_posi error")
                        read_posi = len(rcv_buf)
                        break
                    elif radar_tail_posi == -1:
                        print("continue recv...\n")
                        break
                    else:
                        print("other\n")
                last_read_posi = read_posi

                

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
            timestr_1 = time.strftime("%H_%M_%S", localtime)
            mylogfilesname = 'mylogs_' + re.sub('[-]', '_', str(time.strftime("%Y-%m-%d", localtime)))
            mylogfilename = 'mylog_' + re.sub('[:]', '_', str(time.strftime("%H:%M:%S", localtime))) + \
                '_fd' + str(client_socket.fileno()) + '.bin'
            mylogackfilename = 'mylog_' + re.sub('[:]', '_', str(time.strftime("%H:%M:%S", localtime))) + \
                '_fd' + str(client_socket.fileno()) + 'ack.bin'

            if os.path.exists('mylogfiles')==False:
                os.mkdir('mylogfiles')
            if os.path.exists('mylogfiles/' + mylogfilesname)==False:
                os.mkdir('mylogfiles/' + mylogfilesname)
            if os.path.exists('mylogfiles/' + mylogfilesname + '/' + timestr_1)==False:
                os.mkdir('mylogfiles/' + mylogfilesname + '/' + timestr_1)
            logfilepath = 'mylogfiles/' + '/' + mylogfilesname + '/' + timestr_1 + '/' + mylogfilename
            acklogfilepath = 'mylogfiles/'+ '/'  + mylogfilesname + '/' + timestr_1 + '/' + mylogackfilename

#            print('[new client][time: ' + localtimestr + ']' + ' [fd=' + str(client_socket.fileno()) + \
#                ', statistic: ' + str(len(sockets)) + '/' + str(socket_client_ulimit) + ']')

            mysocketlog = open(logfilepath, 'ab')
            mysocketlog.close()

            mysocketlog = open(acklogfilepath, 'ab')
            mysocketlog.close()

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

def radar_computer_ld2450(data_in):
    objects = [
        {"radar_model":"ld2450", "id":1, "rect_x":100, "rect_y":200, "speed":40, "dis_reso":75},
        {"radar_model":"ld2450", "id":2, "rect_x":300, "rect_y":400, "speed":50, "dis_reso":75}
    ]

    radar_objects_data = []

    radar_objects_data.append(data_in["data"][4:4+8])
    radar_objects_data.append(data_in["data"][4+8:4+8+8])
    radar_objects_data.append(data_in["data"][4+8+8:4+8+8+8])

    radar_objects = []

    for radar_object in radar_objects_data:
        if sum(radar_object[0:4]) > 0:
            x_side = 0
            radar_object_dict = {}
            radar_object_dict["radar_model"] = "ld2450"
            radar_object_dict["id"] = radar_objects_data.index(radar_object)
            radar_object_dict["rect_x"] = radar_object[0]+radar_object[1]*256
            polar_theta_rect_x = 0
            if radar_object[1]&int('10000000', 2):
                radar_object_dict["rect_x"] -= 0x8000
                x_side = 1
                polar_theta_rect_x = radar_object_dict["rect_x"]
            else:
                polar_theta_rect_x = radar_object_dict["rect_x"]
                radar_object_dict["rect_x"] = 0-radar_object_dict["rect_x"]
            
            radar_object_dict["rect_y"] = radar_object[2]+radar_object[3]*256-2**15
            radar_object_dict["speed"] = radar_object[4]+radar_object[5]*256
            radar_object_dict["dis_reso"] = radar_object[6]+radar_object[7]*256
            radar_object_dict["rect_x"] = radar_object_dict["rect_x"]/10
            polar_theta_rect_x = polar_theta_rect_x/10
            radar_object_dict["rect_y"] = radar_object_dict["rect_y"]/10
            polar_posi = Rectangular_to_Polar(polar_theta_rect_x, radar_object_dict["rect_y"])
            radar_object_dict["polar_r"]  = polar_posi[0]
            radar_object_dict["polar_theta"]  = polar_posi[1]
            if x_side == 0:
                radar_object_dict["polar_theta"] = 180-radar_object_dict["polar_theta"]
            radar_objects.append(radar_object_dict)
    # print(f"radar_objects={radar_objects}")
    return radar_objects


def radar_data_analyse(data_in, data_out):
    if os.path.exists('data')==False:
        os.mkdir('data')
    if os.path.exists('data/radardata')==False:
        os.mkdir('data/radardata')
    while(True):
        if button_msg_list["exit"]==False:
            if len(data_in) > 0:

                if button_msg_list["json record"]==True:
                    # print(f"len(data_in)={len(data_in)}")
                    radar_data_json = []
                    try:
                        with open('data/radardata/radar_data.json', 'r') as f:
                            radar_data_json = json.load(f)
                    except:
                        print("ignore")

                    objects_data_item = {}
                    for idata_in in data_in:
                        radar_data_list = radar_computer_ld2450(idata_in)
                        # print(f"radar_data_list={radar_data_list}")
                        localtime = time.localtime()
                        localtimestr = time.strftime("%Y-%m-%d %H:%M:%S", localtime)
                        objects_data_item["time"]=localtimestr
                        objects_data_item["data"]=radar_data_list
                        radar_data_json.append(objects_data_item)
                    
                    with open('data/radardata/radar_data.json', 'w') as f:
                        json.dump(radar_data_json, f, indent=4)
                else:
                    pass

                data_in_1 = data_in.pop()
                if len(data_in_1["data"]) > 0:
                    # print(f"data_in_1={data_in_1['data']}")
                    data_in.clear()
                    radar_data_list = radar_computer_ld2450(data_in_1)
                    for i_data in radar_data_list:
                        data_out.append(i_data)
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
            print(f"radar_cmd_msg={radar_cmd_msg}")

            radar_cmd_msg_bytes = bytes(radar_cmd_msg)

            if radar_cmd_msg_bytes[6]==0xc1:

                area_filter_data = []

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
                print(f"area_filter_xy={area_filter_xy}")

                rect_number = 1
                for item in area_filter_xy:
                    rect_name = "area"+str(rect_number)
                    rect_number+=1
                    radar_sheet.rect_filter_move(rect_name, item["area1_sx"], item["area1_sy"], item["area1_ex"], item["area1_ey"])
        elif len(query_filter_area_msg_list) > 0:
            msg = query_filter_area_msg_list.pop()

            if msg["type"] == "clear":
                for rect_number in range(1, 4):
                    rect_name = "area"+str(rect_number)
                    radar_sheet.rect_filter_move(rect_name, 0, 0, 0, 0)
        else:
            time.sleep(0.2)

def filter_area_select(radar_sheet):
    runtimes = 0
    print(f"radar_sheet.scan_rect_xy_list={radar_sheet.scan_rect_xy_list}")

    print("start scan...")
    areas_counts = len(radar_sheet.scan_rect_xy_list)

    areas_counter = -1

    while True:
        if len(next_af_msg_list)>0:
            msg = next_af_msg_list.pop()

            if msg["type"] == "any":
                nextposi = msg["posi"]
                radar_sheet.rect_filter_move("test_scan", nextposi["x1y1"][0], nextposi["x1y1"][1], nextposi["x3y3"][0], nextposi["x3y3"][1])
                scan_areas = []
                scan_area_item = []
                scan_area_item.append(nextposi["x1y1"][0])
                scan_area_item.append(nextposi["x1y1"][1])
                scan_area_item.append(nextposi["x3y3"][0])
                scan_area_item.append(nextposi["x3y3"][1])
                scan_areas.append(scan_area_item)
                set_filter_area_packer(scan_areas, filtertype=1)
            elif msg["type"] == "clear":
                radar_sheet.rect_filter_move("test_scan", 0, 0, 0, 0)
                # scan_areas = []
                # set_filter_area_packer(scan_areas, filtertype=1)
        else:
            time.sleep(0.2)

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

    radar_sheet1 = radar_sheet(radar_tk_window, "rect", 90, 120, 800, 36, 36)
    plt.title('24GHz radar collect')

    radar_original_data = [
        {"radar_model":"ld2450", "data":[]}
    ]

    t = Thread(target = tcp_creator, args = (radar_original_data, ))
    t.start()

    t = Thread(target = query_filter_area, args = (radar_sheet1, ))
    t.start()

    t = Thread(target = filter_area_select, args = (radar_sheet1, ))
    t.start()

    t = Thread(target = radar_sheet_func, args = (radar_sheet1, ))
    t.start()

    # objects = [
    #     {"radar_model":"ld2450", "id":1, "rect_x":100, "rect_y":200, "speed":40, "dis_reso":75},
    #     {"radar_model":"ld2450", "id":2, "rect_x":300, "rect_y":400, "speed":50, "dis_reso":75}
    # ]
    # objects = [
    #     {"radar_model":"ld2450", "id":1, "polar_r":100, "polar_theta":200, "speed":40, "dis_reso":75},
    #     {"radar_model":"ld2450", "id":2, "polar_r":300, "polar_theta":400, "speed":50, "dis_reso":75}
    # ]
    objects = []

    t = Thread(target = radar_data_analyse, args=(radar_original_data, objects))
    t.start()


    dynamic_plot = DynamicPlotThread(radar_sheet1, objects)
    dynamic_plot.start()

    button_exit = tk_button(radar_tk_window, name = "exit", text="exit", width=len("exit"), height=1, b_x = 0, b_y = 0, callback=exit_button_callback)
    button_exit = tk_button(radar_tk_window, name = "scan mode", text="scan mode multi", width=len("scan mode multi"), height=1, b_x = 50, b_y = 0, callback=scan_mode_button_callback)

    button_json_switch = tk_button(radar_tk_window, name = "json record switch", text="json record off", width=len("json record off"), height=1, b_x = 180, b_y = 0, callback=json_record_button_callback)
    
    button_filter_query = tk_button(radar_tk_window, name = "filter_query", text="query filter", width=len("query filter"), height=1, b_x = 310, b_y = 0, callback=filter_query_button_callback)

    button_filter_query = tk_button(radar_tk_window, name = "set_filter", text="set filter", width=len("set filter"), height=1, b_x = 410, b_y = 0, callback=set_filter_button_callback)
    button_filter_query = tk_button(radar_tk_window, name = "area1 filter", text="area1 filter off", width=len("area1 filter off"), height=1, b_x = 540, b_y = 0, callback=area1_filter_button_callback)
    button_filter_query = tk_button(radar_tk_window, name = "area2 filter", text="area2 filter off", width=len("area2 filter off"), height=1, b_x = 670, b_y = 0, callback=area2_filter_button_callback)
    button_filter_query = tk_button(radar_tk_window, name = "area3 filter", text="area3 filter off", width=len("area3 filter off"), height=1, b_x = 800, b_y = 0, callback=area3_filter_button_callback)
    button_filter_query = tk_button(radar_tk_window, name = "radar rfs", text="radar rfs", width=len("radar rfs"), height=1, b_x = 930, b_y = 0, callback=radar_rfs_button_callback)
    button_filter_query = tk_button(radar_tk_window, name = "query clear", text="query clear", width=len("query clear"), height=1, b_x = 1100, b_y = 0, callback=radar_clear_query_button_callback)
    tk.mainloop()

    os._exit(0)