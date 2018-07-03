import socket
import select
import queue
import pickle
import time

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def customRecv(sock):
    mode = recvall(sock, 1)
    length = recvall(sock, 16)
    stringData = recvall(sock, int(length))
    mode = int.from_bytes(mode, byteorder='little')
    return mode, stringData


def customSend(sock, mode, data):
    sock.send(bytes([mode]))
    length = str(len(data)).ljust(16).encode()
    sock.send(length)
    sock.send(data)

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_IP = ''
server_PORT = 8787
server.bind((server_IP, server_PORT))
server.listen(5)
r_list = [server,]
count = 0 
wait_queue = queue.Queue()
addr_queue = queue.Queue()
list_start = []
list_target = []
append_port = 7777

while True:
    readarray, writearray, errorarray = select.select(r_list,[],[],10)
    for fd in readarray:
        if fd == server: #新連線
            print(fd)
            clientfd , addr = fd.accept()
            print(addr)
            listx = list(addr)
            listx.pop()
            listx.append(append_port)
            append_port += 1
            addr = tuple(listx)
            if wait_queue.empty():  #序列為空時，直接放入資料
                wait_queue.put(clientfd)
                addr_queue.put(addr)
                r_list.append(clientfd)
            else:   #序列不為空時，配對處理
                connfd = wait_queue.get()
                # clientfd.sendall(b"find pair")
                customSend(clientfd,20,b"find pair")
                # connfd.sendall(b"find pair")
                customSend(connfd,20,b"find pair")
                connaddr = addr_queue.get()
            
                conn_data_string = pickle.dumps(connaddr)
                data_string = pickle.dumps(addr)

                # clientfd.sendall(conn_data_string)
                customSend(clientfd,21,conn_data_string)
                # connfd.sendall(data_string)
                customSend(connfd,21,data_string)
                time.sleep(1)
                # clientfd.sendall(data_string)
                customSend(clientfd,22,data_string)
                # connfd.sendall(conn_data_string)
                customSend(connfd,22,conn_data_string)
                r_list.pop()
        else :
            print("one client leave")
            wait_queue.get()
            addr_queue.get()
            r_list.pop()
            
            
                
            #except ConnectionAbortedError:
            #    print("client leave")
            #    i=0
     
server.close()      
