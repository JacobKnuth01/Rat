import socket
import cv2
import pickle
import numpy as np
from PIL import ImageGrab, Image
import os
from pynput import keyboard
from pynput import mouse
class Packet:

    def __init__(self, cam, screen):
        self.cam = cam
        self.screen = screen
MARKER = bytes("=f*f=", "utf-8")
READY = 1
READY = READY.to_bytes(1, "big")
ip = "10.22.4.59"
#ip = "10.22.1.128"
#ip = "10.22.10.123"

data = b""
isOpen = True
def onPress(key):
    global isOpen
    while True:
        if isOpen:
            isOpen=False

            key = pickle.dumps(key)
            s2.sendall(len(key).to_bytes(5, "big"))
            s2.sendall(key)
            isOpen = True
            break
def on_move(x,y):
    global isOpen
    while True:
        if isOpen:
            isOpen = False

            cords = (x,y)
            cords = pickle.dumps(cords)
            s2.sendall(len(cords).to_bytes(5, "big"))
            s2.sendall(cords)
            isOpen = True
            break
def on_click(x, y, button, pressed):
    global isOpen
    while True:
        if isOpen:
            isOpen = False
            data = (x, y, button, pressed)
            data = pickle.dumps(data)
            s2.sendall(len(data).to_bytes(5, "big"))
            s2.sendall(data)
            isOpen = True
            break

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip, 1234))

s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s2.connect((ip, 1235))
print("connected")
l = keyboard.Listener(on_press=onPress)
l.start()

lis = mouse.Listener(
        on_move=on_move, on_click=on_click)
lis.start()

def ReciveData():
    global data
    while True:
        data = data + s.recv(2477058*2)

        if MARKER in data:
            spot = data.index(MARKER)
            packet = data[:spot]
            data = data[spot:]
            data = data[len(MARKER):]
            #print(len(packet))
            return packet


while True:
    #s.sendall(READY)
    pack = ReciveData()

    pack = pickle.loads(pack)

    screen = pack.screen
    cam = pack.cam

    cv2.imshow("cam", cam)
    cv2.imshow("scremn", screen)
    cv2.waitKey(1)



