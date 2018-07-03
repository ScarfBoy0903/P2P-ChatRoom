from kivy.config import Config
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.graphics.texture import Texture
from kivy.graphics import Rectangle
from kivy.uix.widget import Widget
from kivy.base import runTouchApp
from kivy.core.window import Window
import socket
import _thread
import cv2
import numpy as np
from hashlib import md5
from time import sleep
import RC4
import Face_Detection as fd
import pickle

Config.set('graphics', 'resizable', 0)
Window.size = (1280, 720)

imageStart = False
ipAddress = "192.168.43.41"
port = 8877     # 8877 is account server, 8787 is P2P handle server
capture = cv2.VideoCapture(0)
clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn_addr = None 
mood_detect = False
RC4_on = False
recv_sock = None
send_sock = None
message=""

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


def reconnect(port):
    global clientsocket, ipAddress
    clientsocket.close()
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((ipAddress, port))

def sender():
    global conn_addr, RC4_on, send_sock
    print("prepare to send\n")
    sleep(2)
    send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_sock.connect(conn_addr)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    ret, frame = capture.read()
    while ret:
        print("send")
        result, imgencode = cv2.imencode('.jpg', np.fliplr(np.flipud(frame)), encode_param)
        data = np.array(imgencode)
        if RC4_on:
            KeyBytes = RC4.text_to_bytes('key.txt')
            data = RC4.crypt(data, KeyBytes)
        stringData = data.tostring()
        customSend(send_sock,50,stringData)    # mode = 50 (Video send)
        ret, frame = capture.read()
        sleep(0.1)
    send_sock.close()
    cv2.destroyAllWindows()


kv = '''
main:
    BoxLayout:
        orientation: 'vertical'
        padding: root.width * .01, root.height * .01
        spacing: '3dp'
        GridLayout:
            size_hint: [1,.85]
            spacing: '2dp'
            cols: 2
            BoxLayout:
                size_hint: [.7,1]
                TargetCamera:
                # MyCamera:
            GridLayout:
                size_hint: [.3,1]
                rows: 2
                padding: '2dp'
                canvas.before: 
                    Color: 
                        rgb: .5, .5, .5
                    Rectangle: 
                        pos: self.pos 
                        size: self.size
                TextInput:
                    id: history
                    readonly: True
                    size_hint:[1,.8]
                    text:'Welcome to Live Streaming App'
        GridLayout:
            spacing: '2dp'
            size_hint:[1,.05]
            cols:2
            TextInput:
                multiline: False
                size_hint:[.8,1]
                id: chat
                on_text_validate:root.sendChat()
                focus:True
            Button:
                size_hint:[.2,1]
                text:'SEND'
                bold: True
                on_press: root.sendChat()
        BoxLayout:
            size_hint: [1,.1]
            GridLayout:
                cols: 4
                spacing: '10dp'
                Button:
                    text:'Connect'
                    bold: True
                    on_press: root.connect()
                Button:
                    text: 'Close'
                    bold: True
                    on_press: root.close()
                Button:
                    text: 'Login'
                    bold: True
                    on_press: root.login()
                Button:
                    text: 'Setting'
                    bold: True
                    on_press: root.showStatus()
'''


class TargetCamera(Image):
    def __init__(self, **kwargs):
        super(TargetCamera, self).__init__(**kwargs)
        Clock.schedule_once(self.receive, 2)

    def receive(self, dt):
        Clock.schedule_interval(self.receive2, 0.01)
        

    def receive2(self, dt):
        global recv_sock, imageStart, mood_detect, RC4_on, message
        if not imageStart:
            return 
        try:
            print("receive")
            mode , stringData = customRecv(recv_sock)
            if mode == 50:
                data = np.fromstring(stringData, dtype='uint8')
                if RC4_on:
                    KeyBytes = RC4.text_to_bytes('key.txt')
                    data = RC4.crypt(data, KeyBytes)
                decimg = cv2.imdecode(data, 1)
                if mood_detect:
                    decimg = fd.face_detect(decimg)
                buf = b''.join(decimg)
                image_texture = Texture.create(size=(640, 480), colorfmt='bgr')
                image_texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.texture = image_texture
            elif mode == 10:
                message = stringData.decode()
        except:
            pass


class main(BoxLayout):
    account = "Unknown"
    password = None
    login_state = False
    

    def __init__(self, **kwargs):
        super(main, self).__init__(**kwargs)
        Clock.schedule_once(self.login_first, .5)
        Clock.schedule_interval(self.checkMessage, .5)

    def connect(self):
        global imageStart, clientsocket, conn_addr, recv_sock
        if not self.login_state :
            self.tipPopup("You're not login yet!")
            return
        mode, msg = customRecv(clientsocket)  # find pair      #mode = 20 (server P2P call)
        if mode == 20:
            print(msg.decode())
        mode, conn_data = customRecv(clientsocket)      #mode = 21, 22 (server P2P data)
        if mode == 21:
            conn_addr = pickle.loads(conn_data)
            print(conn_addr)
            conn_addr_ip = conn_addr[0]
            conn_addr_port = conn_addr[1]
        mode, data = customRecv(clientsocket)
        if mode == 22:
            addr = pickle.loads(data)
            print(addr)
        _thread.start_new_thread(sender,())
        print("receiver ready")
        receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("socket closed")
        clientsocket.close()
        receiver.bind(addr)
        receiver.listen(5)
        print("start receive")
        recv_sock , addr = receiver.accept()
        imageStart = True

    def checkMessage(self, dt):
        global message
        if message != "":
            msg = message
            message = ""
            x=msg.split("!@#$%^")
            self.printMessage(x[0],x[1])

    def close(self):
        App.get_running_app().stop()

    def login_first(self, dt):
        self.login()

    def login(self):
        loginBox = BoxLayout(orientation='vertical', spacing='10dp')

        tipBox = Label(
            text="Must contain only letters, numbers, and underscores",
            color=[0.5, 0.5, 0.5, 1],
            size_hint=(1, .1))
        loginBox.add_widget(tipBox)

        txtBox = GridLayout(cols=2, spacing='10dp', size_hint=(1, .6))
        txtBox.add_widget(Label(text="Account : ", bold=True, size_hint_x=0.3))
        self.accountText = TextInput(
            id="account", hint_text="e.g. Dragon_Slayer")
        txtBox.add_widget(self.accountText)
        txtBox.add_widget(Label(text="Password: ", bold=True, size_hint_x=0.3))
        self.passwordText = TextInput(
            id="password",
            password=True,
            hint_text="Please avoid using account as password")
        txtBox.add_widget(self.passwordText)
        loginBox.add_widget(txtBox)

        cmdBox = GridLayout(cols=3, spacing='10dp', size_hint=(1, .3))
        btn1 = Button(text="Cancel", bold=True)
        btn1.bind(on_press=self.leavePopup)
        cmdBox.add_widget(btn1)
        btn2 = Button(text="Signup", bold=True)
        btn2.bind(on_press=self.sendSignup)
        cmdBox.add_widget(btn2)
        btn3 = Button(text="Login", bold=True)
        btn3.bind(on_press=self.sendLogin)
        cmdBox.add_widget(btn3)
        loginBox.add_widget(cmdBox)

        self.popup = Popup(
            title='Enter your Account and Password',
            title_align='center',
            title_size='20sp',
            content=loginBox,
            size_hint=(.8, .5))
        self.popup.open()

    def showStatus(self):
        global mood_detect, RC4_on
        statusBox = BoxLayout(orientation='vertical', spacing='10dp')
        statusBox.add_widget(Label(text="Following are your status:"))
        statusBox.add_widget(
            Label(text="Account:" + self.account, color=[0.5, 0.5, 0.5, 1]))
        statusBox.add_widget(
            Label(
                text="Login:" + str(self.login_state),
                color=[0.5, 0.5, 0.5, 1]))
        btn1 = Button(
            text="Mood Detection: " + str(mood_detect), bold=True)
        btn1.bind(on_press=self.toggleMoodDetection)
        statusBox.add_widget(btn1)
        btn2 = Button(
            text="Security transfer (RC4): " + str(RC4_on), bold=True)
        btn2.bind(on_press=self.toggleRC4)
        statusBox.add_widget(btn2)
        btn3 = Button(text="Close", bold=True)
        btn3.bind(on_press=self.leaveStatusPopup)
        statusBox.add_widget(btn3)
        self.popup2 = Popup(
            title='Status',
            title_align='center',
            title_size='20sp',
            content=statusBox,
            size_hint=(.7, .8))
        self.popup2.open()

    def toggleMoodDetection(self, btn):
        global mood_detect
        mood_detect = not mood_detect
        self.popup2.dismiss()
        Clock.schedule_once(self.toggleMoodDetection2)

    def toggleRC4(self, btn):
        global RC4_on
        sleep(1)
        RC4_on = not RC4_on
        self.popup2.dismiss()
        Clock.schedule_once(self.toggleMoodDetection2)

    def toggleMoodDetection2(self, dt):
        self.showStatus()

    def printMessage(self, header, text):
        self.ids.history.text += "\n[" + header + "]\t" + text

    def leaveStatusPopup(self, btn):
        self.popup2.dismiss()

    def valid_account_passwd(self, tmp):
        for ch in tmp:
            if not (ch.isalpha() or ch.isdigit() or ch == "_"):
                return False
        return True

    def tipPopup(self, txt):
        print("tipPopup")
        btn = Button(text="Close", bold=True)
        btn.bind(on_press=lambda *args: self.leaveTipPopup('btn', txt))
        tip = BoxLayout(orientation='vertical', spacing='10dp')
        tip.add_widget(btn)
        self.popup1 = Popup(
            title=txt,
            title_align='center',
            title_size='25sp',
            content=tip,
            size_hint=(.6, .2))
        self.popup1.open()

    def leaveTipPopup(self, btn, txt):
        print("leaveTipPopup")
        self.popup1.dismiss()
        if "login success" in txt:
            self.login_state = True
            self.popup.dismiss()
            reconnect(8787)

    def sendChat(self):  #mode = 10 (SENDCHAT)
        global send_sock
        print("sendChat")
        text = self.ids.chat.text
        self.printMessage(self.account, text)
        text = self.account+"!@#$%^"+text
        text = text.encode()
        customSend(send_sock, 10, text)
        self.ids.chat.text = ""

    def recvChat(self):  #mode = 11 (RECVCHAT)
        print("recvChat")
        global clientsocket
        customRecv(clientsocket)

    def sendSignup(self, btn):  #mode = 5 (SIGNUP)
        print("sendSignup")
        global clientsocket
        reconnect(8877)
        self.account = self.accountText.text
        self.password = self.passwordText.text
        if self.valid_account_passwd(
                self.account) and self.valid_account_passwd(self.password):
            send_account = md5(
                ('mod' + self.account).encode('utf-8')).hexdigest()
            send_password = md5(
                ('mod' + self.password).encode('utf-8')).hexdigest()
            customSend(clientsocket, 5, bytes(send_account + " " + send_password, 'utf-8'))
            mode = None
            data = None
            while mode != 7:
                mode, data = customRecv(clientsocket)
            self.tipPopup(data.decode())
        else:
            self.tipPopup("Invalid characters in account, password !")

    def sendLogin(self, btn):  #mode = 6 (LOGIN)
        print("sendLogin")
        global clientsocket
        reconnect(8877)
        self.account = self.accountText.text
        self.password = self.passwordText.text
        if self.valid_account_passwd(
                self.account) and self.valid_account_passwd(self.password):
            send_account = md5(
                ('mod' + self.account).encode('utf-8')).hexdigest()
            send_password = md5(
                ('mod' + self.password).encode('utf-8')).hexdigest()
            customSend(clientsocket,6, bytes(send_account + " " + send_password, 'utf-8'))
            mode = None
            data = None
            while mode != 7:  #mode = 7 (RETURN STRING)
                mode, data = customRecv(clientsocket)
            self.tipPopup(data.decode())
        else:
            self.tipPopup("Invalid characters in account, password !")

    def leavePopup(self, btn):
        print("leavePopup")
        self.popup.dismiss()


class videoStreamApp(App):
    def build(self):
        return Builder.load_string(kv)

videoStreamApp().run()
cv2.destroyAllWindows()