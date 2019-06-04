import tkinter as tk
from tkinter import *
import cv2
from PIL import Image, ImageTk
import threading
import queue
import RPi.GPIO as GPIO
import smbus
import math
from time import sleep, strftime, time
from datetime import datetime


# Register
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

## set GPIO -------
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

## Set Ultrasonic ----
GPIO_TRIGGER = 4
GPIO_ECHO = 17

## Set PIR ----
GPIO_PIR= 23

## Set BEAM ----
GPIO_BEAM = 27

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

LabelBeam = Label(mainWindow, text = "Not broken", bg = "red")
LabelBeamtk = Label(mainWindow, text = "Beam Broken", bg = "green")

motiondelay = False
switch = False
switchPIR = False
switchBEAM = False
Buttonpressed = True
camswitch = False
pirtest = False
global looper
global pirtest
looper = 0
pirtest = 0


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
    LabelPirtk.place_forget()
    LabelPir.place_forget()

def switchonBEAM():
    global switchBEAM
    switchBEAM = True
    pirtest = True
    runner()

def switchoffBEAM():
    global switchBEAM
    switchBEAM = False
    pirtest = False
    LabelBeam.place_forget()
    LabelBeamtk.place_forget()

def switchon():
    global switch
    switch = True
    ultrasonic()

def switchoff():
    global switch
    switch = False
    LabelSensor.place_forget()
    LabelSensortk.place_forget()
    
def kill():
    GPIO.cleanup()
    cv2.destroyAllWindows()
    mainWindow.destroy()

def read_byte(reg):
    return bus.read_byte_data(address, reg)
 
def read_word(reg):
    h = bus.read_byte_data(address, reg)
    l = bus.read_byte_data(address, reg+1)
    value = (h << 8) + l
    return value
 
def read_word_2c(reg):
    val = read_word(reg)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):
    return math.sqrt((a*a)+(b*b))


def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)
 
def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

bus = smbus.SMBus(1) # bus = smbus.SMBus(0) fuer Revision 1
address = 0x68       # via i2cdetect
 
# Aktivieren, um das Modul ansprechen zu koennen
bus.write_byte_data(address, power_mgmt_1, 0)


def testPir():
    def run():
        while (switchPIR == True):
            if switchPIR == False:
                break
            elif GPIO.input(23):
                global pirtest
                pirtest = 1
                detectMotion()
            else:
                global pirtest
                pirtest = 0
                noMotion()   
    thread = threading.Thread(target=run)
    thread.start()

def detectMotion():
#    print(motiondelay)
    motiondelay = True    
    LabelPirtk.place_forget()
    LabelPir.place(x=155,y=40)
    delayMotion()

def delayMotion():
#    print(motiondelay)
    # time.sleep(6)
    if motiondelay == True:
        GPIO.input(23) == 0
        motiondelay == False

def noMotion():
#    print(motiondelay)
    LabelPir.place_forget()
    pirtest = False
    LabelPirtk.place(x=155, y=40)

def delayfunc():
    LabelPir.place_forget()
#                LabelPirDelay.place(x=155,y=10)
#                time.sleep(3)
    LabelPirDelay.place(x=155, y=10)
    time.sleep(6)
    LabelPirDelay.place_forget()
    LabelPirtk.place(x=155, y=10)


def testBEAM():
    def run():
        while (switchBEAM == True):
            if switchBEAM == False:
                break
            elif (GPIO.input(GPIO_BEAM) == 1):
                LabelBeam.place(x = 185, y = 150)
                LabelBeamtk.place_forget()
            elif (GPIO.input(GPIO_BEAM) == 0):
                LabelBeamtk.place(x = 185, y = 150)
                LabelBeam.place_forget()
                  
    thread = threading.Thread(target=run)
    thread.start()

def runner():
    def run():
        global looper
        global pirtest
        global ultratest
        with open("/home/pi/metin/mpuLog{0}.csv".format(time()), "a") as log:
            log.write("x,y,z,PIR,time\n")
            while (switchBEAM == True):
                
                if switchBEAM == False:
                    break
                else:
                    acceleration_xout = read_word_2c(0x3b)
                    acceleration_yout = read_word_2c(0x3d)
                    acceleration_zout = read_word_2c(0x3f)
                        
                    acceleration_xout_scaled = acceleration_xout / 16384.0
                    acceleration_yout_scaled = acceleration_yout / 16384.0
                    acceleration_zout_scaled = acceleration_zout / 16384.0
                        
                    if ultratest == 1:
                        ultradata = 1000
                    else:
                        ultradata = 0
                    
                
                    test = log.write("{0},{1},{2},{3},{4}\n".format(str(acceleration_xout),str(acceleration_yout),str(acceleration_zout), str(ultradata),datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")))
                    
                    looper+=1
                    print(ultratest)
                    sleep(0.1)
    thread = threading.Thread(target=run)
    thread.start()

def distance():
    GPIO.output(GPIO_TRIGGER, True)
    
    sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    
    StartTime = time()
    StopTime = time()
    
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time()
        
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time()
        
    
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
                global ultratest
                ultratest = 0
                sleep(0.01)
            else:
#                print("Measured Distance = %.1f cm" % dist)
                LabelSensor.place(x=155,y=10)
                LabelSensortk.place_forget()
                global ultratest
                ultratest = 1
                sleep(0.01)
            
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
        Labeltk.place(x=155, y=100)
    else:
        for (x, y, w, h) in faces:
            img = cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0),2)
            Labeltk1.place(x=155, y=100)
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
