import tkinter as tk
from tkinter import *
import cv2
from PIL import Image, ImageTk
import threading
import queue
import time
import RPi.GPIO as GPIO

## set GPIO -------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

## Set Ultrasonic ----
GPIO_TRIGGER = 4
GPIO_ECHO = 17

## Set PIR ----
GPIO_PIR= 23

## Set BEAM ----
GPIO_BEAM = 17

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

GPIO.setup(GPIO_PIR, GPIO.IN)

GPIO.setup(GPIO_BEAM, GPIO.IN)

maxWidth = 300
maxHeight = 375
lightBlue2 = "#adc5ed"
font = "Constantia"
fontButtons = (font,12)
white = "#ffffff"

mainWindow = tk.Tk()
mainWindow.configure(bg=lightBlue2)
mainWindow.geometry('%dx%d+%d+%d' % (maxWidth,maxHeight,0,0))
mainWindow.resizable(0,0)

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 120)

faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_alt.xml')

Labeltk1 = Label(mainWindow, text = "Face Detected", bg ="green")
Labeltk = Label(mainWindow, text = "No Face Found", bg = "red")
LabelSensor = Label(mainWindow, text = "Grip Detection", bg = "green")
LabelSensortk = Label(mainWindow, text = "No Grip Detection", bg = "red")

LabelPir = Label(mainWindow, text = "Motion Detected", bg = "green")
LabelPirDelay = Label(mainWindow, text = "Delay", bg = "orange")
LabelPirtk = Label(mainWindow, text = "No Motion", bg = "red")

switch = False
switchPIR = False
switchBEAM = False
Buttonpressed = True
camswitch = False

def camswitchon():
    global camswitch
    camswitch = True
    runThread()

def camswitchoff():
    global camswitch
    camswitch = False

def switchonPIR():
    global switchPIR
    switchPIR = True
    testPir()

def switchoffPIR():
    global switchPIR
    switchPIR = False

def switchonBEAM():
    global switchBEAM
    switchBEAM = True
    testBEAM()

def switchoffPIR():
    global switchBEAM
    switchBEAM = False

def switchon():
    global switch
    switch = True
    ultrasonic()

def switchoff():
    global switch
    switch = False
    
def kill():
    GPIO.cleanup()
    cv2.destroyAllWindows()
    mainWindow.destroy()

def testPir():
    def run():
        while (switchPIR == True):
            if switchPIR == False:
                break
            elif GPIO.input(23):
                LabelPirtk.place_forget()
#                LabelPirDelay.place_forget()
                LabelPir.place(x=155,y=50)
                time.sleep(4)
            else:
               delayfunc()
                
        
    thread = threading.Thread(target=run)
    thread.start()
    
def delayfunc():
    LabelPir.place_forget()
#                LabelPirDelay.place(x=155,y=10)
#                time.sleep(3)
    LabelPirDelay.place(x=155, y=50)
    time.sleep(6)
    LabelPirDelay.place_forget()
    LabelPirtk.place(x=155, y=50)


def distance():
    GPIO.output(GPIO_TRIGGER, True)
    
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    
    StartTime = time.time()
    StopTime = time.time()
    
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
        
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
        
    
    TimeElapsed = StopTime - StartTime
    
    distance = (TimeElapsed * 34300) / 2
    
    return distance

def ultrasonic():
    def run():
        while (switch == True):
            dist = distance()
            if switch == False:
                break
            elif dist > 50.0:
                LabelSensortk.place(x=150,y=10)
                LabelSensor.place_forget()
                time.sleep(0.1)
            else:
#                print("Measured Distance = %.1f cm" % dist)
                LabelSensor.place(x=155,y=10)
                LabelSensortk.place_forget()
                time.sleep(0.1)
            
    thread = threading.Thread(target=run)
    thread.start()
    
def show_camera():
    while( camswitch == True):
        _, frame = cap.read()
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
        if (Buttonpressed):
            detect_face(gray)
                     
        cv2.imshow('frame',gray)
    
        if cv2.waitKey(1) & camswitch == False:
            break
    
    cap.release()
    
def detect_face(img):
    Buttonpressed = True
    faces = faceCascade.detectMultiScale(img,1.1,5, minSize = (30,30))
    
    if (len(faces)) == 0:
        Labeltk.place(x=155, y=50)
    else:
        for (x, y, w, h) in faces:
            img = cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0),2)
            Labeltk1.place(x=155, y=50)
            Labeltk.place_forget()
            
def runThread():
    myThread = threading.Thread(target=show_camera)
    myThread.setDaemon(False)
    myThread.start()
    
onButton = Button(mainWindow, text = "Start Ultrasonic", font=fontButtons, bg = white, width = 10 , height = 1)
onButton.configure(command = lambda: switchon())
onButton.place(x = 7, y = 7)
    
offButton = Button(mainWindow, text = "Stop Ultrasonic", font=fontButtons, bg = white, width = 10 , height = 1)
offButton.configure(command = lambda: switchoff())
offButton.place(x = 7, y = 47)
    
QuitButton = Button(mainWindow, text = "Close Gui", font=fontButtons, bg = white, width = 10 , height = 1)
QuitButton.configure(command = lambda: kill())
QuitButton.place(x = 7, y = 87)
    
CamonButton = Button(mainWindow, text = "Open Face Detect", font=fontButtons, bg = white, width = 12 , height = 1)
CamonButton.configure(command = lambda: camswitchon())
CamonButton.place(x = 7, y = 127)

CamoffButton = Button(mainWindow, text = "Close Face Detect", font=fontButtons, bg = white, width = 12 , height = 1)
CamoffButton.configure(command = lambda: camswitchoff())
CamoffButton.place(x = 7, y = 167)

onPirButton = Button(mainWindow, text = "Start Pir", font=fontButtons, bg = white, width = 10 , height = 1)
onPirButton.configure(command = lambda: switchonPIR())
onPirButton.place(x = 7, y = 207)
    
offPirButton = Button(mainWindow, text = "Stop Pir", font=fontButtons, bg = white, width = 10 , height = 1)
offPirButton.configure(command = lambda: switchoffPIR())
offPirButton.place(x = 7, y = 247)

onBeamButton = Button(mainWindow, text = "Start Beam", font=fontButtons, bg = white, width = 10 , height = 1)
onBeamButton.configure(command = lambda: switchonBEAM())
onBeamButton.place(x = 7, y = 287)
    
offBeamButton = Button(mainWindow, text = "Stop Beam", font=fontButtons, bg = white, width = 10 , height = 1)
offBeamButton.configure(command = lambda: switchoffBEAM())
offBeamButton.place(x = 7, y = 327)

mainWindow.mainloop()