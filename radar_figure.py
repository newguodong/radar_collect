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


button_msg_list = {"exit":False, "json record":False, "scan mode":"multi"}
button_dict = {}

sendmsglist=[]


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
    if button_msg_list["scan mode"] == "multi":
        button_msg_list["scan mode"] = "single"
        button_dict["scan mode"]["text"] = "scan mode single"
        sendmsglist.append("set scan mode:single")
    else:
        button_msg_list["scan mode"] = "multi"
        button_dict["scan mode"]["text"] = "scan mode multi"
        sendmsglist.append("set scan mode:multi")

class tk_button():
    def __init__(self, window, name, text, width, height, callback, b_x=0, b_y=0, b_anchor='s') -> None:
        self.window = window
        
        button = tk.Button(window,width=width, height=height, text=text, padx=1, pady=1, anchor='center', command = callback)
        button.place(x = b_x, y = b_y)
        button_dict[name] = button
        
    

class radar_sheet():
    def __init__(self, radar_tk_window, radar_normal_angel, radar_theta, radar_distance, sortnum) -> None:
        self.tk_window = radar_tk_window
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

        # 将 matplotlib 图形嵌入到 tkinter 窗口中
        canvas = FigureCanvasTkAgg(self.fig, master=self.tk_window)   
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

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

        colors=list(mcolors.TABLEAU_COLORS.keys())
        # self.color = 'red'
        self.color = mcolors.TABLEAU_COLORS[colors[random.randint(0, len(colors)-1)]]

        self.ax = radar_sheet
        pt, = self.ax.plot(np.pi*polar_theta/180, polar_r, 'o', picker=5, color=self.color, markersize = 8)
        self.pt = pt
        pass
    
    def newlocation(self, polar_theta, polar_r):
        try:
            self.pt.remove()
        except ValueError:
            # print("ignore shot")
            pass
        self.polar_theta = polar_theta
        self.polar_r = polar_r
        pt, = self.ax.plot(np.pi*polar_theta/180, polar_r, 'o', picker=5, color=self.color, markersize = 8)
        self.pt = pt
        
    
    def del_shot(self):
        try:
            self.pt.remove()
        except ValueError:
            # print("ignore shot")
            pass


class DynamicPlotThread(Thread):
    def __init__(self, fig, ax, objects):
        Thread.__init__(self)
        self.fig = fig
        self.ax = ax
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
                        jobject["shot shot"] = radar_shot(self.ax, jobject["polar_theta"], jobject["polar_r"])
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

                        self.shots[ishot_index]["shot shot"].newlocation(self.shots[ishot_index]["polar_theta"], self.shots[ishot_index]["polar_r"])
                else:
                    print("creat new shot")
                    jobject = iobject
                    jobject["shot_id"] = iobject["id"]
                    jobject["shot status"] = 1
                    jobject["shot time"] = 0
                    jobject["shot shot"] = radar_shot(self.ax, jobject["polar_theta"], jobject["polar_r"])
                    self.shots.append(jobject)
            
            self.objects.clear()
            if len(self.shots) > 0:
                for ishot in self.shots:
                    if ishot["shot time"]<1:
                        print(ishot)
                print("")
            self.fig.canvas.draw()
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
radar_data = []
def readMsg(client_socket, access_date, access_time, radar_data_list):
    msg_count = 0
    rcv_buf = bytes()
    read_posi = 0
    last_read_posi = 0
    one_dataframe_data = bytes()
    send_sn_counter = 0
    picture_count = 0
    while True:
        try:
            recv_data = client_socket.recv(65536)
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
                        radar_data_frame = struct.unpack(str(radar_data_frame_tail-radar_data_frame_head)+"B", rcv_buf[read_posi+radar_data_frame_head:read_posi+radar_data_frame_tail])
                        # print(f"read_posi={read_posi}")
                        read_posi += radar_data_frame_tail-radar_data_frame_head
                        if len(radar_data_frame)==30:
                            radar_data.append(radar_data_frame)
                            # print(radar_data_frame)
                            # myradar_data = open('radardata.bin', 'ab')
                            # myradar_data.write(bytes(radar_data_frame))
                            # myradar_data.close()

                            # print("radar data recved")

                            radar_data_frame_dict = {}
                            radar_data_frame_dict["radar_model"] = "ld2450"
                            radar_data_frame_dict["data"] = list(radar_data_frame)
                            radar_data_list.append(radar_data_frame_dict)


                            read_len += 30
                            
                        else:
                            print("radar_data_frame len error")
                            print(f"len(radar_data_frame)={len(radar_data_frame)}")
                            read_posi = len(rcv_buf)
                            # while True:
                            #     time.sleep(1)
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
    
    x = r * np.cos(theta)
    y = r * np.sin(theta)
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
            radar_object_dict = {}
            radar_object_dict["radar_model"] = "ld2450"
            radar_object_dict["id"] = radar_objects_data.index(radar_object)
            radar_object_dict["rect_x"] = radar_object[0]+radar_object[1]*256
            if radar_object[1]&int('10000000', 2):
                radar_object_dict["rect_x"] -= 0x8000
            radar_object_dict["rect_y"] = radar_object[2]+radar_object[3]*256-2**15
            radar_object_dict["speed"] = radar_object[4]+radar_object[5]*256
            radar_object_dict["dis_reso"] = radar_object[6]+radar_object[7]*256
            radar_object_dict["rect_x"] = radar_object_dict["rect_x"]/10
            radar_object_dict["rect_y"] = radar_object_dict["rect_y"]/10
            polar_posi = Rectangular_to_Polar(radar_object_dict["rect_x"], radar_object_dict["rect_y"])
            radar_object_dict["polar_r"]  = polar_posi[0]
            radar_object_dict["polar_theta"]  = polar_posi[1]
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

if __name__ == '__main__':

    # 创建 tkinter 窗口
    radar_tk_window = tk.Tk()
    radar_tk_window.title("radar collect tool")

    radar1 = radar_sheet(radar_tk_window, 90, 120, 800, 36)
    plt.title('24GHz radar collect')

    radar_original_data = [
        {"radar_model":"ld2450", "data":[]}
    ]

    t = Thread(target = tcp_creator, args = (radar_original_data, ))
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


    dynamic_plot = DynamicPlotThread(radar1.fig, radar1.ax_radar, objects)
    dynamic_plot.start()

    button_exit = tk_button(radar_tk_window, name = "exit", text="exit", width=len("exit"), height=1, b_x = 0, b_y = 0, callback=exit_button_callback)
    button_exit = tk_button(radar_tk_window, name = "scan mode", text="scan mode multi", width=len("scan mode multi"), height=1, b_x = 50, b_y = 0, callback=scan_mode_button_callback)

    button_json_switch = tk_button(radar_tk_window, name = "json record switch", text="json record off", width=len("json record off"), height=1, b_x = 180, b_y = 0, callback=json_record_button_callback)

    tk.mainloop()

    os._exit(0)