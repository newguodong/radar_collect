from socket import*
from threading import Thread
import threading
import time
import re
import os
import gc
import struct

import pandas

socket_client_ulimit = 30
socket_client_rcv_timeout = 360
socket_port = 50000

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

# radar_head_mark = b'\xAA\xFF\x03\x00'
# radar_tail_mark = b'\x55\xCC'
radar_head_mark = bytes([0xaa, 0xff, 0x03, 0x00])
radar_tail_mark = bytes([0x55, 0xcc])
radar_data = []
def readMsg(client_socket, access_date, access_time):
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
                    print(f"read_posi={read_posi}")
                    radar_head_posi = rcv_buf[read_posi:].find(radar_head_mark)
                    radar_tail_posi = rcv_buf[read_posi+radar_head_posi:].find(radar_tail_mark)
                    print(f"radar_head_posi={radar_head_posi}")
                    print(f"radar_tail_posi={radar_tail_posi}")
                    if radar_head_posi != -1 and radar_tail_posi != -1:
                        radar_data_frame_head = radar_head_posi
                        radar_data_frame_tail = radar_tail_posi+len(radar_tail_mark)
                        
                        print(f"read_posi={read_posi}")
                        radar_data_frame = struct.unpack(str(radar_data_frame_tail-radar_data_frame_head)+"B", rcv_buf[read_posi+radar_data_frame_head:read_posi+radar_data_frame_tail])
                        print(f"read_posi={read_posi}")
                        read_posi += radar_data_frame_tail-radar_data_frame_head
                        if len(radar_data_frame)==30:
                            radar_data.append(radar_data_frame)
                            print(radar_data_frame)
                            myradar_data = open('radardata.bin', 'ab')
                            myradar_data.write(bytes(radar_data_frame))
                            myradar_data.close()
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

def main():

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

            t = Thread(target = readMsg, args = (client_socket, access_date, access_time))
            t.start()
            # t = Thread(target = sendMsg, args = (client_socket,))
            # t.start()

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

if __name__=='__main__':
    main()
