from socket import*
from threading import Thread
import threading
import time
import re
import os
import gc
import struct

def readMsg(server):
    msg_count = 0
    while True:
        try:
            recv_data = server['socket'].recv(65536)
        except ConnectionResetError:
            print('readMsg(1) remove socket')
            server['socket'].remove(server['socket'])
            server['mysockets'].remove(item_sock)
            if server['mysockets']['socket'].fileno()!=-1:
                server['mysockets']['socket'].shutdown(2)
                server['mysockets']['socket'].close()
            # mysocket_monitor()
            gc.collect()
            break

        if len(recv_data) > 0:
            for item_sock in server['mysockets']:
                if item_sock['socket']==server['sockets']:
                    item_sock['rcvtimeouttimer']=0
            msg_count += 1
            try:
                #recv_data_str = recv_data.decode('utf-8')
                #mysocketlog.write(recv_data_str + '\n')
                server['sockets'].send(recv_data)
                

            except UnicodeDecodeError:
                # mysocketlog.write("recv_data is not 'utf-8'\n")
               print("recv_data is not 'utf-8'\n")
        else:
            print('readMsg(2) client disconnect, remove socket')
            if server['sockets'] in server['sockets']:
                server['sockets'].remove(server['sockets'])
            for item_sock in server['mysockets']:
                if item_sock['socket']==server['sockets']:
                    if item_sock in server['mysockets']:
                        server['mysockets'].remove(item_sock)
            if server['sockets'].fileno()!=-1:
                server['sockets'].shutdown(2)
                server['sockets'].close()
            # mysocket_monitor()
            gc.collect()
            break


def socktimer(server):
    while True:
        time.sleep(1)
        for item_sock in server['mysockets']:
            item_sock['rcvtimeouttimer']+=1
            if item_sock['rcvtimeouttimer']>=server['connection_idle_ulimit']:
                print('rcv timeout, remove socket')
                if item_sock['socket'].fileno()!=-1:
                    item_sock['socket'].shutdown(2)
                    item_sock['socket'].close()
                if item_sock in server['mysockets']:
                    server['mysockets'].remove(item_sock)
                gc.collect()


def mysocket_monitor(server):
    mysocketmonitorfile = open('mysocketmonitor.txt', 'w')
    length = len(threading.enumerate())
    mysocketmonitorfile.write('thread count: ' + str(length) + '\n')
    mysocketmonitorfile.write('client count: ' + str(len(server['sockets'])) + '\n\n')
    mysocketmonitorfile.write('client list:\n')
    socketlistcount = 0
    for isocket in server['sockets']:
        socketlistcount += 1
        mysocketmonitorfile.write('[' + str(socketlistcount) + ']' + str(isocket) + '\n\n')
    mysocketmonitorfile.close()


def monitor_test(server):
    while True:
        time.sleep(5)
        # length = len(threading.enumerate())
        # print('\nthread len='+str(length)+'\n')
        mysocket_monitor(server)


def my_tcp_server_main_creator(server):

    t = Thread(target = monitor_test, args=(server,))
    t.start()

    mysocket_monitor(server)


    # server_port = int(input("port:"))

    mysocket1 = ('', server['port'])
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.bind(mysocket1)
    print('socket bind success')

    server_socket.listen()
    print('listen...')

    server['socktimer_thread'] = Thread(target = socktimer, args = (server, ))
    server['socktimer_thread'].start()

    while True:
        if len(server['sockets']) < server['connection_ulimit']:
            client_socket,client_info = server_socket.accept()
            server['sockets'].append(client_socket)
            
            print('\n---')
            # print(mysockets)
            print('new client:', client_info, 'fd=', client_socket.fileno())
            for item_sock in server['mysockets']:
                if item_sock['socket'].getpeername()[0] == client_socket.getpeername()[0]:
                    print('remove')
                    item_sock['socket'].shutdown(2)
                    item_sock['socket'].close()
                    if item_sock in server['mysockets']:
                        server['mysockets'].remove(item_sock)
                    print(server['mysockets'])

            mysocketitem = {'socket':client_socket, 'rcvtimeouttimer':0, 'readthread':read_thread}
            server['mysockets'].append(mysocketitem)
            socket_index = server['mysockets'].index(mysocketitem)
            read_thread = Thread(target = readMsg, args = (server['mysockets'][socket_index], ))
            read_thread.start()
            # t = Thread(target = sendMsg, args = (client_socket,))
            # t.start()

            
            print(server['mysockets'])

            length = len(threading.enumerate())
            print('thread count='+str(length))
            print('client count=' + str(len(server['sockets']))+'\n')

            mysocket_monitor(server)
        else:
            time.sleep(2)


class my_tcp_server():
    def __init__(self, port, connection_ulimit=30, connection_idle_ulimit=300) -> None:
        self.server = {
            "port": port,
            "connection_ulimit": connection_ulimit,
            "connection_idle_ulimit": connection_idle_ulimit,
            "sockets": [],
            "mysockets": [],
        }
    
    def creat(self):
        self.server['main_creator'] = Thread(target = my_tcp_server_main_creator, args = (self.server, ))
        self.server['main_creator'].start()

        pass


test_mts1 = my_tcp_server(5000, 5, 60)
test_mts1.creat()