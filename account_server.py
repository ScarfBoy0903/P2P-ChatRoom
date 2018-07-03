import sqlite3
import numpy as np
import socket

conn = sqlite3.connect('CNVIEWER.db')

def LogIn(account, password, conn):
    c = conn.cursor()
    query_account = account
    query_account = "'" + query_account + "'"
    query_order = "SELECT * from CNVIEWER WHERE account == " + query_account
    Is_in_DB = False
    cursor = c.execute(query_order)
    for i in cursor:
        Is_in_DB = True
    if(Is_in_DB):
        return False
    else:
        login_account = "'" + account + "'"
        login_password = "'" + password + "'"
        login_order = "INSERT INTO CNVIEWER (ACCOUNT,PASSWORD) VALUES ( " + \
            login_account + "," + login_password + ")"
        c.execute(login_order)
        conn.commit()
        return True


def SignIn(account, password, conn):
    c = conn.cursor()
    query_account = account
    query_account = "'" + query_account + "'"
    query_password = password
    query_password = "'" + query_password + "'"

    query_order = "SELECT * from CNVIEWER WHERE account == " + \
        query_account + "AND password == " + query_password
    Is_account_correct = False
    cursor = c.execute(query_order)
    for i in cursor:
        Is_account_correct = True
    if(Is_account_correct):
        return True
    else:
        return False

def show_all(conn):
    c = conn.cursor()
    cursor = c.execute("SELECT account, password from CNVIEWER")
    for row in cursor:
        print("account = ", row[0])
        print("password = ", row[1])
        print("-----------")

HOST, PORT = "", 8877
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((HOST, PORT))
s.listen(10)
    
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def customRecv(s):
    mode = recvall(s, 1)
    print(mode)
    length = recvall(s, 16)
    print(length)
    stringData = recvall(s, int(length))
    print(stringData)
    mode = int.from_bytes(mode,byteorder='little')
    return mode, stringData

def customSend(mode, data, sock):
    sock.send(bytes([mode]))
    length = str(len(data)).ljust(16).encode()
    sock.send( length)
    sock.send( data )



while(True):
    client, address = s.accept()
    print(str(address)+" connected")
    try:
        mode, data = customRecv(client)

        if (mode == 5): #SIGNUP
            order = data.decode().split()
            print(order)
            account = order[0]
            password = order[1]
            if (LogIn(account, password, conn)):
                customSend(7,b"signup success!",client)
                    # client.close()
            else:
                customSend(7,b"this account has been registed!",client)
        elif (mode == 6): #LOGIN
            order = data.decode().split()
            print(order)
            account = order[0]
            password = order[1]
            if (SignIn(account, password, conn)):
                customSend(7,b"login success!",client)
                    # client.close()
            else:
                customSend(7,b"wrong account data!",client)
        else:
            show_all(conn)
            client.send(b"SHOW!\n")
        client.close()
    except:
        print("except")

conn.close()
