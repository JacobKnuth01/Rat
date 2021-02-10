import socket
import cv2
import pickle
import numpy as np
from PIL import ImageGrab, Image
import os


import pynput.keyboard
import pynput.mouse
import threading

class Packet:

    def __init__(self, cam, screen):
        self.cam = cam
        self.screen = screen
MARKER = bytes("=f*f=", "utf-8")

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("", 1234))
s.listen(1)
tunnel, ipc = s.accept()

s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.bind(("", 1235))
s2.listen(1)
tunnel2, ipc = s2.accept()

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
spot = (0,0)
def mo(x,y):
    global spot
    spot = (x,y)

m = pynput.mouse.Listener(on_move=mo)
m.start()

def xs(spot, screen):
    w = 10
    c = spot[0] - w
    r = 0

    while c < spot[0] + w:

        while r < len(screen):
            if r < spot[1] + 50 and r > spot[1] - 50:
                if c >= 0 and c < len(screen[r]):
                    screen[r][c] = [255, 0, 0]
            r = r + 1
        r = 0
        c = c + 1

    return screen
def CaptureScreen():
    screen = np.array(ImageGrab.grab(bbox=None))
    screen = xs(spot, screen)
    screen = cv2.resize(screen, dsize=(int(len(screen[0])//2), len(screen)//2), interpolation=cv2.INTER_NEAREST)
    return screen
def CaptureCamera():
    r = False
    while not r:
        r, frame = camera.read()
    return frame
def keys():
    global s2
    global tunnel2
    k = pynput.keyboard.Controller()
    mouse = pynput.mouse.Controller()
    while True:
        try:
            size = tunnel2.recv(5)
            size = int.from_bytes(size, "big")
            p = tunnel2.recv(size)
            item = pickle.loads(p)
            ty = str(type(item))
            if ty== "<class 'tuple'>" and len(item)==2:

                mouse.position = (item[0], item[1])
            elif ty == "<class 'pynput.keyboard._win32.KeyCode'>" or ty=="<enum 'Key'>":

                k.press(item)
                k.release(item)
            elif ty == "<class 'tuple'>" and len(item) == 4:

                mouse.position = (item[0], item[1])

                if item[3]:
                    mouse.press(item[2])
                else:
                    mouse.release(item[2])

        except ConnectionResetError:
            s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s2.bind(("", 1235))
            s2.listen(1)

            tunnel2, ipc = s2.accept()
        except Exception as e:
            print(e)




t1 = threading.Thread(target=keys)
t1.start()

while True:
    cv2.waitKey(1)
    cam = CaptureCamera()
    screen = CaptureScreen()

    p = Packet(cam, screen)

    p = pickle.dumps(p)

    try:
        #tunnel.recv(1)
        tunnel.sendall(p)
        tunnel.sendall(MARKER)

    except ConnectionResetError:

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("", 1234))
        s.listen(1)
        tunnel, ipc = s.accept()







